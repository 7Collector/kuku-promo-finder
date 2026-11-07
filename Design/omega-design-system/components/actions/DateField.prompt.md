Use the date field to choose a day. It is a read-only field showing the formatted date and a calendar glyph; a tap opens the date picker dialog. The caller formats the date.

```html
<div class="om-field">
  <span class="om-field__label">Due date</span>
  <button class="om-field__box om-field__box--picker" aria-label="Due date, Thu, 24 Sep">
    <span class="om-field__value">Thu, 24 Sep</span><i class="om-icon om-icon-calendar"></i>
  </button>
</div>
```

- `om-field__box--picker`: the text-field container as a button, value then a 20 px glyph in ink 2.
- `is-disabled` on `om-field`: sunken fill, hairline border, ink 3 value; the glyph stays ink 2.
- `is-pressed` on the box: static mock of the press layer. The label is optional. There is no error state.

Compose source: omega-kmp :ui, DateTimeFields.kt, `DateField(displayValue, selectedDateMillis, onDateSelected, contentDescription, label, enabled)`
