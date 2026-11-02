# Repository design system

Theme: Hallmark Ink, selected by the user. Korean and general UI: Pretendard Variable.
Source of truth: css/tokens.css. Components: _sass/_ink.scss.
Scope: a searchable technical archive and long documents, not a marketing landing page.

Interface copy: use direct functional labels such as 전체 글, 태그, 글 검색.
Do not invent slogans, personal introductions, or decorative descriptions.

- Paper background, near-black type, teal for selected state and keyboard focus.
- One quiet index rail; content capped at 960px; article reading measure 72ch.
- Lists use thin rules and generous row spacing. No resting shadows or nested cards.
- Primary controls use ink; secondary controls use neutral paper and a visible border.
- All controls support visible keyboard focus. Loading, empty, error and full states are explicit.
- Desktop rail can collapse. Mobile menu traps focus only while open; hidden regions are inert.
- Mobile tag picker is searchable and bounded. Results are adjacent and reachable.
- Phone pagination always exposes previous and next actions.
- Code tokens never break internally inside tables; wide tables scroll independently.
- Existing post content, URLs, categories, tags, search index format and logo are preserved.
- Theme storage key theme-mode is retained: light is paper; legacy blue/dark chooses neutral night reading.
- No decorative motion. Reduced-motion disables state transitions.
- Font file: assets/fonts/PretendardVariable.woff2, upstream v1.3.9 with bundled OFL license.
