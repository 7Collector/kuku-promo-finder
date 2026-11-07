# Parent app kit

Static renders of the Omega parent app's Compose screens, one screen per file, in a 360 x 780 phone. Source
files are under `omega-parent-app/shared/src/commonMain/kotlin/auroboris/omega/parent/ui/` unless a path says
otherwise. Wording comes from `ParentLabels.kt`; sample data follows the app's own fixture world (one parent,
Priya Sharma; children Aarav, Class 8-B, and Anaya, Class 5-A; Springdale Public School; bus B1 to Temple
corner) with dates moved to Tuesday 13 October 2026.

The app has four tabs: Today, Learning, Updates, Me. Learning and Updates pin a title, the child chip and a
chip row; the chosen chip decides the body. Everything else is pushed with a back chevron and no bottom plate.

| Screen file | Compose source and composable | Design-system components used |
| --- | --- | --- |
| `today.html` | `TodayScreen.kt` `TodayScreen`; `HomeHero.kt` `GreetingBoard`; `TodayBus.kt` `BusTodayCard`; `ChildChip.kt` `ChildChip` | adaptive shell, bottom nav with count badge, screen scaffold (tab root), section header, stacked card deck, status pill, mini map, list group and list row, board card with the next-lecture hero, timeline row, status badge, tertiary button, AI card |
| `bus.html` | `BusScreen.kt` `BusScreen`; `TodayBus.kt` `BusTodayCard`, `BusMapSheet`; `ContactSchoolScreen.kt` `ContactRow` | screen scaffold with back, screen header, status pill, mini map, full-screen map with bar, recentre pill and sheet, section header, list row, primary and secondary buttons |
| `bus-week.html` | `BusWeek.kt` `BusWeekSection`, `StopChangeSection`; `BusScreen.kt` boarding block | screen bar collapsed, section header, list group, toggle chip, status badge, secondary button (full and compact), callout (help) |
| `homework.html` | `HomeworkScreen.kt` `HomeworkScreen`; `TabHeaders.kt` `TabHeader`, `LearningSegments` | pinned header, choice chips, section header, list group, subject tag, bottom nav |
| `assignments.html` | `AssignmentsScreen.kt` `AssignmentsScreen` | pinned header, choice chips, section header, list group, subject tag |
| `results.html` | `ResultsScreen.kt` `ResultsScreen` | choice chips, board card with score display and progress bar, callout (help), section header, list group, donut, secondary button |
| `subject-result.html` | `SubjectResultScreen.kt` `SubjectResultScreen` | screen header, board card with score display, section header, list group |
| `attendance.html` | `AttendanceScreen.kt` `AttendanceScreen` | card, donut, section header, calendar month, legend, callout (help), list group, status badge |
| `syllabus.html` | `SyllabusScreen.kt` `SyllabusScreen` | board card with score display, section header, list row, donut |
| `syllabus-subject.html` | `SyllabusScreen.kt` `SyllabusSubjectScreen` | screen header, board card, section header, list row, chapter card, progress bar, subtopic row with status ring |
| `week.html` | `WeekScreen.kt` `WeekScreen` | day strip, timeline row |
| `work-detail.html` | `WorkDetailScreen.kt` `HomeworkDetailScreen`, `AssignmentDetailScreen`; `ItemAttachments.kt` `ItemAttachmentsBlock` | screen header, subject tag, section header, list row with leading icon |
| `updates.html` | `UpdatesFeedScreen.kt` `UpdatesFeedScreen`; `TabHeaders.kt` `UpdatesFilters`; rows from `InboxScreen.kt`, `EventsScreen.kt` `EventRow`, `FormsScreen.kt` `FormRow` | pinned header, choice chips, list group, list row with leading icon, status badge |
| `notices.html` | `NoticesScreen.kt` `NoticesScreen` | section header, stacked card deck (two cards, full body, action line), list row, status badge with icon |
| `events.html` | `EventsScreen.kt` `EventsScreen`, `EventRow` | list group, status badge |
| `event-detail.html` | `EventsScreen.kt` `EventDetailScreen` | screen header, surface, facts list, section header, segmented control |
| `forms.html` | `FormsScreen.kt` `FormsScreen`, `FormRow` | list group, status badge |
| `me.html` | `MeScreen.kt` `MeScreen`; `ChildChip.kt` `ChildChip`, `InitialsDisc` | bottom nav, section header, list row (selected, leading icon, chevron), secondary and destructive buttons, status badge |
| `fees.html` | `FeesScreen.kt` `FeesScreen` | screen header, card, facts list, primary and secondary buttons, section header, list row with value |
| `leave.html` | `LeaveScreen.kt` `LeaveScreen`, `LeaveForm`; `NativeDatePicker.kt` `NativeDateField` | callout (success), primary button, card, choice chips, picker field, text area, section header, list group, status badge |
| `sota-plan.html` | `SotaPlanScreen.kt` `SotaPlanScreen`, `SotaBuyBar`; `../labs/LabLaunchCard.kt` `LabLaunchCard` | screen bar collapsed, action bar, primary button, surface, facts list, AI card, status badge, card, toggle chip |
| `contact-school.html` | `ContactSchoolScreen.kt` `ContactSchoolScreen`, `ContactRow` | screen header, section header, list row with leading icon |
| `support.html` | `SupportScreen.kt` `SupportScreen` | text field, primary and secondary buttons, card, section header, list group, status badge |

Not a file of its own: `InboxScreen` is reached only as the rows of the Updates feed, so it is in
`updates.html`. `FormDetailScreen` is not rendered.

Screens taller than the phone are cut at the bottom as they would be on a device. Where a second phone shows
the same screen scrolled, the rest of the content is still in the markup below the visible part (the SOTA card
on Today, language and sign out on Me).

## Parent-only patterns (`parent.css`)

- `pk-app`: put on the shell so the screen bar does not reserve the status strip the kit phone already draws.
- `pk-child-chip`, `pk-initials`: the child chip with its tinted initials disc; the disc alone at 40 in a list
  row and 56 on Me.
- `pk-greeting`: Today's date line and greeting above the child chip.
- `pk-tab-header`: the pinned header of Learning and Updates, title and chip on one row with the chip row under it.
- `pk-bleed`: lets a scrolling chip row or day strip run to the screen edges.
- `pk-bus-card`: the bus status row and the mini map on one surface.
- `pk-entry-row`, `pk-entry-col`, `pk-trailing`, `pk-inline`: layout inside a list entry that carries custom
  content (text column, trailing figure or control, a line with a badge at its end).
- `pk-link-row`: the accent "View all" line that closes a list group.
- `pk-summary`, `pk-tally`: the attendance ring beside its verdict, and the tally with tone dots.
- `pk-board-facts`: label and figure rows on the results board.
- `pk-figure`: the balance figure on the fees card.
- `pk-date-leaf`: the day-over-month tile on an event row.
- `pk-form`, `pk-field-pair`: the leave form's spacing and its two date fields side by side.
- `pk-identity`: the signed-in parent on Me.
- `pk-benefits`, `pk-lab-card`, `pk-disclosure`, `pk-buy-bar`: SOTA's benefit list, the Lab launch card with
  its play pill, the Details disclosure row, and the reassurance line under the buy bar.
- `pk-map-full`, `pk-map-sheet__head`: sizes the full-screen map to the phone and lays out the sheet's heading.
- `pk-sp-*`, `pk-ink*`, `pk-accent`, `pk-danger`, `pk-warning`, `pk-info`, `pk-head`: spacer heights and ink
  steps for loose text lines, standing in for Compose spacers and colour arguments.
