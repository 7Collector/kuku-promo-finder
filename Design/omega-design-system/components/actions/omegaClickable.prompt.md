Use press feedback on anything tappable that is not already a button, chip or field. Rows and buttons take the ink ripple layer alone; only a tile or card that is one tap target also scales.

```html
<button class="om-pressable om-pressable--scale">Attendance tile</button>
<a class="om-pressable">List row</a>
```

- `om-pressable`: an ink layer at 8% on hover and 10% while pressed, over the fast duration.
- `om-pressable--scale`: also scales to 98% while pressed; skipped under reduced motion.
- `is-pressed`: static mock of the pressed state.
- The element needs its own radius so the layer follows its shape. There is no entrance animation here.

Compose source: omega-kmp :ui, OmegaPress.kt, `Modifier.omegaClickable(onClick, enabled, role, scaleOnPress)`, `pressedScale`, `PRESSED_SCALE`
