Use the shared sign-in flow as it is in every app: phone number, then a 6-digit WhatsApp code, then the profile chooser on the board; the layout is fixed and each app supplies only its wording.

```html
<main class="om-signin">
  <h1 class="om-signin-title">Sign in</h1>
  <p class="om-signin-body">We'll send a one-time code on WhatsApp. No password needed.</p>
  <p class="om-signin-field-label">Mobile number</p>
  <div class="om-signin-phone"><span class="om-signin-phone-prefix">+91</span><span class="om-signin-phone-value om-num">9876543210</span></div>
  <div class="om-signin-code"><span class="om-signin-code-cell is-filled">4</span><span class="om-signin-code-cell"></span></div>
</main>
<main class="om-signin-board">
  <p class="om-signin-eyebrow">Omega · +91 98••• ••210</p><h1 class="om-signin-title">Who's using Omega?</h1>
  <div class="om-signin-profiles"><div class="om-signin-profile" role="button"><span class="om-signin-profile-avatar"><span class="om-signin-profile-initials">RS</span></span><span class="om-signin-profile-name">Riya Sharma</span><span class="om-signin-profile-meta">Class 8-B</span><span class="om-signin-profile-last">Last used</span></div></div>
</main>
```

Classes: paper screens `om-signin` (`has-bar` when a top action row is present), `om-signin-title`, `-body`, `-field-label`, `om-signin-phone` (`is-error`; the message goes inside the field as `om-signin-phone-error`), `om-signin-notice` (danger; `is-warning`), `om-signin-code` (`is-error`) with six `om-signin-code-cell` (`is-filled`), `om-signin-resend-wait`. Board screens `om-signin-board` (`is-top` for the no-profiles screen), `om-signin-eyebrow`, `-reason`, `-strong`, `om-signin-profiles` (two-up; `is-compact` one-up on narrow or large-text screens), `om-signin-profile` (`is-loading` fades the avatar and adds `om-signin-profile-spinner`), `-profile-avatar` (72), `-profile-name`, `-profile-meta`, `-profile-last`, `om-signin-remember` (`is-checked`) with `om-signin-check`. Buttons are the shared action buttons: primary "Send code" and "Verify", text "Resend code" and "Use a different number", tertiary "Sign out" on the board.

Compose source: omega-kmp :signin, PhoneEntryScreen.kt `PhoneEntryScreen(state, wording, onPhoneChanged, onSubmit, actions)`, CodeEntryScreen.kt `CodeEntryScreen(state, wording, nowEpochMs, onCodeChanged, onSubmit, onResend, onChangeNumber, actions)`, ProfileChooserScreen.kt `ProfileChooserScreen`, `NoProfilesScreen(state, wording, onStartOver, actions)`, ProfileAvatar.kt `ProfileAvatar(profile, contentDescription, size, onClick, onClickLabel)`, SignInWording.kt, SignInFlow.kt
