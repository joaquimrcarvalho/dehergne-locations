# Analysis Utilities

<cite>
**Referenced Files in This Document**   
- [dehergne_util.py](file://notebooks/dehergne_util.py)
- [dehergne_analysis.ipynb](file://notebooks/dehergne_analysis.ipynb)
- [location-analysis.ipynb](file://notebooks/location-analysis.ipynb)
- [residences.ipynb](file://notebooks/residences.ipynb)
- [jesuit-entry.ipynb](file://notebooks/jesuit-entry.ipynb)
- [dehergne-locations-nodate.ipynb](file://notebooks/dehergne-locations-nodate.ipynb)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Utility Functions](#core-utility-functions)
3. [Detailed Function Analysis](#detailed-function-analysis)
4. [Integration with Analysis Notebooks](#integration-with-analysis-notebooks)
5. [Error Handling and Common Issues](#error-handling-and-common-issues)
6. [Performance Considerations](#performance-considerations)
7. [Best Practices and Extensions](#best-practices-and-extensions)
8. [Conclusion](#conclusion)

## Introduction
The `dehergne_util.py` module provides a collection of utility functions designed to support data processing and enrichment in the analysis of historical Jesuit records. These utilities are essential components of the data analysis pipeline, enabling researchers to extract meaningful information from complex textual data, compute temporal relationships, and link entities to external knowledge bases. The module serves as a bridge between raw data and analytical insights, offering reusable functions that standardize common operations across multiple notebooks. By encapsulating complex parsing logic and date calculations, these utilities enhance code readability, maintainability, and consistency across the research project.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L1-L152)

## Core Utility Functions
The `dehergne_util.py` module contains four primary utility functions that address key data processing challenges in the analysis of historical records: `calc_age_at` for temporal calculations, `get_linked_entity_id` for extracting identifiers from structured comments, `get_wikidata_id` for parsing Wikidata links from entity observation fields, and `extract_coordinates` for geolocation data extraction. These functions work together to transform unstructured textual data into structured, analyzable information. The utilities are designed with robust error handling, accepting `None` values and malformed inputs gracefully, and returning appropriate default values when data is missing. This design philosophy ensures that data processing pipelines can continue even when encountering incomplete or inconsistent records, which is common in historical datasets.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L12-L152)

## Detailed Function Analysis

### calc_age_at Function
The `calc_age_at` function computes the number of years between two dates, primarily used to calculate the age of Jesuits at significant life events such as entry into the order, ordination, or death. The function accepts two date parameters and returns the integer difference in years. It first checks for `None` values and returns `None` if either date is missing. The function leverages the `timelink.kleio.utilities.convert_timelink_date` utility to convert Timelink date strings into Python `datetime` objects, ensuring compatibility with the project's date formatting conventions. The age calculation uses a 365.25-day year to account for leap years, providing a more accurate approximation than a simple 365-day calculation. This function is critical for demographic analysis, enabling researchers to study patterns in the ages of Jesuits at various career milestones.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L12-L28)
- [dehergne_analysis.ipynb](file://notebooks/dehergne_analysis.ipynb#L704)
- [jesuit-entry.ipynb](file://notebooks/jesuit-entry.ipynb#L4332)

### get_linked_entity_id Function
The `get_linked_entity_id` function extracts identifiers from structured comments that follow the pattern `@<provider>: <id>`, where `<provider>` is the name of a linked data provider (e.g., 'wikidata', 'geonames') and `<id>` is the identifier of the linked entity. This function uses regular expressions to search for the specified provider pattern within a comment string and returns the corresponding identifier. It accepts three parameters: the comment string, the linked data provider name, and an optional value to return if no link is found (defaulting to `None`). The function handles `None` input gracefully and uses `re.escape()` to safely incorporate the provider name into the regular expression pattern. This utility is essential for linking entities in the dataset to external knowledge bases, enabling data enrichment and cross-referencing.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L31-L60)
- [location-analysis.ipynb](file://notebooks/location-analysis.ipynb#L501)
- [jesuit-entry.ipynb](file://notebooks/jesuit-entry.ipynb#L676)

### get_wikidata_id Function
The `get_wikidata_id` function specifically targets Wikidata links within entity observation fields, returning both a cleaned comment (with Wikidata references removed) and the extracted Wikidata identifier. The function searches for patterns matching `@wikidata: Q[0-9]*` in both the "comment" and "original" fields of an entity's extra information. It uses `re.findall()` to capture all matching Wikidata IDs and `re.sub()` to remove these references from the text. The function prioritizes IDs found in the comment field but falls back to those in the original name if necessary. This dual-source approach increases the likelihood of successful ID extraction, accommodating variations in data entry practices. The function returns a tuple containing the cleaned comment and the Wikidata ID, with an optional default value for cases where no ID is found.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L63-L81)
- [residences.ipynb](file://notebooks/residences.ipynb#L92)

### extract_coordinates Function
The `extract_coordinates` function parses various coordinate formats from text comments and returns a tuple of latitude and longitude values. It supports four coordinate formats: explicit coordinate tags with directional indicators (e.g., 'coordinates: 40.7128N, 74.0060W'), labeled decimal degrees (e.g., 'latitude: 40.7128, longitude: -74.0060'), signed decimal degrees (e.g., '40.7128, -74.0060'), and degrees-minutes-seconds (DMS) format (e.g., '40°42'51"N 74°00'21"W'). The function uses a series of regular expression patterns to identify and extract coordinate information, converting DMS format to decimal degrees using a nested helper function. For directional formats, it applies appropriate sign multipliers based on the hemisphere indicator (N/S for latitude, E/W for longitude). The function returns `None` if no recognizable coordinate pattern is found, and raises a `ValueError` only after exhausting all parsing attempts, providing clear error messages for debugging.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L85-L151)
- [residences.ipynb](file://notebooks/residences.ipynb#L4367)

## Integration with Analysis Notebooks
The utility functions in `dehergne_util.py` are extensively used across multiple analysis notebooks, demonstrating their role as foundational components of the research workflow. In `dehergne_analysis.ipynb`, `calc_age_at` is applied to calculate the age of Jesuits at various life events, including entry, embarkation, and death, enabling demographic studies of the Jesuit population. The `location-analysis.ipynb` notebook uses `get_linked_entity_id` to extract Wikidata identifiers from place comments, facilitating the creation of a comprehensive database of geographical locations mentioned in the biographies. The `residences.ipynb` notebook leverages `get_wikidata_id` to systematically extract and clean Wikidata references from hierarchical geographical entities, supporting the analysis of Jesuit residences across different administrative levels. These integrations showcase how the utilities enable consistent data processing across different analytical contexts, reducing code duplication and ensuring methodological consistency.

**Section sources**
- [dehergne_analysis.ipynb](file://notebooks/dehergne_analysis.ipynb#L704)
- [location-analysis.ipynb](file://notebooks/location-analysis.ipynb#L501)
- [residences.ipynb](file://notebooks/residences.ipynb#L92)
- [jesuit-entry.ipynb](file://notebooks/jesuit-entry.ipynb#L4332)

## Error Handling and Common Issues
The utility functions implement robust error handling strategies to manage the inherent inconsistencies and missing data common in historical records. All functions accept `None` values for input parameters and return `None` or a specified default value, preventing cascading failures in data processing pipelines. The `calc_age_at` function includes multiple safety checks, verifying that input dates are properly converted to `datetime` objects before performing calculations. The coordinate extraction function employs a defensive programming approach, testing for the presence of coordinate indicators before attempting parsing and providing detailed error messages when parsing fails. A common issue addressed by these utilities is the presence of malformed date strings, which are handled by the underlying `convert_timelink_date` function. Another frequent challenge is ambiguous coordinate formats, which the `extract_coordinates` function resolves through a prioritized sequence of parsing attempts. The modular design of these utilities allows researchers to isolate and address specific data quality issues without disrupting the broader analysis workflow.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L1-L152)

## Performance Considerations
When applying these utilities to large datasets, several performance considerations should be taken into account. The functions are designed for individual record processing and should be applied using vectorized operations (e.g., `pandas.DataFrame.apply()`) rather than explicit loops to maximize efficiency. The regular expression operations in `get_linked_entity_id` and `extract_coordinates` are computationally efficient but can become bottlenecks when processing millions of records. In such cases, pre-compiling regular expressions or using more specialized parsing libraries may provide performance benefits. The `calc_age_at` function involves date conversion operations that can be optimized by caching converted dates when the same date strings are processed multiple times. For extremely large datasets, parallel processing techniques can be employed to distribute the computational load across multiple CPU cores. Memory usage is generally minimal, as the functions process one record at a time and do not maintain large internal data structures.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L1-L152)

## Best Practices and Extensions
Best practices for using and extending the `dehergne_util.py` module include maintaining consistent error handling patterns, documenting new functions with comprehensive docstrings, and ensuring backward compatibility when modifying existing utilities. When extending the module with new parsing functions, developers should follow the established pattern of accepting a string input and returning a structured result with appropriate default values for missing data. The modular design encourages the creation of specialized parsers for different data types, such as extracting bibliographic references or parsing complex name variations. Future extensions could include support for additional coordinate formats, integration with other linked data providers beyond Wikidata, or enhanced date parsing capabilities. The use of type hints and comprehensive unit tests would further improve the module's reliability and maintainability. Researchers are encouraged to contribute new utilities that address common data processing challenges, fostering a shared toolkit that enhances the reproducibility and efficiency of historical research.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L1-L152)

## Conclusion
The analysis utilities provided in `dehergne_util.py` play a crucial role in transforming raw historical data into structured, analyzable information. By encapsulating complex parsing and calculation logic, these functions enable researchers to focus on higher-level analysis rather than data preprocessing details. The utilities demonstrate thoughtful design principles, including robust error handling, graceful degradation with missing data, and clear separation of concerns. Their widespread use across multiple notebooks highlights their value as reusable components that promote consistency and efficiency in the research workflow. As the project evolves, these utilities can serve as a foundation for more sophisticated data processing pipelines, potentially incorporating machine learning techniques for entity recognition or natural language processing for semantic analysis. The modular architecture ensures that the utilities can be extended and adapted to meet emerging research needs while maintaining the integrity of existing analyses.