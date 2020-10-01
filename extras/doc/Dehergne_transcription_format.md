### Dehergne transcription format ###

## Versão em Português ###

### Ficheiros ###

Produz-se um ficheiro por cada letra, para evitar ficheiros demasiados grandes. 


Os ficheiros têm os nomes dehergne-a.cli, dehergne-b.cli, dehergne-c.cli, etc...

Cada ficheiro inclui uma fonte com `id` dehergne-A, dehergne-B, dehergne-C, etc...

Cada "fonte" inclui um único "acto", do tipo `lista$` com `id` dehergne-notices-a,  dehergne-notices-b, dehergne-notices-c, etc... e sem data.


O cabeçalho de cada ficheiro é assim:

    kleio$gacto2.str
        fonte$dehergne-A/1973/Dicionário Biográfico
            /Online archive.org:details:bhsi37
            /obs=Dehergne, Joseph, Répertoire des
             Jésuites de Chine, 
             de 1542 à 1800, 1973

          lista$dehergne-notices-a/0/0/0

Seguem-se as fichas biográficas.

Em cada ficheiro o cabeçalho apenas varia na letra do id do grupo `fonte$` e do grupo `lista$`,

### Fichas biográficas ###

A transcrição das entradas biográficas envolve duas operações: a interpretação da entrada, que contém muitas abreviaturas e convenções gráficas e, num segundo momento lógico, a transcrição na notação Kleio da informação.

Exemplo de entrada:

    Abreu, Antonio de (port.) P.                    1
    E. Goa, déc. 1579 (DI XII, 612 n. 54).
    Emb. non prêtre, le 25 mars 1602, sur le S. Valentim ( W 486).
    V. « Negapatami » (Négapatam), 6 janv. 1604, pr. (Lus. 3, 82). 
    Il signe Antonius Dabreu.
    M. dans la rivière de « Chincheo », = Changchow (Tchang-tcheou),
    ou peut-être Chuanchow (Ts'iuen-tcheou), au Fou-kien, en 1611, 
    en route vers le Japon (Schûtte 343; HS 43, 57 dit 1612).
    Pf. 125. (Distinct du Provincial de Portugal de ce nom, 
    1627-1629 N. Lisbonne 1561, E. à Coïmbre 1576 
    (Lus. 43 II, 509v). 
    Un P. de ce nom meurt dans un naufrage le 31 oct. 1611, mais à Coulam, 
    sur la côte malabare (Goa 24 II). HS 43a, 2v parle, semble-t-il, de ce 
    dernier qu'il reporte à l'an 1612.

Transcrição da informação biográfica

    n$António de Abreu/id=deh-antonio-de-abreu
        ls$nacionalidade/Portugal
        ls$jesuita-estatuto/Padre
        ls$jesuita-entrada/Goa/15791200
        ls$embarcado/S. Valentim/16020325
        ls$jesuita-votos/4V/16040106
        ls$jseuita-votos-local/Negaptattinam%Negapatami (Négapatam)/16040106
        ls$morte/Changchow#no rio, a caminho do Japão/16110000
        ls$dehergne/1

O desdobramento das abreviaturas vem detalhado na p. XIII da obra e é recapitulado de forma breve na página imediatamente anterior ao início da entradas (p.1). 

As secções seguintes detalham a transcrição dos principais atributos das entradas da obra, nem todos presentes no exemplo acima. 

#### Nome, nacionalidade, posição na hierarquia jesuíta, número de ordem e identificador na base de dados ####

    Abreu, Antonio de (port.) P.                    1   

Cada entrada é introduzida pelo grupo `n$` seguido do nome por ordem natural (primeiro nome, partículas, apelidos) e um `id` que irá identificar univocamente esta referência na base de dados. 

O `id` usa o prefixo "deh-" seguido do nome em minusculas com hifens no lugar dos espaços (os identificadores de pessoas não podem ter espaços). O `id` tem de ser único para cada pessoa, de modo que em caso de homonomias tem se produzir ids diferentes, adicionando dígitos (por exemplo, se fosse necessário: `deh-antonio-de-abreu-2`)

    n$António de Abreu/id=deh-antonio-de-abreu

Seguem-se a nacionalidade, grau dentro da hierarquia jesuíta e número de ordem no repertório.

    n$António de Abreu/id=deh-antonio-de-abreu
        ls$nacionalidade/Portugal
        ls$jesuita-estatuto/Padre
        ls$dehergne/1

### Variantes ao nome ###

Por vezes a obra indica nomes alternativos pelos quais a pessoa é conhecida e em alguns casos o nome chinês (este em forma romanizada).

Nesse caso criam-se atributos adicionais com o grupo `ls$` 

    n$Gil de Abreu/id=deh-gil-de-abreu
        ls$nome/Gil d'Abreu
        ls$nome/Gil Dabreu
            

    n$Lodovico António Adorno id=deh-ludovico-antonio-adorno
        ls$nome/Adurnus
        ls$nome-chines/Lou Lei-Sseu
        ls$nome-chines/Sié


### N. M. Nascimento e Morte ###

#### N.,  M. ####
Nascimento e Morte. Incluem normalmente a data e o lugar. Nem todas as entradas têm.

São registadas sob a forma 

    ls$nascimento/LOCAL/Data
    ls$morte/LOCAL/DATA

Em que LOCAL deve ser registado na medida do possível na língua do país. Como o autor trabalha com fontes em Latim nem sempre tem capacidade de registar a localidade corretamente. Por exemplo, regista Scalabis (nota em João de Abreu), em vez de Santarém. Em geral, salvo os casos evidentes, registar como na obra.

A data atualmente tem de ser registada na forma AAAAMMDD com zeros quando não existe informação de mês ou dia.

    Adorno, Lodovico Antonio Luca (ital.) P.     5 
    ...
    N. 28 août 1655, Gênes -E. 2 déc. 1680, Gênes (JS 26, 45v).
    ...
    M. 20 déc. 1699, Goa (JS 25, 229 et 166, 419). HS 51, 229 ...



    n$Lodovico António Adorno/id=deh-ludovico-antonio-adorno
        ...
        ls$nascimento/Génova/16550828
        ...
        ls$morte/Goa/16991220

### E. P. V. Atributos referentes ao percurso na Companhia de Jesus  ###

Distinguimos os atributos específicos do precurso na Companhia de Jesus, dos atributos comuns a outras pessoas fora da ordem, prefixando os primeiros com "jesuita-". Isso aplica-se à entrada para o noviciado, aos diferentes votos feitos ao longo da progressão na ordem, e aos cargos específicos exercidos dentro da ordem.

#### E. ####
 Data, local (cidade) e por vezes província jesuíta onde o missionário fez o noviciado.

    Abreu, Antonio de (port.) P.                    1
    E. Goa, déc. 1579 (DI XII, 612 n. 54).

    n$António de Abreu/id=deh-antonio-de-abreu
        ...
        ls$jesuita-entrada/Goa/15791200

Neste exemplo o dia é desconhecido.

#### P. ####

Data e local da obtenção de ordens sacras.

Notar que este P. aparece no corpo de algumas entradas quando o autor tem informação adicional sobre a ordenação sacerdotal. É por isso diferente do P. que aparece a seguir ao nome, introduzindo informação complementar. Exemplo:

    Abreu, Joâo de (port.) P. <-----             4
    N. 1635, « Elvensis », Elvas -E. 1648 (Lus. 45, 61v).
    Emb. 30 mars 1656 sur le Bom Jésus do Carmo (W 1014); 
    en 1660 était à Goa, mais sujet de la vice-province de Chine (JS 134, 344). 
    P. avant le 30 mars 1656.  <-----
    M. 24 juin 1663, Macao (JS 134, 346 et 352; AHU ms 1659, 108).
    ....

    n$João de Abreu/id=deh-joao-de-abreu
        ls$nacionalidade/Portugal
        ls$nascimento/Elvas%elvensis/16350000
        ...
        ls$jesuita-ordenacao-padre/?/16900408/obs=antes de

O P. no corpo da entrada é registado como `ls$jesuita-ordenacao-padre/LOCAL/DATA` 

* Como dito acima o P. associado ao nome no cabeçalho da entrada fica registado como `ls$jesuita-estatuto/padre`. É sempre registado. Tal como na obra, uma entrada com dois P. fica com dois `ls$` um para o estatuto outro para a informação de ordenação.

Se o local é desconhecido coloca-se "?". A data na forma AAAMMDD com zeros nos elementos desconhecidos.

#### V. ####

Votos jesuítas. Segundo o autor, na p. XV existem as seguintes variantes possíveis de valores a seguir a "V.":

* pr.  -> Professo dos quatro votos
* pr. 3 V -> Professo dos três votos sem o quarto voto de obediência ao Papa para o envio em missão.
* c.spir. -> Coadjutores espirituais
* c.temp. -> Coadjutores temporais (que não são padres mas fazem os mesmos 3 votos dos padres).

Usamos a forma `ls$jesuita-votos/VOTO/DATA` para registar em que VOTO com os seguintes desdobramentos para as abreviaturas:

    ls$jesuita-votos/4V (para pr.)
    ls$jesuita-votos/3V (para pr. 3 V)
    ls$jesuita-votos/coadjutor espiritual
    ls$jesuita-votos/coadjutor temporal

Quando a entrada contém também o local dos votos acrescenta-se o grupo `ls$jesuita-votos-local/LOCAL/DATA` 

### Emb. A. Viagens, chegada e estadias ###

#### Emb. ####

Embarque para a China, nome do navio e data de embarque. O autor recolhe esta informação da obra de Josef Wicky, _Liste der Jesuiten-Indienfahrer 1541-1758,_ que atribui um número a cada barco que transportou missionários para a Índia. O autor regista esse número, precedido da letra W, entre parentesis junto com a informação da viagem. Registamos esse número porque o registo do nome do navio é irregular na obra e interessa poder reconstruir com exatidão quem viajou com quem.

Regista-se na forma `ls$embarque/NAVIO/DATA` seguido de `ls$wicky/NUMERO`

    n$António de Abreu/id=deh-antonio-de-abreu
        ....
        ls$embarque/S. Valentim/16020325
        ls$wicky/486/16020325

#### A. ou arr. ####

Segundo o autor estas abreviaturas indicariam a chegada à China. 
Mas na verdade a utilização é inconstante e muitas vezes 
o que fica registado é uma sequência de locais onde o missionário
esteve depois da chegada ao Oriente. 

Assim usamos a forma `ls$estadia/LOCAL/DATA`, para registar os locais de chegada e posterior permanência no Oriente.

Exemplo: 

    Adorno, Lodovico Antonio Luca (ital.) P.               5 
        .....
        -------
        Emb. 8 avril 1690 (W 1283) pour la Chine (JS 134, 372); 
        Kanchow, Kan-tcheou (celui du Kiangsi); au bout de quelques 
        mois, rentre malade à Macao, puis à Goa. Borg. Lat. 523, 59 
        le dit arr. 1694 et retourné à Goa en 1695; 
        il fit pourtant ses voeux à Kanchow,
        en 1697, v. ci-après.
        -------
    
    n$Lodovico António Adorno/id=deh-ludovico-antonio-adorno
        ...
        ls$embarque/... para a China/16900408
        ls$wicky/1283/16900408
        ls$estadia/Kanchow%Kan-tcheou (o de Kiangsi)
        ls$estadia/Macau#doente/16940000
        ls$estadia/Goa/16950000

Nem sempre é fácil reconstruir as datas do texto sintético da entrada.

### Pessoas referidas ###

Algumas entradas incluem informação sobre pessoas adicionais, normalmente homónimos da pessoa tratada. Essa informação é relevante quando, numa fase posterior, se cruzar estes dados com outros oriundos de outras fontes.

A forma de registar essas pessoas é igual ao da pessoa principal, simplesmente o nome é introduzido pelo grupo `referido$` em vez de `n$` e na atribuição de `id`. Um exemplo explica como proceder:

    Abreu, Antonio de (port.) P.            1
    E. Goa, déc. 1579 (DI XII, 612 n. 54).
    ...
    Pf. 125. (Distinct du Provincial de Portugal de ce nom, 1627-1629 
    N. Lisbonne 1561, E. à Coïmbre 1576 (Lus. 43 II, 509v). 
    Un P. de ce nom meurt dans un naufrage le 31 oct. 1611, 
    mais à Coulam, sur la côte malabare (Goa 24 II). 
    HS 43a, 2v parle, semble-t-il, de ce dernier qu'il reporte à l'an 1612.

As últimas linhas incluem referência a duas pessoas adicionais. que foram registadas da seguinte maneira:

    referido$António de Abreu/id=deh-antonio-de-abreu-ref1
        ls$nacionalidade/Portugal
        ls$jesuita-cargo/Provincial de Portugal/16270000
        ls$jesuita-cargo/Provincial de Portugal/16290000
        ls$nascimento/Lisboa/15610000
        ls$jesuita-entrada/Coimbra/15760000/obs=Lus. 43. II 509v

    referido$António de Abreu/id=deh-antonio-de-abreu-ref2
        ls$nacionalidade/Portugal
        ls$morto/Coulam, Malabar#Naufrágio/16111031

Notar que o `id` destas pessoas adicionais é construído como os das entradas principais com o sufixo ref-N, em que N é um número sequencial dentro dos referidos associados a uma entrada principal.

### Registo do texto integral da referência em obs ###

A entradas incluem para cada item de informação uma série de anotações sobre a fonte utilizada. Normalmente essas informações seriam adicionadas como observações em cada atributo, mas isso iria tornar o registo demasiado moroso. Como a fonte está disponível em texto integral, é mais prático simplesmente copiar o texto integral da entrada como observação ao atributo `ls$dehergne` 

Assim na primeira entrada, de António de Abreu ficaria:


       n$António de Abreu/id=deh-antonio-de-abreu
            ls$nacionalidade/Portugal
            ls$jesuita-estatuto/Padre
            ls$jesuita-entrada/Goa/15791200
            ls$embarcado/S. Valentim/16020325
            ls$wicky/486/16020325
            ls$jesuita-votos/Negaptattinam%Negapatami (Négapatam)/16040106
            ls$morte/Changchow#no rio, a caminho do Japão/16110000/obs=Talvez 漳州 (Zhangzhou) Fujian
            ls$dehergne/1/obs=E. Goa, déc. 1579 (DI XII, 612 n. 54). 
            Emb. non prêtre, le 25 mars 1602, sur le S. Valentim 
            (W 486) | V. « Negapatami » (Négapatam), 6 janv. 1604, 
            pr. (Lus. 3, 82). Il signe Antonius Dabreu. M. dans la 
            rivière de « Chincheo »,m.q. Changchow (Tchang-tcheou),
            ou peut-être Chuanchow (Ts'iuen-tcheou), au Fou-kien, 
            en 1611, en route vers le Japon (Schûtte 343; HS 43, 57 
            dit 1612). Pf. 125. (Distinct du Provincial de Portugal 
            de ce nom, 1627-1629 N. Lisbonne 1561, E. à Coïmbre 1576
            (Lus. 43 II, 509v). Un P. de ce nom meurt dans un naufrage 
            le 31 oct. 1611, mais à Coulam, sur la côte malabare 
            (Goa 24 II). HS 43a, 2v parle, semble-t-il, 
            de ce dernier qu'il reporte à l'an 1612.



Importante: Para não interferir com a notação kleio é necessário verificar que a entrada copiada para o elemento `obs` não contenha os carateres especiais seguintes: $/=#%; . No caso desses caracters ocorrerem (= e ; ocorrerem com alguma frequência no texto devem ser substituídos. Por exemplo "=" por "--" e ";" por ".,"
