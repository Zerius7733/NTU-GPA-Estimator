# NTU GPA Estimator

A Python CLI tool to track and estimate NTU GPA by module and semester.  
It reads/writes GPA records in CSV, computes SGPA/CGPA from AU-weighted grades, and enriches module codes with titles using an NTU mods cache.

## Features

- Interactive CLI menu to add, review, and save GPA records.
- Supports both `Actual GPA.csv` and `Estimated GPA.csv` workflows.
- Computes:
  - `Points` from NTU letter grades.
  - cumulative `CGPA` (AU-weighted).
  - semester `SGPA` per AY group (e.g., `Y1S1`, `Y1S2`).
- Auto-sorts records by AY and module code for consistent output.
- Optional module title enrichment via `mods_cache.json` and NTU mods scraping script.

## Project Structure

- `GPA_Estimator.py`: main CLI app, GPA logic, CSV read/write.
- `fetch_mod_code.py`: fetches module titles from NTU mods and updates cache.
- `mods_cache.json`: local module-code to module-title cache.
- `Actual GPA.csv`: sample actual results dataset.
- `Estimated GPA.csv`: sample estimation/planning dataset.

## Grade Mapping

The app uses this NTU 5.0 scale mapping:

- `A+`, `A` = 5.0
- `A-` = 4.5
- `B+` = 4.0
- `B` = 3.5
- `B-` = 3.0
- `C+` = 2.5
- `C` = 2.0
- `D+` = 1.5
- `D` = 1.0
- `F` = 0.0

## Requirements

- Python 3.11+
- If using module scraping in `fetch_mod_code.py`:
  - `playwright`
  - `beautifulsoup4`
  - Playwright browser binaries

Install dependencies:

```bash
pip install playwright beautifulsoup4
playwright install
```

## Usage

Run from the repository root:

```bash
python GPA_Estimator.py
```

Flow:

1. Choose file:
   - `1` -> `Actual GPA.csv`
   - `2` -> `Estimated GPA.csv`
2. Use menu options:
   - `1` Update List
   - `2` Print List
   - `3` Delete Last
   - `4` Save with Module Name
   - `5` Save without Module Name
   - `6` Reload
   - `7` Exit

## CSV Format

Expected header:

```csv
AY,Module,AU,Grade,Points,SGPA,CGPA,Weight,Description
```

Example row:

```csv
Y2S1,SC2001,3,A,5.0,4.83,4.26,42,Algorithm Design & Analysis
```

Field notes:

- `AY`: semester key (`Y1S1` ... `Y4S2`).
- `AU`: integer academic units.
- `Grade`: NTU letter grade.
- `Points`: numeric value derived from grade mapping.
- `Weight`: running total AU count.
- `Description`: module title from cache/scrape.

## Notes and Limitations

- The tool is stateful and writes directly back to the selected CSV file.
- Scraping depends on NTU mods page structure; selector changes may break fetch logic.
- Network access is required when refreshing module titles.
- No automated tests are included yet.

## Future Improvements

- Add unit tests for GPA/SGPA/CGPA calculations.
- Add input validation and clearer error handling for invalid grades/menu input.
- Decouple scraping from main GPA flow to avoid runtime side effects.
- Add export summaries and trend plots.
