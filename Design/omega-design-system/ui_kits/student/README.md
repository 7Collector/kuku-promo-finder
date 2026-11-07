# Student app kit

Static renders of the student surface of `omega-school-app`. Each file is one screen in a 360 x 780 phone, built from
the design system's `om-` classes plus the app-private `sk-` patterns in `student.css`. Compose sources live in
`omega-school-app/shared/src/commonMain/kotlin/auroboris/omega/school/student/ui/`.

One student throughout: Aanya Sharma, Class 8B, Greenfield Public School, on Tuesday 13 October 2026. Subjects and
teachers: Mathematics (Mrs Kulkarni), Science (Mr Iyer), English (Ms D'Souza), Hindi (Mrs Tiwari), Social science (Mr Rao).

## Screens

| Screen file | Compose source and composable | Design-system components |
| --- | --- | --- |
| `home.html` | `HomeScreen.kt` `HomeScreen` (header, `HighlightRow`, `InvitationRow`), `HomeHero.kt` | adaptive shell, bottom nav, board hero, progress, section header, list group, card deck, status badge, tile grid, module tile, avatar, button |
| `routine.html` | `RoutineScreen.kt` `RoutineScreen` | adaptive shell, bottom nav, screen header, day strip, timeline row, tertiary button |
| `syllabus.html` | `SyllabusScreen.kt` `SyllabusScreen` (`OverallCard`, `SubjectRow`); second phone `TopicOverviewSheet.kt` `TopicOverviewSheet` | adaptive shell, bottom nav, card, donut, gradient sparkle, progress, list group, button; scrim, bottom sheet, chip |
| `syllabus-subject.html` | `SyllabusScreen.kt` `SyllabusSubjectScreen` (`FlashcardsCallout`) | screen bar and header, card, gradient sparkle, button, section header, chapter card, subtopic row, status ring, progress |
| `homework.html` | `HomeworkScreen.kt` `HomeworkScreen` | screen bar and header, segmented control, section header, list group, subject tag |
| `assignments.html` | `AssignmentsScreen.kt` `AssignmentsScreen`; second phone `AssignmentDetailScreen` (`SubmitPanel`) | screen bar and header, section header, list group, list row, subject tag, board card (glow), facts, card, button |
| `quizzes.html` | `QuizzesScreen.kt` `QuizzesScreen` (`QuizPracticeNotice`, `QuizRow`) | screen bar and header, callout, list group, subject tag, status badge |
| `results.html` | `ResultsScreen.kt` `ResultsScreen` | screen bar and header, chips, board card, score, callout, section header, list group, donut, button |
| `subject-result.html` | `SubjectResultScreen.kt` `SubjectResultScreen` | screen bar and header, board card (glow), score, section header, list group |
| `attendance.html` | `AttendanceScreen.kt` `AttendanceScreen` | screen bar and header, card, donut, section header, calendar month, legend, callout, list group, status badge |
| `bus.html` | `BusScreen.kt` `BusScreen` | screen bar and header, card, status badge, list group, list row, section header |
| `notices.html` | `NoticesScreen.kt` `NoticesScreen` | screen bar and header, section header, card deck, list group, list row |
| `events.html` | `EventsScreen.kt` `EventsScreen`; second phone `EventDetailScreen` | screen bar and header, list group, status badge, card, facts, section header, segmented control (toned) |
| `forms.html` | `FormsScreen.kt` `FormsScreen` (`FormRow`); second phone `FormDetailScreen` (`FormProgress`, `FormQuestion`) | screen bar and header, list group, status badge, progress, choice list, text area, button |
| `material.html` | `MaterialScreen.kt` `MaterialScreen` | screen bar and header, subject tag, button, chips, section header, card, progress, list group, list row, status badge |
| `ai-home.html` | `AiHomeScreen.kt` `AiHomeScreen`, `AskAnythingExpand.kt` `AskAnythingBar` | adaptive shell, bottom nav (AI tab selected), screen header, list group, list row, section header, gradient sparkle |
| `ai-chat.html` | `AiChatScreen.kt` `AiConversationScreen` (`MessageTurnBody`, `ConversationComposer`, `ComposerBar`), `StructuredReply.kt` `StructuredReply` / `StepCarousel`, `ChatVisualBlocks.kt` `TableBlock`, `RichMessageText.kt` | screen bar with subtitle, progress dots, formula plate, button, data table, composer, send button |
| `profile.html` | `StudentProfileScreen.kt` `StudentProfileScreen` | screen bar and header, avatar, button, card, facts, list group, list row |

Tab roots (`home`, `routine`, `ai-home`, `syllabus`) carry the bottom navigation from `StudentTabs.kt`: Home, Routine,
AI, Syllabus. Every other screen opens over the shell with the bar hidden and a back chevron.

## `sk-` patterns (`student.css`)

- `sk-gap-*`, `sk-stack`, `sk-row`, `sk-grow`, `sk-bleed`: the app's explicit spacers and simple rows; `sk-bleed` lets a day strip or chip row run to the screen edges.
- `sk-ink*`, `sk-accent-text`, `sk-tone-*`, `sk-on-board*`, `sk-icon-*`, `sk-p`: ink, tone and icon size for one line of text.
- `sk-home-header`, `sk-icon-button`, `sk-avatar-button`: Home's greeting header with the inbox bell and profile avatar.
- `sk-highlight`, `sk-invite-actions`: a "Needs you" row and an invitation's two answers.
- `sk-subject-line`: subject tag, middle dot, then teacher or a toned status.
- `sk-homework-row`, `sk-tick` (`--done`), `sk-struck`, `sk-attachment-chip(s)`, `sk-footnote`: homework's private tick, attachment chips and the footnote.
- `sk-board-facts`, `sk-board-fact`: label and value rows under the score on the results board.
- `sk-trailing-figure`, `sk-trailing-icon`: a row's trailing percent with its change, or an accent action glyph.
- `sk-summary`, `sk-tally`: a donut beside its headline; attendance's toned tally dots.
- `sk-date-leaf`, `sk-event-row`: the date leaf at the head of an event row.
- `sk-plate`: the 40 px sunken plate behind a material kind or AI mode icon.
- `sk-thin-progress`, `sk-suggestion`: the syllabus subject row's 4 px bar and the suggestion card line.
- `sk-ask-bar-slot`, `sk-ask-bar`, `sk-balance`: the "Ask anything" bar above the bottom navigation and the credit balance.
- `sk-chat`, `sk-transcript`, `sk-user-turn`, `sk-user-bubble`, `sk-reply`, `sk-prose`, `sk-chat-block`, `sk-step-*`, `sk-chat-composer`: the conversation: user bubble, reply parts, the step carousel frame and the composer strip.
- `sk-sheet-stack`, `sk-saved-line`, `sk-button-row`, `sk-profile-head`: sheet body spacing, the "Saved" line, paired buttons and the profile heading.
