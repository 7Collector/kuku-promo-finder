Use a slider row to set a number within a range. The current value is always printed beside the label, because a thumb only shows roughly where a number is.

```html
<div class="om-slider-row">
  <div class="om-slider-row__head"><span class="om-slider-row__label">Amplitude</span><span class="om-slider-row__value">1.5</span></div>
  <div class="om-slider" role="slider" aria-label="Amplitude" aria-valuetext="1.5" style="--om-slider-value:.5">
    <span class="om-slider__active"></span><span class="om-slider__thumb"></span><span class="om-slider__inactive"></span>
  </div>
</div>
```

- `--om-slider-value`: position from 0 to 1.
- `om-slider--stepped`: a slider with stops; it hides the end mark (the ticks match their track and do not show).
- `is-disabled` on `om-slider-row`: thumb and active track in ink 3.
- Label in subhead, value in body strong with tabular digits; active track and thumb in accent mark, inactive track sunken. Place it on a surface.

Compose source: omega-kmp :ui, OmegaSliderRow.kt, `OmegaSliderRow(label, value, onValueChange, min, max, step, valueText, enabled)`
