# Identifying place names

This note defines the rules for registering place names in the sources.


## Attributes that are place names

A Certain number of attributes of 
people in the sources are place names.

* baptizado (place of baptism)
* chegada (place of arrival)
* estadia (place of stay)
* jesuita-entrada (place of entry into the Jesuit order)
* jesuita-ordenacao-padre (place of ordination as a jesuit priest)
* jesuita-votos-local (place of taking vows as a jesuit)
* morte (place of death)
* nascimento (place of birth)
* partida (departed to)
* residência (place of residence)
* residencia-missão (place of residence in a mission)

## General rules

Several attributes involve the recording of locations. It is convenient to have some form of standardisation in the format of registration, especially when the place is referred to with some regional or national context.

If the source gives some geographic context use commas to separate different levels in place names, similarly to what is used modernly in postal addresses, ordering from particular to general. For example:

    ls$estadia/Navalafuente, diocese de Toledo

    ls$morte/Tusculum, Itália

In other cases the source may include more specific location information, using an expression of proximity or referring to a specific building. In that case we add the specificiation in parentheses. For example:

    ls$estadia/Macau (Colégio de S. Paulo)


The goal should be to make alphabetical lists of places keep variations of the same place close together and not separate entries in such a way that it is difficult to see all the variants of the same geographic name. So "Macau (Colégio de S. Paulo)" should be listed close to "Macau" and not under "C" for "Colégio de S. Paulo de Macau".


## Identifying place names

To provide an unambiguos reference to a place we use linked data identifiers. The identifiers are URIs that can be used to retrieve information about the place from the web. 

The preferred source of identifiers is
Wikidata. Information on place names in Wikidata includes geographic coordinates, alternate names in different languages, administrative context, and links to other sources of information about the place, such as library catalogs.

The Wikidata identifier is a URI that can be used to retrieve information about the place from the web. For example, the URI for Macau is <https://www.wikidata.org/wiki/Q14773>. The identifier is the part of the URI after the last slash, `Q14773`.

To identify a place in the sources we use the Wikidata identifier after the place name, as a comment. Comment are introduced with the cardonal sign(#) For example:

    ls$estadia/macau#@wikidata:Q14773

If there was a previous comment on the entry the new comment is added after a space. For example:

      ls$morte/Changchow, China#no rio, a caminho do Japão @wikidata:Q57970/16110000

If the identifier is not available in Wikidata, or there
ambiguity in the identification, add a comment with the work ILOC. For example:

    ls$estadia/Changchow, China#ILOC