# AttachmentThumbnail

Use for a picture attached to a message or a submission. Loading and will-not-load are drawn differently on purpose: loading is a still picture glyph, never a spinner; a picture that has given up is the danger container with a warning glyph.

```html
<div class="om-attachment-thumb"><img src="…" alt="Photo of a homework page"></div>
<div class="om-attachment-thumb"><i class="om-icon om-icon-image"></i></div>
<div class="om-attachment-thumb om-attachment-thumb--error"><i class="om-icon om-icon-warning"></i></div>
```

- Loaded: the image fills the square, cropped; `.om-attachment-thumb--contain` fits it inside instead.
- Loading or decoding (no modifier, no image): sunken ground, 18 px image icon in ink 3.
- `.om-attachment-thumb--error`: danger container, 18 px warning icon in danger strong.
- The caller sets the size (`--thumb-size`) and the corner (`border-radius`; chat uses radius md). The component sets neither in Compose.

Compose source: omega-kmp :ui, AttachmentThumbnail.kt, AttachmentThumbnail(bytes: ByteArray?, contentDescription, isError = false, contentScale = ContentScale.Crop)
