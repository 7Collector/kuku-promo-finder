Use the spinner for a short wait in place, such as a submit in flight inside a button. Do not use it for AI replies or content that can be drawn as a skeleton.

```html
<svg class="om-spinner" viewBox="0 0 18 18" role="img" aria-label="Loading"><circle cx="9" cy="9" r="8"/></svg>
```

- 18 px with a 2 px stroke, accent mark by default.
- `om-spinner--danger`: danger tint. Any other tint: set `color` on it or its parent.
- Inside `om-button.is-loading` it takes the button's content colour; mark it `aria-hidden="true"` there, because the button already says "loading".

Compose source: omega-kmp :ui, OmegaSpinner.kt, `OmegaSpinner(contentDescription, tint, size, strokeWidth)`, `OmegaSpinnerSize.inline`
