Use the time field to choose a time of day. It is a read-only field showing the time and a clock glyph; a tap opens the time picker dialog.

```html
<div class="om-field">
  <span class="om-field__label">Reminder</span>
  <button class="om-field__box om-field__box--picker" aria-label="Reminder, 18:00">
    <span class="om-field__value om-num">18:00</span><i class="om-icon om-icon-clock"></i>
  </button>
</div>
```

- Same container and states as the date field: `is-disabled` on `om-field`, `is-pressed` on the box.
- Add `om-num` to the value so the digits are tabular. 24-hour by default.

Compose source: omega-kmp :ui, DateTimeFields.kt, `TimeField(displayValue, hour, minute, onTimeSelected, contentDescription, label, enabled, is24Hour)`
