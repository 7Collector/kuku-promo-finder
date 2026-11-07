# Avatar

Use for a person: initials on the accent container. No ring; the avatar is identity, not status.

```html
<span class="om-avatar" aria-label="Aarav Kumar">AK</span>
<span class="om-avatar om-avatar--tappable" role="button" aria-label="Switch profile" style="--avatar-size:48px">AK</span>
```

- 40 px by default; set `--avatar-size` for another size.
- Initials in body strong, on-accent-container, one line.
- `.om-avatar--tappable`: the avatar is a button (the profile switcher); `:active` or `.is-pressed` gives the ink ripple.
- Leave out `aria-label` when the avatar is decorative and the row around it names the person.

Compose source: omega-kmp :ui, OmegaStatus.kt, Avatar(initials, contentDescription, size = 40.dp, onClick, onClickLabel)
