from src.dataloader import DataLoader
from src import utils
from src.utils import diff_pattern
# import src.eval_punishment_extraction
from argparse import ArgumentParser
import numpy as np
import re
import math
import pandas as pd

'''
This is a script to extract punishments from the judgments of Dutch criminal law cases.

This script assumes we have a dataset (as produced by caseloader.py and caseparser.py) that can be read in via csv
and has a `type` column with `beslissing` entries indicating which text sections contain the final verdict.

Dutch criminal law knows four main types of punishment ('hoofdstraffen'):

    - prison sentence / gevangenisstraf (levenslang, tijdelijk)
    - custody / hechtenis 
        * but 'voorlopige hechtenis' is not a punishment! opgelegd voor overtredingen;
        * Maximum duur van een jaar; in uitzonderlijke gevallen 1 jaar en 4 maanden = 487 dagen
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

And 'maatregelen':

    - plaatsing psychiatrisch ziekenhuis
    - TBS (Ter Beschikking Stelling)
    - Ontrekking aan het verkeer (van gevaarlijke objecten; lijkt op verbeurdverklaring maar kan ook worden toegepast na vrijspraak)
    - Ontneming wederrechtelijk voordeel ('Plukze' wetgeving: wegnemen van verdiensten verkregen door criminele activiteiten)
    - Schadevergoeding aan slachtoffer (dit wordt niet gezien als straf, maar als compensatie voor het slachtoffer)
    - ISD (Inrichting Stelselmatige Daders): plaatsing in een inrichting voor stelselmatige daders (cf. psych. ziekenhuis en TBS zijn voor geestesgestoorden)
    - ...

This script extracts the four main punishments and the TBS maatregel,
(which is very severe and is informally counted as a main punishment though formally not being one)
'''


class PunishmentPattern():
    """Object to compose patterns for punishment extraction."""

    def __init__(self):

        # I do not want to match cases like "gevangenisstraf een gedeelte, groot 3 (drie) maanden niet ten uitvoer"
        # Negative matching is very hard, so instead I match these modifiers and then do post-filtering on the ones I want to exclude
        # Current limitation: we assume the punishment comes before the duration. E.g. 'veroordeelt de verdachte tot 3 maanden gevangenis' is not matched.
        # Compound punishment is supported: "gevangenisstraf voor de duur van 2 (twee) jaar en 6 (zes) maanden"
        # Things like "maandelijkse termijnen" are excluded
        # [^0-9\n\r.;] avoids matching newlines and dots (which \D *does*), which can cause issues, e.g.:
        # 0-9 prevents that the wildcard consumes the first digit of fines, e.g. in "60 euro" the first 6 will be consumed by the wildcard, only the 0 captures by the "bedrag" pattern
        # However, 0-9 will prevent matches when a digit occurs in between, e.g. "geldboete toegewezen aan [slachtoffer 1] volgens artikel 1 van 60 Euro".
        self.connector = r'[^\n\r;.]{0,100}'  # TODO refactor to use this
        self.connector_long = r'[^\n\r;.]{0,150}'  # TODO refactor to use this
        # Avoid matching parketnummer as large fine in "vordering van de officier van justitie tot tenuitvoerlegging in de zaak met parketnummer 23/003276-17 en gelast de tenuitvoerlegging van de niet ten uitvoer gelegde gevangenisstraf voor de duur" E.g. see ECLI:NL:RBGEL:2020:6993
        self.modifier1 = r'(?P<modifier1>voorwaardelijk|proeftijd|niet|vervangend|indien|mindering|maatregel)'
        # The second part is often a subsidiary custody; we match 'hechtenis' to catch and avoid the following edge case:
        # MATCH TAAKSTRAF: taakstraf van 80 (tachtig) uren, met bevel dat indien deze straf niet naar behoren wordt verricht vervangend
        # MATCH HECHTENIS: hechtenis zal worden toegepast voor de duur van 40 (veertig) dagen
        self.modifier2 = r'(?P<modifier2>voorwaardelijk|proeftijd|niet|vervangend|indien|hechtenis|wederrechtelijk)'
        # NOTE not used?
        self.months = r'(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)'
        # Vordering is ambiguous; often used as "vordering tenuitvoerlegging van voorwaardelijke straf"; do lookahead
        self.straf = r'gevangenis|gevangenisstraf|jeugddetentie|detentie|hechtenis|taakstraf|werkstraf|leerstraf|geldboete|vordering(?!\stenuitvoerlegging)(?!\stot\stenuitvoerlegging)|betaling'
        self.nummer = r'(?<!feit )\d+(?!\s?\]'
        # middle regex requires a space before the eenheid; e.g. not to match "uur" in "duur"
        # This only works for the second eenheid!... there's no space before ,-- in 64,--
        # capture optional / to avoid matching parketnummer
        # capture optional - to avoid parsing dates, like 16-09-2021
        self.eenheid1 = r'jaar|jaren|maanden|maand|week|weken|dag|dagen|uur|uren|euro|,[-\d=]{1,2}|(?:\/|-|:)?[\d.]+(?!\s?\])(?:,[-\d=]{1,2})?'
        self.eenheid2 = r'jaar|jaren|maanden|maand|week|weken|dagen|dag|uur|uren' # diff with eenheid1 is absence of money-related matching

        # TODO test without 'betaling'
        # TODO test without 'gevangenis'
        # NOTE kan evt. 'dagen' weglaten, 'dag' matcht ook, ibid. for 'maanden'
        # Match backslash before numbers to avoid matching "parketnummer 23/003276-17" as a bedrag
        # {1,85} number needs to occur in a window of 85 chars after the hoofdstraf (num is empirically tuned)
        # {0,10} short window between num and eenheid, which should follow afterwards directly
        # this catches "gevangenisstraf van 12 (twaalf) maanden, waarvan  6 (zes) maanden voorwaardelijk met een proeftijd"!
        # Be aware that regex { } require escapes
        self.middle = r'\b(?P<straf>{})\b(?P<test1>[^\n\r;.]{{0,85}}?)(?P<nummer1>{}))(?P<test2>[^0-9\n\r;.]{{0,30}}?)(?P<eenheid1>{})(?P<niettest1>[^0-9\n\r;.]{{0,15}})(?:(?P<nummer2>{}))[^0-9\n\r;.]{{0,30}}?(?:\s(?P<eenheid2>{})))?'.format(self.straf, self.nummer, self.eenheid1, self.nummer, self.eenheid2)

        # The composed pattern
        self.pattern = r'(?i)(?:{}{})?{}(?:(?P<niettest2>{}){})?'.format(self.modifier1, self.connector, self.middle, self.connector_long, self.modifier2)

        # Regex for TBS (ter beschikking stelling)
        # "ter beschikking gesteld" wordt ook voor goederen gebruikt
        # tbs = r'(?i)(?P<TBS>TBS|terbeschikkingstelling|ter beschikking (?:stelling|[^\n\r;.]*gesteld))[^\n\r;.]*(?P<type>verple(?:egd|ging)|voorwaarden)'
        # pattern_tbs = r'(?i)(?P<verlenging>verlengt|verlenging)[^\n\r;.]{0,50}(?P<TBS1>TBS|terbeschikkingstelling|ter beschikking (?:stelling|gesteld))|(?P<TBS2>TBS|terbeschikkingstelling|ter beschikking (?:stelling|(?:\w+\s)?gesteld))[^\n\r;.]{0,50}(?P<type>voorwaarden|verpleging)'
        self.pattern_tbs = r'(?i)(?:(?P<verlenging>verlengt|verlenging).{0,50})?(?P<TBS>TBS|terbeschikkingstelling|ter beschikking (?:wordt |is )?(?:stelling|gesteld))(?:(?!voorwaarde|verple).){0,100}(?P<type>voorwaarden|verpleging|verpleegd)?'
        # Soms wordt over de "ter beschikking gestelde" gesproken.
        # "Tegen deze beslissing kan het openbaar ministerie binnen veertien dagen na de uitspraak en de ter beschikking gestelde binnen veertien dagen na betekening daarvan beroep instellen bij het gerechtshof Arnhem-Leeuwarden"

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
        self.pattern_vrijspraak = r'(?i)(?P<vrijspraak>vrijgesproken|vrijspraak|spreekt[^.\r\n;]*\svrij|wijst[^\r\n;]{0,100}\saf)(?:(?!meer of anders).){0,50}(?P<nebisinidem>meer of anders (?:ten laste is|is ten laste) gelegd)?'

        # Pre-compile the regular expressions because they will be applied frequently
        self.regex_hoofdstraf = re.compile(self.pattern)
        self.regex_TBS = re.compile(self.pattern_tbs)
        self.regex_vrijspraak = re.compile(self.pattern_vrijspraak)


# ----------------------------------------------------------------------------------

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


def label_hoofdstraf(pp: PunishmentPattern, beslissing: str):
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

    matches = pp.regex_hoofdstraf.finditer(beslissing)  # returns match objects

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

    for match in pp.regex_TBS.finditer(beslissing):
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

    for match in pp.regex_vrijspraak.finditer(beslissing):
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


def extract_all_punishment_vectors(pp: PunishmentPattern, df: pd.DataFrame, data_column='data'):
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
            straf_vector = label_hoofdstraf(pp, beslissing)
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


# https://regex101.com/r/6fbiBD/12
# NOTE I use this for regex development
# 1. Develop pattern in an online regex tester
# 2. Paste full pattern here
# 3. Diff with the compiled version of the pattern to make sure both versions are up to date
PATTERN_FULL = r'(?i)(?:(?P<modifier1>voorwaardelijk|proeftijd|niet|vervangend|indien|mindering|maatregel)[^\n\r;.]{0,100})?\b(?P<straf>gevangenis|gevangenisstraf|jeugddetentie|detentie|hechtenis|taakstraf|werkstraf|leerstraf|geldboete|vordering(?!\stenuitvoerlegging)(?!\stot\stenuitvoerlegging)|betaling)\b(?P<test1>[^\n\r;.]{0,85}?)(?P<nummer1>(?<!feit )\d+(?!\s?\]))(?P<test2>[^0-9\n\r;.]{0,30}?)(?P<eenheid1>jaar|jaren|maanden|maand|week|weken|dag|dagen|uur|uren|euro|,[-\d=]{1,2}|(?:\/|-|:)?[\d.]+(?!\s?\])(?:,[-\d=]{1,2})?)(?P<niettest1>[^0-9\n\r;.]{0,15})(?:(?P<nummer2>(?<!feit )\d+(?!\s?\]))[^0-9\n\r;.]{0,30}?(?:\s(?P<eenheid2>jaar|jaren|maanden|maand|week|weken|dagen|dag|uur|uren)))?(?:(?P<niettest2>[^\n\r;.]{0,150})(?P<modifier2>voorwaardelijk|proeftijd|niet|vervangend|indien|hechtenis|wederrechtelijk))?'


if __name__ == '__main__':
    '''
    This script can also be used stand-alone with some parameters.
    '''

    # Default values
    # It is assumed the csv is the result from the query + parsing steps, see pipeline.py
    data_fn = 'parsed_data.csv'
    data_dir = './data/query/'

    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="data_fn", default=data_fn)
    parser.add_argument("-d", "--dir", dest="data_dir", default=data_dir)
    parser.add_argument("--debug", dest="debug", default=False)
    args = parser.parse_args()

    data_fn = args.data_fn
    data_dir = args.data_dir
    DEBUG = args.debug

    print("Loading from", data_dir + data_fn)

    # Load the data frame from the specified csv
    dataloader = DataLoader(data_dir=data_dir, data_key='data', data_fn=data_fn, target='type')
    df = dataloader.load()

    # Check which articles of law are cited in the corpus
    print(utils.check_articles(df))

    # Compile the regex patterns used for extracting punishments
    pp = PunishmentPattern()

    # Check whether the structured regex is the same to the full regex after formatting
    diff_pattern(pp.pattern, PATTERN_FULL)

    # Set this flag if you only want to check and debug some specific cases and test cases
    if not DEBUG:
        # df = label_all_beslissingen(df)
        df = extract_all_punishment_vectors(pp, df)
        df.to_csv(dataloader.data_path)
    else:
        print("DEBUG MODE ENABLED.")
        print("Running tests...")
        # NOTE this delayed import is a quick fix because I have a circular import between
        # this script and eval_punishment_extraction
        # TODO make a proper unit test for this?
        from src.eval_punishment_extraction import test_cases, manual_eval_random_cases

        # Run the pattern on a set of tests
        test_cases(pp)

        # Select random cases for manual validation
        manual_eval_random_cases(df, pp, seed=2021)
