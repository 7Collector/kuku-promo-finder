# Omega driver app: screen kit

Static renderings of the driver app's screens, composed from the design system's `om-` components.
The Compose source is `omega-driver-app/shared/src/commonMain/kotlin/auroboris/omega/driver/`; copy is
the English of `ui/DriverLabels.kt` and `auth/ui/SignInLabels.kt`, verbatim. Sample data is the app's
own seeded day (`trip/data/FakeDriverRepository.kt`): Route 1 · Civil Lines, Bus 1, five stops, eight
children, a transport desk.

The driver shell has no tabs and no navigation graph: Today, the running trip and the summary are
three states of one scaffold. The only chrome is the scaffold's bar row (a back chevron on the trip
and the summary, the language switch on Today) and, on the running trip, a pinned action bar.

| Screen file | Compose source and composable | Design-system components |
| --- | --- | --- |
| `today.html` | `ui/DriverShell.kt` `DriverShell` (Today branch, `LanguageToggle`); `ui/TodayScreen.kt` `TodayScreen`, `TripCard`, `CallDeskCallout` | ScreenScaffold, ScreenHeader (large title, context), OmegaSurface, StatusBadge, OmegaButton (primary full width, tertiary), EmptyState, Callout (neutral, phone icon, action) |
| `today-states.html` | `ui/TodayScreen.kt` `TodayScreen` (saved copy), `TripCard` (Running, blocked start, Missed, Cancelled), `CallDeskButton` | ScreenScaffold, ScreenHeader, Callout (warning, neutral), OmegaSurface, StatusBadge (info, warning, neutral), OmegaButton (primary, tertiary with leading icon) |
| `active-trip.html` | `ui/ActiveTripScreen.kt` `ActiveTripScreen`, `SharingIndicator`, `ChildRow`, `RosterHeading`, `ActiveTripActions`; `ui/SendTrouble.kt` `SendTrouble`; `ui/DriverShell.kt` (pinned title header, `OmegaActionBar`) | ScreenScaffold, ScreenHeader (pinned title, back), Callout (success and warning, map-pin icon, title), OmegaSurface, SectionHeader, OmegaListGroupItem, OmegaListEntry, ListRow (selected), StatusBadge, OmegaButton (primary with leading icon, secondary, tertiary, destructive), OmegaActionBar |
| `active-trip-end.html` | `ui/ActiveTripScreen.kt` `ActiveTripActions` (last stop); `ui/DriverShell.kt` `confirmEnd` | as `active-trip.html`, plus OmegaConfirmDialog (destructive) over a scrim |
| `location-not-shared.html` | `ui/ActiveTripScreen.kt` `SharingIndicator` (`CaptureState.Stopped` with `PermissionMissing`; `Sharing` with `notificationHidden`) | as `active-trip.html`, with Callout (danger with title and action; warning with action) |
| `trip-summary.html` | `ui/TripSummaryScreen.kt` `TripSummaryScreen`; `ui/DriverShell.kt` (summary branch) | ScreenScaffold, ScreenHeader (large title, back), Callout (success, neutral, warning), FactsList, SectionHeader, OmegaButton (primary full width) |
| `confirm-dialogs.html` | `ui/DriverShell.kt` `confirmStart`, `confirmNotAtStop`, `confirmEndBeforeLeaving` | OmegaConfirmDialog (ordinary and destructive), scrim, over the Today and running-trip screens |
| `recovery-notice.html` | `auth/ui/SignedInShell.kt` `SignedInShell` (recovery notice) | OmegaDialog with a primary action, scrim, over Today |
| `launch.html` | `App.kt` `App` (`StoreLaunchState`); `omega-kmp` `ui/launch/StoreUnavailableScreen.kt` `StoreOpeningScreen`, `StoreUnavailableScreen` | ScreenScaffold, ErrorState (a danger Callout with title and retry), OmegaText |

Not rendered: the four signed-out screens are the shared `SignInFlow` (see the design system's sign-in
card); the `report` package (`DriverFaults.kt`) is fault reporting and draws nothing; the location
permission prompt is the operating system's own, so the app's part of it is the callout in
`location-not-shared.html`.

## App-private patterns in `driver.css`

- `dk-screen`: sets the scaffold's status-bar inset to 0, because the kit frame draws the status strip itself.
- `dk-stack`: a column with the surface gap (12) between items; the body of Today, the trip head and the summary.
- `dk-route-line`: the "Pickup · Bus 1 · Route 1 · Civil Lines" line in subhead ink 2.
- `dk-trip-card` and its `__meta`, `__when`, `__route`, `__detail`, `__spare`, `__blocked`: the lines of a trip card inside an `om-surface`.
- `dk-account`: Switch login and Sign out, 24 under the day.
- `dk-stop-head` and its `__progress`, `__name`, `__due`: the current stop, its name in display.
- `dk-sharing`: the sharing callout with the notifications callout 8 under it.
- `dk-roster-heading`: a section heading as a list item, 12 above and below.
- `dk-child__top`, `__name`, `__tags`, `__note`, `__actions`: a child's row inside an `om-list-row` entry.
- `dk-weight`: a button that takes the remaining width of its row (`Modifier.weight(1f)`).
- `dk-trip-list`, `dk-pinned-actions`: the 96 the trip list keeps clear, and the action bar pinned over it.
- `dk-centre`, `dk-centre--margin`, `dk-opening-text`: the two launch screens, one thing centred in the window.
