# DayStrip

A horizontally scrolling row of days for moving between them, such as a timetable's week. Each cell is a tab, 48 by 64, with the weekday over the date; the cell's spoken name is the whole day in words. The row carries the page margin as content padding and keeps the selected day in view.

```html
<div class="om-day-strip" role="tablist">
  <div class="om-day-strip-day is-today" role="tab" aria-label="Tuesday 22 September">
    <span class="om-day-strip-weekday">Tue</span><span class="om-day-strip-date">22</span><span class="om-day-strip-dot"></span>
  </div>
  <div class="om-day-strip-day is-selected is-marked" role="tab" aria-selected="true" aria-label="Wednesday 23 September, 6 periods">
    <span class="om-day-strip-weekday">Wed</span><span class="om-day-strip-date">23</span><span class="om-day-strip-dot"></span>
  </div>
</div>
```

States: `.is-selected` (ink fill, paper text); `.is-today` (1 px outline ring, only while not selected); `.is-marked` (a 4 px dot under the date, ink-3 or paper when selected; use it only when the spoken name states the same fact). Cells are 8 apart; always include the dot element so every cell is the same height.

Compose source: omega-kmp :ui, DayStrip.kt, `DayStrip(days, selectedIndex, onSelect)`, `DayStripDay(weekday, date, description, isToday, marked)`
