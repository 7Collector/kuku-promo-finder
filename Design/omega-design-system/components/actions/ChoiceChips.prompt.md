Use choice chips to pick from a short set of options: one of many (radio) or several of many (checkbox). The chosen chip always shows a tick, so selection is never carried by colour alone.

```html
<div class="om-chips" role="radiogroup">
  <button class="om-chip is-selected" role="radio" aria-checked="true"><i class="om-icon om-icon-check"></i>8B</button>
  <button class="om-chip" role="radio" aria-checked="false">9A</button>
</div>
```

- `om-chips`: the horizontally scrolling row, page-margin padding at both ends, 8 px between chips. A single `om-chip` also works on its own in any row.
- `om-chip`: pill, 48 px minimum height, surface with an outline border, ink 2 label.
- `is-selected`: accent container fill, no border, 16 px tick before the label.
- Several of many: the same chip with `role="checkbox"`.
- `is-pressed`: static mock of the press layer. Choice chips have no disabled state; see OmegaToggleChip for one.

Compose source: omega-kmp :ui, ChoiceChips.kt, `ChoiceChips(options, isSelected, label, onToggle, multiSelect)`, `OmegaChoiceChip(text, selected, onClick, role, showTick)`, `selectionChipVisuals`
