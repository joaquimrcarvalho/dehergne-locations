# Jupyter Notebooks for Dehergne Data Analysis

This folder contains Jupyter notebooks for analyzing the Dehergne Jesuit mission data stored in Timelink. These notebooks provide various analytical capabilities for exploring the biographical and historical data of Jesuit missionaries in China from 1552 to 1800.

## Prerequisites

To use these notebooks you need to install VSCode, the Python interpreter and support libraries.

1. Install VSCode from https://code.visualstudio.com/download
2. Install the Python VSCode extension from https://marketplace.visualstudio.com/items?itemName=ms-python.python
3. After restarting VS Code and setting up your environment as instructed in step 2, install the support libraries:
   * Open a terminal in the menu `Terminal` -> `New terminal`
   * Type `pip install -r notebooks/requirements.txt` or if you are on a Windows terminal
     `pip install -r notebooks\requirements.txt`
4. Install Docker. See https://docs.docker.com/get-docker/

## Key Notebooks

### Getting Started
* **[9-tutorial.ipynb](9-tutorial.ipynb)** - Complete tutorial on using Timelink in notebooks (essential first read)
* **[0-vscode_setup.ipynb](0-vscode_setup.ipynb)** - VSCode setup guide
* **[00-index.ipynb](00-index.ipynb)** - Index of available notebooks
* **[check_version_of_timelink.ipynb](check_version_of_timelink.ipynb)** - Check Timelink version compatibility

### Data Import & Management
* **[0-kleio-files.ipynb](0-kleio-files.ipynb)** - Working with Kleio transcription files
* **[01-background-importer.ipynb](01-background-importer.ipynb)** - Background data importer
* **[1-receipts.ipynb](1-receipts.ipynb)** - Data import and management utilities
* **[database-overview.ipynb](database-overview.ipynb)** - Database schema and overview

### Analysis & Visualization
* **[dehergne_analysis.ipynb](dehergne_analysis.ipynb)** - Comprehensive data analysis
* **[location-analysis.ipynb](location-analysis.ipynb)** - Location-based analysis of Jesuit movements
* **[location-analysis-cleaned.ipynb](location-analysis-cleaned.ipynb)** - Cleaned version of location analysis
* **[nacionality_analysis.ipynb](nacionality_analysis.ipynb)** - Nationality distribution analysis
* **[who-was-where.ipynb](who-was-where.ipynb)** - Temporal and spatial analysis of Jesuit presence
* **[people-search-display.ipynb](people-search-display.ipynb)** - Search and display utilities for individuals

### Specialized Analyses
* **[jesuit-networks.ipynb](jesuit-networks.ipynb)** - Network analysis of Jesuit connections
* **[jesuit-entry.ipynb](jesuit-entry.ipynb)** - Analysis of Jesuit entry patterns into the order
* **[wicki-viagens.ipynb](wicki-viagens.ipynb)** - Voyage analysis based on Wicki's data
* **[residences.ipynb](residences.ipynb)** - Analysis of Jesuit residences and movements
* **[wikidata-linked-data.ipynb](wikidata-linked-data.ipynb)** - Wikidata integration and linked data analysis

### Utilities
* **[kleio-to-doc.ipynb](kleio-to-doc.ipynb)** - Convert Kleio data to documentation
* **[dehergne-locations-nodate.ipynb](dehergne-locations-nodate.ipynb)** - Location analysis without date constraints
* **[sandbox.ipynb](sandbox.ipynb)** - Experimental code and testing ground

## Project Context

This repository contains transcriptions of Joseph Dehergne's "Répertoire des Jésuites de Chine de 1552 à 1800", focusing on biographical data of Jesuit missionaries in China. The data is processed using the Timelink system for historical database management.

For more information about the project, see the main [README.md](../README.md).

## Requirements

The notebooks depend on the following Python packages:
* timelink - Core Timelink functionality
* openpyxl - Excel file handling
* jinja2 - Template processing
* matplotlib - Basic plotting
* pygraphviz - Graph visualization
* networkx - Network analysis
* bokeh - Interactive visualizations
* scipy - Scientific computing
* pyuca - Unicode collation

## Usage Tips

1. Start with [9-tutorial.ipynb](9-tutorial.ipynb) to understand the basic Timelink API and notebook functionality
2. Use [00-index.ipynb](00-index.ipynb) to explore available functionality
3. Check [database-overview.ipynb](database-overview.ipynb) to understand the data schema
4. Most notebooks will automatically set up Docker containers for the database and Kleio server

## Support

If you have problems, create an issue or start a discussion in https://github.com/time-link/timelink-py