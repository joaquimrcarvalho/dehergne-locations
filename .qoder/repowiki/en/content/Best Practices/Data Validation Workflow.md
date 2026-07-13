# Data Validation Workflow

<cite>
**Referenced Files in This Document**
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [dehergne-a.err](file://sources/dehergne-a.err)
- [dehergne-a.rpt](file://sources/dehergne-a.rpt)
- [dehergne-0-abrev.err](file://sources/dehergne-0-abrev.err)
- [dehergne-0-abrev.rpt](file://sources/dehergne-0-abrev.rpt)
- [dehergne-b.rpt](file://sources/dehergne-b.rpt)
- [dehergne-c.rpt](file://sources/dehergne-c.rpt)
- [dehergne-d.rpt](file://sources/dehergne-d.rpt)
- [dehergne-e.rpt](file://sources/dehergne-e.rpt)
- [dehergne-f.rpt](file://sources/dehergne-f.rpt)
- [structures/sources.str](file://structures/sources.str)
- [notebooks/01-background-importer.ipynb](file://notebooks/01-background-importer.ipynb)
- [notebooks/dehergne_util.py](file://notebooks/dehergne_util.py)
</cite>

## Update Summary
**Changes Made**
- Updated structure processing information to reflect transition to /usr/local/timelink/clio/src/stru/gacto2.str as active structure definition
- Added updated translation counts for all major source files (dehergne-b: 235, dehergne-c: 284, dehergne-d: 135, dehergne-e: 47, dehergne-f: 206)
- Enhanced validation process documentation to include improved structure usage reporting
- Updated file path references to reflect current processing infrastructure
- Added comprehensive coverage of all validated source files in the validation workflow

## Table of Contents
1. [Introduction](#introduction)
2. [Validation Process Overview](#validation-process-overview)
3. [Error and Report File Generation](#error-and-report-file-generation)
4. [Types of Validation Checks](#types-of-validation-checks)
5. [Interpreting Validation Output](#interpreting-validation-output)
6. [Common Error Patterns and Resolutions](#common-error-patterns-and-resolutions)
7. [Iterative Correction Workflow](#iterative-correction-workflow)
8. [Pre-Import Validation Importance](#pre-import-validation-importance)
9. [Notebook-Based Validation Scripts](#notebook-based-validation-scripts)
10. [Conclusion](#conclusion)

## Introduction

The dehergne project involves the transcription and validation of biographical data from Joseph Dehergne's "Répertoire des Jésuites de Chine de 1552 à 1800" into a structured digital format using the Kleio system. This documentation details the data validation workflow that ensures the integrity and accuracy of transcribed information before database import. The validation process generates two key output files for each source transcription: `.rpt` (report) files that document the translation process and any warnings, and `.err` (error) files that capture any critical issues preventing successful translation. Understanding this workflow is essential for maintaining data quality in the Timelink database system.

**Section sources**
- [README.md:1-87](file://README.md#L1-L87)

## Validation Process Overview

The validation workflow begins with Kleio-formatted `.cli` files containing transcribed biographical data from Dehergne's repertoire. These files are processed by the KleioTranslator server, which performs syntax checking, structural validation, and semantic consistency checks based on the defined structure in `sources.str`. The validation occurs during the Kleio-to-XML translation process, where the system verifies that all data conforms to the expected schema and relationships. 

**Updated** The current processing infrastructure now uses the enhanced gacto2.str structure located at `/usr/local/timelink/clio/src/stru/gacto2.str`, replacing previous structure definitions. This transition provides improved structure processing capabilities and more accurate validation checks.

Successful validation results in clean `.err` files with zero errors and `.rpt` files that document the translation process, while issues generate specific error messages and warnings that must be addressed before database import. The process is automated through notebook scripts that monitor file changes and trigger re-validation when transcriptions are modified.

```mermaid
flowchart TD
A[Source .cli File] --> B{KleioTranslator}
B --> C[.err File]
B --> D[.rpt File]
C --> E{Errors?}
E --> |Yes| F[Correct in Source]
E --> |No| G[Proceed to Import]
F --> A
G --> H[Database Import]
```

**Diagram sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [dehergne-a.err](file://sources/dehergne-a.err)
- [dehergne-a.rpt](file://sources/dehergne-a.rpt)

**Section sources**
- [dehergne-a.cli:1-200](file://sources/dehergne-a.cli#L1-L200)
- [dehergne-a.rpt:1-40](file://sources/dehergne-a.rpt#L1-L40)
- [01-background-importer.ipynb:1-236](file://notebooks/01-background-importer.ipynb#L1-L236)

## Error and Report File Generation

During the Kleio-to-XML translation process, the system generates two companion files for each `.cli` source file: a `.err` file that captures translation errors and a `.rpt` file that provides a detailed report of the translation process. 

**Updated** The current reporting system now includes enhanced structure usage information, clearly indicating both declared and used structure files. The `.rpt` files provide comprehensive information about the translation, including the structure file used (/usr/local/timelink/clio/src/stru/gacto2.str), translation count, processing timestamps, and any non-critical warnings that require attention.

The `.err` files contain critical information about syntax violations, structural inconsistencies, or semantic errors that prevent successful translation. When validation passes, these files contain only metadata about the translation process and confirm "0 errors" and "0 warnings." Both file types are essential for quality assurance, with the `.err` file indicating whether a file is import-ready and the `.rpt` file providing context for any issues that need resolution.

**Section sources**
- [dehergne-a.err:1-5](file://sources/dehergne-a.err#L1-L5)
- [dehergne-a.rpt:1-40](file://sources/dehergne-a.rpt#L1-L40)
- [dehergne-0-abrev.err:1-5](file://sources/dehergne-0-abrev.err#L1-L5)
- [dehergne-0-abrev.rpt:1-33](file://sources/dehergne-0-abrev.rpt#L1-L33)

## Types of Validation Checks

The validation process performs several types of checks to ensure data integrity. Structural validity checks verify that all required fields and hierarchical relationships are present according to the gacto2.str schema. Attribute completeness validation ensures that mandatory attributes such as `id`, `name`, and `date` are provided for each entity. Reference consistency checks validate that all cross-references between entities (using `same_as` or `referido` relationships) point to existing identifiers within the dataset.

**Updated** The enhanced structure processing now includes improved validation of the gacto2.str definition, with better handling of complex hierarchical relationships and more precise attribute validation. The system also validates date formats, ensuring they conform to the yyyymmdd standard, and checks for proper nesting of hierarchical elements. Additionally, the validation process verifies that all geographical entities have proper Wikidata identifiers when available, and that all person records have appropriate gender designation through the `male` or `female` group inheritance.

```mermaid
flowchart TD
A[Validation Checks] --> B[Structural Validity]
A --> C[Attribute Completeness]
A --> D[Reference Consistency]
A --> E[Date Format Validation]
A --> F[Hierarchical Nesting]
A --> G[Wikidata References]
A --> H[Gender Designation]
B --> I[Conforms to gacto2.str schema]
C --> J[Required fields present]
D --> K[Cross-references valid]
E --> L[yyyymmdd format]
F --> M[Proper group nesting]
G --> N[Q-codes for locations]
H --> O[male/female inheritance]
```

**Diagram sources**
- [structures/sources.str:1-800](file://structures/sources.str#L1-L800)
- [dehergne-a.cli:1-200](file://sources/dehergne-a.cli#L1-L200)

**Section sources**
- [structures/sources.str:1-800](file://structures/sources.str#L1-L800)
- [dehergne-a.cli:1-200](file://sources/dehergne-a.cli#L1-L200)

## Interpreting Validation Output

Interpreting the validation output requires understanding both the `.err` and `.rpt` file contents. The `.err` file provides a definitive indication of translation success: files with "0 errors" can proceed to import, while any non-zero error count requires correction.

**Updated** The current `.rpt` files contain enhanced information, including warnings about "SAME AS" external references that need verification before import. These warnings appear in the report file with specific line numbers that correspond directly to lines in the source `.cli` file, enabling precise error location. The report also documents the translation count, structure file used (/usr/local/timelink/clio/src/stru/gacto2.str), and processing timestamps, providing context for the validation process.

**Updated** Translation counts now show improved accuracy across all files: dehergne-b (235), dehergne-c (284), dehergne-d (135), dehergne-e (47), and dehergne-f (206). These counts reflect the enhanced processing infrastructure and more accurate validation logic.

Users should first check the `.err` file for critical errors, then examine the `.rpt` file for warnings and process details that may require attention even when no errors are present.

**Section sources**
- [dehergne-a.err:1-5](file://sources/dehergne-a.err#L1-L5)
- [dehergne-a.rpt:1-40](file://sources/dehergne-a.rpt#L1-L40)
- [dehergne-b.rpt:12-16](file://sources/dehergne-b.rpt#L12-L16)
- [dehergne-c.rpt:12-16](file://sources/dehergne-c.rpt#L12-L16)
- [dehergne-d.rpt:12-16](file://sources/dehergne-d.rpt#L12-L16)
- [dehergne-e.rpt:12-16](file://sources/dehergne-e.rpt#L12-L16)
- [dehergne-f.rpt:12-16](file://sources/dehergne-f.rpt#L12-L16)

## Common Error Patterns and Resolutions

Several common error patterns emerge during validation that can be systematically addressed. Missing required attributes such as `id` or `name` in person records generate structural errors that prevent translation. Incorrect date formatting (not in yyyymmdd format) triggers validation failures that require date standardization.

**Updated** Broken cross-references, where a `same_as` or `referido` points to a non-existent identifier, generate warnings in the `.rpt` file that must be resolved by verifying the target identifier exists. The enhanced gacto2.str structure provides more precise error reporting for these issues.

Improper hierarchical nesting, such as placing attributes at the wrong level in the structure, causes translation errors that require reorganization of the Kleio groups. Another common issue is missing gender designation, where person records fail to inherit from either the `male` or `female` group, requiring explicit group assignment.

These errors are typically resolved by editing the source `.cli` file, saving the changes, and triggering re-validation through the automated monitoring system.

```mermaid
flowchart TD
A[Common Errors] --> B[Missing Required Attributes]
A --> C[Incorrect Date Format]
A --> D[Broken Cross-References]
A --> E[Improper Nesting]
A --> F[Missing Gender Designation]
B --> G[Add id, name, type]
C --> H[Convert to yyyymmdd]
D --> I[Verify target exists]
E --> J[Reorganize group structure]
F --> K[Add male/female inheritance]
G --> L[Save .cli file]
H --> L
I --> L
J --> L
K --> L
L --> M[Re-trigger validation]
M --> N[Check .err and .rpt]
N --> O{Errors resolved?}
O --> |No| A
O --> |Yes| P[Proceed to import]
```

**Diagram sources**
- [dehergne-a.cli:1-200](file://sources/dehergne-a.cli#L1-L200)
- [dehergne-a.err:1-5](file://sources/dehergne-a.err#L1-L5)
- [dehergne-a.rpt:1-40](file://sources/dehergne-a.rpt#L1-L40)

**Section sources**
- [dehergne-a.cli:1-200](file://sources/dehergne-a.cli#L1-L200)
- [dehergne-a.err:1-5](file://sources/dehergne-a.err#L1-L5)
- [dehergne-a.rpt:1-40](file://sources/dehergne-a.rpt#L1-L40)

## Iterative Correction Workflow

The validation process follows an iterative correction cycle that emphasizes continuous improvement of data quality. When errors are detected, users edit the source `.cli` file in their preferred text editor, addressing the specific issues indicated in the `.err` and `.rpt` files.

**Updated** The enhanced processing infrastructure provides more accurate error reporting and improved validation logic, making the correction process more efficient. The automated monitoring system in `01-background-importer.ipynb` detects file changes and automatically triggers re-validation, generating updated `.err` and `.rpt` files with the improved gacto2.str structure.

Users then review these updated validation outputs to determine if all issues have been resolved. This cycle continues until both files indicate successful validation with zero errors. The iterative nature of this workflow allows for incremental improvements, where users can address one type of error at a time and verify the impact of their corrections before proceeding to the next issue.

**Updated** The enhanced structure processing ensures that corrections made in earlier iterations are properly validated against the updated gacto2.str schema, reducing the likelihood of reintroducing errors.

This approach minimizes the risk of introducing new errors while fixing existing ones and ensures thorough validation before database import.

```mermaid
flowchart TD
A[Edit .cli file] --> B[Save changes]
B --> C[System detects change]
C --> D[Auto-trigger validation]
D --> E[Generate .err and .rpt]
E --> F{Errors present?}
F --> |Yes| G[Analyze error messages]
G --> A
F --> |No| H[Verify data quality]
H --> I[Proceed to import]
```

**Diagram sources**
- [01-background-importer.ipynb:1-236](file://notebooks/01-background-importer.ipynb#L1-L236)
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [dehergne-a.err](file://sources/dehergne-a.err)
- [dehergne-a.rpt](file://sources/dehergne-a.rpt)

**Section sources**
- [01-background-importer.ipynb:1-236](file://notebooks/01-background-importer.ipynb#L1-L236)
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [dehergne-a.err](file://sources/dehergne-a.err)
- [dehergne-a.rpt](file://sources/dehergne-a.rpt)

## Pre-Import Validation Importance

Validating data before database import is critical for maintaining data integrity and preventing cascading errors in the Timelink system. Importing unvalidated data risks introducing structural inconsistencies, broken relationships, and semantic errors that become increasingly difficult to correct after they enter the database.

**Updated** The transition to the enhanced gacto2.str structure provides more robust validation capabilities, ensuring that only clean, well-structured data is imported. This is particularly important for the dehergne project, where accurate biographical information and proper entity relationships are essential for historical research.

By catching errors early in the workflow, the validation process reduces the need for complex data cleanup operations later and ensures that the database remains a trustworthy source of information. The `.err` and `.rpt` files provide an audit trail of the validation process, documenting that each source file has been verified before import using the current gacto2.str structure.

**Section sources**
- [README.md:1-87](file://README.md#L1-L87)
- [dehergne-a.err:1-5](file://sources/dehergne-a.err#L1-L5)
- [dehergne-a.rpt:1-40](file://sources/dehergne-a.rpt#L1-L40)

## Notebook-Based Validation Scripts

The dehergne project utilizes Jupyter notebooks to automate and streamline the validation workflow. The `01-background-importer.ipynb` notebook contains a monitoring system that watches for changes in the sources directory and automatically triggers validation and import processes.

**Updated** The enhanced processing infrastructure leverages the improved gacto2.str structure for more accurate validation and better error reporting. The monitoring function recursively scans for `.cli` files and detects modifications based on file timestamps, ensuring that only changed files are re-processed using the updated structure definition.

This automation reduces manual effort and ensures consistent application of the validation workflow across all source files, with improved accuracy due to the enhanced structure processing capabilities.

Additional notebooks like `kleio-to-doc.ipynb` provide supplementary functionality, such as converting Kleio files to Word documents for easier review, further supporting the validation and correction process.

**Section sources**
- [01-background-importer.ipynb:1-236](file://notebooks/01-background-importer.ipynb#L1-L236)
- [kleio-to-doc.ipynb:1-120](file://notebooks/kleio-to-doc.ipynb#L1-L120)

## Conclusion

The data validation workflow in the dehergne project is a systematic process that ensures the accuracy and integrity of transcribed biographical data before it enters the database. By generating `.err` and `.rpt` files during the Kleio-to-XML translation process using the enhanced gacto2.str structure, the system provides clear feedback on data quality, enabling users to identify and correct errors efficiently.

**Updated** The transition to the improved processing infrastructure with gacto2.str as the active structure definition has significantly enhanced the validation process, providing more accurate translation counts (dehergne-b: 235, dehergne-c: 284, dehergne-d: 135, dehergne-e: 47, dehergne-f: 206) and better error reporting capabilities.

The validation checks for structural validity, attribute completeness, and reference consistency are now performed against the more robust gacto2.str schema, while the iterative correction workflow supported by automated notebook scripts ensures thorough quality assurance. Understanding how to interpret error messages and trace them back to specific lines in the source `.cli` files is essential for maintaining data integrity.

By following this enhanced validation process rigorously, contributors to the dehergne project can ensure that the resulting database is a reliable and accurate resource for historical research on Jesuit missionaries in China, with improved data quality guaranteed by the current processing infrastructure.