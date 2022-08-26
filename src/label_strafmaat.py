import sys
from argmine.dataloader import DataLoader
from argmine.utils import utils
from argparse import ArgumentParser
import numpy as np
import re
import difflib
import math
import pandas as pd
import random

'''
This is a script to extract punishments from the judgements of Dutch criminal law cases.

This script assumes we have a dataset (as produced by caseparser.py) that can be read in via csv
and has a `type` column with `beslissing` entries indicating which texts contain the final verdict.

Dutch crimininal law knows four main types of punishment ('hoofdstraffen'):

    - prison sentence / gevangenisstraf (levenslang, tijdelijk)
    - custody / hechtenis (but 'voorlopige hechtenis' is not a punishment! opgelegd voor overtredingen; maximum duur van een jaar; in uitzonderlijke gevallen 1 jaar en 4 maanden = 487 dagen)
        * Deze straf wordt praktisch niet opgelegd.
    - community service / taakstraf (werkstraf of leerstraf); wordt niet opgelegd als er al minstens een half jaar gevangenisstraf is opgelegd; max 240 uur.
    - fine / geldboete volgens categorieën systeem, gaat altijd gepaard met vervangende hechtenis als aan het bedrag niet wordt voldaan, met max een dag per 25 euro en een totale max. van een jaar:
        * 1. 390 euro
        * 2. 3.900 euro
        * 3. 7.800 euro
        * 4. 19.500 euro
        * 5. 78.000 euro
        * 6. 780.000 euro

        UPDATE 2020:

        * 1. 450 euro
        * 2. 4.500 euro
        * 3. 9.000 euro
        * 4. 22.500 euro
        * 5. 90.000 euro
        * 6. 900.000 euro

And additional punishments:

    - ontzetting van rechten (e.g. wegnemen kiesrecht, ontnemen recht op te treden als advocaat, niet mogen dien in leger)
    - verbeurdverklaring (dader verliest eigendom van voorwerpen die een rol bij het strafbare feit speelden of erdoor zijn verkregen)
    - openbaarmaking uitspraak (uitspraak wordt niet zoals normaal anoniem gepubliceerd, maar met naam; aan de schandpaal genageld)

And maatregelen:

    - plaatsing psychiatrisch ziekenhuis
    - TBS (Ter Beschikking Stelling)
    - Ontrekking aan het verkeer (van gevaarlijke objecten; lijkt op verbeurdverklaring maar kan ook worden toegepast na vrijspraak)
    - Ontneming wederrechtelijk voordeel ('Plukze' wetgeving: wegnemen van verdiensten verkregen door criminele activiteiten)
    - Schadevergoeding aan slachtoffer (dit wordt niet gezien als straf, maar als compensatie voor het slachtoffer)
    - ISD (Inrichting Stelselmatige Daders): plaatsing in een inrichting voor stelselmatige daders (cf. psych. ziekenhuis en TBS zijn voor geestesgestoorden)
    - ...

This script extracts the four main punishments and the TBS maatregel (which is very severe and is informally counted as a main punishment though formally not being one)

'''

# I do not want to match cases like "gevangenisstraf een gedeelte, groot 3 (drie) maanden niet ten uitvoer"
# Negative matching is very hard, so instead I match these modifiers and then do post-filtering on the ones I want to exclude
# Current limitation: we assume the punishment comes before the duration. E.g. 'veroordeelt de verdachte tot 3 maanden gevangenis' is not matched.
# Compound punishment is supported "gevangenisstraf voor de duur van 2 (twee) jaar en 6 (zes) maanden"
# Things like "maandelijkse termijnen" are excluded
# [^0-9\n\r.;] avoids matching newlines and dots (which \D *does*), which can cause issues, e.g.:
# 0-9 prevents that the wildcard consumes the first digit of fines, e.g. in "60 euro" the first 6 will be consumed by the wildcard, only the 0 captures by the "bedrag" pattern
# However, 0-9 will prevent matches when a digit occurs in between, e.g. "geldboete toegewezen aan [slachtoffer 1] volgens artikel 1 van 60 Euro".
connector = r'[^\n\r;.]{0,100}'  # TODO refactor to use this
connector_long = r'[^\n\r;.]{0,150}'  # TODO refactor to use this
# Avoid matching parketnummer as large fine in "vordering van de officier van justitie tot tenuitvoerlegging in de zaak met parketnummer 23/003276-17 en gelast de tenuitvoerlegging van de niet ten uitvoer gelegde gevangenisstraf voor de duur" E.g. see ECLI:NL:RBGEL:2020:6993
modifier1 = r'(?P<modifier1>voorwaardelijk|proeftijd|niet|vervangend|indien|mindering|maatregel)'
# The second part is often a subsidiary custody; we match 'hechtenis' to catch and avoid the following edge case:
# MATCH TAAKSTRAF: taakstraf van 80 (tachtig) uren, met bevel dat indien deze straf niet naar behoren wordt verricht vervangend
# MATCH HECHTENIS: hechtenis zal worden toegepast voor de duur van 40 (veertig) dagen
modifier2 = r'(?P<modifier2>voorwaardelijk|proeftijd|niet|vervangend|indien|hechtenis|wederrechtelijk)'
months = r'(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)'
# Vordering is ambiguous; often used as "vordering tenuitvoerlegging van voorwaardelijke straf"; do lookahead
straf = r'gevangenis|gevangenisstraf|jeugddetentie|detentie|hechtenis|taakstraf|werkstraf|leerstraf|geldboete|vordering(?!\stenuitvoerlegging)(?!\stot\stenuitvoerlegging)|betaling'
nummer = r'(?<!feit )\d+(?!\s?\]'
# middle regex requires a space before the eenheid; e.g. not to match "uur" in "duur"
# This only works for the second eenheid!... there's no space before ,-- in 64,--
# capture optional / to avoid matching parketnummer
# capture optional - to avoid parsing dates, like 16-09-2021
eenheid1 = r'jaar|jaren|maanden|maand|week|weken|dag|dagen|uur|uren|euro|,[-\d=]{1,2}|(?:\/|-|:)?[\d.]+(?!\s?\])(?:,[-\d=]{1,2})?'
eenheid2 = r'jaar|jaren|maanden|maand|week|weken|dagen|dag|uur|uren' # diff with eenheid1 is absence of money-related matching

# TODO test without 'betaling'
# TODO test without 'gevangenis'
# NOTE kan evt. 'dagen' weglaten, 'dag' matcht ook, ibid. for 'maanden'
# Match backslash before numbers to avoid matching "parketnummer 23/003276-17" as a bedrag
# {1,85} number needs to occur in a window of 85 chars after the hoofdstraf (num is empirically tuned)
# {0,10} short window between num and eenheid, which should follow afterwards directly
# this catches "gevangenisstraf van 12 (twaalf) maanden, waarvan  6 (zes) maanden voorwaardelijk met een proeftijd"!
# Be aware that regex { } require escapes
middle = r'\b(?P<straf>{})\b(?P<test1>[^\n\r;.]{{0,85}}?)(?P<nummer1>{}))(?P<test2>[^0-9\n\r;.]{{0,30}}?)(?P<eenheid1>{})(?P<niettest1>[^0-9\n\r;.]{{0,15}})(?:(?P<nummer2>{}))[^0-9\n\r;.]{{0,30}}?(?:\s(?P<eenheid2>{})))?'.format(straf, nummer, eenheid1, nummer, eenheid2)

# The composed pattern
pattern = r'(?i)(?:{}{})?{}(?:(?P<niettest2>{}){})?'.format(modifier1, connector, middle, connector_long, modifier2)

# https://regex101.com/r/6fbiBD/12
pattern_full = r'(?i)(?:(?P<modifier1>voorwaardelijk|proeftijd|niet|vervangend|indien|mindering|maatregel)[^\n\r;.]{0,100})?\b(?P<straf>gevangenis|gevangenisstraf|jeugddetentie|detentie|hechtenis|taakstraf|werkstraf|leerstraf|geldboete|vordering(?!\stenuitvoerlegging)(?!\stot\stenuitvoerlegging)|betaling)\b(?P<test1>[^\n\r;.]{0,85}?)(?P<nummer1>(?<!feit )\d+(?!\s?\]))(?P<test2>[^0-9\n\r;.]{0,30}?)(?P<eenheid1>jaar|jaren|maanden|maand|week|weken|dag|dagen|uur|uren|euro|,[-\d=]{1,2}|(?:\/|-|:)?[\d.]+(?!\s?\])(?:,[-\d=]{1,2})?)(?P<niettest1>[^0-9\n\r;.]{0,15})(?:(?P<nummer2>(?<!feit )\d+(?!\s?\]))[^0-9\n\r;.]{0,30}?(?:\s(?P<eenheid2>jaar|jaren|maanden|maand|week|weken|dagen|dag|uur|uren)))?(?:(?P<niettest2>[^\n\r;.]{0,150})(?P<modifier2>voorwaardelijk|proeftijd|niet|vervangend|indien|hechtenis|wederrechtelijk))?'

regex_hoofdstraf = re.compile(pattern)

# Regex for TBS (ter beschikking stelling)
# "ter beschikking gesteld" wordt ook voor goederen gebruikt
# tbs = r'(?i)(?P<TBS>TBS|terbeschikkingstelling|ter beschikking (?:stelling|[^\n\r;.]*gesteld))[^\n\r;.]*(?P<type>verple(?:egd|ging)|voorwaarden)'
# pattern_tbs = r'(?i)(?P<verlenging>verlengt|verlenging)[^\n\r;.]{0,50}(?P<TBS1>TBS|terbeschikkingstelling|ter beschikking (?:stelling|gesteld))|(?P<TBS2>TBS|terbeschikkingstelling|ter beschikking (?:stelling|(?:\w+\s)?gesteld))[^\n\r;.]{0,50}(?P<type>voorwaarden|verpleging)'
pattern_tbs = r'(?i)(?:(?P<verlenging>verlengt|verlenging).{0,50})?(?P<TBS>TBS|terbeschikkingstelling|ter beschikking (?:wordt |is )?(?:stelling|gesteld))(?:(?!voorwaarde|verple).){0,100}(?P<type>voorwaarden|verpleging|verpleegd)?'
# Soms wordt over de "ter beschikking gestelde" gesproken.
# "Tegen deze beslissing kan het openbaar ministerie binnen veertien dagen na de uitspraak en de ter beschikking gestelde binnen veertien dagen na betekening daarvan beroep instellen bij het gerechtshof Arnhem-Leeuwarden"

regex_TBS = re.compile(pattern_tbs)

# Vrijspraak
# Vaak is er vrijspraak op het ene feit, maar een straf voor het andere.
# Ik kan ook vrijspraak als "volledige vrijspraak" identificeren, d.w.z. als er nergens een straf
# wordt gevonden (maar dan zou ik eigenlijk ook bijkomende straffen moeten meenemen)
# 'De verdachte wordt vrijgesproken'
# 'Rechter beslist vrijspraak'
# 'Rechter spreekt verdachte vrij'
# 'wijst af de vordering van de officier van justitie'
# 'wijst het verzoek tot wraking van mr. X af'
# "spreekt verdachte vrij van wat meer of anders is ten laste gelegd;" (geen vrijspraak maar 'ne bis in idem'!)

# We are more liberal here; do not let period block match, e.g. in ``wijst het verzoek tot wraking van mr. H.H. Dethmers af.''
# Instead, just look within a certain window
# Do not match ne bis in idem: 'spreekt verdachte vrij van wat meer of anders is ten laste gelegd'
# vrijspraak = r'(?i)vrijgesproken|vrijspraak|spreekt[^.\r\n;]*\svrij|wijst[^\r\n;]{0,100}\saf'
# Nieuw pattern with ne bis in idem exception; also more efficient with tempered greedy scope
pattern_vrijspraak = r'(?i)(?P<vrijspraak>vrijgesproken|vrijspraak|spreekt[^.\r\n;]*\svrij|wijst[^\r\n;]{0,100}\saf)(?:(?!meer of anders).){0,50}(?P<nebisinidem>meer of anders (?:ten laste is|is ten laste) gelegd)?'
regex_vrijspraak = re.compile(pattern_vrijspraak)

# Dictionaries with relevant information
# 'uur' is special case and is not included, as it's less than a day
to_days = {'jaren': 365,
           'jaar': 365,
           'maanden': 30.42,
           'maand': 30.42,
           'weken': 7,
           'week': 7,
           'dagen': 1,
           'dag': 1,
           ' ': 0,
           '': 0}


def diff_pattern(pattern_from: str, pattern_to: str):
    '''
    Utility function that shows how to change one pattern into another
    Useful for comparing two regular expressions.
    '''
    print('{}\n=>\n{}'.format(pattern_from, pattern_to))
    for i, s in enumerate(difflib.ndiff(pattern_from, pattern_to)):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            print(u'Delete "{}" from position {}'.format(s[-1], i))
        elif s[0] == '+':
            print(u'Add "{}" to position {}'.format(s[-1], i))


def label_hoofdstraf(beslissing: str):
    '''
    This function takes a input string which may contain multiple punishments.
    Output is a vector of the following shape:
    ('TBS', 'gevangenisstraf', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak')

    In case of 'TBS' and 'vrijspraak' the vector element is binary {0,1}.
    In case of 'geldboete' the vector element is an integer amount of euros
    In case of the other punishments, the vector element is the length in days

    beslissing: string with Dutch text containing punishments

    returns:    ('TBS', 'gevangenisstraf', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak')
    '''

    # NOTE Bij geldboetes kan ik ze ook in categorieen opdelen
    # 1. 390 euro
    # 2. 3.900 euro
    # 3. 7.800 euro
    # 4. 19.500 euro
    # 5. 78.000 euro
    # 6. 780.000 euro

    matches = regex_hoofdstraf.finditer(beslissing)  # returns match objects

    # Map all forms of hoofdstraffen on these keys!
    labels = ('TBS', 'gevangenisstraf', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak')

    # We will store the cumulative sentence per label in a vector
    # straf_vector = defaultdict(int, {key: 0 for key in labels})
    straf_vector = dict(zip(labels, [0]*len(labels)))

    # print("BESLISSING\n", beslissing)
    for match in matches:

        # Use named capture groups to robustly retrieve elements
        # Immediately 'sanitize' by converting to lower case
        modifier1 = match['modifier1'].lower() if match['modifier1'] else None
        hoofdstraf = match['straf'].lower()
        # If we find a amount of money, it's also stored under nummer1 and eenheid1
        nummer1 = match['nummer1']
        eenheid1 = match['eenheid1'].lower()
        nummer2 = match['nummer2']
        eenheid2 = match['eenheid2'].lower() if match['eenheid2'] else None
        modifier2 = match['modifier2'].lower() if match['modifier2'] else None

        # Euro test (a connector that we capture to test for presence of euro sign)
        test1 = match['test1'].lower() if match['test1'] else None  # check e.g. for presence of euro sign
        test2 = match['test2'].lower() if match['test2'] else None  # check for presence of month
        niettest1 = match['niettest1'].lower() if match['niettest1'] else None
        niettest2 = match['niettest2'].lower() if match['niettest2'] else None

        # Some of the terms in the regex are synonymous, so we map them to a consistent label set
        # gevangenis|gevangenisstraf|detentie|hechtenis|werkstraf|taakstraf|geldboete|vordering|betaling
        if hoofdstraf == 'gevangenis':
            hoofdstraf = 'gevangenisstraf'
        elif hoofdstraf == 'detentie' or hoofdstraf == 'jeugddetentie':
            hoofdstraf = 'hechtenis'
        elif hoofdstraf == 'werkstraf' or hoofdstraf == 'leerstraf':
            hoofdstraf = 'taakstraf'
        elif (hoofdstraf == 'vordering' or hoofdstraf == 'betaling'):
            hoofdstraf = 'geldboete'

        # Show the whole match for better debugging
        print(f"MATCH {match['straf'].upper()}: {match[0]}")

        # Ignore matches if there's a negation in the same sentence
        # NOTE I could make {0,10} greedy -> {0,10}? in which niettes1 is superfluous
        # so that "niet" at end is always matched by modifier2
        # but this has a nasty side effect: will often prevent matching optional group
        # with nummer2 and eenheid2 if modifier2 is present.
        if (modifier1 == 'niet') or (modifier2 == 'niet'):
            print("Negation detected at beginning or end of match. Skipped.")
            continue

        if modifier1 == 'mindering' or (test1 and 'mindering' in test1):
            print("'in mindering' detected. Skipped.")
            continue

        # NOTE I don't test for plain old niet' anymore; problem?
        if ((niettest1 and ('niet ten uit' in niettest1 or 'niet tenuit' in niettest1))
           or (niettest2 and ('niet ten uit' in niettest2 or 'niet tenuit' in niettest2))):
            print("Negation ('niet ten uitvoer') detected. Skipped.")
            # NOTE this could be "voorwaardelijk part of the sentence"
            continue

        if (test1 and 'heeft doorgebracht' in test1) or (test1 and 'is doorgebracht' in test1):
            print("Previous punishment detected. Skipped.")
            continue

        # Avoid matching "parketnummer 23/003276-17" as nummer1: 23, eenheid1: 003276, nummer2: 17
        # We capture an optional / to check for this case
        # Check for '-' to avoid matching dates like 16-09-2021
        if eenheid1.startswith('/') or eenheid1.startswith('-') or eenheid1.startswith(':'):
            print("Identifier detected, e.g. a date, case number, law reference. Skipped.")
            continue

        # Edge case: ``vordering van de benadeelde partij [benadeelde 6] (parketnummer 03.155784.19 feit'' (ECLI:NL:RBLIM:2020:9868)
        if eenheid1.startswith('.'):
            dot_positions = [match.start() for match in re.finditer(r'\.', eenheid1)]
            diffs = np.diff(dot_positions)
            if any(diffs > 4):
                print("WARNING: detected fine is invalid and probably an identifier instead. Skipped.")
                continue

        if modifier1 == 'maatregel':
            print("Measure ('maatregel') detected. Skipped")
            continue

        if (test1 and 'wederrechtelijk verkregen voordeel' in test1) or modifier2 == 'wederrechtelijk':
            print("Measure to return unlawfully obtained advantages detected. Skipped.")
            continue

        if test1 and ('schadevergoed' in test1 or 'smartengeld' in test1):
            print("Measure for compensation detected. Skipped.")
            continue

        if (test1 and 'aan de staat' in test1):
            print("Payment to state detected. Probably duplicated sum. Skipped.")
            continue

        # Fine or community service typically have replacement custody;
        # we are interested in the main verdict; the replacement is not counted as an additional punishment
        # "indien verdachte de taakstraf niet naar behoren verricht, vervangende hechtenis
        # zal worden toegepast van 110 dagen"
        # "... taakstraf niet naar behoren heeft verricht, wordt vervangende hechtenis toegepast van 50 (vijftig) dagen" (ECLI:NL:RBAMS:2020:6339)
        if (modifier1 == 'vervangend'  # or modifier2 == 'vervangend'
                or modifier1 == 'indien'  # or modifier2 == 'indien'  # misschien ook 'als'?
                or (test1 and 'vervangen' in test1)):  # catches 'ter vervanging van' and `vervangende straf`
            print("Subsidiary punishment detected. Skipped.")
            continue

        # NOTE if specifically modifier2 indicates a voorwaardelijke straf, we do not count it to the total
        # as in: "gevangenisstraf van 12 (twaalf) maanden, waarvan  6 (zes) maanden voorwaardelijk met een proeftijd"
        # This is a punishment of 12 months and not 16 months
        if (modifier1 == 'voorwaardelijk' or modifier2 == 'voorwaardelijk'
                or modifier1 == 'proeftijd' or modifier2 == 'proeftijd'):
            print("Conditional punishment detected.")
            # NOTE we count a conditional punishment as a punishment nevertheless!
            # We later distinguish 'voorwaardelijk' at the beginning and end. See below.
            # i.e. "voorwaardelijke gevangeniststraf" -> main punisment
            # and "gevangeniststraf van X jaar, waarvan 2 jaar voorwaardelijk" -> second part conditional, is discarded
            # continue  # looks like this throws away too many good matches,

        # There are two main cases
        # 1. We have a fine, in which case we want to match an amount of euros
        # 2. We have a form of detainment or community service, in which case we want to find a temporal duration
        #
        # We want to reject fines with temporal durations; as well as detainments with monetary values
        # This can happen in edge cases where replacement punishments are discussed
        # e.g. "5 uur taakstraf per 50 euro niet betaald"
        # e.g. "betaling en verhaal te vervangen door 100 dagen gijzeling"

        # Month test (connector that we capture to check for 10 juli 2018)
        month_detected = False
        months = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
        # test2 is an optional match
        if test2:
            for month in months:
                if month in test2 or (niettest1 and month in niettest1):
                    month_detected = month

        #   text          -> nummer1  eenheid1
        # 1. 20 euro       -> 20   euro    (eurocheck false)
        # 2. 2.000 euro    -> 2    .000    (eurocheck false)
        # 3. 2.000,-       -> 2    .000,-  (eurocheck false)
        # 4. € 20          -> 2    0       (eurocheck true)
        # 5. € 20,--       -> 20   ,--     (eurocheck true)
        euros = None
        # If we have detected a month like '22 januari 2020'
        # then avoid triggering case 4; otherwise we end up with 22202 euros (oops!)
        if month_detected:
            print(f"WARNING: Date detected with month '{month_detected}'. Skipped")
            continue
        if eenheid1 == 'euro':
            euros = int(nummer1)
        elif eenheid1.startswith(',') or eenheid1.startswith('.'):
            # This is a bit weird, but the regex was easier to write if e.g. in 80,--
            # '80' is captured by nummer1 and ',--' by eenheid1
            euros = nummer1 + eenheid1
            # Split on comma, if present; keep amount of euros as integer, discard cents
            euros = int(re.sub(r'\D', '', euros.split(",")[0]))
        elif all(c.isdigit() for c in eenheid1):
            euros = int(nummer1 + eenheid1)

        # Normalize eenheid1
        if euros:
            eenheid1 = 'euro'

        # Main case 1
        if hoofdstraf == 'geldboete':
            if not euros:
                print(f"WARNING: Indication for fine detected, but ({nummer1},{eenheid1}) is no valid amount of euros")
                continue

            # Update straf vector with euros only if hoofdstraf is 'geldboete'
            straf_vector['geldboete'] += euros

            # Go to next match
            continue

        # Main case 2: compute length of punishment in days
        else:
            # If we have found euros but no fine, skip this match
            if euros:
                print("Amount of euros found, but punishment is not a fine")
                continue

            # In some edge cases we may match digits, even though we don't have a fine
            # e.g. ``gevangenisstraf voor de duur van vierentwintig [24] maanden'' (ECLI:NL:RBNHO:2020:11168)
            # 24 is not matched as a number due to the negative lookahead for ']'
            # Therefore 2 is parsed as nummer1, and 4 as eenheid1. Not good.
            if any(c.isdigit() for c in eenheid1):
                print("Digits are not allowed in temporal unit. Match skipped.")
                continue

            # We need nummer1 as integer to do some computations
            nummer1 = 0 if nummer1 == '' else int(nummer1)

            # If unit is in hours, compute and round to number of days
            if eenheid1 == 'uur' or eenheid1 == 'uren':
                # For now save in hours, later round off to days
                # In some edge cases we may add two components
                # If we round up in between, we may overestimate the punishment in days
                straf_vector[hoofdstraf] += nummer1
            # Otherwise, use to_days dict to convert to number of days
            else:
                # Unit of 'taakstraf' has to be hours or days
                # 'taakstraf niet ten uitvoer zal worden gelegd, tenzij verdachte zich voor het einde van de
                # op 2 (twee) jaren gestelde proef' (ECLI:NL:RBAMS:2021:7066)
                if hoofdstraf == 'taakstraf':
                    # NOTE this part of the loop is not reached when the unit is in hours
                    # so we only have to check for presence of days
                    if 'dag' not in eenheid1:
                        print("WARNING: community service has to be specified in hours or days. Skipped!")
                        continue

                if eenheid1 not in to_days.keys():
                    raise KeyError(f"Tijdseenheid '{eenheid1}' has not been assigned a priority value")
                straf_vector[hoofdstraf] += int(to_days[eenheid1] * nummer1)

            # Unlike with fines, we optionally have a second component
            # 'gevangenisstraf van 12 (twaalf) maanden en 6 (zes) maanden'
            #
            # In the following edge case, we do not want to add the second component
            # 'gevangenisstraf van 12 (twaalf) maanden, waarvan 6 (zes) maanden voorwaardelijk'

            # Second component is optional, so do a check
            if nummer2:
                # Note that this check is only performed on the second component
                if modifier2 == 'voorwaardelijk' or modifier2 == 'proeftijd':
                    print("WARNING: Second part of sentence is conditional. This part is excluded.")
                    continue

                if (niettest1 and 'subsidiair' in niettest1) or (niettest2 and 'subsidiair' in niettest2
                   or modifier2 == 'vervangend' or modifier2 == 'indien' or 'vervangend' in test2):
                    print("Subsidiary punishment detected. This part is excluded.")
                    continue

                nummer2 = 0 if nummer2 == '' else int(nummer2)

                # If unit is in hours, compute and round to number of days
                if eenheid2 == 'uur' or eenheid2 == 'uren':
                    straf_vector[hoofdstraf] += nummer2
                # Otherwise, use to_days dict to convert to number of days
                else:
                    if eenheid2 not in to_days.keys():
                        raise KeyError(f"Tijdseenheid '{eenheid2}' has not been assigned a priority value")
                    straf_vector[hoofdstraf] += int(to_days[eenheid2] * nummer2)

    # Convert community service from hours to days
    straf_vector['taakstraf'] = math.ceil(straf_vector['taakstraf'] / 24)

    for match in regex_TBS.finditer(beslissing):
        verlenging = match['verlenging']
        # tbs1 = match['TBS1']  # Corresponds to verlenging
        # tbs2 = match['TBS2']  # Correspondings to new TBS with type indication
        # tbs = tbs1 if tbs1 else tbs2
        tbs = match['TBS']
        tbs_type = match['type']

        print("MATCH TBS:", match.group(0))

        # If neither of the optional groups are present, we may have a false positive
        # talking about "het ter beschikking stellen" e.g. of goods
        if not verlenging and not tbs_type:
            print("WARNING: neither 'verlenging' nor 'type' of TBS detected. Skipped.")
            continue

        # NOTE it doesn't seem to make sense to match a duration, because TBS is often
        # imposed without duration. Or is there always an accompanying prison sentence
        # that says something about the duration?
        straf_vector['TBS'] = 1

    for match in regex_vrijspraak.finditer(beslissing):
        print("MATCH VRIJSPRAAK:", match.group(0))
        if match['nebisinidem']:
        # TODO The following ne bis in idem is not caught
        # "Verklaart niet bewezen hetgeen aan verdachte meer of anders is ten laste gelegd dan hiervoor is bewezen verklaard en **spreekt verdachte daarvan vrij**"
            print("'ne bis in idem' detected. Skipped.")
            continue

        # 3x vrijspraak is not necessarily "more" vrijspraak in any meaningful sense
        # could just mean that more subsidiary charges have been made
        # we therefore just register acquittal as a binary variable
        straf_vector['vrijspraak'] = 1

    # Several checks using domain knowledge
    # In NL prison sentence is max 30 years = 10950 days
    # Maximum community service is 240 hours = 10 days
    # I don't know the max hechtenis, but I suspect a year = 365 days.
    if straf_vector['gevangenisstraf'] > 10950:
        print("XXXXXXXXXXXXXXXXXXXXX")
        print("ERROR: maximum prison sentence exceeded. There is probably a parsing mistake.")
        print("Cutting off at maximum")
        print("XXXXXXXXXXXXXXXXXXXXX")
        straf_vector['gevangenisstraf'] = 10950
    if straf_vector['hechtenis'] > 487:
        print("XXXXXXXXXXXXXXXXXXXXX")
        print("ERROR: maximum custody exceeded. There is probably a parsing mistake")
        print("Cutting off at maximum")
        print("XXXXXXXXXXXXXXXXXXXXX")
        straf_vector['hechtenis'] = 487
    if straf_vector['taakstraf'] > 10:
        print("XXXXXXXXXXXXXXXXXXXXX")
        print("ERROR: maximum community service exceeded. There is probably a parsing mistake")
        print("Cutting off at maximum")
        print("XXXXXXXXXXXXXXXXXXXXX")
        straf_vector['taakstraf'] = 10
    if straf_vector['geldboete'] > 900000:
        print("XXXXXXXXXXXXXXXXXXXXX")
        print("ERROR: maximum fine exceeded. There is probably a parsing mistake")
        print("Cutting off at maximum")
        print("XXXXXXXXXXXXXXXXXXXXX")
        straf_vector['geldboete'] = 900000

    # Convert to tuple ('TBS', 'gevangenisstraf', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak')
    print("OUT:", straf_vector)
    straf_vector = tuple(straf_vector.values())
    if not any(straf_vector):
        print("================")
        print("NO MATCHES FOUND")
        print("================")

    return straf_vector


def pick_highest_from_vector(straf_vector: tuple):
    '''
    label_vector:   tuple ('TBS', 'gevangenisstraf', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak')

    Returns:    type of punishment (e.g. 'gevangenisstraf') and the amount (e.g. '365' days)

    NOTE: we simply assume here that the tuple is ordered by priority!
    That is, if we encounter a non-zero value starting from the left, than this is the most significant punishment.
    '''
    labels = ('TBS', 'gevangenisstraf', 'hechtenis', 'taakstraf', 'geldboete', 'vrijspraak')
    for i, amount in enumerate(straf_vector):
        if amount > 0:
            return labels[i], amount
    return 'nan', 0


def extract_all_straf_vectors(df, data_column='data'):
    # Require a 'type' column, because only "beslissing", and ... are relevant for labelling
    beslissingen = df.loc[df['type'] == 'beslissing'][data_column]
    # wetten = df[ df['articles'] ]
    # strafoplegging = df.loc[ df['type'] == 'strafoplegging']

    straffen = []
    hoogste_straf = []
    hoogste_duur = []

    n_straffen = 6

    for i, beslissing in enumerate(beslissingen):
        print("\n---------------------------------------------")
        print("Case:", beslissingen.index[i])
        print("---------------------------------------------")
        try:
            straf_vector = label_hoofdstraf(beslissing)
            # straf_vector = np.array(straf_vector, dtype='object')
            straf, duur = pick_highest_from_vector(straf_vector)
        # Still throw error, but find out in which case the problem occurs
        except KeyError:
            raise KeyError(f"Key Error occurred in case {beslissingen.index[i]}")
        if len(straf_vector) > n_straffen:
            raise Exception(f"Straf vector of case {beslissingen.index[i]} too long!")
        straffen.append(straf_vector)
        hoogste_straf.append(straf)
        hoogste_duur.append(duur)

    # df = df.assign(straffen=np.nan).assign(straffen=lambda x: x.straffen.astype(object))
    df.loc[df['type'] == 'beslissing', 'straffen'] = pd.Series(straffen, dtype=object).values

    # Additionally store the punishment with highest priority and its amount
    df.loc[df['type'] == 'beslissing', 'hoofdstraf'] = hoogste_straf
    df.loc[df['type'] == 'beslissing', 'straf_hoogte'] = hoogste_duur
    df.fillna('', inplace=True)
    return df


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
    ('- verklaart het ten laste gelegde bewezen, zodanig als hierboven onder 4.4 is omschreven; - spreekt verdachte vrij van wat meer of anders is ten laste gelegd;', (0, 0, 0, 0, 0, 0)),  # ne bis in idem; do not match

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

if __name__ == '__main__':

    # Default values
    data_fn = 'section_data_2021.csv'
    data_dir = './data/'

    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="data_fn", default=data_fn)
    parser.add_argument("-d", "--dir", dest="data_dir", default=data_dir)
    parser.add_argument("--debug", dest="debug", default=False)
    args = parser.parse_args()

    data_fn = args.data_fn
    data_dir = args.data_dir
    DEBUG = args.debug

    print("Loading from", data_dir + data_fn)

    dataloader = DataLoader(data_dir=data_dir, data_key='data', data_fn=data_fn, target='type')
    df = dataloader.load()

    # Check which articles of law are cited in the corpus
    print(utils.check_articles(df))

    # Set this flag if you only want to check and debug some specific cases and test cases
    if not DEBUG:
        # df = label_all_beslissingen(df)
        df = extract_all_straf_vectors(df)
        df.to_csv(dataloader.data_path)
    else:
        print("DEBUG MODE ENABLED.")

    # Testing
    print("==========")
    print("TEST CASES")
    print("==========\n")
    passing = 0
    for i, test in enumerate(tests):
        print(f"TEST CASE {i}: {test[0]}")
        out = label_hoofdstraf(test[0])
        print(out)
        passes = out == test[1]
        print("PASSING:", passes)
        passing += passes
        print()

    print(f"{passing} out of {len(tests)} tests passed.")

    print(f"Used pattern for hoofdstraf:\n{pattern}\n")

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

    # Check whether the structured regex is the same to the full regex after formatting
    diff_pattern(pattern, pattern_full)

    # Select random beslissingen for manual validation
    beslissingen = df.loc[df['type'] == 'beslissing']

    # evaluate_strafmaat_7_feb.md took 25 cases from 2021 (so use paragraph_data_year)
    # I've changed this data set in the meantime (no impact on eval though), so here is a manual list of the original validation cases
    # old_val_ECLIds = ['ECLI:NL:RBAMS:2021:9', 'ECLI:NL:RBDHA:2021:1297', 'ECLI:NL:RBGEL:2021:1150', 'ECLI:NL:RBGEL:2021:1389', 'ECLI:NL:RBGEL:2021:1412', 'ECLI:NL:RBGEL:2021:429', 'ECLI:NL:RBGEL:2021:689', 'ECLI:NL:RBGEL:2021:736', 'ECLI:NL:RBLIM:2021:1908', 'ECLI:NL:RBNHO:2021:870', 'ECLI:NL:RBOVE:2021:1080', 'ECLI:NL:RBOVE:2021:1146', 'ECLI:NL:RBOVE:2021:1624', 'ECLI:NL:RBOVE:2021:265', 'ECLI:NL:RBOVE:2021:287', 'ECLI:NL:RBOVE:2021:387', 'ECLI:NL:RBOVE:2021:539', 'ECLI:NL:RBOVE:2021:547', 'ECLI:NL:RBOVE:2021:789', 'ECLI:NL:RBROT:2021:1539', 'ECLI:NL:RBROT:2021:2754', 'ECLI:NL:RBROT:2021:316', 'ECLI:NL:RBROT:2021:3336', 'ECLI:NL:RBZWB:2021:1399', 'ECLI:NL:RBZWB:2021:782']

    old_val_ECLIds = ['ECLI:NL:RBROT:2021:8835', 'ECLI:NL:RBROT:2021:8814', 'ECLI:NL:RBGEL:2021:4518', 'ECLI:NL:RBZWB:2021:3658', 'ECLI:NL:RBOVE:2021:4510', 'ECLI:NL:RBOVE:2021:3609', 'ECLI:NL:RBOVE:2021:75', 'ECLI:NL:RBNNE:2021:2888', 'ECLI:NL:RBOVE:2021:2379', 'ECLI:NL:RBROT:2021:2039', 'ECLI:NL:RBGEL:2021:3033', 'ECLI:NL:RBROT:2021:8751', 'ECLI:NL:RBAMS:2021:7026', 'ECLI:NL:RBOVE:2021:4354', 'ECLI:NL:RBLIM:2021:5488', 'ECLI:NL:RBGEL:2021:6833', 'ECLI:NL:RBOVE:2021:1784', 'ECLI:NL:RBGEL:2021:6569', 'ECLI:NL:RBROT:2021:7766', 'ECLI:NL:RBGEL:2021:2304', 'ECLI:NL:RBOVE:2021:643', 'ECLI:NL:RBOVE:2021:4172', 'ECLI:NL:RBAMS:2021:765', 'ECLI:NL:RBZWB:2021:6216', 'ECLI:NL:RBZWB:2021:3656']

    # Retrieve these previous validation cases
    old_val_cases = beslissingen.loc[old_val_ECLIds]['data']

    # seed = 2020  # used previously
    seed = 2021
    random.seed(seed)
    idx = random.sample(range(len(beslissingen)), k=25)

    cases = beslissingen.iloc[idx]['data']
    # vectors = beslissingen.iloc[idx]['straffen']
    ECLIds = list(beslissingen.index[idx])

    # Assert there's no overlap before merging
    intersection = set(old_val_ECLIds) & set(ECLIds)
    print(len(intersection), intersection)
    assert len(intersection) == 0

    print("Randomly selected cases for validation:", ECLIds, len(ECLIds))

    # Merge with old validation cases
    cases = pd.concat([old_val_cases, cases], axis=0)
    ECLIds = old_val_ECLIds + ECLIds

    print("All selected cases for validation:", ECLIds, len(ECLIds))

    sys.stdout = open('argmine/experiments/evaluate_strafmaat.md', 'w', encoding='utf-8')
    for i, case in enumerate(cases):
        print("CASE:", ECLIds[i])
        print("=============================")
        print("TEXT:")
        print(case)
        print("\nLABEL VECTOR:")
        print(label_hoofdstraf(case))
        print("\n\nTODO evaluate\n\n")
        print("TP:\nFP:\nTN:\nFN:\n\n")

    sys.stdout.close()

    # If I want to add more cases to evaluate later, just repeat sampling (but check for duplicates)
    # idx = random.sample(range(len(beslissingen)), k=25)
    # print(idx)
