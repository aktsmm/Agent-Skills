#!/usr/bin/env python3
"""
receipt_sorter.py - OCR領収書自動仕分けツール

Usage:
  python receipt_sorter.py --project "202602_TechConnect_Seattle"
  python receipt_sorter.py --project "202602_TechConnect_Seattle" --dry-run
  python receipt_sorter.py --project "202602_TechConnect_Seattle" --input "未仕分け/iCloud写真"
"""

import sys
import io
import os
import re
import csv
import time
import shutil
import zipfile
import tempfile
import argparse
import unicodedata
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# UTF-8 出力（PYTHONUTF8=1 環境変数で制御、ここでは強制設定）
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
if sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

# ── ディレクトリ設定 ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DEFAULT_INPUT = BASE_DIR / "未仕分け"
UNCLASSIFIED_NAME = "未分類"

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
SUPPORTED_EXTS = SUPPORTED_IMAGE_EXTS | {".pdf", ".zip"}

# ── 国判定キーワード ───────────────────────────────────────────────────────────
JP_STRONG = ["円", "¥", "￥", "税", "消費税", "合計", "お買上", "領収", "レシート",
             "様", "枚", "点", "品", "ご利用", "ありがとう"]
US_STRONG = ["USD", "SUBTOTAL", "THANK YOU FOR", "SERVER:", "TABLE:", "CHECK #"]

COUNTRY_KEYWORDS = {
    "jp": ["japan", "日本", "東京", "大阪", "名古屋", "京都", "福岡", "新幹線",
           "羽田", "成田", "関西空港"],
    "us": ["united states", "usa", "seattle", "new york", "california", "chicago",
           "boston", "washington", "las vegas", "san francisco", "los angeles",
           "usd", "wa ", "ca ", "ny "],
    "cn": ["china", "中国", "人民币", "rmb", "cny", "北京", "上海"],
    "gb": ["united kingdom", "england", "gbp", "london"],
    "sg": ["singapore", "sgd"],
    "kr": ["korea", "한국", "원", "krw", "seoul"],
    "au": ["australia", "aud", "sydney", "melbourne"],
}

COUNTRY_OUTPUT = {
    "jp": "jpn",
    "us": "us",
    "cn": "cn",
    "gb": "gb",
    "sg": "sg",
    "kr": "kr",
    "au": "au",
    "xx": "xx",
}

# ── 商品明細キーワード（食品・飲料）──────────────────────────────────────────
# レシート本文にこれらが含まれる場合、meal 系に優先分類する
FOOD_ITEM_KEYWORDS = [
    # 英語: 食品・飲料の一般名
    "BURGER", "SANDWICH", "SALAD", "SOUP", "PIZZA", "PASTA", "TACO", "BURRITO",
    "WRAP", "BOWL", "FRIES", "CHICKEN", "STEAK", "FISH", "SHRIMP", "SAUSAGE",
    "BACON", "EGG", "TOAST", "PANCAKE", "WAFFLE", "BAGEL", "MUFFIN", "CROISSANT",
    "DRINK", "BEVERAGE", "SODA", "JUICE", "LATTE", "MOCHA", "CAPPUCCINO", "TEA",
    "BEER", "WINE", "COCKTAIL", "WATER", "MILK", "SMOOTHIE",
    "DESSERT", "CAKE", "PIE", "ICE CREAM", "COOKIE", "BROWNIE", "DONUT",
    "APPETIZER", "ENTREE", "SIDE", "COMBO", "MEAL DEAL",
    "GRATUITY", "SERVER", "TABLE", "DINE IN", "TAKE OUT", "TO GO",
    "CHOWDER", "CALAMARI", "OYSTER", "CLAM", "LOBSTER", "CRAB",
    # 日本語: 食品
    "弁当", "おにぎり", "サンドイッチ", "ハンバーガー", "カレー", "定食",
    "ドリンク", "ビール", "コーラ", "お茶", "水",
]

# ── 店舗・用途キーワード ───────────────────────────────────────────────────────
MERCHANT_MAP = [
    ("shinkansen",   ["新幹線", "のぞみ", "ひかり", "こだま", "EX予約", "EXご利用票", "みずほ", "さくら"]),
    ("taxi",         ["タクシー", "TAXI", "UBER", "LYFT", "DiDi", "GO TAXI"]),
    ("hotel",        ["ホテル", "HOTEL", "INN", "RESORT", "宿泊", "MARRIOTT", "HILTON",
                      "HYATT", "SHERATON", "WESTIN", "ANA INTERCONTINENTAL"]),
    ("airline",      ["ANA", "JAL", "DELTA", "UNITED", "ALASKA", "AMERICAN AIRLINES",
                      "SOUTHWEST", "JETBLUE", "航空", "AIRLINE", "AIRWAYS"]),
    ("starbucks",    ["スターバックス", "STARBUCKS"]),
    ("coffee",       ["COFFEE", "コーヒー", "CAFE", "カフェ", "ESPRESSO"]),
    ("restaurant",   ["レストラン", "RESTAURANT", "DINING", "DINER", "BISTRO",
                      "GRILL", "KITCHEN", "EATERY", "DELI", "食堂", "居酒屋", "寿司", "ラーメン"]),
    ("convenience",  ["コンビニ", "7-ELEVEN", "SEVEN ELEVEN", "LAWSON", "FAMILY MART",
                      "FAMILYMART", "MINI STOP", "セブン", "ローソン", "ファミマ"]),
    ("supermarket",  ["スーパー", "COSTCO", "WHOLE FOODS", "SAFEWAY", "KROGER",
                      "WALMART", "TARGET", "イオン", "西友"]),
    ("meal",         ["MEAL", "LUNCH", "DINNER", "BREAKFAST", "FOOD", "SNACK"]),
    ("pharmacy",     ["薬局", "PHARMACY", "DRUG STORE", "WALGREENS", "CVS", "RITE AID"]),
    ("transport",    ["交通", "TRANSIT", "METRO", "SUBWAY", "BUS", "Suica", "PASMO",
                      "IC CARD", "鉄道", "電車"]),
    ("shopping",     ["AMAZON", "APPLE STORE", "アップルストア", "百貨店", "デパート",
                      "MALL", "NORDSTROM", "MACY"]),
    ("seminar",      ["セミナー", "SEMINAR", "CONFERENCE", "WORKSHOP", "SUMMIT",
                      "CONNECT", "TECHCONNECT", "TECH CONNECT"]),
]

# ── カード判定 ────────────────────────────────────────────────────────────────
CARD_PATTERNS = {
    "amex":       [r"AMEX", r"AMERICAN\s*EXPRESS", r"JEB[0-9A-Z]",
                   r"\b3[47]\d{2}[\s\-]\d{6}[\s\-]\d{5}\b",
                   r"\*{4}\s*\d{5}"],           # Amexは4桁+6桁+5桁
    "visa":       [r"\bVISA\b"],
    "mastercard": [r"\bMASTERCARD\b", r"\bMASTER\s*CARD\b", r"\bMC\b"],
    "jcb":        [r"\bJCB\b"],
    "diners":     [r"\bDINERS\b", r"\bDINER.?S\s*CLUB\b"],
    "discover":   [r"\bDISCOVER\b"],
}
CARD_NAMES = set(CARD_PATTERNS.keys())

# ── 日付パターン ──────────────────────────────────────────────────────────────
DATE_PATTERNS = [
    # 2026-02-09 / 2026/02/09
    (r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})",
     lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    # 2026年2月9日
    (r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日",
     lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    # 26年2月9日
    (r"(\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日",
     lambda m: (2000 + int(m.group(1)), int(m.group(2)), int(m.group(3)))),
    # 02/09/2026 (US: MM/DD/YYYY)
    (r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
     lambda m: (int(m.group(3)), int(m.group(1)), int(m.group(2)))),
    # 2/11/26 (US: MM/DD/YY)
    (r"\b(\d{1,2})/(\d{1,2})/(\d{2})\b",
     lambda m: (2000 + int(m.group(3)), int(m.group(1)), int(m.group(2)))),
    # Feb 09, 2026 / February 9, 2026
    (r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})",
     lambda m: (int(m.group(3)),
                {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
                 "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
                [m.group(1).lower()[:3]], int(m.group(2)))),
    # 11-Feb-2026 / 09-Feb-2026
    (r"\b(\d{1,2})[\-\s](Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\-\s,]*(\d{4})\b",
     lambda m: (int(m.group(3)),
                {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
                 "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
                [m.group(2).lower()[:3]], int(m.group(1)))),
]

# ── 金額パターン ──────────────────────────────────────────────────────────────
# OCRの「桁分断/連結」対策:
# - 14, 320 のようなカンマ後スペースは許容
# - 7.60 891 のような余分な連結は最初の妥当数値のみ拾う
AMOUNT_NUMBER = r"(?<!\d)(?:\d{1,3}(?:[,\s]\s*\d{3})+|\d+)(?:\.\d{1,2})?(?!\d)"
MAX_RECEIPT_AMOUNT = 5_000_000  # 1枚の領収書として不自然な額は除外
AMOUNT_PATTERNS = [
    r"[¥￥]\s*(" + AMOUNT_NUMBER + r")",
    r"(" + AMOUNT_NUMBER + r")\s*円",
    r"\$\s*(" + AMOUNT_NUMBER + r")",
    r"USD\s*(" + AMOUNT_NUMBER + r")",
    r"(?:TOTAL|合計|お会計|お買上)[^\d\r\n]{0,20}(" + AMOUNT_NUMBER + r")",
    r"(?:GRAND\s*TOTAL)[^\d\r\n]{0,20}(" + AMOUNT_NUMBER + r")",
]


# ── OCRエンジン ───────────────────────────────────────────────────────────────
_predictors = None


def get_predictors():
    global _predictors
    if _predictors is None:
        print("🔧 OCRモデルを初期化中...", file=sys.stderr, flush=True)
        from surya.foundation import FoundationPredictor
        from surya.detection import DetectionPredictor
        from surya.recognition import RecognitionPredictor
        fp = FoundationPredictor()
        dp = DetectionPredictor()
        rp = RecognitionPredictor(fp)
        _predictors = (fp, dp, rp)
    return _predictors


def ocr_image_obj(img) -> str:
    from PIL import Image
    _, det_pred, rec_pred = get_predictors()
    if hasattr(img, "mode") and img.mode != "RGB":
        img = img.convert("RGB")
    results = rec_pred([img], det_predictor=det_pred)
    lines = []
    for page in results:
        for line in page.text_lines:
            if line.text.strip():
                lines.append(line.text.strip())
    return "\n".join(lines)


def ocr_file(path: Path) -> str:
    from PIL import Image
    ext = path.suffix.lower()
    if ext in SUPPORTED_IMAGE_EXTS:
        with Image.open(path) as img:
            img_copy = img.copy()
        return ocr_image_obj(img_copy)
    if ext == ".pdf":
        return ocr_pdf(path)
    return ""


def move_file_with_retry(src: Path, dst: Path, retries: int = 5, delay: float = 0.4):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            shutil.move(str(src), str(dst))
            return
        except PermissionError as e:
            last_error = e
            if attempt < retries:
                time.sleep(delay * attempt)
            else:
                raise
        except Exception as e:
            last_error = e
            raise
    if last_error:
        raise last_error


def ocr_pdf(path: Path) -> str:
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(path))
        texts = []
        try:
            for i in range(len(pdf)):
                page = pdf[i]
                bitmap = page.render(scale=2.0)
                img = bitmap.to_pil()
                texts.append(ocr_image_obj(img))
        finally:
            pdf.close()
        return "\n".join(texts)
    except ImportError:
        print(f"  ⚠️  pypdfium2 未インストール。PDFをスキップ: {path.name}", file=sys.stderr)
        return ""


# ── 情報抽出 ──────────────────────────────────────────────────────────────────

def extract_date(text: str):
    for pattern, extractor in DATE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                y, mo, d = extractor(m)
                if 2000 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
                    return datetime(y, mo, d)
            except Exception:
                continue
    return None


def extract_amount(text: str) -> str:
    candidates = []
    for pat_idx, pat in enumerate(AMOUNT_PATTERNS):
        for m in re.finditer(pat, text, re.IGNORECASE):
            raw = m.group(1)
            try:
                cleaned = re.sub(r"[,\s]", "", raw)
                val = float(cleaned)
                if val <= 0:
                    continue

                if val > MAX_RECEIPT_AMOUNT:
                    continue

                # 連結誤読の典型: 760891（小数点・区切りなしの巨大整数）
                if val >= 100000 and "." not in raw and "," not in raw and " " not in raw:
                    continue

                score = 0
                if pat_idx >= 4:
                    score += 5  # TOTAL/合計を最優先
                if "." in raw:
                    score += 3
                if "," in raw or " " in raw:
                    score += 1
                if val >= 100000 and "." not in raw:
                    score -= 6  # 760891 のような連結誤読を強く減点

                candidates.append((score, val))
            except Exception:
                continue

    if not candidates:
        return "unknown"

    # まずスコア優先、同点なら大きい額
    best = sorted(candidates, key=lambda x: (x[0], x[1]), reverse=True)[0][1]

    # 整数なら小数点なし
    if best == int(best):
        return str(int(best))
    return f"{best:.2f}"


def detect_country(text: str) -> str:
    scores = {cc: 0 for cc in COUNTRY_KEYWORDS}
    tl = text.lower()

    # 強シグナル
    jp_hits = sum(1 for kw in JP_STRONG if kw in text)
    us_hits = sum(1 for kw in US_STRONG if kw in text.upper())
    scores["jp"] += jp_hits * 2
    scores["us"] += us_hits * 2

    # キーワードスコア
    for cc, keywords in COUNTRY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in tl or kw in text:
                scores[cc] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "xx"


def detect_card(text: str) -> str | None:
    tu = text.upper()
    for card, patterns in CARD_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, tu):
                return card
    return None


def _has_food_items(text_upper: str) -> bool:
    """テキストに食品・飲料の商品明細キーワードが含まれるか判定"""
    for kw in FOOD_ITEM_KEYWORDS:
        if kw.upper() in text_upper:
            return True
    return False


def extract_summary(text: str) -> str:
    tu = text.upper()
    tl = text.lower()
    has_food = _has_food_items(tu)

    # Phase 1: 優先度順にキーワードマッチ（全カテゴリ収集）
    matched_categories = []
    for keyword, indicators in MERCHANT_MAP:
        for ind in indicators:
            if ind.upper() in tu or ind in text:
                matched_categories.append(keyword)
                break  # 同じカテゴリの次のインジケータは不要

    # Phase 2: 商品明細による再分類
    # 食品キーワードが見つかった場合、airline/transport/shopping より meal を優先
    RECLASSIFY_IF_FOOD = {"airline", "transport", "shopping", "pharmacy"}
    if has_food and matched_categories:
        # meal系カテゴリがあればそれを優先
        for cat in matched_categories:
            if cat in {"starbucks", "coffee", "restaurant", "convenience", "supermarket"}:
                return f"meal-{cat}"
            if cat == "meal":
                return "meal"
        # meal系がないが food items がある → 誤分類の可能性が高い
        if matched_categories[0] in RECLASSIFY_IF_FOOD:
            # 店舗名をスラッグ化して meal- に付ける
            for line in text.split("\n"):
                line = line.strip()
                if len(line) >= 3 and not re.match(r"^[\d\s/\-¥$¥.,*#()]+$", line):
                    if not re.search(r"\b(total|subtotal|tax|tip|amount|authorization|approved|card|visa|amex|mastercard)\b", line, re.IGNORECASE):
                        return f"meal-{slugify(line)}"
            return "meal"

    # Phase 3: 通常の分類（商品明細に食品なし）
    if matched_categories:
        keyword = matched_categories[0]
        if keyword in {"starbucks", "coffee", "restaurant", "convenience", "supermarket"}:
            return f"meal-{keyword}"
        return keyword

    # フォールバック: 食品キーワードがあるのにカテゴリ未マッチ → meal
    if has_food:
        return "meal"

    # フォールバック: 最初の意味のある行をスラッグ化
    for line in text.split("\n"):
        line = line.strip()
        if re.search(r"\b(total|subtotal|tax|tip|amount|authorization|approved|card|visa|amex|mastercard)\b", line, re.IGNORECASE):
            continue
        # 数字・記号だけの行・短すぎる行はスキップ
        if len(line) >= 4 and not re.match(r"^[\d\s/\-¥$¥.,*#()]+$", line):
            return slugify(line)

    return "receipt"


# カタカナ→ヘボン式ローマ字変換テーブル（jaconv使用、MeCab不要）
def _kana_to_romaji(text: str) -> str:
    """ひらがな・カタカナをヘボン式ローマ字に変換（jaconv使用）"""
    try:
        import jaconv
        # ひらがな→カタカナ→ヘボン式
        text = jaconv.hira2kata(text)
        text = jaconv.kata2hepburn(text)
        return text
    except (ImportError, Exception):
        return text


def slugify(text: str) -> str:
    """文字列をkebab-case ASCIIスラッグに変換。日本語はローマ字化を試みる。"""
    # ひらがな・カタカナをローマ字変換（MeCab不要）
    text = _kana_to_romaji(text)

    # Unicode正規化 → ASCII変換（漢字などは無視）
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", " ", text.lower())
    text = re.sub(r"[\s_]+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:50].strip("-") or "receipt"


# ── ファイル名生成 ─────────────────────────────────────────────────────────────

def generate_filename(text: str, ext: str) -> tuple[str, str | None]:
    """(新ファイル名, カード種別またはNone) を返す"""
    date = extract_date(text)
    if date:
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = datetime.today().strftime("%Y-%m-%d") + "x"  # 日付不明マーク

    country = COUNTRY_OUTPUT.get(detect_country(text), "xx")
    amount  = extract_amount(text)
    card    = detect_card(text)
    summary = extract_summary(text)

    parts = [date_str, country, amount]
    if card:
        parts.append(card)
    parts.append(summary)
    name = "-".join(parts) + ext
    return name, card


def parse_receipt_filename(path: Path):
    stem_parts = path.stem.split("-")
    if len(stem_parts) < 6:
        return None

    date_str = "-".join(stem_parts[:3])
    country = stem_parts[3]
    amount_token = stem_parts[4]
    rest = stem_parts[5:]

    card = None
    if rest and rest[0] in CARD_NAMES:
        card = rest[0]
        summary_parts = rest[1:]
    else:
        summary_parts = rest

    summary = "-".join(summary_parts) if summary_parts else "receipt"

    amount_value = None
    if re.fullmatch(r"\d+(?:\.\d{1,2})?", amount_token):
        amount_value = float(amount_token)

    return {
        "file": path,
        "date": date_str,
        "country": country,
        "amount_token": amount_token,
        "amount_value": amount_value,
        "card": card,
        "summary": summary,
    }


def format_amount(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}"


SUMMARY_JA_MAP = {
    "meal": "食費",
    "convenience": "コンビニ",
    "supermarket": "スーパー",
    "starbucks": "スターバックス",
    "restaurant": "レストラン",
    "coffee": "カフェ",
    "transport": "交通",
    "airline": "航空",
    "shinkansen": "新幹線",
    "hotel": "宿泊",
    "kiosk": "売店",
    "seminar": "セミナー",
    "shopping": "買い物",
    "taxi": "タクシー",
    "pharmacy": "薬局",
    "receipt": "レシート",
}

SUMMARY_DETAIL_JA_MAP = {
    "nyc-7th-ave-deli-mar": "食費（デリ）",
    "qdoba-mexican-eats": "食費（メキシカン）",
}

SUMMARY_TOKEN_JA_MAP = {
    "deli": "デリ",
    "mexican": "メキシカン",
    "qdoba": "メキシカン",
    "grill": "グリル",
    "bar": "バー",
    "market": "マーケット",
}


def summary_to_japanese(summary: str) -> str:
    # 末尾の重複回避番号（-1, -2）を除去
    base = re.sub(r"-\d+$", "", summary)
    parts = [p for p in base.split("-") if p]
    if not parts:
        return "不明"

    if base in SUMMARY_DETAIL_JA_MAP:
        return SUMMARY_DETAIL_JA_MAP[base]

    if parts[0] == "meal":
        if len(parts) >= 2:
            sub = parts[1]
            sub_ja = SUMMARY_JA_MAP.get(sub) or SUMMARY_TOKEN_JA_MAP.get(sub) or "食費"
            return f"meal（{sub} / {sub_ja}）"
        return "meal（食費）"

    if base in SUMMARY_JA_MAP:
        return SUMMARY_JA_MAP[base]

    for token in parts:
        if token in SUMMARY_JA_MAP:
            return f"{base}（{SUMMARY_JA_MAP[token]}）"
        if token in SUMMARY_TOKEN_JA_MAP:
            return f"{base}（{SUMMARY_TOKEN_JA_MAP[token]}）"

    return f"{base}（不明）"


def write_project_report(output_dir: Path, project_name: str) -> Path:
    entries = []
    for file in sorted(output_dir.glob("*")):
        if not file.is_file():
            continue
        parsed = parse_receipt_filename(file)
        if parsed:
            entries.append(parsed)

    numeric_entries = [e for e in entries if e["amount_value"] is not None]

    total_mixed = sum(e["amount_value"] for e in numeric_entries)

    country_totals = defaultdict(float)
    date_totals = defaultdict(float)
    date_country_totals = defaultdict(float)

    for entry in numeric_entries:
        country_totals[entry["country"]] += entry["amount_value"]
        date_totals[entry["date"]] += entry["amount_value"]
        date_country_totals[(entry["date"], entry["country"])] += entry["amount_value"]

    report_path = output_dir / f"{project_name}_summary.md"
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# {project_name} 領収書サマリー\n\n")
        f.write(f"- 生成日時: {now_text}\n")
        f.write(f"- 明細件数: {len(entries)}\n")
        f.write(f"- 金額算出可能件数: {len(numeric_entries)}\n")
        f.write(f"- プロジェクト合計（通貨混在・参考値）: {format_amount(total_mixed)}\n\n")

        f.write("## 国コード別合計\n\n")
        f.write("| 国コード | 合計 |\n")
        f.write("|---|---:|\n")
        for country in sorted(country_totals.keys()):
            f.write(f"| {country} | {format_amount(country_totals[country])} |\n")
        if not country_totals:
            f.write("| - | 0 |\n")

        f.write("\n## 日付別合計\n\n")
        f.write("| 日付 | 国コード | 合計 |\n")
        f.write("|---|---|---:|\n")
        for date, country in sorted(date_country_totals.keys()):
            f.write(f"| {date} | {country} | {format_amount(date_country_totals[(date, country)])} |\n")
        if not date_country_totals:
            f.write("| - | - | 0 |\n")

        f.write("\n## 明細\n\n")
        f.write("| 日付 | 国 | 金額 | カード | 分類 | 概要(日本語) | ファイル名 |\n")
        f.write("|---|---|---:|---|---|---|---|\n")
        for entry in sorted(entries, key=lambda e: e["file"].name):
            summary_ja = summary_to_japanese(entry["summary"])
            f.write(
                f"| {entry['date']} | {entry['country']} | {entry['amount_token']} | "
                f"{entry['card'] or '-'} | {entry['summary']} | {summary_ja} | {entry['file'].name} |\n"
            )

    return report_path


# ── ファイル処理 ───────────────────────────────────────────────────────────────

def safe_dst(dst_dir: Path, filename: str) -> Path:
    """重複ファイル名を避けてパスを返す"""
    dst = dst_dir / filename
    if not dst.exists():
        return dst
    stem = Path(filename).stem
    suf  = Path(filename).suffix
    counter = 1
    while dst.exists():
        dst = dst_dir / f"{stem}-{counter}{suf}"
        counter += 1
    return dst


def process_file(src: Path, output_dir: Path, unclassified_dir: Path,
                 dry_run: bool) -> dict:
    """1ファイルを処理。結果サマリーdictを返す。"""
    ext = src.suffix.lower()

    print(f"\n  📄 {src.name}", flush=True)

    # --- ZIP展開 ---
    if ext == ".zip":
        results = []
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(src) as zf:
                zf.extractall(tmpdir)
            for extracted in sorted(Path(tmpdir).rglob("*")):
                if extracted.is_file() and extracted.suffix.lower() in (SUPPORTED_IMAGE_EXTS | {".pdf"}):
                    r = process_file(extracted, output_dir, unclassified_dir, dry_run)
                    results.append(r)
        return {"src": src, "type": "zip", "children": results}

    if ext not in (SUPPORTED_IMAGE_EXTS | {".pdf"}):
        print(f"     ⚠️  非対応形式スキップ ({ext})", flush=True)
        return {"src": src, "skipped": True}

    # --- OCR ---
    try:
        text = ocr_file(src)
    except Exception as e:
        print(f"     ❌ OCRエラー: {e}", file=sys.stderr, flush=True)
        return {"src": src, "error": str(e)}

    if not text.strip():
        print(f"     ⚠️  テキスト取得不可 → 未分類へ", flush=True)
        dst_dir  = unclassified_dir
        new_name = src.name
        card     = None
    else:
        new_name, card = generate_filename(text, src.suffix.lower())
        dst_dir = output_dir

    # 同一フォルダ・同一ファイル名の場合は移動不要
    if src.parent.resolve() == dst_dir.resolve() and src.name == new_name:
        print(f"     ✅  →  {dst_dir.name}/{src.name} (変更なし)", flush=True)
        return {
            "src":      src,
            "dst":      src,
            "dst_dir":  dst_dir,
            "card":     card,
            "dry_run":  dry_run,
        }

    dst = safe_dst(dst_dir, new_name)

    status = "未分類" if dst_dir == unclassified_dir else "✅"
    print(f"     {status}  →  {dst_dir.name}/{dst.name}", flush=True)

    if not dry_run:
        dst_dir.mkdir(parents=True, exist_ok=True)
        try:
            move_file_with_retry(src, dst)
        except Exception as e:
            print(f"     ❌ 移動エラー: {e}", file=sys.stderr, flush=True)
            return {"src": src, "error": f"move failed: {e}"}

    return {
        "src":      src,
        "dst":      dst,
        "dst_dir":  dst_dir,
        "card":     card,
        "dry_run":  dry_run,
    }


# ── メイン ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OCR領収書自動仕分けツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python receipt_sorter.py --project "202602_TechConnect_Seattle"
  python receipt_sorter.py --project "202602_TechConnect_Seattle" --dry-run
  python receipt_sorter.py --project "202602_TechConnect_Seattle" --input "未仕分け/iCloud写真"
""")
    parser.add_argument("--project",  required=True,
                        help='出力プロジェクトフォルダ名 (例: 202602_TechConnect_Seattle)')
    parser.add_argument("--input",    default=None,
                        help=f"入力フォルダ (デフォルト: 未仕分け/)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="実際にファイルを移動せず結果のみ表示")
    parser.add_argument("--log",      default=None,
                        help="結果をCSVファイルに書き出す (省略時: <project>_dryrun.csv)")
    args = parser.parse_args()

    input_dir        = Path(args.input) if args.input else DEFAULT_INPUT
    output_dir       = BASE_DIR / args.project
    unclassified_dir = BASE_DIR / UNCLASSIFIED_NAME

    if not input_dir.exists():
        print(f"❌ 入力フォルダが見つかりません: {input_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(
        f for f in input_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    )

    print("═" * 60)
    print(f"📁 入力    : {input_dir}")
    print(f"📁 出力    : {output_dir}")
    print(f"📁 未分類  : {unclassified_dir}")
    print(f"🔍 対象    : {len(files)} 件")
    if args.dry_run:
        print("🔎 DRY-RUN モード（ファイルは移動しません）")
    print("═" * 60)

    results = []
    for f in files:
        r = process_file(f, output_dir, unclassified_dir, args.dry_run)
        results.append(r)

    # サマリー
    classified   = [r for r in results if "dst" in r and r.get("dst_dir") == output_dir]
    unclassified = [r for r in results if "dst" in r and r.get("dst_dir") == unclassified_dir]
    errors       = [r for r in results if "error" in r]
    skipped      = [r for r in results if r.get("skipped")]

    label = "予定" if args.dry_run else "完了"
    print("\n" + "═" * 60)
    print(f"✅ 仕分け{label} : {len(classified)} 件 → {args.project}/")
    print(f"📦 未分類    : {len(unclassified)} 件 → {UNCLASSIFIED_NAME}/")
    if errors:
        print(f"❌ エラー     : {len(errors)} 件")
    if skipped:
        print(f"⏭️  スキップ   : {len(skipped)} 件")
    print("═" * 60)

    # CSV ログ出力（PJフォルダ内の csv/ に保存）
    if args.log:
        log_path = Path(args.log)
    else:
        csv_dir = output_dir / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        suffix = "dryrun" if args.dry_run else "result"
        log_path = csv_dir / f"{args.project}_{suffix}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", newline="", encoding="utf-8-sig") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["元ファイル名", "新ファイル名", "保存先フォルダ", "カード", "備考"])
        for r in results:
            if r.get("skipped"):
                writer.writerow([r["src"].name, "", "", "", "スキップ"])
            elif "error" in r:
                writer.writerow([r["src"].name, "", "", "", f"エラー: {r['error']}"])
            elif "dst" in r:
                writer.writerow([
                    r["src"].name,
                    r["dst"].name,
                    r["dst_dir"].name,
                    r.get("card") or "未検出",
                    "dry-run" if args.dry_run else "移動済み",
                ])
    print(f"\n📋 ログ出力: {log_path}")

    if not args.dry_run:
        report_path = write_project_report(output_dir, args.project)
        print(f"📝 サマリー出力: {report_path}")

    sys.stdout.flush()


if __name__ == "__main__":
    main()
