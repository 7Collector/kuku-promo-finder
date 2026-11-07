Use a segmented control for two to four exclusive options that switch what is being shown or written (Day, Week, Month). It does not navigate. The thumb and the label weight carry the selection.

```html
<div class="om-segmented" role="radiogroup" style="--om-segment-count:3;--om-segment-index:1">
  <button class="om-segmented__option" role="radio" aria-checked="false"><span>Day</span></button>
  <button class="om-segmented__option is-selected" role="radio" aria-checked="true"><span>Week</span></button>
  <button class="om-segmented__option" role="radio" aria-checked="false"><span>Month</span></button>
</div>
```

- Set `--om-segment-count` to the number of options and `--om-segment-index` to the chosen one (from 0); the thumb slides between them over the standard duration. Put `is-selected` on the chosen option.
- `is-empty`: nothing chosen yet, no thumb.
- `is-disabled`: every label drops to ink 3; the thumb stays where the answer is.
- Tone for the chosen option only: `om-segmented--success`, `--danger`, `--warning`, `--info`, `--help`, `--tip`, `--neutral`.
- Full width, sunken pill track with a 2 px inset, 48 px options, labels wrap to two lines.

Compose source: omega-kmp :ui, SegmentedControl.kt, `OmegaSegmentedControl(options, selected, label, onSelect, enabled, selectedTone)`
