# Importation Phase

<cite>
**Referenced Files in This Document**   
- [database/README.md](file://database/README.md)
- [notebooks/database-overview.ipynb](file://notebooks/database-overview.ipynb)
- [sources/dehergne-a.xml](file://sources/dehergne-a.xml)
- [notebooks/01-background-importer.ipynb](file://notebooks/01-background-importer.ipynb)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Database Schema and Table Structure](#database-schema-and-table-structure)
3. [XML to Database Import Process](#xml-to-database-import-process)
4. [Entity Insertion Example: dehergne-a.xml](#entity-insertion-example-dehergne-a.xml)
5. [Background Importer Automation](#background-importer-automation)
6. [Common Import Issues and Error Handling](#common-import-issues-and-error-handling)
7. [Optimization for Large Dataset Imports](#optimization-for-large-dataset-imports)
8. [Conclusion](#conclusion)

## Introduction
This document details the importation phase of the Timelink system, focusing on the process of loading XML files into a SQLite database. The system is designed to manage historical data on Jesuit missionaries, with a particular emphasis on individuals, their attributes, relationships, and geographical locations. The import process transforms structured XML data, derived from Joseph Dehergne's biographical dictionary, into a relational database format. This document explains the database schema, traces the insertion of entities using the dehergne-a.xml file as an example, describes the role of the background importer in automating bulk imports, addresses common data integrity issues, and provides optimization strategies for handling large datasets.

## Database Schema and Table Structure
The database schema is designed to represent persons, their temporal attributes, relations, and locations in a flexible and extensible manner. The core tables are `persons`, `attributes`, `relations`, and `geoentities`, all inheriting from a base `entities` table. The `persons` table stores basic information about individuals, such as their ID, name, and sex. The `attributes` table is central to the system, storing all temporal and categorical data about a person (e.g., birth, death, embarkation, Jesuit status) with fields for the attribute type, value, and date. The `relations` table captures connections between entities, such as a person being part of a source list. The `geoentities` table manages geographical information, including modern and historical names linked to Wikidata. This design allows for a rich representation of historical data with temporal precision and semantic linking.

**Section sources**
- [notebooks/database-overview.ipynb](file://notebooks/database-overview.ipynb#L120-L233)

## XML to Database Import Process
The import process begins with XML files that are structured according to a specific schema defined in the project's structure files. These XML files contain hierarchical data representing persons, their attributes, and relations. The Timelink importer tools parse these XML files, extracting entities and their properties. Each `GROUP` element in the XML corresponds to an entity (e.g., a person), and nested `GROUP` elements of type `attribute` or `relation` are processed as child records. The importer maps XML elements to database fields, converting the hierarchical structure into flat relational records. For example, a person's "embarque" (embarkation) attribute is inserted as a row in the `attributes` table, with the person's ID as a foreign key in the `entity` field. This process ensures that all data from the XML source is systematically loaded into the appropriate database tables.

**Section sources**
- [sources/dehergne-a.xml](file://sources/dehergne-a.xml#L80-L150)
- [notebooks/database-overview.ipynb](file://notebooks/database-overview.ipynb#L120-L233)

## Entity Insertion Example: dehergne-a.xml
The `dehergne-a.xml` file serves as a concrete example of the import process. It contains entries for several individuals, starting with "António de Abreu." The import process begins by creating a `person` entity with the ID `deh-antonio-de-abreu`, name, and sex. Subsequently, a series of `attribute` groups are processed. For instance, an attribute of type `jesuita-entrada` with the value "Goa" and date "15791200" is inserted into the `attributes` table. The date is stored as an integer in a YYYYMMDD format, allowing for flexible temporal queries. Another attribute of type `embarque` with the value "S. Valentim" and date "16020325" is similarly inserted. The process also handles references to other individuals, such as a second "António de Abreu" who was a Provincial in Portugal, by creating separate person and attribute records. This demonstrates how a single XML file can populate multiple database rows, accurately representing complex biographical data.

**Section sources**
- [sources/dehergne-a.xml](file://sources/dehergne-a.xml#L89-L435)

## Background Importer Automation
The `01-background-importer.ipynb` notebook implements an automated system for keeping the database synchronized with the source files. It runs a continuous monitoring loop that watches the project directory for any changes to `.cli` or `.kleio` files. When a change is detected, the system automatically triggers a translation of the modified source file into XML and initiates an import into the database. This background process ensures that the database is always up-to-date with the latest source data without requiring manual intervention. The importer is intelligent, processing only files that have been modified since the last import, which makes the system efficient for ongoing data curation. This automation is crucial for maintaining data integrity and streamlining the workflow for researchers and data managers.

**Section sources**
- [notebooks/01-background-importer.ipynb](file://notebooks/01-background-importer.ipynb#L175-L210)

## Common Import Issues and Error Handling
During the import process, several issues can arise, primarily related to data integrity. Primary key conflicts can occur if an entity with a duplicate ID is attempted to be inserted. Data type mismatches may happen if an XML field contains data that does not conform to the expected database type (e.g., a non-numeric value in a date field). Referential integrity violations are a risk if a relation references an entity ID that does not yet exist in the database. The system handles these issues through robust error logging. The translation phase generates error logs that pinpoint the exact source of the problem, such as a malformed date or a missing required field. These logs are essential for data curators to fix the source files before re-importing, ensuring the database remains consistent and reliable.

**Section sources**
- [notebooks/01-background-importer.ipynb](file://notebooks/01-background-importer.ipynb#L106-L107)
- [sources/dehergne-a.xml](file://sources/dehergne-a.xml#L152-L153)

## Optimization for Large Dataset Imports
To efficiently import large datasets, two key strategies are employed: transaction batching and index management. Transaction batching involves grouping multiple insert operations into a single database transaction. Instead of committing each row individually, which is slow due to the overhead of disk I/O and transaction logging, hundreds or thousands of rows are inserted within one transaction. This dramatically reduces the import time. Index management is equally important; database indexes, while essential for fast queries, can slow down insert operations because they must be updated with every new row. A common optimization is to drop non-essential indexes before a bulk import and recreate them afterward. This approach minimizes the overhead during the data loading phase, making the overall process significantly faster for large-scale data migrations.

**Section sources**
- [notebooks/01-background-importer.ipynb](file://notebooks/01-background-importer.ipynb#L108-L109)

## Conclusion
The importation phase is a critical component of the Timelink system, transforming structured XML data into a powerful relational database. The schema, centered on the `persons`, `attributes`, and `relations` tables, provides a flexible framework for representing complex historical information. The use of the `dehergne-a.xml` file as an example illustrates how entities and their temporal attributes are systematically inserted. Automation through the background importer ensures the database stays current with minimal effort. By addressing common issues like primary key conflicts and leveraging optimizations such as transaction batching, the system is robust and efficient, capable of handling the demands of large-scale historical data management.