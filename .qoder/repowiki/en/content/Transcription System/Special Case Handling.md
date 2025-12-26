# Special Case Handling

<cite>
**Referenced Files in This Document**   
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [dehergne-0-abrev.cli](file://sources/dehergne-0-abrev.cli)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [How_to_transcribe.md](file://extras/doc/How_to_transcribe.md)
- [README.md](file://identifications/README.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Handling Name Variants with ls$nome](#handling-name-variants-with-lsnome)
3. [Managing Uncertain Identifications with mesmo_que and xmesmo_que](#managing-uncertain-identifications-with-mesmo_que-and-xmesmo_que)
4. [Resolving Homonyms with Disambiguated IDs](#resolving-homonyms-with-disambiguated-ids)
5. [Recording Additional People with referido$ Groups](#recording-additional-people-with-referido-groups)
6. [Abbreviation Management with dehergne-0-abrev.cli](#abbreviation-management-with-dehergne-0-abrevcli)
7. [Best Practices for Ambiguous Information](#best-practices-for-ambiguous-information)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Conclusion](#conclusion)

## Introduction
The Kleio transcription system for the Dehergne database provides sophisticated mechanisms for handling complex biographical cases involving name variants, uncertain identifications, and homonyms. This document details the specialized attributes and workflows used to manage these special cases, ensuring accurate representation of historical figures while maintaining data integrity. The system employs a combination of name variant tracking, disambiguation techniques, and reference management to handle the complexities of historical records where information may be conflicting, incomplete, or ambiguous. By understanding these mechanisms, transcribers can ensure consistency and accuracy when dealing with challenging cases in the biographical entries of Jesuit missionaries to China.

## Handling Name Variants with ls$nome

The Kleio system uses the `ls$nome` attribute to manage multiple name variants for individuals, allowing for comprehensive representation of how a person was known across different contexts and sources. This attribute is particularly important for historical figures who may have been recorded under various spellings, transliterations, or aliases. Each variant is recorded as a separate `ls$nome` entry, preserving the original forms while establishing their connection to the primary record.

For example, Adam Algenler (ID: deh-adam-algenler) is documented with multiple name variants reflecting different spellings found in historical sources:
```kleio
n$Adam Algenler/id=deh-adam-algenler
   ls$nome/Adam Agenler
   ls$nome/Adam Aingenier
   ls$nome/Adam Algelen
   ls$nome/Adam Aingenis
   ls$nome/Adam Aingiler
```

Similarly, Giulio Aleni (ID: deh-giulio-aleni) has several recorded variants:
```kleio
n$Giulio Aleni/id=deh-giulio-aleni
   ls$nome/Giulio Alenis
   ls$nome/Giulio de Leni
   ls$nome/Giulio de Lenes
   ls$nome/Giulio Anhelis
   ls$nome/Giulio de Elenis
```

The system also handles Chinese name variants, using the `ls$nome-chines` attribute to record different romanizations of Chinese names. For instance, Giulio Aleni is recorded with two Chinese name variants:
```kleio
ls$nome-chines/Ngai Jou-lio Sseu-Ki
ls$nome-chines/Ngai Jou-lio Se-Ki
```

This approach ensures that all known variants are preserved and linked to the individual's primary record, facilitating comprehensive searches and accurate identification across different sources. The transcription guidelines emphasize preserving the original forms as they appear in sources, rather than standardizing spellings, to maintain historical accuracy.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L164-L169)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L382-L386)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L90-L104)

## Managing Uncertain Identifications with mesmo_que and xmesmo_que

The Kleio system employs two specialized attributes—`mesmo_que` and `xmesmo_que`—to manage uncertain identifications and link records that may refer to the same individual. These attributes are crucial for handling cases where historical evidence suggests but does not definitively prove that two records refer to the same person.

The `mesmo_que` attribute is used to indicate that two occurrences within the same file refer to the same person. This creates a direct link between the records, allowing the system to aggregate information while preserving the separate entries. For example, in the case of João Alberto (ID: deh-joao-alberto), the system links his record to António de Abreu (ID: deh-antonio-de-abreu) using `mesmo_que`:
```kleio
n$João Alberto/id=deh-joao-alberto
   referido$António de Abreu/id=deh-joao-alberto-ref1/mesmo_que=deh-antonio-de-abreu
```

The `xmesmo_que` attribute serves a similar purpose but is used when linking records across different files. This is particularly important for maintaining consistency when the same individual appears in multiple source files. For instance, the system uses `xmesmo_que` to link references to the Kangxi Emperor across different files:
```kleio
referido$K'ang Hi/xmesmo_que=deh-kang-hi
```

The documentation provides important guidance on the use of these attributes:
- They are optional and not required for all cases
- When using `xmesmo_que`, the destination ID must be carefully verified, as the system cannot validate its existence during processing
- Using `xmesmo_que` may cause import errors if the referenced file is processed before the file containing the target ID
- The attribute is typically reserved for significant figures who appear frequently across sources

These mechanisms allow transcribers to indicate probable identifications while acknowledging uncertainty, preserving the integrity of the source material while enabling data aggregation.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L289-L291)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L486-L537)

## Resolving Homonyms with Disambiguated IDs

The Kleio system addresses the challenge of homonyms—different individuals sharing the same name—through a systematic approach to ID generation and disambiguation. When multiple individuals share a name, the system creates unique identifiers by appending suffixes to distinguish between them, ensuring each record has a distinct and unambiguous ID.

The primary method for disambiguation is the addition of `-refN` suffixes to the base ID, where N is a sequential number. For example, the three individuals named José de Almeida are distinguished as:
- deh-jose-de-almeida-i
- deh-jose-de-almeida-ii
- deh-jose-de-almeida-iii

Similarly, multiple individuals named António de Abreu are differentiated:
```kleio
n$António de Abreu/id=deh-antonio-de-abreu
referido$António de Abreu/id=deh-antonio-de-abreu-ref1
referido$António de Abreu/id=deh-antonio-de-abreu-ref2
```

The system also handles cases where individuals share names with notable figures from different contexts. For instance, Domingos Álvares (ID: deh-domingos-alvares) is distinguished from another individual with the same name:
```kleio
referido$Domingos Álvares/id=deh-domingos-alvares-ref1
   ls$nacionalidade/Portugal
   ls$jesuita-estatuto/Padre
   ls$nascimento/Covilhã, diocese da Guarda/15340000
   ls$dehergne/28-ref/obs=Pf. 404 n. 1 — Distinct d'un homonyme N. Covilhâ v. 1534, E. 1555, P. 1562, Emb. 1567 (W 108), qui fut recteur de Macao (DI. XII, 346).
```

The transcription guidelines emphasize that IDs must be unique and cannot contain spaces, using hyphens to separate name components. When homonyms occur, additional digits or descriptive suffixes are appended to ensure uniqueness. This systematic approach prevents confusion between individuals with identical or similar names while maintaining a logical and consistent naming convention.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L511-L555)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L25-L49)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L700-L710)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L78-L82)

## Recording Additional People with referido$ Groups

The Kleio system uses `referido$` groups to document additional people mentioned within biographical entries, particularly when these individuals are relevant for disambiguation or provide contextual information. This mechanism allows the transcription of information about homonyms or related figures without creating separate primary records, preserving the context while maintaining data organization.

The `referido$` groups follow the same structure as primary person records but are introduced with the `referido$` prefix instead of `n$`. Each referenced person receives a unique ID constructed from the primary person's ID with a `-refN` suffix. For example, in the entry for António de Abreu, two additional individuals with the same name are documented:
```kleio
referido$António de Abreu/id=deh-antonio-de-abreu-ref1
   ls$nacionalidade/Portugal
   ls$jesuita-cargo/Provincial de Portugal/16270000
   ls$jesuita-cargo/Provincial de Portugal/16290000
   ls$nascimento/Lisboa/15610000
   ls$jesuita-entrada/Coimbra/15760000

referido$António de Abreu/id=deh-antonio-de-abreu-ref2
   ls$nacionalidade/Portugal
   ls$morte/Coulam, Malabar/16111031
```

These referenced groups can also include relationships to the primary person using the `rel$` attribute. For instance, in the entry for Luís de Almeida, the individual who ordained him is documented with a relationship:
```kleio
referido$Belchior Miguel Carneiro Leitão/xmesmo_que=deh-belchior-miguel-carneiro-leitao/id=deh-luis-de-almeida-ref2
   rel$eclesiastica/Ordena/Luís de Almeida/deh-luis-de-almeida/data=15800000
```

The system also uses `referido$` groups to document individuals mentioned in passing or for contextual purposes. For example, in the entry for Michel Alfonso Chen, several notable figures he encountered are documented:
```kleio
referido$Philippe Couplet/id=deh-michel-alfonso-chen-ref1
referido$Luís XIV/id=deh-michel-alfonso-chen-ref2
referido$Inocêncio XI/id=deh-michel-alfonso-chen-ref3
```

This approach ensures that all relevant individuals mentioned in the source material are preserved in the database, providing a comprehensive context for the primary biographical entry while maintaining clear distinctions between primary and secondary figures.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L37-L49)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L627-L631)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L445-L464)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L394-L423)

## Abbreviation Management with dehergne-0-abrev.cli

The `dehergne-0-abrev.cli` file serves as the central repository for abbreviations and acronyms used throughout the Dehergne transcription system, providing standardized expansions and definitions that ensure consistency across all biographical entries. This file is essential for interpreting the condensed notation used in the original source material and maintaining uniformity in the transcribed records.

The abbreviation file follows a structured format where each entry consists of an abbreviation followed by its full expansion. For example:
```kleio
AGI Arch. Gen. de Indias, Séville.
AHN Archivo Historico Nacional Clero-SJ., Legs. 270, Madrid.
AHSI Archivum Historicum Societatis Jesu, Rome, 1932, sq.
ARSI Archivum Romanum Societatis Jesu, Archives de la Compagnie de Jésus, maison généralice, Rome.
```

The file includes a comprehensive range of abbreviations covering archival sources, publications, geographical locations, and ecclesiastical terms. It also provides important contextual notes, such as:
- Indications of references with asterisks (*) denoting volume and page numbers
- Clarifications about regional variations in province names
- Explanations of specialized terminology used in Jesuit records

The system integrates these abbreviations into the transcription workflow by making them available as a reference during the interpretation of source material. Transcribers consult this file to ensure accurate expansion of abbreviations, maintaining consistency across all entries. The file also includes cross-references to external sources, such as archive locations and publication details, enhancing the scholarly value of the transcriptions.

This centralized approach to abbreviation management ensures that all users of the database interpret the same abbreviations consistently, reducing ambiguity and improving the reliability of the transcribed information.

**Section sources**
- [dehergne-0-abrev.cli](file://sources/dehergne-0-abrev.cli#L1-L271)

## Best Practices for Ambiguous Information

The Kleio transcription system incorporates several best practices for handling ambiguous or conflicting information from secondary sources, ensuring that uncertainties are transparently documented while maintaining data integrity. These practices balance the need for accurate representation with the recognition that historical records often contain incomplete or contradictory information.

When source materials provide conflicting dates or details, the system prioritizes the first or most probable date mentioned in the source, while documenting alternatives in comments. For example, José Bernardo de Almeida's birth date is recorded with both possibilities:
```kleio
ls$nascimento/Penela, diocese de Coimbra/17280918#ou 17280115
```

The system emphasizes transparency in handling corrections or additions to Dehergne's original information. When transcribers supplement or correct information based on external sources like Wicky's work, these changes are explicitly documented in comments. For instance:
```kleio
ls$embarque/Santa Marta% Dehergne tem "Santa Maria", corrigido a partir de Wicky
```

For uncertain identifications, the system uses the `obs` (observation) field to document the nature of the uncertainty. In the case of Francisco Álvares, the documentation acknowledges uncertainty about whether he is the same individual mentioned in other sources:
```kleio
referido$Francisco Álvares/id=deh-francisco-alvares-ref1/obs=Dehergne não tem a certeza que seja o anterior
```

The guidelines also recommend using triple quotes (`"""`) to delimit observation text that contains special characters, ensuring proper parsing of the Kleio notation. This is particularly important for preserving the original source text in its entirety, including punctuation and special symbols.

When dealing with incomplete information, the system uses standardized placeholders. Unknown locations are represented with "?", and incomplete dates are formatted with zeros for missing components (e.g., 16580000 for a known year but unknown month and day). This systematic approach to handling incomplete data maintains consistency across records while clearly indicating the level of certainty for each piece of information.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L138-L140)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L725-L729)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L478-L485)

## Troubleshooting Common Issues

The Kleio transcription system documentation identifies several common issues that may arise when handling special cases, along with recommended solutions to maintain data integrity and consistency. These troubleshooting guidelines help ensure that potential problems are addressed proactively during the transcription process.

One common issue involves broken `xmesmo_que` references, which can occur when the referenced ID does not exist or when files are imported in the wrong order. The system may generate errors during import if a file containing `xmesmo_que` references is processed before the file containing the target ID. To prevent this, transcribers should:
- Verify that destination IDs exist before creating `xmesmo_que` links
- Import files in an order that ensures referenced IDs are available
- Use `xmesmo_que` primarily for well-established, frequently occurring figures

Incorrect disambiguation is another potential issue, particularly when distinguishing between homonyms. The documentation emphasizes the importance of careful verification when creating disambiguated IDs. For example, when documenting multiple individuals with the same name, transcribers should:
- Include distinguishing information such as birth dates, locations, or specific roles
- Use the `obs` field to document the basis for disambiguation
- Cross-reference with external sources when available

The system may also encounter issues with inconsistent name variants or abbreviations. To address this:
- Transcribers should consult the `dehergne-0-abrev.cli` file for standardized expansions
- All name variants should be documented using `ls$nome` attributes
- Original spellings should be preserved in the `%` aspect when they differ significantly from standardized forms

When importing files with complex reference structures, validation errors may occur. The recommended approach is to:
- Process files incrementally to identify and resolve issues
- Use the observation fields to document any uncertainties or corrections
- Consult the original source material to verify ambiguous references

These troubleshooting guidelines help maintain the reliability and consistency of the database, ensuring that special cases are handled systematically and transparently.

**Section sources**
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L530-L533)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L725-L729)
- [dehergne-0-abrev.cli](file://sources/dehergne-0-abrev.cli)

## Conclusion
The Kleio transcription system provides a comprehensive framework for handling the complex special cases encountered in the Dehergne database of Jesuit missionaries to China. Through the systematic use of attributes like `ls$nome` for name variants, `mesmo_que` and `xmesmo_que` for uncertain identifications, and disambiguated IDs for homonyms, the system ensures accurate and consistent representation of historical figures. The `referido$` groups enable comprehensive documentation of additional people mentioned in biographical entries, while the centralized `dehergne-0-abrev.cli` file maintains consistency in abbreviation usage. By following the established best practices for handling ambiguous information and addressing common troubleshooting issues, transcribers can maintain data integrity while preserving the nuances of historical records. This sophisticated approach to special case handling demonstrates the system's capacity to manage complex biographical data with precision and scholarly rigor.