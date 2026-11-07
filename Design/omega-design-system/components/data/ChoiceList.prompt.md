# ChoiceList

Use for radio or checkbox rows inside a grouped list. Each row is one control: the whole row takes the tap and carries the role and the selected state.

```html
<div class="om-choice-list" role="radiogroup">
  <div class="om-choice-row is-selected" role="radio" aria-checked="true">
    <span class="om-choice-mark"></span>
    <div class="om-choice-row__text"><span class="om-choice-row__label">Late</span></div>
  </div>
</div>
```

- `.om-choice-row`: 56 minimum; `.om-choice-row--two-line`: 72, with a `__supporting` line.
- `.is-selected` on the row (or the mark): accent mark fill with a surface dot.
- `.om-choice-mark--checkbox`: radius xs; put `<i class="om-icon om-icon-check"></i>` inside, shown only when selected.
- `:active` or `.is-pressed`: ink ripple. Rows are divided by a hairline starting at 50 px, the label keyline.
- There is no disabled state in the source.

Compose source: omega-kmp :ui, OmegaList.kt, ChoiceList(options, isSelected, label, onToggle, multiSelect = false, supporting)
