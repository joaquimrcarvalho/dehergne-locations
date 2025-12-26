# Attribute Notation

<cite>
**Referenced Files in This Document**   
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [sources.str](file://structures/sources.str)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Syntax of ls$ Attributes](#core-syntax-of-ls-attributes)
3. [Date Formatting Standards](#date-formatting-standards)
4. [Aspect Markers: # and %](#aspect-markers--and-)
5. [Common Attribute Types](#common-attribute-types)
6. [Validation Against Schema](#validation-against-schema)
7. [Handling Uncertain Information](#handling-uncertain-information)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Conclusion](#conclusion)

## Introduction
The Kleio transcription system used for the Dehergne Jesuit biographical records employs a structured notation for encoding biographical data. This document details the attribute notation system, focusing on the `ls$` (life-story) attributes that capture key biographical information about Jesuit missionaries to China. The system uses a consistent syntax to represent nationality, status, dates, locations, and other personal attributes, with specific conventions for handling uncertainty and validation.

**Section sources**
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L1-L575)

## Core Syntax of ls$ Attributes
The `ls$` prefix denotes life-story attributes that encode biographical information about individuals. Each attribute follows the format `ls$attribute_type/value`, where the value may include additional components for location, date, and aspects.

The basic structure is:
```
ls$attribute_type/location_or_value/date
```

For example:
- `ls$nacionalidade/Portugal` - Nationality attribute with value "Portugal"
- `ls$jesuita-entrada/Goa/15791200` - Jesuit entry attribute with location "Goa" and date "15791200"
- `ls$morte/Changchow#no rio, a caminho do Japão/16110000` - Death attribute with location "Changchow", comment "no rio, a caminho do Japão", and date "16110000"

The attribute type specifies the kind of information being recorded (e.g., nationality, Jesuit status, entry into the order, embarkation, death). The location or value field contains the primary data, while the date field follows the YYYYMMDD format with zeros for unknown components.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L25-L35)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L55-L64)

## Date Formatting Standards
Dates in the Kleio system follow a strict YYYYMMDD format, with zeros used as placeholders for unknown components. This standardized format ensures consistency across records and facilitates chronological analysis.

The date format rules are:
- Year: 4 digits (YYYY)
- Month: 2 digits (MM)
- Day: 2 digits (DD)
- Unknown components are represented by zeros

For example:
- `15791200` represents December 1579 (day unknown)
- `16020325` represents March 25, 1602 (all components known)
- `16110000` represents 1611 (month and day unknown)
- `17250000` represents 1725 (month and day unknown)

This format allows for flexible dating while maintaining a consistent structure that can be easily parsed and sorted. When only the year is known, the month and day are set to "00". When the year and month are known but not the day, the day is set to "00".

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L27-L33)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L118-L119)

## Aspect Markers: # and %
The Kleio system uses two aspect markers to provide additional context and clarification for attribute values: `#` for comments and `%` for original form.

### Comment Marker (#)
The `#` symbol introduces a comment or clarification about the attribute value. This is used to provide additional context, alternative interpretations, or explanatory notes.

Examples:
- `ls$jesuita-entrada/Goa%Goa, Índia# @wikidata:Q1171/15791200` - The comment `# @wikidata:Q1171` provides a linked data reference
- `ls$morte/Changchow#no rio, a caminho do Japão/16110000` - The comment explains the circumstances of death
- `ls$embarque/S. Valentim/16020325#não padre` - The comment clarifies that the person was not yet a priest

### Original Form Marker (%)
The `%` symbol indicates the original form or alternative spelling of the value. This is particularly useful for handling historical spellings, transliterations, or variant names.

Examples:
- `ls$jesuita-entrada/Goa%Goa, Índia# @wikidata:Q1171/15791200` - "Goa, Índia" is the original form
- `ls$nascimento/Elvas%elvensis# @wikidata:Q243849/16350000` - "elvensis" is the original Latin form
- `ls$nome-chines/Lou Lei-Sseu%Sié` - "Sié" is an alternative form of the Chinese name

These aspect markers allow for rich annotation of the data while maintaining the core structure of the attributes.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L27-L33)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L31-L33)

## Common Attribute Types
The Dehergne transcriptions use a standardized set of attribute types to encode biographical information. These attributes are grouped into categories based on the type of information they represent.

### Personal Identification Attributes
- `ls$nacionalidade` - Nationality of the individual
- `ls$nome` - Alternative names or spellings
- `ls$nome-chines` - Chinese name (romanized)

### Jesuit Status and Career Attributes
- `ls$jesuita-estatuto` - Jesuit status (e.g., Padre, Frade)
- `ls$jesuita-entrada` - Entry into the Jesuit order
- `ls$jesuita-votos` - Jesuit vows taken
- `ls$jesuita-votos-local` - Location where vows were taken
- `ls$jesuita-ordenacao-padre` - Priestly ordination
- `ls$jesuita-cargo` - Jesuit position or office held

### Travel and Location Attributes
- `ls$embarque` - Embarkation for China
- `ls$wicky` - Wicky number (missionary voyage identifier)
- `ls$wicky-viagem` - Wicky voyage number
- `ls$estadia` - Residence or stay in a location
- `ls$partida` - Departure for a destination
- `ls$chegada` - Arrival at a location
- `ls$morte` - Place of death

### Professional and Academic Attributes
- `ls$profissao` - Profession
- `ls$cargo` - Position or office (non-Jesuit)
- `ls$titulo` - Title or honorific
- `ls$grau-academico` - Academic degree

### Biographical Event Attributes
- `ls$nascimento` - Birth
- `ls$morte` - Death

Each attribute type serves a specific purpose in documenting the life and career of the Jesuit missionaries, creating a comprehensive biographical record.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L25-L55)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L72-L355)

## Validation Against Schema
The Kleio attributes are validated against the `sources.str` schema, which defines the structure and constraints for the transcription files. This schema ensures data consistency and integrity across the entire dataset.

The schema validation process checks:
- Correct attribute syntax and structure
- Valid attribute types
- Proper date formatting (YYYYMMDD with zeros for unknown components)
- Required fields for specific attribute types
- Data type consistency

For example, the schema would validate that:
- All `ls$` attributes follow the correct pattern
- Dates are in the proper YYYYMMDD format
- Required components are present
- Attribute types are from the defined set

The schema also defines the hierarchical structure of the data, ensuring that attributes are properly nested within the appropriate groups (e.g., person records). This validation process helps maintain data quality and prevents errors in the transcription process.

**Section sources**
- [sources.str](file://structures/sources.str#L1-L800)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L458-L475)

## Handling Uncertain Information
The Kleio system provides mechanisms for handling uncertain or conflicting information through the use of comments and alternative notations.

### Using Comments for Uncertainty
When there is uncertainty about a date or location, this is indicated in the comment field using the `#` symbol:

- `ls$nascimento/Penela, diocese de Coimbra/17280918#ou 17280115` - Indicates two possible birth dates
- `ls$morte/Batávia# @wikidata:Q1199713 (Jakarta), Indonésiaem viagem/17250000#cerca de` - Indicates approximate date

### Recording Alternative Information
When there are conflicting sources or alternative interpretations, these are recorded in the observation field (`obs`) associated with the `ls$dehergne` attribute:

```
ls$dehergne/1/obs=E. Goa, déc. 1579 (DI XII, 612 n. 54). Emb. non prêtre, le 25 mars 1602, sur le S. Valentim (W 486).| V. « Negapatami » (Négapatam), 6 janv. 1604, pr. (Lus. 3, 82). Il signe Antonius Dabreu. M. dans la rivière de « Chincheo »,m.q. Changchow (Tchang-tcheou), ou peut-être Chuanchow (Ts'iuen-tcheou), au Fou-kien, en 1611, en route vers le Japon (Schûtte 343., HS 43, 57 dit 1612). Pf. 125. (Distinct du Provincial de Portugal de ce nom, 1627-1629 N. Lisbonne 1561, E. à Coïmbre 1576 (Lus. 43 II, 509v). Un P. de ce nom meurt dans un naufrage le 31 oct. 1611, mais à Coulam, sur la côte malabare (Goa 24 II). HS 43a, 2v parle, semble-t-il, de ce dernier qu'il reporte à l'an 1612.
```

This approach allows for the recording of all available information while clearly indicating uncertainties and alternative interpretations.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L34-L35)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L134-L140)

## Troubleshooting Common Issues
Several common issues may arise when working with the Kleio attribute notation system. Understanding these issues and their solutions is essential for maintaining data quality.

### Incorrect Date Formatting
**Issue**: Dates not in YYYYMMDD format or with incorrect zero padding.
**Solution**: Ensure all dates follow the YYYYMMDD format, using zeros for unknown components (e.g., `15791200` for December 1579).

### Invalid Attribute Types
**Issue**: Using non-standard or misspelled attribute types.
**Solution**: Refer to the documentation for the complete list of valid attribute types and use them consistently.

### Missing Required Components
**Issue**: Omitting required components such as dates or locations.
**Solution**: Check the schema requirements for each attribute type and ensure all required components are present.

### Improper Use of Aspect Markers
**Issue**: Misusing `#` and `%` symbols or placing them in incorrect positions.
**Solution**: Use `#` for comments and `%` for original form, placing them in the correct position within the attribute value.

### Conflicting Information
**Issue**: Recording conflicting information without proper annotation.
**Solution**: Use the comment field (`#`) to indicate alternatives and the observation field (`obs`) to provide detailed explanations of conflicting sources.

By following these guidelines, users can ensure the accuracy and consistency of the transcribed data.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L27-L33)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L254-L270)

## Conclusion
The attribute notation system used in the Kleio transcription files provides a structured and consistent method for encoding biographical data about Jesuit missionaries to China. The `ls$` attributes, with their standardized syntax and formatting rules, enable the systematic recording of information about nationality, status, dates, locations, and other personal attributes. The use of aspect markers (`#` for comments and `%` for original form) and the YYYYMMDD date format with zero padding for unknown components ensures both flexibility and consistency in the data. Validation against the `sources.str` schema maintains data integrity, while the ability to record uncertain or conflicting information through comments and observations preserves the complexity of the historical record. This comprehensive system supports detailed biographical research and analysis of the Jesuit missions to China.