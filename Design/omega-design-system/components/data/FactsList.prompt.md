# FactsList

Use for label and value pairs: label in subhead ink 2 at the start, value in body strong at the end, a hairline between rows. In compact mode each pair stacks so neither is squeezed.

```html
<div class="om-facts">
  <div class="om-facts__row"><span class="om-facts__label">Class teacher</span><span class="om-facts__value">Mrs Anjali Raghavan</span></div>
  <div class="om-facts__row"><span class="om-facts__label">Roll number</span><span class="om-facts__value">14</span></div>
</div>
```

- `.om-facts`: label and value share the width equally; the value is right-aligned and the label is centred against a wrapping value.
- `.om-facts--compact`: value under label, 2 apart, both left-aligned.
- The list has no surface of its own and its outer edges stay flush; place it inside a surface or card.

Compose source: omega-kmp :ui, OmegaList.kt, FactsList(facts: List<Pair<String, String>>), LocalCompact
