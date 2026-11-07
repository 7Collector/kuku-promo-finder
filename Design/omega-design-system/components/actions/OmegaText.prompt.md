Use the text helper for any string that sits in a fixed-width surface. Long names and titles end in an ellipsis instead of being clipped, and there is no line cap unless you ask for one, so text survives larger font sizes.

```html
<span class="om-text om-text--lines-1 om-body-strong">Mathematics with Mrs Anjali Raghavan, Class 8 B</span>
<span class="om-text om-text--lines-2 om-subhead">Solve questions 1 to 12 from exercise 4.2 in your maths notebook.</span>
```

- `om-text`: block text that ends in an ellipsis when it overflows. Pair it with a type class (`om-body`, `om-subhead`, `om-caption` and the rest).
- `om-text--lines-1`, `--lines-2`, `--lines-3`: cap the number of lines. Without one, text wraps freely.
- Colour is set by the caller. Sentence case always; no style uppercases its text.

Compose source: omega-kmp :ui, OmegaPrimitives.kt, `OmegaText(text, style, color, maxLines, textAlign)`
