# Progress / Run Tracker (template)

This file is the TEMPLATE. Do not record a real run here.

For every run:

1. Create `progress/run/<short-name>-<YYYY-MM-DD>(run)/PROGRESS.md` and copy everything below the line into it.
2. Fill it in at the start of the run, update it as work lands (not only at the end), and set **State** to `COMPLETE` only when the completion criteria are checked.
3. Leave this root file unchanged.

Existing runs: see `progress/run/`.

---

## Run identity

- **Title:** `<what this run is>`
- **Run folder:** `progress/run/<short-name>-<YYYY-MM-DD>(run)/`
- **Started:** `<date time>`
- **Last updated:** `<date time>`
- **Owner/agent:** `<who>`
- **Requested outcome:** `<what the user asked for, in their terms>`
- **Scope:** `<files / areas in scope>`
- **Out of scope:** `<what this run will not touch>`

## Status

**State:** `NOT STARTED | IN PROGRESS | BLOCKED | COMPLETE`

**Current sentence:** `<one sentence on where the run stands right now>`

**Completion criteria:**

- [ ] `<criterion 1, checkable>`
- [ ] `<criterion 2, checkable>`

## Cold-session starter

### Read first

1. `<file>` — `<why>`
2. `<file>` — `<why>`

### Repository state at handoff

- **Working directory:** `<path>`
- **Branch/commit:** `<branch, commit>`
- **Known dirty files:** `<list or none>`
- **Commands/processes still running:** `<list or none>`
- **External dependencies:** `<runtimes, keys, services>`

### Verification record

- **Commands run:**
  - `<command>` → `<result>`
- **Screenshots/artifacts:**
  - `<path>` — `<what it shows>`

## Final handoff

### What is done

- `<item>`

### What is not done

- `<item, or none>`

### Risks and caveats

- `<item>`

### Handoff sentence

`<one sentence a cold session can act on>`
