#!/usr/bin/env python3
"""Convert a Framer save-as export into a functioning local website."""

from __future__ import annotations

import json
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

SITE_TITLE = "Duckly — Focus with Memory"
SITE_DESCRIPTION = (
    "Duckly is a quiet AI focus companion that helps you choose one clear outcome, "
    "work without noise, and turn each session into next steps you can actually use."
)
SITE_CANONICAL = "https://duckly.app/"
SITE_FAVICON = "./favicon.svg"
OLD_FAVICONS = (
    "./framerusercontent/assets/EYWoEmOsMtYinqapjTJpDvbyM.png",
    "./framerusercontent/images/EYWoEmOsMtYinqapjTJpDvbyM.png",
    "./framerusercontent/images/c2VO3XvtRBUIMqFK9TP66uzRM.png",
)
OLD_SITE_TITLE = "Adion - Digital Agency Framer Template"
OLD_SITE_DESCRIPTION = (
    "Adion creates colorful, playful designs that help brands stand out. "
    "We mix creative ideas with clear goals to build memorable brand experiences."
)
OLD_FRAMER_URL = "https://reserved-follow-277116.framer.app"
NAVBAR_WAITLIST_BUTTON_OLD = (
    "layoutId:`HpoDd5nS4-container`,nodeId:`HpoDd5nS4`,rendersWithMotion:!0,scopeId:`vDE9BFfyG`,"
    "children:f(H,{B2127CXP5:{borderColor:`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`,"
    "borderStyle:`solid`,borderWidth:1},h_cNcTdkm:`var(--token-04892466-a786-493b-80ca-15aa801890e0, rgb(255, 255, 255))`,"
    "height:`100%`,id:`HpoDd5nS4`,IlPhTddpy:`Join the waitlist`,"
    "krcX6ZNc0:`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`"
)
NAVBAR_WAITLIST_BUTTON_NEW = (
    "layoutId:`HpoDd5nS4-container`,nodeId:`HpoDd5nS4`,rendersWithMotion:!0,scopeId:`vDE9BFfyG`,"
    "children:f(H,{B2127CXP5:{borderColor:`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`,"
    "borderStyle:`solid`,borderWidth:1},h_cNcTdkm:`var(--token-04892466-a786-493b-80ca-15aa801890e0, rgb(255, 255, 255))`,"
    "height:`100%`,id:`HpoDd5nS4`,IlPhTddpy:`Join the waitlist`,"
    "krcX6ZNc0:`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`"
)
NAVBAR_WAITLIST_BUTTON_TRANSPARENT = (
    "layoutId:`HpoDd5nS4-container`,nodeId:`HpoDd5nS4`,rendersWithMotion:!0,scopeId:`vDE9BFfyG`,"
    "children:f(H,{B2127CXP5:{borderColor:`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`,"
    "borderStyle:`solid`,borderWidth:1},h_cNcTdkm:`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`,"
    "height:`100%`,id:`HpoDd5nS4`,IlPhTddpy:`Join the waitlist`,"
    "krcX6ZNc0:`rgba(0, 0, 0, 0)`"
)
NAVBAR_WAITLIST_BUTTON_CSS = """html { scroll-behavior: smooth; }
.framer-a10wad-container .framer-qti1r7-container .framer-wWwqq,
.framer-TB78N:not(.framer-v-imxff4):not(.framer-v-1l88t2o) .framer-qti1r7-container .framer-wWwqq {
\tbackground-color: rgb(13, 13, 13) !important;
}
.framer-a10wad-container .framer-qti1r7-container .framer-wWwqq .framer-j35ygy,
.framer-a10wad-container .framer-qti1r7-container .framer-wWwqq .framer-j35ygy p,
.framer-TB78N:not(.framer-v-imxff4):not(.framer-v-1l88t2o) .framer-qti1r7-container .framer-j35ygy,
.framer-TB78N:not(.framer-v-imxff4):not(.framer-v-1l88t2o) .framer-qti1r7-container .framer-j35ygy p {
\t--extracted-r6o4lv: rgb(255, 255, 255) !important;
\t--variable-reference-h_cNcTdkm-dnIh1FUZh: rgb(255, 255, 255) !important;
\t--framer-text-color: rgb(255, 255, 255) !important;
\tcolor: rgb(255, 255, 255) !important;
}
.framer-a10wad-container .framer-qti1r7-container .framer-wWwqq:hover,
.framer-TB78N:not(.framer-v-imxff4):not(.framer-v-1l88t2o) .framer-qti1r7-container .framer-wWwqq:hover {
\tbackground-color: rgb(255, 255, 255) !important;
}
.framer-a10wad-container .framer-qti1r7-container .framer-wWwqq:hover .framer-j35ygy,
.framer-a10wad-container .framer-qti1r7-container .framer-wWwqq:hover .framer-j35ygy p,
.framer-TB78N:not(.framer-v-imxff4):not(.framer-v-1l88t2o) .framer-qti1r7-container .framer-wWwqq:hover .framer-j35ygy,
.framer-TB78N:not(.framer-v-imxff4):not(.framer-v-1l88t2o) .framer-qti1r7-container .framer-wWwqq:hover .framer-j35ygy p {
\t--extracted-r6o4lv: rgb(13, 13, 13) !important;
\t--variable-reference-h_cNcTdkm-dnIh1FUZh: rgb(13, 13, 13) !important;
\t--framer-text-color: rgb(13, 13, 13) !important;
\tcolor: rgb(13, 13, 13) !important;
}"""
NAVBAR_WAITLIST_MARKER = 'framer-qti1r7-container" style="opacity: 1;">'
WAITLIST_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSeIEhVFb2JYUj-_UKJpMB7HcOUd-r-tCgSvQYD97iHH9iaBEg/viewform"
)
HERO_WAITLIST_BUTTON_OLD = (
    'a(`div`,{className:`framer-12w6hmv`,"data-framer-name":`Button-ui-1`,children:a(R,{__fromCanvasComponent:!0,'
    'children:a(i,{children:a(`p`,{className:`framer-styles-preset-biyt9b`,"data-styles-preset":`Fs7W47lcr`,dir:`auto`,'
    'style:{"--framer-text-color":`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`},'
    "children:`Join the waitlist`})}),className:`framer-19f30tb`,fonts:[`Inter`],verticalAlignment:`top`,"
    "withExternalLayout:!0})}),"
)
HERO_WAITLIST_BUTTON_NEW = (
    f'a(`a`,{{href:`{WAITLIST_URL}`,rel:`noopener`,className:`framer-12w6hmv`,"data-framer-name":`Button-ui-1`,'
    "children:a(R,{__fromCanvasComponent:!0,"
    'children:a(i,{children:a(`p`,{className:`framer-styles-preset-biyt9b`,"data-styles-preset":`Fs7W47lcr`,dir:`auto`,'
    'style:{"--framer-text-color":`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`},'
    "children:`Join the waitlist`})}),className:`framer-19f30tb`,fonts:[`Inter`],verticalAlignment:`top`,"
    "withExternalLayout:!0})}),"
)
HERO_WAITLIST_SSR_OPEN = '<div class="framer-12w6hmv" data-framer-name="Button-ui-1">'
HERO_WAITLIST_SSR_CLOSE = (
    'Join the waitlist</p></div></div><div class="framer-a5xcbu"'
)
HERO_WAITLIST_SSR_CLOSE_LINK = (
    f'Join the waitlist</p></div></a><div class="framer-a5xcbu"'
)
HOW_IT_WORKS_ANCHOR = "#how-it-works"
HERO_HOW_IT_WORKS_BUTTON_OLD = (
    'a(`div`,{className:`framer-a5xcbu`,"data-border":!0,"data-framer-name":`Button-ui-1`,children:a(R,{__fromCanvasComponent:!0,'
    'children:a(i,{children:a(`p`,{className:`framer-styles-preset-biyt9b`,"data-styles-preset":`Fs7W47lcr`,dir:`auto`,'
    'style:{"--framer-text-color":`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`},'
    "children:`See how it works`})}),className:`framer-1kixgl2`,fonts:[`Inter`],verticalAlignment:`top`,"
    "withExternalLayout:!0})})"
)
HERO_HOW_IT_WORKS_BUTTON_NEW = (
    f'a(`a`,{{href:`{HOW_IT_WORKS_ANCHOR}`,className:`framer-a5xcbu`,"data-border":!0,"data-framer-name":`Button-ui-1`,'
    "children:a(R,{__fromCanvasComponent:!0,"
    'children:a(i,{children:a(`p`,{className:`framer-styles-preset-biyt9b`,"data-styles-preset":`Fs7W47lcr`,dir:`auto`,'
    'style:{"--framer-text-color":`var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13))`},'
    "children:`See how it works`})}),className:`framer-1kixgl2`,fonts:[`Inter`],verticalAlignment:`top`,"
    "withExternalLayout:!0})})"
)
SECTION_SERVICES_ID_OLD = 'data-framer-name="section-services"'
SECTION_SERVICES_ID_NEW = 'id="how-it-works" data-framer-name="section-services"'
SECTION_SERVICES_ID_JS_OLD = (
    'c(`section`,{className:`framer-1bpfl88`,"data-framer-name":`section-services`,'
)
SECTION_SERVICES_ID_JS_NEW = (
    'c(`section`,{id:`how-it-works`,className:`framer-1bpfl88`,"data-framer-name":`section-services`,'
)
HERO_HOW_IT_WORKS_SSR_OPEN = (
    '<div class="framer-a5xcbu" data-border="true" data-framer-name="Button-ui-1">'
)
HERO_HOW_IT_WORKS_SSR_OPEN_LINK = (
    f'<a class="framer-a5xcbu" data-border="true" data-framer-name="Button-ui-1" href="{HOW_IT_WORKS_ANCHOR}">'
)
HERO_HOW_IT_WORKS_SSR_CLOSE = (
    'See how it works</p></div></div></div></div></section><section class="framer-1bpfl88" data-framer-name="section-services"'
)
HERO_HOW_IT_WORKS_SSR_CLOSE_LINK = (
    'See how it works</p></div></a></div></div></section><section id="how-it-works" class="framer-1bpfl88" data-framer-name="section-services"'
)

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
        OLD_SITE_TITLE,
        SITE_TITLE,
    )
    content = content.replace(
        OLD_SITE_DESCRIPTION,
        SITE_DESCRIPTION,
    )

    content = content.replace(
        f"{OLD_FRAMER_URL}/about",
        "#about",
    )
    content = content.replace(
        f"{OLD_FRAMER_URL}/contact",
        WAITLIST_URL,
    )
    content = content.replace(
        f'href="{OLD_FRAMER_URL}/"',
        'href="./index.html"',
    )

    content = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{SITE_CANONICAL}">',
        content,
    )
    content = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{SITE_CANONICAL}">',
        content,
    )
    if 'property="og:site_name"' not in content:
        content = content.replace(
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Duckly">\n    <meta property="og:type" content="website">',
        )

    content = content.replace(
        OLD_FRAMER_URL,
        SITE_CANONICAL.rstrip("/"),
    )

    if 'id="about"' not in content:
        content = content.replace(
            'data-framer-name="section-about"',
            'id="about" data-framer-name="section-about"',
            1,
        )

    if 'id="how-it-works"' not in content:
        content = content.replace(
            SECTION_SERVICES_ID_OLD,
            SECTION_SERVICES_ID_NEW,
            1,
        )

    if "scroll-behavior: smooth" not in content:
        content = content.replace(
            '<meta name="viewport" content="width=device-width">',
            f'<meta name="viewport" content="width=device-width">\n\t<style>{NAVBAR_WAITLIST_BUTTON_CSS}</style>',
        )
    else:
        content = re.sub(
            r"<style>html \{ scroll-behavior: smooth; \}.*?</style>",
            f"<style>{NAVBAR_WAITLIST_BUTTON_CSS}</style>",
            content,
            count=1,
            flags=re.DOTALL,
        )

    favicon_links = (
        '    <link href="./favicon.svg" rel="icon" type="image/svg+xml">\n'
        '    <link href="./favicon.svg" rel="apple-touch-icon">'
    )
    content = re.sub(
        r'<link href="\./framerusercontent/images/[^"]+" rel="icon" media="\(prefers-color-scheme: light\)">\s*'
        r'<link href="\./framerusercontent/images/[^"]+" rel="icon" media="\(prefers-color-scheme: dark\)">',
        favicon_links,
        content,
    )
    if 'href="./favicon.svg" rel="icon"' not in content:
        content = content.replace(
            '<meta name="framer-search-index-fallback"',
            f'{favicon_links}\n    <meta name="framer-search-index-fallback"',
            1,
        )

    content = patch_navbar_waitlist_ssr(content)
    content = patch_hero_waitlist_ssr(content)
    content = patch_hero_how_it_works_ssr(content)

    index_path.write_text(content, encoding="utf-8")
    print("Prepared index.html")


def patch_navbar_waitlist_ssr(content: str) -> str:
    marker = NAVBAR_WAITLIST_MARKER
    start = content.find(marker)
    if start < 0:
        return content
    end = content.find("</a><!--/$--></div></div></nav>", start)
    if end < 0:
        return content

    chunk = content[start:end]
    chunk = chunk.replace(
        'framer-v-vd11uu hover framer-1byw23u"',
        'framer-v-vd11uu framer-1byw23u"',
    )
    for old_bg in (
        "background-color: rgba(4, 4, 4, 0.1);",
        "background-color: transparent;",
    ):
        chunk = chunk.replace(
            old_bg,
            "background-color: var(--token-bbd5a4a8-5607-4704-9a03-527afeba84bf, rgb(13, 13, 13));",
        )
    chunk = chunk.replace(
        "--extracted-r6o4lv: rgba(82, 82, 82, 1)",
        "--extracted-r6o4lv: rgb(255, 255, 255)",
    )
    chunk = chunk.replace(
        "--extracted-r6o4lv: rgb(13, 13, 13)",
        "--extracted-r6o4lv: rgb(255, 255, 255)",
    )
    chunk = chunk.replace(
        "--variable-reference-h_cNcTdkm-dnIh1FUZh: var(--token-04892466-a786-493b-80ca-15aa801890e0, rgb(255, 255, 255))",
        "--variable-reference-h_cNcTdkm-dnIh1FUZh: rgb(255, 255, 255)",
    )
    chunk = chunk.replace(
        "--variable-reference-h_cNcTdkm-dnIh1FUZh: rgb(13, 13, 13)",
        "--variable-reference-h_cNcTdkm-dnIh1FUZh: rgb(255, 255, 255)",
    )
    return content[:start] + chunk + content[end:]


def patch_seo_metadata() -> None:
    site_dir = LOCAL / "sites" / SITE_ID

    def patch_strings(obj):
        if isinstance(obj, str):
            s = obj
            s = s.replace(OLD_SITE_TITLE, SITE_TITLE)
            s = s.replace(OLD_SITE_DESCRIPTION, SITE_DESCRIPTION)
            s = s.replace("@2026 Adion inc. All Right Reserved", "@2026 Duckly.app All Right Reserved")
            s = s.replace("Adion's", "Duckly's")
            s = s.replace("Adion\u2019s", "Duckly\u2019s")
            s = s.replace("Adion inc.", "Duckly.app")
            s = s.replace("We're Adion", "We're Duckly")
            s = s.replace("We\u2019re Adion", "We\u2019re Duckly")
            s = s.replace("At Adion,", "At Duckly,")
            s = s.replace("with Adion.", "with Duckly.")
            s = s.replace("with Adion", "with Duckly")
            s = s.replace(OLD_FRAMER_URL, SITE_CANONICAL.rstrip("/"))
            s = s.replace("Adion", "Duckly")
            return s
        if isinstance(obj, list):
            return [patch_strings(x) for x in obj]
        if isinstance(obj, dict):
            return {k: patch_strings(v) for k, v in obj.items()}
        return obj

    for path in site_dir.glob("searchIndex*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(
            json.dumps(patch_strings(data), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    bundle_replacements = [
        (OLD_SITE_TITLE, SITE_TITLE),
        (OLD_SITE_DESCRIPTION, SITE_DESCRIPTION),
        (f"siteCanonicalURL:`{OLD_FRAMER_URL}`", f"siteCanonicalURL:`{SITE_CANONICAL.rstrip('/')}`"),
        (f"title:`{OLD_SITE_TITLE}`", f"title:`{SITE_TITLE}`"),
        (OLD_FRAMER_URL, SITE_CANONICAL.rstrip("/")),
    ]
    for old_favicon in OLD_FAVICONS:
        bundle_replacements.append((f"favicon:`{old_favicon}`", f"favicon:`{SITE_FAVICON}`"))
    for pattern in ["shared-lib.*.mjs", "script_main.*.mjs"]:
        for path in list(site_dir.glob(pattern)) + list(ROOT.glob(pattern)):
            text = path.read_text(encoding="utf-8", errors="ignore")
            updated = text
            for old, new in bundle_replacements:
                updated = updated.replace(old, new)
            if updated != text:
                path.write_text(updated, encoding="utf-8")

    print("Patched SEO metadata")


def patch_hero_waitlist_ssr(content: str) -> str:
    if HERO_WAITLIST_SSR_CLOSE not in content:
        return content
    content = content.replace(
        HERO_WAITLIST_SSR_OPEN,
        f'<a class="framer-12w6hmv" data-framer-name="Button-ui-1" href="{WAITLIST_URL}" rel="noopener">',
        1,
    )
    content = content.replace(HERO_WAITLIST_SSR_CLOSE, HERO_WAITLIST_SSR_CLOSE_LINK, 1)
    return content


def patch_hero_how_it_works_ssr(content: str) -> str:
    if HERO_HOW_IT_WORKS_SSR_CLOSE not in content:
        if 'href="#how-it-works"' in content and 'id="how-it-works"' in content:
            return content
        return content
    content = content.replace(
        HERO_HOW_IT_WORKS_SSR_OPEN,
        HERO_HOW_IT_WORKS_SSR_OPEN_LINK,
        1,
    )
    content = content.replace(HERO_HOW_IT_WORKS_SSR_CLOSE, HERO_HOW_IT_WORKS_SSR_CLOSE_LINK, 1)
    return content


def patch_hero_how_it_works_link() -> None:
    site_dir = LOCAL / "sites" / SITE_ID
    for path in site_dir.glob("*.mjs"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated = text
        if SECTION_SERVICES_ID_JS_OLD in updated:
            updated = updated.replace(SECTION_SERVICES_ID_JS_OLD, SECTION_SERVICES_ID_JS_NEW, 1)
        if HERO_HOW_IT_WORKS_BUTTON_OLD in updated:
            updated = updated.replace(
                HERO_HOW_IT_WORKS_BUTTON_OLD,
                HERO_HOW_IT_WORKS_BUTTON_NEW,
            )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"Patched hero how-it-works link in {path.relative_to(ROOT)}")


def patch_hero_waitlist_link() -> None:
    site_dir = LOCAL / "sites" / SITE_ID
    for path in site_dir.glob("*.mjs"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if HERO_WAITLIST_BUTTON_OLD not in text:
            continue
        updated = text.replace(HERO_WAITLIST_BUTTON_OLD, HERO_WAITLIST_BUTTON_NEW)
        path.write_text(updated, encoding="utf-8")
        print(f"Patched hero waitlist link in {path.relative_to(ROOT)}")


def patch_navbar_waitlist_button() -> None:
    site_dir = LOCAL / "sites" / SITE_ID
    for pattern in ["script_main.*.mjs"]:
        for path in list(site_dir.glob(pattern)) + list(ROOT.glob(pattern)):
            text = path.read_text(encoding="utf-8", errors="ignore")
            updated = text
            for old in (NAVBAR_WAITLIST_BUTTON_OLD, NAVBAR_WAITLIST_BUTTON_TRANSPARENT):
                if old in updated:
                    updated = updated.replace(old, NAVBAR_WAITLIST_BUTTON_NEW)
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                print(f"Patched navbar waitlist button in {path.relative_to(ROOT)}")


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
    patch_seo_metadata()
    patch_navbar_waitlist_button()
    patch_hero_waitlist_link()
    patch_hero_how_it_works_link()

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
