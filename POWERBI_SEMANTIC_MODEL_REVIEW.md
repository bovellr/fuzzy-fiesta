# Power BI PBIP Semantic Model Review: `sm_finance_core`

## Review scope and artefacts

- Source reviewed: `Finance_WS_Semantic_Models.zip`, extracted locally for static TMDL inspection.
- PBIP artefact: `sm_finance_core.pbip` with a semantic model folder and a report folder.
- Review method: static inspection of TMDL metadata, relationships, measures, calculation groups, roles, and model-level configuration. No live XMLA execution, VertiPaq Analyzer export, query-plan traces, or business-owner workshops were available; recommendations that depend on business intent are marked as **requires business-owner confirmation**.

## Executive summary

The model is a finance semantic model covering general-ledger actuals, balances, budgets, forecasts, purchasing, invoice ledger, AP/PO validation, account hierarchy, cost centres, jobs, activities, suppliers, customers, dates, statement selectors, navigation tables, and row-level security. It already uses several enterprise patterns: a dedicated `_Measures` table, star-schema-style fact/dimension tables, inactive role-playing date relationships, calculation groups for scenario, variance, time intelligence, balance-sheet reporting, account view, and trend analysis, and a bridge table for cost-centre security.

Primary improvement opportunities are:

1. Reduce the very large measure surface by consolidating repeated actual/budget/forecast/outturn, period/YTD/prior-period, scaling, and variance patterns into fewer base measures and calculation items.
2. Move repeated time-intelligence and scenario-comparison logic from explicit measures into calculation groups where behavior is measure-agnostic.
3. Clarify calculation-group precedence and interaction rules, especially scenario before variance, variance before trend/BS reporting, time intelligence before account view, and dynamic-format-string behavior.
4. Add complete descriptions to measures, calculation items, tables, columns, relationships, perspectives, and hierarchies, with inferred descriptions clearly labelled until finance/business owners confirm definitions.
5. Review relationship direction, inactive date roles, security propagation, and parameter/selector disconnected tables to make DAX simpler and governance stronger.
6. Introduce automated metadata quality checks and DAX regression tests before refactoring.

## Model purpose and scope

### Inferred purpose

**Inferred, requires business-owner confirmation:** `sm_finance_core` appears to provide a governed finance reporting layer for financial statements, management reporting, budget/forecast comparison, balance-sheet as-of reporting, purchasing, invoice/AP validation, and secured cost-centre analysis.

### In scope

- Profit-and-loss reporting for actuals, budgets, forecasts, and outturns.
- Balance-sheet reporting using closing, opening, movement, and as-of calculations.
- Variance reporting against plan, forecast, and selected comparison modes.
- Fiscal-period time intelligence including current period, YTD, full year, prior period, MoM, prior year, YoY, and YoY YTD.
- Procurement and invoice-ledger analysis across suppliers, purchase orders, purchase lines, and AP/PO validation facts.
- Cost-centre restricted access through `Finance_Restricted` role and the `bridge_user_cost_centre_access` table.
- Report navigation and statement-parameter tables used by the report layer.

### Out of scope / not validated

- Numeric correctness against source systems.
- Refresh performance, partitions, incremental refresh, aggregations, and VertiPaq compression metrics.
- Visual-level usage analysis from the report layer, because only static metadata was reviewed.
- Business definitions for finance line items, account classifications, and signs.

## Architecture and PBIP folder structure

The zip contains a standard PBIP layout:

| Area | Purpose | Review notes |
|---|---|---|
| `sm_finance_core.pbip` | PBIP entry point | Opens the semantic model/report in Power BI Desktop project mode. |
| `sm_finance_core.SemanticModel/definition` | TMDL semantic model definition | Contains model metadata, tables, relationships, roles, and shared expressions. |
| `sm_finance_core.SemanticModel/definition/tables` | One TMDL file per table | Includes dimensions, facts, disconnected selectors, a `_Measures` table, and calculation-group tables. |
| `sm_finance_core.SemanticModel/definition/relationships.tmdl` | Relationship definitions | Central place to review cardinality, active/inactive relationships, and security implications. |
| `sm_finance_core.SemanticModel/definition/roles` | RLS roles | Contains `Finance_Restricted`. |
| `sm_finance_core.Report` | Report definition | Report-layer review was not the primary focus of this semantic-model assessment. |

## Table inventory and dimensional-model roles

### Fact tables

| Table | Inferred role | Recommendations |
|---|---|---|
| `fact_gl_transactions` | GL transactional actuals | Keep granular; hide technical keys; ensure additive amount columns have explicit summarization behavior and descriptions. |
| `fact_gl_balances` | Period/account balance snapshots | Document snapshot grain and balance sign convention; avoid using transactional time-intelligence assumptions on balances. |
| `fact_gl_forecasts` | Forecast fact | Confirm versioning grain and relationship to forecast-version dimension. |
| `fact_gl_budget_variance` | Budget/variance support fact | Validate whether this duplicates budget facts already available in measures; remove if only an intermediate extract. |
| `fact_invoice_ledger` | AP invoice ledger | Document active invoice date plus inactive due/received/paid date roles and provide role-specific measures. |
| `fact_purchase_orders` | Purchase-order header fact | Check one-to-many relationship with purchase lines; avoid double-counting when combining header and line values. |
| `fact_purchase_lines` | Purchase-order line fact | Treat as line-grain spend/commitment fact; hide degenerate identifiers unless needed. |
| `fact_ap_po_validation` | AP/PO validation fact | Document validation business rules and exception status columns. |

### Dimension and bridge tables

| Table | Inferred role | Recommendations |
|---|---|---|
| `dim_date` | Conformed fiscal calendar | Mark as date table if not already; document fiscal-year/month logic, prior-period keys, and completeness. |
| `dim_accounts` | Account dimension | Document account type, natural sign, statement mappings, and hierarchy relationship. |
| `dim_account_hierarchy` | Financial-statement hierarchy | Confirm ragged hierarchy handling and sort order; consider parent-child or flattened hierarchy consistency. |
| `dim_cost_centres` | Cost centre dimension | Key security dimension; document ownership, active/inactive status, and hierarchy levels. |
| `dim_jobs`, `dim_activities`, `dim_suppliers`, `dim_customers` | Analysis dimensions | Hide surrogate keys and add business descriptions for display columns. |
| `dim_forecast_version` | Forecast version dimension | Define default/latest version selection rule. |
| `dim_scenario` | Scenario dimension | Align with `cg_Scenario`; avoid conflicting scenario filters. |
| `dim_time_basis` | Time basis selector | Confirm whether it overlaps with time-intelligence calculation group. |
| `bridge_user_cost_centre_access` | RLS bridge | Validate security propagation and many-to-many behavior; prefer single-direction filters unless bidirectional security is explicitly required. |
| Statement/navigation/selector tables | Disconnected report-control dimensions | Keep hidden from most end users except curated slicers; document valid combinations and defaults. |

## Relationships, filter direction, cardinality, and security implications

### Observed patterns

- Facts connect to `dim_date`, `dim_cost_centres`, `dim_accounts`, `dim_jobs`, and `dim_activities` using star-schema relationships.
- Several inactive date relationships support alternative date roles such as invoice due date, received date, paid date, purchase-order created date, purchase-line created date, and receipt date.
- A role named `Finance_Restricted` and a cost-centre bridge indicate cost-centre based RLS.

### Recommendations

1. **Document every inactive date relationship with a matching role-playing measure pattern.** Example: `Invoice Amount by Due Date` should explicitly use `USERELATIONSHIP(fact_invoice_ledger[DueDateKey], dim_date[DateKey])` or a calculation-item pattern if many measures need date-role switching.
2. **Avoid bidirectional filtering except for audited security use cases.** Bidirectional security can leak filters across unrelated facts and make DAX harder to reason about.
3. **Confirm relationship cardinality for bridge and selector tables.** Disconnected selectors should not have accidental relationships that change filter context unexpectedly.
4. **Prefer dimension-to-fact, single-direction filtering.** This keeps measures composable and improves query plans.
5. **Add relationship descriptions.** Include grain, active/inactive status, business reason, and whether the relationship participates in RLS.
6. **Security regression tests are required.** Test users with one, many, and no assigned cost centres; confirm totals cannot be recovered through disconnected slicers or calculation-group combinations.

## Measure catalog and dependency structure

### Current state

Static TMDL inspection found approximately 335 measures in `_Measures.tmdl`. The measure set includes base amounts, display/scaled measures, PL and BS measures, budget/forecast/outturn measures, time-period measures, variance measures, KPI/status measures, and report-specific selectors.

### Enterprise target structure

Use a layered measure architecture:

1. **Base measures**: directly aggregate one fact and one business concept, e.g. `[Actual Amount Base]`, `[Budget Amount Base]`, `[Forecast Amount Base]`, `[Balance Amount Base]`.
2. **Semantic measures**: apply account filters, signs, statement-line logic, or balance/PL behavior, e.g. `[PL Amount]`, `[BS Closing Balance]`, `[Capital Commitments]`.
3. **Presentation measures**: apply unit scaling, selected statement view, or display-only logic. Keep these few and named clearly.
4. **Calculation groups**: apply reusable scenario, variance, time, trend, and account-view transformations.
5. **Report helper measures**: titles, selected labels, formatting helpers, and visual-state measures. Store in a `zz Report Helpers` or `Report UX` display folder.

### Duplicated or reusable logic to consolidate

| Pattern observed | Recommended consolidation | Expected benefit |
|---|---|---|
| Actual/Budget/Forecast/Outturn variants repeated across PL, BS, capital, and KPI measures | Keep one base measure per scenario and let `cg_Scenario` select scenario where possible | Fewer measures, simpler testing, lower maintenance. |
| Period, YTD, prior-period, prior-year, MoM, and YoY explicit measures alongside `cg_Time_Intelligence` | Replace explicit reusable variants with calculation items; keep explicit measures only where balance-sheet semantics differ | Reduces duplicate DAX and inconsistent fiscal logic. |
| Variance measures such as budget variance, forecast variance, and comparison variance alongside `cg_Variance` | Move generic comparison calculations to `cg_Variance`; keep only business-specific variance measures requiring special sign or denominator | Consistent variance logic and dynamic format strings. |
| Scaled/display versions of measures | Use one scaling calculation group or a small set of presentation measures using `[Selected Statement Unit Multiplier]` | Avoid base/display measure explosion. |
| Balance-sheet as-of logic repeated in multiple BS measures | Create base measures for `[BS Closing Balance Base]`, `[BS Opening Balance Base]`, `[BS Movement Base]`; use `cg_BS_Reporting` for as-of variants | Preserves non-additive balance behavior while reducing copies. |

### Inefficient or overly complex measure patterns to review

- Measures that use `FILTER(ALL(...))` where direct Boolean filters in `CALCULATE` would be equivalent. Prefer `CALCULATE([Measure], dim_date[FiscalYearNumber] = _fy, dim_date[FiscalMonthNumber] <= _fp)` after deliberate `REMOVEFILTERS(dim_date)` only when the whole date context must be reset.
- Measures that repeatedly compute selected fiscal period/year keys. Centralize in `[Selected FiscalPeriodKey]`, `[Selected FiscalYear]`, `[Selected FiscalMonth]`, and `[Latest Actual FiscalPeriodKey]` helper measures.
- Measures that use iterators over large fact tables when a simple additive base measure plus dimension filter would work. Use `SUMX` only when row-wise expression evaluation is required.
- Measures that compare against zero with exact equality for currency. Use a tolerance consistently, e.g. `ABS(_denominator) < 0.005`, already visible in variance-style logic.
- Measures where `SELECTEDVALUE` returns blank in totals or multi-selects. Add explicit multi-select behavior using `HASONEVALUE`, `ISINSCOPE`, or documented default values.
- Measures that mix business logic and visual formatting. Separate numeric result measures from label, tooltip, and format-string helpers.

### Suggested base-measure blueprint

```DAX
Actual Amount Base :=
SUM ( fact_gl_transactions[AmountGBP] )

Budget Amount Base :=
SUM ( fact_gl_budget_variance[BudgetAmountGBP] )

Forecast Amount Base :=
SUM ( fact_gl_forecasts[ForecastAmountGBP] )

Selected Unit Multiplier :=
COALESCE ( SELECTEDVALUE ( 'Statement Unit'[Multiplier] ), 1 )

Amount Display :=
DIVIDE ( [Amount Base], [Selected Unit Multiplier] )
```

Column names above are illustrative because source-column business definitions were not validated. Replace with the actual certified amount columns.

## DAX improvement standards

### Iterator usage

- Replace `SUMX(fact, fact[amount])` with `SUM(fact[amount])` when no row-wise expression is required.
- Move row-wise sign adjustment or currency conversion into Power Query/source SQL if static by row; otherwise isolate it in a single base measure.
- Avoid nested iterators over facts and dimensions unless the business rule explicitly requires evaluating each visible row independently.

### Filter context

- Use `KEEPFILTERS` when adding a filter that should intersect existing slicers.
- Use `REMOVEFILTERS` only for the specific table/columns being reset; avoid broad `ALL` over fact tables.
- Prefer `TREATAS` for disconnected selectors only when relationships are intentionally absent and documented.
- Make total behavior explicit for measures depending on a single period, scenario, or statement line.

### Time intelligence

- Because the model appears fiscal-period-key based, custom fiscal logic is appropriate. Avoid built-in calendar functions such as `SAMEPERIODLASTYEAR` unless the date table is certified and day-grain behavior is intended.
- Balance-sheet measures should use as-of logic, not additive YTD logic, unless calculating movements.
- Provide regression tests for fiscal year boundary behavior, especially period 1 prior-period fallback and prior-year comparisons.

### Variables

- Use variables for selected period/scenario values, denominator values, and repeated sub-expressions.
- Return named variables rather than deeply nested `IF`/`CALCULATE` blocks.
- Use consistent variable names: `_Current`, `_Prior`, `_Denominator`, `_FiscalYear`, `_FiscalPeriod`, `_Result`.

## Calculation groups

### Inventory

| Calculation group | Inferred precedence | Purpose | Recommended action |
|---|---:|---|---|
| `cg_Scenario` | 10 | Select Actual, Budget, Forecast, or Outturn | Keep; document that it should run before variance calculations. |
| `cg_Variance` | 15 | Compare selected measures against plan/forecast/comparison scenarios | Keep; refactor repeated scenario comparison measures into this group. |
| `cg_Trend_Analysis` | 20 | Period trend behavior | Review overlap with time intelligence; merge if only one item remains. |
| `cg_BS_Reporting` | 25 | Balance-sheet current/as-of/prior/movement behavior | Keep separate from generic time intelligence due to semi-additive BS semantics. |
| `cg_Time_Intelligence` | 30 | Current period, YTD, full year, prior, MoM, YoY | Keep; add descriptions, selection expression defaults, and consistent dynamic format strings. |
| `cg_Account_View` | 40 | PL, BS, and charity BS views | Keep; document interaction with account hierarchy and statement selectors. |

### Precedence and interaction rules

Recommended documented interpretation of current precedence:

1. `cg_Scenario` selects the scenario slice first.
2. `cg_Variance` can override scenario context to compute actual-vs-plan/forecast/comparison deltas.
3. `cg_Trend_Analysis` and `cg_BS_Reporting` shape period trend or balance-sheet semi-additive behavior.
4. `cg_Time_Intelligence` applies fiscal time transformations for additive measures.
5. `cg_Account_View` applies account-view transformation last.

Validate this ordering with DAX regression queries, because calculation-group precedence can materially change results when calculation items apply `CALCULATE(SELECTEDMEASURE(), ...)` and modify the same filters.

### Calculation item recommendations

- Add descriptions to every calculation item, including business definition, technical filter behavior, valid measure types, and examples.
- Add format-string expressions to every item. Items returning percentages should use a percent format; items returning currency should preserve `SELECTEDMEASUREFORMATSTRING()`.
- Add selection expressions/defaults where supported by the target compatibility level, so visuals have deterministic behavior when no calculation item is selected.
- Review `MoM %`, `YoY %`, and variance percentage denominator sign convention. Finance teams often require denominator as `ABS(prior)` for movement percentages but raw plan/forecast denominator for budget variance; document the chosen rule.
- Prevent conflicting slicers by hiding calculation-group columns from generic field lists and exposing curated slicers only.

### Potential redundancy or conflict

- `cg_Trend_Analysis` has only one inferred calculation item, `Analysis by Period`. If it is only a pass-through or visual helper, consider removing it or merging the behavior into `cg_Time_Intelligence`.
- `dim_scenario` and `cg_Scenario` may both filter scenario context. Decide whether scenario is modeled as a physical dimension, a calculation-group selector, or both with clearly separated responsibilities.
- `dim_time_basis` and `cg_Time_Intelligence` may overlap. If both are user-facing, document precedence and allowed combinations.
- Explicit PL/BS time measures can conflict with time calculation items. Hide or deprecate explicit variants once calculation-group coverage is complete.

### Usage examples

| User need | Recommended measure/calculation group combination |
|---|---|
| Actual YTD PL | Base PL amount + `cg_Scenario = Actual` + `cg_Time_Intelligence = YTD`. |
| Actual vs Budget % | Base amount + `cg_Variance = Variance to Plan %`; scenario item should be controlled by the calc item. |
| BS closing balance as of current period | BS base balance + `cg_BS_Reporting = As Of Current Period`; avoid additive YTD calc item. |
| Forecast outturn vs plan | Base amount + `cg_Variance = Variance Outturn to Plan`. |

## Metadata and descriptions

### Required description standard

Every object should have two description parts:

1. **Business definition:** plain-language meaning, owner, and intended users.
2. **Technical notes:** source table/column, DAX pattern, filter behavior, security considerations, and caveats.

Use this prefix where definitions are inferred:

> **Inferred pending finance owner confirmation:** ...

### Priority metadata backlog

| Object type | Required actions |
|---|---|
| Measures | Add descriptions for all measures. Include scenario/time assumptions, sign convention, blank behavior, total behavior, and whether the measure is deprecated. |
| Calculation groups/items | Add descriptions, precedence rationale, dynamic-format-string notes, and examples of compatible/incompatible measures. |
| Tables | Add table descriptions with grain, source system, refresh cadence, owner, and dimensional role. |
| Columns | Hide technical keys; describe business columns, sort columns, flags, and status columns. |
| Hierarchies | Define levels, sort order, ragged behavior, and roll-up semantics. |
| Relationships | Describe grain, active/inactive state, security participation, and role-playing date purpose. |
| Perspectives | If perspectives exist or are planned, document persona, visible tables/measures, and maintenance owner. |

### Example descriptions

- `[Actual GBP Base]`: **Inferred pending finance owner confirmation:** Aggregates actual general-ledger transaction value in GBP before display scaling. Technical note: intended as a base measure for scenario, variance, and time calculation groups; should not include visual-specific formatting logic.
- `cg_Time_Intelligence[YTD]`: **Inferred pending finance owner confirmation:** Returns fiscal year-to-date value through the selected fiscal period. Technical note: removes existing date filters and reapplies fiscal-year and fiscal-month filters; valid for additive measures, not closing balance measures unless explicitly approved.
- `bridge_user_cost_centre_access`: **Inferred pending finance owner confirmation:** Maps user identities to cost centres they are permitted to view. Technical note: participates in `Finance_Restricted` RLS; must be tested for users with no access and users with multiple cost centres.

## Naming, formatting, display folders, and organization

### Naming conventions

- Measures: `[Business Concept Base]`, `[Business Concept]`, `[Business Concept Display]`, `[Business Concept %]`.
- Avoid abbreviations except widely accepted finance terms: PL, BS, YTD, MoM, YoY, GBP.
- Calculation groups: prefix with `cg_` for technical tables, but expose friendly slicer column names.
- Selector tables: use consistent names, e.g. `Selector Statement Measure`, `Selector Comparison Mode`, or keep current names but standardize spaces/underscores.
- Hidden helper measures: prefix with `_` only if they are hidden; otherwise use display folders.

### Display folders

Recommended folders:

- `00 Base Measures`
- `01 Scenario Measures`
- `02 PL Measures`
- `03 BS Measures`
- `04 Capital and Procurement`
- `05 Variance and KPI`
- `06 Report UX Helpers`
- `99 Deprecated`

### Formatting conventions

- Currency: `£#,0; (£#,0); -` or enterprise-standard equivalent.
- Scaled currency: dynamic format string reflecting units selected by `Statement Unit`.
- Percentages: `0.0%;-0.0%;0.0%` or confirm zero display with finance owner.
- Counts: `#,0`.
- Ratios/days: separate formats; never reuse currency format.

## Performance findings and remediation

### Findings

1. The measure count is high for one central measure table, increasing governance and regression risk.
2. Repeated scenario, variance, and time patterns likely increase formula-engine work and create inconsistent edge-case behavior.
3. Semi-additive BS logic and additive PL logic coexist; if not isolated, users can apply invalid time-intelligence combinations.
4. Disconnected selector tables can make measures branch heavily with `SELECTEDVALUE` and `SWITCH` logic.
5. Static review cannot confirm VertiPaq issues, but finance models commonly suffer from high-cardinality text columns, unhidden keys, and unused columns in fact tables.

### Remediation plan

| Phase | Action | Validation |
|---|---|---|
| 1 | Export measure dependencies and identify unused measures from report visuals and XMLA DMV usage. | Measure dependency graph; unused/deprecated list. |
| 2 | Add descriptions and display folders without changing DAX. | Metadata diff only; no numeric change expected. |
| 3 | Introduce or certify base measures for actual, budget, forecast, outturn, balances, commitments, and invoices. | DAX Studio queries compare old vs new by fiscal period/account/cost centre. |
| 4 | Replace duplicate explicit time/variance measures with calculation-group driven measures. | Regression matrix across periods, scenarios, and statement views. |
| 5 | Optimize relationships, hidden columns, summarization, and data types. | VertiPaq Analyzer before/after memory and cardinality comparison. |
| 6 | Establish semantic-model CI checks. | Automated checks fail builds for missing descriptions, visible keys, invalid formats, and unapproved bidirectional relationships. |

## Assumptions, risks, open questions, and governance

### Assumptions

- Fiscal calendar uses fiscal year/month/period keys rather than standard calendar-year time intelligence.
- GBP is the reporting currency for most core finance measures.
- Balance-sheet measures require semi-additive as-of logic.
- Cost-centre security is mandatory for restricted finance users.

### Risks

- Refactoring explicit measures into calculation groups can change totals if current measures include custom total behavior.
- Scenario calculation items can conflict with physical scenario filters if both are active.
- Balance-sheet measures can return incorrect results if users apply generic YTD calculation items.
- Missing descriptions create audit and support risk, especially for finance sign conventions and security filters.

### Open questions for business/data owners

1. What is the certified sign convention for income, expenditure, assets, liabilities, and reserves?
2. Should variance percentages use raw denominator or absolute denominator by statement section?
3. What is the authoritative default forecast version?
4. Which date role should each invoice and purchasing measure use by default?
5. Which explicit measures are currently used by certified reports, Excel connected workbooks, or downstream semantic models?
6. Are statement parameter and navigation tables intended to be visible in self-service perspectives?
7. What is the expected behavior for multi-select fiscal periods and scenarios?

### Recommended governance

- Assign business owners for PL, BS, procurement, AP, and security definitions.
- Maintain a semantic-model changelog with DAX semantic changes explicitly called out.
- Introduce a deprecation process: hide first, monitor usage, then remove after an agreed window.
- Require pull-request review for TMDL changes with automated metadata and DAX formatting checks.
- Keep a certified measure catalog generated from TMDL and published with the model.

## Validation approach and regression-test cases

### Static checks

- Parse TMDL and fail if any measure, calculation item, table, or visible column lacks a description.
- Fail if technical key columns are visible, unless explicitly approved.
- Fail if measures are not in display folders.
- Fail if calculation items lack format-string definitions where the result type changes.
- Fail if unapproved bidirectional or many-to-many relationships exist.

### DAX regression tests

Create DAX query tests comparing old and refactored measures for representative slices:

| Test area | Regression case |
|---|---|
| PL actual period | Compare old `[PL Actual Period]` to new base measure with `cg_Scenario = Actual` and `cg_Time_Intelligence = Current Period`. |
| PL YTD budget | Compare old `[PL Budget YTD]` to new base measure with `cg_Scenario = Budget` and `cg_Time_Intelligence = YTD`. |
| Forecast outturn | Validate actual-to-date plus forecast remainder behavior by fiscal period and forecast version. |
| BS closing balance | Validate current period, prior period, and prior year as-of values by account hierarchy and cost centre. |
| Variance percentages | Validate zero, negative, and small denominator behavior. |
| Fiscal boundary | Validate period 1 prior-period fallback and prior-year period mapping. |
| RLS | Validate permitted and denied cost centres for sample users. |
| Inactive date roles | Validate invoice due/received/paid and PO created/receipt role-specific measures. |
| Calculation-group combinations | Validate scenario + variance + time + account-view combinations return documented results. |

### Suggested tooling

- Tabular Editor Best Practice Analyzer for naming, descriptions, hidden columns, formats, and relationship rules.
- DAX Studio Server Timings and Query Plan for expensive measures.
- VertiPaq Analyzer for memory, cardinality, and encoding review.
- Power BI Project/TMDL diff review in source control.
- XMLA DMV extracts for dependencies, object visibility, and usage.

## Proposed implementation backlog

1. Generate a full measure catalog with expression, display folder, format string, description, dependency list, and deprecation status.
2. Add missing descriptions to all semantic objects, starting with calculation groups and the top 50 most-used measures.
3. Create a dependency graph and classify measures as base, semantic, presentation, report-helper, duplicate, or deprecated.
4. Certify base measures and standardize naming/display folders.
5. Refactor generic time and variance measures into calculation groups after regression tests are in place.
6. Add calculation-group documentation directly in object descriptions and in a published model guide.
7. Validate RLS and inactive date-role behavior with automated DAX queries.
8. Run VertiPaq Analyzer and remove/hide unused high-cardinality columns.
9. Establish CI quality gates for TMDL metadata and DAX formatting.

## Semantic-change documentation

No semantic-model files were changed as part of this review. This document provides recommendations only. Any future DAX refactor should record:

- Original measure/calculation item name.
- New measure/calculation item name.
- Expected numeric equivalence or intentional difference.
- Affected reports/visuals.
- Regression test evidence.
- Business-owner approval for semantic changes.
