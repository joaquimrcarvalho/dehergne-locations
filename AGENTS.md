# Dehergne Répertoire - Timelink Project

This is a **Timelink** historical data transcription and analysis project containing the biographical data of Jesuit missionaries in China (1552-1800), transcribed from Joseph Dehergne's "Répertoire des Jésuites de Chine de 1552 à 1800" (1973).

## Project Overview

This repository contains:
- **Source transcriptions**: Biographical entries of Jesuit missionaries in Kleio notation format (`.cli` files)
- **Location identification**: Wikidata-linked place names for geographic analysis
- **Analysis notebooks**: Jupyter notebooks for data exploration and visualization
- **Database exports**: SQLite database backups and inference rules

The project is part of the research "Linking the West and the East: Reconstructing Itineraries and Networks between Europe and China through Macao" supported by Macao Polytechnic University (project RP/CIPFIC－01/2023).

## Technology Stack

### Core Technologies
- **Timelink**: Historical database management system (Kleio server version 12.9, build 588)
- **Kleio notation**: Formal language for historical source transcription (`.cli` files)
- **Python 3.12.11**: Primary programming language for analysis
- **Jupyter Notebooks**: Interactive data analysis environment
- **SQLite**: Default database backend
- **Git**: Version control for transcription and identification data

### Key Python Packages
```
timelink          # Core Timelink functionality for database management
openpyxl          # Excel file handling
jinja2            # Template processing
matplotlib        # Basic plotting
pygraphviz        # Graph visualization
networkx          # Network analysis
bokeh             # Interactive visualizations
scipy             # Scientific computing
pyuca             # Unicode collation
pandas            # Data manipulation (implied)
```

## Project Structure

```
├── sources/              # Primary data: Kleio transcription files (.cli)
│   ├── dehergne-a.cli    # Biographical entries starting with letter A
│   ├── dehergne-b.cli    # Biographical entries starting with letter B
│   ├── ...               # Files for each letter (a-z)
│   ├── dehergne-t.cli    # Main working file with structure info
│   └── *.xml, *.rpt      # Translation outputs (auto-generated)
├── structures/           # Kleio structure definition files
│   └── sources.str.json  # Structure configuration
├── notebooks/            # Jupyter notebooks for analysis
│   ├── 9-tutorial.ipynb              # Essential tutorial for Timelink
│   ├── 0-kleio-files.ipynb           # Kleio file management
│   ├── location-analysis.ipynb       # Geographic analysis
│   ├── jesuit-networks.ipynb         # Network analysis
│   └── dehergne_util.py              # Shared utility functions
├── identifications/      # Entity resolution/record linking exports
├── inferences/           # Derived data, mapped locations, analysis outputs
│   ├── *.xlsx            # Excel exports of location data
│   └── wikidata-references/  # Wikidata-linked location info
├── database/             # SQLite database backups
├── templates/            # Jinja2 templates for output generation
│   └── markdown/base/    # Templates for entity markdown rendering
├── extras/               # Documentation and utility scripts
│   ├── doc/              # Project documentation (Portuguese/English)
│   │   ├── Dehergne_transcription_format.md
│   │   ├── How_to_transcribe.md
│   │   ├── locations_how_to.md
│   │   └── sources_overview.md
│   └── scripts/          # Helper shell scripts
└── .vscode/              # VSCode settings for Kleio server integration
```

## Kleio Data Format

### Basic Structure
Kleio files (`.cli`) use a hierarchical notation with groups, elements, and aspects:

```
kleio$gacto2.str                    # Header with structure file
   fonte$dehergne-a/1973/Dicionário Biográfico
      lista$dehergne-notices-a/0/0/0

         n$António de Abreu/id=deh-antonio-de-abreu
            ls$nacionalidade/Portugal
            ls$jesuita-estatuto/Padre
            ls$jesuita-entrada/Goa/15791200
            ls$embarque/S. Valentim/16020325
            ls$wicky/486/16020325
            ls$jesuita-votos/4V/16040106
            ls$morte/Changchow, China/16110000
            ls$dehergne/1/obs=Full text of entry...
```

For details on the transcription of the original data see [extras/doc/Dehergne_transcription_format.md](../extras/doc/Dehergne_transcription_format.md)

### Key Group Types
- `n$` (nome): Person entity with unique ID
- `ls$` (life story): Person attributes (birth, death, positions, stays)
- `rel$`: Relations between people
- `referido$`: Referenced persons (mentioned in entries)
- `fonte$`: Source declaration
- `lista$`: List/act container

### Common Attribute Types (`ls$`)
- `nascimento` (birth): `ls$nascimento/PLACE/DATE`
- `morte` (death): `ls$morte/PLACE/DATE`
- `jesuita-entrada` (entry to Jesuits): `ls$jesuita-entrada/PLACE/DATE`
- `jesuita-votos` (vows): `ls$jesuita-votos/VOTE_TYPE/DATE`
- `jesuita-estatuto` (status): `ls$jesuita-estatuto/Padre|Irmão`
- `embarque` (embarkation): `ls$embarque/SHIP_NAME/DATE`
- `wicky` (Wicki number): `ls$wicky/NUMBER/DATE`
- `wicky-viagem` (fleet number): `ls$wicky-viagem/FLEET_NUMBER/DATE`
- `estadia` (stay): `ls$estadia/PLACE/DATE`
- `nacionalidade`: `ls$nacionalidade/COUNTRY`

### Date Format
Dates use `YYYYMMDD` format with `00` for unknown day/month:
- `16020325` = March 25, 1602
- `15791200` = December 1579 (day unknown)
- `16110000` = 1611 (month and day unknown)

### Wikidata Linking
Places are linked to Wikidata using comment syntax:
```
ls$estadia/Macau# @wikidata:Q14773/1660
ls$morte/Changchow, China#no rio @wikidata:Q57970/16110000
```

### Person Identification
Link multiple occurrences of the same person:
- `mesmo_que=ID` (same file)
- `xmesmo_que=ID` (cross-file reference)

## Development Workflow

### Environment Setup
1. Install VSCode with Python extension
2. Install Python 3.12.11
3. Install dependencies: `pip install -r notebooks/requirements.txt`
4. Install Docker (for Kleio server)

### Running Analysis Notebooks
```python
from timelink.notebooks import TimelinkNotebook
tlnb = TimelinkNotebook()
db = tlnb.db  # Access database connection
```

### Querying Data
```python
from timelink.pandas import entities_with_attribute

df = entities_with_attribute(
    entity_type='person',
    the_type=['nascimento', 'morte', 'jesuita-entrada'],
    column_name='value',
    show_elements=['extra_info', 'groupname'],
    db=db
)
```

### Updating Database from Sources
Use `notebooks/0-kleio-files.ipynb` or `notebooks/01-background-importer.ipynb` to process `.cli` files and update the database.

## Code Style Guidelines

### Python / Notebooks
- Place shared utilities in `notebooks/dehergne_util.py`
- Use `timelink.kleio.utilities.convert_timelink_date` for date manipulation
- Notebooks run from `notebooks/` - use relative paths like `../inferences/` for output
- Use `calc_age_at()` from `dehergne_util.py` for age calculations

### Kleio Transcription
- Keep person IDs unique with prefix `deh-` (e.g., `deh-antonio-de-abreu`)
- Add `-refN` suffix for referenced persons (e.g., `deh-antonio-de-abreu-ref1`)
- Use `@wikidata:Q12345` syntax in comments for place identification
- Use triple quotes `"""` for observations containing special characters
- Maintain hierarchical indentation (3 spaces per level)

### Location Naming
- Use commas for geographic hierarchy: `ls$estadia/Navalafuente, diocese de Toledo`
- Use parentheses for specific locations: `ls$estadia/Macau (Colégio de S. Paulo)`
- Add `#ILOC` comment if Wikidata ID is not available or ambiguous

## Key Files Reference

### Documentation (Portuguese/English)
- `extras/doc/Dehergne_transcription_format.md` - Complete transcription guide
- `extras/doc/How_to_transcribe.md` - General Kleio notation tutorial
- `extras/doc/locations_how_to.md` - Place name identification guide
- `extras/doc/sources_overview.md` - Sources cited by Dehergne
- `extras/doc/Concepts.md` - Timelink methodology concepts

### Analysis Entry Points
- `notebooks/9-tutorial.ipynb` - Start here for Timelink tutorial
- `notebooks/00-index.ipynb` - Index of available notebooks
- `notebooks/location-analysis.ipynb` - Geographic data analysis
- `notebooks/jesuit-networks.ipynb` - Network analysis of Jesuit connections

### Configuration
- `.kleio.json` - Kleio server configuration
- `.vscode/settings.json` - VSCode Kleio server settings
- `structures/sources.str.json` - Source structure definition

## License and Attribution

- **Timelink software**: MIT License (includes commercial usage)
- **Kleio transcriptions**: Copyright of respective transcribers
- **This repository**: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

## Support and Resources

- **Timelink Python package**: https://github.com/time-link/timelink-py
- **Main project**: Biographical data from Dehergne, Joseph. Répertoire des Jésuites de Chine de 1552 à 1800. Bibliotheca Instituti Historici S.I 37. Roma/Paris: Institutum historicum/Letouzey & Ané, 1973.
- **Chinese translation**: 在華耶穌會士列傳及書目補編 (Zhonghua Book Company, 1995)
- **Copilot instructions**: See `.github/copilot-instructions.md` for detailed coding guidelines

## Notes for AI Agents

1. **Primary language**: Documentation is mixed English/Portuguese; code comments are primarily English
2. **Data integrity**: Do not edit `.cli` source files unless explicitly requested for data correction
3. **Wikidata linking**: Location identification is a key ongoing task - use `@wikidata:QID` format
4. **Date handling**: Always use Timelink date utilities for date manipulation
5. **File paths**: Notebooks run from `notebooks/` directory; use relative paths accordingly
