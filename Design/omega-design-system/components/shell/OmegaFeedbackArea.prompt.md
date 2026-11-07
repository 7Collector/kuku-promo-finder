# OmegaFeedbackArea

The app's one transient confirmation, for a success that happens where no inline message can live. One message at a time; a new one replaces the old, and it leaves after 4 seconds. It is a brief dark plate (the board with on-board text), never the accent. Draw it as a sibling over the shell: it clears the keyboard, the navigation bar and the shell's bottom layer, then a 16 gap. Failures do not use it.

```html
<div class="om-feedback-area" style="--feedback-clearance:64px">
  <div class="om-feedback-toast" role="status">Attendance saved for Class 7B</div>
</div>
```

Variants: none. `--feedback-clearance` is the height of whatever the shell has at the bottom (the plate, an action bar), or 0. The plate is full width less 24 side gaps, radius md, padding 16 by 12, subhead text, two lines at most. Renders nothing while there is nothing to say.

Compose source: omega-kmp :ui, OmegaFeedback.kt, `OmegaFeedbackArea(host, bottomLayer, onHaptic)`, `OmegaFeedbackHost.announce(message, haptic)`, `OmegaFeedbackHost.VISIBLE_MILLIS`
