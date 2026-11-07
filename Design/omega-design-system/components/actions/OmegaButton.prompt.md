Use a button for an action. One primary per screen or sheet, full width at the bottom; secondary for the alternative; tertiary and destructive are text-only and sit inline. A filled danger button exists only as the confirm of a destructive confirmation dialog.

```html
<button class="om-button om-button--primary om-button--full"><span class="om-button__label">Submit homework</span></button>
<button class="om-button om-button--secondary om-button--compact"><span class="om-button__label">Save draft</span></button>
<button class="om-button om-button--tertiary"><i class="om-icon om-icon-plus"></i><span class="om-button__label">Add task</span></button>
<button class="om-button om-button--primary om-button--full is-loading" aria-label="Submit homework, loading"><svg class="om-spinner" viewBox="0 0 18 18"><circle cx="9" cy="9" r="8"/></svg></button>
```

- Kind: `om-button--primary`, `--secondary`, `--tertiary`, `--destructive`, `--danger-fill` (dialog confirm only).
- Width: `--full` (fills the row, 16 px label) or `--compact` (hugs the label, 13 px label). Text-only kinds always use the 16 px label.
- On the board: add `om-button--on-board`. Label wrapping for a text-only action on its own line: `om-button--wrap`.
- States: `is-disabled` (or `disabled`), `is-loading` (the spinner replaces the label and icon), `is-pressed` (static mock of the press layer).
- 48 px minimum height, radius md, optional 18 px leading icon, 8 px gap. Disabled and loading filled buttons share the sunken look.

Compose source: omega-kmp :ui, OmegaButtons.kt, `OmegaButton(text, onClick, style, fillMaxWidth, enabled, isLoading, onStage, leadingIcon, maxLines, background, contentColor)`, `PrimaryButton`, `SecondaryButton`, `TertiaryButton`, `DestructiveButton`, `buttonVisuals`
