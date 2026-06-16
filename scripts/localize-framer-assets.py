#!/usr/bin/env python3
"""Download framerusercontent.com assets and rewrite references to local paths."""

import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN = "https://framerusercontent.com"
LOCAL = ROOT / "framerusercontent"
SITE_ID = "j6NSi8nacPdId5ZW27YZz"
SITE_BASE = f"{CDN}/sites/{SITE_ID}/"

URL_RE = re.compile(
    r"https://framerusercontent\.com/(?:[a-zA-Z0-9_./-]+(?:\.[a-zA-Z0-9]+)?(?:\?[a-zA-Z0-9=&._%-]+)?)"
)
LOCAL_QUERY_URL_RE = re.compile(
    r"\./framerusercontent/([a-zA-Z0-9_./-]+(?:\.[a-zA-Z0-9]+)?\?[a-zA-Z0-9=&._%-]+)"
)


def clean_url(url: str) -> str:
    return url.split("`")[0].split("\\")[0].rstrip(".,;")


def url_to_local_path(url: str) -> Path:
    parsed = urllib.parse.urlsplit(clean_url(url))
    rel = parsed.path.lstrip("/")
    if parsed.query:
        path = Path(rel)
        safe_query = re.sub(r"[^a-zA-Z0-9._-]+", "_", parsed.query).strip("_")
        rel = (path.with_name(f"{path.stem}__{safe_query}{path.suffix}")).as_posix()
    return LOCAL / rel


def local_url(url: str) -> str:
    return f"./{url_to_local_path(url).relative_to(ROOT).as_posix()}"


def local_query_url_to_cdn(url: str) -> str:
    rel = clean_url(url).removeprefix("./framerusercontent/")
    return f"{CDN}/{rel}"


def download(url: str) -> tuple[str, bool, str]:
    url = clean_url(url)
    dest = url_to_local_path(url)
    if dest.exists() and dest.stat().st_size > 0:
        return url, True, "exists"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return url, True, f"{len(data)} bytes"
    except Exception as exc:
        return url, False, str(exc)


def collect_urls() -> set[str]:
    urls: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".html", ".mjs", ".js", ".css", ""} and path.name not in {"script"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        urls.update(clean_url(match) for match in URL_RE.findall(text))
        urls.update(local_query_url_to_cdn(match) for match in LOCAL_QUERY_URL_RE.findall(text))
    return urls


def discover_site_modules(urls: set[str]) -> None:
    queue = [u for u in urls if f"/sites/{SITE_ID}/" in u and u.endswith(".mjs")]
    seen = set(queue)
    while queue:
        batch, queue = queue[:20], queue[20:]
        for url in batch:
            ok, _ = download(url)[1:]
            if not ok:
                continue
            text = url_to_local_path(url).read_text(encoding="utf-8", errors="ignore")
            for rel in re.findall(r"(?:import\s*\(|from\s*)[`\"']\./([^`\"']+\.mjs)[`\"']", text):
                nxt = SITE_BASE + rel
                if nxt not in seen:
                    seen.add(nxt)
                    urls.add(nxt)
                    queue.append(nxt)


def rewrite_files() -> int:
    changed = 0
    targets = [p for p in ROOT.rglob("*") if p.is_file()]
    for path in targets:
        if path.is_relative_to(LOCAL) or path.suffix not in {".html", ".mjs", ".js", ".css", ""}:
            if path.name not in {"script"}:
                if not path.is_relative_to(LOCAL):
                    continue
        try:
            original = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        updated = URL_RE.sub(lambda m: local_url(clean_url(m.group(0))), original)
        updated = LOCAL_QUERY_URL_RE.sub(
            lambda m: local_url(local_query_url_to_cdn(m.group(0))),
            updated,
        )
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    urls = collect_urls()
    discover_site_modules(urls)
    urls = {u for u in urls if u != f"{CDN}/modules"}

    failed = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(download, url) for url in sorted(urls)]
        for future in as_completed(futures):
            url, ok, msg = future.result()
            if not ok:
                failed.append((url, msg))

    changed = rewrite_files()

    script_path = ROOT / "script"
    if script_path.exists():
        text = script_path.read_text(encoding="utf-8")
        updated = text.replace(
            'cdn:"https://framerusercontent.com/sites/"',
            'cdn:"./framerusercontent/sites/"',
        )
        if updated != text:
            script_path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"Downloaded {len(urls) - len(failed)}/{len(urls)} assets into {LOCAL}")
    if failed:
        print("Failed downloads:")
        for url, err in failed:
            print(f"  {url}: {err}")
    print(f"Rewrote {changed} files")


if __name__ == "__main__":
    main()
