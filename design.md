# Repository design system

Theme: Hallmark Ink, selected by the user. Korean and general UI: Pretendard Variable.
Source of truth: css/tokens.css. Components: _sass/_ink.scss.
Scope: a searchable technical archive and long documents, not a marketing landing page.

Interface copy: use direct functional labels such as 전체 글, 태그, 글 검색.
Do not invent slogans, personal introductions, or decorative descriptions.

- Paper background, near-black type, teal for selected state and keyboard focus.
- Center a 620px reading column. Desktop post navigation has the index, search and article headings.
- List rows align the title left and date right, separated by space. No resting shadows or nested cards.
- Primary controls use ink; secondary controls use neutral paper and a visible border.
- All controls support visible keyboard focus. Loading, empty, error and full states are explicit.
- Archive navigation uses text links and a native alphabet disclosure. Mobile article contents fold below the date.
- Mobile tag picker is searchable and bounded. Results are adjacent and reachable.
- Phone pagination always exposes previous and next actions.
- Code tokens never break internally inside tables; wide tables scroll independently.
- Existing post content, URLs, categories, tags, search index format and logo are preserved.
- Theme storage key theme-mode is retained: light is paper; legacy blue/dark chooses neutral night reading.
- No decorative motion. Reduced-motion disables state transitions.
- Font file: assets/fonts/PretendardVariable.woff2, upstream v1.3.9 with bundled OFL license.
