# Voyage Entity

<cite>
**Referenced Files in This Document**   
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb)
- [dehergne-a.cli](file://sources/dehergne-a.cli)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md)
- [dehergne_util.py](file://notebooks/dehergne_util.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Voyage Reconstruction from Wicky's Lists](#voyage-reconstruction-from-wickys-lists)
3. [Temporal Modeling of Voyages](#temporal-modeling-of-voyages)
4. [Voyage-Location Relationships](#voyage-location-relationships)
5. [Network Analysis of Missionary Movements](#network-analysis-of-missionary-movements)
6. [Challenges in Voyage Reconstruction](#challenges-in-voyage-reconstruction)
7. [Encoding Multi-leg Journeys and Uncertain Details](#encoding-multi-leg-journeys-and-uncertain-details)
8. [Integration with Residence Patterns](#integration-with-residence-patterns)
9. [Conclusion](#conclusion)

## Introduction
The Voyage entity in the dehergne project represents the journeys of Jesuit missionaries from Europe to Asia, primarily focusing on voyages to India and China during the 16th to 18th centuries. This documentation explains how voyage data is reconstructed from Josef Wicky's lists of Jesuit travelers to India, derived from biographical entries in Kleio transcriptions (.cli files), and represented in processed markdown files. The voyage data model captures temporal aspects of journeys through departure and arrival dates, connects voyages to geographic locations, and supports network analysis of missionary movements and colonial connections. The documentation also addresses challenges in voyage reconstruction, encoding multi-leg journeys, and integrating voyage data with residence patterns to create comprehensive mobility histories.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1-L1729)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L1-L575)

## Voyage Reconstruction from Wicky's Lists

The voyage data in the dehergne project is primarily reconstructed from Josef Wicky's "Liste der Jesuiten-Indienfahrer 1541-1758" (List of Jesuit India Travelers 1541-1758), which serves as a foundational source for tracking Jesuit missionary movements. The wicki-viagens.ipynb notebook demonstrates how this data is integrated into the project, using Wicky's sequential numbering system to identify specific voyages and individual travelers.

In the Kleio transcription format, voyage information is encoded using specific attributes that link Dehergne's biographical entries with Wicky's voyage records. The key attributes used for voyage reconstruction are:

- `ls$embarque/NAVIO/DATA`: Records the ship name and embarkation date
- `ls$wicky/NUMERO/DATA`: Records Wicky's sequential number for the individual traveler and the date
- `ls$wicky-viagem/ARMADA/DATA`: Records Wicky's sequential number for the armada (fleet) and the date

For example, in the dehergne-a.cli file, the entry for Belchior Nunes Barreto includes:
```
ls$embarque/Esfera/15510310
ls$wicky/31/15510310
ls$wicky-viagem/5/15510310
```

This indicates that Belchior Nunes Barreto embarked on the ship "Esfera" on March 10, 1551, was the 31st Jesuit listed by Wicky on this voyage, and traveled on armada number 5. The integration of Wicky's armada number (wicky-viagem) was a crucial enhancement, as Dehergne's original work only included the individual traveler number (wicky), which prevented reconstruction of who traveled together.

The wicki-viagens.ipynb notebook demonstrates how this data can be queried to identify all missionaries who traveled on the same armada. For instance, setting `voyage_of_interest = '89'` allows the notebook to retrieve all travelers on armada 89, which departed in 1657. This enables researchers to study cohort-based mobility patterns and analyze social networks among missionaries who shared the same journey.

The voyage reconstruction process involves cross-referencing Dehergne's biographical information with Wicky's voyage lists to create a comprehensive picture of missionary movements. When discrepancies arise between sources (such as ship names), these are documented in observation fields to maintain transparency about the provenance of information, adhering to open science principles.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1-L1729)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L209-L277)

## Temporal Modeling of Voyages

The temporal modeling of voyages in the dehergne project is implemented through a structured date system that captures the timing of missionary journeys with varying degrees of precision. The system uses an 8-digit format (AAAAMMDD) for dates, where zeros are used for unknown month or day values, allowing for flexible temporal representation that accommodates the varying quality of historical records.

Voyage dates are primarily captured through the embarkation date (`ls$embarque/NAVIO/DATA`), which represents the departure point of the journey from Europe. This date field is central to the temporal modeling of voyages, as it establishes the chronological framework for missionary movements. In cases where multiple dates are provided by different sources, the most probable date is recorded in the main field, while alternatives are documented in comment fields (e.g., `ls$nascimento/Penela, diocese de Coimbra/17280918#ou 17280115`).

The temporal model also accounts for the duration of voyages, which could span several months. While specific arrival dates in Asia are not always recorded in the primary voyage attributes, they can be inferred from subsequent entries in the biographical records, such as `ls$estadia/LOCAL/DATA` for locations in Asia. This creates a temporal sequence from departure to arrival and subsequent movements.

The wicki-viagens.ipynb notebook demonstrates temporal analysis of voyage patterns over time, showing the number of missionaries traveling to India across different years. This analysis reveals historical trends in missionary mobility, such as peaks in travel during certain periods and gaps during times of political or religious upheaval.

For voyages with uncertain dates, the system employs a flexible approach by recording the known elements and annotating uncertainties. For example, when only the year is known, the date is recorded with zeros for the month and day (e.g., 16570000), preserving the temporal information while acknowledging its limitations. This approach enables chronological analysis while maintaining data integrity and transparency about uncertainties in the historical record.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L578-L1479)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L118-L134)

## Voyage-Location Relationships

The voyage-location relationships in the dehergne project are modeled through a combination of embarkation points, destination inferences, and subsequent residence records that together create a spatial framework for missionary journeys. The primary location data associated with voyages is the embarkation point, recorded in the `ls$embarque/NAVIO/DATA` attribute, which captures both the ship name and departure location.

In the Kleio transcription format, locations are recorded with hierarchical specificity, typically following a pattern from specific to general (e.g., "Bom Jesus da Vidigueira" as a specific church or port, potentially within a larger administrative region). The Dehergne_transcription_format.md documentation outlines conventions for recording locations, including the use of commas to separate different levels of geographic specificity and parentheses for additional contextual information.

The project enhances location data through linked data integration, using Wikidata identifiers to provide unambiguous references to geographic entities. As documented in the Dehergne_transcription_format.md file, locations can include Wikidata references in the format `@wikidata:Q1171`, which links to the specific entity in the Wikidata knowledge base. This enables integration with external geographic databases and facilitates spatial analysis.

While the primary voyage records focus on departure points, destination locations are inferred through subsequent biographical entries. The `ls$estadia/LOCAL/DATA` attribute records locations where missionaries resided after their voyages, creating a sequence of spatial movements. For example, a missionary might have an embarkation record for Lisbon, followed by estadia records for Goa, Macau, and Beijing, reconstructing the full journey trajectory.

The relationship between voyages and locations is further enriched by additional attributes such as `ls$jesuita-votos-local/LOCAL/DATA`, which records locations where Jesuits took their vows, often in Asian destinations after their voyages. This creates a network of location connections that extends beyond the simple departure-arrival model to capture the complex spatial patterns of missionary life.

**Section sources**
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L369-L393)

## Network Analysis of Missionary Movements

The voyage data in the dehergne project serves as a foundation for network analysis of missionary movements and colonial connections, enabling researchers to study the social and institutional networks that facilitated Jesuit expansion in Asia. By reconstructing voyages from Wicky's lists and integrating them with biographical data, the project creates a rich dataset for analyzing patterns of mobility, cohort formation, and institutional connections.

The wicki-viagens.ipynb notebook demonstrates how voyage data can be used for network analysis by identifying all missionaries who traveled on the same armada. For example, the analysis of voyage 89 reveals a cohort of 23 missionaries who departed together in 1657, including notable figures like Ferdinand Verbiest and Martino Martini. This cohort-based approach allows researchers to study the formation of missionary networks from the moment of departure, examining how shared journeys may have influenced subsequent collaborations and institutional relationships in Asia.

The network analysis capabilities are enhanced by the integration of multiple data dimensions, including:
- Nationality (`ls$nacionalidade`)
- Jesuit province of entry (`ls$jesuita-entrada`)
- Academic qualifications (`ls$grau-academico`)
- Professional expertise (`ls$profissao`)

These attributes allow for multidimensional network analysis, revealing patterns such as the predominance of Portuguese missionaries in certain periods, the representation of different European regions, and the distribution of specialized skills within voyage cohorts.

The temporal dimension of voyage data enables longitudinal network analysis, tracking how missionary networks evolved over time. The wicki-viagens.ipynb notebook includes analysis of the number of missionaries traveling over time, revealing trends in recruitment and deployment that can be correlated with historical events and institutional developments.

Furthermore, the integration of voyage data with residence patterns (`ls$estadia`) and institutional roles (`ls$jesuita-cargo`) allows for the reconstruction of career trajectories and institutional networks, showing how initial voyage cohorts dispersed across Asian missions and assumed various roles in the Jesuit organizational structure.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1-L1729)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)

## Challenges in Voyage Reconstruction

The reconstruction of voyages in the dehergne project faces several challenges related to incomplete records, ambiguous route descriptions, and inconsistencies between sources. These challenges require careful documentation and methodological approaches to ensure data integrity while maximizing the information that can be extracted from historical sources.

One significant challenge is the incomplete nature of voyage records in Dehergne's original work. As noted in the Dehergne_transcription_format.md documentation, Dehergne only recorded the individual traveler number from Wicky's lists, not the armada number, which initially prevented reconstruction of who traveled together. This limitation was addressed by supplementing Dehergne's data with information from Wicky's original work, adding the `ls$wicky-viagem/ARMADA/DATA` attribute to restore the cohort information.

Ambiguous route descriptions present another challenge, particularly regarding ship names and specific embarkation points. The documentation notes cases where Dehergne's records may contain errors or omissions compared to Wicky's original lists, such as a ship named "Santa Maria" in Dehergne that appears as "Santa Marta" in Wicky. The project addresses this by maintaining fidelity to Dehergne's original transcription while adding corrective information in comment fields, ensuring transparency about the provenance of data.

Temporal uncertainties are also common, with many records providing only partial dates (year only, or year and month). The system handles this through its flexible date format (AAAAMMDD with zeros for unknown elements) and by documenting alternative dates in comment fields when sources disagree.

Another challenge is the inconsistent use of arrival indicators in the biographical records. As noted in the documentation, the abbreviations "A." or "arr." that should indicate arrival in China are used inconsistently, sometimes referring to intermediate stops or terrestrial journeys rather than final arrival. This requires careful interpretation and often relies on contextual clues from other biographical entries to reconstruct the complete journey.

The project addresses these challenges through systematic documentation practices, including the use of observation fields to record uncertainties and discrepancies, maintaining a clear audit trail of data interpretation decisions.

**Section sources**
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L253-L277)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)

## Encoding Multi-leg Journeys and Uncertain Details

The dehergne project employs specific encoding strategies to represent multi-leg journeys and uncertain voyage details, accommodating the complex mobility patterns of Jesuit missionaries who often made multiple voyages between Europe and Asia throughout their careers. The data model supports the representation of successive journeys through the repetition of voyage-related attributes, allowing for the chronological sequencing of multiple embarkations.

For multi-leg journeys, the system uses repeated instances of voyage attributes rather than creating a single complex record. Each leg of a journey is encoded as a separate `ls$embarque` entry, maintaining chronological order through the date field. This approach, as documented in the Dehergne_transcription_format.md file, allows for the representation of return journeys to Europe and subsequent re-embarkations, such as in the case of Miguel do Amaral who made multiple voyages.

The encoding of uncertain details follows a systematic approach that prioritizes transparency and data provenance. When information is uncertain or conflicting, the primary record contains the most probable interpretation, while alternative possibilities are documented in comment fields using the `#` symbol. For example, when multiple dates are possible, the preferred date is recorded with alternatives noted (e.g., `ls$nascimento/Penela, diocese de Coimbra/17280918#ou 17280115`).

For voyage details with partial information, the system uses its flexible date format (AAAAMMDD) with zeros representing unknown components. This allows for the recording of year-only dates (e.g., 16570000) or year-month dates (e.g., 16570300) while preserving the temporal information that is available.

The project also employs a hierarchical approach to location specificity, allowing for varying levels of geographic precision. When exact locations are unknown, more general regions are recorded, with additional context provided in comment fields. This approach accommodates the varying quality of geographic information in historical sources.

To maintain data integrity while acknowledging uncertainties, the system uses observation fields (`obs`) to document the reasoning behind interpretive decisions, sources of conflicting information, and methodological considerations. This creates a transparent audit trail that supports scholarly scrutiny and future reinterpretation of the data.

**Section sources**
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L307-L314)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)

## Integration with Residence Patterns

The integration of voyage data with residence patterns in the dehergne project creates comprehensive mobility histories that extend beyond simple departure-arrival models to capture the full trajectory of missionary careers. This integration is achieved through the connection of voyage attributes with residence and activity records, forming a chronological sequence of movements and locations that documents the complete mobility pattern of each missionary.

The primary mechanism for this integration is the use of complementary attributes that bridge voyage and residence data. While `ls$embarque` records the departure from Europe, `ls$estadia` records subsequent locations in Asia, creating a continuous timeline of movement. Additional attributes like `ls$chegada` and `ls$partida` provide more specific information about arrivals and departures at intermediate locations, allowing for the reconstruction of complex multi-stage journeys.

The temporal framework established by voyage dates serves as an anchor for the entire mobility history, with subsequent residence dates positioned relative to the known embarkation date. This allows for the reconstruction of journey durations and the timing of activities in different locations. For example, the interval between embarkation and the first `ls$estadia` record in Asia provides information about the duration of the sea voyage.

The integration also extends to institutional and professional activities, with attributes like `ls$jesuita-votos-local` recording locations where missionaries took their vows, often in Asian destinations after their voyages. This creates a rich network of location-based events that documents not just physical movement but also career progression and institutional integration.

The dehergne_util.py file contains functions that support this integration, such as `calc_age_at` which can compute a missionary's age at specific dates, enabling demographic analysis of mobility patterns. This function, combined with the chronological data from voyages and residences, allows researchers to study age-related patterns in missionary deployment and career progression.

By integrating voyage data with residence patterns, the project enables the reconstruction of complete career trajectories, revealing patterns such as the typical sequence of assignments, the duration of stays in different locations, and the geographic range of individual careers. This comprehensive approach to mobility history supports sophisticated analyses of missionary networks, institutional strategies, and colonial connections.

**Section sources**
- [dehergne_util.py](file://notebooks/dehergne_util.py#L1-L152)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L278-L306)

## Conclusion

The Voyage entity in the dehergne project represents a sophisticated data model for reconstructing and analyzing the movements of Jesuit missionaries from Europe to Asia during the early modern period. By integrating Josef Wicky's lists of India travelers with Joseph Dehergne's biographical dictionary, the project creates a rich dataset that captures both the individual and collective dimensions of missionary mobility.

The voyage data model successfully addresses the challenges of historical record-keeping through a flexible system that accommodates incomplete information, uncertain dates, and ambiguous route descriptions while maintaining data integrity and transparency. The use of standardized attributes like `ls$embarque`, `ls$wicky`, and `ls$wicky-viagem` enables the reconstruction of voyage cohorts and the analysis of social networks among missionaries who traveled together.

The integration of voyage data with residence patterns, institutional roles, and professional attributes creates comprehensive mobility histories that extend beyond simple departure-arrival models to capture the full trajectory of missionary careers. This integrated approach supports sophisticated network analysis of missionary movements and colonial connections, revealing patterns of cohort formation, institutional deployment strategies, and geographic networks.

The project's commitment to open science principles is evident in its transparent documentation of data sources, interpretive decisions, and uncertainties, ensuring that the reconstructed voyage data remains faithful to its historical sources while being accessible for scholarly analysis. The use of linked data through Wikidata identifiers enhances the geographic precision of location data, facilitating spatial analysis and integration with external datasets.

Overall, the Voyage entity provides a powerful framework for studying the complex dynamics of missionary expansion, offering researchers a detailed and nuanced understanding of the human networks that connected Europe and Asia during the early modern period.

**Section sources**
- [wicki-viagens.ipynb](file://notebooks/wicki-viagens.ipynb#L1-L1729)
- [dehergne-a.cli](file://sources/dehergne-a.cli#L1-L200)
- [Dehergne_transcription_format.md](file://extras/doc/Dehergne_transcription_format.md#L1-L575)
- [dehergne_util.py](file://notebooks/dehergne_util.py#L1-L152)