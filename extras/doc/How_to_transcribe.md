# How to transcribe sources #

## General notation ##

The Kleio notation uses the concepts of `group`, `element`, `aspect`.

`Groups` represent entities, such as people, objects, institutions, but also acts (like baptisms, marriages, burials), events. In database terms groups are similar to tables that represent real world entities. Groups have a name that denotes the type of entity they describe.

Groups are registered with their name followed with a dollar sign:

        person$



`Elements` register information about groups, such as names of people, dates of acts, places of events. In databases the elements correspond the columns or fields of the database that register information about real world entities. 

Elements are registered with their name, followed by the = sign and the value of element. Sucessive element are separated by a slash.

        person$name=John Smith/sex=m

In most cases elements appear in a group in a predetermined order, and it is not necessary to name the element explicitly.

        person$John Smith/m

`Aspects` are diferent perspectives on the value of elements. There are three different aspects: `core`, `comment` and `original`. 

Core corresponds to the actual value of the element and must be present; `comment` is a comment on the value and `original` a representation of the original ortography of the value, if it is relevant. Comments are introduced with the # sign and original wording with the % sign.

    person$John Smith#Clear signature%John Smythe

## The source orientes model ##

Timelink uses the general notation above in a specific model that facilitates registration of personal information in historical sources. 

Baseado numa estrutura fonte/acto/actor ou objecto
Uma fonte contém um ou mais actos.
Os actos contém actores (pessoas) e objectos (propriedades, instituições…)
Os actores e os objectos são descritos por atributos que possuem um dado valor em determinado momento no tempo.
Actores e objectos estabelecem relações entre si em determinados momentos no tempo.



The model uses a hierarchy of nested groups. 

Each kleio file includes a source group, earch source a number of acts and each act a number of persons.

Persons related information is registred in `ls$` (life-story) and `rel$` (relation groups).

        kleio%
            source$
                act$
                    person$
                        ls$ (atributes of the person)
                        rel$ (relations of the person)

                        relative$ (persons related)

Transcriptions use a 

## File Header ##

All files start with with 