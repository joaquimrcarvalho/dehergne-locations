Place here CSV files single column with wikidata ids.
- locations_names_wikidata.csv example of file with wikidata ids
- locations_wikidata_info.xlsx - file with info fetched from wikidata

The notebook "wikidata-linked-data.ipynb" will read these files and fetch the data from wikidata updating an Excel file with the results.

The name of the file with the wikidata information is set in notebooks/dehergne_util.py, variable `locations_wikidata_info_file`