---
tags: [template]
---
<%*
// adr-template.md — Architecture Decision Record template.
// Invoke via Templater to document a significant architectural choice.
const adrNumber = await tp.system.prompt("ADR Number (e.g. 0042)");
const title     = await tp.system.prompt("Decision title (e.g. Use PostgreSQL as primary store)");
const adrStatus = await tp.system.suggester(
  ["proposed","accepted","deprecated","superseded"],
  ["proposed","accepted","deprecated","superseded"],
  false, "ADR status"
);
const today     = tp.date.now("YYYY-MM-DD");
const filename  = `adr-${adrNumber.padStart(4,"0")}-${title.toLowerCase().replace(/\s+/g,"-").replace(/[^a-z0-9-]/g,"")}`;
await tp.file.rename(filename);
-%>
---
tags: [adr, architecture]
adr_number: <% adrNumber %>
status: <% adrStatus %>
created: <% today %>
updated: <% today %>
---

# ADR-<% adrNumber %>: <% title %>

**Date:** <% today %>
**Status:** <% adrStatus %>

---

## Context

<!-- Describe the situation, forces, and constraints that make this
     decision necessary. Include relevant technical and business
     factors. Be factual; avoid advocating for any option here. -->

### Problem Statement

### Forces & Constraints

- Technical constraint:
- Business constraint:
- Time constraint:

### Options Considered

| Option | Summary | Pros | Cons |
|--------|---------|------|------|
| A      |         |      |      |
| B      |         |      |      |
| C (chosen) |    |      |      |

---

## Decision

<!-- State the decision clearly in a single sentence or short
     paragraph. Explain *why* this option was chosen over others. -->

**We will** [decision statement].

**Rationale:**

- Reason 1
- Reason 2
- Reason 3

---

## Consequences

### Positive

<!-- Benefits that result directly from this decision. -->

-
-

### Negative

<!-- Trade-offs, technical debt, or risks introduced. -->

-
-

### Neutral

<!-- Changes that are neither clearly good nor bad, but notable. -->

-
-

---

## Implementation Notes

<!-- Optional: concrete steps, migration plan, or code pointers
     needed to act on this decision. -->

- [ ] Step 1
- [ ] Step 2

---

## Related Decisions

<!-- Link to ADRs that this decision builds on, contradicts,
     or is later superseded by. -->

- [[adr-]] — context / superseded by / related to
- [[adr-]] —

## References

<!-- External docs, RFCs, blog posts that informed this decision. -->

-
-
