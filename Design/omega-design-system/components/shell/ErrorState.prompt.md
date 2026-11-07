# ErrorState

Something failed: a danger callout that says what happened and what still works, with Retry only when there is something to retry.

```html
<div class="om-error-state" role="alert">
  <i class="om-icon om-icon-octagon-alert"></i>
  <div class="om-state-body">
    <div class="om-state-title">Attendance not sent</div>
    <div class="om-state-text">Three marks are still on this phone. Check your connection and try again.</div>
    <!-- optional tertiary button, painted in the callout's text colour: Retry -->
  </div>
</div>
```

Variants: message only; with retry; with a title (`.om-state-title`) and retry. Danger container, radius lg, 16 padding, a 20 icon in danger strong, 12 between icon and text.

Compose source: omega-kmp :ui, OmegaStates.kt, `ErrorState(text, title, retryLabel, onRetry)`, built on `Callout(tone = Tone.Danger)`
