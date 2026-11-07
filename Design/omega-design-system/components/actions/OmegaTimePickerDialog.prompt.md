Use the time picker dialog to choose a time; it is what the time field opens. A surface card over the scrim, with the clock in Omega colours and Cancel and Done as buttons.

```html
<div class="om-picker-scrim"><div class="om-picker-dialog" role="dialog">
  <h2 class="om-picker-dialog__title">Reminder time</h2>
  <div class="om-time-picker">
    <div class="om-time-picker__display"><span class="om-time-picker__unit is-selected">18</span><span class="om-time-picker__separator">:</span><span class="om-time-picker__unit">00</span></div>
    <div class="om-time-picker__dial"><span class="om-time-picker__hand om-time-picker__hand--inner" style="--om-dial-angle:180deg"></span>
      <span class="om-time-picker__number om-time-picker__number--inner is-selected" style="--om-dial-angle:180deg">18</span></div>
  </div>
  <div class="om-picker-dialog__actions"><button class="om-button om-button--secondary om-button--compact">Cancel</button><button class="om-button om-button--primary om-button--compact">Done</button></div>
</div></div>
```

- `om-time-picker__unit.is-selected`: the field being edited (accent container); the other is sunken.
- `om-time-picker__number` with `--om-dial-angle` (30 degrees per hour); `--inner` for the 24-hour inner ring; `is-selected` for the chosen number. `om-time-picker__hand` takes the same angle.
- `om-time-picker__period`: the AM/PM selector, 12-hour clocks only.

Compose source: omega-kmp :ui, OmegaPickerDialogs.kt, `OmegaTimePickerDialog(state, title, onConfirm, onDismiss, confirmLabel, dismissLabel)`, `omegaTimePickerColors`
