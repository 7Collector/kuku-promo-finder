# OmegaPill

A small caption label in a fully rounded pill, such as "Now", "Ch. 7 · Trigonometry" or "78 credits left". The caller chooses the fill and text colour as a pair from the tokens; when the visible label is an abbreviation, give it a spoken name.

```html
<span class="om-pill" style="--pill-bg:var(--accent-container);--pill-fg:var(--on-accent-container);--pill-dot:var(--accent-mark)">
  <span class="om-pill-dot"></span>Now
</span>
```

Variants: with or without the 5 px leading dot (`.om-pill-dot`, static). Colours through `--pill-bg`, `--pill-fg`, `--pill-dot`. One line, never wraps. Padding 10 by 4, gap 5.

Compose source: omega-kmp :ui, OmegaBottomNav.kt, `OmegaPill(text, background, contentColor, leadingDot, contentDescription)`
