Use the formula plate to set one formula apart from the text around it; it spans the full width, centres its content, and holds at most four lines.

```html
<div class="om-formula-plate"><span class="om-formula-plate-text">sin²θ + cos²θ = 1</span></div>
```

Classes: `om-formula-plate` (full width, sunken, radius md, padding 16, content centred), `om-formula-plate-text` (the formula type role in ink, centred, clipped after four lines). The plate has two forms: plain text as above, or a content slot that holds typeset LaTeX. Typeset maths always uses the light theme colours on a transparent background so it sits on the sunken plate; pass the ink colour and the formula size. HTML has no LaTeX renderer in this bundle, so a typeset formula is shown with a stand-in; do not imitate it with images.

Compose source: omega-kmp :ui, AiSurfaces.kt, `FormulaPlate(formula)` and `FormulaPlate(content)`; OmegaLatex.kt, `omegaLatexConfig(color, fontSize)`
