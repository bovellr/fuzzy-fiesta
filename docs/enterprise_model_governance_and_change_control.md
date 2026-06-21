# Enterprise Governance and Change Control Guide for `sm_finance_core`

## 1. Document purpose

This document defines the recommended enterprise governance and change-control approach for the `sm_finance_core` Power BI semantic model. It is intended for finance business owners, BI developers, data engineers, data stewards, platform administrators, and release approvers.

The guidance applies to:

- semantic-model TMDL changes;
- DAX measures and calculation groups;
- relationships, roles, perspectives, hierarchies, and metadata;
- PBIP source-control workflow;
- security and row-level security (RLS);
- validation, testing, approval, deployment, and support.

## 2. Governance objectives

The governance framework should ensure that the model is:

1. **Trusted**: certified definitions, controlled changes, and traceable approvals.
2. **Secure**: role-based access and RLS are tested and monitored.
3. **Performant**: DAX and model design are optimized before production release.
4. **Maintainable**: measures, calculation groups, metadata, and documentation follow standards.
5. **Auditable**: all semantic changes have version history, business sign-off, and test evidence.
6. **Reusable**: base measures and calculation groups support governed self-service reporting.
7. **Recoverable**: changes can be rolled back quickly if results, performance, or security are affected.

## 3. Governance roles and responsibilities

| Role | Responsibilities | Required approval areas |
|---|---|---|
| Finance Business Owner | Owns business definitions, sign conventions, KPIs, financial-statement logic, and acceptance criteria. | Measure definitions, variance logic, account mappings, period-close rules. |
| Data Product Owner | Owns roadmap, prioritization, release acceptance, and stakeholder communications. | Release scope, backlog priority, publication readiness. |
| Semantic Model Owner | Owns the certified semantic model, object naming, dependency management, and compatibility with reports/downstream users. | Model design, measure lifecycle, calculation-group interactions. |
| Power BI Developer | Implements PBIP/TMDL/DAX changes, documentation, and regression tests. | Technical implementation and peer review. |
| Data Engineer | Owns upstream data contracts, source transformations, data quality checks, and refresh reliability. | Source schema, refresh pipeline, transformation changes. |
| Security Owner | Owns RLS policy, user/group mapping, and access review. | Role changes, RLS bridge changes, security exceptions. |
| Platform Administrator | Owns workspace, deployment pipeline, gateway, capacity, endorsement, and tenant settings. | Deployment, workspace/capacity configuration, gateway changes. |
| QA / Peer Reviewer | Reviews correctness, test evidence, performance evidence, and documentation completeness. | Pull-request approval and release evidence. |
| Support Owner | Owns incident triage, release notes, known issues, and operational monitoring. | Production support readiness. |

## 4. Model ownership and certification

### 4.1 Ownership metadata

Maintain the following ownership metadata in the model documentation and workspace description:

| Attribute | Required value |
|---|---|
| Semantic model name | `sm_finance_core` |
| Business domain | Finance |
| Business owner | Named finance owner or finance governance board |
| Technical owner | Named BI/data engineering owner |
| Support channel | Team mailbox, service desk queue, or Teams channel |
| Source systems | Confirmed GL, budget, forecast, procurement, AP/invoice, workforce sources |
| Certification status | Development / Promoted / Certified |
| Review frequency | Monthly for changes; quarterly governance review; annual access review minimum |

### 4.2 Certification criteria

The model should only be certified when:

- all visible tables, columns, measures, calculation groups, relationships, and hierarchies have descriptions;
- finance business definitions are confirmed and documented;
- RLS is tested for representative users;
- performance testing is completed and accepted;
- refresh reliability meets service-level expectations;
- regression-test evidence is attached to the release;
- unused/deprecated measures are hidden or removed according to policy;
- lineage and ownership metadata are complete;
- change-control approval is recorded.

## 5. Semantic-model standards

### 5.1 Dimensional modeling standards

- Use a star-schema-first design with conformed dimensions and narrow fact tables.
- Use one-direction dimension-to-fact relationships unless bidirectional filtering is explicitly approved.
- Document inactive date relationships and provide role-specific measures or calculation-group logic.
- Avoid ambiguous relationship paths across finance facts.
- Hide surrogate keys and technical columns from report authors unless explicitly required.
- Do not expose staging, bridge, or parameter tables to end users unless they are intentionally curated slicers.

### 5.2 DAX standards

- Use base measures for direct aggregations and build semantic measures on top of them.
- Use calculation groups for reusable scenario, time, variance, display-unit, and semi-additive patterns.
- Avoid using measures directly in `CALCULATE` Boolean filter arguments; use `FILTER` table expressions when filtering by measure results.
- Use variables for repeated expressions, selected values, denominators, and current/prior values.
- Use `DIVIDE` for division and apply denominator tolerance for currency values.
- Keep presentation text, labels, and icons separate from numeric measures.
- Explicitly document total-row and multi-select behavior.

### 5.3 Calculation-group standards

- Each calculation group must have a documented purpose, precedence, compatible measure types, incompatible measure types, and examples.
- Calculation items must include descriptions and dynamic format-string rules.
- Calculation groups that modify scale or unit formatting should apply dynamic format strings and should run after semantic calculation groups.
- Balance-sheet semi-additive calculation groups must remain separate from additive time-intelligence calculation groups.
- Avoid exposing conflicting old and new calculation-group slicers at the same time.

### 5.4 Metadata standards

Every governed object should include a description with:

1. business definition;
2. technical implementation note;
3. source or dependency note where relevant;
4. owner or approval note where relevant;
5. caveats, limitations, or business-owner confirmation status.

Use the prefix below for definitions inferred during technical review:

> **Inferred pending business-owner confirmation:**

## 6. Measure lifecycle management

| Lifecycle state | Meaning | Required action |
|---|---|---|
| Proposed | New measure requested but not implemented. | Capture requirement, owner, and acceptance criteria. |
| vNext | Implemented side-by-side for validation. | Keep visible only to developers/testers; run regression tests. |
| Active | Approved for production use. | Add final description, display folder, and documentation. |
| Deprecated | Replaced but retained for compatibility. | Hide measure, document replacement, monitor usage. |
| Retired | Safe to remove. | Remove after agreed retention period and release approval. |

Deprecated measures should remain hidden for at least one release cycle unless usage analysis proves there are no dependencies.

## 7. Change classification

| Change type | Examples | Risk | Approval required |
|---|---|---:|---|
| Documentation-only | README, model guide, descriptions that do not change logic. | Low | Technical owner. |
| Metadata-only | Display folders, descriptions, hiding unused columns. | Low/Medium | Technical owner; business owner if object visibility changes. |
| Additive measure | New base or helper measure with no existing behavior changed. | Medium | Semantic model owner and peer reviewer. |
| Measure replacement | Refactor of existing measure or redirect visuals to vNext measure. | High | Finance owner, semantic model owner, QA reviewer. |
| Calculation-group change | New item, precedence change, dynamic format change. | High | Finance owner, semantic model owner, QA reviewer. |
| Relationship change | Cardinality, active/inactive status, filter direction. | High | Semantic model owner, data engineer, QA reviewer. |
| RLS/security change | Role definition, bridge table, security filter, workspace permission. | Critical | Security owner, finance owner, platform admin. |
| Source schema/change | New source, changed grain, changed data type, changed source business rule. | High/Critical | Data engineer, finance owner, semantic model owner. |

## 8. Change-control workflow

### 8.1 Intake

Every requested change should include:

- requester and business owner;
- business problem or reporting need;
- affected reports, measures, tables, and users;
- expected result and acceptance criteria;
- urgency and target release;
- security or regulatory implications;
- rollback expectation.

### 8.2 Impact assessment

Before implementation, assess:

- measure dependency graph;
- report visual dependencies;
- Excel or downstream semantic-model dependencies;
- RLS impact;
- refresh impact;
- calculation-group precedence impact;
- performance risk;
- required documentation updates.

### 8.3 Development

- Implement changes in PBIP/TMDL source control, not directly in production.
- Use a feature branch or PR branch.
- Keep changes small enough for meaningful review.
- Add or update object descriptions with each semantic change.
- Add vNext measures side-by-side for significant refactors.
- Avoid destructive deletes until deprecation is complete.

### 8.4 Peer review

A pull request should include:

- summary of business and technical change;
- semantic-change log;
- files changed;
- impacted measures/calculation groups/tables;
- test evidence;
- screenshots for report-visible changes where applicable;
- rollback plan;
- approval checklist.

### 8.5 Validation

Minimum validation evidence:

- DAX regression query output for old vs new measures;
- row-count and reconciliation checks for affected facts;
- RLS test results;
- performance timings for high-use reports/measures;
- refresh test result;
- metadata standards check;
- business-owner sign-off for changed semantics.

### 8.6 Release

- Deploy through a controlled pipeline: Development → Test/UAT → Production.
- Record release version, date, approvers, and release notes.
- Notify report owners and key finance users of semantic changes.
- Monitor refresh, performance, and user issues after release.

### 8.7 Rollback

Rollback must be available for every high-risk change. The rollback plan should identify:

- previous PBIP commit or release tag;
- measures/calculation groups to restore;
- reports to repoint if required;
- RLS/security rollback steps;
- owner responsible for rollback approval and execution.

## 9. Required change-control artefacts

### 9.1 Semantic-change log

| Field | Required content |
|---|---|
| Change ID | Ticket, PR, or release reference. |
| Date | Date approved/released. |
| Requester | Person/team requesting the change. |
| Business owner | Approver of business meaning. |
| Technical owner | Implementer or semantic model owner. |
| Change summary | Short summary of what changed. |
| Object(s) changed | Measures, calc groups, tables, relationships, roles, reports. |
| Previous behavior | Existing logic/result. |
| New behavior | New logic/result. |
| Expected semantic impact | Equivalent / intentionally changed / unknown pending validation. |
| Test evidence | Link or summary of validation output. |
| Approval | Names/dates of approvers. |
| Rollback reference | Commit/tag or deployment package. |

### 9.2 Measure replacement register

| Existing measure | vNext measure | Status | Numeric equivalence | Owner | Notes |
|---|---|---|---|---|---|
| `[Actual GBP Base]` | `[vNext Actual GBP Base]` | Proposed | Pending test | Finance / BI | Validate by fiscal period, account, cost centre. |
| `[Budget GBP Base]` | `[vNext Budget GBP Base]` | Proposed | Pending test | Finance / BI | Validate budget scenario and fiscal filters. |
| `[Forecast GBP Base]` | `[vNext Forecast GBP Base]` | Proposed | Pending test | Finance / BI | Validate forecast version behavior. |
| `[BS Closing Balance (As-Of)]` | `[vNext BS Closing Balance As Of Base]` | Proposed | Pending test | Finance / BI | Validate period 0 and semi-additive behavior. |

### 9.3 Release checklist

- [ ] Business requirement captured and approved.
- [ ] Impact assessment completed.
- [ ] DAX formatted and peer reviewed.
- [ ] Metadata/descriptions updated.
- [ ] Regression tests passed or accepted differences documented.
- [ ] RLS tests passed.
- [ ] Performance tests accepted.
- [ ] Refresh test passed.
- [ ] Report owners notified.
- [ ] Release notes prepared.
- [ ] Rollback plan confirmed.
- [ ] Production deployment approved.

## 10. Testing and validation standards

### 10.1 DAX regression testing

For every measure replacement, compare old and new values by:

- fiscal year;
- fiscal period;
- account hierarchy level;
- cost centre hierarchy level;
- scenario;
- forecast version where applicable;
- total rows and subtotal rows;
- RLS user profile.

### 10.2 Performance testing

Use DAX Studio Server Timings and Query Plan for:

- top finance dashboard pages;
- high-cardinality matrix visuals;
- measures using calculation groups;
- semi-additive balance-sheet calculations;
- RLS-enabled queries.

Performance evidence should include before/after timings and any accepted trade-offs.

### 10.3 Security testing

RLS validation must include:

- a user with one cost centre;
- a user with multiple cost centres;
- a user with no cost centre access;
- an unrestricted finance admin if applicable;
- attempts to infer restricted totals through disconnected slicers or calculation groups.

### 10.4 Metadata quality checks

Automated checks should fail a release when:

- visible measures have no descriptions;
- visible tables or columns have no descriptions;
- technical keys are visible without approval;
- calculation groups lack descriptions or format-string rules;
- unapproved bidirectional relationships exist;
- deprecated measures remain visible;
- DAX contains known invalid patterns, such as measures used directly in `CALCULATE` Boolean filters.

## 11. Deployment and release management

Recommended environments:

| Environment | Purpose | Access |
|---|---|---|
| Development | Developer implementation and initial smoke testing. | BI developers and data engineers. |
| Test / UAT | Business validation, regression testing, RLS testing. | BI team, finance testers, security reviewers. |
| Production | Certified reporting and governed self-service. | Approved users only. |

Release notes should include:

- release version;
- summary of changes;
- semantic changes;
- known issues;
- deprecated objects;
- required report updates;
- validation summary;
- rollback reference.

## 12. Monitoring and operational controls

Monitor the model for:

- refresh failures and duration trends;
- query duration and capacity pressure;
- report usage and low-usage certified artefacts;
- RLS exceptions or access-review findings;
- measure usage and deprecated-object dependencies;
- user-reported reconciliation issues.

Recommended review cadence:

| Review | Frequency |
|---|---|
| Refresh reliability | Daily/weekly depending on SLA. |
| Performance and capacity | Monthly or after major releases. |
| Access and RLS | Quarterly, with annual formal recertification. |
| Measure/catalog governance | Monthly during refactor; quarterly thereafter. |
| Business definitions | Quarterly or when finance policy changes. |

## 13. Documentation standards

The repository should maintain:

- model review and recommendation document;
- implementation guide;
- DAX refactor script;
- semantic-change log;
- measure catalog;
- calculation-group guide;
- relationship and RLS documentation;
- release notes;
- known issues and support runbook.

Documentation must be updated in the same PR as the model change.

## 14. Decision records

Use architectural decision records for significant choices, such as:

- scenario dimension vs scenario calculation group;
- dynamic format strings vs static custom formats;
- balance-sheet semi-additive approach;
- RLS bridge design;
- relationship filter-direction exceptions;
- measure deprecation policy.

Minimum decision-record fields:

| Field | Description |
|---|---|
| Decision ID | Unique reference. |
| Status | Proposed / Accepted / Superseded. |
| Context | Problem and constraints. |
| Decision | Chosen approach. |
| Consequences | Benefits, risks, and trade-offs. |
| Approvers | Business and technical owners. |
| Date | Decision date. |

## 15. Immediate next steps

1. Assign named business, technical, security, and support owners.
2. Confirm certified definitions for core finance measures and sign conventions.
3. Create a measure catalog and dependency register from TMDL/XMLA metadata.
4. Apply vNext measures and calculation groups in a development branch only.
5. Run regression and RLS testing before any report migration.
6. Establish a release checklist and semantic-change log for every PR.
7. Schedule a quarterly model governance review.
