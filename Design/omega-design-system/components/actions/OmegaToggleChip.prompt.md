Use a toggle chip for one independent on or off setting, such as "Anonymous". It looks like a choice chip but is a switch, not one of a set; disable it while its value is being saved.

```html
<button class="om-chip is-selected" role="switch" aria-checked="true"><i class="om-icon om-icon-check"></i>Needs a guardian's signature</button>
<button class="om-chip" role="switch" aria-checked="false">Anonymous</button>
<button class="om-chip is-disabled" role="switch" aria-checked="false" disabled>Notify parents</button>
```

- `om-chip`: off. `is-selected`: on, with the 16 px tick.
- `is-disabled` (or `disabled`): sunken fill, ink 3 label, outline border kept. A disabled chip that is on keeps its tick.

Compose source: omega-kmp :ui, ChoiceChips.kt, `OmegaToggleChip(text, checked, onCheckedChange, enabled)`, `selectionChipVisuals(selected, enabled)`
