# OfflineBanner

The device is offline. It uses the neutral tone: grey means offline, never a warning, because nothing is wrong with the data on screen; it is the last saved copy.

```html
<div class="om-offline-banner" role="status">
  <i class="om-icon om-icon-cloud-off"></i>
  <div class="om-state-body"><div class="om-state-text">Offline — showing saved data</div></div>
</div>
```

Variants: default text or the caller's. Neutral container, radius lg, 16 padding, the cloud-off glyph at 20 in neutral strong. No action and no title.

Compose source: omega-kmp :ui, OmegaStates.kt, `OfflineBanner(text)`, `OFFLINE_BANNER_TEXT`, built on `Callout(tone = Tone.Neutral, icon = CloudOff)`
