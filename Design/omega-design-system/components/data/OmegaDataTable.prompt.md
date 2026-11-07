# OmegaDataTable

Use for a small table of text, at most six columns. Columns are as wide as their widest cell between 64 and 220 px; a long cell wraps, and a table wider than its slot scrolls sideways. Nothing is truncated or squeezed.

```html
<div class="om-data-table">
  <div class="om-data-table__frame"><div class="om-data-table__scroll"><table>
    <thead><tr><th scope="col">Subject</th><th scope="col">Unit test</th></tr></thead>
    <tbody><tr><td>Physics</td><td class="om-num">41/50</td></tr></tbody>
  </table></div></div>
  <p class="om-data-table__caption">Class 9A, term 1</p>
</div>
```

- Frame: surface, radius md, a 1 px hairline border. Header row on the sunken ground in body strong; cells in body.
- Rows are separated by 1 px hairlines; cells have 12 by 8 padding and are top-aligned.
- `.om-data-table__caption` (optional): caption in ink 2, 8 below the table.
- Every row has exactly as many cells as the header: pad a short row with empty cells.
- No row selection, sorting or pressed state in the source.

Compose source: omega-kmp :ui, OmegaDataTable.kt, OmegaDataTable(columns, rows, caption, cell), DataTableCellText(text, header), DataTableMetrics (MAX_COLUMNS = 6, min 64.dp, max 220.dp)
