---
name: kleio-files
description: "Use when working with a Timelink/Kleio repository to check database status, list Kleio files and their translation/import status, translate and import changed sources, or inspect translation and import errors."
user-invocable: true
---

# Kleio Files

Use this skill to perform the basic operations from `notebooks/0-kleio-files.ipynb` without requiring the user to open the notebook.

## Preconditions

Before running Timelink code, establish the repository root and validate the workspace:

1. Start in the user's current directory and walk up through its parents until finding a directory containing all three directories `notebooks`, `sources`, and `structures`.
2. If no such directory exists, stop and report that this does not appear to be a Dehergne/Kleio repository. Do not run against an arbitrary directory.
3. Confirm that `notebooks/requirements.txt` exists. The skill uses paths relative to the discovered repository root.
4. Check that Docker is installed and available with `docker info`. Timelink may download its Docker image on the first run, so the first operation can take several minutes. If Docker is installed but not running, ask the user to start Docker Desktop and retry.

## Python environment

Prefer the repository's `.venv`:

- macOS/Linux: `.venv/bin/python`
- Windows: `.venv\\Scripts\\python.exe`

If `.venv` is absent, or its Python cannot import `timelink`, check for another selected Python interpreter and test it with:

```bash
python -c "import timelink; print(timelink.__file__)"
```

If no usable interpreter is available, explain the problem and offer to create and populate the repository environment. Do not install anything without the user's confirmation. On confirmation, run the platform-appropriate commands from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r notebooks/requirements.txt
```

On Windows, use `.venv\\Scripts\\python.exe` in place of `.venv/bin/python`. If an environment exists but dependencies are missing, offer to run its Python with `-m pip install -r notebooks/requirements.txt`.

Do not copy Timelink server paths or tokens from another checkout. `TimelinkNotebook` discovers the local configuration. Use the selected interpreter for every operation, rather than relying on the shell's active environment.

## Initialize Timelink

Run the following from the repository root in a short-lived Python process. Keep the object alive for all operations in that process:

```python
from timelink.notebooks import TimelinkNotebook

tlnb = TimelinkNotebook(
    kleio_image="kleio-server",
    kleio_version="latest",
    kleio_update=True,
)
tlnb.print_info()
```

If the user only needs a read-only status and an existing Timelink server is available, initialization may attach to that server according to the local project configuration. If initialization fails, report the concrete error and check Docker, the selected interpreter, and the workspace's Timelink settings before retrying.

## Operations

Run only the operation requested by the user. When several operations are requested, initialize once and run them in the order below. Display file tables sorted by `name`.

### Database status

Show the row count for each database table:

```python
tlnb.table_row_count_df()
```

Also include `tlnb.print_info()` output when it has not already been shown, so the user can identify the database and Kleio server in use.

### List Kleio files and status

Retrieve the file status table and show these columns when present:

```python
kleio_files = tlnb.get_kleio_files(match_path=True)
columns = [
    "name", "status", "errors", "warnings",
    "import_status", "import_errors",
]
print(kleio_files[[column for column in columns if column in kleio_files.columns]]
      .sort_values("name")
      .to_string(index=False))
```

Interpret `import_status` as follows:

- `I`: imported
- `E`: imported with errors
- `W`: imported with warnings and no errors
- `N`: not imported
- `U`: translation updated and needs reimport

### Translate and update as needed

The normal update operation translates changed Kleio files and imports the resulting data:

```python
tlnb.db.update_from_sources(
    path="",
    with_import_errors=True,
    match_path=True,
)
kleio_files = tlnb.get_kleio_files(match_path=True)
print(kleio_files.sort_values("name").to_string(index=False))
```

Before doing this, tell the user that it can change the local database. If the user asks to force all translations to be regenerated, or there was a Kleio server update, first run:

```python
tlnb.kleio_server.translation_clean("", recurse="yes")
```

Then run `update_from_sources` again. Treat a clean translation as a potentially expensive operation and obtain confirmation before doing it.

### Check translation errors

Use the import-status dataframe to identify files whose Kleio translation reports errors:

```python
imported_files_df = tlnb.get_import_status(match_path=True)
translation_errors = imported_files_df[imported_files_df["errors"] > 0]

if translation_errors.empty:
    print("No translation errors found")
else:
    print(translation_errors[
        ["path", "name", "errors", "warnings", "import_status",
         "import_errors", "import_warnings"]
    ].sort_values("name").to_string(index=False))
    for file_number in translation_errors.index.unique():
        print(tlnb.get_translation_report(imported_files_df, file_number))
```

If the dataframe does not contain one of the optional report columns, display only columns that exist instead of failing the whole operation.

### Check import errors

Identify files with database import errors and print each import report:

```python
imported_files_df = tlnb.get_import_status(match_path=True)
import_errors = imported_files_df[imported_files_df["import_errors"] > 0]

if import_errors.empty:
    print("No import errors found")
else:
    print(import_errors[
        ["import_status", "import_errors", "import_warnings", "name",
         "imported", "errors", "warnings", "path"]
    ].sort_values("name").to_string(index=False))
    for file_number in import_errors.index:
        row = imported_files_df.loc[file_number]
        print(f"File: {row['name']} - {row['path']}")
        print(tlnb.get_import_rpt(
            imported_files_df,
            rows=file_number,
            match_path=True,
        ))
```

For one named file, use its Kleio filename with `tlnb.get_import_rpt('filename.cli')` when supported by the installed Timelink version.

## Reporting results

Always state:

- the repository root used;
- the Python interpreter used;
- whether Docker was available;
- the operation performed;
- any files with translation errors, import errors, warnings, or status `N`/`U`;
- whether the database was modified.

Do not edit `.cli` source files as part of this skill. If a translation report points to a source error, show the file and report details and ask before making any data correction.
