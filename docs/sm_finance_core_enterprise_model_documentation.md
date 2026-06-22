# `sm_finance_core` Enterprise Semantic Model Documentation

## 1. Document control

| Attribute | Value |
|---|---|
| Model | `sm_finance_core` |
| Domain | Finance |
| Repository artefact reviewed | `Finance_WS_Semantic_Models.zip` |
| Documentation type | Enterprise semantic model documentation |
| Status | Draft pending business-owner confirmation |
| Prepared for | Finance, BI, data engineering, governance, security, and support teams |
| Review method | Static PBIP/TMDL review plus documented vNext DAX refactor recommendations |
| Last updated | 2026-06-22 |

### 1.1 Change history

| Version | Date | Author / owner | Summary | Approval status |
|---|---|---|---|---|
| 0.1 | 2026-06-22 | BI / data engineering review | Initial enterprise model documentation created from static PBIP/TMDL inspection and vNext refactor assets. | Draft; requires business-owner and semantic-model-owner approval. |

### 1.2 Approval requirements

Before this document is treated as certified model documentation, the following approvals are required:

- Finance Business Owner: confirms finance definitions, sign conventions, KPIs, and statement logic.
- Semantic Model Owner: confirms table roles, relationship assumptions, DAX patterns, calculation-group interactions, and deprecation approach.
- Security Owner: confirms RLS design, bridge table behavior, and access-review cadence.
- Data Engineering Owner: confirms source-system lineage, refresh cadence, data quality controls, and source grain.
- Platform Owner: confirms workspace, deployment pipeline, endorsement/certification, and operational monitoring.

## 2. Executive summary

`sm_finance_core` is a governed finance semantic model for financial reporting, management reporting, budget/forecast analysis, balance-sheet reporting, purchasing, AP/invoice analysis, workforce-related finance measures, navigation, and cost-centre-secured reporting.

Static inspection indicates the model uses enterprise-friendly patterns including:

- PBIP/TMDL source-controlled semantic model structure;
- a dedicated `_Measures` table;
- fact and dimension tables following a broadly star-schema-oriented design;
- calculation groups for scenario, variance, time intelligence, balance-sheet reporting, account view, and trend analysis;
- inactive date relationships for role-playing dates;
- RLS support through `Finance_Restricted` and cost-centre access mapping.

The current improvement direction is to introduce a non-destructive `vNext` DAX layer, validate it side-by-side, and then deprecate duplicate or overly specific current measures only after regression testing and business approval.

## 3. Model purpose, scope, and users

### 3.1 Business purpose

**Inferred pending business-owner confirmation:** The model provides a central finance reporting layer for actual, budget, forecast, outturn, balance-sheet, procurement, AP/invoice, and workforce-related reporting across fiscal periods, accounts, cost centres, jobs, activities, suppliers, customers, and report-navigation constructs.

### 3.2 In-scope capabilities

- Profit-and-loss / income-and-expenditure reporting.
- Balance-sheet / statement-of-financial-position reporting.
- Trial balance and account-hierarchy analysis.
- Actual, budget, forecast, and outturn reporting.
- Variance to plan, forecast, comparison scenario, and outturn-to-plan reporting.
- Current period, YTD, full-year, prior-period, MoM, prior-year, YoY, and YoY YTD analysis.
- Purchase order, purchase line, AP/PO validation, and invoice-ledger reporting.
- Workforce-related finance metrics such as WTC, WTW, WTP, HCT, WTE, and cost-per-WTE patterns where source definitions are confirmed.
- Cost-centre restricted reporting through RLS.
- Report page navigation, statement selectors, display-unit selectors, and other disconnected control tables.

### 3.3 Out-of-scope capabilities

- Source-system master-data stewardship outside Power BI.
- Official financial close process approval.
- Write-back or commentary workflow governance unless separately implemented.
- Statutory filing or externally audited reporting without additional controls.
- Data quality remediation in source systems.

### 3.4 Primary personas

| Persona | Expected usage |
|---|---|
| Finance executive | High-level financial position, trends, and variance performance. |
| Finance business partner | Cost-centre, directorate, service-line, and account analysis. |
| Budget holder | Actuals vs budget, forecast/outturn, and variance commentary. |
| Procurement/AP analyst | PO, purchase-line, invoice-ledger, and AP/PO validation analysis. |
| Workforce/finance analyst | Workforce cost, WTE/WTC/WTW/WTP/HCT analysis where definitions are confirmed. |
| BI developer | Curated report development, semantic-model extension, DAX support. |
| Data engineer | Source refresh, transformation, lineage, and quality management. |
| Auditor/governance reviewer | Change traceability, approvals, RLS, and certified definition review. |

## 4. Architecture and PBIP structure

| Artefact | Purpose | Governance note |
|---|---|---|
| `sm_finance_core.pbip` | PBIP project entry point. | Changes should be made through source control and reviewed through PRs. |
| `sm_finance_core.SemanticModel/definition` | TMDL semantic model definition. | Authoritative semantic-model metadata. |
| `sm_finance_core.SemanticModel/definition/tables` | Table, column, measure, partition, and calculation-group TMDL files. | Object descriptions and display folders should be maintained here. |
| `sm_finance_core.SemanticModel/definition/relationships.tmdl` | Relationship definitions. | Relationship changes require impact assessment and regression testing. |
| `sm_finance_core.SemanticModel/definition/roles` | RLS role definitions. | Role changes require security-owner approval. |
| `sm_finance_core.Report` | Report definition. | Report changes should be coordinated with semantic changes. |
| `docs/implementation/refactored_measures_and_calculation_groups.dax` | Proposed vNext DAX implementation script. | Non-destructive implementation layer for controlled validation. |
| `docs/implementation/powerbi_dax_refactor_implementation_guide.md` | vNext rollout and validation guide. | Required implementation guidance before production migration. |
| `docs/enterprise_model_governance_and_change_control.md` | Enterprise governance and change-control guide. | Defines approvals, lifecycle, release, and support controls. |

## 5. Data model inventory

### 5.1 Fact tables

| Table | Business role | Grain / key consideration | Enterprise documentation requirement |
|---|---|---|---|
| `fact_gl_transactions` | GL transaction movements. | Transaction or posting-line grain; includes signed amount and workforce-related metrics. | Confirm source system, posting grain, signed amount convention, and whether data is closed-period only. |
| `fact_gl_balances` | Period/account finance balances, actuals, budgets, WTC. | Fiscal period/account/cost centre style grain; includes opening-balance flag. | Confirm snapshot/semi-additive behavior and period 0 brought-forward treatment. |
| `fact_gl_forecasts` | Forecast values and versions. | Forecast period/version/account/cost-centre grain. | Confirm default/latest forecast version and forecast freeze process. |
| `fact_gl_budget_variance` | Budget variance/commentary-support style fact. | Contains actual, budget, variance, run-rate, prior-period/year values. | Confirm whether it is authoritative or derived/denormalized from other finance facts. |
| `fact_invoice_ledger` | Invoice ledger values and statuses. | Invoice-level or invoice-line grain; active invoice date and inactive due/received/paid date roles. | Document invoice lifecycle definitions and active date role. |
| `fact_purchase_orders` | Purchase order header values. | PO header grain. | Prevent double counting when combined with purchase-line fact. |
| `fact_purchase_lines` | Purchase line quantities and values. | PO line grain. | Confirm quantity/value definitions and receipt/invoice status rules. |
| `fact_ap_po_validation` | AP/PO matching and validation exceptions. | Invoice/register validation grain. | Document validation flags and exception categories. |

### 5.2 Dimension and control tables

| Table | Role | Enterprise documentation requirement |
|---|---|---|
| `dim_date` | Conformed fiscal calendar. | Confirm fiscal-year start, fiscal-month numbering, period keys, prior-period keys, and marked-date-table status. |
| `dim_accounts` | Account dimension. | Confirm account hierarchy, natural sign, display sign, account type, statement mappings, and reporting categories. |
| `dim_account_hierarchy` | Financial-statement/account hierarchy. | Document hierarchy levels, sorting, ragged behavior, and roll-up rules. |
| `dim_cost_centres` | Cost-centre dimension and security axis. | Document entity/directorate/care group/division/service-line hierarchy and RLS impact. |
| `dim_jobs` | Job/project dimension. | Confirm source, active/inactive logic, and grain. |
| `dim_activities` | Activity dimension. | Confirm activity hierarchy and use in finance reporting. |
| `dim_suppliers` | Supplier dimension. | Confirm supplier identity, duplicate handling, and sensitive fields. |
| `dim_customers` | Customer dimension. | Confirm use cases and data sensitivity. |
| `dim_forecast_version` | Forecast version selector. | Confirm default version, type, sort order, and lifecycle. |
| `dim_scenario` | Scenario dimension. | Align with scenario calculation groups and scenario selector behavior. |
| `dim_time_basis` | Time-basis selector. | Confirm overlap or interaction with time-intelligence calculation groups. |
| `bridge_user_cost_centre_access` | RLS bridge table. | Document user identity mapping, refresh cadence, exception process, and access review. |
| Statement/navigation/selector tables | Disconnected report-control tables. | Document valid values, defaults, and which are exposed to report consumers. |

## 6. Relationships and security implications

### 6.1 Relationship principles

- Use one-direction dimension-to-fact relationships by default.
- Keep inactive role-playing date relationships documented and activated only through explicit measures/calculation items.
- Avoid bidirectional filtering unless explicitly approved for a documented use case.
- Document many-to-many or bridge-table behavior with security implications.
- Test relationship changes against all finance facts because shared dimensions can affect unrelated visuals.

### 6.2 Date roles

The model contains active date relationships for primary fact dates and inactive relationships for alternate roles such as invoice due date, invoice received date, invoice paid date, PO created date, purchase-line created date, and purchase-line receipt date.

Enterprise rule:

- Every inactive date relationship must have either a named role-playing measure or documented calculation-item pattern.
- Report users must be able to identify which date role a measure uses.
- Date-role switches must be regression-tested for totals and fiscal-boundary behavior.

### 6.3 RLS and security

`Finance_Restricted` and `bridge_user_cost_centre_access` indicate a cost-centre-based RLS design.

Required RLS controls:

- RLS business owner and technical owner assigned.
- User-to-cost-centre mapping source documented.
- Refresh and exception process documented.
- Quarterly access review and annual formal recertification.
- Tests for one cost centre, multiple cost centres, no cost centre, and unrestricted/admin access.
- Tests that disconnected selectors and calculation groups cannot expose restricted totals.

## 7. Measure architecture

### 7.1 Current-state observations

Static inspection found a large central measure table with hundreds of measures. Measure names indicate repeated patterns for:

- actual/budget/forecast/outturn;
- MTD/YTD/FY/prior period/prior year/MoM/YoY;
- PL and BS reporting;
- scaled/display values;
- variance and RAG/status logic;
- workforce and procurement metrics;
- report navigation, labels, colors, and UI helpers.

### 7.2 Target measure layers

| Layer | Purpose | Examples |
|---|---|---|
| Base measures | Direct source-column aggregations. | `[vNext Actual GBP Base]`, `[vNext Budget GBP Base]`, `[vNext Forecast GBP Base]`. |
| Semantic measures | Apply finance meaning, sign convention, or semi-additive rules. | `[vNext BS Closing Balance As Of Base]`, `[vNext Forecast Outturn GBP Base]`. |
| Presentation measures | Apply scaling/display behavior only where calculation groups cannot. | `[vNext Actual GBP Display]`. |
| Calculation groups | Apply reusable scenario/time/variance/unit transformations. | `cg_vNext_Time_Intelligence`, `cg_vNext_Display_Unit`. |
| UX helpers | Text labels, titles, colors, navigation helpers. | `[vNext Selected FY Label]`, `[vNext Current Filter Summary]`. |

### 7.3 Measure governance rules

- New measures must include description, display folder, format string, owner/approval status where appropriate, and test evidence.
- Measures replacing existing production measures should be introduced as `vNext` first.
- Report-visible measures must not have ambiguous names or hidden semantic assumptions.
- Deprecated measures must be hidden, assigned a replacement, and retained for an agreed deprecation window.
- Measures must not use invalid DAX patterns such as direct measure references in `CALCULATE` Boolean filters.

## 8. Calculation-group documentation

### 8.1 Existing calculation groups observed

| Calculation group | Inferred purpose | Governance requirement |
|---|---|---|
| `cg_Scenario` | Actual, Budget, Forecast, Outturn selection. | Document interaction with `dim_scenario`. |
| `cg_Variance` | Variance to plan/forecast/comparison. | Confirm denominator/sign conventions. |
| `cg_Time_Intelligence` | Fiscal current period, YTD, FY, prior, MoM, YoY. | Confirm fiscal-boundary behavior and additive-measure compatibility. |
| `cg_BS_Reporting` | Balance-sheet current/as-of/prior/movement logic. | Keep separate from additive time-intelligence. |
| `cg_Account_View` | PL, BS, charity BS account views. | Confirm interaction with account hierarchy and statement selectors. |
| `cg_Trend_Analysis` | Period/trend analysis behavior. | Review whether it overlaps with time-intelligence. |

### 8.2 vNext calculation groups

| Calculation group | Purpose | Precedence | Notes |
|---|---|---:|---|
| `cg_vNext_Scenario` | Scenario selector. | 10 | Should run before variance comparisons. |
| `cg_vNext_Variance` | Reusable variance calculations. | 15 | Can override scenario context for comparisons. |
| `cg_vNext_BS_Reporting` | Semi-additive balance-sheet reporting. | 25 | Use instead of generic YTD on closing balances. |
| `cg_vNext_Time_Intelligence` | Additive fiscal-period time intelligence. | 30 | Use for additive measures only unless approved. |
| `cg_vNext_Display_Unit` | Unit scaling and dynamic format strings. | 50 | Should run after semantic calculation groups to scale/format final numeric result. |

### 8.3 Calculation-group controls

- Every calculation item must have a business description and technical note.
- Every percentage item must use an explicit percentage dynamic format string.
- Unit-scaling calculation items must apply dynamic format strings that intentionally supersede base measure formats.
- Invalid combinations must be hidden through curated slicers, perspectives, or report design.
- Precedence changes require high-risk change approval and regression testing.

## 9. Metadata catalog standards

### 9.1 Object description template

Use this structure for all governed objects:

```text
Business definition: <business-friendly meaning>.
Technical notes: <source, DAX, relationship, filter, or calculation-group behavior>.
Owner/approval: <business or technical owner, if known>.
Caveats: <limitations, assumptions, or pending confirmations>.
```

### 9.2 Required metadata by object type

| Object type | Required metadata |
|---|---|
| Table | Role, grain, source, refresh cadence, owner, security sensitivity. |
| Column | Business meaning, data type, source mapping, visibility, sort-by column if applicable. |
| Measure | Business definition, DAX behavior, format string, display folder, total behavior, replacement/deprecation status. |
| Calculation group | Purpose, precedence, compatible measures, incompatible measures, interaction rules. |
| Calculation item | Business result, technical filter behavior, dynamic format string, examples. |
| Relationship | From/to columns, cardinality, active status, filter direction, role-playing/security note. |
| Role | Intended population, filter logic, owner, review cadence, test evidence. |
| Perspective | Persona, included objects, excluded objects, owner. |
| Hierarchy | Levels, sort order, ragged behavior, roll-up semantics. |

## 10. Data quality and reconciliation controls

| Control | Requirement |
|---|---|
| Source row counts | Compare source extract counts to model-loaded rows for facts and key dimensions. |
| Finance totals | Reconcile actual, budget, forecast, and balance totals to authoritative finance outputs by fiscal period. |
| Dimension completeness | Check unknown/unmapped account, cost centre, supplier, activity, job, and date keys. |
| Fiscal calendar | Validate continuous dates, fiscal periods, prior-period keys, and prior-year keys. |
| Forecast version | Validate latest/default version and version sorting. |
| RLS bridge | Validate no orphan users, no orphan cost centres, and expected access counts. |
| Calculation groups | Validate allowed combinations and blocked/hidden invalid combinations. |

## 11. Performance and capacity documentation

Each production release should record:

- dataset size and refresh duration;
- top slow visuals and measures;
- DAX Studio Server Timings for high-use reports;
- VertiPaq Analyzer summary for high-cardinality columns;
- before/after timings for significant DAX or relationship changes;
- capacity impact and known performance risks.

Performance risk areas for this model include:

- large measure surface area;
- repeated time/variance explicit measures;
- semi-additive BS calculations;
- disconnected selector-driven branching logic;
- RLS-enabled queries;
- high-cardinality text or transaction identifiers if visible/loaded unnecessarily.

## 12. Change control and release documentation

### 12.1 Change types

| Change | Change-control level |
|---|---|
| Documentation-only | Low risk; technical-owner approval. |
| Metadata-only | Low/medium risk; owner approval if visibility changes. |
| New additive measure | Medium risk; semantic-model owner approval. |
| Existing measure replacement | High risk; finance-owner approval and regression evidence. |
| Calculation-group change | High risk; precedence and interaction testing required. |
| Relationship change | High risk; model-wide regression required. |
| RLS/security change | Critical; security-owner and business-owner approval required. |
| Source schema or grain change | High/critical; source owner, data engineer, and finance approval required. |

### 12.2 Required release evidence

- Change request or ticket reference.
- Pull request and commit reference.
- Semantic-change log.
- Measure replacement register, where applicable.
- Regression test output.
- RLS test evidence.
- Performance evidence.
- Refresh test result.
- Business-owner approval for changed semantics.
- Rollback plan.
- Release notes.

### 12.3 Semantic-change log template

| Field | Value |
|---|---|
| Change ID |  |
| Release version |  |
| Date |  |
| Requester |  |
| Business owner |  |
| Technical owner |  |
| Object(s) changed |  |
| Previous behavior |  |
| New behavior |  |
| Expected impact | Equivalent / changed by design / pending validation |
| Test evidence |  |
| Approval |  |
| Rollback reference |  |

## 13. Operational support model

### 13.1 Support triage categories

| Category | Examples | Owner |
|---|---|---|
| Data freshness | Refresh failure, stale period, missing source file. | Data engineer / platform admin. |
| Data accuracy | Total mismatch, sign issue, missing account/cost centre. | Finance owner + semantic model owner. |
| Security | User sees too much/little data. | Security owner + platform admin. |
| Performance | Slow report, timeout, capacity pressure. | BI developer + platform admin. |
| Usability | Missing field, unclear label, slicer confusion. | Product owner + BI developer. |
| Change request | New measure, hierarchy, scenario, report need. | Product owner + semantic model owner. |

### 13.2 Support runbook minimum content

- How to identify current production version.
- How to verify last refresh status and duration.
- How to test RLS as a user.
- How to run core reconciliation queries.
- How to identify deprecated measures used by reports.
- How to escalate security or finance-definition issues.
- How to roll back to the previous release.

## 14. Model documentation maintenance cadence

| Documentation artefact | Owner | Cadence |
|---|---|---|
| Enterprise model documentation | Semantic model owner | Every release and quarterly review. |
| Measure catalog | BI developer / semantic model owner | Every semantic change. |
| Calculation-group guide | BI developer | Every calculation-group change. |
| RLS documentation | Security owner | Every role change and quarterly access review. |
| Relationship documentation | Semantic model owner | Every relationship change. |
| Release notes | Product owner / support owner | Every production release. |
| Decision records | Semantic model owner | Every significant design decision. |

## 15. Current assumptions and pending confirmations

| Area | Assumption | Required confirmation |
|---|---|---|
| Finance sign convention | Income, expenditure, asset, liability, and reserve signs are governed by account metadata. | Finance owner. |
| Forecast version | Selected/latest forecast version should be centrally controlled. | Finance planning owner. |
| Balance-sheet as-of logic | Period 0/brought-forward plus selected period logic is correct. | Finance owner. |
| Scenario behavior | `dim_scenario` and scenario calculation groups can coexist with clear responsibilities. | Semantic model owner. |
| Unit formatting | Display-unit calculation group should apply final dynamic unit formatting. | Finance owner and BI owner. |
| RLS | Cost-centre bridge is the authoritative access mechanism. | Security owner. |
| Deprecated measures | Existing measures can be hidden after usage monitoring and regression testing. | Product owner and semantic model owner. |

## 16. Enterprise readiness checklist

- [ ] Named business, technical, security, data engineering, platform, and support owners recorded.
- [ ] All visible tables documented.
- [ ] All visible columns documented or hidden if technical.
- [ ] All measures documented with definitions and technical notes.
- [ ] Calculation groups documented with precedence and interaction rules.
- [ ] RLS roles documented and tested.
- [ ] Relationship inventory documented and approved.
- [ ] Measure catalog and dependency graph produced.
- [ ] Deprecated measures hidden and tracked.
- [ ] Regression tests automated or repeatable.
- [ ] Performance baseline captured.
- [ ] Release checklist and semantic-change log adopted.
- [ ] Support runbook published.
- [ ] Governance review scheduled.
