# Copilot Instructions for the Dehergne Répertoire Project

## Project Overview
This workspace is a **Timelink** project containing the transcription of Joseph Dehergne's "Répertoire des Jésuites de Chine". It uses the **Kleio** notation for data entry and **Python/Jupyter** for analysis.
- **Goal**: Analyze biographical data of Jesuits in China (1552-1800).
- **Core Library**: `timelink` (manages the database and Kleio file translation).
- **Other Libs**: `pandas`, `networkx`, `matplotlib`, `pyuca`.

## Architecture & Data Flow
1.  **Sources** (`sources/*.cli`):
    -   Primary data stored in Kleio format text files.
    -   Split by letter (e.g., `dehergne-a.cli`).
    -   **DO NOT** edit these files unless explicitly asked for data correction.
    -   Format: `n$` (person), `ls$` (attribute/link), `rel$` (relation).
    -   Metadata often in comments using specific tags (e.g., `@wikidata:`).

2.  **Processing** (Timelink):
    -   Kleio Server translates `.cli` -> Database (SQLite by default).
    -   Notebooks connect to the database via `timelink.notebooks.TimelinkNotebook`.

3.  **Analysis** (`notebooks/`):
    -   Jupyter notebooks for cleaning, querying, and visualizing; see `notebooks/README.md` for the full index.
    -   Key notebooks: `location-analysis-new.ipynb` (place extraction/enrichment), `chgis-tgaz.ipynb` (CHGIS Temporal Gazetteer matching), `dehergne_analysis.ipynb`, `jesuit-networks.ipynb`.
    -   Shared modules: `dehergne_util.py` (date conversion, Wikidata link extraction, TGAZ client), `temporal_semantics.py` + `copresence.py` (interval/co-presence analysis), `biographical_note.py` (bilingual biography generation).
    -   `timelink.pandas` is used to fetch data into DataFrames.

## Key Developer Workflows

### 1. Environment Setup
-   Initialize Timelink in notebooks:
    ```python
    from timelink.notebooks import TimelinkNotebook
    tlnb = TimelinkNotebook()
    # tlnb.print_info() # Optional check
    db = tlnb.db # Access the database connection
    ```

### 2. Data Querying
-   Use `timelink.pandas.entities_with_attribute` to fetch flat tables of specific attributes:
    ```python
    from timelink.pandas import entities_with_attribute
    df = entities_with_attribute(
        entity_type='person',
        the_type=['nascimento', 'morte', 'jesuita-entrada'], # Filter by attribute types
        column_name='value',
        show_elements=['extra_info', 'groupname'], # Additional columns
        db=db
    )
    ```
-   Avoid raw SQL unless necessary; prefer Timelink's abstraction which handles Kleio's graph structure/inheritance.

### 3. Data Ingestion
-   To update the database from `.cli` sources, use `notebooks/0-kleio-files.ipynb` or `notebooks/01-background-importer.ipynb`.
-   This requires the Kleio server (handled by `TimelinkNotebook`).

## Coding Conventions

### Python / Notebooks
-   **Imports**: Put project-specific configs or utils in `notebooks/dehergne_util.py` if reused.
-   **Dates**: Timelink dates are often strings (YYYYMMDD). Use `timelink.kleio.utilities.convert_timelink_date` or `dehergne_util.calc_age_at` for manipulation.
-   **Pathing**: Notebooks run from `notebooks/`. Use relative paths like `../inferences/` for output.

### Kleio Data (`.cli`)
-   **Wikidata Links**: Use the syntax `link$wikidata/"<url>"/id=<id>` or comment tag `@wikidata: <id>`.
-   **Dates**: Format `YYYYMMDD`. `00` for unknown day/month (e.g., `16000000`).
-   **Structure**: Hierarchy matters. `ls$` (attribute) is usually indented under `n$` (person).

## Project Structure
-   `sources/`: Raw `.cli` files (Human edited).
-   `notebooks/`: Analysis code.
-   `database/`: SQLite database location (usually).
-   `inferences/`: Output data, mapped locations, secondary derived files.
-   `identifications/`: Files related to entity resolution/identification.
