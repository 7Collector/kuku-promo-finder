Use the send button as the composer's send control. It takes the AI gradient when there is something to send and is fully disabled when there is not.

```html
<button class="om-send" aria-label="Send"><span class="om-send__circle"><i class="om-icon om-icon-arrow-up"></i></span></button>
<button class="om-send is-disabled" aria-label="Send" disabled><span class="om-send__circle"><i class="om-icon om-icon-arrow-up"></i></span></button>
```

- `om-send`: a 48 px target holding a 40 px circle with a 20 px glyph in paper on the AI gradient.
- `is-disabled` (or `disabled`): sunken circle, ink 3 glyph, no press feedback.
- The glyph can be swapped (the `icon` parameter); arrow up is the default.

Compose source: omega-kmp :ui, OmegaComposer.kt, `OmegaSendButton(enabled, description, onClick, icon)`
