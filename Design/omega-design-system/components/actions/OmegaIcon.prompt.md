Use an icon from the Omega set at the system stroke weight, with its colour always given. An icon beside a label that already says the same thing is decorative and stays silent.

```html
<i class="om-icon om-icon--s20 om-icon-calendar" style="color:var(--ink-2)"></i>
<i class="om-icon om-icon--s20 om-icon-warning" role="img" aria-label="Overdue" style="color:var(--danger-strong)"></i>
```

- Size: `om-icon--s20` (the composable's default), `om-icon--s18` (inside buttons), `om-icon--s16` (the chip tick). Without one, `om-icon` uses `--icon-size`, 24 px by default.
- Colour comes from `color`; the usual choice is ink 2, or the colour of the label beside it.
- A meaningful icon gets `role="img"` and an `aria-label`; a decorative one gets neither.

Compose source: omega-kmp :ui, OmegaPrimitives.kt, `OmegaIcon(imageVector, contentDescription, tint, size = 20.dp)`
