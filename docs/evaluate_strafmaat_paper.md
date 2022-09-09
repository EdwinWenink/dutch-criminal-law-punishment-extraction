# Manual evaluation

Punishments that should be matched are in **bold**.
These are decisions sections from 35 randomly sampled real Dutch criminal law cases from 2021.
Below each case is the output of the punishment extraction pipeline.
This file is produced by running `src/eval_punishment_extration.py`.

- TP: 45
- FP: 5
- TN: 52
- FN: 5

$$F1 = \frac{2 TP}{2TP + FP + FN} = \fraC{90}{90 + 5 +5} = 0.90$$

CASE: ECLI:NL:RBAMS:2021:2514
=============================
TEXT:
10 Beslissing De rechtbank komt op grond van het voorgaande tot de volgende beslissing. Verklaart bewezen dat verdachte het ten laste gelegde heeft begaan zoals hiervoor in rubriek 3.4 is vermeld. Verklaart niet bewezen hetgeen aan verdachte meer of anders is ten laste gelegd dan hiervoor is bewezen verklaard en spreekt verdachte daarvan vrij. Het bewezen verklaarde levert op:  opzettelijk handelen in strijd met een in artikel 2 onder B van de Opiumwet gegeven verbod. Verklaart het bewezene strafbaar. Verklaart verdachte, [verdachte], daarvoor strafbaar. Veroordeelt verdachte tot **een gevangenisstraf voor de duur van 42 (tweeënveertig) maanden**. Beveelt dat de tijd die door verdachte voor de tenuitvoerlegging van deze uitspraak in verzekering en in voorlopige hechtenis is doorgebracht, bij de tenuitvoerlegging van die straf in mindering gebracht zal worden. Verklaart verbeurd: 1 STK Lidl tas (G6006051); 1 STK Lidl tas (G6006053); 1 STK Lidl tas (G6006055); 1 STK Lidl tas (G6006056); 1 STK Lidl tas (G6006057); 1 STK Lidl tas (G6006058). Verklaart onttrokken aan het verkeer: 52 STK verdovende middelen (G6006060); 1 STK verdovende middelen (G6006229); 14 STK verdovende middelen (G6006049); 20 STK verdovende middelen (G6006050); 18 STK verdovende middelen (G6006052). Dit vonnis is gewezen door mr. A.A. Spoel,  voorzitter, mrs. E. Akkermans en R. Gaarthuis,  rechters, in tegenwoordigheid van mr. K. Kanters,  griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank van 19 mei 2021.

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 42 (tweeënveertig) maanden
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd dan hiervoor is bewezen verklaard en spreekt verdachte daarvan vrij. Het bewezen verklaarde levert op:  opzettelijk h
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 1277, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 1277, 0, 0, 0, 0)

TP: 1
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBAMS:2021:7026
=============================
TEXT:
10 Beslissing De rechtbank komt op grond van het voorgaande tot de volgende beslissing. Verklaart bewezen dat verdachte de onder 1, 2 en 3 ten laste gelegde feiten heeft begaan zoals hiervoor in rubriek 4.3 is vermeld. Verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd dan hiervoor is bewezen verklaard en spreekt verdachte daarvan vrij. Het bewezen verklaarde levert op:  ten aanzien van het onder 1 bewezenverklaarde:  eenvoudige belediging, meermalen gepleegd;  ten aanzien van het onder 2 en 3 bewezenverklaarde:  bedreiging met enig misdrijf tegen het leven gericht, meermalen gepleegd. Verklaart het bewezene strafbaar. Verklaart verdachte, [verdachte], daarvoor strafbaar. **Veroordeelt verdachte tot een taakstraf van 40 (veertig) uren**. Beveelt, voor het geval dat de verdachte de taakstraf niet naar behoren heeft verricht, dat vervangende hechtenis zal worden toegepast van 20 (twintig) dagen. Beveelt dat de tijd die door verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering is doorgebracht, bij de uitvoering van deze straf geheel in mindering zal worden gebracht naar de maatstaf van 2 (twee) uren per dag. Beveelt dat een gedeelte, groot 20 (twintig) uren, van deze taakstraf niet ten uitvoer zal worden gelegd, tenzij later anders wordt gelast. Stelt daarbij een proeftijd van 2 (twee) jaren vast. De tenuitvoerlegging kan worden gelast indien de veroordeelde zich voor het einde van de proeftijd schuldig maakt aan een strafbaar feit. Dit vonnis is gewezen door mr. M.T.C. de Vries,  voorzitter, mrs. P.L.C.M. Ficq en O.P.M. Fruytier, rechters, in tegenwoordigheid van mr. H.L. van Loon,  griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank van 3 december 2021.

- MATCH TAAKSTRAF: taakstraf van 40 (veertig) uren
- MATCH HECHTENIS: niet naar behoren heeft verricht, dat vervangende hechtenis zal worden toegepast van 20 (twintig) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd dan hiervoor is bewezen verklaard en spreekt verdachte daarvan vrij. Het bewezen verklaarde levert op:  ten aanzien v
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 2, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 0, 2, 0, 0)

TP: 1
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBAMS:2021:765
=============================
TEXT:
8 De beslissing De rechtbank komt op grond van het voorgaande tot de volgende beslissing. Verklaart bewezen dat verdachte het tenlastegelegde heeft begaan zoals hiervoor in rubriek 4 is vermeld. Verklaart niet bewezen wat aan verdachte meer of anders is tenlastegelegd dan hiervoor is bewezen verklaard en spreekt verdachte daarvan vrij. Het bewezen verklaarde levert op:  diefstal, gevolgd van geweld of bedreiging met geweld tegen personen, gepleegd met het oogmerk om, bij betrapping op heterdaad, aan zichzelf hetzij de vlucht mogelijk te maken, hetzij het bezit van het gestolene te verzekeren  Legt op de maatregel tot plaatsing in een inrichting voor stelselmatige daders voor de duur van 2 (twee) jaren. Dit vonnis is gewezen door mr. R.C.J. Hamming,        voorzitter, mrs. C.P.E. Meewisse, J.M. Jongkind,         rechters, in tegenwoordigheid van mr. J.G.R. Becker,         griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank van 25 februari 2021.

- MATCH VRIJSPRAAK: meer of anders is tenlastegelegd dan hiervoor is bewezen verklaard en spreekt verdachte daarvan vrij. Het bewezen verklaarde levert op:  diefstal, gev
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)


TP: 0
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBGEL:2021:2304
=============================
TEXT:
4 De beslissing De rechtbank:   **spreekt verdachte vrij van het tenlastegelegde**;   verklaart de benadeelde partij [slachtoffer 1] niet-ontvankelijk in de vordering tot immateriële schade. Dit vonnis is gewezen door mr. R.W.H. van Brandenburg, voorzitter, mr. J.M.J.M. Doon en mr. E.H.T. Rademaker, rechters, in tegenwoordigheid van mr. V. Stroink, griffier, en uitgesproken ter openbare terechtzitting van deze rechtbank op 29 april 2021.

- MATCH VRIJSPRAAK: spreekt verdachte vrij van het tenlastegelegde;   verklaart de benadeeld
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 1
FP: 0
TN: 0
FN: 0


CASE: ECLI:NL:RBGEL:2021:3033
=============================
TEXT:
9 De beslissing De rechtbank: **spreekt verdachte vrij van het primair ten laste gelegde feit**;   verklaart bewezen dat verdachte het subsidiair ten laste gelegde feit, zoals vermeld onder ‘De bewezenverklaring’, heeft begaan;   verklaart niet bewezen hetgeen verdachte meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplevert het strafbare feit zoals vermeld onder ‘De kwalificatie van het bewezenverklaarde’;   verklaart verdachte hiervoor strafbaar;   veroordeelt verdachte wegens het bewezenverklaarde tot een **gevangenisstraf voor de duur van 12 maanden**;   bepaalt dat een gedeelte van deze gevangenisstraf, te weten 5 maanden, niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten, omdat verdachte zich voor het einde van de proeftijd van drie jaren niet heeft gehouden aan de volgende voorwaarden: stelt als algemene voorwaarde dat verdachte zich niet schuldig maakt aan een strafbaar feit; stelt als bijzondere voorwaarden dat: - verdachte zich binnen 14 dagen na het ingaan van de proeftijd zal melden bij Reclassering Leger des Heils op het adres Utrechtsestraat 47, 6811 LT Arnhem en zich gedurende de proeftijd zal blijven melden bij de reclassering, zo vaak en zolang de reclassering dat nodig vindt; - verdachte meewerkt aan ambulante begeleiding door een nader te bepalen instelling voor ambulante forensische begeleiding en zich houdt aan de afspraken die de instelling in overleg met de reclassering voor hem heeft opgesteld. De begeleiding duurt de gehele proeftijd of zoveel korter als de reclassering nodig vindt; - verdachte meewerkt aan het realiseren van dagbesteding in de vorm van betaalde arbeid, vrijwilligerswerk of anderszins dagbesteding voor de duur van de proeftijd of zoveel korter als de reclassering nodig vindt; - verdachte meewerkt aan controle van het gebruik van alcohol en drugs om het middelengebruik te beheersen, waarbij de reclassering urinecontrole en ademonderzoek (blaastest) kan gebruiken voor de controle en waarbij de reclassering bepaalt hoe vaak hij wordt gecontroleerd;   stelt als overige voorwaarden dat: verdachte zijn medewerking zal verlenen aan het ten behoeve van het vaststellen van zijn identiteit afnemen van een of meer vingerafdrukken of een identiteitsbewijs als bedoeld in artikel 1 van de Wet op de identificatieplicht ter inzage zal aanbieden; verdachte zijn medewerking zal verlenen aan het reclasseringstoezicht als bedoeld in artikel 14c van het Wetboek van Strafrecht. De medewerking aan huisbezoeken en het zich melden bij de reclasseringsinstelling zo vaak en zolang de reclassering dit noodzakelijk acht zijn daaronder begrepen;   geeft opdracht aan de reclassering tot het houden van toezicht op de naleving van deze bijzondere voorwaarden en tot begeleiding van verdachte ten behoeve daarvan;   beveelt dat de tijd, door verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering en voorlopige hechtenis doorgebracht, bij de uitvoering van de opgelegde gevangenisstraf in mindering zal worden gebracht. Dit vonnis is gewezen door mr. C.H.M. Pastoors (voorzitter), mr. M.G.E. ter Hart en mr. W. Oosterbaan, rechters, in tegenwoordigheid van mr. L.R. van Damme, griffier, en uitgesproken ter openbare terechtzitting van deze rechtbank op 17 juni 2021.

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 12 maanden
- MATCH GEVANGENISSTRAF: gevangenisstraf, te weten 5 maanden, niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten, omdat verdachte zich voor het einde van de proeftijd van drie jaren niet
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: spreekt verdachte vrij van het primair ten laste gelegde feit;   verklaa
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplev
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 365, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 365, 0, 0, 0, 1)

TP: 2
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBGEL:2021:4518
=============================
TEXT:
10 De beslissing De rechtbank:   verklaart bewezen dat verdachte het tenlastegelegde, zoals vermeld onder ‘De bewezenverklaring’, heeft begaan;   verklaart niet bewezen hetgeen verdachte meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplevert de strafbare feiten zoals vermeld onder ‘De kwalificatie van het bewezenverklaarde’;   verklaart verdachte hiervoor strafbaar;   veroordeelt verdachte wegens het bewezenverklaarde **tot een gevangenisstraf voor de duur van negen maanden**;   bepaalt dat een gedeelte van deze gevangenisstraf, te weten vier maanden, niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten omdat verdachte zich voor het einde van de proeftijd van drie jaren niet heeft gehouden aan de volgende voorwaarden:   stelt als algemene voorwaarde dat verdachte zich niet schuldig maakt aan een strafbaar feit;   stelt als bijzondere voorwaarde dat:  contactverbod - verdachte gedurende de proeftijd op geen enkele wijze – direct of indirect – contact zal opnemen, zoeken of hebben met [slachtoffer] zolang het Openbaar Ministerie dit nodig vindt. De politie ziet toe op handhaving van dit contactverbod;   beveelt dat de tijd, door verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering en voorlopige hechtenis doorgebracht, bij de uitvoering van de opgelegde gevangenisstraf in mindering zal worden gebracht; veroordeelt verdachte in verband met het feit onder nummer 1 en 2 tot betaling van schadevergoeding aan de benadeelde partij [getuige 1] van € 37,48 aan materiële schade en € 1.500,- aan smartengeld, vermeerderd met de wettelijke rente vanaf 22 november 2019 tot aan de dag dat het hele bedrag is betaald; veroordeelt verdachte in de kosten die de benadeelde partij in deze procedure heeft gemaakt en de kosten die de benadeelde partij mogelijk nog moet maken om het toegewezen bedrag betaald te krijgen, tot vandaag begroot op € 35,88; legt aan verdachte de verplichting op om aan de Staat, ten behoeve van benadeelde partij [getuige 1] , een bedrag te betalen van € 37,48 aan materiële schade en € 1.500,- aan smartengeld. Dit wordt vermeerderd met de wettelijke rente vanaf 22 november 2019 tot aan de dag dat het hele bedrag is betaald. Als dit bedrag niet wordt betaald, kunnen 25 dagen gijzeling worden toegepast zonder dat de betalingsverplichting vervalt; bepaalt daarbij dat met betaling aan de benadeelde partij in zoverre de betaling aan de Staat vervalt en omgekeerd;   verklaart de vordering van de benadeelde partij voor het overige niet-ontvankelijk. Dit vonnis is gewezen door mr. A.J.H. Steenweg (voorzitter), mr. M.E. Snijders en mr. P. Verkroost rechters, in tegenwoordigheid van mr. K.M. Rokette, griffier, en uitgesproken ter openbare terechtzitting van deze rechtbank op 6 augustus 2021. mr. A.J.H. Steenweg, mr. M.E. Snijders en mr. K.M. Rokette zijn buiten staat dit vonnis mede te ondertekenen.

- MATCH BETALING: betaling van schadevergoeding aan de benadeelde partij [getuige 1] van € 37,48 aan materiële 
    * Measure for compensation detected. Skipped.
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplev
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 2
FN: 1


CASE: ECLI:NL:RBGEL:2021:6569
=============================
TEXT:
9 De beslissing De rechtbank:   verklaart bewezen dat verdachte de ten laste gelegde feiten, zoals vermeld onder ‘De bewezenverklaring’, heeft begaan;   verklaart niet bewezen hetgeen verdachte meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplevert de strafbare feiten zoals vermeld onder ‘De kwalificatie van het bewezenverklaarde’;   verklaart verdachte hiervoor strafbaar;   legt op de maatregel van plaatsing in een inrichting voor stelselmatige daders voor de duur van 2 (twee) jaar;   **wijst af het verzoek tot opheffing van de voorlopige hechtenis**. Dit vonnis is gewezen door mr. J.M. Breimer (voorzitter), mr. A. Tegelaar en mr. M.P. Bos, rechters, in tegenwoordigheid van mr. J.C.M. Vogelpoel, griffier, en uitgesproken ter openbare terechtzitting van deze rechtbank op 8 december 2021. Mr. A. Tegelaar en Mr. M.P. Bos zijn buiten staat dit vonnis mede te ondertekenen

- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplev
    * 'ne bis in idem' detected. Skipped.
- MATCH VRIJSPRAAK: wijst af het verzoek tot opheffing van de voorlopige hecht
-  OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 1
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBGEL:2021:6833
=============================
TEXT:
10 De beslissing De rechtbank: **spreekt verdachte vrij** van de onder parketnummer 05/220228-21 en parketnummer 05/234089-21 ten laste gelegde feiten;   verklaart bewezen dat verdachte de overige ten laste gelegde feiten, zoals vermeld onder ‘De bewezenverklaring’, heeft begaan;   verklaart niet bewezen hetgeen verdachte meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplevert de strafbare feiten zoals vermeld onder ‘De kwalificatie van het bewezenverklaarde’;   verklaart verdachte hiervoor strafbaar;   veroordeelt verdachte wegens het bewezenverklaarde tot een **gevangenisstraf voor de duur van 4 (vier) weken**;   beveelt dat de tijd, door verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering en in voorlopige hechtenis doorgebracht, bij de uitvoering van de opgelegde gevangenisstraf in mindering zal worden gebracht; veroordeelt verdachte in verband met de zaak met parketnummer 05/216680-21 feit 1 tot betaling van schadevergoeding aan de benadeelde partij [benadeelde] van € 32,- (tweeëndertig euro) aan materiële schade, vermeerderd met de wettelijke rente vanaf 10 juli 2021 tot aan de dag dat het hele bedrag is betaald; veroordeelt verdachte in de kosten die de benadeelde partij in deze procedure heeft gemaakt en de kosten die de benadeelde partij mogelijk nog moet maken om het toegewezen bedrag betaald te krijgen, tot vandaag begroot op nul;   verklaart de benadeelde partij [benadeelde] voor het overige niet-ontvankelijk in de vordering tot materiële schade; legt aan verdachte de verplichting op om aan de Staat, ten behoeve van benadeelde partij [benadeelde] , een bedrag te betalen van € 32,- aan materiële schade. Dit wordt vermeerderd met de wettelijke rente vanaf 10 juli 2021 tot aan de dag dat het hele bedrag is betaald. Als dit bedrag niet wordt betaald, kan 1 dag gijzeling worden toegepast zonder dat de betalingsverplichting vervalt; bepaalt daarbij dat met betaling aan de benadeelde partij in zoverre de betaling aan de Staat vervalt en omgekeerd. Dit vonnis is gewezen door mr. Y. Yeniay-Cenik, voorzitter, mr. C. Kleinrensink en mr. J.M.J.M. Doon, rechters, in tegenwoordigheid van mr. E.A. Clevers, griffier, en uitgesproken ter openbare terechtzitting van deze rechtbank op 20 december 2021.

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 4 (vier) weken
- MATCH BETALING: betaling van schadevergoeding aan de benadeelde partij [benadeelde] van € 32,- (tweeëndertig 
    * Measure for compensation detected. Skipped.
- MATCH VRIJSPRAAK: spreekt verdachte vrij van de onder parketnummer 05/220228-21 en parketn
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en spreekt verdachte daarvan vrij;   verstaat dat het aldus bewezenverklaarde oplev
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 28, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 28, 0, 0, 0, 1)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBLIM:2021:5488
=============================
TEXT:
9 De beslissing  De rechtbank:  Vrijspraak - **spreekt de verdachte vrij van de feiten 1 en 4** in de zaak 03/702623-15 en feit 3 in de zaak 03/702645-17;  Bewezenverklaring verklaart de feiten 2, 3, 5 en 6 in de zaak 03/702623-15 en feit 1 in de zaak 03/702645-17 bewezen zoals hierboven onder 3.5 is omschreven; spreekt de verdachte vrij van wat meer of anders is ten laste gelegd;  Strafbaarheid verklaart dat het bewezenverklaarde de strafbare feiten oplevert zoals hierboven onder 4 is omschreven; verklaart de verdachte strafbaar;  Straf veroordeelt de verdachte voor de feiten 2, 3, 5 en 6 in de zaak 03/702623-15 en feit 1 in de zaak 03/702645-17 tot een **gevangenisstraf van 36 maanden**; beveelt dat de tijd die door de veroordeelde vóór de tenuitvoerlegging van deze uitspraak in voorarrest is doorgebracht, bij de uitvoering van deze gevangenisstraf in mindering zal worden gebracht; verstaat dat tenuitvoerlegging van de opgelegde gevangenisstraf volledig zal plaatsvinden binnen de penitentiaire inrichting, tot het moment dat de verdachte in aanmerking komt voor deelname aan een penitentiair programma, als bedoeld in artikel 4 Penitentiaire beginselenwet of tot het moment dat de regeling van voorwaardelijke invrijheidsstelling aan de orde is, als bedoeld in artikel 6:2:10 Wetboek van Strafvordering. Dit vonnis is gewezen door mr. L.P. Bosma, voorzitter, mr. M.J.A.G. van Baal en mr. L. Feuth, rechters, in tegenwoordigheid van mr. H.M.E. de Beukelaer en mr. O.A.G. Corten, griffiers, en uitgesproken ter openbare zitting van 9 juli 2021.

- MATCH GEVANGENISSTRAF: gevangenisstraf van 36 maanden
- MATCH TBS: ter beschikking gestelde foto.  Belgisch grondgebied Omstreeks 13.24 uur hebben wij terug controle op de Nissan. De bestuur
    * WARNING: neither 'verlenging' nor 'type' of TBS detected. Skipped.
- MATCH VRIJSPRAAK: Vrijspraak - spreekt de verdachte vrij van de feiten 1 en 4 
- MATCH VRIJSPRAAK: spreekt de verdachte vrij van wat meer of anders is ten laste gelegd
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 1095, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 1095, 0, 0, 0, 1)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBLIM:2021:5570
=============================
TEXT:
4 De beslissing  De rechtbank:  Vrijspraak - **spreekt de verdachte vrij**. Dit vonnis is gewezen door mr. L.P. Bosma, voorzitter, mr. M.J.A.G. van Baal en mr. L. Feuth, rechters, in tegenwoordigheid van mr. H.M.E. de Beukelaer en mr. O.A.G. Corten, griffiers, en uitgesproken ter openbare zitting van 9 juli 2021.  BIJLAGE I: De tenlastelegging Aan de verdachte is ten laste gelegd dat: hij in of omstreeks de periode van 1 januari 2014 tot en met 27 mei 2015 in de gemeente Echt-Susteren en/of de gemeente Sittard-Geleen en/of de gemeente Roermond en/of de gemeente Valkenswaard en/of de gemeente Heerlen en/of de gemeente Kerkrade en/of de gemeente Schinnen, in elk geval in Nederland en/of te Borgloon (B), in elk geval in België en/of te Selfkant en/of te Alsdorf, in elk geval in Duitsland, heeft deelgenomen aan een organisatie, bestaande uit een samenwerkingsverband van natuurlijke personen, te weten de leden van MC Bandidos (chapter Sittard) en/of een samenwerkingsverband bestaande uit (onder meer) de volgende personen: [verdachte 6] en/of [verdachte 1] en/of [verdachte 7] en/of [verdachte 10]  en/of [verdachte 5] en/of [verdachte 2] en/of [verdachte 3] en/of [verdachte 4] en/of [verdachte 9] en/of [verdachte 8] en/of          [verdachte 13] en/of [verdachte 14] en/of [verdachte 11] en/of [verdachte 12]  en/of [verdachte 15] en/of [verdachte 17] en/of [verdachte 21] en/of [verdachte 22]  en/of [verdachte 16] , welke organisatie tot oogmerk had het plegen van misdrijven te weten: - afpersing (art. 317 Sr) en/of - diefstal met geweld (art. 312 Sr) en/of - bedreiging (art. 285 Sr) en/of - openlijk geweld (art. 141 Sr) en/of - verboden wapenbezit (art. 26 WWM); (zaak 1).

- MATCH VRIJSPRAAK: Vrijspraak - spreekt de verdachte vrij. Dit vonnis is geweze
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 1
FP: 0
TN: 0
FN: 0


CASE: ECLI:NL:RBMNE:2021:5182
=============================
TEXT:
5 BESLISSING De rechtbank: - stelt het bedrag waarop het door de veroordeelde wederrechtelijk verkregen voordeel wordt geschat vast op € 3.800,-; - legt de veroordeelde de verplichting op tot betaling van € 3.800,- aan de staat ter ontneming van het wederrechtelijk verkregen voordeel; - veroordeelde is voor dit bedrag hoofdelijk aansprakelijk met dien verstande dat indien en voor zover de mededader van veroordeelde betaalt, veroordeelde in zoverre van deze verplichting zal zijn bevrijd. - bepaalt de duur van de gijzeling die met toepassing van artikel 6:6:25 van het Wetboek van Strafvordering ten hoogste kan worden gevorderd op 152 dagen. Dit vonnis is gewezen door mr. E.H.M. Druijf, voorzitter, mrs. N.P.J. Janssens en A. Bouteibi, rechters, in tegenwoordigheid van mr. E.E. van Wiggen-van der Hoek, griffier, en is uitgesproken op de openbare terechtzitting van 26 oktober 2021. Mr. A. Bouteibi en de griffier zijn buiten staat dit vonnis mede te ondertekenen.

- MATCH BETALING: betaling van € 3.800,- aan de staat ter ontneming van het wederrechtelijk
    * Measure to return unlawfully obtained advantages detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBNNE:2021:2888
=============================
TEXT:
Beslissing op de vordering na voorwaardelijke veroordeling onder parketnummer Gelast de tenuitvoerlegging van de straf voor zover voorwaardelijk opgelegd bij vonnis van de politierechter van de Rechtbank Noord-Nederland, locatie Groningen van 12 februari 2021, te weten: een **taakstraf van 20 uren**. Dit vonnis is gewezen door mr. M.B.W. Venema, voorzitter, mr. M.S. van der Kuijl en mr. H.J. Schuth, rechters, bijgestaan door mr. A.C. Fennema-Smit, griffier, en uitgesproken ter openbare terechtzitting van deze rechtbank op 12 juli 2021.

- MATCH TAAKSTRAF: taakstraf van 20 uren
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 1, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 0, 1, 0, 0)

TP: 1
FP: 0
TN: 0
FN: 0


CASE: ECLI:NL:RBOVE:2021:1717
=============================
TEXT:
9 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte de onder 1, 2, en 3 ten laste gelegde feiten heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het onder 1, 2 en 3 bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde de volgende strafbare feiten oplevert:  feit 1: het misdrijf: Handelen in strijd met artikel 26 eerste lid van de Wet wapens en munitie en het feit begaan met betrekking tot een wapen van categorie II, meermalen gepleegd, en handelen in strijd met artikel 26 eerste lid van de Wet wapens en munitie en het feit begaan met betrekking tot een vuurwapen van categorie III, meermalen gepleegd, en handelen in strijd met artikel 26 eerste lid van de Wet wapens en munitie en het feit begaan met betrekking tot munitie, meermalen gepleegd.  feit 2 en feit 3: telkens het misdrijf: handelen in strijd met artikel 26 eerste lid van de Wet wapens en munitie en handelen in strijd met artikel 31 eerste lid van de Wet wapens en munitie.  strafbaarheid verdachte - verklaart verdachte strafbaar voor het onder 1, 2 en 3 bewezen verklaarde;  straf - veroordeelt verdachte tot een **gevangenisstraf voor de duur van 12 (twaalf) maanden**; - bepaalt dat de tijd die de verdachte voor de tenuitvoerlegging van deze uitspraak in verzekering en voorlopige hechtenis heeft doorgebracht, bij de uitvoering van de gevangenisstraf geheel in mindering zal worden gebracht;  opheffing schorsing voorlopige hechtenis - heft op de schorsing van de voorlopige hechtenis met ingang van heden; Dit vonnis is gewezen door mr. S. Taalman, voorzitter, mr. drs. H.M. Braam en mr. D ten Boer, rechters, in tegenwoordigheid van mr. J.M. van Westerlaak, griffier, en is in het openbaar uitgesproken op: 26 april 2021.

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 12 (twaalf) maanden
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het onder 1, 2 e
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 365, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 365, 0, 0, 0, 0)

TP: 1
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBOVE:2021:1784
=============================
TEXT:
11 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte het tenlastegelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en spreekt hem daarvan vrij; - verklaart dat het bewezenverklaarde oplevert:  feit 1 primair Het misdrijf: poging tot doodslag  Feit 2 Het misdrijf: poging tot toebrengen zwaar lichamelijk letsel, meermalen gepleegd  Feit 3 Het misdrijf: bedreiging, meermalen gepleegd - verklaart het bewezen verklaarde niet strafbaar en ontslaat verdachte van alle rechtsvervolging daarvan;  schadevergoeding - bepaalt dat de benadeelde partijen [slachtoffer 1] , [slachtoffer 2] en [slachtoffer 3] in het geheel niet-ontvankelijk zijn in de vorderingen en dat de benadeelde partijen de vorderingen slechts bij de burgerlijke rechter kunnen aanbrengen;  opheffing bevel voorlopige hechtenis - heft op het geschorste bevel tot voorlopige hechtenis. Dit vonnis is gewezen door mr. J. Faber, voorzitter, mr. A. van Holten en mr. M. van Bruggen, rechters, in tegenwoordigheid van mr. O.R.R. Hetterscheidt, griffier, en is in het openbaar uitgesproken op 29 april 2021.

- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij; - verklaart dat het bewezenverklaarde oplevert: 
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBOVE:2021:2379
=============================
TEXT:
9 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte het primair ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte primair meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het bewezenverklaarde strafbaar; - verklaart dat het bewezenverklaarde het volgende strafbare feit oplevert:  het misdrijf: overtreding van een voorschrift,  gesteld krachtens artikel 9.2.2.1 van de Wet milieubeheer, juncto artikel 1.2.2 lid 3 van het Vuurwerkbesluit, opzettelijk begaan.  strafbaarheid verdachte - verklaart verdachte strafbaar voor het bewezenverklaarde;  straf - veroordeelt verdachte tot een **gevangenisstraf voor de duur van 6 (zes) maanden**; - bepaalt dat deze gevangenisstraf in zijn geheel niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten. De rechter kan de tenuitvoerlegging gelasten indien verdachte voor het einde van de proeftijd van 3 (drie) jaren de navolgende voorwaarde niet is nagekomen: - stelt als algemene voorwaarde dat verdachte: - zich voor het einde van de proeftijd niet schuldig maakt aan een strafbaar feit; - veroordeelt verdachte tot een **taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 215 (tweehonderdvijftien) uren**; - beveelt, voor het geval dat verdachte de taakstraf niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 107 (honderdzeven) dagen;  het inbeslaggenomen voorwerp - gelast de teruggave van het geldbedrag van € 5.700,00 aan verdachte. Dit vonnis is gewezen door mr. M. Melaard, voorzitter, mr. J. Wentink en mr. M. van Berlo, rechters, in tegenwoordigheid van mr. J. Izgi, griffier, en is in het openbaar uitgesproken op 14 juni 2021. Mr. M. Melaard, mr. J. Wentink en mr. J. Izgi zijn buiten staat dit vonnis mede te ondertekenen.

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 6 (zes) maanden
- MATCH TAAKSTRAF: taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 215 (tweehonderdvijftien) uren
- MATCH HECHTENIS: niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 107 (honderdzeven) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het bewezenverkl
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 182, 'hechtenis': 0, 'taakstraf': 9, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 182, 0, 9, 0, 0)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBOVE:2021:3523
=============================
TEXT:
5 De beslissing De rechtbank verklaart niet bewezen dat verdachte het primair en subsidiair ten laste gelegde heeft begaan en **spreekt haar daarvan vrij**; Dit vonnis is gewezen door mr. J. de Ruiter, voorzitter, mr. H. Manuel en mr. B. Roodveldt, rechters, in tegenwoordigheid van mr. H.R. Lageveen, griffier, en is in het openbaar uitgesproken op 14 september 2021. Mr. B. Roodveldt  is niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH VRIJSPRAAK: spreekt haar daarvan vrij; Dit vonnis is gewezen door mr. J. de Ruiter, voo
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 1
FP: 0
TN: 0
FN: 0


CASE: ECLI:NL:RBOVE:2021:3609
=============================
TEXT:
9 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte het onder 1, 2 en 3 ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feiten - verklaart het bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde de volgende strafbare feiten oplevert: feit 1, het misdrijf: valsheid in geschrift feit 2, het misdrijf: valsheid in geschrift, meermalen gepleegd feit 3, het misdrijf: in de gevallen, waarin een wettelijk voorschrift een verklaring onder ede vordert, schriftelijk, persoonlijk, opzettelijk een valse verklaring onder ede afleggen, meermalen gepleegd  strafbaarheid verdachte - verklaart verdachte strafbaar voor het onder 1, 2 en 3 bewezen verklaarde;  straf - veroordeelt de verdachte tot een **taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 100 (honderd) uren**; - beveelt, voor het geval dat de verdachte de taakstraf niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 50 (vijftig) dagen; Dit vonnis is gewezen door mr. H. Manuel, voorzitter, mr. G.H. Meijer en mr. R. ter Haar, rechters, in tegenwoordigheid van mr. W. Verhagen griffier, en is in het openbaar uitgesproken op 27 september 2021.  Buiten staat mr. R. ter Haar is niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH TAAKSTRAF: taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 100 (honderd) uren
- MATCH HECHTENIS: niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 50 (vijftig) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feiten - verklaart het bewezen ve
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 5, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 0, 5, 0, 0)

TP: 1
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBOVE:2021:4172
=============================
TEXT:
10 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte het ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde het volgende strafbare feit oplevert: het misdrijf: verduistering, gepleegd door hem die het goed uit hoofde van zijn persoonlijke dienstbetrekking onder zich heeft, meermalen gepleegd.  strafbaarheid verdachte - verklaart verdachte strafbaar voor het bewezen verklaarde;  straf - veroordeelt verdachte tot een **gevangenisstraf voor de duur van 3 (drie) maanden**; - bepaalt dat deze gevangenisstraf in zijn geheel niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten. De rechter kan de tenuitvoerlegging gelasten indien de verdachte voor het einde van de proeftijd van 3 (drie) jaren de navolgende voorwaarde niet is nagekomen: - stelt als algemene voorwaarde dat de verdachte: - zich voor het einde van de proeftijd niet schuldig maakt aan een strafbaar feit; - veroordeelt de verdachte tot een **taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 200 (tweehonderd) uren**; - beveelt, voor het geval dat de verdachte de taakstraf niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 100 (honderd) dagen; - beveelt dat de tijd die de verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering heeft doorgebracht, bij de uitvoering van de taakstraf in mindering wordt gebracht, waarbij als maatstaf geldt dat voor de eerste zestig dagen doorgebracht in verzekering of voorlopige hechtenis, twee uren en voor de resterende dagen één uur per dag aftrek plaatsvindt;  schadevergoeding - wijst de vordering van de benadeelde partij [zorginstelling] toe tot een bedrag van € 63.757,90 (bestaande uit materiële schade); - veroordeelt de verdachte tot betaling aan de benadeelde partij [zorginstelling] van een bedrag van € 63.757,90 (te vermeerderen met de wettelijke rente vanaf 14 juni 2018); - veroordeelt de verdachte daarnaast in de kosten van het geding door de benadeelde partij gemaakt, tot op heden begroot op nihil, alsook in de kosten van betekening van dit vonnis, de in verband met de tenuitvoerlegging van dit vonnis nog te maken kosten en de kosten vallende op de invordering; - legt de maatregel op dat de verdachte verplicht is ter zake van het bewezen verklaarde feit tot betaling aan de Staat der Nederlanden van een bedrag van € 63.757,90, (zegge: drieënzestigduizend zevenhonderdzevenenvijftig euro en negentig cent), te vermeerderen met de wettelijke rente vanaf 14 juni 2018 ten behoeve van de benadeelde, en bepaalt, voor het geval volledig verhaal van het verschuldigde bedrag niet mogelijk blijkt, dat gijzeling voor de duur van 330 dagen kan worden toegepast. Tenuitvoerlegging van de gijzeling laat de betalingsverplichting onverlet; - bepaalt dat als de verdachte heeft voldaan aan zijn verplichting tot betaling aan de Staat der Nederlanden van bedoeld bedrag daarmee de verplichting van de verdachte om aan de benadeelde partij het bedrag te betalen, komt te vervallen, en andersom, als de verdachte aan de benadeelde partij het verschuldigde bedrag heeft betaald, dat daarmee de verplichting tot betaling aan de Staat der Nederlanden van dat bedrag komt te vervallen. Dit vonnis is gewezen door mr. S.K. Huisman, voorzitter, mr. E. Venekatte en mr. J.T. Pouw, rechters, in tegenwoordigheid van mr. E.L. Vedder, griffier, en is in het openbaar uitgesproken op 8 november 2021. Buiten staat Mr. J.T. Pouw is niet in de gelegenheid dit vonnis mede te ondertekenen.  

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 3 (drie) maanden
- MATCH TAAKSTRAF: taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 200 (tweehonderd) uren
- MATCH HECHTENIS: niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 100 (honderd) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VORDERING: vordering van de benadeelde partij [zorginstelling] toe tot een bedrag van € 63.757,90 (bestaande uit
- MATCH BETALING: betaling aan de benadeelde partij [zorginstelling] van een bedrag van € 63.757,90 (te vermeerder
- MATCH BETALING: maatregel op dat de verdachte verplicht is ter zake van het bewezen verklaarde feit tot betaling aan de Staat der Nederlanden van een bedrag van € 63.757,90, (zegge: drieë
    * Measure ('maatregel') detected. Skipped
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het bewezen verk
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 91, 'hechtenis': 0, 'taakstraf': 9, 'geldboete': 127514, 'vrijspraak': 0}
    * (0, 91, 0, 9, 127514, 0)

TP: 2
FP: 2
TN: 2
FN: 0


CASE: ECLI:NL:RBOVE:2021:4354
=============================
TEXT:
9 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte het onder 1 primair en 2 primair ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en **spreekt hem daarvan vrij**;  strafbaarheid feiten - verklaart het onder 1 primair en 2 primair bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde de volgende strafbare feiten oplevert:  feit 1 primair het misdrijf:  Overtreding van voorschrift gesteld krachtens artikel 9.2.2.1. van de Wet milieubeheer, opzettelijk begaan.  feit 2 primair het misdrijf:  Overtreding van een voorschrift gesteld krachtens artikel 9.2.2.1. van de Wet milieubeheer, opzettelijk begaan.  strafbaarheid verdachte - verklaart verdachte strafbaar voor het onder 1 primair en 2 primair bewezen verklaarde;  straf - veroordeelt verdachte tot een **gevangenisstraf voor de duur van 4 (vier) maanden**; - bepaalt dat deze gevangenisstraf in zijn geheel niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten. De rechter kan de tenuitvoerlegging gelasten indien de verdachte voor het einde van de proeftijd van 3 (drie) jaren de navolgende voorwaarde(n) niet is nagekomen: stelt als algemene voorwaarde dat de verdachte: - zich voor het einde van de proeftijd niet schuldig maakt aan een strafbaar feit; - veroordeelt de verdachte tot een **taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 160 (honderdzestig) uren**; - beveelt, voor het geval dat de verdachte de taakstraf niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 80 (tachtig) dagen; - beveelt dat de tijd die de verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering heeft doorgebracht, bij de uitvoering van de taakstraf in mindering wordt gebracht, waarbij als maatstaf geldt dat voor de eerste zestig dagen doorgebracht in verzekering of voorlopige hechtenis, twee uren en voor de resterende dagen één uur per dag aftrek plaatsvindt;  de in beslag genomen voorwerpen - gelast de teruggave aan verdachte van het in beslag genomen voorwerp, te weten het op de beslaglijst genoemde voorwerp onder 2, te weten:   GSM/ iPhone (meisje op de achtergrond, sealbag nr. 38971527 (G_2398746, zwart, Apple). Dit vonnis is gewezen door mr. M. van Berlo, voorzitter, mr. M. Melaard en mr. D. ten Boer, rechters, in tegenwoordigheid van mr. J.M. van Westerlaak, griffier, en is in het openbaar uitgesproken op: 22 november 2021.

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 4 (vier) maanden
- MATCH TAAKSTRAF: taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 160 (honderdzestig) uren
- MATCH HECHTENIS: niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 80 (tachtig) dagen
* Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feiten - verklaart het onder 1 pr
* 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 121, 'hechtenis': 0, 'taakstraf': 7, 'geldboete': 0, 'vrijspraak': 0}
* (0, 121, 0, 7, 0, 0)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBOVE:2021:4510
=============================
TEXT:
5 De beslissing De rechtbank: stelt het bedrag waarop het door de veroordeelde wederrechtelijk verkregen voordeel wordt geschat vast op € 43.172,75. legt de veroordeelde de verplichting op tot betaling van € 43.172,75 aan de Staat ter ontneming van het wederrechtelijk verkregen voordeel; bepaalt de duur van de gijzeling die met toepassing van artikel 6:6:25 van het Wetboek van Strafvordering ten hoogste kan worden gevorderd op 863 dagen. Dit vonnis is gewezen door mr. V.P.K van Rosmalen, voorzitter, mr. N.J.C. Monincx en A.S. Metgod, rechters, in tegenwoordigheid van mr. Y.W. van den Bosch, griffier, en is in het openbaar uitgesproken op 2 december 2021. Mr. N.J.C. Monincx en mr. A.S. Metgod zijn niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH BETALING: betaling van € 43.172,75 aan de Staat ter ontneming van het wederrechtelijk
    * Measure to return unlawfully obtained advantages detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBOVE:2021:606
=============================
TEXT:
9 De beslissing De rechtbank:  bewezenverklaring - verklaart niet bewezen dat verdachte het onder 1 primair en 2 ten laste gelegde heeft begaan en **spreekt haar daarvan vrij**; - verklaart bewezen dat verdachte het onder 1 subsidiair ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte onder 1 subsidiair meer of anders is ten laste gelegd en spreekt haar daarvan vrij;  strafbaarheid feit - verklaart het bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde het volgende strafbare feit oplevert: het misdrijf: medeplichtigheid aan opzettelijk handelen in strijd met het in artikel 2 onder B van de Opiumwet gegeven verbod, meermalen gepleegd;  strafbaarheid verdachte - verklaart verdachte strafbaar voor het onder 1 subsidiair bewezen verklaarde;  straf - veroordeelt verdachte tot een **taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 60 (zestig) uren**; - beveelt, voor het geval dat verdachte de taakstraf niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 30 dagen; - beveelt dat de tijd die verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering heeft doorgebracht, bij de uitvoering van de taakstraf in mindering wordt gebracht, waarbij als maatstaf geldt dat twee uren per dag aftrek plaatsvindt. Dit vonnis is gewezen door mr. S.M. Milani, voorzitter, mr. A.M.G. Ellenbroek en mr. V. Wolting rechters, in tegenwoordigheid van mr. I. Potgieter, griffier, en is in het openbaar uitgesproken op 10 februari 2021.  Buiten staat De jongste rechter en de griffier zijn niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH TAAKSTRAF: taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 60 (zestig) uren
- MATCH HECHTENIS: niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 30 dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: spreekt haar daarvan vrij; - verklaart bewezen dat verdachte het onder 1 su
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt haar daarvan vrij;  strafbaarheid feit - verklaart het bewezen verk
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 3, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 3, 0, 1)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBOVE:2021:643
=============================
TEXT:
9 De beslissing De rechtbank:  bewezenverklaring - verklaart bewezen dat verdachte het ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde het volgende strafbare feit oplevert:  witwassen, meermalen gepleegd;  strafbaarheid verdachte - verklaart verdachte strafbaar voor het bewezen verklaarde;  straf - veroordeelt verdachte tot een **taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 60 (zestig) uren**; - beveelt, voor het geval dat verdachte de taakstraf niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 30 dagen; - beveelt dat de tijd die verdachte vóór de tenuitvoerlegging van deze uitspraak in verzekering heeft doorgebracht, bij de uitvoering van de taakstraf in mindering wordt gebracht, waarbij als maatstaf geldt dat voor de eerste 60 in verzekering of voorlopige hechtenis doorgebrachte dagen, twee uren en voor de resterende dagen één uur per dag aftrek plaatsvindt;  de inbeslaggenomen voorwerpen - heft het strafrechtelijk beslag op. Dit vonnis is gewezen door mr. M. Melaard, voorzitter, mr. M.B. Werkhoven en J. Wentink, rechters, in tegenwoordigheid van mr. E. Koning, griffier, en is in het openbaar uitgesproken op 15 februari 2021.

- MATCH TAAKSTRAF: taakstraf, bestaande uit het verrichten van onbetaalde arbeid voor de duur van 60 (zestig) uren
- MATCH HECHTENIS: niet naar behoren verricht, dat vervangende hechtenis zal worden toegepast voor de duur van 30 dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH TAAKSTRAF: taakstraf in mindering wordt gebracht, waarbij als maatstaf geldt dat voor de eerste 60 in verzekering of voorlopige hechtenis
    * 'in mindering' detected. Skipped.
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt hem daarvan vrij;  strafbaarheid feit - verklaart het bewezen verk
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 3, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 0, 3, 0, 0)

TP: 1
FP: 0
TN: 3
FN: 0


CASE: ECLI:NL:RBOVE:2021:75
=============================
TEXT:
10 De beslissing De rechtbank:  bewezenverklaring - verklaart niet bewezen dat verdachte het onder 1 ten laste gelegde heeft begaan en **spreekt haar daarvan vrij**; - verklaart bewezen dat verdachte het onder 2 primair ten laste gelegde heeft begaan, zoals hierboven omschreven; - verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en spreekt haar daarvan vrij;  strafbaarheid feit - verklaart het bewezen verklaarde strafbaar; - verklaart dat het bewezen verklaarde de volgende strafbare feiten oplevert: feit 2 primair het misdrijf: laster, meermalen gepleegd;  strafbaarheid verdachte - verklaart verdachte strafbaar voor het onder 2 primair bewezen verklaarde;  straf - **veroordeelt verdachte tot een gevangenisstraf voor de duur van 137 (honderdzevenendertig) dagen;** - bepaalt dat van deze gevangenisstraf een gedeelte van 120 (honderdtwintig) dagen niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten. De rechter kan de tenuitvoerlegging gelasten indien verdachte voor het einde van de proeftijd van 3 (drie) jaren de navolgende voorwaarde niet is nagekomen: - stelt als algemene voorwaarde dat verdachte: - zich voor het einde van de proeftijd niet schuldig maakt aan een strafbaar feit; - bepaalt dat de tijd die de verdachte voor de tenuitvoerlegging van deze uitspraak in verzekering en voorlopige hechtenis heeft doorgebracht, bij de uitvoering van de gevangenisstraf geheel in mindering zal worden gebracht;  
schadevergoedingen - veroordeelt verdachte tot betaling aan de benadeelde partij [naam 2] (feit 2 primair): van een bedrag van € 250,00, te vermeerderen met de wettelijke rente vanaf 11 november 2018; - veroordeelt verdachte daarnaast in de kosten van het geding door de benadeelde partij gemaakt, tot op heden begroot op nihil, alsook in de kosten van betekening van dit vonnis, de in verband met de tenuitvoerlegging van dit vonnis nog te maken kosten en de kosten vallende op de invordering; - legt de maatregel op dat verdachte verplicht is ter zake van de bewezen verklaarde feiten tot betaling aan de Staat der Nederlanden van een bedrag van € 250,00, te vermeerderen met de wettelijke rente vanaf 11 november 2018 ten behoeve van de benadeelde, en bepaalt, voor het geval volledig verhaal van het verschuldigde bedrag niet mogelijk blijkt, dat gijzeling voor de duur van 5 dagen kan worden toegepast. Tenuitvoerlegging van de gijzeling laat de betalingsverplichting onverlet; - bepaalt dat als verdachte heeft voldaan aan zijn verplichting tot betaling aan de Staat der Nederlanden van bedoeld bedrag daarmee de verplichting van verdachte om aan de benadeelde partij het bedrag te betalen, komt te vervallen, en andersom, als verdachte aan de benadeelde partij het verschuldigde bedrag heeft betaald, dat daarmee de verplichting tot betaling aan de Staat der Nederlanden van dat bedrag komt te vervallen; - bepaalt dat de benadeelde partij: [naam 2] , voor een deel van € 950,00 niet-ontvankelijk is in de vordering, en dat de benadeelde partij de vordering voor dat deel slechts bij de burgerlijke rechter kan aanbrengen; - veroordeelt verdachte tot betaling aan de benadeelde partij [naam 6] (feit 2 primair): van een bedrag van € 250,00, te vermeerderen met de wettelijke rente vanaf 12 september 2018; - veroordeelt verdachte daarnaast in de kosten van het geding door de benadeelde partij gemaakt, tot op heden begroot op nihil, alsook in de kosten van betekening van dit vonnis, de in verband met de tenuitvoerlegging van dit vonnis nog te maken kosten en de kosten vallende op de invordering; - legt de maatregel op dat verdachte verplicht is ter zake van de bewezen verklaarde feiten tot betaling aan de Staat der Nederlanden van een bedrag van € 250,00, te vermeerderen met de wettelijke rente vanaf 12 september 2018 ten behoeve van de benadeelde, en bepaalt, voor het geval volledig verhaal van het verschuldigde bedrag niet mogelijk blijkt, dat gijzeling voor de duur van 5 dagen kan worden toegepast. Tenuitvoerlegging van de gijzeling laat de betalingsverplichting onverlet; - bepaalt dat als verdachte heeft voldaan aan zijn verplichting tot betaling aan de Staat der Nederlanden van bedoeld bedrag daarmee de verplichting van verdachte om aan de benadeelde partij het bedrag te betalen, komt te vervallen, en andersom, als verdachte aan de benadeelde partij het verschuldigde bedrag heeft betaald, dat daarmee de verplichting tot betaling aan de Staat der Nederlanden van dat bedrag komt te vervallen; - bepaalt dat de benadeelde partij: [naam 6] , voor een deel van € 950,00 niet-ontvankelijk is in de vordering, en dat de benadeelde partij de vordering voor dat deel slechts bij de burgerlijke rechter kan aanbrengen. Dit vonnis is gewezen door mr. S.M. Milani, voorzitter, mr. J. Wentink en mr. M.W. Eshuis, rechters, in tegenwoordigheid van E.P. Endlich, griffier, en is in het openbaar uitgesproken op 12 januari 2021.  Buiten staat Mrs. Wentink en Eshuis zijn niet in de gelegenheid dit vonnis mede te ondertekenen.  

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 137 (honderdzevenendertig) dagen
- MATCH GEVANGENISSTRAF: gevangenisstraf een gedeelte van 120 (honderdtwintig) dagen niet ten uit
    * Negation ('niet ten uitvoer') detected. Skipped.
- MATCH BETALING: betaling aan de benadeelde partij [naam 2] (feit 2 primair): van een bedrag van € 250,00, te vermeerder
- MATCH BETALING: maatregel op dat verdachte verplicht is ter zake van de bewezen verklaarde feiten tot betaling aan de Staat der Nederlanden van een bedrag van € 250,00, te vermeerder
    * Measure ('maatregel') detected. Skipped
- MATCH BETALING: betaling aan de benadeelde partij [naam 6] (feit 2 primair): van een bedrag van € 250,00, te vermeerder
- MATCH BETALING: maatregel op dat verdachte verplicht is ter zake van de bewezen verklaarde feiten tot betaling aan de Staat der Nederlanden van een bedrag van € 250,00, te vermeerder
    * Measure ('maatregel') detected. Skipped
- MATCH VRIJSPRAAK: spreekt haar daarvan vrij; - verklaart bewezen dat verdachte het onder 2 pr
- MATCH VRIJSPRAAK: meer of anders is ten laste gelegd en spreekt haar daarvan vrij;  strafbaarheid feit - verklaart het bewezen verk
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 137, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 500, 'vrijspraak': 1}
    * (0, 137, 0, 0, 500, 1)

TP: 2
FP: 2
TN: 3
FN: 0


CASE: ECLI:NL:RBROT:2021:1932
=============================
TEXT:
10.  Beslissing  De rechtbank: verklaart bewezen dat de verdachte het ten laste gelegde feit, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert het hiervoor vermelde strafbare feit; verklaart de verdachte strafbaar; veroordeelt de verdachte tot een **jeugddetentie voor de duur van twee (2) dagen**; beveelt dat de tijd die door de veroordeelde voor de tenuitvoerlegging van deze uitspraak in verzekering en in voorlopige hechtenis is doorgebracht, bij de uitvoering van de opgelegde jeugddetentie in mindering wordt gebracht, voor zover deze tijd niet reeds op een andere vrijheidsstraf in mindering is gebracht; legt de verdachte een **taakstraf op, bestaande uit een werkstraf voor de duur van tachtig (80) uur**, waarbij de Raad voor de Kinderbescherming dient te bepalen uit welke werkzaamheden de werkstraf dient te bestaan; beveelt dat, voor het geval de veroordeelde de werkstraf niet naar behoren verricht, vervangende jeugddetentie zal worden toegepast voor de duur van veertig (40) dagen; bepaalt dat deze taakstraf niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten; verbindt hieraan een proeftijd, die wordt vastgesteld op twee jaren; tenuitvoerlegging kan worden gelast als de veroordeelde de algemene voorwaarde niet naleeft en ook als de veroordeelde gedurende de proeftijd een bijzondere voorwaarde niet naleeft of een voorwaarde die daaraan van rechtswege is verbonden; stelt als algemene voorwaarde dat de veroordeelde: - zich voor het einde van die proeftijd niet zal schuldig maken aan een strafbaar feit; stelt als bijzondere voorwaarden dat de veroordeelde: - zich gedurende een door de gecertificeerde instelling Jeugdbescherming Noord, gevestigd te Groningen, te bepalen periode (die loopt tot maximaal het einde van de proeftijd) en op door de jeugdreclassering te bepalen tijdstippen zal melden bij de jeugdreclassering, zo vaak en zo lang deze instelling dat noodzakelijk acht; - zijn medewerking verleent aan de maatregel Hulp en Steun, voor de duur van de proeftijd of zoveel korter als de jeugdreclassering noodzakelijk acht; - zich zal inspannen voor het hebben en behouden van een passende dagbesteding; - zijn medewerking zal verlenen aan een forensische GGZ-behandeling bij de Waag of een soortgelijke instelling, zolang als de jeugdreclassering dit noodzakelijk acht; verstaat dat van rechtswege de volgende voorwaarden zijn verbonden aan de hierboven genoemde bijzondere voorwaarden: - de veroordeelde zal ten behoeve van het vaststellen van zijn identiteit medewerking verlenen aan het nemen van één of meer vingerafdrukken of een identiteitsbewijs als bedoeld in artikel 1 van de Wet op de identificatieplicht ter inzage aanbieden;- de veroordeelde zal medewerking verlenen aan jeugdreclasseringstoezicht, de medewerking aan huisbezoeken daaronder begrepen en het zich melden bij de jeugdreclassering zo vaak en zolang als de jeugdreclassering dit noodzakelijk acht; geeft opdracht aan de gecertificeerde instelling Jeugdbescherming Noord, gevestigd te Groningen, tot het houden van toezicht op de naleving van voormelde bijzondere voorwaarden en de veroordeelde ten behoeve daarvan te begeleiden; Dit vonnis is gewezen door: mr. A. Verweij, voorzitter, tevens kinderrechter, en mrs. S.E.C. Debets en A.L. Pöll, rechters, in tegenwoordigheid van mr. L.F. Verhaart, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op 4 maart 2021. De jongste rechter en de griffier zijn buiten staat dit vonnis mede te ondertekenen. 

- MATCH JEUGDDETENTIE: jeugddetentie voor de duur van twee (2) dagen
- MATCH TAAKSTRAF: taakstraf op, bestaande uit een werkstraf voor de duur van tachtig (80) uur, waarbij de Ra
- MATCH JEUGDDETENTIE: niet naar behoren verricht, vervangende jeugddetentie zal worden toegepast voor de duur van veertig (40) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert h
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 2, 'taakstraf': 4, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 2, 4, 0, 0)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBROT:2021:2039
=============================
TEXT:
10. Beslissing  De rechtbank: verklaart niet bewezen, dat de verdachte het impliciet primair ten laste gelegde feit heeft begaan en **spreekt de verdachte daarvan vrij**; verklaart bewezen, dat de verdachte het impliciet subsidiair ten laste gelegde feit, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte ook daarvan vrij; stelt vast dat het bewezen verklaarde oplevert het hiervoor vermelde strafbare feit; verklaart de verdachte voor het bewezen verklaarde niet strafbaar en ontslaat de verdachte ten aanzien daarvan van alle rechtsvervolging; **gelast dat de verdachte ter beschikking wordt gesteld; stelt daarbij de navolgende voorwaarden** betreffende het gedrag van de terbeschikkinggestelde: 
de terbeschikkinggestelde verleent ten behoeve van het vaststellen van zijn identiteit medewerking aan het nemen van één of meer vingerafdrukken of biedt een identiteitsbewijs als bedoeld in artikel 1 van de Wet op de identificatieplicht ter inzage aan; 
de terbeschikkinggestelde zal zich niet schuldig maken aan het plegen van strafbare feiten; 
de terbeschikkinggestelde moet zich melden bij Reclassering Nederland, zolang en zo frequent als de reclassering dat nodig vindt en volgt de aanwijzingen op die hij krijgt; 
de terbeschikkinggestelde zal meewerken aan een time-out in een Forensisch Psychiatrisch Centrum (FPC) of een andere instelling, als de reclassering dat nodig vindt. Deze time-out duurt maximaal 7 weken, met de mogelijkheid van verlenging met nog eens maximaal 7 weken, tot maximaal 14 weken per jaar; 
de terbeschikkinggestelde zal niet naar het buitenland of naar de Nederlandse Antillen reizen, zonder toestemming van het openbaar ministerie; 
de terbeschikkinggestelde laat zich voor een periode van maximaal 24 maanden klinisch opnemen in de Forensisch Psychiatrische Kliniek van Fivoor te Rotterdam, of een soortgelijke door IFZ geïndiceerde zorginstelling, waarbij hij zich zal houden aan de aanwijzingen die hem in het kader van die behandeling door of namens de (geneesheer-) directeur van die instelling zullen worden gegeven, ook als de inname van medicatie onderdeel is van de behandeling; 
de terbeschikkinggestelde laat zich – aansluitend aan de klinische opname – ambulant behandelen door een nader te bepalen zorgverlener (te bepalen door de reclassering), waarbij hij zich zal houden aan de huisregels en de aanwijzingen die hem in het kader van de behandeling worden gegeven door de zorgverlener, ook als de inname van medicatie onderdeel is van de behandeling; 
de terbeschikkinggestelde werkt – aansluitend aan de klinische opname - mee aan plaatsing en verblijf in een instelling voor begeleid wonen of maatschappelijke opvang (te bepalen door de reclassering), waarbij hij zich houdt aan de huisregels en het dagprogramma dat de instelling in overleg met de reclassering voor hem heeft opgesteld, waarbij het verblijf duurt zolang dit door de reclassering nodig wordt geacht; 
de terbeschikkinggestelde gebruikt geen drugs- en alcohol. De controle op de naleving van deze voorwaarde zal ondersteund worden door middel van urineonderzoeken en/of ademonderzoeken (blaastesten), waarbij de reclassering bepaalt welk controlemiddel wordt ingezet en hoe vaak er wordt gecontroleerd; de ter beschikking gestelde zal op geen enkele wijze – direct of indirect - contact opnemen, zoeken of hebben met de heer [naam slachtoffer] , geboren op [geboortedatum slachtoffer] te [geboorteplaats slachtoffer] ; geeft aan Reclassering Nederland opdracht de terbeschikkinggestelde bij de naleving van de voorwaarden hulp en steun te verlenen; beveelt de onmiddellijke uitvoerbaarheid van de terbeschikkingstelling met voorwaarden; heft op het bevel tot voorlopige hechtenis van de verdachte met ingang van heden; **wijst af de gevorderde tenuitvoerlegging van de bij vonnis van 11 juni 2019 van de politierechter in deze rechtbank aan de veroordeelde opgelegde voorwaardelijke taakstraf**; bepaalt dat de bijzondere voorwaarden verbonden aan de bij vonnis van 11 juni 2019 van de politierechter in deze rechtbank aan de veroordeelde opgelegde voorwaardelijke taakstraf, komen te vervallen. Dit vonnis is gewezen door: mr. J.L.M. Boek, voorzitter, mr. C.E. Bos en mr. R.H. Kroon, rechters, in tegenwoordigheid van mr. C.Y. de Lange, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op de datum die in de kop van dit vonnis is vermeld. De oudste rechter en jongste rechter zijn buiten staat dit vonnis mede te ondertekenen. Bijlage I  Tekst tenlastelegging Aan de verdachte wordt ten laste gelegd dat hij op of omstreeks 6 augustus 2020 te Rotterdam, ter uitvoering van het door verdachte voorgenomen misdrijf om [naam slachtoffer] opzettelijk van het leven te beroven, althans zwaar lichamelijk letsel toe te brengen, meerdere malen, althans eenmaal, met een (stanley)mes, althans een scherp en/of puntig voorwerp, stekende en/of snijbewegingen heeft gemaakt in de richting van de romp en/of het bovenlichaam, althans het lichaam, van voornoemde          [naam slachtoffer] , terwijl hij, verdachte, voornoemde [naam slachtoffer] vast had en/of waardoor voornoemde [naam slachtoffer] in zijn arm is geraakt / gestoken / gesneden, terwijl de uitvoering van dat voorgenomen misdrijf niet is voltooid.

- MATCH TBS: ter beschikking wordt gesteld; stelt daarbij de navolgende voorwaarden
- MATCH TBS: ter beschikking gestelde zal op geen enkele wijze – direct of indirect - contact opnemen, zoeken of hebben met de heer [naa
- WARNING: neither 'verlenging' nor 'type' of TBS detected. Skipped.
- MATCH TBS: terbeschikkingstelling met voorwaarden
- MATCH VRIJSPRAAK: spreekt de verdachte daarvan vrij; verklaart bewezen, dat de verdachte het implicie
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte ook daarvan vrij; stelt vast dat het bewezen verklaarde oplevert h
    * 'ne bis in idem' detected. Skipped.
- MATCH VRIJSPRAAK: wijst af de gevorderde tenuitvoerlegging van de bij vonnis
- OUT: {'TBS': 1, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (1, 0, 0, 0, 0, 1)

TP: 4
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBROT:2021:4354
=============================
TEXT:
12 . Beslissing  De rechtbank: verklaart niet bewezen, dat de verdachte het onder 1 ten laste gelegde feit heeft begaan en **spreekt de verdachte daarvan vrij**; verklaart bewezen, dat de verdachte de onder 2, 3 en 4 ten laste gelegde feiten, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte (ook) daarvan vrij; stelt vast dat het bewezen verklaarde oplevert de hiervoor vermelde strafbare feiten; verklaart de verdachte strafbaar; 
**veroordeelt de verdachte tot een taakstraf voor de duur van 150 (honderdvijftig) uren**, waarbij de Reclassering Nederland dient te bepalen uit welke werkzaamheden de taakstraf dient te bestaan; beveelt dat de tijd die door de veroordeelde voor de tenuitvoerlegging van deze uitspraak in verzekering en in voorlopige hechtenis is doorgebracht, bij de uitvoering van de opgelegde taakstraf in mindering wordt gebracht volgens de maatstaf van twee uren per dag, zodat na deze aftrek 146 (honderdzesenveertig) uren te verrichten taakstraf resteert; beveelt dat, voor het geval de veroordeelde de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 73 dagen; bepaalt dat van deze taakstraf een gedeelte, groot 50 (vijftig) uren, niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten; verbindt hieraan een proeftijd, die wordt gesteld op twee jaar; tenuitvoerlegging kan worden gelast als de veroordeelde de algemene voorwaarde niet naleeft; stelt als algemene voorwaarde: de veroordeelde zal zich vóór het einde van de proeftijd niet aan een strafbaar feit schuldig maken; beslist ten aanzien van de voorwerpen, geplaatst op de lijst van inbeslaggenomen en nog niet teruggegeven voorwerpen, als volgt: gelast de teruggave aan verdachte van het geldbedrag van € 802,60 (beslagnummer G5976729 op 7 februari 2020); verklaart de benadeelde partij [naam benadeelde 1] niet-ontvankelijk in de vordering; veroordeelt de benadeelde partij in de kosten door de verdachte ter verdediging tegen de vordering gemaakt, en begroot deze kosten op nihil; verklaart de benadeelde partij [naam benadeelde 2] niet-ontvankelijk in de vordering; veroordeelt de benadeelde partij in de kosten door de verdachte ter verdediging tegen de vordering gemaakt, en begroot deze kosten op nihil. Dit vonnis is gewezen door: mr. V.F. Milders, voorzitter, en mrs. V.M. de Winkel en N. Freese, rechters, in tegenwoordigheid van M.J. Grootendorst, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op de datum die in de kop van dit vonnis is vermeld. De oudste rechter, de jongste rechter en de griffier zijn buiten staat dit vonnis mede te ondertekenen. Bijlage I  Tekst tenlastelegging Aan de verdachte wordt ten laste gelegd dat hij op of omstreeks 07 februari 2020 te Hoogvliet Rotterdam, gemeente Rotterdam alleen, althans tezamen en in vereniging met (een) ander(en), opzettelijk valse, vervalste of wederrechtelijk vervaardigde merken, te weten negenentwintig (29) trainingspakken van het merk Stone Island, en/of tweeëntwintig (22) trainingspakken van het merk Nike, heeft/hebben ingevoerd, doorgevoerd, uitgevoerd, verkocht, te koop heeft/hebben aangeboden, afgeleverd, uitgedeeld en/of in voorraad gehad; hij op of omstreeks 07 februari 2020 te Hoogvliet Rotterdam, gemeente Rotterdam alleen, althans tezamen en in vereniging met (een) ander(en), (een) wapen(s) van categorie III, onder 1 van de Wet wapens en munitie, te weten (een) vuurwapen(s) in de zin van artikel 1, onder 3º van die wet in de vorm van een pistool/revolver, - een gaspistool van het merk Retay, type Lord, kaliber 9mm pak en/of - een revolver van het merk Ekol, type Arda, kaliber 4mm flobert voorhanden heeft/hebben gehad; hij op of omstreeks 07 februari 2020 te Hoogvliet Rotterdam, gemeente Rotterdam alleen, althans tezamen en in vereniging met (een) ander(en), munitie in de zin van artikel 1 onder 4° van de Wet wapens munitie, te weten munitie als bedoeld in artikel 2 lid 2 van die wet, van de Categorie III, te weten - achtenzestig (68) stuks, kogelpatronen van het kaliber 4mm flobert en/of - negen (9) stuks, knal en/of gaspatronen van het kaliber 9mm voorhanden heeft/hebben gehad; hij op of omstreeks 07 februari 2020 te Hoogvliet Rotterdam, gemeente Rotterdam alleen, althans tezamen en in vereniging met (een) ander(en), een wapen van categorie I onder 7°, te weten - een speelgoed machinegeweer, zijnde een voorwerp dat voor wat betreft zijn vorm en afmetingen een sprekende gelijkenis vertoonde met een vuurwapen, te weten een automatisch vuurwapen, en/of - een speelgoed pistool, zijnde een voorwerp dat voor wat betreft zijn vorm en afmetingen een sprekende gelijkenis vertoonde met een vuurwapen, te weten een pistool voorhanden heeft/hebben gehad.

- MATCH TAAKSTRAF: taakstraf voor de duur van 150 (honderdvijftig) uren, waarbij de Re
- MATCH HECHTENIS: niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 73 dagen
* Negation detected at beginning or end of match. Skipped.
- MATCH TAAKSTRAF: taakstraf een gedeelte, groot 50 (vijftig) uren, niet ten uitv
* Negation ('niet ten uitvoer') detected. Skipped.
- MATCH VRIJSPRAAK: spreekt de verdachte daarvan vrij; verklaart bewezen, dat de verdachte de onder 2, 
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte (ook) daarvan vrij; stelt vast dat het bewezen verklaarde oplevert d
* 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 7, 'geldboete': 0, 'vrijspraak': 1}
* (0, 0, 0, 7, 0, 1)

TP: 2
FP: 0
TN: 3
FN: 0


CASE: ECLI:NL:RBROT:2021:7766
=============================
TEXT:
10. Beslissing  De rechtbank: verklaart bewezen, dat de verdachte het primair ten laste gelegde feit, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert het hiervoor vermelde strafbare feit; verklaart de verdachte strafbaar;  ontzegt de verdachte de bevoegdheid motorrijtuigen te besturen voor de tijd van 6 (zes) maanden; bepaalt dat deze ontzegging van de rijbevoegdheid niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten; verbindt hieraan een proeftijd, die wordt gesteld op 2 (twee) jaar; tenuitvoerlegging kan worden gelast als de veroordeelde de algemene voorwaarde niet naleeft; stelt als algemene voorwaarde dat de veroordeelde zich vóór het einde van de proeftijd niet aan een strafbaar feit schuldig zal maken; veroordeelt de verdachte tot een **taakstraf voor de duur van 90 (negentig) uren**, waarbij de Reclassering Nederland dient te bepalen uit welke werkzaamheden de taakstraf dient te bestaan; beveelt dat, voor het geval de veroordeelde de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 45 (vijfenveertig) dagen. Dit vonnis is gewezen door: mr. R.J.A.M. Cooijmans, voorzitter, en mrs. W.A.F. Damen en F.J.E. van Rossum, rechters, in tegenwoordigheid van mr. V.E. Scholtens, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op 27 juli 2021. De oudste rechter en de jongste rechter zijn buiten staat dit vonnis mede te ondertekenen. 

- MATCH TAAKSTRAF: taakstraf voor de duur van 90 (negentig) uren, waarbij de Re
- MATCH HECHTENIS: niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 45 (vijfenveertig) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert h
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 4, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 0, 4, 0, 0)

TP: 1
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBROT:2021:8751
=============================
TEXT:
10.  Beslissing  De rechtbank: verklaart bewezen dat de verdachte het ten laste gelegde feit, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezenverklaarde oplevert het hiervoor vermelde strafbare feit; verklaart de verdachte strafbaar; veroordeelt de verdachte tot een **taakstraf voor de duur van 80 (tachtig) uren**, waarbij Reclassering Nederland dient te bepalen uit welke werkzaamheden de taakstraf dient te bestaan; beveelt dat de tijd die door de veroordeelde voor de tenuitvoerlegging van deze uitspraak in verzekering en in voorlopige hechtenis is doorgebracht, bij de uitvoering van de opgelegde taakstraf in mindering wordt gebracht volgens de maatstaf van twee uren per dag, zodat na deze aftrek 74 (vierenzeventig) uren te verrichten taakstraf resteert; beveelt dat, voor het geval de veroordeelde de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 37 (zevenendertig) dagen; veroordeelt de verdachte tot een **gevangenisstraf voor de duur van 1 (één) maand**; bepaalt dat deze gevangenisstraf niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten; verbindt hieraan een proeftijd, die wordt gesteld op 2 (twee) jaar; tenuitvoerlegging kan worden gelast als de veroordeelde de algemene voorwaarde niet naleeft; stelt als algemene voorwaarde: de veroordeelde zal zich vóór het einde van de proeftijd niet aan een strafbaar feit schuldig maken. Dit vonnis is gewezen door: mr. A.M.G. van de Kragt, voorzitter, mrs. W.M. Stolk en A. Greve-Kortrijk, rechters, in tegenwoordigheid van mr. T.W. Veldhoen-Flier, griffieren uitgesproken op de openbare terechtzitting van deze rechtbank op de datum die in de kop van dit vonnis is vermeld. De jongste rechter en de griffier zijn buiten staat dit vonnis mede te ondertekenen. Bijlage I  Tekst tenlastelegging Aan de verdachte wordt ten laste gelegd dat hij op of omstreeks 6 februari 2021 te Rotterdam opzettelijk aanwezig heeft gehad een (grote) hoeveelheid zgn. XTC (te weten 151 pillen), althans een (grote) hoeveelheid van een materiaal bevattende MDMA en/of MDA en/of MDEA, zijnde MDMA en/of MDA en/of MDEA, een middel als bedoeld in de bij de Opiumwet behorende lijst I, dan wel aangewezen krachtens het vijfde lid van artikel 3a van die wet; (art 10 lid 3 Opiumwet, art 2 ahf/ond C Opiumwet)

- MATCH TAAKSTRAF: taakstraf voor de duur van 80 (tachtig) uren, waarbij Recla
- MATCH HECHTENIS: niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 37 (zevenendertig) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 1 (één) maand
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezenverklaarde oplevert he
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 30, 'hechtenis': 0, 'taakstraf': 4, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 30, 0, 4, 0, 0)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBROT:2021:8814
=============================
TEXT:
10 . Beslissing  De rechtbank: verklaart niet bewezen, dat de verdachte de in de zaak met parketnummer 10/093717-20 onder 1 primair en onder 2 primair ten laste gelegde feiten heeft begaan en **spreekt de verdachte daarvan vrij**; verklaart bewezen, dat de verdachte het in de zaak met parketnummer 10/047294-20 ten laste gelegde feit en de in de zaak met parketnummer 10/093717-20 onder 1 subsidiair, onder 2 subsidiair, 3 en 4 ten laste gelegde feiten, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte ook daarvan vrij; stelt vast dat het bewezen verklaarde oplevert de hiervoor vermelde strafbare feiten; verklaart de verdachte strafbaar; veroordeelt de verdachte voor de in de zaak met parketnummer 10/093717-20 onder 1 subsidiair, onder 2 subsidiair en 3 bewezenverklaarde feiten en het in de zaak onder parketnummer 10/047294-20 bewezenverklaarde feit tot een **gevangenisstraf voor de duur van 3 (drie) maanden**; veroordeelt de verdachte voor het in de zaak met parketnummer 10/093717-20 onder 4 bewezenverklaarde feit tot een **hechtenis voor de duur van 2 (twee) weken**; beveelt dat de tijd die door de veroordeelde voor de tenuitvoerlegging van deze uitspraak in de in de zaken onder beide parketnummers in verzekering en/of in voorlopige hechtenis is doorgebracht, bij de uitvoering van de opgelegde gevangenisstraf in mindering wordt gebracht, voor zover deze tijd niet reeds op een andere vrijheidsstraf in mindering is gebracht. Dit vonnis is gewezen door: mr. R. Brand, voorzitter, en mrs. A.M.J. van Buchem-Spapens en F.W.H. van den Emster, rechters, in tegenwoordigheid van J.P. van der Wijden, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op 26 augustus 2021. De oudste rechter, de jongste rechter en de griffier zijn buiten staat dit vonnis mede te ondertekenen. 

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 3 (drie) maanden
- MATCH HECHTENIS: hechtenis voor de duur van 2 (twee) weken
- MATCH VRIJSPRAAK: spreekt de verdachte daarvan vrij; verklaart bewezen, dat de verdachte het in de za
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte ook daarvan vrij; stelt vast dat het bewezen verklaarde oplevert d
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 91, 'hechtenis': 14, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 91, 14, 0, 0, 1)

TP: 3
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBROT:2021:8835
=============================
TEXT:
10 .Beslissing  De rechtbank: verklaart bewezen, dat de verdachte de ten laste gelegde feiten, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert de hiervoor vermelde strafbare feiten; verklaart de verdachte strafbaar; veroordeelt de verdachte tot een **gevangenisstraf voor de duur van 4 (vier) maanden**; bepaalt dat deze gevangenisstraf niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten; verbindt hieraan een proeftijd, die wordt gesteld op 2 (twee) jaar; tenuitvoerlegging kan worden gelast als de veroordeelde de algemene voorwaarde niet naleeft; stelt als algemene voorwaarde: - de veroordeelde zal zich vóór het einde van de proeftijd niet aan een strafbaar feit schuldig maken;  veroordeelt de verdachte tot een **taakstraf voor de duur van 180 (honderdtachtig) uren**, waarbij Reclassering Nederland dient te bepalen uit welke werkzaamheden de taakstraf dient te bestaan; beveelt dat, voor het geval de veroordeelde de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 90 (negentig) dagen. Dit vonnis is gewezen door: mr. M.C. Franken, voorzitter, en mrs. T.M. Riemens en L. Daum, rechters, in tegenwoordigheid van mr. H.P. Eekhout, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op 22 april 2021.  

- MATCH GEVANGENISSTRAF: gevangenisstraf voor de duur van 4 (vier) maanden
- MATCH TAAKSTRAF: taakstraf voor de duur van 180 (honderdtachtig) uren, waarbij Recla
- MATCH HECHTENIS: niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 90 (negentig) dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert d
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 121, 'hechtenis': 0, 'taakstraf': 8, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 121, 0, 8, 0, 0)

TP: 2
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBROT:2021:9086
=============================
TEXT:
7. Beslissingen op voorwaardelijke verzoeken   Beslissing op voorwaardelijke getuigenverzoeken 213. De verdediging heeft bij pleidooi verzocht om (alsnog) de volgende personen als getuige/deskundige te horen: 1. [naam getuige 1]2. [naam getuige 2] 3. [naam getuige 3]4. [naam getuige 4]5. [naam getuige 5]6. [naam getuige 6]7. Een onafhankelijke deskundige, voor een onderzoek naar (de verkrijging van) het bewijsmateriaal en de bejegening van de geheimhouders, zoals verzocht bij brief van 5 januari 2021. 8. De Canadese rechter [naam 3] van het Superior Court of Justice in Toronto, omtrent de uitleg van de door hem geformuleerde voorwaarden. 214. De rechtbank acht zich voldoende ingelicht op basis van het dossier en de uitvoerige behandeling daarvan ter zitting. Van de noodzaak tot het horen van de door de verdediging verzochte personen is daarom niet gebleken. De verzoeken worden afgewezen.  Beslissing op een voorwaardelijk verzoek tot het stellen van prejudiciële vragen 215. De verdediging heeft bij dupliek verzocht dat de rechtbank prejudiciële vragen zal stellen aan het HvJ EU indien de rechtbank haar niet volgt in een of meer van de door haar ingenomen standpunten over de uitleg van het Unierecht. De rechtbank deelt niet alle standpunten van de verdediging over dit onderwerp, bijvoorbeeld waar het gaat om het aan een vormverzuim te verbinden rechtsgevolg. Toch ziet de rechtbank geen aanleiding om prejudiciële vragen te stellen aan het HvJ EU. Dat heeft niet te maken met een gebrek aan dapperheid of durf, zoals de verdediging heeft gesuggereerd, noch met vrees voor vertraging. De rechtbank heeft in de bespreking van de verweren (met name B4, B5 en C4) aan de hand van de Europese jurisprudentie uitvoerig gemotiveerd waarom het oordeel van de rechtbank op onderdelen afwijkt van het standpunt van de verdediging. De rechtbank is dan ook van oordeel dat – voor zover de door de verdediging voorgestelde vragen al relevant zijn voor het beslissingskader in deze zaak – antwoorden op dergelijke vragen al kunnen worden gevonden aan de hand van eerdere rechtspraak van het HVJ EU. De rechtbank **wijst het verzoek dan ook af**.  Aanvullende verweren, verzoeken en nagekomen stukken 216. Tussen de laatste zittingsdag en de sluiting van het onderzoek ter terechtzitting heeft de verdediging een aantal e-mailberichten aan de rechtbank gestuurd, waarin onderwerpen ter sprake komen die in direct of iets verder verwijderd verband staan tot de rechtsvragen die in dit vonnis aan de orde komen. Tevens heeft de verdediging in die berichten een aantal aanvullende stukken in het geding gebracht; die maken daarmee onderdeel uit van het dossier. De officier van justitie is in de gelegenheid gesteld om op de in die e-mails vervatte verweren, verzoeken en stukken te reageren, waarop de verdediging nog de gelegenheid tot het nemen van een repliek heeft aangegrepen. De rechtbank heeft het niet nodig gevonden om de onderwerpen die in die e-mails aan de orde komen ook nog op een nadere terechtzitting te behandelen. Zij acht zich door de genoemde – uitvoerige – e-mailwisseling namelijk voldoende voorgelicht. In dit vonnis komen uit die e-mailwisseling slechts die stellingen van de verdediging aan de orde die direct betrekking hebben op de door de rechtbank te beantwoorden vragen in het kader van de artikelen 348 en 350 Sv. Van de overige door de verdediging aan de orde gestelde punten heeft de rechtbank kennisgenomen; zij geven haar echter geen aanleiding tot een nadere reactie.

- MATCH VRIJSPRAAK: wijst het verzoek dan ook af.  Aanvullende verweren, verzoeken en nagekomen st
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 1
FP: 0
TN: 0
FN: 0


CASE: ECLI:NL:RBROT:2021:9086
=============================
TEXT:
15. Beslissing  De rechtbank: verklaart de officier van justitie niet-ontvankelijk in de vervolging ten aanzien van het onder feit 2 subsidiair ten laste gelegde; verklaart bewezen, dat de verdachte rechtspersoon de onder 1, 2 primair en 3 primair tenlastegelegde feiten, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte rechtspersoon meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte rechtspersoon daarvan vrij; stelt vast dat het bewezenverklaarde oplevert de hiervoor vermelde strafbare feiten; verklaart de verdachte rechtspersoon strafbaar; bepaalt dat aan de verdachte rechtspersoon geen hoofdstraf wordt opgelegd; beslist ten aanzien van de voorwerpen, geplaatst op de lijst van inbeslaggenomen en nog niet teruggegeven voorwerpen, als volgt:- verklaart verbeurd als bijkomende straf: 1a. Geld Euro  Geld 4250 euro 2a. Geld Euro  Geld 3450 euro 3a. Geld Euro  48.575 euro 4a. Geld buitenlands Waarde  200 Zwitserse Frank 167.17 5. 106.00 STK GSM zaktelefoon  BLACKBERRY Z30  106 stuks Blackberry Z30/LERDA15008_324968 6. 40.00 STK GSM zaktelefoon BLACKBERRY Z10  LERDA15008_324969/40 stuks Blackberry Z10 7. 508.00 STK GSM zaktelefoon  BLACKBERRY Q10  LERDA15008_324971/508 stuks Blackberry Q10 8. 362.00 STK GSM zaktelefoon BLACKBERRY Leap LERDA15008_324972 / 362 stuks Blackberry Leap 9. 355.00 STK GSM zaktelefoon BLACKBERRY Q5 LERDA15008_324976 / 355 stuks Blackberry Q5 10. 34.00 STK GSM zaktelefoon BLACKBERRY Classic LERDA15008_324978 / 34 stuks Blackberry Classic 11. 61.00 STK GSM zaktelefoon BLACKBERRY P9900 LERDA15008_324980 / 61 stuks Blackberry P9900 12. 206.00 STK GSM zaktelefoon BLACKBERRY P9982 LERDA15008_324981 / 206 stuks Blackberry P9982 13. 252.00 STK GSM zaktelefoon BLACKBERRY P9983 LERDA15008_324982 / 252 stuks Blackberry P9983 14. 644.00 STK GSM zaktelefoon BLACKBERRY P9720 LERDA15008_324984 / 644 stuks Blackberry P9720 15. 10.00 STK GSM zaktelefoon BLACKBERRY P9100 LERDA15008 324985 / 10 stuks Blackberry P9100 16. 10.00 STK GSM zaktelefoon BLACKBERRY P9981 LERDA15008_324987 / 10 stuks Blackberry P9981 17. 42.00 STK GSM zaktelefoon BLACKBERRY P9790 LERDA15008_324988 / 42 stuks Blackberry P9790 18. 21.00 STK GSM zaktelefoon BLACKBERRY P9360 LERDA15008_324989 / 21 stuks Blackberry P9360 19. 43.00 STK GSM zaktelefoon LERDA15008_324991 / defecte GSM, div merken en mode 20. 51.00 STK GSM zaktelefoon NOKIA 6021 LERDA15008_324992 / 51 stuks Nokia 6021 21. 299.00 STK GSM zaktelefoon NOKIA 5000 LERDA15008_324993 / 299 stuks Nokia 5000 22. 5.00 STK Onderdelen BLACKBERRY LERDA15008_324996 / 5 achterkantjes van diverse Bl 23. 786.00 STK Onderdelen Kl:zwart+wit BLACKBEERY LERDA15008_324998 / 786 stuks kabels/stekkers Blac 24. 8.00 STK GSM zaktelefoon  LERDA15008_32500/8 stuks Mini Phone/voice chang 25. 6.00 STK Telefoontoestel  LERDA15008_325007/6 stuks Cryptophone 26. 6.00 STK GSM zaktelefoon SAMSUNG Galaxy S5  LERDA15008_325009/Samsung Galaxy S5 Cryptophone. 27. 1.00 STK Laptop Kl:Zilver  APPLE MacBk Pro PL2600-15008_323043/MacBk Pro KE075.02.04.003 28. 1.00 STK GSM zaktelefoon Kl: Wit BLACKBERRY 9900 PL2600-LERDA15008_323076/Blackberry 9900 wit IMEI 29. 1.00 STK Harddisk  APPLE MacBk Air  PL2600-LERDA_323083/SD kaartje met Windows Macboo 30. 1.00 STK Laptop  PL2600-LERDA15008_323089/Mabook Pro 15 inch Dit vonnis is gewezen door: mr. E. Rabbie, voorzitter, mr. J.C. Tijink en mr. T.M. Riemens, rechters, in tegenwoordigheid van mr. D. Ince, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op 21 september 2021.  

- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte rechtspersoon daarvan vrij; stelt vast dat het bewezenverklaarde oplevert de
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 1
FN: 0


CASE: ECLI:NL:RBROT:2021:9706
=============================
TEXT:
4.  Bewijsbeslissing In bijlage II heeft de rechtbank de inhoud van wettige bewijsmiddelen opgenomen, houdende voor de bewezenverklaring redengevende feiten en omstandigheden. Op grond daarvan is wettig en overtuigend bewezen dat de verdachte het ten laste gelegde heeft begaan op die wijze dat: zij in de periode van 1 maart 2019 tot en met 29 juli 2019 te Rotterdam meermalen, telkens opzettelijk een hoeveelheid medicijnen die  toebehoorde aan [naam apotheek] ,  en welk goed verdachte uit hoofde van haar persoonlijke dienstbetrekking, te weten als medewerkster ondersteunende diensten, onder zich hadtelkens wederrechtelijk zich heeft toegeëigend Hetgeen meer of anders is ten laste gelegd is niet bewezen. De verdachte moet daarvan worden vrijgesproken.

- MATCH VRIJSPRAAK: vrijgesproken.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 0
FP: 1
TN: 0
FN: 0


CASE: ECLI:NL:RBROT:2021:9706
=============================
TEXT:
11 . Beslissing  De rechtbank: verklaart bewezen, dat de verdachte het ten laste gelegde feit, zoals hiervoor omschreven, heeft begaan; verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert het hiervoor vermelde strafbare feit; verklaart de verdachte strafbaar; veroordeelt de verdachte tot een **taakstraf voor de duur van 200 (tweehonderd) uren**, waarbij de Reclassering Nederland dient te bepalen uit welke werkzaamheden de taakstraf dient te bestaan; beveelt dat de tijd die door de veroordeelde voor de tenuitvoerlegging van deze uitspraak in verzekering en in voorlopige hechtenis is doorgebracht, bij de uitvoering van de opgelegde taakstraf in mindering wordt gebracht volgens de maatstaf van twee uren per dag, zodat na deze aftrek 192 (honderdtweeënnegentig) uren te verrichten taakstraf resteert; beveelt dat, voor het geval de veroordeelde de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 96 dagen; heft op het bevel tot voorlopige hechtenis van de verdachte, die bij eerdere beslissing is geschorst; verklaart de benadeelde partijen [naam benadeelde 1] en [naam benadeelde 2]  niet-ontvankelijk in de vorderingen; veroordeelt de verdachte, om tegen behoorlijk bewijs van kwijting aan de benadeelde partij [naam benadeelde 3], te betalen een bedrag van € 48.498,45 (zegge: achtenveertigduizend vierhonderdachtennegentig euro en vijfenveertig cent), bestaande uit materiële schade, te vermeerderen met de wettelijke rente hierover vanaf 1 maart 2019 tot aan de dag der algehele voldoening; verklaart de benadeelde partij niet-ontvankelijk in het resterende deel van de vordering; bepaalt dat dit deel van de vordering slechts kan worden aangebracht bij de burgerlijke rechter; veroordeelt de verdachte in de proceskosten door de benadeelde partij gemaakt, tot op heden aan de zijde van de benadeelde partij begroot op nihil en in de kosten ten behoeve van de tenuitvoerlegging nog te maken; legt aan de verdachte de maatregel tot schadevergoeding op, inhoudende de verplichting aan de staat ten behoeve van [naam benadeelde 3] te betalen € 48.498,45 (zegge: achtenveertigduizend vierhonderdachtennegentig euro en vijfenveertig cent), vermeerderd met de wettelijke rente vanaf 1 maart 2019 tot aan de dag van de algehele voldoening; bepaalt dat indien volledig verhaal van de hoofdsom van € 48.498,45 niet mogelijk blijkt, gijzeling kan worden toegepast voor de duur van 278 dagen; de toepassing van de gijzeling heft de betalingsverplichting niet op; verstaat dat betaling aan de benadeelde partij, tevens geldt als betaling aan de staat ten behoeve van de benadeelde partij en omgekeerd. Dit vonnis is gewezen door: mr. J.L.M. Boek, voorzitter, en mrs. D. Smulders en E. IJspeerd, rechters, in tegenwoordigheid van C.A. van den Houwen, griffier, en uitgesproken op de openbare terechtzitting van deze rechtbank op 30 september 2021. De voorzitter /oudste rechter /jongste rechter /griffier is /zijn buiten staat dit vonnis mede te ondertekenen.

- MATCH TAAKSTRAF: taakstraf voor de duur van 200 (tweehonderd) uren, waarbij de Re
- MATCH HECHTENIS: niet naar behoren verricht, vervangende hechtenis zal worden toegepast voor de duur van 96 dagen
    * Negation detected at beginning or end of match. Skipped.
- MATCH VRIJSPRAAK: meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij; stelt vast dat het bewezen verklaarde oplevert h
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 9, 'geldboete': 0, 'vrijspraak': 0}
    * (0, 0, 0, 9, 0, 0)

TP: 1
FP: 0
TN: 2
FN: 0


CASE: ECLI:NL:RBZWB:2021:3656
=============================
TEXT:
9 De beslissing  De rechtbank:  Bewezenverklaring - verklaart het ten laste gelegde bewezen, zodanig als hierboven onder 4.4 is omschreven; - spreekt verdachte vrij van wat meer of anders is ten laste gelegd;  Strafbaarheid - verklaart dat het bewezen verklaarde de volgende strafbare feiten oplevert:  feit 1:  Medeplegen van opzettelijk handelen in strijd met het in artikel 3, onder B, van de Opiumwet gegeven verbod;  feit 2:  Medeplegen van opzettelijk handelen in strijd met een in artikel 3, onder C, van de Opiumwet gegeven verbod; - verklaart verdachte strafbaar;  Strafoplegging - veroordeelt verdachte tot een **taakstraf van tweehonderd uren**; - beveelt dat indien verdachte de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast van honderd dagen; - bepaalt dat de tijd die verdachte voor de tenuitvoerlegging van deze uitspraak in voorarrest heeft doorgebracht in mindering wordt gebracht bij de tenuitvoerlegging van de taakstraf naar rato van 2 uur per dag; - veroordeelt verdachte tot een **gevangenisstraf van vier maanden voorwaardelijk met een proeftijd van twee jaar**; - bepaalt dat deze straf niet ten uitvoer wordt gelegd, tenzij de rechter tenuitvoerlegging gelast, omdat verdachte voor het einde van de proeftijd de hierna vermelde voorwaarden niet heeft nageleefd; - stelt als algemene voorwaarde dat verdachte zich voor het einde van de proeftijd niet schuldig maakt aan een strafbaar feit;  Beslag - verklaart onttrokken aan het verkeer de inbeslaggenomen voorwerpen op de beslaglijst vermeld onder de nummers: 13 en 15 t/m 26; - gelast de bewaring ten behoeve van de rechthebbende van de inbeslaggenomen voorwerpen op de beslaglijst vermeld onder de nummers: 10, 12 en 27. Dit vonnis is gewezen door mr. W.J.M. Fleskens, voorzitter, mr. M.E.M.W. Nuijts en mr. M.H.M. Collombon, rechters, in tegenwoordigheid van mr. M. de Jonge, griffier, en is uitgesproken ter openbare zitting op 21 juli 2021. Mr. Nuijts is niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH TAAKSTRAF: mindering wordt gebracht bij de tenuitvoerlegging van de taakstraf naar rato van 2 uur per dag
    * 'in mindering' detected. Skipped.
- MATCH VRIJSPRAAK: spreekt verdachte vrij van wat meer of anders is ten laste gelegd
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 2
FN: 2


CASE: ECLI:NL:RBZWB:2021:3658
=============================
TEXT:
8 De beslissing  De rechtbank:  Bewezenverklaring - verklaart het ten laste gelegde bewezen, zodanig als hierboven onder 4.4 is omschreven; - spreekt verdachte vrij van wat meer of anders is ten laste gelegd;  Strafbaarheid - verklaart dat het bewezen verklaarde de volgende strafbare feiten oplevert: feit 1:  Medeplegen van opzettelijk handelen in strijd met het in artikel 3, onder B, van de Opiumwet gegeven verbod; feit 2:  Medeplegen van opzettelijk handelen in strijd met een in artikel 3, onder C, van de Opiumwet gegeven verbod; - verklaart verdachte strafbaar;  Strafoplegging - veroordeelt verdachte tot **een taakstraf van honderdtwintig uren**; - beveelt dat indien verdachte de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast van zestig dagen; - veroordeelt verdachte tot **een gevangenisstraf van twee maanden voorwaardelijk met een proeftijd van twee jaar**; - bepaalt dat deze straf niet ten uitvoer wordt gelegd, tenzij de rechter tenuitvoerlegging gelast, omdat verdachte voor het einde van de proeftijd de hierna vermelde voorwaarden niet heeft nageleefd; - stelt als algemene voorwaarde dat verdachte zich voor het einde van de proeftijd niet schuldig maakt aan een strafbaar feit. Dit vonnis is gewezen door mr. W.J.M. Fleskens, voorzitter, mr. M.E.M.W. Nuijts en mr. M.H.M. Collombon, rechters, in tegenwoordigheid van mr. M. de Jonge, griffier, en is uitgesproken ter openbare zitting op 21 juli 2021. Mr. Nuijts is niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH VRIJSPRAAK: spreekt verdachte vrij van wat meer of anders is ten laste gelegd
    * 'ne bis in idem' detected. Skipped.
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 0}

NO MATCHES FOUND
(0, 0, 0, 0, 0, 0)

TP: 0
FP: 0
TN: 1
FN: 2


CASE: ECLI:NL:RBZWB:2021:6216
=============================
TEXT:
6 De beslissing  De rechtbank:  Vrijspraak - **spreekt verdachte vrij van het ten laste gelegde feit**;  Benadeelde partijen - verklaart de benadeelde partij [aangeefster] niet-ontvankelijk in de vordering en bepaalt dat de vordering bij de burgerlijke rechter kan worden aangebracht; - bepaalt dat iedere partij zijn eigen kosten draagt. Dit vonnis is gewezen door mr. C.H.W.M. Sterk, voorzitter, mr. L.W. Louwerse en mr. R. de Jong, rechters, in tegenwoordigheid van mr. G.P.A.J. Joosen, griffier, en is uitgesproken ter openbare zitting op 7 december 2021. Mr. L.W. Louwerse is niet in de gelegenheid dit vonnis mede te ondertekenen.

- MATCH VRIJSPRAAK: Vrijspraak - spreekt verdachte vrij van het ten laste gelegd
- OUT: {'TBS': 0, 'gevangenisstraf': 0, 'hechtenis': 0, 'taakstraf': 0, 'geldboete': 0, 'vrijspraak': 1}
    * (0, 0, 0, 0, 0, 1)

TP: 1
FP: 0
TN: 0
FN: 0
