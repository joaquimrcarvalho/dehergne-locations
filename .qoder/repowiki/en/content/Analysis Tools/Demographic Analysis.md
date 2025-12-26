# Demographic Analysis

<cite>
**Referenced Files in This Document**   
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb)
- [dehergne_util.py](file://notebooks/dehergne_util.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Nationality Distribution Analysis](#nationality-distribution-analysis)
3. [Data Retrieval and Filtering](#data-retrieval-and-filtering)
4. [Exporting Nationality Data](#exporting-nationality-data)
5. [Chronological Analysis of Missionary Departures](#chronological-analysis-of-missionary-departures)
6. [Data Validation and Quality Assurance](#data-validation-and-quality-assurance)
7. [Performance Considerations](#performance-considerations)
8. [Best Practices for Demographic Reporting](#best-practices-for-demographic-reporting)

## Introduction
The `nacionality_analysis.ipynb` notebook provides a comprehensive framework for analyzing the demographic composition of Jesuit missionaries based on their nationality. This document details the methodology, functionality, and analytical capabilities of the notebook, focusing on its ability to query, process, and visualize nationality data from person entities. The analysis centers on the 'nacionalidade' attribute, enabling researchers to understand recruitment patterns, geographical origins, and temporal trends in missionary deployment.

## Nationality Distribution Analysis
The notebook begins by analyzing the distribution of nationalities among Jesuit missionaries using the `attribute_values` function from the `timelink.pandas` module. This function queries the database to retrieve frequency counts of all nationality values across person entities. The analysis reveals that Portugal is the most represented nationality with 431 individuals, followed by France (184), China (177), and Italy (125). The data includes a diverse range of nationalities, from major European countries to regions in Asia and beyond, reflecting the global reach of the Jesuit missions.

The analysis generates summary statistics that provide insights into the demographic composition of the missionary population. These statistics are presented in tabular format, showing the count of individuals for each nationality. The notebook also computes percentage distributions, enabling researchers to understand the relative proportions of different national groups within the overall population. For example, Portuguese missionaries constitute the largest demographic segment, representing a significant majority of the total missionary population.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L318-L324)

## Data Retrieval and Filtering
The notebook retrieves detailed records of individuals with nationality attributes using the `entities_with_attribute` function. This function queries the database for person entities that have the 'nacionalidade' attribute, returning a comprehensive dataset that includes various attributes such as name, groupname, and additional information. A critical filtering step is applied to include only primary individuals by filtering for `groupname='n'`, which excludes references, family members, and other non-primary entities.

The filtering process ensures that the analysis focuses on actual missionaries rather than peripheral figures mentioned in the records. This approach enhances the accuracy and relevance of the demographic analysis by concentrating on individuals who were directly involved in missionary activities. The filtered dataset provides a clean and focused view of the missionary population, enabling more precise demographic studies and trend analysis.

The notebook also demonstrates the ability to retrieve multiple attributes simultaneously, such as combining nationality data with birth information ('nascimento') or voyage details ('wicky'). This multi-attribute querying capability allows for more complex analyses that can correlate nationality with other biographical or historical data points, providing richer insights into the lives and movements of the missionaries.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L398-L414)

## Exporting Nationality Data
The notebook includes functionality for exporting nationality data to Excel files, facilitating further analysis and visualization outside the notebook environment. Using pandas' `to_excel` method, the notebook exports the complete dataset of individuals with nationality attributes to an Excel file named `paises_pessoas_n.xlsx`. This export includes all relevant columns and preserves the structured format of the data, making it accessible for researchers who prefer to work with spreadsheet applications.

In addition to exporting raw data, the notebook generates summary statistics and exports them to a separate Excel file named `paises_totais_n.xlsx`. This summary file contains aggregated data grouped by nationality, providing a concise overview of the demographic distribution. The export functionality supports demographic reporting by enabling researchers to share findings, create visualizations, and perform additional analyses using familiar tools like Microsoft Excel or Google Sheets.

The export process is designed to be straightforward and efficient, requiring minimal configuration. Researchers can easily modify the export paths or file names to suit their organizational needs. This functionality enhances the usability of the analysis by bridging the gap between computational analysis and traditional research workflows, allowing for seamless integration of data across different platforms and tools.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L432-L433)
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L650-L651)

## Chronological Analysis of Missionary Departures
The notebook supports chronological analysis of missionary departures by combining nationality data with voyage information from Wicky's lists. This integration enables researchers to track changes in recruitment patterns over time and analyze the temporal distribution of missionary deployments. The analysis involves extracting the year of departure from the 'wicky.date' attribute and grouping the data by decade to identify trends in missionary movements.

The chronological analysis reveals patterns in the timing of missionary departures, showing how recruitment and deployment varied across different periods. For example, the data can show whether certain nationalities were more prominently recruited during specific decades or how the overall volume of missionary departures changed over time. This temporal perspective adds a dynamic dimension to the demographic analysis, allowing researchers to understand not just who the missionaries were, but when they were active and how their deployment evolved.

The notebook demonstrates this functionality by creating a dataset that combines nationality information with departure dates, then grouping the results by country and decade. This grouped data provides a clear visualization of recruitment trends, such as the peak periods for Portuguese or French missionaries. The analysis can be extended to examine correlations between nationality and specific historical events or geopolitical changes that may have influenced missionary activities.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L848-L862)
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L1228-L1240)

## Data Validation and Quality Assurance
The notebook addresses common data quality issues such as inconsistent nationality spellings and missing data through systematic validation processes. The analysis includes strategies for identifying and handling incomplete or ambiguous records, ensuring the reliability of the demographic findings. For instance, the notebook uses data imputation techniques to handle missing departure dates by replacing NaN values with default values like '0000', allowing for consistent chronological analysis.

The data validation process also involves examining the consistency of nationality entries across different records. By analyzing the frequency distribution of nationality values, researchers can identify potential spelling variations or transcription errors that may affect the accuracy of the analysis. The notebook's approach to data quality emphasizes transparency and reproducibility, documenting the steps taken to clean and prepare the data for analysis.

Additionally, the notebook leverages the `convert_timelink_date` function from the `dehergne_util.py` module to ensure consistent date formatting across different attributes. This utility function helps standardize date representations, reducing the risk of errors in chronological analyses. The integration of custom utility functions demonstrates a proactive approach to data quality, addressing potential issues at the processing stage rather than relying solely on manual correction.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L1232-L1234)
- [dehergne_util.py](file://notebooks/dehergne_util.py#L5-L8)

## Performance Considerations
When grouping large datasets, the notebook employs efficient data processing techniques to optimize performance. The use of pandas' groupby operations is carefully managed to minimize computational overhead, particularly when dealing with extensive datasets containing hundreds or thousands of records. The notebook demonstrates best practices for handling large-scale demographic data by leveraging pandas' built-in optimization features and memory management capabilities.

The performance considerations extend to the export functionality, where the notebook efficiently writes data to Excel files without excessive memory consumption. By processing data in chunks and using optimized file writing methods, the notebook ensures that performance remains stable even with large datasets. These performance optimizations are crucial for maintaining responsiveness and usability, especially when researchers need to iterate on their analyses or work with multiple large datasets simultaneously.

The notebook also includes configuration settings such as `pd.set_option('display.max_rows', 550)` to manage the display of large datasets, preventing performance issues related to rendering excessive data in the notebook interface. These settings strike a balance between usability and performance, allowing researchers to work with comprehensive datasets while maintaining a responsive and efficient analysis environment.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L403-L404)
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L1238-L1239)

## Best Practices for Demographic Reporting
The notebook exemplifies best practices for demographic reporting by combining rigorous data analysis with clear documentation and reproducible methods. The structured approach to data retrieval, filtering, and analysis ensures that findings are based on accurate and well-defined criteria. The inclusion of summary statistics, percentage calculations, and chronological trends provides a comprehensive view of the demographic landscape, supporting robust scholarly interpretation.

The integration of data export functionality promotes transparency and collaboration by enabling researchers to share their findings in accessible formats. The use of standardized file formats like Excel facilitates peer review and collaborative research, allowing multiple scholars to work with the same data. The notebook's emphasis on data quality and validation further enhances the credibility of the demographic reporting, ensuring that conclusions are based on reliable and well-processed data.

By documenting the analytical workflow and providing clear examples of data processing steps, the notebook serves as a model for reproducible research in historical demography. The combination of computational analysis and traditional scholarly methods creates a powerful framework for understanding the complex demographic patterns of Jesuit missionary activities, setting a high standard for future research in this field.

**Section sources**
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L1238-L1240)
- [nacionality_analysis.ipynb](file://notebooks/nacionality_analysis.ipynb#L2568-L2574)