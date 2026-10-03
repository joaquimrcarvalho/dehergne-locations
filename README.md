# Timelink source file repository

Transcription of the biographies of Joseph Dehergne, Répertoire des Jésuites de Chine de 1552 à 1800, Bibliotheca Instituti Historici S.I 37 (Roma : Paris: Institutum historicum ; Letouzey & Ané, 1973)

## First-time setup

The recommended environment for working with this repository is VS Code with the Python and Jupyter extensions. The notebooks use Timelink to translate the Kleio source files and to provide access to the database.

### Prerequisites

1. Install [VS Code](https://code.visualstudio.com/download).
2. Install the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) VS Code extensions.
3. Install Python 3.12 or a compatible recent Python version.
4. Install and start [Docker Desktop](https://docs.docker.com/get-docker/). Timelink uses Docker for the Kleio server and database services.

### Create the Python environment

Open the repository folder in VS Code, open **Terminal > New Terminal**, and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r notebooks/requirements.txt
```

On Windows, activate the environment with `.venv\\Scripts\\activate` instead of `source .venv/bin/activate`.

In VS Code, select the `.venv` interpreter when prompted, or use **Python: Select Interpreter** from the Command Palette. Select the same interpreter as the kernel when opening a notebook.

### Configure Timelink

1. Install the [Timelink VS Code extension](https://marketplace.visualstudio.com/items?itemName=time-link.timelink-vscode-web).
2. Open [notebooks/0-vscode_setup.ipynb](./notebooks/0-vscode_setup.ipynb) and run its cells in order. This discovers the local Kleio server settings and writes them to the workspace configuration.
3. If the notebook or a later notebook cannot connect after restarting VS Code, run the configuration cells in `0-vscode_setup.ipynb` again.

Do not copy Timelink paths or tokens from another checkout: they are specific to each computer and workspace.

### First notebook run

After setup, open [notebooks/9-tutorial.ipynb](./notebooks/9-tutorial.ipynb) for the basic workflow. To load or refresh the transcription database from the Kleio files, use [notebooks/0-kleio-files.ipynb](./notebooks/0-kleio-files.ipynb). The [notebooks/00-index.ipynb](./notebooks/00-index.ipynb) notebook provides an index of the remaining analyses.

## Sources included in this repository
### Dehergne, Joseph. Répertoire des Jésuites de Chine de 1552 à 1800. Bibliotheca Instituti Historici S.I 37. Roma : Paris: Institutum historicum ; Letouzey & Ané, 1973. ###

Biographical dictionary focussed on the french jesuit missionaries on China but including many others. Available at archive.org as PDF with embedded OCR. Also in text format, but the OCR in the text format version is of lower quality than the one embedded in the PDF.

This work is used as reference for names, dates and other bibliographical information by Brockey, Liam Matthew. Journey to the East: The Jesuit Mission to China, 1579-1724. Cambridge, Mass.: Belknap Press: An Imprint of Harvard University Press, 2008.

There is a Chinese translation, which is very helpful in what regards the Chinese names of missionaries and current names of places.

> Joseph, S. I. Dehergne. 在華耶穌會士列傳及書目補編. 第1版.., 中華書局, 1995.


#### Scope ####

Enumeration at the start of the _Repertoire_ (before p.1):
* those belonging to the vice-province, or to the French mission in China
* those, Chinese or not, that were in continental China (with the exception of Macau) [because "hundreds and hunderds" of those destined to Japan and other non-China missions stayed in Macau and studied at S.Paulo College, see p.XI ]).
* the Jesuit Superiors, bishops of Japan and Macau, Visitors (both of Japan and China), vice-provincials, and other superiors even if they never laid foot in China.
* Procurators (fr. procureurs, pt. procuradores) in charge of the mission in Macau and Goa.
* Those that died in China on their way to Japan.
* In smaller print those that were meant for China but died on their way or were detoured to other missions, the "macaistes" that have not worked in inland China and others who influenced, in various ways, the China mission.

The main target are French Jesuits missionaires in China. But includes all that were in mainland China.
Does not include those at Macau that were in transit to places other than continental China (for instance Japan).

### Aditional information ###

#### Identifying the fleet of the voyage from Lisbon to Goa

Dehergne includes information from:

* Wicki, J., & Boxer, C. R. (1967). Liste der Jesuiten-Indienfahrer, 1541-1758. Aschendorffsche.

This information relates to the voyage from Lisbon to Goa, India. In Wicki's work there is a sequential number for each fleet of ships that made the voyage in a given
year, and another sequentitial number each missionary abroad.

Dehergne keeps only the missionary numbers, not the fleet numbers. This prevents knowing
who travelled with whom. We recovered the fleet numbers from the Wicki list and
added to each entry. More information in the
transcription documentation [in portuguese](./extras/doc/Dehergne_transcription_format.md)

#### Identifying names

Current work on identifying place names is going
on in a fork:

    https://github.com/joaquimrcarvalho/dehergne-locations

We use wikidata links to identity the place names, e.g.

    ls$estadia/Goa# @wikidata:Q1171

#### Complementary sources

Whenever possible missing information was added, mostly
from reports "Cartas ânuas", using modern editions when available.

The main items added are place of entry in the Jesuits, places of
stay, and tasks ("jesuitas-tarefa").

Currently:
* Miguel Rodrigues Lourenço & António Guimarães Pinto. (2023). Cartas ânuas da Cochinchina (1619-1635). Centro Cientifico e Cultural de Macau; Universidade de Macau.

### Credits ###

The identification of place names and reconstruction of networks of places and people was supported by Macao Polytechnic University, through project RP/CIPFIC－01/2023.


## License

Timelink link software is distributed under a MIT license that includes usage for commercial purposes.

Kleio transcriptions of historical sources are not distributed under the same license.

Each Kleio transcription file is copyright of the person or persons that produced the transcription.

(c) Joaquim Carvalho, Macao Polytechnic University

_Files in this repository are covered by the Creative Commons
Attribution-NonCommmercial-ShareAlike 4.0 International_

[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
