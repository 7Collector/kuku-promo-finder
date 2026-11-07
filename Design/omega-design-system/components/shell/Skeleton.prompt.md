# Skeleton

A loading placeholder: a static sunken block the shape of what is coming. No shimmer and no pulse; motion answers touch. It is hidden from assistive technology, and the screen announces "Loading" once, not per block.

```html
<div class="om-skeleton"></div>
<div class="om-skeleton" style="width:70%"></div>
<div class="om-skeleton" style="--skeleton-height:56px"></div>
```

Variants: height through `--skeleton-height` (default 16 for a text line; about 56 for a row). Width is the caller's. Radius xs.

Compose source: omega-kmp :ui, OmegaStates.kt, `Skeleton(modifier, height)`
