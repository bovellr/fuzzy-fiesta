# Azure DevOps Measures Register

## Purpose

`azure_devops_measures_register.csv` is an Azure DevOps-friendly register of the `sm_finance_core` measures. It is designed for upload, backlog triage, governance review, or conversion into Azure DevOps work items.

## Contents

- Current PBIP measures extracted from `_Measures.tmdl`: **335**
- Proposed vNext measures extracted from `docs/implementation/refactored_measures_and_calculation_groups.dax`: **56**
- Total register rows: **391**
- Current measures missing business definitions/descriptions in TMDL: **311**

## Azure DevOps import notes

The CSV includes Azure DevOps-oriented columns such as `Work Item Type`, `Title`, `Area Path`, and `Tags`, plus model governance fields such as measure name, definition, format string, display folder, lifecycle status, governance status, owner, dependencies, and validation status.

Recommended Azure DevOps import approach:

1. Import the CSV into a dedicated governance backlog or query it from Excel.
2. Keep `Work Item Type` as `Task` unless your process template uses a custom work item type.
3. Map `Title`, `Area Path`, and `Tags` to native Azure DevOps fields.
4. Keep the remaining columns as imported fields in Excel, a wiki table, or custom fields if your Azure DevOps process supports them.
5. Use `Lifecycle Status`, `Governance Status`, and `Validation Status` to prioritize review and regression testing.

## Required governance actions

- Confirm business definitions for rows where `Business Definition` starts with `Missing`.
- Validate current-vs-vNext replacement mappings before report migration.
- Update `Replacement Measure` once a current measure is superseded by a vNext measure.
- Attach DAX regression evidence to Azure DevOps tasks before changing lifecycle status to `Active` or `Deprecated`.
