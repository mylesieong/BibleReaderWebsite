#!/usr/bin/env python3
"""Static site generator for the Footlamp marketing site.

Emits plain HTML into the repository root so the result can be served by
GitHub Pages (or any static host) with no build step at serve time. Run it
after editing this file or `_data/topics.json`, then commit the output:

    python3 build.py

Content is written against `docs/app_description_external_facing.md` and
`docs/store-listing.md` in the app repository. The copy rules in
store-listing.md section 7 apply here too - in particular: no audio claims,
keyword search is not AI, KJV, BSB and WEB only (never the ESV), the AI
features are "Explain" and "Ask" (never "Father AI" or any persona), and no
accuracy words ("accurate", "verified", "trusted", "grounded").
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
APP_NAME = "Footlamp: Explain Bible Verses"
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
    ("ai-bible-study-assistant", "Explain & Ask"),
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
            ("ai-bible-study-assistant", "Explain & Ask"),
            ("compare-bible-translations", "KJV, BSB & WEB"),
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
        <p>The Bible, explained as you read it. The King James Version, the Berean
        Standard Bible and the World English Bible, carried on your device. Android
        and iOS.</p>
        <p><a href="{PRIVACY_URL}">Privacy Policy</a> &middot;
           <a href="{TERMS_URL}">Terms of Use</a> &middot;
           <a href="mailto:{CONTACT_EMAIL}">Contact</a></p>
        <p>Part of <a href="https://mylesieong.github.io/">Sai vs. Reality</a></p>
      </div>
      {"".join(cols)}
    </div>
    <p class="colophon">&copy; {date.today().year} {e(PUBLISHER)}. Scripture quotations on this
    site are from the King James Version, and on the translation comparison page also from the
    Berean Standard Bible and the World English Bible; all three are in the public domain.
    There is no web reader &mdash; {e(SITE_NAME)} is an Android and iOS app.</p>
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
        "A Bible app for iOS and Android that explains any verse in plain words and "
        "answers your questions. The King James Version, Berean Standard Bible and "
        "World English Bible are on the device, so reading and search work offline. "
        "No ads and no account."
    ),
    "publisher": {"@id": f"{BASE_URL}#publisher"},
    "installUrl": [APP_STORE_URL, PLAY_STORE_URL],
    "featureList": [
        "Explain any verse: a one-line summary, what it says, its context and why it matters",
        "Key phrases highlighted in the verse, related verses and follow-up questions",
        "Ask a question in your own words and keep the conversation going",
        "Full KJV, BSB and WEB text bundled on the device",
        "Works offline for reading, search, compare, topics and the verse of the day",
        "Compare a verse side by side across all three translations",
        "On-device keyword search across the whole Bible",
        "A 7-day starter plan for people new to the Bible",
        "Verse of the day with a two-step prayer",
        "Topic collections for anxiety, hope, healing and encouragement",
        "Daily reminder notification",
        "No advertising and no account",
    ],
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD",
        "description": (
            "Free to download. Reading, search, compare, topics, the starter plan, the "
            "verse of the day, prayers and reminders are never locked. Everyone gets 5 "
            "Explain or Ask requests a day; an optional Premium subscription makes them "
            "unlimited and keeps past conversations."
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
     "Yes. The app is free to download, and reading is never locked. Every book and "
     "chapter in KJV, BSB and WEB, keyword search, verse compare, the topic "
     "collections, the 7-day starter plan, the verse of the day, prayers and the daily "
     "reminder are free and unlimited. Everyone also gets 5 Explain or Ask requests a "
     "day; an optional Premium subscription makes them unlimited and keeps your past "
     "conversations."),
    ("What does Explain do?",
     "Tap any verse and choose Explain. You get a one-line summary, then what the verse "
     "says, its context and why it matters, in plain words. Key phrases are highlighted "
     "in the verse with a short note on each, related verses open in one tap, and a few "
     "follow-up questions are there if you want to keep going."),
    ("Does it work offline?",
     "Reading, search, compare, topics, the starter plan and the verse of the day work "
     "with no network at all &mdash; the full text of all three translations is carried "
     "on your device. Explain, Ask and prayers for a verse are generated, so they need "
     "a connection."),
    ("Do I need an account?",
     "No. There is no sign-up, no email address and no password. An anonymous "
     "identity is created silently on first launch so that Explain, Ask and your "
     "conversations work, and that is the whole of it."),
    ("Are there ads?",
     "None, in any format, anywhere in the app."),
    ("Which translations are included?",
     "The King James Version, the Berean Standard Bible and the World English Bible, "
     "all bundled on the device. You can switch between them without losing your "
     "place, and compare a verse across all three side by side."),
    ("How many Explain and Ask requests do I get?",
     "Five a day on the free app, shared between Explain and Ask and resetting at your "
     "own local midnight. The app shows how many you have left before you spend one, "
     "and a request that fails on a bad connection is not charged against the "
     "allowance."),
    ("What does Premium add?",
     "Two things: Explain and Ask become unlimited, and your past conversations are "
     "kept so you can read them back and continue them. It is bought through your "
     "existing App Store or Google Play account and can be cancelled from your own "
     "store settings at any time."),
    ("Is there a web or desktop version?",
     "No. Footlamp is an Android and iOS app. This site describes it; the "
     "reading happens in the app."),
]

FEATURES = [
    ("Explain", "Any verse, in plain words",
     "Tap a verse and choose Explain: a one-line summary, then what it says, its "
     "context and why it matters. Key phrases are highlighted with a note on each, and "
     "related verses open in one tap.",
     "ai-bible-study-assistant"),
    ("Ask", "What you&rsquo;re still wondering",
     "Ask a question in your own words &mdash; &ldquo;what does the Bible say about "
     "anxiety?&rdquo; &mdash; and get an answer drawn from scripture. Keep asking; "
     "follow-ups continue the same conversation.",
     "ai-bible-study-assistant"),
    ("Read", "The whole Bible, on your device",
     "Every book, chapter and verse in KJV, BSB and WEB. The app opens on the chapter "
     "you last read and never asks for a signal to do it.",
     "offline-bible-app"),
    ("Compare", "Three translations, one verse",
     "Put a verse side by side across all three translations and see exactly where "
     "the wording differs before you draw a conclusion from it.",
     "compare-bible-translations"),
    ("Daily", "A verse, a prayer, a reminder",
     "A verse each day from thirty chosen for the moments people bring to scripture, "
     "each with its own artwork. Pray with it in two short steps, then go deeper.",
     "verse-of-the-day"),
    ("Start here", "A 7-day starter plan",
     "New to the Bible? A short passage, one thing to look for and one question to sit "
     "with, about five minutes a day. A missed day costs nothing; then carry on through "
     "Luke, a chapter a day.",
     None),
]


def build_home() -> None:
    cards = []
    for eyebrow, title, body, link in FEATURES:
        more = f'<p class="more">Read more &rarr;</p>' if link else ""
        tag = f'<a class="card" href="{link}/">' if link else '<div class="card">'
        end = "</a>" if link else "</div>"
        cards.append(
            f'{tag}<span class="eyebrow">{e(eyebrow)}</span>'
            f"<h3>{title}</h3><p class=\"muted\">{body}</p>{more}{end}"
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
      <span class="eyebrow">Android &amp; iOS &middot; Free to download</span>
      <h1>The Bible, <span class="ai-text">explained as you read it.</span></h1>
      <p class="verse-line">&ldquo;Thy word is a lamp unto my feet, and a light unto my path.&rdquo; &mdash; Psalm 119:105</p>
      <p class="lead">Stuck on a verse? Tap it and Footlamp explains it in plain words.
      Then ask whatever you&rsquo;re still wondering. No ads, no account, and the King
      James Version, Berean Standard Bible and World English Bible are on your phone, so
      reading and search work with no signal at all.</p>
      {store_buttons()}
    </div>
    <div class="hero-art">
      <img src="assets/img/app-logo.png" width="512" height="512"
           alt="The Footlamp app icon: a lit clay oil lamp over the opening verses of John."
           loading="eager" decoding="async" fetchpriority="high">
    </div>
  </div>
</section>

<section id="features" aria-labelledby="features-heading">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What it does</span>
      <h2 id="features-heading">Understand it, then keep reading</h2>
      <p class="lead">Reading, search, compare, topics, the starter plan and the verse of
      the day work with no network, no account and no payment.</p>
    </div>
    <div class="grid grid-3">{"".join(cards)}</div>
  </div>
</section>

<section id="explain" aria-labelledby="ai-heading">
  <div class="wrap">
    <div class="grid grid-2">
      <div class="card card-ai">
        <span class="eyebrow">Explain &amp; Ask</span>
        <h2 id="ai-heading">For the verse that doesn&rsquo;t land the first time</h2>
        <p>Explain sits on every verse in every book, in all three translations. Tap a
        verse, choose Explain, and the answer comes back as short cards rather than a
        wall of text.</p>
        <ul class="ticks">
          <li>In one line: the verse summed up in a sentence</li>
          <li>What it says, its context, and why it matters</li>
          <li>Key phrases highlighted in the verse, each with a short note</li>
          <li>Related verses, quoted from the Bible on your phone</li>
          <li>Questions to keep thinking with, one tap away</li>
        </ul>
        <p><a href="ai-bible-study-assistant/">How Explain and Ask work &rarr;</a></p>
      </div>
      <div class="card">
        <span class="eyebrow">The free allowance</span>
        <h2>Five a day, and nothing hidden</h2>
        <p>Explain and Ask cost real money to run, so everyone gets five requests a day,
        shared between the two and resetting at your own local midnight. The app shows
        how many you have left <em>before</em> you spend one, and a request that fails is
        not charged.</p>
        <h3>What Premium adds</h3>
        <ul class="ticks">
          <li>Unlimited Explain and Ask</li>
          <li>Your past conversations, to read back and continue</li>
        </ul>
        <ul class="ticks crosses">
          <li>Reading, search, compare, topics, the starter plan, the verse of the day,
          prayers and reminders are never locked &mdash; Premium adds, it never
          withholds</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section id="topics" aria-labelledby="topics-heading">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">When you need a word</span>
      <h2 id="topics-heading">Verses for what you&rsquo;re carrying today</h2>
      <p class="lead">Thirty verses curated across four collections, each one paired
      with a short guided prayer in the app.</p>
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
        <h3>Reading is never locked</h3>
        <p class="muted">Chapters, all three translations, keyword search, verse
        compare, topics and the daily reminder are free, unlimited, and work
        offline.</p>
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

{band("Read it, understand it, keep going",
      "Free to download on the App Store and Google Play.")}
"""
    page(
        "",
        "Footlamp: Explain Bible Verses - Free Offline Bible App",
        "Tap any Bible verse and Footlamp explains it in plain words, then answers your "
        "questions. KJV, BSB and WEB offline on iOS and Android. No ads, no account.",
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
    collection follows whichever of KJV, BSB or WEB you read in, and tapping any verse
    opens it in the reader in full context &mdash; with the chapter around it, the other
    translations a tap away, and Explain there for anything that does not land.</p>
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
    both &mdash; tap it and choose <a href="../ai-bible-study-assistant/">Explain</a> for
    a plain-words summary, its context and why it matters, then keep asking follow-up
    questions in the same conversation until it makes sense. Explain and Ask are
    generated, so they are the parts of the app that need a connection.</p>
    <h2>When you are {e(felt)} and offline</h2>
    <p>The whole point of carrying all three translations on the device is that the moment
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
     "on the device and need no connection. Explain, Ask and prayers for a verse are "
     "generated, so they are the features that require one."),
    ("Do I have to download the Bible text first?",
     "No. All three translations ship inside the app, so there is nothing to download "
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
    title = "Offline Bible App - Read KJV, BSB & WEB With No Signal"
    description = ("Footlamp carries the full KJV, BSB and WEB on your phone. Reading, "
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
    text of the King James Version, the Berean Standard Bible and the World English
    Bible is carried on your device from the moment you install it.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid-2">
      <div class="card">
        <h2>Works with the network off</h2>
        <ul class="ticks">
          <li>Every book, chapter and verse in KJV, BSB and WEB</li>
          <li>Keyword search across the whole translation, instantly</li>
          <li>Topic collections for anxiety, hope, healing and encouragement</li>
          <li>Verse compare, side by side across all three translations</li>
          <li>The 7-day starter plan</li>
          <li>The verse of the day, in whichever translation you have chosen</li>
          <li>The daily reminder notification</li>
          <li>Your reading position, remembered exactly</li>
        </ul>
      </div>
      <div class="card card-ai">
        <h2>Needs a connection</h2>
        <ul class="ticks crosses">
          <li>Explain &mdash; the plain-words explanation of a verse</li>
          <li>Ask &mdash; a question, and the follow-ups in a conversation</li>
          <li>A prayer written for the verse in front of you</li>
        </ul>
        <p class="muted">That is the whole list. These run on a server because the
        answer is generated, not looked up. When a request fails on a bad connection the
        app says so rather than waiting forever, and a failed request is never charged
        against your daily allowance.</p>
        <p><a href="../ai-bible-study-assistant/">How Explain and Ask work &rarr;</a></p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Nothing to download, nothing to manage</h2>
    <p>Some Bible apps are readers with a download manager attached: you pick a
    translation, wait for it, and discover on the plane which ones you forgot. All three
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
    returning to the app costs no navigation. Switching translation keeps you on the
    same verse, so you can read a passage in another wording without hunting for your
    place again.</p>
    <h2>What leaves your device</h2>
    <p>Only what you send to Explain or Ask, or a verse you ask a prayer for, and only
    when you ask. Nothing about your reading &mdash; not the chapter,
    not your searches, not the topics you open &mdash; is sent anywhere, because none of
    it needs to be. The <a href="{PRIVACY_URL}">privacy policy</a> sets this out in
    full, and there is <a href="../bible-app-without-ads/">no account and no
    advertising</a> attached to any of it.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(OFFLINE_FAQ)}</div>
</section>

{band("The whole Bible, with the radio off",
      "Free to download on iOS and Android. KJV, BSB and WEB bundled, nothing to download afterwards.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "Offline Bible app"),
          faq_ld(OFFLINE_FAQ)], og_type="article")


AI_FAQ = [
    ("What do Explain and Ask do?",
     "Explain works on a single verse: tap it while reading and get a one-line summary, "
     "what it says, its context and why it matters, with key phrases highlighted, "
     "related verses and follow-up questions. Ask takes a question in your own words "
     "and answers it from scripture, and you can keep asking in the same conversation."),
    ("How many requests do I get for free?",
     "Five a day, shared between Explain and Ask and resetting at your own local "
     "midnight. The app shows how many are left before you spend one."),
    ("What happens if a request fails?",
     "Nothing is charged. Only answered requests count against the allowance, so "
     "trying again after a dropped connection costs nothing."),
    ("Are the answers written by a person?",
     "No. Explanations and answers are generated by a language model. The verse text "
     "and the related verses you see are quoted from the Bible on your phone, so the "
     "scripture itself is always one tap away to read for yourself."),
    ("Are my conversations saved?",
     "Yes, they are kept from the start &mdash; so subscribing reveals a history that "
     "already exists rather than an empty list. Reading back and continuing a past "
     "conversation is a Premium feature."),
    ("Do Explain and Ask work offline?",
     "No. They are generated, so they need a connection. Everything else &mdash; "
     "reading, search, compare, topics, the starter plan and the verse of the day "
     "&mdash; works with no network at all."),
]


def build_ai() -> None:
    slug = "ai-bible-study-assistant"
    title = "Explain Any Bible Verse, Ask Any Question - Footlamp"
    description = ("Tap any Bible verse for a plain-words explanation, its context and why "
                   "it matters, then ask your questions. Five a day free, on iOS and "
                   "Android.")
    body = f"""
{breadcrumbs(slug, "Explain & Ask")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Explain &amp; Ask</span>
    <h1>Stuck on a verse? <span class="ai-text">Tap it, and it&rsquo;s explained.</span></h1>
    <p class="lead">Not every verse lands the first time, and not everyone arrives at the
    Bible with a chapter and verse. Some arrive with a question &mdash; &ldquo;what does
    the Bible say about anxiety?&rdquo; &mdash; and no idea where to start looking.
    Explain and Ask are for both.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid grid-3">
      <div class="card card-ai">
        <span class="eyebrow">Explain</span>
        <h3>Any verse, in plain words</h3>
        <p class="muted">Tap a verse while reading and choose Explain. A one-line
        summary comes first, then what it says, its context and why it matters, in about
        a minute&rsquo;s reading. It works on every verse in every book, in all three
        translations.</p>
      </div>
      <div class="card card-ai">
        <span class="eyebrow">Ask</span>
        <h3>A question, in your own words</h3>
        <p class="muted">Ask has its own tab. Type anything, or tap a suggestion
        &mdash; &ldquo;What is grace?&rdquo;, &ldquo;Who was Paul?&rdquo;, &ldquo;How do I
        start praying?&rdquo; &mdash; and get an answer drawn from scripture.</p>
      </div>
      <div class="card card-ai">
        <span class="eyebrow">Keep asking</span>
        <h3>Follow-ups, in the same conversation</h3>
        <p class="muted">Context carries from one turn to the next, so you can think
        something through instead of starting over. Start a new conversation when the
        subject changes, so an unrelated question never inherits the last topic.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>What an explanation looks like</h2>
    <ul>
      <li><strong>The verse, with key phrases highlighted.</strong> One to three phrases
      are marked in the verse itself; tap one for a short note on it.</li>
      <li><strong>In one line.</strong> The verse summed up in a single sentence.</li>
      <li><strong>What it says, context, why it matters.</strong> Three short sections in
      plain words, not a commentary shelf.</li>
      <li><strong>Related verses.</strong> Two to four references with a line on why each
      one is related. Their text is quoted from the Bible on your phone, and a tap opens
      the reader there.</li>
      <li><strong>Think about it.</strong> Three follow-up questions; tap one and it is
      asked in the same conversation.</li>
    </ul>
    <h2>Pointing back at the text</h2>
    <p>Explain and Ask are built to send you back to scripture rather than stand in
    front of it. The verse is on the screen above the explanation, related verses open in
    the reader with the chapter around them, and the text to read for yourself is always
    one tap away. Explanations and answers are generated by a language model, so read
    them the way you would read a note in the margin.</p>
    <h2>Five a day, free, and nothing hidden</h2>
    <p>Explain and Ask cost real money to run, so everyone gets five requests a day,
    shared between the two. Three things follow from that, all of them deliberate:</p>
    <ul>
      <li><strong>The allowance is visible before you spend it.</strong> The app shows
      how many requests remain, so running out is never a surprise delivered
      mid-thought.</li>
      <li><strong>It resets at your local midnight</strong>, at the start of your day
      rather than at the start of a server&rsquo;s.</li>
      <li><strong>A failed request is not charged.</strong> Only answered requests count,
      and trying again after a dropped connection costs nothing.</li>
    </ul>
    <h2>What Premium adds</h2>
    <p>Premium makes Explain and Ask unlimited and keeps your past conversations, so a
    thought from last week can be read back and continued rather than retyped.
    Conversations are kept from the beginning, which means subscribing reveals a history
    that already exists rather than an empty list.</p>
    <p>It is bought through your existing App Store or Google Play account &mdash; no new
    payment details &mdash; a previous purchase can be restored on a new device, and it is
    cancelled from your own store settings at any time. Reading, search, compare, topics,
    the starter plan, the verse of the day, prayers and reminders are never locked,
    whether you subscribe or not.</p>
    <h2>What happens to your question</h2>
    <p>A question you ask, or a verse you ask to have explained, is sent to our server,
    forwarded to a language model to be answered, and stored so your conversations work.
    It is linked to an anonymous identity created silently on first launch, not to a name
    or an email address, because <a href="../bible-app-without-ads/">the app never asks
    you for one</a>. The <a href="{PRIVACY_URL}">privacy policy</a> is the authority on
    this.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(AI_FAQ)}</div>
</section>

{band("Explain your first verse today",
      "Five Explain or Ask requests a day, free, with no account to create first.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "Explain & Ask"),
          faq_ld(AI_FAQ)], og_type="article")


# Philippians 4:6, read from the en_bsb.xml and en_web.xml bundled in the app.
# Both translations are in the public domain.
COMPARE_SAMPLE = {
    "ref": "Philippians 4:6",
    "BSB": ("Be anxious for nothing, but in everything, by prayer and petition, with "
            "thanksgiving, present your requests to God."),
    "WEB": ("In nothing be anxious, but in everything, by prayer and petition with "
            "thanksgiving, let your requests be made known to God."),
}

COMPARE_FAQ = [
    ("Which translations does Footlamp include?",
     "The King James Version, the Berean Standard Bible and the World English Bible, "
     "and no others. All three are bundled on the device."),
    ("Does Footlamp have the ESV or the NIV?",
     "No. The three translations in the app are all in the public domain, which is what "
     "lets them be carried in full on your phone and quoted freely."),
    ("Can I switch translation without losing my place?",
     "Yes. Switching keeps you on the same verse, so you can read a passage in another "
     "wording without hunting for your place again."),
    ("Can I see all three at once?",
     "Yes. Tap a verse and choose compare, and the same verse is shown side by side "
     "across all three translations."),
    ("Which translation should I read?",
     "Whichever your church, study group or memory prefers &mdash; that is what the "
     "compare screen is for. The KJV is the older, more literary text; the BSB and WEB "
     "are modern English. Reading a verse in more than one is usually more useful than "
     "choosing once."),
]


def build_compare() -> None:
    slug = "compare-bible-translations"
    sample = TOPICS["Anxiety"][0]
    assert sample["ref"] == COMPARE_SAMPLE["ref"]
    title = "KJV vs BSB vs WEB - Compare Bible Translations"
    description = ("How the King James Version, Berean Standard Bible and World English "
                   "Bible differ, and how to read one verse in all three. Offline in "
                   "Footlamp on iOS and Android.")
    body = f"""
{breadcrumbs(slug, "KJV, BSB & WEB")}
<section>
  <div class="wrap prose">
    <span class="eyebrow">Translations</span>
    <h1>KJV, BSB and WEB, side by side</h1>
    <p class="lead">Footlamp carries three translations: the King James Version, the
    Berean Standard Bible and the World English Bible. All three live on your device, you
    can switch between them without losing your place, and you can put a single verse
    side by side across all three before drawing a conclusion from its wording.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="table-scroll">
      <table>
        <caption>All three translations are bundled in the app; nothing here is a download.</caption>
        <thead>
          <tr><th scope="col">&nbsp;</th><th scope="col">King James Version</th><th scope="col">Berean Standard Bible</th><th scope="col">World English Bible</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Origin</th><td>1611, in the form most people know since 1769</td><td>A recent translation from the Hebrew and Greek</td><td>An update of the 1901 American Standard Version</td></tr>
          <tr><th scope="row">Register</th><td>Early modern English &mdash; literary, familiar from memory and liturgy</td><td>Contemporary English, plain and readable</td><td>Modern English that keeps close to the older wording</td></tr>
          <tr><th scope="row">Reads well when</th><td>You know passages by heart, or your church reads from it</td><td>You want the wording to get out of the way</td><td>You want modern English with a word-for-word feel</td></tr>
          <tr><th scope="row">Copyright</th><td>Public domain</td><td>Public domain</td><td>Public domain</td></tr>
          <tr><th scope="row">In the app</th><td>Full text, offline</td><td>Full text, offline</td><td>Full text, offline</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section>
  <div class="wrap prose">
    <h2>Why compare at all</h2>
    <p>Any translation is a set of decisions, and the decisions are most visible where
    translations diverge. Reading a verse in more than one is the cheapest way to see
    where a reading rests on the underlying text and where it rests on a translator&rsquo;s
    choice of English word &mdash; which is exactly the point at which it is worth slowing
    down.</p>
    <p>Here is a verse the app curates under <a href="../bible-verses-about-anxiety/">anxiety</a>,
    in all three:</p>
  </div>
  <div class="wrap"><ul class="verse-list">
    <li class="verse"><blockquote>&ldquo;{e(sample["text"])}&rdquo;</blockquote><cite>{e(sample["ref"])} &middot; KJV</cite></li>
    <li class="verse"><blockquote>&ldquo;{e(COMPARE_SAMPLE["BSB"])}&rdquo;</blockquote><cite>{e(sample["ref"])} &middot; BSB</cite></li>
    <li class="verse"><blockquote>&ldquo;{e(COMPARE_SAMPLE["WEB"])}&rdquo;</blockquote><cite>{e(sample["ref"])} &middot; WEB</cite></li>
  </ul></div>
  <div class="wrap prose">
    <p>&ldquo;Be careful for nothing&rdquo; meant &ldquo;be anxious about nothing&rdquo; in
    1611 and means close to its opposite in casual reading today. That is not a flaw in
    the KJV; it is four centuries of drift in one English word, and the BSB and WEB
    renderings make it plain at a glance. That is the kind of thing verse compare exists
    to surface.</p>
    <h2>How it works in the app</h2>
    <ul>
      <li><strong>Tap a verse</strong> to open a small action card &mdash; everything you
      might want to do with that verse is in one place.</li>
      <li><strong>Choose compare</strong> and the verse appears side by side across all
      three translations, in a stable order.</li>
      <li><strong>Switch translation</strong> and you stay on the same verse.</li>
      <li><strong>Choose Explain</strong> for a plain-words explanation of the verse
      &mdash; that is <a href="../ai-bible-study-assistant/">Explain</a>, and it needs a
      connection.</li>
    </ul>
    <p>Your chosen translation applies everywhere: the reader, keyword search, the topic
    collections and the verse of the day all follow it, so the choice is made once
    rather than repeated per screen.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(COMPARE_FAQ)}</div>
</section>

{band("Compare any verse, offline",
      "All three translations bundled, free to download on iOS and Android, with nothing to download afterwards.")}
"""
    page(slug, title, description, body,
         [ORGANISATION, WEBSITE, SOFTWARE_APP, breadcrumb_ld(slug, "KJV, BSB & WEB"),
          faq_ld(COMPARE_FAQ)], og_type="article")


def build_redirect(old_slug: str, new_slug: str) -> None:
    """A retired page. GitHub Pages has no server-side redirects, so the old URL
    keeps a stub that refreshes to the new one and points search engines at it."""
    target = abs_url(new_slug)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved &ndash; {e(SITE_NAME)}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url=../{new_slug}/">
</head>
<body>
<p>This page has moved to <a href="../{new_slug}/">{target}</a>.</p>
</body>
</html>
"""
    out = ROOT / old_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"  {out.relative_to(ROOT)} (redirect)")


VOTD_FAQ = [
    ("Where does the verse of the day come from?",
     "A curated set of thirty verses, chosen for the moments people bring to "
     "scripture, each with its own artwork."),
    ("Can I get a daily reminder?",
     "Yes, at the time you choose. Turn it on from the Profile screen, and off again "
     "just as easily. It is scheduled on the device, so it fires without a network "
     "connection."),
    ("Does the verse of the day follow my translation?",
     "Yes. It is shown in whichever of KJV, BSB or WEB you have chosen, matching the rest "
     "of your reading."),
    ("What is the guided prayer?",
     "A short two-step prayer and reflection attached to the day's verse, so the "
     "daily verse becomes a practice rather than just a card. You can step forward and "
     "back through it, and when you finish, the card offers to go deeper: have the "
     "verse explained, or talk it through."),
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
        <p class="muted">One of thirty curated passages, shown in whichever of KJV,
        BSB or WEB you read in, on its own artwork. It stays the same all day, and
        survives an app update &mdash; upgrading never resets your day.</p>
      </div>
      <div class="card">
        <span class="eyebrow">Step two</span>
        <h3>Pray with it</h3>
        <p class="muted">A short two-step prayer and reflection attached to that verse.
        Step forward and back freely. When you are done, go deeper: have the verse
        explained, or talk it through.</p>
      </div>
      <div class="card">
        <span class="eyebrow">Optional</span>
        <h3>The reminder</h3>
        <p class="muted">One toggle on the Profile screen, at the time you choose. It is scheduled
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
    across <a href="../compare-bible-translations/">all three translations</a>, or have
    it <a href="../ai-bible-study-assistant/">explained</a> in plain words and talk it
    through until it lands. If the verse names something you are carrying, the
    <a href="../bible-verses-about-hope/">topic collections</a> go deeper on it.</p>
    <p>The verse, its artwork and the reminder <a href="../offline-bible-app/">work
    offline</a>; Explain and talking it through need a connection. Nothing here costs
    anything, and there is nothing to sign up for.</p>
    <h2>Questions</h2>
  </div>
  <div class="wrap">{faq_html(VOTD_FAQ)}</div>
</section>

{band("Start tomorrow with something already chosen",
      "Free to download on iOS and Android. A verse, a prayer, and a reminder if you want one.")}
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
     "anonymous identity is created silently on first launch so Explain, Ask and "
     "your conversations work."),
    ("What personal information is collected?",
     "No name, email address, phone number, postal address or payment details &mdash; "
     "nothing in the app asks for any of them. Explain and Ask requests and their "
     "answers are stored against an anonymous identifier so your conversations work."),
    ("Is my reading tracked?",
     "No. Reading, search, topics, verse compare and the verse of the day all run on "
     "the device and send nothing. Anonymous app usage and crash analytics are "
     "collected; there is no cross-app tracking and no advertising identifier "
     "request."),
    ("How is the app paid for, if not by ads?",
     "By an optional Premium subscription that makes Explain and Ask unlimited and "
     "keeps your past conversations. Everything the ad-supported version did is still "
     "free and unlimited."),
]


def build_no_ads() -> None:
    slug = "bible-app-without-ads"
    title = "A Bible App With No Ads and No Account - Footlamp"
    description = ("No advertising, no sign-up, no email address and no password. Read "
                   "the Bible offline in KJV, BSB and WEB without handing over anything. Free "
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
          <li>Creates an anonymous identity silently on first launch, so Explain, Ask
          and your conversations work without an account</li>
          <li>Keeps reading, search, topics, compare and the verse of the day entirely
          on your device</li>
          <li>Sends only what you give Explain or Ask, or a verse you ask a prayer
          for, and only when you ask</li>
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
    subscription: reading, all three translations, keyword search, topic collections, verse
    compare, the verse of the day, generated prayers and the daily reminder are free and
    unlimited, and will stay that way.</p>
    <p>Premium adds two things &mdash; unlimited Explain and Ask, and your past
    conversations kept to read back and continue &mdash; because those are the things
    that cost money to run. You can reach the
    offer deliberately from the Profile screen rather than only discovering it by
    running out.</p>
    <h2>Transparency inside the app</h2>
    <ul>
      <li>The Privacy Policy and the Terms of Use open from inside the app, both before
      and after subscribing, so the documents never become unreachable.</li>
      <li>The purchase screen states plainly that you can cancel from your own store
      account settings at any time.</li>
      <li>The Profile screen shows your subscription status and how many Explain and
      Ask requests remain today, so the state of your account is never hidden.</li>
      <li>Send feedback from the Profile screen whenever you want to.</li>
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
        "No account, no ads, and nothing collected while you read. What Explain and Ask "
        "send to our server, what is kept, and how to have it deleted."
    )
    body = f"""
<section class="hero">
  <div class="wrap prose">
    <span class="eyebrow">Privacy</span>
    <h1>Privacy Policy</h1>
    <p class="lead">Reading, searching and the verse of the day never leave your
    device. Explain, Ask and verse prayers are the features that do, and this page sets
    out exactly what they send and what is kept.</p>
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
    build_compare()
    build_redirect("kjv-vs-esv", "compare-bible-translations")
    build_votd()
    build_no_ads()
    for name in TOPICS:
        build_topic(name)
    build_privacy()
    build_404()

    build_sitemap(
        [("", "1.0")]
        + [(s, "0.8") for s in
           ("offline-bible-app", "ai-bible-study-assistant", "compare-bible-translations",
            "verse-of-the-day", "bible-app-without-ads")]
        + [(f"bible-verses-about-{n.lower()}", "0.7") for n in TOPICS]
    )

    # .nojekyll keeps GitHub Pages from running the output through Jekyll, which
    # would otherwise skip files and directories beginning with an underscore.
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("Done.")


if __name__ == "__main__":
    main()
