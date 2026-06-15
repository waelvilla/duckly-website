#!/usr/bin/env python3
"""Convert a Framer save-as export into a functioning local website."""

from __future__ import annotations

import re
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN = "https://framerusercontent.com"
LOCAL = ROOT / "framerusercontent"
SITE_ID = "j6NSi8nacPdId5ZW27YZz"
SITE_BASE = f"{CDN}/sites/{SITE_ID}/"
SAVE_AS_PREFIX = "./Adion - Digital Agency Framer Template_files/"

URL_RE = re.compile(
    r"https://framerusercontent\.com/(?:[a-zA-Z0-9_./-]+(?:\.[a-zA-Z0-9]+)?(?:\?[a-zA-Z0-9=&._%-]+)?)"
)


def clean_url(url: str) -> str:
    return url.split("`")[0].split("\\")[0].rstrip(".,;")


def url_to_local_path(url: str) -> Path:
    rel = clean_url(url)[len(CDN) + 1 :]
    return LOCAL / rel


def local_url(url: str) -> str:
    return f"./{url_to_local_path(url).relative_to(ROOT).as_posix()}"


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


def prepare_html() -> None:
    index_path = ROOT / "index.html"
    content = index_path.read_text(encoding="utf-8")

    content = content.replace(SAVE_AS_PREFIX, "./")

    content = re.sub(
        r'<script>try\{if\(localStorage\.getItem\("__framer_force_showing_editorbar_since"\)\).*?</script>',
        "",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r'<link rel="modulepreload" href="https://framer\.com/edit/init\.mjs">',
        "",
        content,
    )
    content = re.sub(
        r'<style>\s*#__framer-editorbar-container \{.*?</style>',
        "",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r'<div id="__framer-editorbar-container"[^>]*>.*?</iframe>',
        "",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r'<div id="__framer-badge-container">.*?</div>\s*(?=<script data-framer-appear-animation)',
        "",
        content,
        flags=re.DOTALL,
    )

    content = content.replace(
        "Adion - Digital Agency Framer Template",
        "Duckly — Focus with Memory",
    )
    content = content.replace(
        "Adion creates colorful, playful designs that help brands stand out. We mix creative ideas with clear goals to build memorable brand experiences.",
        "Duckly is a quiet AI focus companion that helps you choose one clear outcome, work without noise, and turn each session into next steps you can actually use.",
    )

    content = content.replace(
        "https://reserved-follow-277116.framer.app/about",
        "#about",
    )
    content = content.replace(
        "https://reserved-follow-277116.framer.app/contact",
        "https://docs.google.com/forms/d/e/1FAIpQLSeIEhVFb2JYUj-_UKJpMB7HcOUd-r-tCgSvQYD97iHH9iaBEg/viewform",
    )
    content = content.replace(
        'href="https://reserved-follow-277116.framer.app/"',
        'href="./index.html"',
    )

    if 'id="about"' not in content:
        content = content.replace(
            'data-framer-name="section-about"',
            'id="about" data-framer-name="section-about"',
            1,
        )

    if "scroll-behavior: smooth" not in content:
        content = content.replace(
            '<meta name="viewport" content="width=device-width">',
            '<meta name="viewport" content="width=device-width">\n\t<style>html { scroll-behavior: smooth; }</style>',
        )

    index_path.write_text(content, encoding="utf-8")
    print("Prepared index.html")


def patch_bootstrap_files() -> None:
    for path in ROOT.glob("bootstrap*.js"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace(
            'userContent: "https://framerusercontent.com"',
            'userContent: "./framerusercontent"',
        ).replace(
            'modulesCDN: "https://framerusercontent.com/modules"',
            'modulesCDN: "./framerusercontent/modules"',
        )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"Patched {path.name}")


def patch_script_file() -> None:
    script_path = ROOT / "script"
    if not script_path.exists():
        return
    text = script_path.read_text(encoding="utf-8")
    updated = text.replace(
        'cdn:"https://framerusercontent.com/sites/"',
        'cdn:"./framerusercontent/sites/"',
    )
    if updated != text:
        script_path.write_text(updated, encoding="utf-8")
        print("Patched script analytics bootstrap")


def collect_urls() -> set[str]:
    urls: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_relative_to(LOCAL):
            continue
        if path.suffix not in {".html", ".mjs", ".js", ".css", ""} and path.name not in {
            "script"
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        urls.update(clean_url(match) for match in URL_RE.findall(text))
    return urls


def relocate_script_main() -> None:
    """Copy root script_main into the site folder so relative imports resolve."""
    site_dir = LOCAL / "sites" / SITE_ID
    site_dir.mkdir(parents=True, exist_ok=True)

    root_scripts = sorted(ROOT.glob("script_main.*.mjs"))
    if not root_scripts:
        print("No script_main.*.mjs at project root")
        return

    script_name = root_scripts[-1].name
    dest = site_dir / script_name
    shutil.copy2(root_scripts[-1], dest)
    print(f"Copied {script_name} -> {dest.relative_to(ROOT)}")

    index_path = ROOT / "index.html"
    content = index_path.read_text(encoding="utf-8")
    local_src = f"./framerusercontent/sites/{SITE_ID}/{script_name}"
    updated = re.sub(
        r'src="\./script_main\.[^"]+\.mjs"',
        f'src="{local_src}"',
        content,
    )
    if updated == content:
        updated = re.sub(
            rf'src="\./framerusercontent/sites/{re.escape(SITE_ID)}/script_main\.[^"]+\.mjs"',
            f'src="{local_src}"',
            content,
        )
    if updated != content:
        index_path.write_text(updated, encoding="utf-8")
        print(f"Updated index.html script src -> {local_src}")


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
            for rel in re.findall(
                r"(?:import\s*\(|from\s*)[`\"']\./([^`\"']+\.mjs)[`\"']", text
            ):
                nxt = SITE_BASE + rel
                if nxt not in seen:
                    seen.add(nxt)
                    urls.add(nxt)
                    queue.append(nxt)


def rewrite_files() -> int:
    changed = 0
    targets = [p for p in ROOT.rglob("*") if p.is_file()]
    for path in targets:
        if path.suffix not in {".html", ".mjs", ".js", ".css", ""} and path.name not in {
            "script"
        }:
            if not path.is_relative_to(LOCAL):
                continue
        try:
            original = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        updated = URL_RE.sub(lambda m: local_url(clean_url(m.group(0))), original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def localize_assets() -> None:
    relocate_script_main()
    urls = collect_urls()
    site_script = next(LOCAL.glob(f"sites/{SITE_ID}/script_main.*.mjs"), None)
    if site_script:
        urls.add(f"{SITE_BASE}{site_script.name}")
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
    patch_script_file()
    patch_bootstrap_files()

    print(f"Downloaded {len(urls) - len(failed)}/{len(urls)} assets into {LOCAL}")
    if failed:
        print("Failed downloads:")
        for url, err in failed:
            print(f"  {url}: {err}")
    print(f"Rewrote {changed} files")


def main() -> None:
    prepare_html()
    localize_assets()
    print("\nDone. Run: npm start")
    print("Open: http://localhost:8765/index.html")


if __name__ == "__main__":
    main()
