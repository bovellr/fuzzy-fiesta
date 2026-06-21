# Power BI DAX Refactor Implementation Guide

## Purpose

This guide accompanies `refactored_measures_and_calculation_groups.dax` and provides the implementation approach for the proposed `sm_finance_core` semantic-model DAX refactor.

The script is intentionally delivered as a **vNext implementation layer**, not as destructive edits to the existing model. It introduces new reusable measures and calculation groups so the team can regression-test results before hiding, deprecating, or deleting current measures.

## Deliverables

- `docs/implementation/refactored_measures_and_calculation_groups.dax` contains the proposed updated DAX measures and calculation groups.
- This guide explains the implementation order, validation approach, semantic-change controls, and rollout plan.
- `POWERBI_SEMANTIC_MODEL_REVIEW.md` remains the business/technical review and recommendations document.

## Implementation principles

1. **Preserve behavior first.** Add `vNext` objects alongside current measures. Do not replace current report measures until comparison tests pass.
2. **Centralize reusable logic.** Base measures aggregate source columns; scenario, time, variance, BS, and display-unit behavior is applied through calculation groups where safe.
3. **Separate semantic and presentation logic.** Numeric base measures should not contain visual-only formatting or labels.
4. **Treat balance-sheet logic separately.** Use the BS reporting calculation group for semi-additive as-of behavior; avoid generic YTD on closing balances.
5. **Document inferred definitions.** Descriptions use “inferred pending confirmation” where business definitions were not supplied.

## Proposed object groups

| Object group | Purpose |
|---|---|
| `00 vNext Base Measures` | Additive source aggregations for GL, budget, forecast, workforce, procurement, invoice ledger, and AP validation facts. |
| `01 vNext Helpers` | Selected fiscal period, scenario, forecast version, and statement-unit helper logic. |
| `02 vNext Presentation` | Display/scaled wrappers over base values. |
| `03 vNext Scenario Measures` | Scenario-aware amount and outturn logic. |
| `04 vNext Balance Sheet` | Semi-additive closing, prior-period closing, and movement measures. |
| `05 vNext Variance Measures` | Explicit variance measures retained for compatibility and regression testing. |
| `06 vNext Date Role Measures` | Measures activating inactive date relationships for due/paid/received/created/receipt date roles. |
| `07 vNext Report UX` | Non-numeric report helper labels and summaries. |
| `cg_vNext_Scenario` | Scenario calculation items. |
| `cg_vNext_Variance` | Reusable variance calculation items. |
| `cg_vNext_Time_Intelligence` | Fiscal-period time calculations for additive measures. |
| `cg_vNext_BS_Reporting` | Balance-sheet semi-additive reporting calculations. |
| `cg_vNext_Display_Unit` | Optional calculation group for display-unit scaling after compatibility testing. |

## Recommended implementation order

### Phase 1: Prepare

1. Back up the PBIP project and semantic model.
2. Open the semantic model in Tabular Editor or another TMDL-aware editor.
3. Confirm the referenced columns exist in the target model. Static inspection found these important columns:
   - `fact_gl_balances[ActualGBP]`, `fact_gl_balances[BudgetGBP]`, `fact_gl_balances[ActualWTC]`, `fact_gl_balances[BudgetWTC]`
   - `fact_gl_forecasts[ForecastGBP]`, `fact_gl_forecasts[ForecastVersion]`
   - `fact_gl_transactions[SignedAmount]`, `fact_gl_transactions[Wtw]`, `fact_gl_transactions[Wtc]`, `fact_gl_transactions[Wtp]`, `fact_gl_transactions[Hct]`
   - `fact_purchase_orders[NetAmount]`
   - `fact_purchase_lines[NetValue]`, `fact_purchase_lines[InvoicedValue]`, `fact_purchase_lines[ReceivedValue]`, `fact_purchase_lines[OutstandingInvValue]`, `fact_purchase_lines[QtyOrdered]`, `fact_purchase_lines[QtyReceived]`, `fact_purchase_lines[QtyInvoiced]`
   - `fact_invoice_ledger[OriginalAmount]`, `fact_invoice_ledger[OutstandingAmount]`, `fact_invoice_ledger[PaidAmount]`
   - `fact_ap_po_validation[NetAmount]`
4. Confirm dimension column names used by the proposed logic, especially `dim_scenario[Scenario]`, `dim_forecast_version[ForecastVersion]`, `dim_accounts[AccountType]`, and `dim_cost_centres[CostCentreName]`. Adjust names if the production model uses different business columns.

### Phase 2: Add vNext measures

1. Add all `vNext` measures from the DAX script to the existing `_Measures` table.
2. Keep `vNext` display folders exactly as supplied during testing so reviewers can isolate new objects.
3. Do not point existing visuals to the new measures yet.
4. Run DAX query comparisons for each replacement candidate.

### Phase 3: Add calculation groups

Create the following calculation groups as new tables:

| Calculation group | Column | Precedence |
|---|---|---:|
| `cg_vNext_Scenario` | `Scenario Calc` | 10 |
| `cg_vNext_Variance` | `Variance Calc` | 15 |
| `cg_vNext_BS_Reporting` | `BS Reporting Calc` | 25 |
| `cg_vNext_Time_Intelligence` | `Time Calc` | 30 |
| `cg_vNext_Display_Unit` | `Display Unit Calc` | 50 |

Keep the existing calculation groups in place during testing. Do not expose both old and new calculation-group slicers to end users simultaneously.

### Phase 4: Regression testing

Run regression tests by fiscal period, fiscal year, account hierarchy, cost centre, scenario, and security role.

Minimum test matrix:

| Existing measure | vNext comparison |
|---|---|
| `[Actual GBP Base]` | `[vNext Actual GBP Base]` |
| `[Budget GBP Base]` | `[vNext Budget GBP Base]` |
| `[Forecast GBP Base]` | `[vNext Forecast GBP Base]` |
| `[Actual GBP (Display)]` | `[vNext Actual GBP Display]` |
| `[Budget GBP (Display)]` | `[vNext Budget GBP Display]` |
| `[Forecast GBP (Display)]` | `[vNext Forecast GBP Display]` |
| `[Budget Variance]` | `[vNext Budget Variance GBP Base]` |
| `[Budget Variance %]` | `[vNext Budget Variance %]` |
| `[BS Closing Balance (As-Of)]` | `[vNext BS Closing Balance As Of Base]` |
| `[BS Prior Period Closing]` | `[vNext BS Prior Period Closing Base]` |
| `[BS Movement MoM]` | `[vNext BS Movement Base]` |
| `[PL Forecast Outturn]` | `[vNext Forecast Outturn GBP Base]` or display-scaled equivalent |

### Phase 5: Report migration

1. Migrate one test report page first.
2. Replace explicit current/YTD/prior/variance measures with one base measure plus calculation-group selections where results match.
3. Keep deprecated measures hidden in a `99 Deprecated` display folder with descriptions identifying replacements.
4. After an agreed monitoring window, remove unused deprecated measures.

## Semantic-change log template

Use this template for every replacement:

| Field | Value |
|---|---|
| Existing object |  |
| vNext object |  |
| Intended behavior | Equivalent / changed by design |
| Reason for change |  |
| Test query |  |
| Test result | Pass / fail / accepted difference |
| Business owner approval |  |
| Migration date |  |

## Validation queries

Example DAX query pattern:

```DAX
EVALUATE
SUMMARIZECOLUMNS (
    dim_date[FiscalYearNumber],
    dim_date[FiscalMonthNumber],
    dim_cost_centres[CostCentreKey],
    "Old Actual", [Actual GBP Base],
    "New Actual", [vNext Actual GBP Base],
    "Difference", [Actual GBP Base] - [vNext Actual GBP Base]
)
```

For percentage measures, test zero, small-denominator, negative-denominator, blank, and total rows.

For RLS, test at least:

- one user with one cost centre;
- one user with multiple cost centres;
- one user with no assigned cost centre;
- one administrator/unrestricted user if applicable.

## Known implementation notes

- `vNext Pay % Income` uses `dim_accounts[AccountType]` values of `Income` and `Pay`. Confirm actual values before use.
- `vNext Selected Statement Unit Suffix` assumes `'Statement Unit'[Suffix]` exists. If the model uses a different suffix column, update the measure.
- Scenario calculation groups assume a compatible `dim_scenario[Scenario]` column. If the existing model uses a different scenario column or disconnected selector, adjust the calculation items.
- Forecast outturn logic should be validated against finance close and forecast-version rules.
- `cg_vNext_Display_Unit` should not be applied to ratios, percentages, text measures, or already-scaled display measures.

## Rollback plan

Because this implementation adds vNext objects rather than editing existing objects, rollback is straightforward:

1. Remove report references to vNext measures/calculation groups.
2. Hide or delete vNext objects.
3. Restore old calculation-group slicers if they were hidden.
4. Re-run smoke tests on original report pages.

## Definition of done

- All vNext objects are added with descriptions and display folders.
- Regression tests pass or business-approved semantic differences are documented.
- Invalid calculation-group combinations are hidden or blocked through curated report slicers.
- Deprecated measures are hidden and documented with replacement mappings.
- RLS behavior is validated for representative restricted users.
- Performance is checked with DAX Studio Server Timings and VertiPaq Analyzer before production release.

## Format-string precedence and unit scaling

Custom format strings should **not** globally supersede dynamic formatting when the business requirement is to apply selectable units such as base units, thousands, or millions.

Recommended rule:

1. **Base measures keep static custom formats** as safe defaults, for example currency, count, ratio, or percentage formatting.
2. **Calculation groups own unit-aware dynamic formatting** when they change the numeric scale of a selected measure.
3. **Dynamic format strings should supersede selected-measure custom formats only for the calculation item that changes units**, such as `Selected Statement Unit`, `Thousands`, or `Millions`.
4. **Percentage, ratio, text, and already-scaled display measures should preserve their own formats** and should not use the display-unit calculation group.
5. **The display-unit calculation group should have higher precedence than semantic calculation groups** so the final numeric result is scaled and formatted last.

In the supplied vNext script, `cg_vNext_Display_Unit` implements this pattern. `Base Units` and `Preserve Format / No Unit Override` keep `SELECTEDMEASUREFORMATSTRING()`, while `Selected Statement Unit`, `Thousands`, and `Millions` intentionally apply dynamic unit-specific format strings.

## Troubleshooting: PLACEHOLDER error in CALCULATE Boolean filters

If Power BI shows an error such as `A function 'PLACEHOLDER' has been used in a True/False expression that is used as a table filter expression`, check whether a measure has been used directly in a `CALCULATE` Boolean filter argument.

Invalid pattern:

```DAX
CALCULATE (
    MAX ( dim_date[PeriodKey] ),
    REMOVEFILTERS ( dim_date ),
    NOT ISBLANK ( [vNext Actual GBP Base] )
)
```

Correct pattern:

```DAX
MAXX (
    FILTER (
        ALL ( dim_date ),
        NOT ISBLANK ( CALCULATE ( [vNext Actual GBP Base] ) )
    ),
    dim_date[PeriodKey]
)
```

The corrected pattern uses `FILTER` to create a table expression and uses `CALCULATE` inside the row context to evaluate the measure for each date row. This is the pattern now used by `[vNext Latest Actual Fiscal Period Key]`.
