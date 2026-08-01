---
tags: [template]
---
<%*
// weekly-review.md — Weekly review template.
// Generates a dated review note with Dataview task query.
const weekEnd   = tp.date.now("YYYY-MM-DD");
const weekStart = tp.date.now("YYYY-MM-DD", -7);
const isoWeek   = tp.date.now("[W]WW");
const year      = tp.date.now("YYYY");
const energy    = await tp.system.suggester(
  ["1 — Exhausted","2 — Low","3 — Okay","4 — Good","5 — Energised"],
  ["1","2","3","4","5"],
  false, "Average energy level this week (1–5)"
);
const focus     = await tp.system.suggester(
  ["1 — Scattered","2 — Distracted","3 — Moderate","4 — Focused","5 — Deep work"],
  ["1","2","3","4","5"],
  false, "Average focus level this week (1–5)"
);
const highlight = await tp.system.prompt("One-line highlight of the week");
await tp.file.rename(`weekly-review-${weekEnd}`);
-%>
---
tags: [weekly-review, <% year %>]
week: <% isoWeek %>
period_start: <% weekStart %>
period_end: <% weekEnd %>
energy: <% energy %>
focus: <% focus %>
created: <% weekEnd %>
---

# Weekly Review — <% isoWeek %> (<% weekStart %> → <% weekEnd %>)

> **Highlight:** <% highlight %>
> **Energy:** <% energy %>/5   |   **Focus:** <% focus %>/5

---

## Wins

<!-- What went well? Celebrate progress, no matter how small.
     Include shipped work, skills practised, habits maintained. -->

-
-
-

## Challenges

<!-- What was hard, blocked, or didn't go as planned?
     Be honest; this log is for you. -->

-
-

## Learnings

<!-- Key insights from this week — technical, personal, or process.
     Link to skill notes created or updated this week. -->

-
-
-

## Next Week Goals

<!-- 3–5 concrete, achievable goals. Use Tasks plugin syntax
     so they show up in dashboard queries. -->

- [ ] Goal 1 📅 <% tp.date.now("YYYY-MM-DD", 7) %>
- [ ] Goal 2 📅 <% tp.date.now("YYYY-MM-DD", 7) %>
- [ ] Goal 3 📅 <% tp.date.now("YYYY-MM-DD", 7) %>

---

## Tasks Completed This Week

<!-- Dataview query — shows tasks checked off between weekStart and weekEnd. -->

```dataview
TASK
FROM ""
WHERE completed = true
  AND completion >= date("<% weekStart %>")
  AND completion <= date("<% weekEnd %>")
SORT completion ASC
```

---

## Metrics Snapshot

<!-- Optional: fill in any numbers you track. -->

| Metric              | Value |
|---------------------|-------|
| Commits / PRs merged |      |
| New notes created   |       |
| Books / articles read |     |
| Workouts            |       |
| Deep-work hours     |       |

---

## Notes & Reflections

<!-- Free-form observations, mood log, or anything that doesn't
     fit the structured sections above. -->

---

## References & Links

- [[weekly-review-<% tp.date.now("YYYY-MM-DD", -7) %>]] — previous week
- [[weekly-review-<% tp.date.now("YYYY-MM-DD", 7) %>]] — next week (pre-created)
