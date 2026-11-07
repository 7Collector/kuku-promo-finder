# Omega design system

The design system of the Omega school apps (teacher/student, parent, driver), mirrored from the
Compose Multiplatform source in `omega-kmp` `:ui` (`auroboris.omega.ui.designsystem`). The Kotlin
is the source of truth; this bundle is its HTML/CSS rendering for design work.

## Character

Quiet paper, ink, one ballpoint accent, one dark board.

- **Paper and surfaces.** Screens sit on `--paper`; grouped lists, tiles and sheets are white
  `--surface`. In-flow surfaces cast no shadow: separation is paper against surface, and hairlines.
  Only bottom sheets lift.
- **Ink ranks.** Hierarchy comes from type size, weight and the three ink tones, not from colour.
- **One accent.** `--accent` (default "ballpoint" blue `#2B4FD8`) is for primary buttons,
  selection, links, focus and progress. Schools can white-label it; the rest of the accent family
  is derived from it to hold WCAG contrast.
- **One board.** At most one dark `--board` surface per screen, for the thing that matters now.
- **Tones are semantic.** Info, help, tip, success, warning, danger and neutral map to domain
  states and always come with text or an icon. Never decorative.
- **The AI gradient** is the only gradient: the sparkle mark, the selected AI tab, the composer
  focus ring and the send button. Never a background, never text.
- **Subject colours** are labelled dots only, never filled chips.

## Rules that are easy to break

- Sentence case everywhere. No uppercase or letter-spaced labels (they mean nothing in Indic
  scripts).
- Never put text in a fixed-height container; line boxes are centred and untrimmed so tall
  scripts do not clip. Truncate with an ellipsis, never clip.
- Numbers (times, scores, counts, percentages) use tabular figures: add `.om-num`.
- Spacing is the 4 px scale only: 2, 4, 8, 12, 16, 20, 24, 32, 40, 48.
- Radii by component class: 6 badges, 12 controls and tiles, 16 lists and cards, 24 the board and
  sheets, pill for chips and avatars.
- Touch targets are at least 48 px; list rows at least 56 px (one line) or 72 px (two lines).
- Icons are the vendored Lucide paths at a 2.75 stroke, round caps, never filled:
  `<i class="om-icon om-icon-home"></i>`.
- Motion answers touch (100 / 180 / 280 ms), never loops, and is instant under reduced motion.
- Light only. There is no dark theme.

## Layout

- `styles.css` is the single entry point (imports only).
- `tokens/` holds colours, type, spacing, radii, elevation, motion, icons and the base.
- `components/<group>/` holds the component CSS, a preview card per family and a `.prompt.md`
  per composable naming its Compose source.
- `guidelines/` holds the foundation cards.

CSS variables use the Kotlin token names in kebab case (`OmegaTheme.colors.accentContainer` is
`--accent-container`, `OmegaTheme.typography.bodyStrong` is `--text-body-strong` and the class
`.om-body-strong`). dp and sp map 1:1 to px.
