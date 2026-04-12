---
tags: [template]
---
<%*
// skill-template.md — Invoke via Templater to scaffold a new skill note.
// Prompts will appear as modal dialogs inside Obsidian.
const category   = await tp.system.prompt("Category (e.g. backend, frontend, devops, data)");
const technology = await tp.system.prompt("Technology / skill name (e.g. FastAPI, Docker)");
const level      = await tp.system.suggester(["beginner","intermediate","advanced"], ["beginner","intermediate","advanced"], false, "Proficiency level");
const aliases    = await tp.system.prompt("Aliases (comma-separated, e.g. fast-api, ASGI framework)");
const today      = tp.date.now("YYYY-MM-DD");
await tp.file.rename(technology.toLowerCase().replace(/\s+/g, "-"));
-%>
---
tags: [skill, <% category %>, <% technology %>]
status: draft
level: <% level %>
updated: <% today %>
aliases: [<% aliases %>]
created: <% today %>
---

# <% technology %>

> One-sentence summary of what this technology is and why it matters.

## Overview

<!-- Describe the technology: purpose, origin, key selling points.
     Answer: What problem does it solve? Who uses it and why? -->

## Core Concepts

<!-- List the 3–7 foundational ideas a practitioner must understand.
     Use sub-headings or bullet points. Link to related skill notes. -->

### Concept 1

### Concept 2

### Concept 3

## Patterns & Best Practices

<!-- Document proven patterns, idioms, or architectural conventions.
     Include when to use each pattern and any trade-offs. -->

- **Pattern A** — explanation
- **Pattern B** — explanation

## Common Gotchas

<!-- Capture surprising behaviours, version-specific quirks, or
     mistakes you have actually made. Saves future-you debug time. -->

- Gotcha 1: description
- Gotcha 2: description

## Code Snippets

<!-- Paste minimal, runnable examples. Use fenced code blocks with
     the appropriate language tag (python, ts, bash, yaml, etc.). -->

```language
# Minimal working example
```

```language
# Another useful snippet
```

## References

<!-- Official docs, RFCs, authoritative blog posts, course links. -->

- [Official Documentation]()
- [Source Repository]()

## Related

<!-- Wiki-link to notes that complement or extend this skill. -->

- [[]]
- [[]]
