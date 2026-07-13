# Best Practices

<cite>
**Referenced Files in This Document**   
- [How_to_transcribe.md](file://extras/doc/How_to_transcribe.md)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [dehergne-a.rpt](file://sources/dehergne-a.rpt)
- [dehergne-a.err](file://sources/dehergne-a.err)
- [identifications/README.md](file://identifications/README.md)
- [identifications/mhk_identification_toliveira.cli.exclude](file://identifications/mhk_identification_toliveira.cli.exclude)
- [README.md](file://README.md)
- [locations_how_to.md](file://extras/doc/locations_how_to.md)
- [obs-reformatting.md](file://extras/obs-reformatting.md)
</cite>

## Update Summary
**Changes Made**   
- Added new section on Observation Formatting Guidelines
- Updated Transcription Standards to include comprehensive observation formatting rules
- Enhanced Data Validation Workflows to cover observation field processing
- Updated Error Handling Procedures to address observation formatting corrections

## Table of Contents
1. [Transcription Standards](#transcription-standards)
2. [Observation Formatting Guidelines](#observation-formatting-guidelines)
3. [Data Validation Workflows](#data-validation-workflows)
4. [Version Control and Collaboration](#version-control-and-collaboration)
5. [Error Handling Procedures](#error-handling-procedures)
6. [Identification Best Practices](#identification-best-practices)
7. [Data Integrity and Reproducibility](#data-integrity-and-reproducibility)

## Transcription Standards

The dehergne project follows strict transcription standards to ensure consistency and accuracy in recording biographical data from Joseph Dehergne's "Répertoire des Jésuites de Chine." Transcription is performed using the Kleio notation system, which structures information hierarchically with groups, elements, and aspects. The core structure follows a source/act/actor-object/attributes-relations model, where each source contains acts, and each act contains people with their attributes and relations.

Consistent naming conventions are critical for maintaining data integrity. Each person entry begins with the `n$` group followed by the full name in natural order (first name, particles, surnames) and a unique identifier. The identifier uses the prefix "deh-" followed by the name in lowercase with hyphens replacing spaces (e.g., `deh-antonio-de-abreu`). In cases of homonyms, disambiguation is achieved by appending a sequential number (e.g., `deh-antonio-de-abreu-2`). This systematic approach ensures each person has a globally unique identifier within the database.

Proper use of abbreviations is essential for accurate transcription. The Dehergne work uses standardized abbreviations for key biographical events: "N." for birth, "M." for death, "E." for entry into the Jesuit order, "P." for priestly ordination, and "V." for vows. These abbreviations are expanded according to documented conventions: "pr." indicates profession of the four vows, "pr. 3 V" indicates profession of three vows without the fourth vow of obedience to the Pope for mission assignment, "c.spir." denotes spiritual coadjutors, and "c.temp." denotes temporal coadjutors. When transcribing, these abbreviations are converted to their full semantic equivalents in the Kleio format.

Handling uncertain data requires careful annotation. When dates are incomplete, they are recorded in AAAAMMDD format with zeros for unknown components (e.g., 16550800 for August 1655). Uncertain information is documented using comments (introduced with the # sign) and original wording (introduced with the % sign). For example, when a person's death date is uncertain, it might be recorded as `ls$morte/Goa/16991220#ou 16991225`. This preserves the ambiguity while maintaining the primary assertion. Geographic locations are standardized using comma-separated hierarchical notation from specific to general (e.g., `soure, diocese de Coimbra, Portugal`) and enhanced with Wikidata identifiers when available.

**Updated** Added comprehensive observation formatting guidelines that govern how biographical notes are processed and formatted within the transcription system.

**Section sources**
- [How_to_transcribe.md](file://extras/doc/How_to_transcribe.md#L1-L100)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L1-L575)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)
- [obs-reformatting.md](file://extras/obs-reformatting.md#L1-L11)

## Observation Formatting Guidelines

The dehergne project implements comprehensive formatting rules for processing observation data in the `ls$dehergne/NNN/obs` field format. These guidelines ensure consistency and readability of biographical notes while maintaining the integrity of source citations and original text.

**Text Merging and Organization**
Consecutive `ls$dehergne/NNN/obs=` entries for the same person must be merged into a single block. This consolidation prevents fragmentation of biographical information and ensures that related observations are presented cohesively. The merged text should maintain logical connections between different pieces of information about the same individual.

**Triple Quote Wrapping**
Observation text must be wrapped in triple quotes immediately after the equals sign: `ls$dehergne/NNN/obs="""..."""`. This formatting convention is particularly important when observation text contains special characters such as `$`, `/`, `=`, `#`, `%`, or `;`. The triple quote wrapper prevents parsing errors and ensures that complex citation formats are preserved correctly within the Kleio notation system.

**Text Fragmentation and Line Reflow**
Any fragmented text should be joined into a single paragraph before rewrapping. Lines should be reflowed to approximately 80 characters (ASCII) without altering the original wording or citations. This standardization improves readability while preserving the exact content of source materials. The reflow process should maintain sentence boundaries and preserve all punctuation, accents, and formatting elements.

**Event Marker Formatting**
Each event marker (such as `N. ...`, `E. ...`, `Emb. ...`, `Arr. ...`, `V. ...`, `M. ...`, `P. ...`, `v. ...`) must be placed on its own line. This separation creates clear visual distinction between different life events and makes the biographical narrative easier to parse and understand. Event markers should be properly indented to align with surrounding `ls$` lines.

**Citation Preservation**
All references, citations, accents, and punctuation must be preserved exactly as they appear in the source materials. Only whitespace and line breaks should be adjusted during the reformatting process. This strict preservation ensures that scholarly citations remain intact and that the academic rigor of the original sources is maintained.

**Indentation and Alignment**
The original indentation level should be maintained and aligned with surrounding `ls$` lines. Proper indentation helps maintain the hierarchical structure of the transcription and ensures that the formatting remains consistent with the overall Kleio notation conventions.

**Scope Limitations**
Formatting changes should only affect the observation text itself and should not alter other fields or add/remove content. The reformatting process is strictly limited to improving presentation while preserving all substantive content and structure.

**Section sources**
- [obs-reformatting.md](file://extras/obs-reformatting.md#L1-L11)

## Data Validation Workflows

The dehergne project employs a robust data validation workflow using `.rpt` (report) and `.err` (error) files to catch errors early in the transcription process. After processing a Kleio transcription file (`.cli`), the Timelink system generates corresponding `.rpt` and `.err` files that document the translation process and identify any issues. These validation files are essential for maintaining data quality and ensuring the integrity of the database.

The `.rpt` file provides a comprehensive report of the translation process, including processing statistics, structural information, and warnings. It begins with metadata about the KleioTranslator version and processing timestamp, followed by details about the source file being processed. The report includes the structure file used, translation count, and a summary of groups present in the file. Most importantly, it lists any warnings or informational messages that require attention. For example, the report may indicate "SAME AS" references to external entities, reminding users to verify that the referenced identifiers exist before importing the file. These warnings help prevent broken links and ensure referential integrity across the database.

The `.err` file complements the `.rpt` file by specifically documenting errors and warnings encountered during translation. A clean validation process should result in zero errors and warnings, as indicated by the message "0 errors. 0 warnings." When issues are detected, the `.err` file provides specific information about the nature and location of problems, allowing transcribers to correct them before proceeding. This immediate feedback loop enables rapid identification and resolution of transcription errors, preventing the propagation of invalid data into the database.

The validation workflow follows a systematic process: transcribers first create or modify `.cli` files using the Kleio notation, then process these files through the Timelink system to generate `.rpt` and `.err` files. They review these validation files to identify and correct any issues, repeating the process until both files indicate no errors or warnings. This iterative approach ensures that only validated, high-quality data is imported into the database, maintaining the reliability of the entire dataset.

**Updated** Enhanced validation workflow to include observation formatting validation, ensuring that restructured observation text meets all formatting requirements before import.

**Section sources**
- [dehergne-a.rpt](file://sources/dehergne-a.rpt#L1-L40)
- [dehergne-a.err](file://sources/dehergne-a.err#L1-L5)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)

## Version Control and Collaboration

The dehergne project utilizes Git for version control, enabling effective collaboration among multiple transcribers while maintaining a clear history of changes. The repository structure supports collaborative transcription through a well-defined branching strategy that separates work in progress from stable, validated data. This approach allows multiple contributors to work simultaneously on different aspects of the project without conflicts.

The primary branching strategy follows a feature-branch model where each major transcription effort or correction is developed on a dedicated branch. For example, when transcribing entries for a specific letter of the alphabet, a contributor would create a feature branch (e.g., `transcribe-letter-A`) from the main branch. This isolation allows for focused work without affecting the stability of the main codebase. Once the transcription is complete and validated, the feature branch is merged into the main branch through a pull request, which triggers a review process to ensure quality before integration.

Collaborative identification work is facilitated through the use of identification export files stored in the `identifications/` directory. These files, such as `mhk_identification_toliveira.cli.exclude`, contain record-linking information that maps multiple occurrences of the same historical person across different sources. When multiple contributors are working on related entries, they can reference these identification files to ensure consistency in person identification. The `.exclude` extension indicates that these files contain identification data that should be excluded from regular processing but preserved for record-keeping and restoration purposes.

Regular synchronization is essential for effective collaboration. Contributors are encouraged to frequently pull changes from the main repository to stay updated with others' work. The `updateFromTemplate.sh` script provides a mechanism for repositories forked from the main dehergne project to incorporate updates from the original template, ensuring that all forks maintain compatibility with the latest tools and standards. This script adds the original repository as a remote, pulls updates, and then removes the remote to prevent accidental pushes, maintaining the integrity of the original project.

**Updated** Added guidance for collaborative observation formatting work, including how to coordinate formatting changes across multiple transcription files while maintaining consistency.

**Section sources**
- [identifications/README.md](file://identifications/README.md#L1-L3)
- [identifications/mhk_identification_toliveira.cli.exclude](file://identifications/mhk_identification_toliveira.cli.exclude#L1-L514)
- [extras/scripts/updateFromTemplate.sh](file://extras/scripts/updateFromTemplate.sh#L1-L23)

## Error Handling Procedures

Error handling in the dehergne project follows a strict protocol to maintain data integrity and ensure the reliability of the database. When errors are identified in the transcription data, they must be corrected at the source level by editing the original `.cli` files rather than modifying the database directly. This approach preserves the audit trail and ensures that corrections are properly documented and version-controlled.

The process for correcting errors begins with identifying the issue through validation files (`.rpt` and `.err`) or during data review. Once an error is detected, the contributor locates the relevant `.cli` file containing the erroneous transcription. For example, if an incorrect date is found for a person's entry into the Jesuit order, the contributor would edit the corresponding `ls$jesuita-entrada` line in the appropriate `.cli` file (e.g., `dehergne-a.cli` for entries starting with 'A'). Corrections are made using the standard Kleio notation, preserving the hierarchical structure and formatting conventions.

**Updated** Enhanced error handling procedures to include observation formatting corrections, covering how to fix formatting violations in observation text and validate that reformatting meets all established guidelines.

For observation formatting errors, corrections should be made by reapplying the formatting rules from `extras/obs-reformatting.md`. This includes ensuring proper triple quote wrapping, correct line reflow, appropriate event marker placement, and preservation of all citations and punctuation. After making corrections, the contributor must reprocess the `.cli` file through the Timelink system to generate updated `.rpt` and `.err` files. These new validation files are reviewed to confirm that the error has been resolved and that no new issues have been introduced.

In cases where errors involve person identification or record linkage, corrections are made using the `mesmo_que` or `xmesmo_que` attributes in the `.cli` files. The `mesmo_que` attribute is used to link occurrences of the same person within the same file, while `xmesmo_que` is used for cross-file identification. When correcting identification errors, contributors must ensure that the target identifier exists and is correctly spelled, as the system cannot verify the existence of external references. Documentation in the form of comments should accompany significant corrections to provide context for future reviewers.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)
- [dehergne-a.rpt](file://sources/dehergne-a.rpt#L1-L40)
- [dehergne-a.err](file://sources/dehergne-a.err#L1-L5)

## Identification Best Practices

Identification best practices in the dehergne project focus on accurately linking multiple occurrences of the same historical person across different sources while managing false positives through systematic exclusion. The `identifications/README.md` file outlines the process for exporting and restoring identification data, ensuring that person linking information is preserved and can be reapplied when the sources are imported into a new database environment.

The primary tool for managing identifications is the `.exclude` file format, exemplified by `mhk_identification_toliveira.cli.exclude`. These files contain structured data that maps multiple occurrences (occ) of the same real person (rperson) across different transcription files. Each `rperson` entry defines a unique real-world individual with a stable identifier (e.g., `rp-46`), name, and status, while associated `occ` entries link specific transcription occurrences to this real person. This approach enables the aggregation of biographical information from multiple sources into a coherent narrative for each historical individual.

Managing false positives is a critical aspect of identification work. The `.exclude` files serve as a mechanism to document and preserve identification decisions, including cases where similar names were determined to refer to different individuals. For example, the file contains entries like `rperson$rp-41/António de Abreu` which links multiple occurrences while distinguishing this individual from others with similar names. When uncertainty exists, identifiers are marked with appropriate status indicators and accompanied by explanatory observations that document the reasoning behind identification decisions.

Contributors should follow specific guidelines when performing identification work. First, they should consult existing identification files to avoid duplicating effort or creating conflicting identifications. Second, when creating new identifications, they should use stable, memorable identifiers for frequently occurring individuals (such as emperors or prominent Jesuits) to facilitate cross-referencing. Third, all identification decisions should be documented with clear observations that explain the evidence supporting the linkage. Finally, contributors should be aware of the timing implications of using `xmesmo_que` references, as importing a file with external references before the target file can generate errors that will resolve on subsequent imports.

**Updated** Added guidance for coordinating identification work with observation formatting, ensuring that person identification decisions are properly documented alongside formatted observation text.

**Section sources**
- [identifications/README.md](file://identifications/README.md#L1-L3)
- [identifications/mhk_identification_toliveira.cli.exclude](file://identifications/mhk_identification_toliveira.cli.exclude#L1-L514)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L486-L538)

## Data Integrity and Reproducibility

Maintaining data integrity and ensuring reproducibility are fundamental principles in the dehergne project. These goals are achieved through a combination of systematic transcription practices, rigorous validation, and transparent documentation of all data modifications. The project adheres to the principles of "Open Science," ensuring that all data transformations are traceable and verifiable by other researchers.

Data integrity is preserved through several mechanisms. First, all source transcriptions are maintained in their original `.cli` format, providing a permanent record of the raw data. Second, changes to the data are never made directly to the database; instead, corrections are applied to the source `.cli` files and reprocessed, creating a complete audit trail. Third, the use of unique, persistent identifiers for persons and locations ensures referential integrity across the dataset. Finally, the inclusion of original text excerpts in the `obs` attribute of each entry allows researchers to verify the accuracy of transcriptions against the source material.

Reproducibility is ensured through comprehensive documentation and standardized workflows. The project maintains detailed documentation in the `extras/doc/` directory, including `How_to_transcribe.md` and `Dehergne_transcription_format.md`, which describe the transcription standards and data model. The use of Wikidata identifiers for locations (e.g., `@wikidata:Q14773` for Macau) provides unambiguous references that can be independently verified. When external sources are used to supplement information from Dehergne's work, these sources are explicitly documented in the `obs` attributes, allowing others to replicate the research process.

**Updated** Enhanced reproducibility guidelines to include observation formatting standards, ensuring that the formatting rules can be consistently applied and validated across all transcription projects.

Contributing to the shared knowledge base follows a structured process that emphasizes transparency and collaboration. Contributors are encouraged to document their research process, including the sources consulted and reasoning behind identification decisions. The project's licensing under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International ensures that contributions remain accessible to the research community while protecting against commercial exploitation. Regular backups of the database are maintained in the `database/` directory, providing recovery points and enabling the recreation of the research environment as needed.

The observation formatting guidelines provide a concrete example of how reproducible standards can be established and maintained. By following the specific formatting rules outlined in `extras/obs-reformatting.md`, contributors can ensure that their work produces consistent, high-quality results that can be easily understood and validated by others. This attention to detail in formatting contributes significantly to the overall reproducibility of the project.

**Section sources**
- [README.md](file://README.md#L1-L87)
- [locations_how_to.md](file://extras/doc/locations_how_to.md#L1-L66)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L448-L485)
- [database/README.md](file://database/README.md#L1-L3)
- [obs-reformatting.md](file://extras/obs-reformatting.md#L1-L11)