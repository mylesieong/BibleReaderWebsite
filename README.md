# Bible Project — website

The static marketing site for **Bible Project**, the free Bible reader for Android and
iOS. It is a landing page plus a small set of SEO pages, and it is deliberately plain:
no framework, no JavaScript, no build step at serve time.

This repository is consumed as a **git submodule** of the app repository
(`mylesieong/bible-reader`), mounted at `website/`.

## Layout

```
index.html                          landing page
offline-bible-app/                  SEO — reading offline
ai-bible-study-assistant/           SEO — Father AI
kjv-vs-esv/                         SEO — comparing the two translations
verse-of-the-day/                   SEO — daily verse, prayer, reminder
bible-app-without-ads/              SEO — no ads, no account, privacy
bible-verses-about-anxiety/         SEO — topic collection
bible-verses-about-hope/            SEO — topic collection
bible-verses-about-healing/         SEO — topic collection
bible-verses-about-encouragement/   SEO — topic collection
privacy-policy.html                 the privacy policy (URL is in both store listings)
404.html                            not-found page (GitHub Pages serves this)
sitemap.xml, robots.txt             generated
assets/css/site.css                 the only stylesheet
assets/img/                         logo, favicon, Open Graph image
_data/topics.json                   the 30 curated verses (see below)
_data/privacy-policy.html           the policy prose, wrapped by the build
build.py                            the generator
```

Every HTML file above is **generated output and is committed**, so the site can be
served straight from the repository with nothing installed.

## Building

```bash
python3 build.py
```

Python 3.9+, standard library only. Edit `build.py` (copy, page structure, metadata) or
`_data/topics.json` (verse content), re-run it, and commit the changed HTML alongside
the source change.

## Deploying

This repository is mounted as a git submodule inside `mylesieong.github.io` at
`products/bible-project/`, and the site is served from
`https://mylesieong.github.io/products/bible-project/`. `.nojekyll` is emitted by the
build so Jekyll does not skip the underscore-prefixed `_data/` directory.

`privacy-policy.html` must keep its filename: both store listings point at
`https://mylesieong.github.io/products/bible-project/privacy-policy.html`.

**`BASE_URL` in `build.py` is the site's address.** It is the
only place the absolute URL appears — canonical tags, Open Graph URLs, JSON-LD and
`sitemap.xml` are all derived from it. Every link between pages is relative, so the
site works under any path without changes.

Two other constants near the top of `build.py` are placeholders:
`APP_STORE_URL` and `PLAY_STORE_URL` point at listings that are not live yet.

## Where the content comes from

- **Copy** is written against `docs/app_description_external_facing.md` and
  `docs/store-listing.md` in the app repository. The copy rules in §7 of the store
  listing apply here too — in particular: never claim audio, keyword search is not AI,
  KJV and ESV only, "Father AI" is capitalised exactly that way, and the free tier is
  never described as having lost something.
- **Colours** are the app's own palette, lifted from
  `shared/src/commonMain/kotlin/com/municornio/biblereader/ui/theme/Theme.kt` and
  mirrored as CSS custom properties at the top of `assets/css/site.css`. The app is
  light-only by design; the site preserves that rather than inventing a dark theme the
  product never had.
- **`_data/topics.json`** holds the 30 curated verses and their guided prayers,
  extracted from `GoldenVerse.kt` in the app, with the verse text resolved against the
  bundled `en_kjv.xml`. Verse text on the site is quoted from the **King James
  Version**, which is in the public domain; the ESV is copyrighted and is quoted only
  inside the app, under its own terms.

## SEO notes

Each page carries a unique `<title>` (≤ 65 characters) and meta description
(70–170 characters), a canonical URL, Open Graph and Twitter card tags, and JSON-LD:
`Organization`, `WebSite` and `MobileApplication` on every page, plus `FAQPage`,
`BreadcrumbList` and `ItemList` where they apply. There is exactly one `<h1>` per page,
headings are properly nested, every page is reachable from the footer, and all ten are
listed in `sitemap.xml`.
