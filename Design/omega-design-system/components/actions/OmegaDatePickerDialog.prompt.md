Use the date picker dialog to choose a day; it is what the date field opens. The selected day is filled with the accent, today is ringed, and Done stays disabled until a day is chosen.

```html
<div class="om-picker-scrim"><div class="om-picker-dialog om-picker-dialog--date" role="dialog">
  <h2 class="om-picker-dialog__title">Due date</h2>
  <div class="om-date-picker">
    <p class="om-date-picker__headline">Oct 22, 2026</p><div class="om-date-picker__rule"></div>
    <div class="om-date-picker__nav"><span class="om-date-picker__month">October 2026<i class="om-icon om-icon-chevron-right"></i></span>
      <button class="om-date-picker__arrow"><i class="om-icon om-icon-chevron-left"></i></button><button class="om-date-picker__arrow"><i class="om-icon om-icon-chevron-right"></i></button></div>
    <div class="om-date-picker__week"><span class="om-date-picker__weekday">S</span><!-- seven --></div>
    <div class="om-date-picker__week"><span class="om-date-picker__day is-today"><span>13</span></span><span class="om-date-picker__day is-selected"><span>22</span></span><!-- seven per row --></div>
  </div>
  <div class="om-picker-dialog__actions"><button class="om-button om-button--secondary om-button--compact">Cancel</button><button class="om-button om-button--primary om-button--compact">Done</button></div>
</div></div>
```

- `om-picker-dialog--date`: 12 px side padding (the calendar brings its own gutters); title and actions keep the 24 px keyline.
- `om-date-picker__day`: a 48 px cell with a 40 px circle. `is-selected`: accent fill. `is-today`: accent mark ring, accent text. Empty cells keep their width.
- No day chosen yet: give Done `is-disabled`.

Compose source: omega-kmp :ui, OmegaPickerDialogs.kt, `OmegaDatePickerDialog(state, onConfirm, onDismiss, confirmEnabled, title, confirmLabel, dismissLabel)`, `omegaDatePickerColors`
