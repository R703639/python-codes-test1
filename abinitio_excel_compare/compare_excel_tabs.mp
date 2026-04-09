// ============================================================
// Ab Initio Graph: compare_excel_tabs.mp
// Row-by-Row Comparison of Two Tabs in an Excel File
// ============================================================
//
// GRAPH LAYOUT (Pseudo-GDE representation)
// =========================================
//
//   ┌─────────────────────┐     ┌──────────────┐
//   │  Read Excel Tab 1   │────▶│   Sort by     │──┐
//   │  (Input File)       │     │   key_column  │  │
//   └─────────────────────┘     └──────────────┘  │
//                                                  │   ┌──────────────────┐     ┌──────────────────┐
//                                                  ├──▶│  Join (Full      │────▶│  Write Output    │
//                                                  │   │  Outer Join on   │     │  (CSV / Excel)   │
//   ┌─────────────────────┐     ┌──────────────┐  │   │  key_column)     │     └──────────────────┘
//   │  Read Excel Tab 2   │────▶│   Sort by     │──┘   │                  │
//   │  (Input File)       │     │   key_column  │      │  Transform:      │
//   └─────────────────────┘     └──────────────┘      │  compare_excel   │
//                                                      │  _tabs.transform │
//                                                      └──────────────────┘
//
// ============================================================
// COMPONENT DETAILS
// ============================================================
//
// ────────────────────────────────────────────────────────────
// COMPONENT 1: Read Excel Tab 1
// ────────────────────────────────────────────────────────────
// Type:          Input File (or m_excel_input if using Excel connector)
// File:          ${DATA_DIR}/input_workbook.xlsx
// Sheet:         Sheet1
// DML:           excel_tab1.dml
// Parameters:
//   - HEADER_ROW = 1
//   - START_DATA_ROW = 2
//
// ────────────────────────────────────────────────────────────
// COMPONENT 2: Read Excel Tab 2
// ────────────────────────────────────────────────────────────
// Type:          Input File (or m_excel_input if using Excel connector)
// File:          ${DATA_DIR}/input_workbook.xlsx
// Sheet:         Sheet2
// DML:           excel_tab2.dml
// Parameters:
//   - HEADER_ROW = 1
//   - START_DATA_ROW = 2
//
// ────────────────────────────────────────────────────────────
// COMPONENT 3: Sort Tab 1
// ────────────────────────────────────────────────────────────
// Type:          Sort
// Sort Key:      key_column (ascending)
// Input DML:     excel_tab1.dml
// Output DML:    excel_tab1.dml
//
// ────────────────────────────────────────────────────────────
// COMPONENT 4: Sort Tab 2
// ────────────────────────────────────────────────────────────
// Type:          Sort
// Sort Key:      key_column (ascending)
// Input DML:     excel_tab2.dml
// Output DML:    excel_tab2.dml
//
// ────────────────────────────────────────────────────────────
// COMPONENT 5: Join (Full Outer Join)
// ────────────────────────────────────────────────────────────
// Type:          Join
// Join Type:     Full Outer Join
// Join Key:      key_column
// Input 0 DML:   excel_tab1.dml  (from Sort Tab 1)
// Input 1 DML:   excel_tab2.dml  (from Sort Tab 2)
// Output DML:    diff_output.dml
// Transform:     compare_excel_tabs.transform
//
// ────────────────────────────────────────────────────────────
// COMPONENT 6: Write Output
// ────────────────────────────────────────────────────────────
// Type:          Output File
// File:          ${DATA_DIR}/diff_output.csv
// DML:           diff_output.dml
// Format:        Delimited (comma-separated)
//
// ============================================================
// GRAPH PARAMETERS (set in .pset or GDE Parameter tab)
// ============================================================
//
// DATA_DIR     = /path/to/your/data
// AB_HOME      = ${AB_HOME}
//
// ============================================================
// NOTES
// ============================================================
//
// 1. Both tabs must share the same column structure.
//    Update the .dml files if your columns differ.
//
// 2. The key_column is used to match rows between tabs.
//    Choose a unique identifier (e.g., ID, employee_no).
//
// 3. The transform uses out :: abort to skip identical rows,
//    so only differences appear in the output.
//
// 4. If your Excel file requires the Ab Initio Excel connector
//    (m_excel_input), ensure the connector is installed.
//    Otherwise, convert tabs to CSV first and use Input File.
//
// 5. Output shows:
//    - ADDED:   rows in Tab 2 not in Tab 1
//    - REMOVED: rows in Tab 1 not in Tab 2
//    - CHANGED: rows in both tabs with different column values
//      (changed_columns field lists which columns differ)
//
// ============================================================
