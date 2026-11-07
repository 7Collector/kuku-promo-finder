Use the text area for longer writing such as notes or instructions. It is the text field in multi-line form: at least three lines tall and growing with its text.

```html
<div class="om-field om-field--area">
  <label class="om-field__label">Notes</label>
  <div class="om-field__box"><textarea class="om-field__input" rows="3" placeholder="Anything to bring?" aria-label="Notes"></textarea></div>
</div>
```

- `om-field--area`: sets the three-line minimum (72 px of text inside the 12 px padding).
- `is-error` with a message in `om-field__support`, and `is-disabled`, as on the text field.
- Label above and supporting text below are optional.

Compose source: omega-kmp :ui, OmegaTextField.kt, `OmegaTextArea(value, onValueChange, contentDescription, label, placeholder, supportingText, isError, errorMessage, enabled, minLines = 3)`
