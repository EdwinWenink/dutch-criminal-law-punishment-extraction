import glob
import regex
from pathlib import Path
import pandas
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import numpy as np
from src.utils import get_logger

log = get_logger(__name__)


class CaseParser:
    '''
    Parses case xml from Open Data van de Rechtspraak
    as requested through RESTful API from rechtspraak.nl
    '''

    def __init__(self, data_key='data', level='section', include_section_titles=False, exclude_procedures=[]):
        '''
        params:

        data_key:       preferred column name to store the parsed text data under
        level:          whether to store data on section or paragraph level
        include_section_titles:     one may want to exclude these for ML applications, since they are used for labelling
        '''
        super().__init__()

        # This matches article numbers of length 1-3 (wetboek strafrecht goes to 400+)
        # optionally with a clause, e.g. '14b'.
        # The negative lookahead ensures that matches are *not* at the start of the line
        # because these are probably section numbering.
        # This does assume you strip leading spaces or newlines with .strip()
        # This regex is simple but is only applied to the 'toepasselijke wettelijke voorschriften' sections
        # See https://regex101.com/r/ie8oKR/1
        artikel_nr_pattern = r'(?!^)\b\d{1,2}\w?\b'
        self.artikel_nr = regex.compile(artikel_nr_pattern)
        self.data_key = data_key   # where to store the text data in the final dataframe
        # TODO maybe add self.data_dir? Take into account the case xmls may be in a sub folder
        self.include_section_titles = include_section_titles
        self.level = level
        self.exclude_procedures = exclude_procedures

    def get_raw_text(self, results):
        '''
        Gets all raw text from a bs4.element.ResultSet which you get after a find_all() call
        Does NOT work for a Tag
        Returns raw text as a single string

        In principle each case only has one section with the beslissing identified
        But for robustness I assume there can be multiple, just in case
        '''

        # TODO does this work? No it does NOT.
        # assert isinstance(results, bs4.element.ResultSet)

        # TODO make this also handle e.g. a list of text and other scenarios?
        # If TAG just directly use get_text()

        raw_text = []
        for result in results:
            raw_text += [text for text in result.stripped_strings]
        # The following nested list comprehension actually interweaves the word order and has a different length
        # [ text for text in beslissing.stripped_strings for beslissing in beslissingen]
        return ' '.join(raw_text)

    def parse_case(self, case):

        # Parse the xml of the case text
        soup = BeautifulSoup(case, features='xml')

        # The section titles are formatted like this "<nr>1</nr>Title"
        # When calling get_text(), this will give "1Title"
        # As a dirty fix, I append a space within each <nr> tag
        for nr in soup.find_all('nr'):
            if isinstance(nr.string, str):
                nr.string = nr.string+' '
            else:
                # There is an edge case where nr.string is a NoneType
                print(f"Warning: <nr> {nr.string} in {nr} is of type {type(nr.string)} ")

        # Metadata
        description = soup.Description

        # Get case identifier
        ECLI = description.identifier.text

        # Type of procedure
        procedure = description.procedure.text.strip()

        # Do not parse case if it's of a procedure in the exclude list
        if procedure in self.exclude_procedures:
            print(f"Skipping {ECLI} ({procedure})")
            return None, None, None, None

        # Date of case
        date = description.date.text.strip()

        # Rechtsgebieden (can be multiple!)
        subject = description.subject.text
        subject = regex.split(';|,', subject)
        subject = [x.strip() for x in subject]

        try:
            # Inhoudsindicatie of the case
            inhoudsindicatie = soup.inhoudsindicatie

            # If for some reason we haven't found the ECLI from metadata yet,
            # We can also get it from the inhoudsindicatie
            if ECLI is None:
                ECLI = inhoudsindicatie.get('id')

            # We don't need the soup object anymore, just the text
            inhoudsindicatie = inhoudsindicatie.get_text()
        except AttributeError as e:
            print("Parsing <inhoudsindicatie> failed")
            print(e)
            inhoudsindicatie = ''

        print("Parsing case ", ECLI)

        try:
            # This fails e.g. for ECLIs of type PHR -> ECLI:NL:PHR:YYYY:XXXX
            case_raw = soup.uitspraak.get_text()
        except AttributeError as e:
            print(e)
            # If this happens, "inhoudsindicatie" is included in case_raw
            # So filter it out again to avoid duplicating text
            case_raw = soup.get_text()
            case_raw = case_raw.replace(inhoudsindicatie, '')

        # - Uitspraak.info
        #
        # Uitspraak from rechtspraak contains <section role="{}"> with following role labels:
        # - Procesverloop
        # - Overwegingen
        #   * Motivering van de straf
        #   * Overwegingen
        #   * Aanvullende strafmotivering
        #   * Beoordeling van het wrakingsverzoek
        #   * De beoordeling van het beklag
        #   * Overweging met betrekking tot het bewijs
        #   * Overwegingen met betrekking tot de tenlastegelegde feiten
        # - Beslissing

        '''
        The overwegingen contain the most interesting arguments
        If I want to get them, I need to further parse overwegingen for paragraphs matching:

        Waardering bewijs

        Standpunt van het Openbaar Ministerie

        Standpunt van de verdediging

        Vaststaande feiten

        Motivering straf

        Oordeel van de rechtbank
        '''

        # Maintain a separate idx for paragraphs
        par_id = 0

        # uitspraak.info
        info = soup.find_all('uitspraak.info')
        info_raw = self.get_raw_text(info)

        section_data = []
        # In the CaseLoader class, there is an additional check to not retrieve xmls
        # without section tags; if check is not done, this may be an empty list
        sections = soup.find_all('section')

        # Label sections
        for section_id, section in enumerate(sections):
            title = section.title.get_text(strip=False).strip()  # Do not use the bs4 strip, breaks!
            if section.has_attr('role'):
                label = section.get('role')  # overweging, beslissing, procesverloop
            else:
                label = self.label_based_on_title(title)

            '''
            #section_text = self.get_raw_text(section)  # my own function only works on ResultSet
            if self.include_section_titles:
                # The following line retrieves all text of the whole section, INCLUDING title
                section_text = section.get_text().strip()
            # Alternatively, we may want to exclude the title, since we used it for labeling
                else:
            '''

            if self.include_section_titles:
                section_text = f"{title}\n"
                par_texts = [title]
            else:
                section_text = ''
                par_texts = []

            pars = section.find_all('para')
            for par in pars:
                # There are empty paragraphs, e.g. <par></par>
                if par:
                    par_text = par.get_text()
                    # Only keep paragraphs with sensible text
                    # E.g. filter out '======================'
                    # if any(char.isalnum() for char in par_text): # keeps paragraphs with only digits, e.g. '1'
                    # NOTE Next line *does* filter out '1' as well
                    if par_text.lower().islower():  # Sneaky trick to check if string contains alphabetical chars
                        section_text = f"{section_text}\n{par_text}"
                        par_texts.append(par_text)

                # Deal with degenerate cases where only a space or newline is added
                section_text = section_text.strip()

            # TODO find articles for other section types as well
            # TODO if paragraph level, store refs per paragraph?
            if label == 'wettelijke voorschriften':
                # Parse article references with regex
                # Take into account that section titles also begin with a number
                articles = self.artikel_nr.findall(section_text)
            else:
                articles = []

            # Store data per paragraph
            if self.level == 'paragraph':
                for par_text in par_texts:
                    # Keep a separate count for paragraphs
                    par_id += 1
                    section_data.append({
                        'ECLI': ECLI,
                        'section_id': par_id,  # Still store under section_id to keep structure simple
                        'title': title,
                        'type': label,
                        self.data_key: par_text,
                        'articles': articles,
                        'subject': subject,
                        'procedure': procedure,
                        'date': date
                        })

            # Default to section level
            else:
                # Record data in a list of lists
                # Each element list will be a data row later on
                section_data.append({
                    'ECLI': ECLI,
                    'section_id': section_id,
                    'title': title,
                    'type': label,
                    self.data_key: section_text,
                    'articles': articles,
                    'subject': subject,
                    'procedure': procedure,
                    'date': date
                    })

        # TODO maybe include inhoudsindicatie as a separate section with type='inhoudsindicatie'
        return ECLI, case_raw, inhoudsindicatie, section_data

    def label_based_on_title(self, title):
        '''
        Rule based labelling based on section title
        The philosophy of this funtion is to label as much as possible
        and then decide later which sections are irrelevant for a given application
        (e.g. "Bijlagen").
        '''

        # TODO candidate titles to cover from "overig"; similar titles grouped
        # "Inleiding" <- soortgelijk aan overzicht vooronderzoek?
        # "De behandeling ter terechtzitting"
        # "De aanleiding"
        # "Waar gaat de zaak over?"
        # "Waar het in deze zaak om gaat"
        # "Voorafgaande veroordeling" <- "voorafgaand", paragraaf 2
        # "Arrest van de meervoudige kamer voor strafzaken van het gerechtshof" -> komt maar eens voor geloof ik; statement aan begin van hoger beroep; relatie met voorgaande uitspraak
        # "Het hoger beroep"
        #
        # "Het beklag"
        # "Het geding"
        # "Het cassatieberoep"
        #
        # "De feiten"
        # "De stukken"
        # "De voorhanden stukken"
        # "Bevindingen"
        # "De stukken betreffende het beklag"
        # "Strafbare feiten waarop de voordeelsberekening is gebaseerd"
        # "Uitgelezen data taxi en camerabeelden" -> "data"
        # "Uitgelezen data taxi en reconstructie"
        #
        # "Verklaringen verdachte"
        #
        # Immateriële schade
        # Letsel verdachte
        #
        #
        # "Het verslag van de advocaat-generaal"
        #
        # "Adviezen" (e.g. advies van externe partije zoals een inrichting voor psychologische evaluatie)
        #
        #
        # "moord"
        # "medeplegen van van het plegen van witwassen een gewoonte maken" (...?)
        #
        # Zitten de volgende meer richting bewijs, strafmaat, of uitspraak?
        # "opzettelijk handelen in strijd met het in artikel 2 onder C van de Opiumwet"
        # "handelen in strijd met artikel 26, eerste lid, van de Wet wapens en munitie."
        # "Overtreding van artikel 5 van de Wegenverkeerswet 1994."

        # "Conclusie" -> Niet hetzelfde als beslissing denk ik! Verschillende secties hebben conclusies
        # "Uitspraak"
        # "Tussenconclusie"
        # "Vrijspraak feit [3]" -> onderdeel van materiele vragen, in dit geval of een feit strafbaar is
        #
        # Tenuitvoerlegging voorwaardelijke veroordeling
        #
        #
        # Many entries from "overig" are empty titles with just a number
        #
        # These concepts are fuzzy, e.g. many may contain "standpunten"
        #
        #
        # POSSIBLE CONFLICTS: Cases that would be different with different rule priorities
        # --------------------------------------------------------------------------------
        # "Overwegingen ten aanzien van het bewijs" -> bewezenverklaring or overwegingen
        # "Tenlastelegging, bewezenverklaring, bewijsvoering en kwalificatie" -> ECLI:NL:RBROT:2020:1893
        # "Beslissing op de vordering na voorwaardelijke veroordeling" --> rule for 'vordering' will cause conflict
        # "Vordering van de benadeelde partij" --> rule for 'vordering' causes conflict
        # "Vorderingen benadeelde partijen en schadevergoedingsmaatregelen" --> "vordering" (eis) and "benadeelde partijen"
        # "Overwegingen ten aanzien van het bewijs" --> currently 'bewezenverklaring', could be 'overweging' or 'bewijsoverwegingen'
        # "Kwalificatie en strafbaarheid van [de feiten | het feit]" -> 'kwalificatie' of 'bepaling strafbaarheid' SOLVED: zijn hetzelfde
        # "De strafbaarheid van het bewezenverklaarde" --> 'strafbaarheid' and possible 'bewezenverklaring'
        # "De feitelijke uitgangspunten voor de beslissing van het hof" (ECLI:NL:GHAMS:2020:3491) --> 'beslissing' (current) vs. 'bewezenverklaring'
        # "Bewijsverweren" --> "bewijs" will lead to "bewezenverklaring", but "overweging" may be more appropriate here ( ECLI:NL:RBROT:2020:11301 )

        title = title.lower()

        # TODO Logical order of labels WIP
        # TODO some labels may be specific to particular types of cases; e.g. cassatie, hoger beroep
        # - Identificatie partijen
        # - [Optioneel] Procesverloop TODO is het verschil met 'onderzoek' duidelijk? Nee.
        # - [E.g. in wrakingen] Verzoek
        # - Onderzoek (van de zaak; op de terechtzitting)
        # - [Alleen in hoger beroep] Vonnis waarvan beroep
        # - Tenlastelegging/aanklacht
        # - Strafeis (vordering?) -> Dit is een lastige; overlap met "strafoplegging"
        # - Voorvragen (vier formele vragen)
        #   * 1. Is de dagvaarding geldig: "vastgesteld dat de dagvaarding geldig is"
        #   * 2. Is de rechter bevoegd? "rechter is bevoegd tot kennisneming van de zaak"
        #   * 3. Is het Openbaar Ministerie ontvankelijk? "Openbaar Ministerie is ontvankelijk in zijn vervolging"
        #   * 4. Kan de vervolging zonder schorsing worden voortgezet? "geen redenen tot schorsing van vervolging"
        # - Materiele vragen, chronologische volgorde:
        #   * Kan het ten laste gelegde feit worden bewezen?
        #   * Is het een strafbaar feit? (ook wel 'kwalificatie' van de feiten genoemd)
        #   * Is de dader strafbaar?
        #   * Welke straf of maatregel moet worden opgelegd? (gevangenis, hechtenis/bewaring, taakstraf, geldboete)
        #       - Bevat soms kopje "vordering van de officier van justitie". Dan zou "vordering" dus onder "strafoplegging moeten vallen"
        #       - Echter "vordering tot tenuitvoerlegging" is een apart kopje soms vóór de wettelijke voorschriften
        # TODO "tenuitvoerlegging" van 'vordering' of 'voorwaardelijke veroordeling' als apart kopje?
        # - Het beslag
        # - Benadeelde partij (vaak ná strafoplegging)
        # - Toepasselijke wettelijke voorschriften
        # - Beslissing
        # - Bijlagen

        # Aanpak: de meer specifieke regels moeten logischerwijs prioriteit hebben

        # TODO instead of these exceptions, could also place this rule last.
        if ('straf' not in title and 'ontvankelijk' not in title and 'bevoegd' not in title and 'verzoek' not in title and 'standpunt' not in title
            and ('rechtbank' in title
                 or 'verdachte' in title
                 or 'veroordeelde' in title
                 or 'betrokkene' in title
                 or 'verzoeker' in title
                 or 'verzoekster' in title)):
            # Conflict met 'voorvragen': in Hoger Beroep zaken "Ontvankelijkheid van de verdachte in het hoger beroep" (e.g. ECLI:NL:GHAMS:2020:3222)
            # Conflict 'Strafbaarheid van verdachte'
            # "De rechtbank"
            # "RECHTBANK NOORD-NEDERLAND" -> informatie over rechtbank
            # [verdachte] -> informatie over verdachte
            # [betrokkene]
            # [naam verdachte]
            label = 'identificatie'
        elif ('verloop' in title or 'procedure' in title):
            label = 'procesverloop'
            '''
            # Excluded because I'm now excluding cases e.g. in Raadkamer of Hoge beroep that discuss "verzoeken"
            elif 'verzoek' in title:
                # TODO check meaning
                # "Verzoeken verdediging"
                # "Het verzoek en de reactie daarop"
                # "Voorwaardelijk verzoek"
                # "Het verzoek en de reactie daarop"
                # "Het wrakingsverzoek"
                # "Verzoek tot terugwijzing naar rechtbank"
                label = 'verzoek'
            '''
        elif 'onderzoek' in title or 'terechtzitting' in title:
            # Korte statement over waar de zaak is behandeld, bijv:
            # "De zaak is inhoudelijk behandeld op de zitting van 18 november 2020, waarbij de officier van justitie, mr. Vroombout en de verdediging hun standpunten kenbaar hebben gemaakt." (ECLI:NL:RBZWB:2020:5981)
            # "Dit vonnis is gewezen naar aanleiding van het onderzoek op de openbare terechtzitting van 23 november 2020. De verdachte is niet verschenen." (ECLI:NL:RBOVE:2020:4167)
            # 'Onderzoek van de zaak'
            # 'Onderzoek op de terechtzitting'
            # 'De behandeling ter terechtzitting' (ECLI:NL:RBNHO:2020:10987)
            label = 'procesverloop'
        elif 'vonnis waarvan beroep' in title or 'hoger beroep' in title:
            # Alleen in hoger beroep; bevat of het vonnis waartegen het beroep is ingesteld zal worden vernietigd; dus een soort conclusie
            # E.g. inhoud: "Het beroepen vonnis zal worden vernietigd omdat het hof tot een andere bewezenverklaring komt dan de rechtbank."
            label = 'vonnis waarvan beroep'

        elif 'inleiding' in title or 'aanleiding' in title:
            label = 'inleiding'

        elif ('beoordeling' not in title
              and ('tenlastelegging' in title or 'telastelegging' in title or 'aanklacht' in title
                   or 'beschuldiging' in title or 'primair' in title or 'subsidiair' in title)):

            # Avoid conflict with "De beoordeling van de tenlastelegging" -> Should be "overweging"
            # https://nl.wikipedia.org/wiki/Tenlastelegging
            # Typically at the beginning of a case text. What's the charge?
            # Typically main charge first (primair), then secondary charges indicated by "subsidiair" and "meer subsidiair"
            # "Primair"
            # "Subsidiair"
            # '[De] tenlastelegging'
            # 'De inhoud van de tenlastelegging'
            # "Beschuldigingen"
            label = 'tenlastelegging'

        elif 'eis' in title or 'vordering' in title:
            '''
            Sometimes 'eis' will have it's own section right after 'tenlastelegging'.
            However, sometimes the 'strafeis' or 'vordering' will be e.g. under 'strafoplegging'
            '''
            # Vordering at beginning of the text is synonymous to "eis"
            # TODO But be aware that "vordering tot tenuitvoerlegging" is often its own section later in the text
            # TODO vordering tot tenuitvoerlegging of verbeurdverklaring?
            # E.g. ECLI:NL:RBZWB:2020:6395
            # 'Vordering (tot tenuitvoerlegging)' often contains both 'eis' and the judgement, e.g. 'toewijzing'
            # We can thus expect mistakes between "eis" and "strafoplegging"
            label = 'eis'
            '''
            elif 'vordering' in title:
                # TODO kan onder "strafoplegging vallen"?
                # TODO maar vordering tot tenuitvoerlegging is vaak apart kopje!
                # 'De inhoud van de vordering'
                # 'Vordering van de officier van justitie'
                # 'De vordering'
                # '[De] vordering[en] [tot] tenuitvoerlegging'
                # TODO vordering van officier en vordering tot tenuitvoerlegging zijn NIET hetzelfde!
                # 'Vordering tot verbeurdverklaring'
                # TODO conflict 'De beoordeling van de civiele vorderingen'
                label = 'vordering'
            '''

        # VOORVRAGEN
        # Soms is er een kopje 'voorvragen' waarin het antwoord op deze vier vragen summier wordt gesteld
        # Soms hebben deze vragen een eigen kopje, soms een algemeen kopje als 'voorvragen'
        # Ik vind het het meest consistent om al dezen als 'voorvragen' te labelen;
        # ook zijn het de materiele vragen waar de interessante redeneringen te vinden zijn
        # Checks whether formalities are satisfied, e.g. texts will contain phrases like (these are not titles!)
        # Volgt beslissingsmodel vier formele vragen:
        # 1. Is de dagvaarding geldig: "vastgesteld dat de dagvaarding geldig is"
        # 2. Is de rechter bevoegd? "rechter is bevoegd tot kennisneming van de zaak"
        # 3. Is het Openbaar Ministerie ontvankelijk? "Openbaar Ministerie is ontvankelijk in zijn vervolging"
        # 4. Kan de vervolging zonder schorsing worden voortgezet? "geen redenen tot schorsing van vervolging"

        # VOORVRAAG 1
        elif ('geldig' in title and 'dagvaarding' in title):
            # "Geldigheid dagvaarding"
            # "Geldigheid dagvaarding ten aanzien van feit 2"
            # label = 'geldigheid dagvaarding'
            label = 'voorvragen'

        # VOORVRAAG 2
        elif ('bevoegd' in title):
            # label = 'bevoegdheid rechter'
            label = 'voorvragen'

        # VOORVRAAG 3
        elif 'ontvankelijkheid' in title:
            # "De ontvankelijkheid"
            # "De ontvankelijkheid van [de officier van justitie | het Openbaar Ministerie | het beklag | het hoger beroep]"
            # label = 'bepaling ontvankelijkheid'
            label = 'voorvragen'

        # VOORVRAAG 4
        # Volgens mij nergens expliciet aanwezig; deze is ook meer een ja/nee vraag.

        # Voorvragen fallback
        elif ('voorvragen' in title):
            # Algemeen label als fallback
            label = 'voorvragen'

        # TODO WAAR HOREN 'OVERWEGINGEN' PRECIES THUIS?

        # - Materiele vragen, chronologische volgorde:
        #   1 Kan het ten laste gelegde feit worden bewezen?
        elif ('beoordeling'  in title
                or 'waardering' in title
                or 'overweging' in title
                or 'beschouwing' in title
                or 'verweren' in title  # avoid that 'bewijsverweren' will lead to 'bewijsverklaring'
                or 'verweer' in title
                #or 'bewijsoverweging' in title
                or 'motivering' in title):  # includes 'motivering bewijs'
            # "beoordeling van de vordering"
            # "beoordeling van het eerste [en tweede] cassatiemiddel"
            # 'Motivering bewijs'
            # "Motivering straffen" --> N.B. deze past niet bij materiële vraag 1, meer bij 4
            # Dezelfde structuur als 'overwegingen' maar specifiek over bewijs
            # "Waardering van het bewijs"
            # "Beoordeling van het bewijs"
            # "Overwegingen ten aanzien van het bewijs"
            # "Aanvullende bewijsoverweging"
            # label = 'bewijsoverwegingen'
            label = 'overwegingen'

        elif 'standpunt' in title or 'advies' in title:
            # Standpunten are typically part of some 'overweging'
            # But overwegingen may pertain to 'bewijs' or 'straf'
            # Which means that this labeling on 'standpunt' may
            # be a source of fuzziness between 'overweging' and e.g. 'strafbepaling'
            #
            # "standpunten"
            # "Standpunt van de verdediging"
            # "Standpunt verdediging"
            # "Het standpunt van de verdediging"
            # "Het standpunt van de rechter"
            # "Standpunt [van het] Openbaar Ministerie"
            # "Standpunt van partijen"
            # "De standpunten van partijen"
            # "De standpunten van de veroordeelde en de officier van justitie"
            # "De standpunten van de raadsman en de officier van justitie"
            # "De standpunten van klager, de raadsman en de officier van justitie"
            # "Het standpunt van verzoekers"
            # "Het standpunt van verzoekster" (vrouwelijk)
            # "Het standpunt van de terbeschikkinggestelde en zijn raadsman"
            # "Het standpunt van de reclassering"
            # "Het standpunt van de rapporterende psychiater"
            # "Het standpunt van de rapporterend klinisch psycholoog"
            # "Het standpunt van de inrichting"
            # "Het standpunt van de terbeschikkinggestelde en zijn raadsman"
            # "Advies" (previous few 'standpunten' are in fact advice from external parties, so semantically similar)
            # label = "standpunt"

            # Standpunten are typically presented within "overwegingen"
            label = 'overwegingen'

        # 2. Is het een strafbaar feit? (ook wel 'kwalificatie' van de feiten genoemd)
        # 3. Is de dader strafbaar?
        elif ('kwalificatie' in title or 'strafbaar' in title or 'strafbare' in title):
                '''
                or ('strafbaar' in title and 'feit' in title) # vraag 2
                or ('strafbaar' in title and 'verdachte' in title)): # vraag 3
                '''
                # TODO strafbaarheid van feit (kwalificatie) en verdachte zijn onderscheiden, maar komen soms samen voor!
                # TODO los van elkaar of niet?
                # Betekenis: De kwalificatie van het feit: Zijn de ten laste gelegde handelingen strafbaar?
                # Zie: https://nl.wikipedia.org/wiki/Tenlastelegging
                #
                # "De kwalificatie van het bewezenverklaarde"
                # "Kwalificatie en strafbaarheid van [de feiten | het feit]"
                # "Strafbaarheid van [[het] feit | [de] feiten | het bewezen verklaarde |het bewezenverklaarde]"
                # "Strafbaarheid van verdachte"
                # "Strafbaarheid feiten en verdachte"
                # "Strafbare feiten waarop de voordeelsberekening is gebaseerd"
                # "De strafbaarheid"
                label = 'bepaling strafbaarheid'

        #   4 Welke straf of maatregel moet worden opgelegd? (gevangenis, hechtenis/bewaring, taakstraf, geldboete)
        elif ('oplegging' in title or 'straf' in title or 'verplichting' in title or 'maatregel' in title
            or 'detentie' in title or 'inrichting' in title or 'hechtenis' in title or 'bewaring' in title
            or 'betaling' in title or 'bedrag' in title or 'tenuitvoerlegging' in title):
            # TODO conflict sometimes we can also have "De overwegingen ten aanzien van straf en/of maatregel"
            # TODO conflict "strafbare feiten waarop de voordeelsberekening is gebaseerd"

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
            label = 'strafoplegging'

        elif 'bewezenverklaring' in title or 'bewijs' in title or ('feiten' in title and 'strafbaar' not in title):
            # Typically there's first a section 'bewezenverklaring'
            # where it is stated which *facts* are considered proven
            # followed by a 'bewijs' section which states in which
            # proof the facts stated in 'bewijsverklaring' are grounded
            # I give them the same label
            # Conflict: 'bewijsverweren' should be 'overweging' instead
            #
            # "De feiten"
            # Put lower to avoid conflict e.g. with "Strafbaarheid van de feiten" cf. 'bepaling strafbaarheid'
            label = 'bewezenverklaring'

        elif 'benadeeld' in title:  # and 'partij' in title:
            '''
            This type of section is fuzzy. It may include a 'vordering' for 'schadevergoeding',
            then the judge's judgement whether damages follow from the established facts,
            and then the imposing of a 'maatregel' (cf. label 'strafoplegging')
            E.g. see ECLI:NL:RBZWB:2020:6395
            '''
            # benadeelde partijen
            # TODO conflict with 'vordering': "Vordering van de benadeelde partij"
            # TODO possible conflict with 'strafoplegging': "Vordering benadeelde partij en schadevergoedingsmaatregel"
            # TODO conflict "schade van benadeelde partijen"
            # Solved by putting this rule later i.e. with lower priority
            # "De schade van benadeelden" --> excluded if we require 'partij'
            # TODO we may perhaps label this as "eis", because it contains "vorderingen" from the "benadeelde partijen"
            label = 'benadeelde partijen'

        elif 'beslag' in title:
            label = 'beslag'

        elif ('wettelijke voorschrift' in title
                or ('wettelijke bepaling' in title)
                or ('toepass' in title and 'wet' in title) # catches toepass{ing|elijk}
                or ('artikel' in title)
                or ('juri' in title and 'kader' in title)
              ):
            # This is a section that lists relevant legislature
            # 'Toepasselijke wettelijke voorschriften'
            # "Het wettelijke voorschrift"
            # "De toegepaste wettelijke bepalingen"
            # 'Toepassing van wetsartikelen'
            # "Toegepast wetsartikel"
            # "Juridisch kader"
            #
            # Possible conflict: sometimes the 'tenlastelegging' also mentions articles of law
            # E.g. " ... als bedoeld in de bij de Opiumwet behorende lijst I, dan wel aangewezen krachtens het vijfde lid van artikel 3a van die wet" ( ECLI:NL:RBNHO:2020:10314 )
            # In the case of ECLI:NL:RBNHO:2020:10314 this is only misclassified because the xml has a faulty section header
            label = 'wettelijke voorschriften'

        elif 'beslissing' in title or 'vrijspraak' in title:
            # TODO conflict "De feitelijke uitgangspunten voor de beslissing van het hof"
            # Possible conflict with 'wettelijke voorschriften': "De beslissing is gebaseerd op de volgende wetsartikelen ..."
            # It can happen a case has multiple 'beslissing' sections: "8 Beslissing omtrent in beslag genomen en niet teruggegeven geldbedrag" (ECLI:NL:RBNHO:2020:10314)
            # no `or 'uitspraak' in title` because of conflict with: "Samenstelling raadkamer en uitspraakdatum" (Rekestprocedure)
            # and with "De uitspraak waarvan hierziening is gevraagd"
            label = 'beslissing'
        elif 'bijlage' in title:
            label = 'bijlage'
        else:
            # Kandidaten:
            label = 'overig'

        return label

    def parse_all_cases(self, data_dir, write_to_csv=True, write_case_text=False, include_inhoudsindicatie=True):

        data_dir = Path(data_dir)

        # Collect all data as a dictionary with ECLI as key, section data as value
        data = defaultdict(dict)

        ECLIds = []
        dataframes = []
        for source in glob.glob(f'{data_dir}/*.xml'):
            with open(source, mode='r', encoding='utf-8') as f:
                uitspraak = f.read()
                ECLI, case_raw, inhoudsindicatie, section_data = self.parse_case(uitspraak)
            if ECLI is None:
                continue

            # data[ECLI] = section_data
            ECLIds.append(ECLI)
            frames = []
            for section_dict in section_data:
                # orient='columns' is more intuitive to me
                # but results in jagged arrays; index + transpose instead
                df = pd.DataFrame.from_dict(section_dict, orient='index').T
                frames.append(df)

            # Stack horizontally
            df = pd.concat(frames)
            dataframes.append(df)

            if write_case_text:
                outfile = source.replace('.xml', '.txt')
                with open(outfile, mode='w', encoding='utf-8') as f:
                    if include_inhoudsindicatie:
                        f.write(inhoudsindicatie + case_raw)
                    else:
                        f.write(case_raw)

        if len(dataframes) == 0:
            print("Dataframe is empty! No xml files parsed.")
            return

        df = pd.concat(dataframes, axis=0)

        # Strip all control characters from the data
        # TODO do I want this?
        df[self.data_key] = [regex.sub(r'\p{C}', ' ', dp[self.data_key]) for _, dp in df.iterrows()]

        # Set simple integer index
        df["id"] = list(range(len(df)))
        df.set_index("id", inplace=True)

        # Drop rows with no associated text data
        df[self.data_key].replace('', np.nan, inplace=True)
        print(f"Dropping {np.sum(df[self.data_key].isna())} sections without text")
        df.dropna(subset=[self.data_key], inplace=True)

        # df = pd.concat(dataframes, keys=ECLIds)

        # Data looks like
        # { ECLI :
        #   {
        #   'title': 'This is a case title',
        #   'data': 'This is the section text'
        #   etc...
        #   }
        # }

        # Some text entries will be very long
        # e.g. when opening in excel they are wrapped to the next line
        if write_to_csv:
            df.to_csv(f'{data_dir}/data_{self.level}_{"w_title" if self.include_section_titles else "wo_title" }.csv', header=True)
            log.info("Writing parsed cases to csv")

        return df

    def check_section_labels(self, case, get_raw_text=False):
        '''
        Function to test whether a case xml has labeled sections

        case            case xml
        get_raw_text    return section text without markup
        '''

        soup = BeautifulSoup(case, features='xml')

        # First check if there's sections at all
        # sections = soup.find_all('section')  # returns empty list if not present
        sections = soup.find('section')  # returns None is not present
        if sections is None or len(sections) == 0:  # This catches both scenarios
            log.info("Case xml contains no sections.")
            return False

        # Formele opmerkingen over procesverloop
        # Momenteel niet gebruikt, minder belangrijk dan overwegingen en beslissingen
        # procesverloop = soup.find_all(role='procesverloop')

        # Opsommingen van feiten, relevante bepalingen, wetten
        overwegingen = soup.find_all(role='overwegingen')

        # Dit is doorgaans een extreem korte sectie die zoiets zegt als: bezwaar is gegrond.
        # Let op: in ingewikkelde zaken kan dit een langere opsomming zijn met een reactie op meerdere punten
        # Sommige van die punten worden toegewezen, anderen toegestaan; dus niet eenduidige conclusie
        # De laatste 1 a 2 <parablock> tags zijn doorgaans wat formele info over griffiers etc.
        beslissingen = soup.find_all(role='beslissing')

        # For now only check presence of "overwegingen" and "beslissing"
        return True if len(overwegingen) > 0 and len(beslissingen) > 0 else False

    def inspect_overig_labels(self, df):
        # Print type labels
        print(df['type'].value_counts())

        # Check which labels are still overig
        overig_df = df[ df['type'] == 'overig']
        for i, data in overig_df.iterrows():
            print()
            print(data.loc['ECLI'])
            print(data.loc['title'])
            print(data.loc[self.data_key])
            print()

        print("Overig:", len(overig_df))


if __name__ == '__main__':

    # TODO accept args

    case_dir = 'data/new/query_last_year/cases/'
    # case_dir = 'data/new/query_test/cases/'
    level = 'section' # 'paragraph'
    # When False, you'll have slightly more empty columns,
    # meaning that some sections only have a title
    include_section_titles = True
    # include_section_titles = False
    exclude_procedures = ['Hoger beroep', 'Cassatie', 'Cassatie in het belang der wet', 'Raadkamer', 'Artikel 81 RO-zaken', 'Wraking', 'Beschikking']

    parser = CaseParser(data_key='data',
                        level=level,
                        include_section_titles=include_section_titles,
                        exclude_procedures=exclude_procedures)

    # Parse the returned cases
    df = parser.parse_all_cases(case_dir, write_case_text=False)

    parser.inspect_overig_labels(df)  # NOTE Do this with level='section'!

    # To csv
    with open('data/new/parsed_data.csv', encoding='utf-8', mode='w') as f:
        df.to_csv(f)


    '''

    # Just for quick testing
    query_dir = Path(r'data\type=uitspraak&Subject=http%3A%2F%2Fpsi.rechtspraak.nl%2Frechtsgebied%23strafrecht&date=2020-06-01&date=2021-01-01&max=50&return=DOC')

    for source in glob.glob(f'{query_dir}/*.xml'):
        with open(source, mode='r', encoding='utf-8') as f:
            uitspraak = f.read()
            if parser.check_section_labels(uitspraak, get_raw_text=False):
                print("Check PASSED")
            else:
                print("Check FAILED: ", source)
    '''

    '''
    #ecli = 'ECLI-NL-GHAMS-2020-1451'
    #ecli = 'ECLI-NL-GHARL-2020-4169'
    #ecli = 'ECLI-NL-RBAMS-2020-2789'
    #ecli = 'ECLI-NL-RBAMS-2020-2791'
    #ecli = 'ECLI-NL-RBAMS-2020-2830'
    ecli = 'ECLI-NL-RBAMS-2020-2831'
    #ecli = 'ECLI-NL-RBNHO-2020-4026'

    source = query_dir / f"{ecli}.xml"
    with open(source, mode='r', encoding='utf-8') as f:
        uitspraak = f.read()
    ECLI, case_raw, inhoudsindicatie, section_data = parser.parse_case(uitspraak)
    '''

    #df = parser.parse_all_cases(query_dir, write_case_text=False, include_inhoudsindicatie=True)
    #print(df)

# Soms is er een "grondslag van het geschil" zonder role-identifier

# TODO parsen relevante wetsartikelen en verwijzingen

# TODO Dataset samenvoegen met classificatie van type vergrijp?
