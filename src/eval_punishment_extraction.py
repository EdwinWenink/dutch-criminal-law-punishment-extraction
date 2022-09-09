import sys
import random
import pandas as pd
from src.extract_punishments import label_hoofdstraf, PunishmentPattern

# Keywords:
# "veroordeelt de verdachte tot een gevangenisstraf voor de duur van [X]"
# "De uitspraak van het hof"
# "een jeugddetentie voor de duur van [411] dagen"
# "een taakstraf voor de duur van [240] uren"
# "een gevangenisstraf voor de duur van 540 dagen" -> Kan ook betekenen dat deze NIET wordt toegekend.
# "Plaatsing in een inrichting van jeugdigen."
# e.g. ECLI:NL:RBGEL:2020:6999
# "Verplichting tot betaling"
# "Bijkomende straf"
# "De straf"
# "Moet er geen straf of maatregel worden opgelegd?"
# "Maatregel"
# "De straf en/of de maatregel"
# "Vermogensmaatregel"
# "De op te leggen straf of maatregel"
# "Ten aanzien van de schadevergoedingsmaatregel"
# "Vaststelling van het te betalen bedrag"

# Merk op dat twee matches van gevangenis straf gaan over een hoeveelheid die *niet* van de bepaalde gevangenisstraf uitgevoerd zal worden. Hoe ondervang ik dit?


tests = [
    # Gevangenisstraf, hechtenis, detentie
    ('een gevangenisstraf van 5 (vijf) jaren', (0, 1825, 0, 0, 0, 0)),
    ('veroordeelt de verdachte tot hechtenis voor de duur van 3 (drie) maanden;', (0, 0, 91, 0, 0, 0) ),
    ('Veroordeelt verdachte tot honderdtachtig (180) dagen jeugddetentie.', (0, 0, 180, 0, 0, 0)),
    ('veroordeelt de verdachte tot een gevangenisstraf voor de duur van 2 (twee) jaar en 6 maanden;', (0, 912, 0, 0, 0, 0)),
    ('verdachte moet 5 (vijf) jaar naar de gevangenis!', (0, 1825, 0, 0, 0, 0)),  # not matched by design right now; haven't seen this formulation anywhere
    ('gevangenisstraf van 5 jaar, en verbindt hieraan een proeftijd, die wordt gesteld op 2 jaar;', (0, 1825, 0, 0, 0, 0)),
    ('voorwaardelijke gevangenisstraf van 5 jaar, en verbindt hieraan een proeftijd, die wordt gesteld op 2 jaar;', (0, 1825, 0, 0, 0, 0)),
    ('detentie voor de duur van 49 (negenenveertig) dagen', (0, 0, 49, 0, 0, 0)),
    ('jeugddetentie voor de duur van negenenveertig (49) dagen', (0, 0, 49, 0, 0, 0)),
    ('gevangenisstraf een gedeelte van 120 (honderdtwintig) dagen niet ten uitvoer', (0, 0, 0, 0, 0, 0)),

    # Voorwaardelijke detentie als hoofdstraf
    ('gevangenisstraf van 2 weken voorwaardelijk met een proeftijd van 2 jaar', (0, 14, 0, 0, 0, 0)),  # shouldn't match 2 jaar as the main punishment
    ('veroordeelt verdachte wegens de bewezenverklaarde feiten 1, 3 en 4 tot een gevangenisstraf voor de duur van 6 (zes) maanden; bepaalt dat deze gevangenisstraf niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten omdat verdachte zich voor het einde van de proeftijd van drie (3) jaren schuldig heeft gemaakt aan een strafbaar feit;', (0, 182, 0, 0, 0, 0)),

    # Detentie met voorwaardelijk deel
    ('bepaalt dat van deze gevangenisstraf een gedeelte groot 3 (drie) maanden niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten;', (0, 0, 0, 0, 0, 0)),
    ('de gevangenisstraf van 3 maanden is voorwaardelijk', (0, 91, 0, 0, 0, 0)),  # TODO match or not?
    ('Strafoplegging - veroordeelt verdachte tot een gevangenisstraf van 12 (twaalf) maanden, waarvan  6 (zes) maanden voorwaardelijk met een proeftijd van twee jaar; - bepaalt dat het voorwaardelijke deel van de straf niet ten uitvoer wordt gelegd, tenzij de rechter tenuitvoerlegging gelast, omdat verdachte voor het einde van de proeftijd de hierna vermelde voorwaarden niet heeft nageleefd;', (0, 365, 0, 0, 0, 0)),
    ('van deze gevangenisstraf zal een gedeelte, groot 3 (drie) maanden, van deze gevangenisstraf niet tenuitvoergelegd zal worden, tenzij later anders wordt gelast. Stelt daarbij een proeftijd van 2 (twee) jaren vast.', (0, 0, 0, 0, 0, 0)),
    ('bepaalt dat van deze gevangenisstraf een gedeelte, groot 10 (tien) weken, niet ten uitvoer zal worden gelegd, tenzij de rechter later anders', (0, 0, 0, 0, 0, 0)),
    ('bepaalt dat van deze gevangenisstraf een gedeelte, groot 10 (tien) weken, niet ten uitvoer zal worden gelegd, tenzij de rechter later anders mocht gelasten wegens niet nakoming van de voorwaarden', (0, 0, 0, 0, 0, 0)),  # negation at the end

    # Boetes
    ('Wijst de vordering van de benadeelde partij [naam slachtoffer] toe tot een bedrag van € 5.000,- (vijfduizend euro) aan vergoeding van immateriële schade', (0, 0, 0, 0, 5000, 0)),
    ('Wijst de vordering van de benadeelde partij [naam slachtoffer] toe tot een bedrag van 2.000,- euro (vijfduizend euro) aan vergoeding van immateriële schade', (0, 0, 0, 0, 2000, 0)),
    ('een geldboete van €60, oftewel 60 Euro',(0, 0, 0, 0, 60, 0)),
    ('een geldboete van 5 euro.', (0, 0, 0, 0, 5, 0)),
    ('betaling van een geldboete van € 500,=', (0, 0, 0, 0, 500, 0)),
    ('vordering van € 2.000,22 wat is hier de eenheid?', (0,0,0,0,2000,0)),
    ('betaling aan de benadeelde partij [Slachtoffer 1] (feit 1, 2,', (0, 0, 0, 0, 0, 0)),  # This one is hard to counter, because most of the time we do have (9) as number1
    ('betaling aan de benadeelde partij [Slachtoffer 3] (feit 9) van € 5.226,53,', (0, 0, 0, 0, 5226, 0)),
    ('bepaalt dat bij niet betaling 5 (vijf) dagen gijzeling kan worden toegepast, met dien verstande dat toepassing van de gijzeling de betalingsverplichting niet opheft', (0, 0, 0, 0, 0, 0)),

    # Samengestelde geldbedragen; doorgaans wordt nog expliciet en dubbelop de verplichting benoemd
    ('Wijst de vordering van de benadeelde partij [slachtoffer 1] toe tot een bedrag van  € 1.314,28 (duizend driehonderdveertien euro en achtentwintig cent), bestaande uit € 314,28 (driehonderdveertien euro en achtentwintig cent) aan vergoeding van materiële schade en € 1.000,00 (duizend euro) aan vergoeding van immateriële schade, te vermeerderen met de wettelijke rente daarover vanaf het moment van het ontstaan van de schade op 27 juni 2020 tot aan de dag van de algehele voldoening.', (0, 0, 0, 0, 1314, 0)),
    ('vordering van de benadeelde partij [persoon] toe tot een bedrag van € 87,-- (zevenentachtig euro) aan vergoeding van materiële schade en € 1.000 aan immateriele. Veroordeelt verdachte voorts in de kosten door de benadeelde partij gemaakt en ten behoeve van de tenuitvoerlegging van deze uitspraak nog te maken, tot op de dag van de uitspraak begroot op € 922,-- (negenhonderd en tweeëntwintig euro). Legt verdachte de verplichting op ten behoeve van [persoon] aan de Staat € 1.087,-- (duizend zevenentachtig euro) te betalen, te vermeerderen met de wettelijke rente daarover vanaf het moment van het ontstaan van de schade (17 augustus 2020) tot aan de dag van de algehele voldoening, behalve voor zover deze vordering al door of namens een ander is betaald.', (0, 0, 0, 0, 1087, 0)),  # 922 euro is maatregel; moeilijke hier is om totaal te vinden
    ('Wijst de vordering van de benadeelde partij [persoon 5] toe tot een bedrag van € 1.306,04 (duizend, driehonderd en zes euro en vier eurocent) aan vergoeding van materiële schade. Veroordeelt verdachte tot betaling van het toegewezen bedrag aan [persoon 5] voornoemd, te vermeerderen met de wettelijke rente daarover vanaf het moment van het ontstaan van de schade (15 augustus 2020) tot aan de dag van de algehele voldoening. Veroordeelt verdachte voorts in de kosten door de benadeelde partij gemaakt en ten behoeve van de tenuitvoerlegging van deze uitspraak nog te maken, tot op heden begroot op nihil. Legt verdachte de verplichting op ten behoeve van [persoon 5] aan de Staat € 1.306,04 (duizend, driehonderd en zes euro en vier eurocent), te vermeerderen met de wettelijke rente daarover vanaf het moment van het ontstaan van de schade (15 augustus 2020) tot aan de dag van de algehele voldoening, te betalen.', (0, 0, 0, 0, 1306, 0)),
    ('Wijst de vordering van de benadeelde partij [slachtoffer] gedeeltelijk toe tot een bedrag van € 7.580,37 (zevenduizend vijfhonderdtachtig euro en zevenendertig eurocent), bestaande uit € 2.580,37 (tweeduizend vijfhonderdtachtig euro en zevenendertig eurocent) aan vergoeding van materiële schade en € 5.000,- (vijfduizend euro) aan vergoeding van immateriële schade' , (0, 0, 0, 0, 7580, 0)),
    ('Wijst de vordering van de benadeelde partij [naam slachtoffer] toe tot een bedrag van € 5.000,- (vijfduizend euro) aan vergoeding van immateriële schade. Legt verdachte de verplichting op ten behoeve van [naam slachtoffer] aan de Staat € 5.000,- (vijfduizend euro) te betalen.', (0, 0, 0, 0, 5000, 0)),

    # Taakstraffen
    ('veroordeelt verdachte tot een taakstraf van honderdtwintig uren;', (0, 0, 0, 5, 0, 0)),
    ('Persoon wordt veroordeeld tot taakstraf van 40 (veertig) uur', (0, 0, 0, 2, 0, 0)),
    ('taakstraf van 60 uur plus 8 uur', (0, 0, 0, 3, 0, 0)),
    ('taakstraf niet ten uitvoer zal worden gelegd, tenzij verdachte zich voor het einde van de op 2 (twee) jaren gestelde proef', (0, 0, 0, 0, 0, 0)),

    # Taakstraf met vervangende, subsidiaire hechtenis
    ('taakstraf bestaande uit het verrichten van onbetaalde arbeid voor de duur van 60 (zestig) uren, subsidiair 30 dagen hechtenis', (0, 0, 0, 3, 0, 0)),
    ('wanneer taakstraf niet naar behoren heeft verricht, wordt vervangende hechtenis toegepast van 50 (vijftig) dagen', (0, 0, 0, 0, 0, 0)),  # avoid matching taakstraf of 50 days (10 days is max btw)
    ('wanneer verdachte taakstraf niet naar behoren heeft verricht, wordt vervangende hechtenis toegepast van 50 (vijftig) dagen', (0, 0, 0, 0, 0, 0)),  # niet geinterresseerd in vervangende straffen
    ('Veroordeelt de verdachte tot een taakstraf van 40 (veertig) uren, met bevel, voor het geval dat de verdachte de taakstraf niet naar behoren heeft verricht, dat vervangende hechtenis zal worden toegepast van 20 (twintig) dagen.' , (0, 0, 0, 2, 0, 0)),
    ('bepaalt de duur van de gijzeling die met toepassing van artikel 6:6:25 van het Wetboek van Strafvordering ten hoogste kan worden gevorderd op 3 jaren.', (0, 0, 0, 0, 0, 0)),
    ('beveelt dat indien verdachte de taakstraf niet naar behoren verricht, vervangende hechtenis zal worden toegepast van 30 dagen', (0, 0, 0, 0, 0, 0)),  # shouldn't be taakstraf of 30 days
    ('veroordeelt verdachte wegens de bewezenverklaarde feiten 1, 3 en 4 tot een taakstraf van 240 uren, met bevel dat indien deze straf niet naar behoren wordt verricht vervangende hechtenis zal worden toegepast voor de duur van 120 dagen;', (0, 0, 0, 10, 0, 0)),

    ('bepaalt dat de tijd die verdachte voor de tenuitvoerlegging van deze uitspraak in voorarrest heeft doorgebracht in mindering wordt gebracht bij de tenuitvoerlegging van de taakstraf naar rato van 2 uur per dag;', (0, 0, 0, 0, 0, 0)),
    ('Gelast de tenuitvoerlegging van de werkstraf, voor zover voorwaardelijk opgelegd bij vonnis van de kinderrechter van Rechtbank Noord-Nederland, locatie Leeuwarden van 6 oktober 2020, te weten: 50 uren werkstraf subsidiair 25 dagen vervangende jeugddetentie', (0, 0, 0, 3, 0, 0)),

    # Boete met vervangende hechtenis
    ('hechtenis heeft doorgebracht naar rato van 50 euro per dag', (0, 0, 0, 0, 0, 0)),

    # Vrijspraak
    ('spreekt de verdachte daarvan vrij', (0, 0, 0, 0, 0, 1)),
    ('wijst de vordering van de benadeelde partij voor het overige af', (0, 0, 0, 0, 0, 1)),

    # Ne bis in idem (should not match vrijspraak)
    ('- verklaart het ten laste gelegde bewezen, zodanig als hierboven onder 4.4 is omschreven; - spreekt verdachte vrij van wat meer of anders is ten laste gelegd;', (0, 0, 0, 0, 0, 0)),
    ('verklaart niet bewezen hetgeen aan de verdachte meer of anders ten laste is gelegd dan hiervoor bewezen is verklaard en spreekt de verdachte daarvan vrij;', (0, 0, 0, 0, 0, 0)),
    ('verklaart niet bewezen wat aan verdachte meer of anders is ten laste gelegd en **spreekt hem daarvan vrij**;', (0, 0, 0, 0, 0, 0)),
    ('verklaart niet bewezen wat aan verdachte primair meer of anders is ten laste gelegd en **spreekt hem daarvan vrij;**', (0, 0, 0, 0, 0, 0)),
    ('verklaart niet bewezen hetgeen verdachte meer of anders is ten laste gelegd dan hierboven bewezen is verklaard en **spreekt verdachte daarvan vrij**;', (0, 0, 0, 0, 0, 0)),
    ('Hetgeen meer of anders is ten laste gelegd is niet bewezen. De verdachte moet daarvan worden vrijgesproken', (0, 0, 0, 0, 0, 0)),

    # TBS
    ('is het hof tevens van oordeel dat de algemene veiligheid van personen het opleggen van een TBS-maatregel met bevel tot verpleging van overheidswege eist.', (1, 0, 0, 0, 0, 0)),
    ('De beslissing De rechtbank: verlengt de terbeschikkingstelling van [betrokkene] met twee jaren;', (1, 0, 0, 0, 0, 0)),
    ('gelast dat de verdachte, voor de feiten 2, 3 en 4, ter beschikking wordt gesteld en stelt daarbij de volgende, het gedrag van de ter beschikking gestelde betreffende, voorwaarden'' (ECLI:NL:RBLIM:2020:9778)', (1, 0, 0, 0, 0, 0)),
    ('verlengt de termijn gedurende welke [verdachte] ter beschikking is gesteld met verpleging van overheidswege met één jaar" (ECLI:NL:RBLIM:2020:10468)', (1, 0, 0, 0, 0, 0)),
    ('ter beschikking wordt gesteld en beveelt dat hij van overheidswege zal worden verpleegd; (ECLI:NL:RBGEL:2021:1002)', (1, 0, 0, 0, 0, 0)),
    # only match TBS with verlanging or indication of type
    ('ter beschikking stelling van de goederen aan benadeelde partij', (0, 0, 0, 0, 0, 0)),
    ('TBS kliniek De Kijvelanden, wederrechtelijk van de vrijheid heeft beroofd en/of beroofd gehouden, immer', (0, 0, 0, 0, 0, 0)),

    # Maatregelen (momenteel niet gematcht)
    ('ontzegt de verdachte de bevoegdheid motorrijtuigen te besturen voor de tijd van 6 (zes) maanden;', (0, 0, 0, 0, 0, 0)),
    ('Verklaart onttrokken aan het verkeer: een mes.', (0, 0, 0, 0, 0, 0)),
    ('legt [verdachte] de verplichting op tot betaling aan de staat ter ontneming van het wederrechtelijk verkregen voordeel van € 331.083,14 (zegge: driehonderdeenendertigduizend drieëntachtig euro en veertien eurocent)', (0, 0, 0, 0, 0, 0)),  # dit is een maatregel, die claim ik momenteel niet te matchen
    (' veroordeelt verdachte in verband met het feit onder nummer 1 en 2 tot betaling van schadevergoeding aan de benadeelde partij [getuige 1] van  37,48 aan materiële schade en  1.500,- aan smartengeld, vermeerderd met de wettelijke rente vanaf 22 november 2019 tot aan de dag dat het hele bedrag is betaald', (0, 0, 0, 0, 0, 0)),
    ('de verplichting op tot betaling van 43.172,75 euro aan de Staat ter ontneming van het wederrechtelijk verkregen voordeel', (0, 0, 0, 0, 0, 0)),
    ('legt de maatregel op dat verdachte verplicht is ter zake van het bewezen verklaarde feit tot betaling aan de Staat der Nederlanden van een bedrag van € 436,27, te vermeerder', (0, 0, 0, 0, 0, 0)),
    ('... dat verdachte verplicht is ter zake van het bewezen verklaarde feit tot betaling aan de Staat der Nederlanden van een bedrag van € 436,27, te vermeerder', (0, 0, 0, 0, 0, 0)),

    # Edge cases (identifiers, data, etc.)
    ('Vordering [aangever 2] (feit 2 parketnummer 15/144152-20) Verklaart de benadeelde partij [aangever 2] niet', (0, 0, 0, 0, 0, 0)),
    ('vordering 2-20-2020', (0, 0, 0, 0, 0, 0)),  # parse geen data als bedragen
    ('Vordering tenuitvoerlegging - gelast dat de voorwaardelijke straf, die bij vonnis van de rechtbank Gelderland, locatie Arnhem van 10 juli 2018 is opgelegd in de zaak onder parketnummer X', (0, 0, 0, 0, 0, 0)),
    # Actually, this is a really ambiguous test case; it also doesn't match because the digit 2 is absent...
    ('gelast de tenuitvoerlegging van de bij vonnis d.d. 26 juli 2019 voorwaardelijk aan de verdachte opgelegde straf, te weten een gevangenisstraf voor de duur van twee weken.', (0, 0, 0, 0, 0, 0)),
    ('dat bij niet betaling het daarbij vermelde aantal dagen gijzeling kan worden toegepast: benadeelde partij [naam 3] (feit 3, parketnummer 02/289273-19), â‚¬ 100,00, te vermeerderen met de wettelijke rente, berekend vanaf 18 april 2019 tot aan de dag der algehele voldoening;', (0, 0, 0, 0, 0, 0)),
    ('vordering in het jaar 2020 van 2000 euro', (0, 0, 0, 0, 2000, 0)),  # this case is made up, probably fine to not match
    ('vordering van de benadeelde partij [benadeelde partij 16] tot een bedrag van 150 euro', (0, 0, 0, 0, 150, 0)),  # do not match 6 as eenheid1

    ('vordering van de officier van justitie tot tenuitvoerlegging in de zaak met parketnummer 23/003276-17 en gelast de tenuitvoerlegging van de niet ten uitvoer gelegde gevangenisstraf voor de duur', (0, 0, 0, 0, 0, 0)),
    ('vordering van de officier van justitie tot tenuitvoerlegging in de zaak met parketnummer 23/003276-17', (0, 0, 0, 0, 0, 0)),
    # Dit match niet omdat de "tussen tekst" na vordering langer is dan 85. Wat is het effect van 85 verhogen op de test cases?
    ('Veroordeelt verdachte tot betaling van het toegewezen bedrag aan [persoon 3] voornoemd, te vermeerderen met de wettelijke rente daarover vanaf het moment van het ontstaan van de schade (4 juli 2020) tot aan de dag van de algehele voldoening.', (0, 0, 0, 0, 0, 0)),
    # Kortere (fictieve) variant
    ('veroordeelt verdachte tot betaling van het toegewezen bedrag voor de schade ontstaan op 4 juli 2020', (0, 0, 0, 0, 0, 0)),
    ('gevangenisstraf voor de duur van vierentwintig [24] maanden', (0, 365, 0, 0, 0, 0)),
    # TODO nu match ik "vordert" niet; dus deze match faalt wel zoals verwacht, maar niet vanwege de juiste reden (schadevergoeding)
    ('De benadeelde partij [benadeelde 5] vordert een schadevergoeding van € 130,00 terzake van feit 3 (parketnummer 03.155784.19).', (0, 0, 0, 0, 0, 0)),
    ('wijst de vordering van de benadeelde partij [benadeelde 6] (parketnummer 03.155784.19 feit 1) gedeeltelijk toe en veroordeelt de verdachte om tegen behoorlijk bewijs van kwijting aan de benadeelde partij te betalen € 70,75, te vermeerderen met de wettelijke rente te berekenen over de periode van 21 april 2019 tot aan de dag van de volledige voldoening;', (0, 0, 0, 0, 70, 0)),
    ('veroordeelt tot werkstraf, bij het niet of niet naar behoren verrichten daarvan te vervangen door dertig (30) dagen jeugddetentie', (0, 0, 0, 0, 0, 0)),
    # Deze hechtenis *is* al doorgebracht
    ('hechtenis heeft doorgebracht, te weten vierenveertig (44) dagen, bij de tenuitvoerlegging van het onvoorwaardelijk', (0, 0, 0, 0, 0, 0)),
    ('vordert betaling voor feit 10 begaan op 10 januari 2020', (0, 0, 0, 0, 0, 0)),
    ('vordert betaling voor feit 10 begaan ...', (0, 0, 0, 0, 0, 0)),  # edge case
    ('vordering voor feit 10', (0, 0, 0, 0, 0, 0)),
    ('geldboete voor feit 10', (0, 0, 0, 0, 0, 0)),

    # Nog indelen
    ]

def test_cases(pp: PunishmentPattern):
    print(f"Used pattern for hoofdstraf:\n{pp.pattern}\n")
    # Testing
    print("==========")
    print("TEST CASES")
    print("==========\n")
    passing = 0
    for i, test in enumerate(tests):
        print(f"TEST CASE {i}: {test[0]}")
        out = label_hoofdstraf(pp, test[0])
        print(out)
        passes = out == test[1]
        print("PASSING:", passes)
        passing += passes
        print()

    print(f"{passing} out of {len(tests)} tests passed.")


def check_outliers():
    # Outliers to check
    # Taakstraf

    # 738: ECLI:NL:RBAMS:2021:7066 -> Fixed
    # 25: ECLI:NL:RBNNE:2021:3376 -> Order: 'te weten: 50 uren werkstraf subsidiair 25 dagen vervangende jeugddetentie.'
    # 13: ECLI:NL:RBZWB:2021:6511 -> Max taakstraf is succeeding because a previous conditional punishment is added
    # 12: ECLI:NL:RBGEL:2021:4230 -> Fixed
    # 11: ECLI:NL:RBAMS:2021:7624 -> Fixed
    # 11: ECLI:NL:RBGEL:2021:1200 -> Fixed
    #
    # Geldboete
    # 8215446: ECLI:NL:RBOVE:2021:1983
    # 1700000: ECLI:NL:RBZWB:2021:2862
    # 500239: ECLI:NL:RBZWB:2021:2861

    '''
    outliers = ['ECLI:NL:RBAMS:2021:7066', 'ECLI:NL:RBNNE:2021:3376', 'ECLI:NL:RBZWB:2021:6511',
                'ECLI:NL:RBGEL:2021:4230', 'ECLI:NL:RBAMS:2021:7624', 'ECLI:NL:RBGEL:2021:1200',
                'ECLI:NL:RBOVE:2021:1983', 'ECLI:NL:RBZWB:2021:2862', 'ECLI:NL:RBZWB:2021:2861']

    for ECLI in outliers:
        print("ECLI:", ECLI)
        outlier = df.loc[ECLI]
        beslissing = outlier.loc[outlier['type'] == 'beslissing']['data'][0]
        straf_vector = label_hoofdstraf(beslissing)
        print()
    '''


def manual_eval_random_cases(df: pd.DataFrame, pp: PunishmentPattern,
                             seed=2021,
                             fn_out='docs/evaluate_strafmaat.md',
                             old_val_ECLIs=None,
                             n_samples=25):
    '''
    Select random decisions, extract punishments, and write them out to a file for manual validation.

    seed:               seed to use for manual validation
    pp:                 PunishmentPattern instance
    fn_out:             filepath where results are written to
    old_val_ECLIs:      if you have previous evaluation results you want to still include,
                        you can submit a manual list of their case ECLIs
    '''

    beslissingen = df.loc[df['type'] == 'beslissing']
    ECLIs = None

    # Retrieve these previous validation cases
    if old_val_ECLIs:
        # NOTE that len(ECLIs) is not always equal to len(cases), because a case may have multiple 'beslissing' sections
        # old_val_cases = beslissingen.loc[old_val_ECLIs]['data']
        old_val_cases = beslissingen.loc[old_val_ECLIs, 'data']
        old_val_ECLIs = list(old_val_cases.index)

    if n_samples > 0:
        print(f"Randomly sampling {n_samples} cases.")
        random.seed(seed)
        idx = random.sample(range(len(beslissingen)), k=n_samples)
        cases = beslissingen.iloc[idx]['data']
        # vectors = beslissingen.iloc[idx]['straffen']
        ECLIs = list(beslissingen.index[idx])

        if old_val_ECLIs:
            # Assert there's no overlap before merging
            intersection = set(old_val_ECLIs) & set(ECLIs)
            print(len(intersection), intersection)
            assert len(intersection) == 0

        print("Randomly selected cases for validation:", ECLIs, len(ECLIs))

    # Merge if applicable
    if old_val_ECLIs and ECLIs:
        print("Merging randomly selected cases with manually provided cases.")
        # TODO does this destroy the index?
        cases = pd.concat([old_val_cases, cases], axis=0)
        ECLIs = old_val_ECLIs + ECLIs
    elif old_val_ECLIs:
        print("Using manually provided cases only.")
        ECLIs = old_val_ECLIs
        cases = old_val_cases

    if not ECLIs:
        print("ERROR: you have not selected any cases for manual evaluation.")
        print("Terminating.")
        return

    print("All selected cases for validation:", set(ECLIs), len(set(ECLIs)))
    assert len(ECLIs) == len(cases)  # N.B. may contain multiple sections from the same case!

    sys.stdout = open(fn_out, 'w', encoding='utf-8')
    for i, case in enumerate(cases):
        print("CASE:", ECLIs[i])
        print("=============================")
        print("TEXT:")
        print(case)
        print("\nLABEL VECTOR:")
        print(label_hoofdstraf(pp, case))
        print("\n\nTODO evaluate\n\n")
        print("TP:\nFP:\nTN:\nFN:\n\n")

    sys.stdout.close()
