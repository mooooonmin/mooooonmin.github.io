# Ink redesign verification

Date: 2026-11-02 (Asia/Seoul). User requested the Ink theme, Pretendard, and fixes
for the earlier UI/UX audit. This document records implementation and local validation.

## Implemented

- Ink paper/ink/teal tokens, quiet ruled lists, responsive index rail, and optional
  neutral night reading. Existing `theme-mode=blue` values remain compatible.
- Self-hosted Pretendard Variable v1.3.9, with upstream license. The previous
  theme styles and fonts remain in the repository but are no longer imported.
- Visible search submit control, inline search editing, query/result-count status,
  loading/empty/error/retry states, and clean Markdown snippets.
- Searchable bounded tag list; selected results are brought into view. URL history,
  failed-request retry, keyboard focus, and static no-JavaScript tag links work.
- Hidden sidebar leaves the tab order. Mobile menu isolates background focus,
  handles Escape, and restores focus to its trigger.
- Page h1/main landmark, skip link, real publication dates, linked alphabetical
  category, generated article contents, and full previous/next post titles.
- Phone pagination retains visible previous/current/next. Desktop keeps every
  numbered destination. Command tokens in tables never split internally.
- Korean interface states, 404 recovery links, and readable metadata/counts.
- Removed invented introductory slogans; page titles and navigation use direct
  functional labels such as `전체 글` and `태그`.

Implementation sources: `_layouts/default.html`, `_layouts/post.html`,
`_includes/pagination.html`, `_sass/_ink.scss`, `css/tokens.css`, `assets/js/site.js`,
`assets/js/tags.js`, `assets/js/search.js`, and `scripts/generate_search_index.py`.
No post bodies or existing post routes were edited.

## Verification

- `bundle exec jekyll build`: passed.
- `python scripts/validate_all.py --include-site-integrity --include-smoke`: passed. This includes
  17 Python tests and 4 Node search tests (17 + 4 = 21 unit tests), JavaScript syntax,
  source encoding, post format, duplicate times, whitespace, and site integrity.
- Generated-site integrity: 212 HTML files, 10,439 internal references, 223 images
  in the final run; these are the validator's scanned totals, not manually estimated.
- `python scripts/smoke_render.py`: passed, 11 routes × 2 viewports = 22 combinations.
- `python scripts/check_uiux.py`: passed. Checks include 6 routes × 6 widths = 36
  layout cases plus keyboard, mobile tags, pagination, table commands, search
  retry, saved theme, and no-JavaScript navigation scenarios. It is included in CI
  and in `validate_all.py --include-smoke`.
- Independent Hallmark finish review: two findings (sidebar button overlap,
  search control heights), both fixed and confirmed in recaptures; final verdict ship.

## Hallmark raw output and interpretation

The final rendered comparison preserved 126/126 recorded links and 1/1 named
fields. Heading changes reflect localized interface labels and the move from a
site-name h1 to a page h1. The linter's figure parser also counts concatenated
navigation numerals; its changed figure count does not indicate deleted article data.

Raw final output: 1 FAIL (73), 0 open REFLEX, 2 WARN (kept headings/figures),
11 WAIVED, 1 DISMISSED. Do not describe this as a fully clean automated run.

Gate 73 is a verified clipped-scroll false positive on the tag picker: the tool
compares off-scrollport text-node rectangles with footer hit-testing without
intersecting ancestor scroll clipping. The tag text is clipped inside the picker;
the footer is in normal flow below it. Both the implementation review and the
independent screenshot reviewer confirmed no painted overlap.

Recorded exceptions: Ink's deliberately neutral ink/grey tokens (22), and natural
wrapping of real technical titles/citations instead of truncation (49b). The
blockquote rule warning (3) is dismissed because it marks quoted article text.

Artifacts are outside the repository under:
`C:/Users/minhe/.codex/visualizations/2026/11/02/01a199f2-2747-7302-9e7f-400d5efd96cf/hallmark-audit/`.
Logs: `final-validation.log`, `ink-smoke.log`, `ink-uiux.log`, `ink-lint.log`.
Screenshots: `ink/`. Before/after comparison: `.hallmark/compare.html`.

These checks used local Chromium and the local Jekyll build. Live deployment,
real-device Safari, and screen-reader testing were not performed.
