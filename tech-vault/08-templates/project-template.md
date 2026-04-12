---
tags: [template]
---
<%*
// project-template.md — Invoke via Templater to scaffold a new project note.
const projectName = await tp.system.prompt("Project name (e.g. API Gateway v2)");
const status      = await tp.system.suggester(
  ["planning","in-progress","on-hold","done","cancelled"],
  ["planning","in-progress","on-hold","done","cancelled"],
  false, "Project status"
);
const owner       = await tp.system.prompt("Owner / team (e.g. @erick, platform-team)");
const repoUrl     = await tp.system.prompt("Repository URL (leave blank if none)", "");
const today       = tp.date.now("YYYY-MM-DD");
await tp.file.rename(projectName.toLowerCase().replace(/\s+/g, "-"));
-%>
---
tags: [project, <% status %>]
status: <% status %>
owner: <% owner %>
created: <% today %>
updated: <% today %>
repo: "<% repoUrl %>"
---

# <% projectName %>

> One-sentence description of the project and its business value.

## Objective

<!-- What does this project achieve?
     Include measurable success criteria where possible. -->

- **Goal:**
- **Success criteria:**
- **Out of scope:**

## Stack

<!-- List every major technology used. Link to skill notes. -->

| Layer        | Technology      | Notes                         |
|--------------|-----------------|-------------------------------|
| Frontend     |                 |                               |
| Backend      |                 |                               |
| Database     |                 |                               |
| Auth         |                 |                               |
| Infra / CI   |                 |                               |
| Monitoring   |                 |                               |

## Architecture

<!-- High-level description of the system design.
     Embed a canvas link or ASCII diagram if useful. -->

```
[Client] → [API Gateway] → [Service A]
                        ↘ [Service B] → [Database]
```

<!-- Link to relevant ADRs for major architectural decisions. -->

- Decision: [[adr-]]
- Canvas: [[tech-stack-overview]]

## Tasks

<!-- Use Obsidian Tasks plugin syntax. Add due dates with 📅 YYYY-MM-DD. -->

### Backlog

- [ ] Define API contracts
- [ ] Set up CI pipeline
- [ ] Write integration tests

### In Progress

- [ ]

### Done

- [x] Project kickoff meeting

## Timeline

<!-- Key milestones. Use ISO dates for sorting. -->

| Milestone          | Target Date | Status  |
|--------------------|-------------|---------|
| Kickoff            | <% today %> | done    |
| MVP                |             | pending |
| Production launch  |             | pending |

## Notes

<!-- Running log of decisions, blockers, and context that does not
     belong in a formal ADR but should be preserved. -->

### <% today %>

-

## References

<!-- Design docs, Notion pages, Jira board, Figma links, etc. -->

- [Repo](<% repoUrl %>)
- [Design Doc]()
- [Ticket Board]()

## Related

- [[]]
- [[]]
