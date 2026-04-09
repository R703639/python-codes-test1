# Ab Initio Graph: Compare Two Excel Tabs (Row-by-Row)

This Ab Initio graph compares two tabs (sheets) in an Excel workbook and outputs the row-level differences: **ADDED**, **REMOVED**, and **CHANGED** rows.

## Graph Flow

```
Read Tab 1 ──▶ Sort by key ──┐
                              ├──▶ Full Outer Join ──▶ Write Diff Output
Read Tab 2 ──▶ Sort by key ──┘    (compare transform)
```

## Files

| File | Description |
|------|-------------|
| `compare_excel_tabs.mp` | Graph design with component configuration |
| `compare_excel_tabs.transform` | Transform logic for the Join component |
| `excel_tab1.dml` | DML layout for Tab 1 (Sheet1) |
| `excel_tab2.dml` | DML layout for Tab 2 (Sheet2) |
| `diff_output.dml` | DML layout for the diff output |

## Setup Instructions

1. **Update DML files** — Edit `excel_tab1.dml` and `excel_tab2.dml` to match your actual Excel column names and types.

2. **Set the key column** — The `key_column` field is used to match rows between tabs. Replace it with your unique identifier (e.g., `employee_id`, `order_no`).

3. **Configure graph parameters** — Set `DATA_DIR` to point to your input Excel file location.

4. **Excel connector** — If you have the Ab Initio Excel connector (`m_excel_input`), use it directly. Otherwise, export each tab as CSV and use standard `Input File` components.

5. **Import into GDE** — Open the `.mp` file in GDE, create the components as described, wire them together, and attach the `.transform` and `.dml` files.

## Output Format

The diff output CSV contains:

| Column | Description |
|--------|-------------|
| `key_column` | Row identifier |
| `diff_status` | `ADDED`, `REMOVED`, or `CHANGED` |
| `changed_columns` | Comma-separated list of columns that differ |
| `tab1_values` | Pipe-separated values from Tab 1 |
| `tab2_values` | Pipe-separated values from Tab 2 |

## Example Output

```
key_column,diff_status,changed_columns,tab1_values,tab2_values
EMP001,CHANGED,"col_b,col_d",Alice|Sales|NY|50000|Active,Alice|Marketing|NY|55000|Active
EMP007,ADDED,,,,Bob|Engineering|SF|80000|Active
EMP003,REMOVED,,,Carol|HR|LA|60000|Inactive,
```
