"""Core BEO splitting logic adapted from local tool."""
import csv
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import fitz  # PyMuPDF


# Prefer the canonical label used on BEOs: "BEO #: 35325" or "Banquet Event Order: 00201291"
# Many packets also contain mid-page notes like "Reference BEO# 37057" (no colon),
# which should NOT cause ambiguity. So we prioritize the colon form, especially in
# header/footer regions.
# Banquet Checks often use "BEO#:" (no space between BEO and #)
BEO_BANQUET_ORDER_RE = re.compile(r"\bBanquet\s+Event\s+Order\s*:\s*(\d{3,})\b", re.IGNORECASE)
BEO_HASH_NO_SPACE_RE = re.compile(r"\bBEO#\s*:\s*(\d{3,})\b", re.IGNORECASE)  # "BEO#:" no space (Banquet Checks)
BEO_COLON_RE = re.compile(r"\bBEO\s*#\s*:\s*(\d{3,})\b", re.IGNORECASE)  # "BEO #:" with space
BEO_LOOSE_RE = re.compile(r"\bBEO\s*#?\s*:?\s*(\d{3,})\b", re.IGNORECASE)

REFERENCE_LINE_HINTS = (
    "REFERENCE",
    "REFER TO",
    "REF ",
    "SPLIT BEO",
    "SPLIT BEOS",
    "NEXT DAY",
    "FROM BEO",
    "ALSO OCCURRING",
)


@dataclass(frozen=True)
class PageResult:
    page_number: int  # 1-based
    status: str  # OK | UNKNOWN | AMBIGUOUS
    beo: str  # empty unless OK
    matches: str  # comma-separated unique matches (for debugging)


def _extract_all_text(page: "fitz.Page") -> str:
    """Best-effort full-page text extraction."""
    txt = page.get_text("text") or ""
    if txt.strip():
        return txt
    blocks = page.get_text("blocks") or []
    parts: List[str] = []
    for b in blocks:
        if len(b) >= 5 and isinstance(b[4], str):
            parts.append(b[4])
    return "\n".join(parts)


def _extract_header_footer_text(page: "fitz.Page", margin_ratio: float = 0.18) -> str:
    """
    Extract text from the top/bottom of the page only.
    This helps avoid false ambiguity from mid-page notes referencing other BEOs.
    """
    rect = page.rect
    height = float(rect.height) if rect and rect.height else 0.0
    if height <= 0:
        return ""
    top_y = height * margin_ratio
    bottom_y = height * (1.0 - margin_ratio)

    blocks = page.get_text("blocks") or []
    parts: List[str] = []
    for b in blocks:
        # (x0, y0, x1, y1, text, block_no, block_type)
        if len(b) < 5 or not isinstance(b[4], str):
            continue
        y0, y1 = float(b[1]), float(b[3])
        if y1 <= top_y or y0 >= bottom_y:
            parts.append(b[4])
    return "\n".join(parts)


def _matches_from_text(regex: "re.Pattern[str]", text: str) -> Set[str]:
    return set(regex.findall(text or ""))


def _is_banquet_check(page: "fitz.Page") -> bool:
    """Detect if this page is a Banquet Check (vs regular BEO)."""
    full_text = _extract_all_text(page).upper()
    # Look for "Banquet Check" text which appears on Banquet Checks
    return "BANQUET CHECK" in full_text or "BANQUETCHECK" in full_text.replace(" ", "")


def extract_single_beo_from_page(page: "fitz.Page") -> Tuple[Optional[str], str, Set[str]]:
    """
    Returns (beo, status, matches).
    Status:
      - OK: exactly one distinct BEO detected
      - UNKNOWN: none detected
      - AMBIGUOUS: multiple distinct detected (should be reviewed)
    """
    hf_text = _extract_header_footer_text(page)
    full_text = _extract_all_text(page)

    # 1) Strongest signal: "Banquet Event Order:" in header/footer (common format).
    m = _matches_from_text(BEO_BANQUET_ORDER_RE, hf_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 2) "Banquet Event Order:" anywhere on page.
    m = _matches_from_text(BEO_BANQUET_ORDER_RE, full_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 3) "BEO#:" (no space) in header/footer - common in Banquet Checks.
    m = _matches_from_text(BEO_HASH_NO_SPACE_RE, hf_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 4) "BEO#:" (no space) anywhere on page.
    m = _matches_from_text(BEO_HASH_NO_SPACE_RE, full_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 5) "BEO #:" colon form in header/footer.
    m = _matches_from_text(BEO_COLON_RE, hf_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 6) "BEO #:" colon form anywhere on page (handles layouts where header/footer blocks aren't detected cleanly).
    m = _matches_from_text(BEO_COLON_RE, full_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 7) Fallback: loose "BEO #" match in header/footer (rare templates without colon).
    m = _matches_from_text(BEO_LOOSE_RE, hf_text)
    if len(m) == 1:
        return next(iter(m)), "OK", m
    if len(m) > 1:
        return None, "AMBIGUOUS", m

    # 8) Last resort: loose match on page, but ignore lines that look like references/notes.
    #    This keeps verification strict while supporting occasional template variations.
    candidates: Set[str] = set()
    for line in (full_text or "").splitlines():
        u = line.upper()
        if any(h in u for h in REFERENCE_LINE_HINTS):
            continue
        candidates |= _matches_from_text(BEO_LOOSE_RE, line)

    if len(candidates) == 1:
        return next(iter(candidates)), "OK", candidates
    if len(candidates) == 0:
        return None, "UNKNOWN", set()
    return None, "AMBIGUOUS", candidates


def write_report_csv(outdir: str, results: List[PageResult]) -> str:
    """Write the split report CSV file."""
    report_path = os.path.join(outdir, "split_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["page", "status", "beo", "matches"])
        w.writeheader()
        for r in results:
            w.writerow(
                {
                    "page": r.page_number,
                    "status": r.status,
                    "beo": r.beo,
                    "matches": r.matches,
                }
            )
    return report_path


def split_pdf(
    input_pdf: str,
    outdir: str,
    stop_on_problems: bool = False,
) -> Tuple[int, int, str]:
    """
    Split a PDF into individual BEO files.
    Returns: (num_beos, num_problem_pages, report_path)
    """
    os.makedirs(outdir, exist_ok=True)

    doc = fitz.open(input_pdf)
    writers: Dict[str, fitz.Document] = {}
    unknown_doc = fitz.open()
    ambiguous_doc = fitz.open()

    results: List[PageResult] = []
    problem_pages = 0
    
    # Detect if this is a Banquet Check document by checking first page
    is_banquet_check = False
    if doc.page_count > 0:
        first_page = doc.load_page(0)
        is_banquet_check = _is_banquet_check(first_page)
    
    # Determine filename prefix
    file_prefix = "BC_" if is_banquet_check else "BEO_"

    for idx in range(doc.page_count):
        page_number = idx + 1
        page = doc.load_page(idx)
        beo, status, matches = extract_single_beo_from_page(page)

        if status == "OK" and beo:
            if beo not in writers:
                writers[beo] = fitz.open()
            # Insert this page into the target doc (page range is inclusive).
            writers[beo].insert_pdf(doc, from_page=idx, to_page=idx)
            results.append(PageResult(page_number, "OK", beo, ",".join(sorted(matches))))
        elif status == "UNKNOWN":
            problem_pages += 1
            unknown_doc.insert_pdf(doc, from_page=idx, to_page=idx)
            results.append(PageResult(page_number, "UNKNOWN", "", ""))
        else:  # AMBIGUOUS
            problem_pages += 1
            ambiguous_doc.insert_pdf(doc, from_page=idx, to_page=idx)
            results.append(PageResult(page_number, "AMBIGUOUS", "", ",".join(sorted(matches))))

    report_path = write_report_csv(outdir, results)

    if stop_on_problems and problem_pages > 0:
        # Write the problem PDFs for review, but do not write per-BEO outputs.
        if unknown_doc.page_count:
            unknown_doc.save(os.path.join(outdir, "UNKNOWN_BEO.pdf"))
        if ambiguous_doc.page_count:
            ambiguous_doc.save(os.path.join(outdir, "AMBIGUOUS_BEO.pdf"))
        # Close docs
        for w in writers.values():
            w.close()
        unknown_doc.close()
        ambiguous_doc.close()
        doc.close()
        return 0, problem_pages, report_path

    # Save per-BEO PDFs with appropriate prefix
    for beo, outdoc in writers.items():
        out_path = os.path.join(outdir, f"{file_prefix}{beo}.pdf")
        outdoc.save(out_path)
        outdoc.close()

    # Save problem buckets if present
    if unknown_doc.page_count:
        unknown_doc.save(os.path.join(outdir, "UNKNOWN_BEO.pdf"))
    if ambiguous_doc.page_count:
        ambiguous_doc.save(os.path.join(outdir, "AMBIGUOUS_BEO.pdf"))

    unknown_doc.close()
    ambiguous_doc.close()
    doc.close()

    return len(writers), problem_pages, report_path


def run_ocr_if_needed(input_pdf: str, outdir: str) -> Optional[str]:
    """
    Attempts OCR using `ocrmypdf` into outdir/input_ocr.pdf and returns that path.
    Returns None if ocrmypdf is not available or OCR fails.
    """
    ocrmypdf = shutil.which("ocrmypdf")
    if not ocrmypdf:
        # Log that OCR is not available
        log_path = os.path.join(outdir, "ocrmypdf.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("ERROR: ocrmypdf not found in PATH. OCR cannot be performed.\n")
            f.write("Please ensure ocrmypdf and tesseract-ocr are installed.\n")
        return None
    
    ocr_out = os.path.join(outdir, "input_ocr.pdf")
    cmd = [
        ocrmypdf,
        "--force-ocr",  # Force OCR even if text layer exists
        "--deskew",  # Deskew pages
        "--clean",  # Clean up artifacts
        input_pdf,
        ocr_out,
    ]
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        # Log successful OCR
        log_path = os.path.join(outdir, "ocrmypdf.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("OCR completed successfully.\n")
            if result.stdout:
                f.write(f"Output: {result.stdout}\n")
        return ocr_out
    except subprocess.TimeoutExpired:
        log_path = os.path.join(outdir, "ocrmypdf.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("ERROR: OCR timed out after 5 minutes.\n")
        return None
    except subprocess.CalledProcessError as e:
        # Save OCR output log for troubleshooting.
        log_path = os.path.join(outdir, "ocrmypdf.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"ERROR: OCR failed with exit code {e.returncode}\n")
            if e.stdout:
                f.write(f"Output: {e.stdout}\n")
        return None
    except Exception as e:
        log_path = os.path.join(outdir, "ocrmypdf.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"ERROR: Unexpected error during OCR: {str(e)}\n")
        return None
