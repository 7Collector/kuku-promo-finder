# CalendarMonth, CalendarDay and Legend

One month: a row of weekday headers, then weeks of day cells 4 apart, the last week left short. Each day's tone comes from the screen's own mapping (attendance to tone), and a tone never stands alone: the same meaning is in the cell's spoken name and in a legend.

```html
<div class="om-calendar-month">
  <div class="om-calendar-weekdays"><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span></div>
  <div class="om-calendar-days">
    <span></span><!-- one empty cell per day before the 1st -->
    <div class="om-calendar-day om-calendar-day--success" aria-label="Tuesday 1 September, present">1</div>
    <div class="om-calendar-day is-today" aria-label="Tuesday 22 September, today">22</div>
  </div>
</div>
<div class="om-legend">
  <span class="om-legend-item"><span class="om-legend-swatch om-legend-swatch--success"></span>Present</span>
</div>
```

Day states: unmarked (plain ink-3 number); `--info`, `--help`, `--tip`, `--success`, `--warning`, `--danger`, `--neutral` (tone container, on-container text); `.is-today` (1.5 ink ring); `.is-selected` (2 accent ring, drawn inside today's ring); `--tappable` (48 tall instead of 40); optional `.om-calendar-day-caption` under the number. Legend swatches take the same tone suffixes and wrap onto a second line.

Compose source: omega-kmp :ui, Calendar.kt, `CalendarMonth(year, month, weekdayHeaders, describeDate, today, firstDayOfWeek, tone, status, onDayClick)`, `CalendarDay(day, tone, isToday, contentDescription, onClick, caption, selected)`, `Legend(items)`
