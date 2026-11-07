# Teacher app kit

Static renders of the teacher surface of the Omega school app. Each file is one screen in one state, built from the
Compose source in `omega-school-app/shared/src/commonMain/kotlin/auroboris/omega/school/teacher/ui/`. Layout, order, copy
and tones come from that source; names and figures are sample data.

The teacher is Meera Nair, Mathematics, class teacher of 8B (38 on roll), also teaching 9A and 10C at Roorkee Public
School. The day is Tuesday 13 October 2026.

## Screens

| Screen file | Compose source file and composable | DS components used |
| --- | --- | --- |
| `home.html` | `TeacherHomeScreen.kt` · `TeacherHomeScreen` | adaptive shell, bottom nav (pill tabs), board hero, live dot, progress on board, button on board, on-stage glass, avatar, section header, card deck, module tile grid, status badge, AI card, timeline row |
| `classes.html` | `TeacherClassesScreen.kt` · `TeacherClassesScreen` | adaptive shell, bottom nav, screen header, section header, list group, list chevron |
| `class-detail.html` | `TeacherClassDetailScreen.kt` · `TeacherClassDetailScreen` | adaptive shell, bottom nav, section header, module tile grid, status badge, list group, list row, avatar, tertiary button |
| `attendance-register.html` | `AttendanceRegisterScreen.kt` · `AttendanceRegisterScreen` (cards view), `RegisterHeader` | status badge, section header |
| `attendance-register-list.html` | `AttendanceRegisterScreen.kt` · `AttendanceRegisterScreen` (list view), `RegisterHeader`, `RegisterFooter` | status badge, primary and secondary button |
| `attendance-calendar.html` | `TeacherAttendanceCalendarScreen.kt` · `TeacherClassAttendanceScreen` | screen bar, back button, screen header, card, calendar month, legend, section header, list group, list row, status badge |
| `homework-compose.html` | `HomeworkComposeScreen.kt` · `HomeworkComposeScreen` | screen bar, screen header, section header, field, area field, chip, date field, tertiary button, callout (help), action bar, primary button |
| `assignments.html` | `TeacherAssignmentsScreen.kt` · `TeacherAssignmentsScreen` | screen bar, screen header, list group, status badge, progress, secondary button, callout (help), action bar, primary button |
| `grade.html` | `TeacherGradeScreen.kt` · `TeacherGradeScreen` | screen bar, screen header, progress, list group, field (accent, centred), status badge, callout (help), action bar, primary button |
| `syllabus-coverage.html` | `SyllabusCoverageScreen.kt` · `SyllabusCoverageScreen` | screen bar, screen header, progress, date field, list group, status ring, status badge, primary, secondary, tertiary and destructive button, action bar with info slot |
| `quiz.html` | `TeacherQuizScreen.kt` · `QuizLibraryScreen` (left), `TeacherQuizScreen` (right) | screen bar, screen header, primary button, list group, list row, status badge, field, AI card, tertiary and destructive button, action bar |
| `student-profile.html` | `TeacherStudentProfileScreen.kt` · `TeacherStudentProfileScreen` | screen bar, screen header, avatar, secondary button, AI card, list group, list row with value, section header, card, calendar month |
| `leave-review.html` | `TeacherLeaveReviewScreen.kt` · `TeacherLeaveReviewScreen` | screen bar, screen header, card, avatar, status badge, area field, primary and secondary button, callout (help) |
| `assistant-home.html` | `TeacherAssistantHomeScreen.kt` · `TeacherAssistantHomeScreen` (left); `TeacherPlanScreen.kt` · `TeacherPlanScreen` with `TeacherAiDraftCards.kt` · `LessonPlanCards`, `BulletCard`, `SequenceCard` (right) | adaptive shell, bottom nav, screen header, gradient sparkle, list group, list row, section header, sparkline, field, AI card, action bar, primary and secondary button |
| `school-figures.html` | `TeacherSchoolFiguresScreen.kt` · `TeacherSchoolFiguresScreen` (top of the screen, then scrolled to the review list) | screen bar, screen header, callout (info), section header, card, secondary, primary and destructive button, field |
| `class-overview.html` | `TeacherClassOverviewScreen.kt` · `TeacherClassOverviewScreen` | screen bar, screen header, chip, section header, card, chart (bar, line), list group, list row with value |

## App-private patterns (`teacher.css`)

Everything here is built from token variables. A few component dimensions the tokens do not carry (tile sizes, the
register card's avatar, the figure height) are literal pixel values copied from the Compose source.

Layout helpers

- `tk-gap-2` … `tk-gap-32`: fixed vertical spacers, one per `Spacer` height used in the source.
- `tk-row` (`--top`, `--12`, `--4`), `tk-wrap` (`--4`), `tk-stack` (`--2`, `--4`, `--8`, `--12`, `--section`), `tk-pair`, `tk-grow`, `tk-natural`: row, wrapping row, column, two equal halves, weighted child, natural-width child.
- `tk-ink`, `tk-ink-2`, `tk-ink-3`, `tk-accent-text`, `tk-danger-text`: text colour roles.
- `tk-field-label`: the label above a chip group or bare date field.
- `tk-icon-line` (`--success`, `--strong`): small icon followed by a line of text.
- `tk-icon-button`: a 48 px icon-only touch target (refresh, month arrows, row overflow).
- `tk-entry` (`--roomy`, `--ring`): a padded entry inside a list group that is not a plain list row.
- `tk-text-actions` (`--inset`): a row of text buttons pulled back to the text edge.
- `tk-board-top`: marker on a screen whose top is a dark board, so the kit's status strip takes the board colour.

Today

- `tk-home-header` (`__text`, `__greeting`, `__roles`, `__aside`): school, date, greeting and role lines beside the avatar and refresh.
- `tk-hero-actions`, `tk-hero-square`: the hero's action row and its square glass button.
- `tk-queue-chevron`: trailing chevron of the "Not yet sent" banner (state not drawn in this kit).

Classes

- `tk-class-row` (`__text`): three-line class row with a trailing chevron.
- `tk-class-board` (`__top`, `__back`, `__role`, `__title`, `__rest`, `__subtitle`, `__stats`, `__stat`, `__value`, `__label`): the class detail's dark header with back, role, title and three figures.

Attendance register

- `tk-register`, `tk-register-body`, `tk-register-footer`: the full-screen register frame.
- `tk-register-band` (`__row`, `__titles`, `__title`, `__count`), `tk-register-close` (`__disc`), `tk-view-toggle` (`__option`, `is-selected`), `tk-register-rail` (`__fill`): the dark band with close, title, count, Cards/List toggle and progress rail.
- `tk-deck`, `tk-deck__peek`, `tk-student-card` (`__top`, `__roll`, `__status`, `__centre`, `__avatar`, `__name`, `__position`): the swipe deck and its student card.
- `tk-roll-strip`, `tk-roll-tile` (`--unmarked`, `--success`, `--warning`, `--danger`, `--info`, `--neutral`, `is-current`; `__box`, `__caption`): the roll-number strip under the deck.
- `tk-register-controls`, `tk-outline-button` (`--square`, `--step`, `--mark`), `tk-mark-grid`: undo, mark-everyone, previous/next and the four mark buttons.
- `tk-roster`, `tk-roster-row` (`__tile`, `__tile--unmarked`, `__text`, `__name`), `tk-sync-line` (`--blocked`): the list view's rows and their save-state line.

Attendance calendar

- `tk-month-nav` (`__title`): month title between two arrows.

Marks

- `tk-step` (`--lead`), `tk-score-field`: the minus and plus steppers around the score field.
- `tk-file-chip`: an attached file's name with its icon.
- `tk-button-saved`: the success-coloured "Saved" state of the save button (state not drawn in this kit).

Syllabus

- `tk-topic` (`__ring`, `__body`, `__actions`): a topic with its status ring, text and state buttons.

Quiz

- `tk-quiz-option` (`is-correct`, `__mark`): an answer option, the correct one checked and bold.
- `tk-drafted`: the "Drafted" tag on an AI-drafted question (defined; `quiz.html` currently composes the tag from `tk-row` instead).

Assistant

- `tk-tool-tile`: the 40 px sunken icon tile leading each assistant tool row.
- `tk-bullet`, `tk-plan-step`: bullet line and lesson-sequence step inside an AI card.

School figures

- `tk-figure-image` (`tk-figure-stroke`, `tk-figure-label`): the sunken frame holding a cut-out figure; the drawing inside is a placeholder.
