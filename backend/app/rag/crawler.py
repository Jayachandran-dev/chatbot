"""Website crawler + file ingestion."""
from __future__ import annotations
import io
import re
from typing import List, Tuple, Set
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


HEADERS = {"User-Agent": "ZenbotCrawler/1.0 (+https://zenfuture.example)"}


def fetch_url(url: str, timeout: float = 15.0) -> Tuple[str, str]:
    """Return (title, visible_text) for a URL."""
    with httpx.Client(timeout=timeout, headers=HEADERS, follow_redirects=True) as c:
        r = c.get(url)
        r.raise_for_status()
        html = r.text
    return extract_from_html(html)


def extract_from_html(html: str) -> Tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "svg"]):
        tag.decompose()
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return title, text


def crawl(start_url: str, max_pages: int = 10) -> List[Tuple[str, str, str]]:
    """Same-domain BFS. Returns list of (url, title, text)."""
    parsed = urlparse(start_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    seen: Set[str] = set()
    queue: List[str] = [start_url]
    out: List[Tuple[str, str, str]] = []
    with httpx.Client(timeout=15.0, headers=HEADERS, follow_redirects=True) as c:
        while queue and len(out) < max_pages:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            try:
                r = c.get(url)
                if r.status_code != 200 or "text/html" not in r.headers.get("content-type", ""):
                    continue
                title, text = extract_from_html(r.text)
                if text:
                    out.append((url, title, text))
                soup = BeautifulSoup(r.text, "lxml")
                for a in soup.find_all("a", href=True):
                    href = urljoin(url, a["href"]).split("#")[0]
                    if href.startswith(base) and href not in seen and len(queue) + len(out) < max_pages * 3:
                        queue.append(href)
            except Exception:
                continue
    return out


def extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def extract_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_file(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_pdf(data)
    if name.endswith(".docx"):
        return extract_docx(data)
    if name.endswith((".html", ".htm")):
        _, text = extract_from_html(data.decode("utf-8", errors="ignore"))
        return text
    # txt, md, csv, json — treat as plain text
    return data.decode("utf-8", errors="ignore")
