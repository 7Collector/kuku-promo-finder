# GroupedList

Use to hold a run of list rows on one surface: surface fill on paper, radius lg, no outline, rows separated by hairlines inset to the text keyline. Mark the last row so it draws no hairline.

```html
<div class="om-list-group">
  <div class="om-list-row">…</div>
  <div class="om-list-row om-list-row--last">…</div>
</div>
```

- `.om-list-group`: the shared surface (`GroupedList` and `OmegaListGroup` are the same thing).
- `.om-list-group-item`: one row's share of a group whose rows are separate lazy-list items.
- `.om-list-group-item--first`, `.om-list-group-item--last`: radius lg on the outer corners; square between, no gap.

Compose source: omega-kmp :ui, OmegaList.kt, GroupedList(content); OmegaSurface.kt, OmegaListGroup(content), OmegaListGroupItem(first, last)
