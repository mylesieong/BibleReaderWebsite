#!/usr/bin/env python3
"""Static site generator for the Footlamp marketing site.

Emits plain HTML into the repository root so the result can be served by
GitHub Pages (or any static host) with no build step at serve time. Run it
after editing this file or `_data/topics.json`, then commit the output:

    python3 build.py

Content is written against `docs/app_description_external_facing.md` and
`docs/store-listing.md` in the app repository. The copy rules in
store-listing.md section 7 apply here too - in particular: no audio claims,
keyword search is not AI, KJV and ESV only, and "Father AI" is capitalised.
"""

from __future__ import annotations

import html
import json
import pathlib
import re

from datetime import date

# --- Site constants ----------------------------------------------------------
# BASE_URL must be the site's real, final origin + path, with a trailing slash.
# It is used for canonical URLs, Open Graph URLs, JSON-LD and sitemap.xml only;
# every in-page link is relative, so the site works under any path.
BASE_URL = "https://saivsreality.com/products/footlamp/"

SITE_NAME = "Footlamp"
APP_NAME = "Footlamp: Bible & Ask AI"
PUBLISHER = "Municornio Ltd."
CONTACT_EMAIL = "unicornio.macau@gmail.com"
PRIVACY_URL = "https://saivsreality.com/products/footlamp/privacy-policy.html"
TERMS_URL = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"

# The App Store URL is by numeric id only, so it survives store-name changes.
APP_STORE_URL = "https://apps.apple.com/app/id6504839289"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.municornio.biblereader"

BUILD_DATE = date.today().isoformat()

ROOT = pathlib.Path(__file__).parent
TOPICS = json.loads((ROOT / "_data" / "topics.json").read_text(encoding="utf-8"))

# --- Small helpers -----------------------------------------------------------


def e(text: str) -> str:
    """Escape text for use in HTML content and attributes."""
    return html.escape(text, quote=True)


def depth_prefix(slug: str) -> str:
    """Relative path back to the site root from a page's directory."""
    return "" if slug == "" else "../"


def abs_url(slug: str) -> str:
    return BASE_URL if slug == "" else f"{BASE_URL}{slug}/"


# --- Shared chrome -----------------------------------------------------------

NAV = [
    ("#features", "Features"),
    ("ai-bible-study-assistant", "Father AI"),
    ("offline-bible-app", "Offline"),
    ("verse-of-the-day", "Verse of the Day"),
    ("#faq", "FAQ"),
]

FOOTER_COLUMNS = [
    (
        "The app",
        [
            ("#features", "Features"),
            ("offline-bible-app", "Offline Bible"),
            ("ai-bible-study-assistant", "Father AI"),
            ("kjv-vs-esv", "KJV vs ESV"),
            ("verse-of-the-day", "Verse of the Day"),
            ("bible-app-without-ads", "No ads, no account"),
        ],
    ),
    (
        "Read by topic",
        [
            ("bible-verses-about-anxiety", "Anxiety"),
            ("bible-verses-about-hope", "Hope"),
            ("bible-verses-about-healing", "Healing"),
            ("bible-verses-about-encouragement", "Encouragement"),
        ],
    ),
]


def link_href(prefix: str, href: str) -> str:
    """A nav target: "#anchor" is a fragment on the home page, anything else a page."""
    return f"{prefix}{href}" if href.startswith("#") else f"{prefix}{href}/"


def header(slug: str) -> str:
    p = depth_prefix(slug)
    items = []
    for href, label in NAV:
        target = link_href(p, href)
        current = ' aria-current="page"' if href == slug else ""
        items.append(f'<a href="{target}"{current}>{e(label)}</a>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{p}">
      <img src="{p}assets/img/app-logo.png" width="30" height="30" alt="" loading="eager" decoding="async">
      <span>{e(SITE_NAME)}</span>
    </a>
    <nav class="site-nav" aria-label="Primary">
      {"".join(items)}
    </nav>
  </div>
</header>"""


def footer(slug: str) -> str:
    p = depth_prefix(slug)
    cols = []
    for title, links in FOOTER_COLUMNS:
        lis = "".join(
            f'<li><a href="{link_href(p, href)}">{e(label)}</a></li>'
            for href, label in links
        )
        cols.append(f"<div><h2>{e(title)}</h2><ul>{lis}</ul></div>")
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>{e(SITE_NAME)}</h2>
        <p>A Bible you can read anywhere, with an AI that answers when you have a
        question. King James Version and English Standard Version, carried on your
        device. Android and iOS.</p>
        <p><a href="{PRIVACY_URL}">Privacy Policy</a> &middot;
           <a href="{TERMS_URL}">Terms of Use</a> &middot;
           <a href="mailto:{CONTACT_EMAIL}">Contact</a></p>
        <p>Part of <a href="https://mylesieong.github.io/">Sai vs. Reality</a></p>
      </div>
      {"".join(cols)}
    </div>
    <p class="colophon">&copy; {date.today().year} {e(PUBLISHER)}. Scripture quotations on this
    site are from the King James Version, which is in the public domain. The English Standard
    Version is available inside the app. There is no web reader &mdash; {e(SITE_NAME)} is an
    Android and iOS app.</p>
  </div>
</footer>"""


def store_buttons(extra_class: str = "") -> str:
    return f"""<div class="cta-row {extra_class}">
  <a class="btn btn-primary" href="{APP_STORE_URL}">Download on the App&nbsp;Store</a>
  <a class="btn btn-secondary" href="{PLAY_STORE_URL}">Get it on Google&nbsp;Play</a>
</div>
<p class="small muted">Free. No ads, no sign-up, no account. Android and iOS.</p>"""


def band(heading: str, body: str) -> str:
    return f"""<section aria-labelledby="cta-heading"><div class="wrap"><div class="band">
  <h2 id="cta-heading">{heading}</h2>
  <p class="lead">{body}</p>
  {store_buttons()}
</div></div></section>"""


def breadcrumbs(slug: str, label: str) -> str:
    return f"""<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap"><ol>
  <li><a href="../">{e(SITE_NAME)}</a></li>
  <li aria-current="page">{e(label)}</li>
</ol></div></nav>"""


def breadcrumb_ld(slug: str, label: str) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": label, "item": abs_url(slug)},
        ],
    }


# --- Page shell --------------------------------------------------------------


def page(slug: str, title: str, description: str, body: str, jsonld: list[dict],
         og_type: str = "website", filename: str | None = None) -> None:
    """Write one page to <slug>/index.html (or index.html at the root).

    `filename` writes a flat file of that name at the root instead, for pages
    like the privacy policy whose URL is fixed by an app-store listing."""
    p = depth_prefix(slug)
    url = BASE_URL + filename if filename else abs_url(slug)
    graph = json.dumps(
        {"@context": "https://schema.org", "@graph": jsonld},
        ensure_ascii=False, separators=(",", ":"),
    )
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#FBFBFB">
<meta name="color-scheme" content="light">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="{e(PUBLISHER)}">

<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(SITE_NAME)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="en_CA">
<meta property="og:image" content="{BASE_URL}assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(SITE_NAME)} app icon">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{BASE_URL}assets/img/og-image.png">

<link rel="icon" href="{p}assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{p}assets/img/icon-180.png">
<link rel="stylesheet" href="{p}assets/css/site.css">

<script type="application/ld+json">{graph}</script>
</head>
<body>
{header(slug)}
<main id="main">
{body}
</main>
{footer(slug)}
</body>
</html>
"""
    if filename:
        out = ROOT / filename
    else:
        out = ROOT / "index.html" if slug == "" else ROOT / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"  {out.relative_to(ROOT)}")


# --- Structured data ---------------------------------------------------------

ORGANISATION = {
    "@type": "Organization",
    "@id": f"{BASE_URL}#publisher",
    "name": PUBLISHER,
    "url": BASE_URL,
    "email": CONTACT_EMAIL,
    "logo": f"{BASE_URL}assets/img/app-logo.png",
}

WEBSITE = {
    "@type": "WebSite",
    "@id": f"{BASE_URL}#website",
    "name": SITE_NAME,
    "url": BASE_URL,
    "inLanguage": "en",
    "publisher": {"@id": f"{BASE_URL}#publisher"},
}

SOFTWARE_APP = {
    "@type": "MobileApplication",
    "@id": f"{BASE_URL}#app",
    "name": APP_NAME,
    "alternateName": SITE_NAME,
    "applicationCategory": "BooksApplication",
    "operatingSystem": "iOS, Android",
    "url": BASE_URL,
    "image": f"{BASE_URL}assets/img/app-logo.png",
    "description": (
        "An offline Bible reader for iOS and Android with the King James Version "
        "and English Standard Version on the device, plus Father AI to answer "
        "questions and explain any verse. No ads and no account."
    ),
    "publisher": {"@id": f"{BASE_URL}#publisher"},
    "installUrl": [APP_STORE_URL, PLAY_STORE_URL],
    "featureList": [
        "Full KJV and ESV text bundled on the device",
        "Works offline for reading, search, topics and the verse of the day",
        "Father AI answers questions and explains verses in plain language",
        "Compare a verse side by side across translations",
        "On-device keyword search across the whole Bible",
        "Verse of the day with a guided prayer and reflection",
        "Topic collections for anxiety, hope, healing and encouragement",
        "Daily reminder notification",
        "No advertising and no account",
    ],
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD",
        "description": (
            "Free to download. Reading, translations, search, topics, verse compare and "
            "the verse of the day are free and unlimited. Father AI includes five "
            "questions a day free; an optional Premium subscription makes it unlimited "
            "and unlocks conversation history."
        ),
    },
}


def faq_ld(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)},
            }
            for q, a in items
        ],
    }


def faq_html(items: list[tuple[str, str]]) -> str:
    return '<div class="faq">' + "".join(
        f"<details class=\"faq-item\"><summary>{e(q)}</summary><p>{a}</p></details>"
        for q, a in items
    ) + "</div>"


def verse_ld(entries: list[dict]) -> dict:
    return {
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": v["ref"],
                "item": {
                    "@type": "Quotation",
                    "text": v["text"],
                    "isPartOf": {"@type": "Book", "name": "The Holy Bible, King James Version"},
                },
            }
            for i, v in enumerate(entries)
        ],
    }


def verse_html(entries: list[dict], with_prayer: bool = True) -> str:
    out = []
    for v in entries:
        prayer = (
            f'<p class="prayer"><strong>Guided prayer.</strong> {e(v["prayer"])}</p>'
            if with_prayer else ""
        )
        out.append(
            f'<li class="verse"><blockquote>&ldquo;{e(v["text"])}&rdquo;</blockquote>'
            f'<cite>{e(v["ref"])} &middot; KJV</cite>{prayer}</li>'
        )
    return f'<ul class="verse-list">{"".join(out)}</ul>'


# --- Landing page ------------------------------------------------------------

HOME_FAQ = [
    ("Is Footlamp free?",
     "Yes. The app is free to download, and reading is never gated. Every book and "
     "chapter in KJV and ESV, keyword search, topic collections, verse compare, the "
     "verse of the day and the daily reminder are free and unlimited. Father AI "
     "includes five questions a day at no cost; an optional Premium subscription "
     "makes it unlimited and unlocks your conversation history."),
    ("Does it work offline?",
     "Reading, search, topics, verse compare and the verse of the day work with no "
     "network at all &mdash; the full text of both translations is carried on your "
     "device. Father AI is the one feature that needs a connection."),
    ("Do I need an account?",
     "No. There is no sign-up, no email address and no password. An anonymous "
     "identity is created silently on first launch so that Father AI and its history "
     "work, and that is the whole of it."),
    ("Are there ads?",
     "None, in any format, anywhere in the app."),
    ("Which translations are included?",
     "The King James Version and the English Standard Version, both bundled on the "
     "device. You can switch between them without losing your place, and compare a "
     "verse across the two side by side."),
    ("How many Father AI questions do I get?",
     "Five a day on the free app, resetting at your own local midnight. The Profile "
     "screen shows how many you have left before you spend one, and a question that "
     "fails on a bad connection is not charged against the allowance."),
    ("What does Premium add?",
     "Two things: Father AI becomes unlimited, and your full conversation history "
     "unlocks so you can reopen and continue anything you have asked before. It is "
     "bought through your existing App Store or Google Play account, works across "
     "both platforms from one purchase, and can be cancelled from your own store "
     "settings at any time."),
    ("Is there a web or desktop version?",
     "No. Footlamp is an Android and iOS app. This site describes it; the "
     "reading happens in the app."),
]

FEATURES = [
    ("Read", "The whole Bible, on your device",
     "Every book, chapter and verse in KJV and ESV. The app opens on the exact "
     "chapter you last read, moves to the next or previous chapter in one tap, and "
     "never asks for a signal to do it.",
     "offline-bible-app"),
    ("Ask", "Father AI, grounded in scripture",
     "Ask a question in ordinary language &mdash; &ldquo;what does the Bible say about "
     "anxiety?&rdquo; &mdash; and get an answer with the verses behind it. Have any "
     "verse explained in plain language. Keep asking; follow-ups continue the same "
     "conversation.",
     "ai-bible-study-assistant"),
    ("Compare", "Two translations, one verse",
     "Put a verse side by side across KJV and ESV and see exactly how the wording "
     "differs before you draw a conclusion. Switch translation from the compare "
     "screen and stay on the same verse.",
     "kjv-vs-esv"),
    ("Search", "Instant, on-device, offline",
     "Type any word or phrase and get every verse in your translation that contains "
     "it. It runs on the device, so results are immediate and work in airplane mode. "
     "Tap a result to land in the reader at that exact verse.",
     None),
    ("Daily", "A verse, a prayer, a reminder",
     "A new verse each day from thirty chosen for the moments they meet, with "
     "artwork made for each one, and a short two-step prayer and reflection attached "
     "to it. Turn on a reminder at the time you choose.",
     "verse-of-the-day"),
    ("Browse", "When you arrive with a feeling",
     "Topic collections for anxiety, hope, healing and encouragement &mdash; for the "
     "days you have a feeling rather than a reference. Every verse opens straight "
     "into the reader.",
     "bible-verses-about-anxiety"),
]


def build_home() -> None:
    cards = []
    for eyebrow, title, body, link in FEATURES:
        more = f'<p class="more">Read more &rarr;</p>' if link else ""
        tag = f'<a class="card" href="{link}/">' if link else '<div class="card">'
        end = "</a>" if link else "</div>"
        cards.append(
            f'{tag}<span class="eyebrow">{e(eyebrow)}</span>'
            f"<h3>{e(title)}</h3><p class=\"muted\">{body}</p>{more}{end}"
        )

    topic_links = "".join(
        f'<a class="card" href="bible-verses-about-{name.lower()}/">'
        f"<h3>{e(name)}</h3>"
        f'<p class="muted">{len(vs)} curated verses, each with a guided prayer.</p>'
        f'<p class="more">Read them &rarr;</p></a>'
        for name, vs in TOPICS.items()
    )

    body = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Android &amp; iOS &middot; Free</span>
      <h1>A Bible you can read anywhere, with an <span class="ai-text">AI that answers</span> when you have a question.</h1>
      <p class="verse-line">&ldquo;Thy word is a lamp unto my feet, and a light unto my path.&rdquo; &mdash; Psalm 119:105</p>
      <p class="lead">No ads. No account. No sign-up. The full King James Version and
      English Standard Version are carried on your device, so reading, search and the
      verse of the day work on a plane, on a subway, or with no signal at all.</p>
      {store_buttons()}
    </div>
    <div class="hero-art">
      <img src="assets/img/app-logo.png" width="512" height="512"
           alt="The Footlamp app icon: a figure with an open hand, lit from behind."
           loading="eager" decoding="async" fetchpriority="high">
    </div>
  </div>
</section>

<section id="features" aria-labelledby="features-heading">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What it does</span>
      <h2 id="features-heading">Read, search, compare, and ask</h2>
      <p class="lead">Everything below except Father AI works with no network, no
      account and no payment.</p>
    </div>
    <div class="grid grid-3">{"".join(cards)}</div>
  </div>
</section>

<section id="father-ai" aria-labelledby="ai-heading">
  <div class="wrap">
    <div class="grid grid-2">
      <div class="card card-ai">
        <span class="eyebrow">Father AI</span>
        <h2 id="ai-heading">When you arrive with a question rather than a reference</h2>
        <p>Father AI is a destination in the app, not a hidden action. Ask anything in
        your own words and read the answer with the scripture it is grounded in, so the
        response points back to the text rather than replacing it.</p>
        <ul class="ticks">
          <li>Ask in ordinary language, or tap a suggested prompt</li>
          <li>Have any verse explained without a commentary shelf</li>
          <li>Follow-up questions continue the same conversation</li>
          <li>Start a new conversation deliberately, so topics never bleed</li>
          <li>Retry a question that failed on a bad connection, at no cost</li>
        </ul>
        <p><a href="ai-bible-study-assistant/">How Father AI works &rarr;</a></p>
      </div>
      <div class="card">
        <span class="eyebrow">The free allowance</span>
        <h2>Five questions a day, and nothing hidden</h2>
        <p>Father AI costs real money to run, so the free app includes five questions a
        day, resetting at your own local midnight. The Profile screen shows how many you
        have left <em>before</em> you spend one, so running out is never a surprise. A
        request that fails is not charged.</p>
        <h3>What Premium adds</h3>
        <ul class="ticks">
          <li>Unlimited Father AI questions</li>
          <li>Your full conversation history, to reopen and continue</li>
          <li>One purchase entitles you on both iOS and Android</li>
        </ul>
        <ul class="ticks crosses">
          <li>Reading, search, topics, compare and the verse of the day stay free
          and unlimited &mdash; Premium adds, it never withholds</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="topics" aria-labelledby="topics-heading">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Topics</span>
      <h2 id="topics-heading">For the days you have a feeling, not a reference</h2>
      <p class="lead">Thirty verses curated across four collections, each one paired
      with a short guided prayer and reflection questions in the app.</p>
    </div>
    <div class="grid grid-2">{topic_links}</div>
  </div>
</section>

<section id="privacy" aria-labelledby="privacy-heading">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What is not here</span>
      <h2 id="privacy-heading">Stated plainly, so nothing is mistaken for an omission</h2>
    </div>
    <div class="grid grid-2">
      <div class="card">
        <h3>No advertising</h3>
        <p class="muted">In any format, anywhere in the app. Nothing sits between
        opening it and the verse.</p>
      </div>
      <div class="card">
        <h3>No sign-up or sign-in</h3>
        <p class="muted">You are never asked for a name, an email address, a phone
        number or payment details. There is no login screen.
        <a href="bible-app-without-ads/">More on this &rarr;</a></p>
      </div>
      <div class="card">
        <h3>No web or desktop client</h3>
        <p class="muted">Android and iOS only. This site is not a reader.</p>
      </div>
      <div class="card">
        <h3>Reading is never gated</h3>
        <p class="muted">Chapters, both translations, keyword search, topics, verse
        compare and the daily reminder are free, unlimited, and the parts guaranteed to
        work offline.</p>
      </div>
    </div>
  </div>
</section>

<section id="faq" aria-labelledby="faq-heading">
  <div class="wrap">
    <div class="section-head">
      <h2 id="faq-heading">Frequently asked questions</h2>
    </div>
    {faq_html(HOME_FAQ)}
  </div>
</section>

{band("Read, ask, and pray &mdash; wherever you are",
      "Connected or not. Free on the App Store and Google Play.")}
"""
    page(
        "",
        "Footlamp: Offline KJV & ESV Bible App with Father AI",
        "A free, ad-free Bible app for iOS and Android. Read KJV and ESV fully "
        "offline, compare translations, and ask Father AI any question. "
        "No account, no sign-up.",
        body,
        [ORGANISATION, WEBSITE, SOFTWARE_APP, faq_ld(HOME_FAQ)],
    )


# --- Topic pages -------------------------------------------------------------

TOPIC_COPY = {
    "Anxiety": (
        "Bible Verses About Anxiety - 7 Verses with Prayers",
        "Seven Bible verses about anxiety and worry, in the King James Version, each "
        "with a short guided prayer. Read them in context, offline, in the free "
        "Footlamp app.",
        "Anxiety is the reason a great many people open a Bible, and it rarely comes "
        "with a chapter and verse attached. These seven passages are the collection "
        "the app surfaces under <em>Anxiety</em> &mdash; on worry about tomorrow, on "
        "casting your cares, and on a peace that is described as passing "
        "understanding.",
        "worried",
    ),
    "Hope": (
        "Bible Verses About Hope - 7 Verses with Prayers",
        "Seven Bible verses about hope in the King James Version, each with a guided "
        "prayer. Read them in full context offline in the free Footlamp app for "
        "iOS and Android.",
        "Hope in scripture is not optimism about how things will turn out; it is "
        "confidence in who is holding them. These seven passages are the collection "
        "the app surfaces under <em>Hope</em>, gathered for the stretches where the "
        "outcome is genuinely unknown.",
        "waiting on something",
    ),
    "Healing": (
        "Bible Verses About Healing - 7 Verses with Prayers",
        "Seven Bible verses about healing in the King James Version, each with a short "
        "guided prayer. Read them in context, offline, in the free Footlamp app.",
        "These seven passages are the collection the app surfaces under "
        "<em>Healing</em> &mdash; for illness, for grief, and for the kind of injury "
        "that does not show. They are offered as scripture to sit with, not as "
        "medical advice.",
        "unwell or grieving",
    ),
    "Encouragement": (
        "Bible Verses About Encouragement - 9 Verses with Prayers",
        "Nine Bible verses about encouragement and strength in the King James Version, "
        "each with a guided prayer. Read them offline in the free Footlamp app.",
        "These nine passages are the collection the app surfaces under "
        "<em>Encouragement</em> &mdash; the verses to reach for when the work is long, "
        "the week has been unkind, or someone else needs something better than advice.",
        "running low",
    ),
}


def build_topic(name: str) -> None:
    entries = TOPICS[name]
    slug = f"bible-verses-about-{name.lower()}"
    title, description, intro, felt = TOPIC_COPY[name]
    others = "".join(
        f'<a class="card" href="../bible-verses-about-{n.lower()}/"><h3>{e(n)}</h3>'
        f'<p class="muted">{len(v)} verses with guided prayers.</p></a>'
        for n, v in TOPICS.items() if n != name
    )
    body = f"""
{breadcrumbs(slug, f"Verses about {name.lower()}")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Topic collection</span>
    <h1>Bible verses about {e(name.lower())}</h1>
    <p class="lead">{intro}</p>
    <p>Every verse below is quoted from the King James Version. In the app the same
    collection is available in the English Standard Version too, and tapping any verse
    opens it in the reader in full context &mdash; with the chapter around it, the other
    translation beside it, and Father AI available to explain anything that does not
    land.</p>
  </div>
</section>

<section aria-labelledby="verses-heading">
  <div class="wrap">
    <h2 id="verses-heading" class="section-head">The {len(entries)} verses, with their guided prayers</h2>
    {verse_html(entries)}
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Reading these in context</h2>
    <p>A verse lifted out of its chapter can be made to say almost anything. Footlamp
    is built so that a topic list is a way <em>in</em> to the text rather than a
    substitute for it: tap a verse and you land in the reader at that exact verse, with
    the surrounding chapter there to be read.</p>
    <p>If a sentence is dense or archaic &mdash; and the King James Version has plenty of
    both &mdash; you can ask for a plain-language explanation of that verse without
    leaving the page, then keep asking follow-up questions in the same thread until the
    answer actually lands. That is <a href="../ai-bible-study-assistant/">Father AI</a>,
    and it is the one part of the app that needs a connection.</p>
    <h2>When you are {e(felt)} and offline</h2>
    <p>The whole point of carrying both translations on the device is that the moment
    you need them is rarely the moment you have signal. Reading, keyword search, the
    topic collections, verse compare and the verse of the day all
    <a href="../offline-bible-app/">work with the network off entirely</a>.</p>
    <h2>The other collections</h2>
  </div>
  <div class="wrap"><div class="grid grid-3">{others}</div></div>
</section>

{band(f"All {len(entries)} {e(name.lower())} verses, in your pocket",
      "Free on iOS and Android, with the whole Bible on your device and a guided prayer for every verse in this collection.")}
"""
    page(
        slug, title, description, body,
        [
            ORGANISATION, WEBSITE, SOFTWARE_APP,
            breadcrumb_ld(slug, f"Bible verses about {name.lower()}"),
            verse_ld(entries),
            {
                "@type": "WebPage",
                "name": title,
                "url": abs_url(slug),
                "description": description,
                "isPartOf": {"@id": f"{BASE_URL}#website"},
                "about": {"@type": "Thing", "name": f"Bible verses about {name.lower()}"},
                "dateModified": BUILD_DATE,
            },
        ],
        og_type="article",
    )


# --- Feature pages -----------------------------------------------------------

OFFLINE_FAQ = [
    ("Does the Footlamp app work without internet?",
     "Yes. Reading any book, chapter and verse, keyword search, the topic "
     "collections, verse compare, the verse of the day and the daily reminder all run "
     "on the device and need no connection. Father AI is the only feature that "
     "requires one."),
    ("Do I have to download the Bible text first?",
     "No. Both translations ship inside the app, so there is nothing to download "
     "after installing and nothing to manage."),
    ("Does search work offline?",
     "Yes. Keyword search is a plain string search over the translation you have "
     "selected, running entirely on the device, which is also why it is instant."),
    ("Will the daily reminder fire in airplane mode?",
     "Yes. The reminder is scheduled on the device itself and does not depend on a "
     "push server."),
]


def build_offline() -> None:
    slug = "offline-bible-app"
    title = "Offline Bible App - Read KJV & ESV With No Signal"
    description = ("Footlamp carries the full KJV and ESV on your phone. Reading, "
                   "search, topics and the verse of the day all work in airplane mode. "
                   "Free on iOS and Android.")
    body = f"""
{breadcrumbs(slug, "Offline Bible")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Offline</span>
    <h1>An offline Bible, because the moment you need it rarely has signal</h1>
    <p class="lead">A plane, a subway, a hospital basement, a dead battery on the last
    bar &mdash; the app treats all of these as normal, not as an error state. The full
    text of the King James Version and the English Standard Version is carried on your
    device from the moment you install it.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid-2">
      <div class="card">
        <h2>Works with the network off</h2>
        <ul class="ticks">
          <li>Every book, chapter and verse in KJV and ESV</li>
          <li>Keyword search across the whole translation, instantly</li>
          <li>Topic collections for anxiety, hope, healing and encouragement</li>
          <li>Verse compare, side by side across translations</li>
          <li>The verse of the day, in whichever translation you have chosen</li>
          <li>The daily reminder notification</li>
          <li>Your reading position, remembered exactly</li>
        </ul>
      </div>
      <div class="card card-ai">
        <h2>Needs a connection</h2>
        <ul class="ticks crosses">
          <li>Father AI &mdash; asking a question, explaining a verse, and the
          follow-ups in a conversation</li>
        </ul>
        <p class="muted">That is the whole list. Father AI runs on a server because an
        answer grounded in scripture is generated, not looked up. When a request fails
        on a bad connection the app says so rather than waiting forever, you can retry
        it, and a failed request is never charged against your daily allowance.</p>
        <p><a href="../ai-bible-study-assistant/">How Father AI works &rarr;</a></p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Nothing to download, nothing to manage</h2>
    <p>Some Bible apps are readers with a download manager attached: you pick a
    translation, wait for it, and discover on the plane which ones you forgot. Both
    translations here are bundled in the app itself. There is no per-book download, no
    cache to warm and nothing to expire.</p>
    <h2>Instant search, because it never leaves the device</h2>
    <p>Type a word or a half-remembered phrase and every verse in your selected
    translation that contains it comes back immediately. This is a plain string search,
    not an AI feature, and saying so is the stronger claim: it is deterministic, it is
    fast, and it works with the radio off. Tap any result and you land in the reader at
    that exact verse rather than staring at a list.</p>
    <h2>Your place is kept</h2>
    <p>Open the Bible tab and you are back on the exact chapter you last read, so
    returning to the app costs no navigation. Switching translation &mdash; from the
    Profile screen or from the compare screen &mdash; keeps you on the same verse, and
    asks you to confirm first so an accidental tap never silently changes the text in
    front of you.</p>
    <h2>What leaves your device</h2>
    <p>Only a Father AI question. Nothing about your reading &mdash; not the chapter,
    not your searches, not the topics you open &mdash; is sent anywhere, because none of
    it needs to be. The <a href="{PRIVACY_URL}">privacy policy</a> sets this out in
    full, and there is <a href="../bible-app-without-ads/">no account and no
    advertising</a> attached to any of it.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(OFFLINE_FAQ)}</div>
</section>

{band("The whole Bible, with the radio off",
      "Free on iOS and Android. KJV and ESV bundled, nothing to download afterwards.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "Offline Bible app"),
          faq_ld(OFFLINE_FAQ)], og_type="article")


AI_FAQ = [
    ("What is Father AI?",
     "Father AI is the assistant inside Footlamp. It answers questions asked in "
     "ordinary language and explains individual verses in plain language, with the "
     "scripture the answer rests on shown alongside it."),
    ("How many questions do I get for free?",
     "Five a day, resetting at your own local midnight rather than someone else's. "
     "The Profile screen shows how many are left before you spend one."),
    ("What happens if a question fails?",
     "Nothing is charged. Only answered questions count against the allowance, and "
     "you can retry a request that failed on a bad connection at no cost."),
    ("Does Father AI replace reading the Bible?",
     "It is built not to. Answers are returned with the scripture they are grounded "
     "in, so the response points back to the text, and every verse it cites opens in "
     "the reader in full context."),
    ("Are my conversations saved?",
     "Yes, they are kept from the start &mdash; so subscribing reveals a history that "
     "already exists rather than an empty list. Reopening and continuing a past "
     "conversation, and deleting one, are Premium features."),
    ("Does Father AI work offline?",
     "No. It is the one feature in the app that needs a connection. Everything else "
     "&mdash; reading, search, topics, compare, the verse of the day &mdash; works "
     "with no network at all."),
]


def build_ai() -> None:
    slug = "ai-bible-study-assistant"
    title = "Father AI - Ask Any Bible Question, Answered in Scripture"
    description = ("Father AI answers Bible questions in plain language and explains any "
                   "verse, with the scripture behind every answer. Five a day free, "
                   "on iOS and Android.")
    body = f"""
{breadcrumbs(slug, "Father AI")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Father AI</span>
    <h1>Ask in your own words. <span class="ai-text">Get an answer grounded in scripture.</span></h1>
    <p class="lead">Not everyone arrives at the Bible with a chapter and verse. Plenty
    arrive with a question &mdash; &ldquo;what does the Bible say about anxiety?&rdquo;
    &mdash; and no idea where to start looking. Father AI is the door in.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid-3">
      <div class="card card-ai">
        <span class="eyebrow">Ask</span>
        <h3>A question, in ordinary language</h3>
        <p class="muted">Father AI has its own tab, so the assistant is a destination
        rather than a hidden action. Ask anything, or tap a suggested prompt when you
        cannot yet phrase what you want. The answer comes back with the scripture it
        rests on.</p>
      </div>
      <div class="card card-ai">
        <span class="eyebrow">Explain</span>
        <h3>Any verse, in plain language</h3>
        <p class="muted">Tap a verse while reading and ask for an explanation without
        leaving the chapter. A dense or archaic sentence becomes usable, with no
        commentary shelf and no second app.</p>
      </div>
      <div class="card card-ai">
        <span class="eyebrow">Keep asking</span>
        <h3>Follow-ups, in the same thread</h3>
        <p class="muted">Context carries from one turn to the next, so an explanation
        can be pushed until it actually lands. Start a new conversation deliberately
        when the subject changes, so an unrelated question never inherits the last
        topic.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Answers that point back at the text</h2>
    <p>The design constraint on Father AI is that it must send you to scripture rather
    than stand in front of it. Answers are returned with the verses behind them, and
    every verse cited opens in the reader with the chapter around it. If you disagree
    with the answer, the text to check it against is one tap away.</p>
    <h2>Five questions a day, free, and nothing hidden</h2>
    <p>Father AI costs real money to run, so the free app includes five questions a day.
    Three things follow from that, all of them deliberate:</p>
    <ul>
      <li><strong>The allowance is visible before you spend it.</strong> The Profile
      screen shows how many questions remain, so running out is never a surprise
      delivered mid-thought.</li>
      <li><strong>It resets at your local midnight</strong>, at the start of your day
      rather than at the start of a server's.</li>
      <li><strong>A failed request is not charged.</strong> Only answered questions
      count, and retrying after a dropped connection costs nothing.</li>
    </ul>
    <h2>What Premium adds</h2>
    <p>Premium lifts the daily limit entirely and unlocks your conversation history, so
    a thought from last week can be picked up rather than retyped. Conversations are
    kept from the beginning, which means subscribing reveals a history that already
    exists rather than an empty list, and subscribers can delete any conversation.</p>
    <p>It is bought through your existing App Store or Google Play account &mdash; no new
    payment details &mdash; one purchase entitles you on both platforms, a previous
    purchase can be restored on a new device, and it is cancelled from your own store
    settings at any time. Reading, search, topics, verse compare and the verse of the
    day are free and unlimited whether you subscribe or not.</p>
    <h2>What happens to your question</h2>
    <p>A question you ask is sent to our server, forwarded to a language model to be
    answered, and stored so your conversation history works. It is linked to an
    anonymous identity created silently on first launch, not to a name or an email
    address, because <a href="../bible-app-without-ads/">the app never asks you for
    one</a>. The <a href="{PRIVACY_URL}">privacy policy</a> is the authority on this.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(AI_FAQ)}</div>
</section>

{band("Ask your first five questions today",
      "Father AI is free to try, five questions a day, with no account to create first.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "Father AI"),
          faq_ld(AI_FAQ)], og_type="article")


KJV_ESV_FAQ = [
    ("Which translations does Footlamp include?",
     "The King James Version and the English Standard Version, and no others. Both "
     "are bundled on the device."),
    ("Can I switch translation without losing my place?",
     "Yes. Switching from the Profile screen or from the compare screen keeps you on "
     "the same verse, and the app asks you to confirm before it switches so an "
     "accidental tap never silently changes the text you are reading."),
    ("Can I see both translations at once?",
     "Yes. Tap a verse and choose compare, and the same verse is shown side by side "
     "across both translations."),
    ("Which translation should I read?",
     "Whichever your church, study group or memory prefers &mdash; that is what the "
     "compare screen is for. The KJV is the older, more literary text; the ESV is a "
     "modern translation that stays close to the wording of the original. Reading a "
     "verse in both is usually more useful than choosing once."),
]


def build_kjv_esv() -> None:
    slug = "kjv-vs-esv"
    sample = TOPICS["Anxiety"][0]
    title = "KJV vs ESV - Compare Bible Translations Verse by Verse"
    description = ("How the King James Version and the English Standard Version differ, "
                   "and how to read a verse in both at once. Footlamp bundles KJV "
                   "and ESV offline on iOS and Android.")
    body = f"""
{breadcrumbs(slug, "KJV vs ESV")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Translations</span>
    <h1>KJV and ESV, side by side</h1>
    <p class="lead">Footlamp carries two translations and only two: the King James
    Version and the English Standard Version. Both live on your device, you can switch
    between them without losing your place, and you can put a single verse side by side
    across the pair before drawing a conclusion from its wording.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="table-scroll">
      <table>
        <caption>Both translations are bundled in the app; nothing here is a download.</caption>
        <thead>
          <tr><th scope="col">&nbsp;</th><th scope="col">King James Version</th><th scope="col">English Standard Version</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">First published</th><td>1611</td><td>2001</td></tr>
          <tr><th scope="row">Register</th><td>Early modern English &mdash; literary, familiar from memory and liturgy</td><td>Contemporary English, deliberately restrained</td></tr>
          <tr><th scope="row">Approach</th><td>Formal equivalence, word for word</td><td>Essentially literal, word for word where modern English allows</td></tr>
          <tr><th scope="row">Reads well when</th><td>You know passages by heart, or your church reads from it</td><td>You want the wording to get out of the way</td></tr>
          <tr><th scope="row">In the app</th><td>Full text, offline</td><td>Full text, offline</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Why compare at all</h2>
    <p>Any translation is a set of decisions, and the decisions are most visible where
    two translations diverge. Reading a verse in both is the cheapest way to see where a
    reading rests on the underlying text and where it rests on a translator's choice of
    English word &mdash; which is exactly the point at which it is worth slowing down.</p>
    <p>Here is a verse the app curates under <a href="../bible-verses-about-anxiety/">anxiety</a>,
    in the KJV:</p>
  </div>
  <div class="wrap">{verse_html([sample], with_prayer=False)}</div>
  <div class="wrap prose">
    <p>&ldquo;Be careful for nothing&rdquo; meant &ldquo;be anxious about nothing&rdquo; in
    1611 and means close to its opposite in casual reading today. That is not a flaw in
    the KJV; it is four centuries of drift in one English word, and it is the kind of
    thing verse compare exists to surface. The ESV rendering of the same verse is in the
    app, next to this one.</p>
    <h2>How it works in the app</h2>
    <ul>
      <li><strong>Tap a verse</strong> to open a small action card &mdash; everything you
      might want to do with that verse is in one place.</li>
      <li><strong>Choose compare</strong> and the verse appears side by side across both
      translations, in a stable order.</li>
      <li><strong>Switch translation from there</strong>, or from the Profile screen, and
      you stay on the same verse. The app confirms the switch first.</li>
      <li><strong>Ask for an explanation</strong> of either wording without leaving the
      verse &mdash; that is <a href="../ai-bible-study-assistant/">Father AI</a>, and it
      is the one part that needs a connection.</li>
    </ul>
    <p>Your chosen translation applies everywhere: the reader, keyword search, the topic
    collections and the verse of the day all follow it, so the choice is made once
    rather than repeated per screen.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(KJV_ESV_FAQ)}</div>
</section>

{band("Compare any verse, offline",
      "Both translations bundled, free on iOS and Android, with nothing to download afterwards.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "KJV vs ESV"),
          faq_ld(KJV_ESV_FAQ)], og_type="article")


VOTD_FAQ = [
    ("Where does the verse of the day come from?",
     "A curated set of thirty verses, chosen for the moments they meet, each with "
     "artwork made for it."),
    ("Can I get a daily reminder?",
     "Yes. Turn it on from the Profile screen, and off again just as easily. It is "
     "scheduled on the device, so it fires without a network connection."),
    ("Does the verse of the day follow my translation?",
     "Yes. It is shown in whichever of KJV or ESV you have chosen, matching the rest "
     "of your reading."),
    ("What is the guided prayer?",
     "A short two-step prayer and reflection attached to the day's verse, so the "
     "daily verse becomes a practice rather than just a card. You can step forward and "
     "back through it, and your progress persists across app launches &mdash; a prayer "
     "begun in the morning can be finished later that day."),
]


def build_votd() -> None:
    slug = "verse-of-the-day"
    samples = [TOPICS["Hope"][0], TOPICS["Encouragement"][0], TOPICS["Healing"][0]]
    title = "Verse of the Day with a Guided Prayer - Footlamp"
    description = ("A new verse each day from thirty curated passages, with artwork and a "
                   "short guided prayer, plus an optional daily reminder. Free and offline "
                   "on iOS and Android.")
    body = f"""
{breadcrumbs(slug, "Verse of the Day")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Daily practice</span>
    <h1>A verse a day, and a reason to open the app</h1>
    <p class="lead">The hardest part of a daily reading habit is not the reading. It is
    deciding what to read. The verse of the day removes that decision: open the app and
    something chosen is already waiting, in your translation, with artwork made for
    it.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid-3">
      <div class="card">
        <span class="eyebrow">Step one</span>
        <h3>The verse</h3>
        <p class="muted">One of thirty curated passages, shown in whichever of KJV or
        ESV you read in. It stays the same all day, and survives an app update &mdash;
        upgrading never resets your day.</p>
      </div>
      <div class="card">
        <span class="eyebrow">Step two</span>
        <h3>The guided prayer</h3>
        <p class="muted">A short two-step prayer and reflection attached to that verse.
        Step forward and back freely; progress persists across launches, so a prayer
        begun at breakfast can be finished at night.</p>
      </div>
      <div class="card">
        <span class="eyebrow">Optional</span>
        <h3>The reminder</h3>
        <p class="muted">One toggle on the Profile screen, on or off. It is scheduled
        on the device itself, so it arrives with no signal &mdash; and the app never
        becomes a source of notifications you did not ask for.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Three of the thirty</h2>
    <p>Quoted here in the King James Version; in the app they follow whichever
    translation you have chosen.</p>
  </div>
  <div class="wrap">{verse_html(samples)}</div>
</section>

<section>
  <div class="wrap prose">
    <h2>Where the day can go from there</h2>
    <p>The verse of the day is a starting point rather than the whole of it. From the
    card you can open the verse in the reader with its chapter around it, compare it
    across <a href="../kjv-vs-esv/">both translations</a>, or ask
    <a href="../ai-bible-study-assistant/">Father AI</a> to explain it in plain language
    and keep asking until it lands. If the verse names something you are carrying, the
    <a href="../bible-verses-about-hope/">topic collections</a> go deeper on it.</p>
    <p>Everything on this page except Father AI
    <a href="../offline-bible-app/">works offline</a>, including the reminder. Nothing
    here costs anything, and there is nothing to sign up for.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(VOTD_FAQ)}</div>
</section>

{band("Start tomorrow with something already chosen",
      "Free on iOS and Android. A verse, a prayer, and a reminder if you want one.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "Verse of the Day"),
          faq_ld(VOTD_FAQ)], og_type="article")


NOADS_FAQ = [
    ("Does Footlamp show ads?",
     "No. There is no advertising in any format, anywhere in the app, and no ad SDK "
     "in it."),
    ("Do I need to create an account?",
     "No. There is no sign-up, no sign-in, no email address and no password. An "
     "anonymous identity is created silently on first launch so Father AI and its "
     "history work."),
    ("What personal information is collected?",
     "No name, email address, phone number, postal address or payment details &mdash; "
     "nothing in the app asks for any of them. Father AI questions and answers are "
     "stored against an anonymous identifier so conversation history works."),
    ("Is my reading tracked?",
     "No. Reading, search, topics, verse compare and the verse of the day all run on "
     "the device and send nothing. Anonymous app usage and crash analytics are "
     "collected; there is no cross-app tracking and no advertising identifier "
     "request."),
    ("How is the app paid for, if not by ads?",
     "By an optional Premium subscription that lifts the Father AI daily limit and "
     "unlocks conversation history. Everything the ad-supported version did is still "
     "free and unlimited."),
]


def build_no_ads() -> None:
    slug = "bible-app-without-ads"
    title = "A Bible App With No Ads and No Account - Footlamp"
    description = ("No advertising, no sign-up, no email address and no password. Read "
                   "the Bible offline in KJV and ESV without handing over anything. Free "
                   "on iOS and Android.")
    body = f"""
{breadcrumbs(slug, "No ads, no account")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">No ads, no account</span>
    <h1>Nothing between opening the app and the verse</h1>
    <p class="lead">Footlamp has no advertising in any format, anywhere. It has no
    sign-up screen, no sign-in screen, and no field asking for your email address. You
    install it, you open it, and you are reading.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid-2">
      <div class="card">
        <h2>What the app never does</h2>
        <ul class="ticks crosses">
          <li>Show an advertisement, on launch or anywhere else</li>
          <li>Ask for a name, email address, phone number or postal address</li>
          <li>Ask you to create a password or log in</li>
          <li>Request an advertising identifier or track you across apps</li>
          <li>Gate a chapter, a translation, a search or the verse of the day</li>
        </ul>
      </div>
      <div class="card">
        <h2>What it does instead</h2>
        <ul class="ticks">
          <li>Creates an anonymous identity silently on first launch, so Father AI and
          its history work without an account</li>
          <li>Keeps reading, search, topics, compare and the verse of the day entirely
          on your device</li>
          <li>Sends only your Father AI questions, and only when you ask one</li>
          <li>Links your subscription to your existing App Store or Google Play
          account, so no new payment details are handed over</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Why the ads went</h2>
    <p>An earlier version of this app was ad-supported, which meant an advertisement
    stood between opening it and the first verse. That is now gone, replaced by an
    optional Premium subscription. Nothing the free app used to do moved behind that
    subscription: reading, both translations, keyword search, topic collections, verse
    compare, the verse of the day, generated prayers and the daily reminder are free and
    unlimited, and will stay that way.</p>
    <p>Premium adds two things &mdash; unlimited Father AI and full conversation history
    &mdash; because those are the two things that cost money to run. You can reach the
    offer deliberately from the Profile screen rather than only discovering it by
    running out.</p>
    <h2>Transparency inside the app</h2>
    <ul>
      <li>The Privacy Policy and the Terms of Use open from inside the app, both before
      and after subscribing, so the documents never become unreachable.</li>
      <li>The purchase screen states plainly that you can cancel from your own store
      account settings at any time.</li>
      <li>The Profile screen shows your subscription status and how many Father AI
      questions remain, so the state of your account is never hidden.</li>
      <li>A feedback survey opens from the Profile screen whenever you want it &mdash;
      and the one-time invitation to it can be dismissed and is never shown again.</li>
    </ul>
    <p>The <a href="{PRIVACY_URL}">full privacy policy</a> is the authority on what is
    collected and why.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(NOADS_FAQ)}</div>
</section>

{band("Open it, and start reading",
      "Free on iOS and Android. No ads, no sign-up, and nothing to hand over.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "No ads, no account"),
          faq_ld(NOADS_FAQ)], og_type="article")


def build_privacy() -> None:
    """The privacy policy. Its URL is printed in both store listings, so the page
    is written flat as `privacy-policy.html` and must keep that name. The prose
    lives in `_data/privacy-policy.html` and is the legal text verbatim; only the
    surrounding chrome is generated."""
    slug = ""
    prose = (ROOT / "_data" / "privacy-policy.html").read_text(encoding="utf-8").strip()
    title = f"Privacy Policy \u2013 {SITE_NAME}"
    description = (
        "No account, no ads, and nothing collected while you read. What Father AI "
        "sends to our server, what is kept, and how to have it deleted."
    )
    body = f"""
<section class="hero">
  <div class="wrap prose">
    <span class="eyebrow">Privacy</span>
    <h1>Privacy Policy</h1>
    <p class="lead">Reading, searching and the verse of the day never leave your
    device. Father AI is the one feature that does, and this page sets out exactly
    what it sends and what is kept.</p>
  </div>
</section>

<section>
  <div class="wrap prose">
{prose}
  </div>
</section>
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE], og_type="article", filename="privacy-policy.html")


# --- 404, sitemap, robots ----------------------------------------------------


def build_404() -> None:
    """GitHub Pages serves /404.html for unknown paths. It is written flat rather
    than through page() because it must work from any depth, so it uses absolute
    same-origin links and is marked noindex."""
    links = "".join(
        f'<li><a href="{BASE_URL}{href}/">{e(label)}</a></li>'
        for _, group in FOOTER_COLUMNS for href, label in group
    )
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found &ndash; {e(SITE_NAME)}</title>
<meta name="robots" content="noindex, follow">
<meta name="theme-color" content="#FBFBFB">
<meta name="color-scheme" content="light">
<link rel="icon" href="{BASE_URL}assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="stylesheet" href="{BASE_URL}assets/css/site.css">
</head>
<body>
<main id="main">
  <section class="hero">
    <div class="wrap prose">
      <span class="eyebrow">404</span>
      <h1>That page is not here</h1>
      <p class="lead">The link may be old, or the address may have a typo in it. These
      are all the pages there are:</p>
      <ul>{links}</ul>
      <p><a class="btn btn-primary" href="{BASE_URL}">Back to {e(SITE_NAME)}</a></p>
    </div>
  </section>
</main>
</body>
</html>
"""
    (ROOT / "404.html").write_text(doc, encoding="utf-8")
    print("  404.html")


def build_sitemap(slugs: list[tuple[str, str]]) -> None:
    entries = "".join(
        f"\n  <url><loc>{abs_url(s)}</loc><lastmod>{BUILD_DATE}</lastmod>"
        f"<changefreq>monthly</changefreq><priority>{pri}</priority></url>"
        for s, pri in slugs
    )
    entries += (
        f"\n  <url><loc>{BASE_URL}privacy-policy.html</loc><lastmod>{BUILD_DATE}</lastmod>"
        f"<changefreq>yearly</changefreq><priority>0.4</priority></url>"
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}\n</urlset>\n",
        encoding="utf-8",
    )
    print("  sitemap.xml")

    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {BASE_URL}sitemap.xml\n",
        encoding="utf-8",
    )
    print("  robots.txt")


# --- Entry point -------------------------------------------------------------


def main() -> None:
    print("Building the Footlamp site...")
    build_home()
    build_offline()
    build_ai()
    build_kjv_esv()
    build_votd()
    build_no_ads()
    for name in TOPICS:
        build_topic(name)
    build_privacy()
    build_404()

    build_sitemap(
        [("", "1.0")]
        + [(s, "0.8") for s in
           ("offline-bible-app", "ai-bible-study-assistant", "kjv-vs-esv",
            "verse-of-the-day", "bible-app-without-ads")]
        + [(f"bible-verses-about-{n.lower()}", "0.7") for n in TOPICS]
    )

    # .nojekyll keeps GitHub Pages from running the output through Jekyll, which
    # would otherwise skip files and directories beginning with an underscore.
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("Done.")


if __name__ == "__main__":
    main()
