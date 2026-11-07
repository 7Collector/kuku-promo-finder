# OmegaSurface

Use a surface for any block that sits on paper; name the role and the role chooses fill and radius. Separation is paper versus surface and hairlines, never a shadow.

```html
<div class="om-surface">…</div>
<div class="om-surface om-surface--tonal">…</div>
<div class="om-surface om-surface--tappable" role="button" aria-label="Homework, 3 pending">…</div>
<hr class="om-hairline">
```

- `.om-surface`: Flat, Editorial, Raised and Overlay all draw the same: surface fill, radius lg, 16 padding.
- `.om-surface--tonal`: sunken fill, radius md.
- `.om-surface--flush`: content padding 0 (what a list group uses).
- `.om-surface--tappable`: one target, 48 minimum; `:active` or `.is-pressed` gives the ink ripple and the 0.98 scale.
- `.om-hairline`: a 1 px rule in hairline. A divider and only a divider.
- A translucent background override is composited over paper first; in CSS just set an opaque `background`.

Compose source: omega-kmp :ui, OmegaSurface.kt, OmegaSurface(role: OmegaSurfaceRole, onClick, contentDescription, background, contentPadding = 16.dp), OmegaHairline()
