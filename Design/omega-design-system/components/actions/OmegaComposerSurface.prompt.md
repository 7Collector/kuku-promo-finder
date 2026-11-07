Use the composer surface as the message bar of an AI chat. It is a pill that holds a bare text field and round controls; the AI gradient ring appears only while the field has focus.

```html
<div class="om-composer">
  <div class="om-composer__field"><div class="om-field om-field--bare" style="flex:1"><div class="om-field__box">
    <input class="om-field__input" placeholder="Ask about your homework" aria-label="Message"></div></div></div>
  <button class="om-send is-disabled" aria-label="Send" disabled><span class="om-send__circle"><i class="om-icon om-icon-arrow-up"></i></span></button>
</div>
```

- `is-focused` (or real focus inside): a 1.5 px AI gradient ring fades in over the outline border.
- `--om-composer-padding`: inner padding, 4 px by default.
- `om-composer__field`: the slot for the bare field, 48 px minimum so one line centres between the controls. Controls are bottom-aligned, so a long draft grows upward.
- `om-composer__action` (attach) and `om-composer__action--stop` are slot content as the school app fills it, not part of the library surface.

Compose source: omega-kmp :ui, OmegaComposer.kt, `OmegaComposerSurface(focused, contentPadding, content)`
