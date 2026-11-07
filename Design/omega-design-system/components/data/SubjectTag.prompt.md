# SubjectTag

Use to name a subject: an 8 px dot in the subject's categorical colour and the name in subhead ink 2. Never a filled chip; the colour is a key and the name is the meaning.

```html
<span class="om-subject-tag om-subject-tag--3"><span class="om-subject-tag__dot"></span>Chemistry</span>
```

- `.om-subject-tag--1` to `--8`: the eight subject colours.
- Or set `--subject-color` directly.
- In Compose the colour is picked by hashing the subject's stable id, so one subject always gets the same colour; in static markup choose the index by hand and keep it stable.

Compose source: omega-kmp :ui, OmegaStatus.kt, SubjectTag(name, key); OmegaColor.kt, OmegaColors.subjectColor(key)
