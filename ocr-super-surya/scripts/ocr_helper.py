#!/usr/bin/env python3
"""
OCR Helper - Surya OCR wrapper for common tasks.

Usage:
    from ocr_helper import ocr_image, ocr_pdf
    
    # Single image
    text = ocr_image("screenshot.png")
    
    # PDF (all pages)
    results = ocr_pdf("document.pdf")
    
    # With verbose logging
    text = ocr_image("image.png", verbose=True)
"""

import os
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logger = logging.getLogger("ocr_helper")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logger.addHandler(handler)
logger.setLevel(logging.WARNING)  # Default: only warnings and errors


def set_verbose(enabled: bool = True):
    """Enable or disable verbose logging."""
    logger.setLevel(logging.DEBUG if enabled else logging.WARNING)


# Check GPU availability
def get_device_info() -> dict:
    """Get device information (GPU/CPU)."""
    import torch
    
    if torch.cuda.is_available():
        return {
            "device": "cuda",
            "gpu_name": torch.cuda.get_device_name(0),
            "vram_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3)
        }
    return {"device": "cpu", "gpu_name": None, "vram_gb": 0}


def _run_with_oom_retry(func, *args, max_retries: int = 3, **kwargs):
    """
    Run a function with automatic OOM retry and batch size reduction.
    
    On CUDA OOM, reduces batch size by half and retries.
    """
    import torch
    
    batch_sizes = [
        ("RECOGNITION_BATCH_SIZE", int(os.environ.get("RECOGNITION_BATCH_SIZE", 512))),
        ("DETECTOR_BATCH_SIZE", int(os.environ.get("DETECTOR_BATCH_SIZE", 36))),
    ]
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            if "out of memory" not in str(e).lower():
                raise
            
            if attempt == max_retries - 1:
                logger.error(f"❌ OOM after {max_retries} retries. Consider reducing image size.")
                raise
            
            # Reduce batch sizes by half
            for env_var, current_size in batch_sizes:
                new_size = max(1, current_size // 2)
                os.environ[env_var] = str(new_size)
                logger.warning(f"⚠️  OOM detected. Reducing {env_var}: {current_size} → {new_size}")
                batch_sizes = [(v, s // 2) for v, s in batch_sizes]
            
            # Clear CUDA cache
            torch.cuda.empty_cache()
            logger.info(f"🔄 Retry {attempt + 2}/{max_retries}...")


def ocr_image(
    image_path: str,
    output_format: str = "text",
    verbose: bool = False,
    auto_retry: bool = True
) -> str | dict:
    """
    OCR a single image using Surya.
    
    Args:
        image_path: Path to the image file
        output_format: "text" for plain text, "json" for detailed results
        verbose: Enable detailed logging
        auto_retry: Automatically retry with smaller batch size on OOM
    
    Note:
        Language is auto-detected by Surya. No manual specification needed.
    
    Returns:
        Extracted text (str) or detailed results (dict)
    """
    if verbose:
        set_verbose(True)
    
    from PIL import Image
    from surya.recognition import RecognitionPredictor
    from surya.detection import DetectionPredictor
    from surya.foundation import FoundationPredictor
    
    logger.debug(f"📂 Loading image: {image_path}")
    
    # Load image
    image = Image.open(image_path)
    logger.debug(f"📐 Image size: {image.size}")
    
    # Initialize predictors
    logger.debug("🔧 Initializing predictors...")
    foundation_predictor = FoundationPredictor()
    recognition_predictor = RecognitionPredictor(foundation_predictor)
    detection_predictor = DetectionPredictor()
    
    def _run_ocr():
        return recognition_predictor(
            [image], 
            det_predictor=detection_predictor
        )
    
    # Run OCR with optional retry
    logger.debug("🔍 Running OCR...")
    if auto_retry:
        predictions = _run_with_oom_retry(_run_ocr)
    else:
        predictions = _run_ocr()
    
    logger.debug(f"✅ Found {sum(len(p.text_lines) for p in predictions)} text lines")
    
    if output_format == "json":
        return {
            "text_lines": [
                {
                    "text": line.text,
                    "confidence": line.confidence,
                    "bbox": line.bbox
                }
                for page in predictions
                for line in page.text_lines
            ]
        }
    
    # Return plain text
    return "\n".join(
        line.text 
        for page in predictions 
        for line in page.text_lines
    )


def ocr_pdf(
    pdf_path: str,
    dpi: int = 300,
    verbose: bool = False,
    auto_retry: bool = True
) -> list[str]:
    """
    OCR all pages of a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for PDF to image conversion
        verbose: Enable detailed logging
        auto_retry: Automatically retry with smaller batch size on OOM
    
    Note:
        Language is auto-detected by Surya. No manual specification needed.
    
    Returns:
        List of extracted text per page
    """
    if verbose:
        set_verbose(True)
    
    try:
        import pdf2image
    except ImportError:
        raise ImportError(
            "pdf2image is required for PDF processing. "
            "Install with: pip install pdf2image"
        )
    
    from surya.recognition import RecognitionPredictor
    from surya.detection import DetectionPredictor
    from surya.foundation import FoundationPredictor
    
    logger.debug(f"📄 Converting PDF to images (dpi={dpi}): {pdf_path}")
    
    # Convert PDF to images
    images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
    logger.debug(f"📚 Found {len(images)} pages")
    
    # Initialize predictors
    logger.debug("🔧 Initializing predictors...")
    foundation_predictor = FoundationPredictor()
    recognition_predictor = RecognitionPredictor(foundation_predictor)
    detection_predictor = DetectionPredictor()
    
    def _run_ocr():
        return recognition_predictor(
            images,
            det_predictor=detection_predictor
        )
    
    # OCR all pages with optional retry
    logger.debug("🔍 Running OCR on all pages...")
    if auto_retry:
        predictions = _run_with_oom_retry(_run_ocr)
    else:
        predictions = _run_ocr()
    
    # Extract text per page
    results = []
    for i, page in enumerate(predictions):
        page_text = "\n".join(line.text for line in page.text_lines)
        results.append(page_text)
        logger.debug(f"✅ Page {i+1}: {len(page.text_lines)} lines")
    
    return results


def ocr_batch(
    image_paths: list[str],
    verbose: bool = False,
    auto_retry: bool = True
) -> dict[str, str]:
    """
    OCR multiple images in batch (more efficient).
    
    Args:
        image_paths: List of image file paths
        verbose: Enable detailed logging
        auto_retry: Automatically retry with smaller batch size on OOM
    
    Note:
        Language is auto-detected by Surya. No manual specification needed.
    
    Returns:
        Dictionary mapping file paths to extracted text
    """
    if verbose:
        set_verbose(True)
    
    from PIL import Image
    from surya.recognition import RecognitionPredictor
    from surya.detection import DetectionPredictor
    from surya.foundation import FoundationPredictor
    
    logger.debug(f"📚 Loading {len(image_paths)} images...")
    
    # Load all images
    images = [Image.open(p) for p in image_paths]
    
    # Initialize predictors
    logger.debug("🔧 Initializing predictors...")
    foundation_predictor = FoundationPredictor()
    recognition_predictor = RecognitionPredictor(foundation_predictor)
    detection_predictor = DetectionPredictor()
    
    def _run_ocr():
        return recognition_predictor(
            images,
            det_predictor=detection_predictor
        )
    
    # Run OCR on all images at once with optional retry
    logger.debug("🔍 Running batch OCR...")
    if auto_retry:
        predictions = _run_with_oom_retry(_run_ocr)
    else:
        predictions = _run_ocr()
    
    # Map results to file paths
    results = {}
    for path, page in zip(image_paths, predictions):
        results[path] = "\n".join(line.text for line in page.text_lines)
        logger.debug(f"✅ {path}: {len(page.text_lines)} lines")
    
    return results


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR using Surya")
    parser.add_argument("input", help="Image or PDF file path")
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--no-retry", action="store_true", help="Disable OOM auto-retry")
    
    args = parser.parse_args()
    
    # Enable verbose if requested
    if args.verbose:
        set_verbose(True)
    
    # Show device info
    device_info = get_device_info()
    print(f"🖥️  Device: {device_info['device']}", end="")
    if device_info['gpu_name']:
        print(f" ({device_info['gpu_name']}, {device_info['vram_gb']:.1f}GB)")
    else:
        print()
    
    # Process input
    input_path = Path(args.input)
    auto_retry = not args.no_retry
    
    if input_path.suffix.lower() == ".pdf":
        print(f"📄 Processing PDF: {input_path}")
        results = ocr_pdf(
            str(input_path), 
            verbose=args.verbose,
            auto_retry=auto_retry
        )
        text = "\n\n--- Page Break ---\n\n".join(results)
    else:
        print(f"🖼️  Processing image: {input_path}")
        output_format = "json" if args.json else "text"
        text = ocr_image(
            str(input_path), 
            output_format=output_format,
            verbose=args.verbose,
            auto_retry=auto_retry
        )
    
    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else str(text))
        print(f"✅ Saved to: {args.output}")
    else:
        print("\n--- OCR Result ---")
        print(text)
