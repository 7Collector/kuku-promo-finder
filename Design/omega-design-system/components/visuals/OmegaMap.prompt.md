Use the mini map as a picture of where something is inside a card (no gestures; the whole box opens the full-screen map), and the full-screen map for looking around; while tiles load, when offline, or when maps are off, a sunken placeholder with the place name is shown instead.

```html
<div class="om-map">
  <a class="om-map-frame" role="button" aria-label="Map of Temple corner, with the bus">
    <svg class="om-map-canvas" viewBox="0 0 290 146" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect class="om-map-ground" width="290" height="146"/><path class="om-map-street" stroke-width="12" d="M-10 58H300"/>
      <path class="om-map-route-casing" d="M16 58H270"/><path class="om-map-route is-driven" d="M16 58H136"/><path class="om-map-route" d="M136 58H270"/>
      <circle class="om-map-landmark" cx="270" cy="58" r="5"/><text class="om-map-label is-landmark" x="270" y="80">School</text>
    </svg>
  </a>
  <p class="om-map-attribution">OpenFreeMap © OpenMapTiles Data from OpenStreetMap</p>
</div>
<!-- not drawn: <a class="om-map-frame"><span class="om-map-placeholder"><i class="om-icon om-icon-map-pin"></i><span>Temple corner</span><span class="om-map-placeholder-note">You are offline.</span></span></a> -->
```

Classes: `om-map`, `om-map-frame` (at least 148 tall, radius md, hairline), `om-map-attribution` (always shown, 4 below), `om-map-placeholder`, `om-map-placeholder-note`; drawing: `om-map-ground`, `om-map-street`, `om-map-route-casing` (8, surface), `om-map-route` (5, accent mark; `is-driven` mutes the part already covered), `om-map-pin` (`is-dimmed` at half strength) with `om-map-pin-body`, `-glass`, `-roof`, `-mirror`, `om-map-halo` (live vehicle only), `om-map-landmark`, `om-map-label` (`is-landmark`). Pin kinds: place (accent pin, bold label), landmark (ink-2 dot, smaller regular label), vehicle (a bus turned to its heading, or a round badge when the heading is unknown). Full screen: `om-map-full`, `om-map-full-bar`, `om-map-full-close`, `om-map-full-title`, `om-map-full-bottom`, `om-map-recentre` (appears after the camera is moved), `om-map-full-sheet`. The ground in HTML is a neutral stand-in, never real tiles. A driver's phone number never appears on the map.

Compose source: omega-kmp :ui-map, OmegaMap.kt, `OmegaMiniMap(pins, placeLabel, description, offline, offlineNote, expandLabel, onExpand, suspended, route, framePins)`, `OmegaFullScreenMap(visible, pins, title, placeLabel, description, offline, offlineNote, closeLabel, onClose, …)`, `OmegaMapPin(latitude, longitude, kind, dimmed, label, headingDeg)`, `OmegaMapPinKind`, `OmegaMapRoute(points, progress)`
