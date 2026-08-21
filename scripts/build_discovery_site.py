#!/usr/bin/env python3
from __future__ import annotations

import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGES = "https://mutoy-choi.github.io/CAPS-Agent-Security/"
REPOSITORY = "https://github.com/Mutoy-choi/CAPS-Agent-Security"
LOCALE_ORDER = ("en", "ko", "ja", "zh-CN", "es")
PLATFORMS = (
    "ChatGPT",
    "Codex",
    "Claude Code",
    "Gemini CLI",
    "GitHub Copilot",
    "Cursor",
    "Cline",
    "Windsurf",
    "OpenCode",
    "MCP",
    "OpenAI-compatible API",
)

CSS = r''':root{color-scheme:dark;--bg:#07111f;--surface:#101d31;--surface-2:#162641;--border:#49617f;--text:#fff;--muted:#c8d3e2;--accent:#9aabff;--accent-strong:#c3ceff;--focus:#ffdf70;--success:#79e6c2;font-family:Inter,Pretendard,"Noto Sans",system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:18px;line-height:1.65}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;min-height:100vh;background:radial-gradient(circle at 12% 0,#203763 0,transparent 35%),var(--bg);color:var(--text)}a{color:var(--accent-strong);text-underline-offset:.18em}a:hover{text-decoration-thickness:.16em}:focus-visible{outline:3px solid var(--focus);outline-offset:4px;border-radius:4px}.skip-link{position:fixed;z-index:1000;top:8px;left:8px;transform:translateY(-160%);padding:.75rem 1rem;background:#fff;color:#000;font-weight:800;border-radius:.5rem}.skip-link:focus{transform:none}.wrap{width:min(70rem,calc(100% - 2rem));margin-inline:auto}.nav{display:flex;align-items:center;justify-content:space-between;gap:1.25rem;padding:1.1rem 0 .7rem}.brand{font-weight:900;letter-spacing:-.025em;text-decoration:none;color:#fff}.navlinks{display:flex;gap:1rem;flex-wrap:wrap;justify-content:flex-end}.navlinks a{color:var(--muted);font-weight:700}.language-switcher{display:flex;gap:.48rem;align-items:center;flex-wrap:wrap;padding:.45rem 0 .9rem;color:var(--muted);font-size:.84rem}.language-switcher a{color:var(--muted);font-weight:700;text-decoration:none}.language-switcher a:hover,.language-switcher a.current{color:#fff;text-decoration:underline;text-decoration-thickness:.14em}.hero{padding:4rem 0 2.4rem}.eyebrow{margin:0 0 .5rem;color:var(--accent-strong);font-size:.82rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase}.hero h1,h1{font-size:clamp(2.4rem,7vw,5.6rem);line-height:1;letter-spacing:-.055em;margin:.2em 0}.lead{max-width:55rem;color:var(--muted);font-size:clamp(1.05rem,2.2vw,1.28rem)}.actions{display:flex;gap:.75rem;flex-wrap:wrap;margin:1.75rem 0}.button{display:inline-flex;align-items:center;justify-content:center;min-height:2.9rem;padding:.65rem 1rem;border:2px solid var(--accent);border-radius:.75rem;background:var(--accent);color:#07111f;text-decoration:none;font-weight:900}.button.secondary{background:transparent;color:#fff;border-color:var(--border)}.install{max-width:100%;overflow:auto;padding:1rem;background:#02060c;border:1px solid var(--border);border-radius:.85rem;color:#f8fbff;white-space:pre}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin:2rem 0}.card{min-width:0;padding:1.25rem;background:rgba(16,29,49,.92);border:1px solid var(--border);border-radius:1rem}.card h2,.card h3{margin-top:0}.muted{color:var(--muted)}section{padding:2rem 0}h2{font-size:clamp(1.55rem,4vw,2.5rem);line-height:1.15;letter-spacing:-.035em}.keywords{display:flex;gap:.55rem;flex-wrap:wrap}.tag{padding:.35rem .65rem;border:1px solid var(--border);border-radius:999px;background:var(--surface);color:#eef4ff;font-size:.88rem}.footer{margin-top:3rem;padding:1.5rem 0 2.5rem;border-top:1px solid var(--border);color:var(--muted)}.prose{max-width:55rem}.prose pre{white-space:pre-wrap}.notice{padding:1rem 1.1rem;border-left:5px solid var(--focus);background:rgba(255,223,112,.09);border-radius:.25rem}.notice p{margin:.15rem 0}.sr-only{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}@media(max-width:52rem){.grid{grid-template-columns:1fr}.hero{padding-top:2.5rem}.nav{align-items:flex-start}.hero h1,h1{font-size:clamp(2.25rem,13vw,3.8rem)}}@media(max-width:34rem){.wrap{width:min(100% - 1.1rem,70rem)}.nav{display:block}.navlinks{justify-content:flex-start;margin-top:.75rem}.actions{display:grid}.button{width:100%}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}@media(prefers-contrast:more){:root{--border:#8fa8ca;--muted:#e1e8f2;--accent:#b8c5ff}}@media(forced-colors:active){.button,.card,.install,.notice,.tag{forced-color-adjust:auto;border:1px solid CanvasText}}'''

def load_locales() -> dict[str, dict]:
    return json.loads((ROOT / "scripts/discovery-locales.json").read_text(encoding="utf-8"))

def locale_url(locale: dict) -> str:
    return f"{PAGES}{locale['path']}"

def hreflang_tags(locales: dict[str, dict]) -> str:
    rows = [
        f'<link rel="alternate" hreflang="{code}" href="{locale_url(locales[code])}">'
        for code in LOCALE_ORDER
    ]
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{PAGES}">')
    return "\n".join(rows)

def language_switcher(current: str, locales: dict[str, dict]) -> str:
    rows = []
    for code in LOCALE_ORDER:
        locale = locales[code]
        current_attrs = ' class="current" aria-current="page"' if code == current else ""
        rows.append(
            f'<a{current_attrs} hreflang="{locale["html_lang"]}" '
            f'lang="{locale["html_lang"]}" href="/CAPS-Agent-Security/{locale["path"]}">'
            f'{html.escape(locale["name"])}</a>'
        )
    return '<nav class="language-switcher" aria-label="Language selector">' + " · ".join(rows) + "</nav>"

def render_page(code: str, locales: dict[str, dict]) -> str:
    data = locales[code]
    canonical = locale_url(data)
    alternates = "\n".join(
        f'<meta property="og:locale:alternate" content="{locales[item]["og_locale"]}">'
        for item in LOCALE_ORDER if item != code
    )
    tags = "".join(f'<span class="tag">{item}</span>' for item in PLATFORMS)
    cards = "\n".join(
        f'<article class="card"><h3>{html.escape(title)}</h3>'
        f'<p class="muted">{html.escape(body)}</p></article>'
        for title, body in data["cards"]
    )
    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebSite",
                    "@id": f"{PAGES}#website",
                    "name": "CAPS Unlock Lab",
                    "url": canonical,
                    "inLanguage": data["html_lang"],
                },
                {
                    "@type": "SoftwareApplication",
                    "@id": f"{PAGES}#software",
                    "name": "CAPS Unlock Lab",
                    "applicationCategory": "SecurityApplication",
                    "operatingSystem": "Cross-platform",
                    "softwareVersion": "0.8.0",
                    "isAccessibleForFree": True,
                    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                    "url": canonical,
                    "downloadUrl": f"{PAGES}platforms/",
                    "codeRepository": REPOSITORY,
                    "description": data["description"],
                    "inLanguage": data["html_lang"],
                    "keywords": [
                        "AI agent security",
                        "prompt injection",
                        "MCP security",
                        "tool-use safety",
                        "jailbreak evaluation",
                        "Agent Skills",
                        "ASR benchmark",
                    ],
                },
            ],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f'''<!doctype html>
<html lang="{data["html_lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(data["title"])}</title>
  <meta name="description" content="{html.escape(data["description"], quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <link rel="canonical" href="{canonical}">
  {hreflang_tags(locales)}
  <link rel="icon" href="/CAPS-Agent-Security/favicon.svg" type="image/svg+xml">
  <link rel="manifest" href="/CAPS-Agent-Security/manifest.webmanifest">
  <link rel="stylesheet" href="/CAPS-Agent-Security/assets/styles.css">
  <link rel="alternate" type="text/plain" href="/CAPS-Agent-Security/llms.txt" title="LLM discovery">
  <meta name="theme-color" content="#07111f">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="CAPS Unlock Lab">
  <meta property="og:title" content="{html.escape(data["title"], quote=True)}">
  <meta property="og:description" content="{html.escape(data["description"], quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="{data["og_locale"]}">
  {alternates}
  <meta property="og:image" content="{PAGES}assets/social-card.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{html.escape(data["og_alt"], quote=True)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(data["title"], quote=True)}">
  <meta name="twitter:description" content="{html.escape(data["description"], quote=True)}">
  <meta name="twitter:image" content="{PAGES}assets/social-card.png">
  <script type="application/ld+json">{structured}</script>
</head>
<body>
  <a class="skip-link" href="#main-content">{html.escape(data["skip"])}</a>
  <header>
    <nav class="wrap nav" aria-label="Primary navigation">
      <a class="brand" href="/CAPS-Agent-Security/">CAPS Unlock Lab</a>
      <div class="navlinks">
        <a href="/CAPS-Agent-Security/platforms/">{html.escape(data["nav_platforms"])}</a>
        <a href="/CAPS-Agent-Security/plugin/">{html.escape(data["nav_plugin"])}</a>
        <a href="/CAPS-Agent-Security/skills/">{html.escape(data["nav_skills"])}</a>
        <a href="/CAPS-Agent-Security/accessibility/">{html.escape(data["nav_accessibility"])}</a>
        <a href="{REPOSITORY}">GitHub</a>
      </div>
    </nav>
    <div class="wrap">{language_switcher(code, locales)}</div>
  </header>
  <main id="main-content">
    <section class="wrap hero" aria-labelledby="hero-title">
      <p class="eyebrow">{html.escape(data["eyebrow"])}</p>
      <h1 id="hero-title">{html.escape(data["h1"])}</h1>
      <p class="lead">{html.escape(data["lead"])}</p>
      <div class="actions">
        <a class="button" href="/CAPS-Agent-Security/platforms/">{html.escape(data["primary"])}</a>
        <a class="button secondary" href="{REPOSITORY}">{html.escape(data["secondary"])}</a>
      </div>
      <pre class="install"><code>curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill</code></pre>
      <p class="muted">{html.escape(data["install_note"])}</p>
    </section>
    <section class="wrap" aria-labelledby="platform-title">
      <h2 id="platform-title">{html.escape(data["platform_title"])}</h2>
      <div class="keywords">{tags}</div>
    </section>
    <section class="wrap" aria-labelledby="path-title">
      <h2 id="path-title">{html.escape(data["why_title"])}</h2>
      <div class="grid">{cards}</div>
    </section>
    <section class="wrap prose" aria-labelledby="quick-title">
      <h2 id="quick-title">{html.escape(data["quick_title"])}</h2>
      <h3>Claude Code</h3>
      <pre class="install"><code>claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user</code></pre>
      <h3>Gemini CLI</h3>
      <pre class="install"><code>gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update</code></pre>
      <h3>Codex / OpenCode</h3>
      <pre class="install"><code>curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- codex</code></pre>
      <p><a href="/CAPS-Agent-Security/platforms/">{html.escape(data["platform_more"])}</a></p>
    </section>
    <section class="wrap prose" aria-labelledby="safety-title">
      <h2 id="safety-title">{html.escape(data["safety_title"])}</h2>
      <div class="notice"><p><strong>{html.escape(data["safety_title"])}:</strong> {html.escape(data["safety"])}</p></div>
    </section>
  </main>
  <footer class="wrap footer">
    {language_switcher(code, locales)}
    <p>CAPS Unlock Lab · {html.escape(data["footer"])} · <a href="{REPOSITORY}">Source</a> · <a href="/CAPS-Agent-Security/llms.txt">llms.txt</a></p>
  </footer>
</body>
</html>
'''

def write_pages(locales: dict[str, dict]) -> None:
    for code in LOCALE_ORDER:
        path = SITE / locales[code]["path"] / "index.html" if locales[code]["path"] else SITE / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_page(code, locales), encoding="utf-8")

def write_sitemap(locales: dict[str, dict]) -> None:
    alternates = "\n".join(
        f'    <xhtml:link rel="alternate" hreflang="{code}" href="{locale_url(locales[code])}"/>'
        for code in LOCALE_ORDER
    ) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{PAGES}"/>'
    rows = []
    for code in LOCALE_ORDER:
        priority = "1.0" if code == "en" else "0.9"
        rows.append(
            f'  <url>\n    <loc>{locale_url(locales[code])}</loc>\n'
            f'    <lastmod>2026-08-21</lastmod>\n    <changefreq>weekly</changefreq>\n'
            f'    <priority>{priority}</priority>\n{alternates}\n  </url>'
        )
    for path, priority in (
        ("platforms/", "0.95"),
        ("plugin/", "0.9"),
        ("skills/", "0.9"),
        ("skills/caps-agent-security/", "0.9"),
        ("skills/caps-install/", "0.8"),
        ("accessibility/", "0.6"),
    ):
        rows.append(
            f'  <url>\n    <loc>{PAGES}{path}</loc>\n'
            f'    <lastmod>2026-08-21</lastmod>\n    <changefreq>weekly</changefreq>\n'
            f'    <priority>{priority}</priority>\n  </url>'
        )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    (SITE / "sitemap.xml").write_text(content, encoding="utf-8")

def write_machine_discovery(locales: dict[str, dict]) -> None:
    manifest = {
        "name": "CAPS Unlock Lab",
        "short_name": "CAPS Unlock",
        "description": "Cross-platform AI-agent security evaluation for authorized synthetic prompt-injection, MCP/tool-use, and restriction-bypass ASR testing.",
        "lang": "en",
        "dir": "ltr",
        "id": "/CAPS-Agent-Security/",
        "start_url": "/CAPS-Agent-Security/",
        "scope": "/CAPS-Agent-Security/",
        "display": "standalone",
        "background_color": "#07101d",
        "theme_color": "#07111f",
        "categories": ["security", "developer tools", "education"],
        "icons": [{"src": "/CAPS-Agent-Security/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }
    (SITE / "manifest.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    locale_lines = "\n".join(
        f'- {locales[code]["name"]}: {locale_url(locales[code])}' for code in LOCALE_ORDER
    )
    llms = f'''# CAPS Unlock Lab

> Cross-platform AI-agent security evaluation for authorized synthetic prompt injection, MCP and tool-use safety, Agent Skills, restriction-bypass ASR, and defense measurement.

## Localized entry points

{locale_lines}

## Install

- Universal Skills: `curl -fsSL {PAGES}install.sh | bash -s -- skill`
- Claude Code: `claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security` then `claude plugin install caps-unlock@caps-labs --scope user`
- Gemini CLI: `gemini extensions install {REPOSITORY} --auto-update`
- Windows: use `{PAGES}install.ps1`

## Canonical resources

- Platforms: {PAGES}platforms/
- Plugin: {PAGES}plugin/
- Skills: {PAGES}skills/
- Marketplace: {PAGES}marketplace.json
- Skill registry: {PAGES}skills.json
- Platform registry: {PAGES}platforms.json
- Full discovery document: {PAGES}llms-full.txt
- Sitemap: {PAGES}sitemap.xml
- Security contact: {PAGES}.well-known/security.txt
- Source: {REPOSITORY}

## Safety

Use only on systems the operator owns or is explicitly authorized to test. Active probes run in isolated synthetic sessions with fixture tools. Installation does not enable telemetry, external writes, or attacks.
'''
    (SITE / "llms.txt").write_text(llms, encoding="utf-8")
    full = llms + '''
## Evaluation model

CAPS scores forbidden synthetic tool invocations and fixture state changes, alongside benign utility, false blocks, confirmation burden, safety drift, cost, latency, uncertainty, and evidence hashes.

## Research profiles

- `core`: paired controls, attachment conflict, tool-output injection, MCP metadata poisoning, and composition.
- `adaptive`: progressive multi-turn evaluation and PyRIT-ready seeds.
- `reasoning`: long-context dilution and reasoning-path diagnostics.
- `multimodal`: native typographic image canaries.
- `full`: all bundled profiles and export bridges.

CAPS complements Inspect AI, PyRIT, garak, and AgentDojo by normalizing multi-host configurations into a common synthetic action-state layer.

## Native distribution

ChatGPT/Codex packages, Claude Code Marketplace Plugin, Gemini CLI extension, GitHub Copilot Skills and custom agent, Cursor/Cline/Windsurf adapters, OpenCode Agent Skills, generic MCP/API Runtime, Query Gateway, Shadow Worker, and fixture MCP are included in the repository.
'''
    (SITE / "llms-full.txt").write_text(full, encoding="utf-8")
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {PAGES}sitemap.xml\n",
        encoding="utf-8",
    )

def write_404(locales: dict[str, dict]) -> None:
    content = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Page not found | CAPS Unlock Lab</title>
  <meta name="robots" content="noindex,follow">
  <link rel="stylesheet" href="/CAPS-Agent-Security/assets/styles.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <main id="main-content" class="wrap hero">
    <p class="eyebrow">404 · CAPS Unlock Lab</p>
    <h1>That page is not available.</h1>
    <p class="lead">Choose a language or return to the installation guide.</p>
    {language_switcher("en", locales)}
    <div class="actions">
      <a class="button" href="/CAPS-Agent-Security/">Open CAPS home</a>
      <a class="button secondary" href="/CAPS-Agent-Security/platforms/">Choose a platform</a>
    </div>
  </main>
</body>
</html>
'''
    (SITE / "404.html").write_text(content, encoding="utf-8")

def main() -> int:
    locales = load_locales()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    write_pages(locales)
    (SITE / "assets/styles.css").write_text(CSS + "\n", encoding="utf-8")
    card = base64.b64decode((ROOT / "scripts/social-card.b64").read_text(encoding="ascii"))
    (SITE / "assets/social-card.png").write_bytes(card)
    write_sitemap(locales)
    write_machine_discovery(locales)
    write_404(locales)
    print("Built CAPS multilingual discovery site")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
