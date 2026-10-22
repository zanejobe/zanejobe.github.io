#!/usr/bin/env python3
# Run from repo root: python3 scripts/generate_publications_ris.py

"""Generate NCBI-compatible RIS from _includes/publications-from-cv.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "_includes" / "publications-from-cv.md"
DEFAULT_OUTPUT = REPO_ROOT / "files" / "Zane_Jobe_publications.ris"

JOURNALS = sorted(
    [
        "Palaeogeography, Palaeoclimatology, Palaeoecology",
        "Journal of Geophysical Research Earth Surface",
        "Journal of South American Earth Sciences",
        "Earth and Planetary Science Letters",
        "Geological Society of America Bulletin",
        "Journal of the Geological Society",
        "Journal of Open-Source Software",
        "Journal of Sedimentary Research",
        "Marine and Petroleum Geology",
        "Geological Society, London, Special Publications",
        "The Depositional Record",
        "The Sedimentary Record",
        "Frontiers in Earth Science",
        "Basin Research",
        "Marine Geology",
        "Sedimentologika",
        "Sedimentology",
        "Geosphere",
        "Geology",
    ],
    key=len,
    reverse=True,
)

BOOK_TITLE_SEPM = (
    "Stratigraphic Evolution of Deep-Water Architecture: Examples on controls and "
    "depositional styles from the Magallanes Basin, Chile"
)
BOOK_TITLE_GCS = "Answering the Challenges of Production from Deep-water Reservoirs"
BOOK_TITLE_USGS = (
    "Science to support adaptive habitat management–Overton Bottoms North Unit, "
    "Big Muddy National Fish and Wildlife Refuge, Missouri"
)
BOOK_TITLE_AGILE = "52 Things You Should Know About Geology"
PUB_MISSOURI = "Missouri Division of Geology and Land Survey"

# Known citation typos in the source markdown.
SOURCE_FIXES: dict[int, tuple[str, str]] = {
    18: ("Lutz, B.P. Da Gama, R.", "Lutz, B.P., Da Gama, R."),
    32: ("Hunt, J. Jackson, C.", "Hunt, J., Jackson, C."),
    19: ("Girardclos, S. Hansen, E.", "Girardclos, S., Hansen, E."),
}


def extract_doi(text: str) -> str | None:
    match = re.search(r"https?://doi\.org/(\S+?)(?:\]|\s|$)", text, re.I)
    if match:
        return match.group(1).rstrip(".,;)")
    match = re.search(r"\bdoi:\s*(\S+?)(?:\]|\s|$)", text, re.I)
    if match:
        return match.group(1).rstrip(".,;)")
    return None


def strip_md(text: str) -> str:
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: match.group(2) if "doi.org" in match.group(2).lower() else "",
        text,
    )
    text = re.sub(r"https?://doi\.org/\S+", "", text)
    text = re.sub(r"\bdoi:\s*\S+", "", text, flags=re.I)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip(" ,.;")
    return text


def is_initials(token: str) -> bool:
    return bool(re.fullmatch(r"(?:[A-Z]\.?\s*){1,4}", token.strip()))


def split_authors(authors_raw: str) -> list[str]:
    authors_text = authors_raw.strip().rstrip(",")
    authors_text = authors_text.replace("&", "and")
    authors_text = re.sub(r",?\s+and\s+", ", and ", authors_text)
    parts = [part.strip() for part in re.split(r",\s*", authors_text) if part.strip()]
    parts = [re.sub(r"^and\s+", "", part).strip() for part in parts]

    authors: list[str] = []
    index = 0
    while index < len(parts):
        part = parts[index]
        if re.fullmatch(r"(IV|III|II|Jr\.?|Sr\.?)", part, re.I):
            if authors:
                authors[-1] = authors[-1] + ", " + part
            index += 1
            continue

        surname = part
        if index + 1 < len(parts):
            nxt = parts[index + 1]
            if nxt.lower() in ("editors", "editor", "eds", "ed", "eds."):
                authors.append(surname)
                index += 1
                continue
            if is_initials(nxt) or re.fullmatch(r"[A-Z][a-z]{1,10}", nxt):
                given = nxt
                index += 2
                if index < len(parts) and re.fullmatch(
                    r"(IV|III|II|Jr\.?|Sr\.?)", parts[index], re.I
                ):
                    given = given + ", " + parts[index]
                    index += 1
                authors.append(f"{surname}, {given}")
                continue

        authors.append(surname)
        index += 1

    cleaned: list[str] = []
    for author in authors:
        author = re.sub(r"\s+", " ", author).strip(" ,")
        if not author or author.lower() in ("and", "editors", "editor", "eds", "ed"):
            continue
        if re.fullmatch(r"[A-Z]\.?", author):
            continue
        cleaned.append(author)
    return cleaned


def find_journal(text: str) -> tuple[int, str] | None:
    lowered = text.lower()
    for journal in JOURNALS:
        index = lowered.find(journal.lower())
        if index != -1:
            return index, journal
    return None


def parse_vol_pages(text: str) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    vol = iss = sp = ep = article = None
    match = re.search(r"(\d+)\s*\((\d+)\)\s*[:.]?\s*(\d+)\s*[–—-]\s*(\d+)", text)
    if match:
        return match.group(1), match.group(2), match.group(3), match.group(4), None

    match = re.search(r"(\d+)\s*\((\d+)\)", text)
    if match:
        vol, iss = match.group(1), match.group(2)

    match = re.search(r"\bv(?:ol)?\.?\s*(\d+)\b", text, re.I)
    if match:
        vol = match.group(1)

    match = re.search(r"\bno\.?\s*(\d+)\b", text, re.I)
    if match:
        iss = match.group(1)

    match = re.search(r"\bp{1,2}\.?\s*(\d+)\s*[–—-]\s*(\d+)", text, re.I)
    if match:
        sp, ep = match.group(1), match.group(2)
    else:
        match = re.search(r"(?<![.\d])(\d{1,4})\s*[–—-]\s*(\d{1,4})\b", text)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            if not (1900 <= start <= 2035):
                sp, ep = str(start), str(end)

    match = re.search(r"\b(e\d+)\b", text)
    if match:
        article = match.group(1)

    match = re.search(r"\b(SP\d+(?:\.\d+)?)\b", text)
    if match:
        article = match.group(1)

    return vol, iss, sp, ep, article


def authors_end_before_title(before: str) -> tuple[str, str]:
    """Split author list from title when year is missing."""
    parts = [part.strip() for part in re.split(r",\s*", before) if part.strip()]
    index = 0
    last = 0
    while index < len(parts):
        if index + 1 >= len(parts):
            break
        nxt = parts[index + 1]
        if is_initials(nxt):
            index += 2
            if index < len(parts) and re.fullmatch(
                r"(IV|III|II|Jr\.?|Sr\.?)", parts[index], re.I
            ):
                index += 1
            last = index
        else:
            break
    if last == 0:
        return before, ""
    return ", ".join(parts[:last]), ", ".join(parts[last:])


def parse_published_papers(source_text: str) -> list[tuple[int, str, str | None]]:
    start = source_text.find("### Published")
    end = source_text.find("</div>")
    block = source_text[start:end]

    section_year: str | None = None
    papers: list[tuple[int, str, str | None]] = []
    for line in block.splitlines():
        year_match = re.match(r"^####\s+(\d{4})\s*$", line.strip())
        if year_match:
            section_year = year_match.group(1)
            continue
        entry_match = re.match(r"^(\d+)\\.\s+(.*)$", line.strip())
        if entry_match:
            papers.append((int(entry_match.group(1)), entry_match.group(2).strip(), section_year))
    return papers


def build_ris_record(
    num: int, raw: str, section_year: str | None
) -> tuple[str | None, str | None]:
    if num in SOURCE_FIXES:
        old, new = SOURCE_FIXES[num]
        if old != new:
            raw = raw.replace(old, new)

    doi = extract_doi(raw)
    body = strip_md(raw)
    body = re.sub(r"\s*####\s*\d{4}.*$", "", body).strip()

    year: str | None = None
    authors_raw: str | None = None
    rest: str | None = None

    match = re.match(r"^(.+?)\s*\((\d{4})\)\.\s*(.*)$", body)
    if match:
        authors_raw, year, rest = match.group(1), match.group(2), match.group(3)
    else:
        match = re.match(r"^(.+?),\s*(\d{4})[.,]\s*(.*)$", body)
        if match:
            authors_raw, year, rest = match.group(1), match.group(2), match.group(3)

    if not year:
        year = section_year
        journal_match = find_journal(body)
        if "URTEC" in body:
            match = re.search(r"\bURTEC", body)
            before = body[: match.start()].rstrip(" ,.")
            authors_raw, title_part = authors_end_before_title(before)
            rest = (title_part + " " + body[match.start() :]).strip()
        elif journal_match:
            index, _ = journal_match
            before = body[:index].rstrip(" ,.").rstrip(".")
            authors_raw, title_part = authors_end_before_title(before)
            rest = (title_part + ". " + body[index:]).strip()
        else:
            return None, "cannot split without year"

    authors = split_authors(authors_raw or "")

    record_type = "JOUR"
    title: str | None = None
    journal: str | None = None
    book_title: str | None = None
    vol = iss = sp = ep = article = None
    isbn: str | None = None
    publisher: str | None = None

    if "URTEC" in (rest or ""):
        record_type = "CONF"
        match = re.search(r"(URTEC[-\w]*)", rest or "")
        title = (rest or "")[: match.start()].strip(" ,.:;") if match else rest
        journal = "URTeC"
        vol = match.group(1) if match else None
    elif "Agile Libre" in (rest or "") or "52 Things You Should Know About Geology" in (rest or ""):
        record_type = "CHAP"
        title = "Turbidity currents and submarine channels"
        book_title = BOOK_TITLE_AGILE
        publisher = "Agile Libre"
        match = re.search(r"ISBN:\s*([\d-]+)", rest or "")
        if match:
            isbn = match.group(1)
    elif "SEPM Field Trip Guidebook" in (rest or "") or ", in Fildani" in (rest or ""):
        record_type = "CHAP"
        match = re.match(r"^(.+?),\s*in\b", rest or "")
        title = match.group(1).strip() if match else (rest or "").split(",")[0]
        book_title = BOOK_TITLE_SEPM
        publisher = "SEPM"
        vol = "10"
        match = re.search(r"pp\.\s*(\d+)\s*[–—-]\s*(\d+)", rest or "")
        if match:
            sp, ep = match.group(1), match.group(2)
    elif "GCS-SEPM" in (rest or "") or "Bob F. Perkins" in (rest or ""):
        record_type = "CHAP"
        match = re.match(r"^(.+?),\s*in:", rest or "")
        title = match.group(1).strip() if match else (rest or "").split(", in")[0]
        book_title = BOOK_TITLE_GCS
        publisher = "GCS-SEPM Foundation"
        match = re.search(r"pp\.\s*(\d+)\s*[–—-]\s*(\d+)", rest or "")
        if match:
            sp, ep = match.group(1), match.group(2)
    elif "chap. 2 of Jacobson" in (rest or "") or "Scientific Investigations Report" in (rest or ""):
        record_type = "CHAP"
        match = re.match(r"^(.+?)\s+in the Missouri River Valley", rest or "")
        if match:
            title = (
                match.group(1).strip()
                + " in the Missouri River Valley and its potential influence on environmental management"
            )
        else:
            title = (rest or "").split(", chap.")[0].strip()
        book_title = BOOK_TITLE_USGS
        publisher = "U.S. Geological Survey"
        vol = "2006-5086"
        match = re.search(r"p\.\s*(\d+)\s*[–—-]\s*(\d+)", rest or "")
        if match:
            sp, ep = match.group(1), match.group(2)
    elif "Surficial material map" in (rest or "") or "Open-File Report" in (rest or ""):
        record_type = "MAP"
        match = re.match(r"^(.+?):\s*Missouri Division", rest or "")
        title = match.group(1).strip() if match else (rest or "").split(":")[0].strip()
        book_title = PUB_MISSOURI
        publisher = PUB_MISSOURI
    else:
        journal_match = find_journal(rest or "")
        if journal_match:
            index, journal = journal_match
            title = (rest or "")[:index].strip(" ,.:;")
            after = (rest or "")[index + len(journal) :].strip(" ,.:;")
            vol, iss, sp, ep, article = parse_vol_pages(after)
            if "Special Publications" in journal:
                record_type = "CHAP"
                book_title = journal
                journal = None
        else:
            match = re.match(r"^(.+?[.?!])\s+(.+)$", rest or "")
            if match:
                title = match.group(1).rstrip(".")
                after = match.group(2)
                journal = after.split(",")[0].strip()
                vol, iss, sp, ep, article = parse_vol_pages(after)
            else:
                title = rest
                record_type = "GEN"

    title = re.sub(r"\s+", " ", (title or "")).strip(" ,.*")
    title = title.replace("*", "").strip()
    if title.endswith(":"):
        title = title[:-1].strip()

    if not title or len(title) < 5:
        return None, "bad title"
    if not authors:
        return None, "no authors"

    if not year and doi:
        year_match = re.search(r"(20\d{2}|19\d{2})", doi)
        if year_match:
            year = year_match.group(1)
    if not year:
        year = section_year or "n.d."

    lines = [f"TY  - {record_type}"]
    for author in authors:
        lines.append(f"AU  - {author}")
    lines.append(f"TI  - {title}")
    if journal:
        lines.append(f"JO  - {journal}")
    if book_title:
        lines.append(f"T2  - {book_title}")
    if publisher:
        lines.append(f"PB  - {publisher}")
    lines.append(f"PY  - {year}")
    lines.append(f"Y1  - {year}///")
    if vol:
        lines.append(f"VL  - {vol}")
    if iss:
        lines.append(f"IS  - {iss}")
    if sp:
        lines.append(f"SP  - {sp}")
    if ep:
        lines.append(f"EP  - {ep}")
    if article and not sp:
        lines.append(f"SP  - {article}")
    if isbn:
        lines.append(f"SN  - {isbn}")
    if doi:
        lines.append(f"DO  - {doi}")
        lines.append(f"UR  - https://doi.org/{doi}")
    lines.append(f"ID  - jobe-{num}")
    lines.append("ER  - ")
    return "\n".join(lines), None


def generate_ris(source_path: Path, output_path: Path) -> int:
    papers = parse_published_papers(source_path.read_text())
    records: list[str] = []
    issues: list[tuple[int, str]] = []

    for num, raw, section_year in sorted(papers, key=lambda item: -item[0]):
        ris, issue = build_ris_record(num, raw, section_year)
        if ris:
            records.append(ris)
        else:
            issues.append((num, issue or "unknown error"))

    if issues:
        details = ", ".join(f"{num} ({reason})" for num, reason in issues)
        raise RuntimeError(f"Failed to build {len(issues)} record(s): {details}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(records) + "\n")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate NCBI-compatible RIS from publications-from-cv.md."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Source markdown (default: {DEFAULT_INPUT.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output RIS file (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    args = parser.parse_args()

    count = generate_ris(args.input, args.output)
    print(f"Wrote {count} records -> {args.output}")


if __name__ == "__main__":
    main()
