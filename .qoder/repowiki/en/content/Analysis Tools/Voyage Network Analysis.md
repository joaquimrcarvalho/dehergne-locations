# Voyage Network Analysis

<cite>
**Referenced Files in This Document**   
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb)
- [dehergne_util.py](file://notebooks/dehergne_util.py)
- [jesuitas-nacionalidade-teste.txt](file://inferences/jesuitas-nacionalidade-teste.txt)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Voyage Network Reconstruction Methodology](#voyage-network-reconstruction-methodology)
3. [Querying Specific Voyages](#querying-specific-voyages)
4. [Data Enrichment and Attribute Integration](#data-enrichment-and-attribute-integration)
5. [Temporal Analysis and Year Extraction](#temporal-analysis-and-year-extraction)
6. [Data Export and Network Visualization](#data-export-and-network-visualization)
7. [Practical Examples and Analysis](#practical-examples-and-analysis)
8. [Common Issues and Validation Strategies](#common-issues-and-validation-strategies)
9. [Performance Considerations](#performance-considerations)
10. [Best Practices for Historical Network Analysis](#best-practices-for-historical-network-analysis)

## Introduction
The voyage network analysis tools documented in this report focus on the `wicki-viagens.ipynb` notebook, which reconstructs missionary voyage networks using Wicky's list of Jesuit travelers to India (1541-1758). This analysis provides a comprehensive framework for understanding the movement patterns of Jesuit missionaries across centuries, enabling researchers to explore historical migration patterns, geographic diversity, and temporal trends in missionary activities. The notebook serves as a powerful tool for transforming historical records into structured, analyzable data networks that can reveal insights into the global reach and organizational structure of the Jesuit order during the early modern period.

## Voyage Network Reconstruction Methodology
The `wicki-viagens.ipynb` notebook implements a systematic methodology for reconstructing voyage networks by integrating multiple data sources and applying rigorous data processing techniques. The process begins with establishing a connection to the Timelink database, which contains structured information about Jesuit missionaries and their voyages. The notebook leverages the `TimelinkNotebook` class to initialize the database connection and retrieve entity data with specific attributes. The core of the methodology involves querying individuals who traveled on specific voyages using the 'wicky-viagem' attribute, which corresponds to voyage identifiers from Wicky's original list. This attribute serves as the primary key for linking missionaries to specific voyages, enabling the reconstruction of complete voyage cohorts.

The methodology employs the `entities_with_attribute` function from the `timelink.pandas` module to retrieve comprehensive data about missionaries, including their names, group affiliations, and multiple attributes such as embarkation points, training locations, and national origins. This function allows for the simultaneous retrieval of multiple attribute types, creating a rich dataset for each missionary. The notebook processes this data to filter out non-travelers (those with groupname not equal to 'n') and ensures data integrity by validating that embarkation dates match voyage dates. This filtering process is crucial for maintaining the accuracy of the reconstructed networks, as it eliminates individuals who may be mentioned in relation to a voyage but did not actually participate in it.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1-L1729)

## Querying Specific Voyages
The notebook provides a systematic approach to querying individuals who traveled on specific voyages, with a particular focus on voyage '89' in 1657 as a case study. The process begins by setting the `voyage_of_interest` variable to the desired voyage identifier, which in the example is set to '89'. The notebook then uses the `entities_with_attribute` function to retrieve all individuals associated with this voyage, specifying the attribute type as 'wicky-viagem' and including additional attributes such as 'embarque' (embarkation), 'jesuita-entrada' (training location), and 'nacionalidade' (nationality). This comprehensive data retrieval creates a DataFrame containing detailed information about each traveler on the specified voyage.

To ensure the accuracy of the results, the notebook implements a date validation process that filters travelers based on the alignment of their embarkation dates with the voyage dates. This is accomplished by extracting the year from both the 'wicky-viagem.date' and 'embarque.date' fields and comparing them for equality. The code snippet `travellers['wicky-viagem.date.year'] = travellers['wicky-viagem.date'].str[:4]` extracts the year from the voyage date, while a similar operation is performed on the embarkation date. The subsequent filtering operation `travellers = travellers[travellers['wicky-viagem.date.year'] == travellers['embarque.date.year']]` ensures that only travelers whose embarkation year matches the voyage year are included in the final results. This validation step is critical for eliminating potential false positives that might arise from individuals being associated with a voyage in different years.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L139-L158)

## Data Enrichment and Attribute Integration
The notebook enriches voyage data with additional attributes to provide comprehensive context on missionary movements, focusing on three key dimensions: departure points ('embarque'), training locations ('jesuita-entrada'), and national origins ('nacionalidade'). These attributes are integrated into the analysis through the `more_attributes` parameter in the `entities_with_attribute` function call, which allows for the simultaneous retrieval of multiple attribute types. The 'embarque' attribute provides information about the embarkation points of missionaries, revealing the geographic origins of voyage cohorts and highlighting major departure ports. The 'jesuita-entrada' attribute indicates the training locations where missionaries received their education, offering insights into the institutional pathways within the Jesuit order. The 'nacionalidade' attribute documents the national origins of missionaries, enabling the analysis of geographic diversity within voyage cohorts.

The integration of these attributes creates a multidimensional dataset that supports sophisticated analysis of missionary networks. For example, the combination of embarkation points and national origins allows researchers to trace migration patterns and identify potential discrepancies between a missionary's country of origin and their point of departure. The training location data provides context for understanding the educational background and institutional affiliations of missionaries, which may influence their roles and assignments in the mission field. The notebook presents this enriched data in tabular format, with columns for embarkation point, name, nationality, training location, and voyage year, facilitating both quantitative analysis and qualitative interpretation of the voyage networks.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L146-L147)

## Temporal Analysis and Year Extraction
The notebook implements a systematic methodology for extracting and normalizing year information from date fields to enable temporal analysis of missionary movements. This process is essential for aligning voyage dates with embarkation dates and ensuring accurate cohort identification. The extraction is accomplished through string slicing operations on the date fields, specifically using the pandas string accessor `.str[:4]` to extract the first four characters of the date string, which correspond to the year. This approach assumes a consistent date format where the year is represented by four digits at the beginning of the date string.

The normalization process involves converting the extracted year strings to integer values using the `.astype(int)` method, which facilitates numerical comparisons and sorting. This conversion is demonstrated in the code snippet `travellers_all['wicky-viagem.date.year'] = travellers_all['wicky-viagem.date'].str[:4].astype(int)`, which creates a new column with normalized year values. The normalized year data enables various temporal analyses, including the grouping of voyages by year, the calculation of annual voyage frequencies, and the identification of temporal trends in missionary activities. The notebook uses these normalized year values to create time series visualizations that illustrate the evolution of voyage patterns over the 1541-1758 period, providing insights into the expansion and contraction of Jesuit missionary activities across centuries.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1620-L1621)

## Data Export and Network Visualization
The notebook generates publication-ready outputs and prepares data for network visualization through systematic data export processes. For publication-ready outputs, the notebook utilizes the pandas `to_markdown()` method to convert DataFrames into markdown-formatted tables that can be easily incorporated into reports and publications. This is demonstrated in the code snippet `table = travellers[['embarque','name','embarque.date.year']].to_markdown()`, which creates a markdown table containing embarkation points, names, and embarkation years for travelers on a specific voyage. The resulting markdown format ensures compatibility with various publishing platforms and maintains the structural integrity of the tabular data.

For network visualization, the notebook prepares data in formats suitable for graph analysis tools. While the specific export functions are not detailed in the provided code, the structured nature of the DataFrame output suggests compatibility with network analysis libraries such as NetworkX or Gephi. The comprehensive attribute data, including voyage identifiers, embarkation points, national origins, and training locations, provides the necessary edge and node properties for constructing complex network graphs. These networks can visualize relationships between missionaries, voyages, and geographic locations, revealing patterns of collaboration, migration routes, and institutional connections within the Jesuit order. The preparation of clean, well-structured data is a critical step in enabling effective network visualization and analysis.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L573-L574)

## Practical Examples and Analysis
The notebook provides practical examples that demonstrate the application of voyage network analysis to real historical data, with a focus on analyzing the composition of specific voyage cohorts and mapping geographic diversity. One prominent example is the analysis of voyage '89' in 1657, which reveals a diverse cohort of 23 missionaries embarking from two primary locations: Bom Jesus da Vidigueira and S. Lourenço das Almas. The analysis shows that the majority of travelers were from Portugal, but the cohort also included missionaries from Belgium, Austria, Germany, France, and Italy, highlighting the international character of Jesuit missionary activities. This geographic diversity is further illustrated by the training locations, which include Coimbra, Landsberg, Mechelen, Vienna, Naples, Genoa, and Rome, reflecting the global network of Jesuit educational institutions.

Another practical example involves the temporal analysis of voyage frequencies over time, which reveals patterns in missionary activities across the 1541-1758 period. The notebook groups voyages by year and counts the number of travelers per voyage, creating a time series that can be visualized to identify periods of increased or decreased missionary activity. This analysis can be used to correlate voyage patterns with historical events, such as political changes, religious developments, or colonial expansions. The practical examples demonstrate how the voyage network analysis tools can transform raw historical data into meaningful insights about the scale, scope, and evolution of Jesuit missionary activities, providing researchers with powerful tools for exploring historical patterns and relationships.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L208-L386)

## Common Issues and Validation Strategies
The voyage network analysis process encounters several common issues that require careful validation strategies to ensure data accuracy and reliability. One significant issue is ambiguous voyage references, where historical records may contain incomplete or conflicting information about voyage identifiers or dates. This can lead to difficulties in accurately linking missionaries to specific voyages, particularly when multiple voyages occurred in the same year. Another common issue is mismatched dates, where the recorded embarkation date does not align with the voyage date, potentially indicating errors in the historical records or complexities in the travel itineraries of missionaries.

To address these issues, the notebook implements several validation strategies. The primary strategy is the year-based filtering of travelers, which ensures that only individuals with matching embarkation and voyage years are included in the analysis. This approach helps to eliminate false positives that might arise from individuals being associated with a voyage in different years. Additionally, the notebook filters out non-travelers by checking the 'groupname' attribute, ensuring that only individuals with the value 'n' (indicating travelers) are included in the analysis. These validation strategies are complemented by the comprehensive attribute data, which allows for cross-verification of information across multiple dimensions, such as comparing national origins with embarkation points to identify potential discrepancies or anomalies in the data.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L151-L157)

## Performance Considerations
When joining multiple attribute types in the voyage network analysis, several performance considerations must be addressed to ensure efficient data processing and analysis. The integration of multiple attributes such as 'embarque', 'jesuita-entrada', and 'nacionalidade' increases the complexity of database queries and can impact performance, particularly when working with large datasets spanning multiple centuries of missionary activities. The notebook mitigates these performance challenges by leveraging the efficient data retrieval capabilities of the Timelink system and optimizing the query parameters to retrieve only the necessary data.

The use of pandas DataFrames for data manipulation provides significant performance advantages, as pandas is optimized for handling large datasets and complex operations. However, the notebook must balance the comprehensiveness of data retrieval with performance considerations, as including too many attributes or processing excessively large datasets can lead to memory constraints and slow execution times. The notebook addresses this by implementing targeted filtering operations early in the analysis process, reducing the dataset size before performing more computationally intensive operations. Additionally, the use of efficient string operations for year extraction and date validation minimizes processing overhead, ensuring that the analysis can be performed efficiently even with large historical datasets.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L146-L147)

## Best Practices for Historical Network Analysis
The voyage network analysis tools exemplify several best practices for conducting historical network analysis, particularly in the context of large-scale historical datasets. One key best practice is the systematic validation of data through multiple criteria, such as verifying that embarkation dates match voyage dates and filtering out non-travelers based on group affiliation. This approach ensures the accuracy and reliability of the reconstructed networks, which is essential for drawing valid historical conclusions. Another best practice is the integration of multiple data dimensions, including geographic, temporal, and institutional attributes, which enables comprehensive analysis of historical networks from multiple perspectives.

The notebook also demonstrates best practices in data presentation and export, generating publication-ready markdown tables and preparing data for network visualization. This focus on usability ensures that the analysis results can be effectively communicated to both academic and general audiences. Additionally, the notebook exemplifies the importance of transparent methodology, with clear documentation of the data processing steps and validation strategies. These best practices collectively contribute to the creation of robust, reliable, and insightful historical network analyses that can advance our understanding of complex historical phenomena such as global missionary movements and institutional networks.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1-L1729)