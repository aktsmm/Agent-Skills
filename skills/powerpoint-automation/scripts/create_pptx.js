// =============================================================================
// Ag-ppt-create - AI-powered PPTX generation pipeline
// https://github.com/aktsmm/Ag-ppt-create
//
// Copyright (c) aktsmm. Licensed under CC BY-NC-SA 4.0.
// DO NOT MODIFY THIS HEADER BLOCK.
// =============================================================================
/**
 * create_pptx.js - Create PowerPoint from JSON content using pptxgenjs
 *
 * Usage:
 *   node scripts/create_pptx.js <content.json> <output.pptx>
 *
 * Features:
 *   - Creates clean, professional slides from JSON
 *   - Supports images (local path or URL)
 *   - Image positions: right, bottom, full
 *   - Great for code-heavy presentations
 *
 * Author: aktsmm
 * License: CC BY-NC 4.0
 */

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");
const { addSignature } = require("./pptx-signature");

// Design constants
const COLORS = {
  purple: "5B5FC7", // Microsoft Purple
  darkGray: "333333",
  white: "FFFFFF",
  lightGray: "F5F5F5",
  darkBlue: "1E3A5F", // Dark background threshold reference
};

const FONTS = {
  title: "Yu Gothic UI",
  body: "Yu Gothic UI",
};

/**
 * Determine if a background color is dark (needs white text)
 * @param {string} hexColor - Hex color without # (e.g., "5B5FC7")
 * @returns {boolean} True if background is dark
 */
function isDarkColor(hexColor) {
  if (!hexColor) return false;
  const hex = hexColor.replace("#", "");
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  // Calculate relative luminance (perceived brightness)
  // Formula: 0.299*R + 0.587*G + 0.114*B
  const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
  return luminance < 128; // Dark if luminance < 50%
}

/**
 * Get text color based on slide background
 * @param {Object} slideData - Slide data with optional background field
 * @param {string} defaultColor - Default color to use
 * @returns {string} Appropriate text color
 */
function getTextColor(slideData, defaultColor) {
  // Check for explicit dark background flag or background image
  if (slideData.dark_background || slideData.darkBackground) {
    return COLORS.white;
  }
  // Check for background color
  if (slideData.background_color) {
    return isDarkColor(slideData.background_color)
      ? COLORS.white
      : defaultColor;
  }
  // Check for background image (usually dark in presentations)
  if (slideData.background_image || slideData.backgroundImage) {
    return COLORS.white;
  }
  return defaultColor;
}

// Slide dimensions (16:9)
const SLIDE_WIDTH = 13.333;
const SLIDE_HEIGHT = 7.5;

/**
 * Get image dimensions from local file
 * @param {string} imagePath - Path to image file
 * @returns {{width: number, height: number}|null} Image dimensions in pixels
 */
function getImageSize(imagePath) {
  try {
    // Try using image-size package if available
    const sizeOf = require("image-size");
    const dimensions = sizeOf(imagePath);
    return { width: dimensions.width, height: dimensions.height };
  } catch {
    // Fallback: read PNG/JPEG headers manually
    try {
      const buffer = fs.readFileSync(imagePath);
      // PNG: width at bytes 16-19, height at bytes 20-23
      if (
        buffer[0] === 0x89 &&
        buffer[1] === 0x50 &&
        buffer[2] === 0x4e &&
        buffer[3] === 0x47
      ) {
        const width = buffer.readUInt32BE(16);
        const height = buffer.readUInt32BE(20);
        return { width, height };
      }
      // JPEG: search for SOF0 marker
      if (buffer[0] === 0xff && buffer[1] === 0xd8) {
        let offset = 2;
        while (offset < buffer.length) {
          if (buffer[offset] !== 0xff) break;
          const marker = buffer[offset + 1];
          if (marker >= 0xc0 && marker <= 0xc3) {
            const height = buffer.readUInt16BE(offset + 5);
            const width = buffer.readUInt16BE(offset + 7);
            return { width, height };
          }
          const segmentLength = buffer.readUInt16BE(offset + 2);
          offset += 2 + segmentLength;
        }
      }
    } catch {
      // Ignore errors
    }
    return null;
  }
}

/**
 * Detect if image is likely an icon/logo based on size
 * @param {string} imagePath - Path to image file
 * @param {number} minContentSize - Minimum size for content images (default 400px)
 * @returns {{isIcon: boolean, suggestedPct: number}} Detection result
 */
function isIconOrLogo(imagePath, minContentSize = 400) {
  const size = getImageSize(imagePath);
  if (!size) {
    return { isIcon: false, suggestedPct: 45 };
  }

  const { width, height } = size;

  // Very small images (< 400px) are likely icons
  if (width < minContentSize || height < minContentSize) {
    const suggested = Math.min(
      20,
      Math.max(10, Math.round((width / SLIDE_WIDTH / 96) * 100 * 1.2))
    );
    return { isIcon: true, suggestedPct: suggested };
  }

  // Square images under 800px are likely logos
  const aspectRatio = width / height;
  if (
    aspectRatio >= 0.9 &&
    aspectRatio <= 1.1 &&
    Math.max(width, height) <= 800
  ) {
    const suggested = Math.min(
      25,
      Math.max(15, Math.round((width / SLIDE_WIDTH / 96) * 100 * 1.2))
    );
    return { isIcon: true, suggestedPct: suggested };
  }

  return { isIcon: false, suggestedPct: 45 };
}

/**
 * Download image from URL and return as base64
 * @param {string} url - Image URL
 * @returns {Promise<string>} Base64 encoded image data
 */
function downloadImage(url) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith("https") ? https : http;
    console.log(`  📥 Downloading: ${url.substring(0, 50)}...`);

    protocol
      .get(url, (response) => {
        // Handle redirects
        if (
          response.statusCode >= 300 &&
          response.statusCode < 400 &&
          response.headers.location
        ) {
          return downloadImage(response.headers.location)
            .then(resolve)
            .catch(reject);
        }

        if (response.statusCode !== 200) {
          reject(new Error(`Failed to download: ${response.statusCode}`));
          return;
        }

        const chunks = [];
        response.on("data", (chunk) => chunks.push(chunk));
        response.on("end", () => {
          const buffer = Buffer.concat(chunks);
          const base64 = buffer.toString("base64");
          const contentType = response.headers["content-type"] || "image/png";
          resolve(`data:${contentType};base64,${base64}`);
        });
        response.on("error", reject);
      })
      .on("error", reject);
  });
}

/**
 * Resolve image path - local file or URL
 * @param {Object} imageConfig - Image configuration
 * @param {string} basePath - Base path for relative paths
 * @returns {Promise<string|null>} Image path or data URI
 */
async function resolveImage(imageConfig, basePath) {
  if (imageConfig.url) {
    try {
      return await downloadImage(imageConfig.url);
    } catch (err) {
      console.warn(`  ⚠️  Failed to download image: ${err.message}`);
      return null;
    }
  }

  if (imageConfig.path) {
    const candidates = [
      path.resolve(basePath, "..", imageConfig.path),
      path.resolve(imageConfig.path),
      path.resolve(basePath, imageConfig.path),
    ];

    for (const candidate of candidates) {
      if (fs.existsSync(candidate)) {
        return candidate;
      }
    }
    console.warn(`  ⚠️  Image not found: ${imageConfig.path}`);
  }

  return null;
}

/**
 * Add title slide
 * @param {pptxgen} pptx - Presentation object
 * @param {Object} slideData - Slide data
 */
function addTitleSlide(pptx, slideData) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.purple };

  // Title
  slide.addText(slideData.title || "", {
    x: 0.5,
    y: 2.2,
    w: "92%",
    h: 1.5,
    fontSize: 44,
    fontFace: FONTS.title,
    color: COLORS.white,
    bold: true,
    align: "center",
    valign: "middle",
  });

  // Subtitle
  if (slideData.subtitle) {
    slide.addText(slideData.subtitle, {
      x: 0.5,
      y: 3.8,
      w: "92%",
      h: 0.8,
      fontSize: 24,
      fontFace: FONTS.body,
      color: COLORS.white,
      align: "center",
    });
  }

  return slide;
}

/**
 * Add content slide with optional image
 * @param {pptxgen} pptx - Presentation object
 * @param {Object} slideData - Slide data
 * @param {string} basePath - Base path for images
 */
async function addContentSlide(pptx, slideData, basePath) {
  const slide = pptx.addSlide();

  // Detect if slide has dark background (for text color decisions)
  const hasDarkBg =
    slideData.dark_background ||
    slideData.darkBackground ||
    slideData.background_image ||
    slideData.backgroundImage ||
    (slideData.background_color && isDarkColor(slideData.background_color));
  const bodyTextColor = hasDarkBg ? COLORS.white : COLORS.darkGray;

  // Apply background if specified
  if (slideData.background_color) {
    slide.background = { color: slideData.background_color.replace("#", "") };
  }

  // Title bar (only if not using full dark background)
  if (!hasDarkBg) {
    slide.addShape("rect", {
      x: 0,
      y: 0,
      w: "100%",
      h: 1.0,
      fill: { color: COLORS.purple },
    });
  }

  // Title text
  slide.addText(slideData.title || "", {
    x: 0.5,
    y: 0.2,
    w: "92%",
    h: 0.7,
    fontSize: 28,
    fontFace: FONTS.title,
    color: COLORS.white,
    bold: true,
  });

  // Default content area
  let contentArea = { x: 0.5, y: 1.3, w: 12.3, h: 5.0 };

  // Handle image if present
  if (slideData.image) {
    const imagePath = await resolveImage(slideData.image, basePath);
    if (imagePath) {
      const position = slideData.image.position || "right";
      let widthPct = slideData.image.width_percent || 45;
      const heightPct = slideData.image.height_percent || 50;

      // Detect icons/logos and limit their size (only for local files)
      const isDataUri = imagePath.startsWith("data:");
      if (!isDataUri) {
        const { isIcon, suggestedPct } = isIconOrLogo(imagePath);
        if (isIcon) {
          const size = getImageSize(imagePath);
          console.log(
            `    [i] Icon/logo detected (${size?.width}x${size?.height}px) - using size: ${suggestedPct}%`
          );
          widthPct = Math.min(widthPct, suggestedPct);
        }
      }

      try {
        // Build image options
        const imageOpts = isDataUri ? { data: imagePath } : { path: imagePath };

        if (position === "full") {
          // Full slide image
          slide.addImage({
            ...imageOpts,
            x: 0.5,
            y: 1.3,
            w: 12.3,
            h: 5.5,
          });
          return slide; // No text content for full image
        } else if (position === "right") {
          // Image on right - calculate height based on actual aspect ratio
          const imgW = (13.333 * widthPct) / 100;
          const imgY = 1.5;
          const imgX = 13.333 - 0.5 - imgW;
          const maxImgH = 5.0; // Maximum height to fit in content area

          // Get actual image dimensions to maintain aspect ratio
          let imgH = maxImgH; // Default
          if (!isDataUri) {
            const size = getImageSize(imagePath);
            if (size && size.width && size.height) {
              const aspectRatio = size.height / size.width;
              imgH = imgW * aspectRatio;
              // Cap height if too tall
              if (imgH > maxImgH) {
                imgH = maxImgH;
              }
            }
          }

          slide.addImage({
            ...imageOpts,
            x: imgX,
            y: imgY,
            w: imgW,
            h: imgH,
          });
          contentArea.w = (13.333 * (100 - widthPct - 5)) / 100;
        } else if (position === "bottom") {
          // Image at bottom
          const imgH = (7.5 * heightPct) / 100;
          slide.addImage({
            ...imageOpts,
            x: 0.5,
            y: 7.5 - 0.5 - imgH,
            w: 12.3,
            h: imgH,
          });
          contentArea.h = (7.5 * (100 - heightPct - 20)) / 100;
        } else if (position === "center") {
          // Image centered (for photo slides)
          // Note: Limit width to prevent tall images from exceeding slide bounds
          // Available height = 7.5 - 1.5 (title) - 0.3 (margin) = 5.7"
          const maxWidth = 60; // Limit to 60% to prevent overflow with tall images
          const effectiveWidthPct = Math.min(widthPct, maxWidth);
          const imgW = (13.333 * effectiveWidthPct) / 100;
          const imgX = (13.333 - imgW) / 2;
          const availableHeight = 5.5; // Conservative estimate

          if (widthPct > maxWidth) {
            console.log(
              `    [i] Center image width limited: ${widthPct}% → ${maxWidth}% (to fit slide height)`
            );
          }

          slide.addImage({
            ...imageOpts,
            x: imgX,
            y: 1.5,
            w: imgW,
            h: availableHeight, // Let pptxgenjs scale proportionally if image is shorter
          });
          contentArea = null; // No content area for centered images
        }
      } catch (err) {
        console.warn(`  ⚠️  Failed to add image: ${err.message}`);
      }
    }
  }

  // Content bullets (skip if content area was nullified by full/center image)
  if (!contentArea) {
    return slide;
  }
  const items = slideData.items || slideData.content || [];
  if (items.length > 0) {
    const textContent = items.map((item) => {
      if (typeof item === "object") {
        return { text: item.text || String(item), options: { bullet: true } };
      }
      return { text: String(item), options: { bullet: true } };
    });

    slide.addText(textContent, {
      x: contentArea.x,
      y: contentArea.y,
      w: contentArea.w,
      h: contentArea.h,
      fontSize: 20,
      fontFace: FONTS.body,
      color: bodyTextColor, // Dynamic: white on dark bg, dark gray on light bg
      valign: "top",
      paraSpaceAfter: 8,
    });
  }

  return slide;
}

/**
 * Add section slide
 * @param {pptxgen} pptx - Presentation object
 * @param {Object} slideData - Slide data
 */
function addSectionSlide(pptx, slideData) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.purple };

  slide.addText(slideData.title || "", {
    x: 0.5,
    y: 2.5,
    w: "92%",
    h: 1.2,
    fontSize: 40,
    fontFace: FONTS.title,
    color: COLORS.white,
    bold: true,
    align: "center",
    valign: "middle",
  });

  if (slideData.subtitle) {
    slide.addText(slideData.subtitle, {
      x: 0.5,
      y: 3.8,
      w: "92%",
      h: 0.6,
      fontSize: 22,
      fontFace: FONTS.body,
      color: COLORS.white,
      align: "center",
    });
  }

  return slide;
}

/**
 * Add two-column comparison slide
 * @param {pptxgen} pptx - Presentation object
 * @param {Object} slideData - Slide data
 */
function addTwoColumnSlide(pptx, slideData) {
  const slide = pptx.addSlide();

  // Title bar
  slide.addShape("rect", {
    x: 0,
    y: 0,
    w: "100%",
    h: 1.0,
    fill: { color: COLORS.purple },
  });

  // Title text
  slide.addText(slideData.title || "", {
    x: 0.5,
    y: 0.2,
    w: "92%",
    h: 0.7,
    fontSize: 28,
    fontFace: FONTS.title,
    color: COLORS.white,
    bold: true,
  });

  // Left column title
  if (slideData.left_title) {
    slide.addText(slideData.left_title, {
      x: 0.5,
      y: 1.3,
      w: 5.8,
      h: 0.5,
      fontSize: 22,
      fontFace: FONTS.title,
      color: COLORS.purple,
      bold: true,
    });
  }

  // Left column content
  const leftItems = slideData.left_items || [];
  if (leftItems.length > 0) {
    const leftContent = leftItems.map((item) => {
      const text =
        typeof item === "object" ? item.text || String(item) : String(item);
      return { text, options: { bullet: true } };
    });

    slide.addText(leftContent, {
      x: 0.5,
      y: 1.9,
      w: 5.8,
      h: 4.8,
      fontSize: 18,
      fontFace: FONTS.body,
      color: COLORS.darkGray,
      valign: "top",
      paraSpaceAfter: 6,
    });
  }

  // Right column title
  if (slideData.right_title) {
    slide.addText(slideData.right_title, {
      x: 7.0,
      y: 1.3,
      w: 5.8,
      h: 0.5,
      fontSize: 22,
      fontFace: FONTS.title,
      color: COLORS.purple,
      bold: true,
    });
  }

  // Right column content
  const rightItems = slideData.right_items || [];
  if (rightItems.length > 0) {
    const rightContent = rightItems.map((item) => {
      const text =
        typeof item === "object" ? item.text || String(item) : String(item);
      return { text, options: { bullet: true } };
    });

    slide.addText(rightContent, {
      x: 7.0,
      y: 1.9,
      w: 5.8,
      h: 4.8,
      fontSize: 18,
      fontFace: FONTS.body,
      color: COLORS.darkGray,
      valign: "top",
      paraSpaceAfter: 6,
    });
  }

  return slide;
}

/**
 * Validate and fix content issues
 * @param {Array} slides - Slides array
 * @returns {Array} Fixed slides array
 */
function validateAndFixContent(slides) {
  let fixedCount = 0;

  slides.forEach((slide, i) => {
    const type = slide.type || "content";
    const items = slide.items || slide.content || [];
    const title = slide.title || `Slide ${i + 1}`;

    // closing type with items → convert to content
    if (type === "closing" && items.length > 1) {
      console.log(
        `  ⚠️  Warning: Slide ${i + 1} '${title.substring(
          0,
          30
        )}...' has type='closing' with ${items.length} items`
      );
      console.log(`      → Auto-converting to type='content'`);
      slide.type = "content";
      fixedCount++;
    }
  });

  if (fixedCount > 0) {
    console.log(`  ✅ Auto-fixed ${fixedCount} slide(s)\n`);
  }

  return slides;
}

/**
 * Main function
 */
async function main() {
  const args = process.argv.slice(2);

  // Check for --no-signature flag
  const noSignature = args.includes("--no-signature");
  const filteredArgs = args.filter((a) => a !== "--no-signature");

  if (filteredArgs.length < 2) {
    console.log(
      "Usage: node scripts/create_pptx.js <content.json> <output.pptx> [--no-signature]"
    );
    console.log("");
    console.log("Options:");
    console.log("  --no-signature  Disable repository signature in notes");
    console.log("");
    console.log("Example:");
    console.log(
      "  node scripts/create_pptx.js output_manifest/content.json output_ppt/result.pptx"
    );
    process.exit(1);
  }

  const [inputJson, outputPptx] = filteredArgs;

  // Load content
  console.log(`\nLoading: ${inputJson}`);
  const content = JSON.parse(fs.readFileSync(inputJson, "utf-8"));
  let slides = content.slides || content;
  if (!Array.isArray(slides)) {
    slides = [slides];
  }

  // Validate content
  console.log("🔍 Validating content...");
  slides = validateAndFixContent(slides);

  // Create presentation
  const pptx = new pptxgen();
  pptx.defineLayout({ name: "CUSTOM", width: 13.333, height: 7.5 }); // 16:9
  pptx.layout = "CUSTOM";

  console.log(`Creating ${slides.length} slides...\n`);

  const basePath = path.dirname(path.resolve(inputJson));
  const createdSlides = []; // Track created slides for signature

  for (let i = 0; i < slides.length; i++) {
    const slideData = slides[i];
    const type = slideData.type || "content";
    const title = slideData.title || `Slide ${i + 1}`;
    const hasImage = slideData.image ? " 📷" : "";

    console.log(
      `  Slide ${i + 1}: ${title.substring(0, 40)}... [${type}]${hasImage}`
    );

    let slide;
    switch (type) {
      case "title":
      case "closing":
        // If title/closing has image, use small image (avoid oversized presenter photos)
        if (slideData.image) {
          // Limit image size for title slides (e.g., presenter photos)
          const titleSlideData = { ...slideData };
          if (titleSlideData.image) {
            titleSlideData.image = {
              ...titleSlideData.image,
              width_percent: Math.min(
                titleSlideData.image.width_percent || 25,
                25
              ),
              position: titleSlideData.image.position || "right",
            };
          }
          slide = await addContentSlide(pptx, titleSlideData, basePath);
        } else {
          slide = addTitleSlide(pptx, slideData);
        }
        break;
      case "section":
      case "section_title":
        slide = addSectionSlide(pptx, slideData);
        break;
      case "two_column":
        slide = addTwoColumnSlide(pptx, slideData);
        break;
      default:
        slide = await addContentSlide(pptx, slideData, basePath);
    }

    // Add speaker notes to each slide (first/last handled by addSignature)
    // Note: addNotes overwrites, so we add to all slides here
    // and addSignature will prepend/append signature to first/last
    if (slideData.notes) {
      slide.addNotes(slideData.notes);
    }

    createdSlides.push({ slide, notes: slideData.notes, index: i });
  }

  // Add repository signature to first and last slides
  // This overwrites notes with signature + original notes
  if (!noSignature && createdSlides.length > 0) {
    const first = createdSlides[0];
    const last = createdSlides[createdSlides.length - 1];
    addSignature(first.slide, last.slide, {
      firstNotes: first.notes,
      lastNotes: last.notes,
    });
  }

  // Ensure output directory exists
  const outputDir = path.dirname(outputPptx);
  if (outputDir && !fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Save
  await pptx.writeFile({ fileName: outputPptx });
  console.log(`\n✅ Created: ${outputPptx}`);
  console.log(`   Total slides: ${slides.length}`);
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
