Use the text field for every single-line input. It draws its own bordered container and the label sits above it, never inside. An error always comes with a message.

```html
<div class="om-field">
  <label class="om-field__label">Homework title</label>
  <div class="om-field__box"><input class="om-field__input" placeholder="Chapter 4 worksheet" aria-label="Homework title"></div>
  <p class="om-field__support">Shown to every section you pick below</p>
</div>
```

- `is-error`: danger border, text and caret; `om-field__support` then holds the required error message.
- `is-disabled`: sunken fill, hairline border, ink 3 text.
- `om-field--accent` with `--om-field-accent`: border and text in a colour that reflects the value (a score box). Ignored when disabled or in error.
- `om-field--center`: centred text. `om-field--bare`: no container, only where the surroundings already are one.
- Label and supporting text are optional. Focus changes only the caret (accent mark); `om-field__caret` draws one in a static mock.
- 48 px minimum height, radius md, 12 px padding, body text, placeholder in ink 3. There is no character counter.

Compose source: omega-kmp :ui, OmegaTextField.kt, `OmegaTextField(value, onValueChange, contentDescription, label, placeholder, supportingText, isError, errorMessage, enabled, bare, accent, textAlign)`, `fieldVisuals`
