"""
This module contains a class that defines regex patterns for extracting
punishments in Dutch criminal law cases.
"""

import re

from src.utils import diff_pattern


class PunishmentPattern():
    """Object to compose patterns for punishment extraction."""

    def __init__(self):
        # Regex components (see explanation under docs)
        # Be aware that regex { } require escapes
        self.connector = r'[^\n\r;.]{0,100}'
        self.connector_long = r'[^\n\r;.]{0,150}'
        self.modifier1 = r'(?P<modifier1>voorwaardelijk|proeftijd|niet|vervangend|indien|mindering|maatregel)'
        self.modifier2 = r'(?P<modifier2>voorwaardelijk|proeftijd|niet|vervangend|indien|hechtenis|wederrechtelijk)'
        self.straf = r'gevangenis|gevangenisstraf|jeugddetentie|detentie|hechtenis|taakstraf|werkstraf|leerstraf|geldboete|vordering(?!\stenuitvoerlegging)(?!\stot\stenuitvoerlegging)|betaling'
        self.nummer = r'(?<!feit )\d+(?!\s?\]'
        self.eenheid1 = r'jaar|jaren|maanden|maand|week|weken|dag|dagen|uur|uren|euro|,[-\d=]{1,2}|(?:\/|-|:)?[\d.]+(?!\s?\])(?:,[-\d=]{1,2})?'
        self.eenheid2 = r'jaar|jaren|maanden|maand|week|weken|dagen|dag|uur|uren' # diff with eenheid1 is absence of money-related matching
        self.middle = r'\b(?P<straf>{})\b(?P<test1>[^\n\r;.]{{0,85}}?)(?P<nummer1>{}))(?P<test2>[^0-9\n\r;.]{{0,30}}?)(?P<eenheid1>{})(?P<niettest1>[^0-9\n\r;.]{{0,15}})(?:(?P<nummer2>{}))[^0-9\n\r;.]{{0,30}}?(?:\s(?P<eenheid2>{})))?'.format(self.straf, self.nummer, self.eenheid1, self.nummer, self.eenheid2)

        # The composed pattern
        self.pattern = r'(?i)(?:{}{})?{}(?:(?P<niettest2>{}){})?'.format(self.modifier1, self.connector, self.middle, self.connector_long, self.modifier2)

        # Regex for TBS (ter beschikking stelling)
        self.pattern_tbs = r'(?i)(?:(?P<verlenging>verlengt|verlenging).{0,50})?(?P<TBS>TBS|terbeschikkingstelling|ter beschikking (?:wordt |is )?(?:stelling|gesteld))(?:(?!voorwaarde|verple).){0,100}(?P<type>voorwaarden|verpleging|verpleegd)?'

        # Regex for vrijspraak (acquittal)
        # We are more liberal here; do not let period block match, e.g. in ``wijst het verzoek tot wraking van mr. H.H. Dethmers af.''
        # Instead, just look within a certain window but use a tempered greedy scope.
        # Do not match `ne bis in idem` constructions like: 'spreekt verdachte vrij van wat meer of anders is ten laste gelegd'.
        self.pattern_vrijspraak = r'(?i)((?P<nebisinidem1>meer of anders (?:ten laste is gelegd|is ten laste gelegd|is tenlastegelegd|tenlastegelegd is)).{0,50})?(?P<vrijspraak>vrijgesproken|vrijspraak|spreekt[^.\r\n;]*\svrij|wijst[^\r\n;]{0,100}\saf)(?:(?!meer of anders).){0,50}(?P<nebisinidem2>meer of anders (?:ten laste is gelegd|is ten laste gelegd|is tenlastegelegd|tenlastegelegd is))?'

        # Pre-compile the regular expressions because they will be applied frequently
        self.regex_hoofdstraf = re.compile(self.pattern)
        self.regex_TBS = re.compile(self.pattern_tbs)
        self.regex_vrijspraak = re.compile(self.pattern_vrijspraak)


if __name__ == '__main__':
    # https://regex101.com/r/6fbiBD/12
    # NOTE I use this for regex development
    # 1. Develop pattern in an online regex tester
    # 2. Paste full pattern here
    # 3. Diff with the compiled version of the pattern to make sure both versions are up to date
    PATTERN_FULL = r'(?i)(?:(?P<modifier1>voorwaardelijk|proeftijd|niet|vervangend|indien|mindering|maatregel)[^\n\r;.]{0,100})?\b(?P<straf>gevangenis|gevangenisstraf|jeugddetentie|detentie|hechtenis|taakstraf|werkstraf|leerstraf|geldboete|vordering(?!\stenuitvoerlegging)(?!\stot\stenuitvoerlegging)|betaling)\b(?P<test1>[^\n\r;.]{0,85}?)(?P<nummer1>(?<!feit )\d+(?!\s?\]))(?P<test2>[^0-9\n\r;.]{0,30}?)(?P<eenheid1>jaar|jaren|maanden|maand|week|weken|dag|dagen|uur|uren|euro|,[-\d=]{1,2}|(?:\/|-|:)?[\d.]+(?!\s?\])(?:,[-\d=]{1,2})?)(?P<niettest1>[^0-9\n\r;.]{0,15})(?:(?P<nummer2>(?<!feit )\d+(?!\s?\]))[^0-9\n\r;.]{0,30}?(?:\s(?P<eenheid2>jaar|jaren|maanden|maand|week|weken|dagen|dag|uur|uren)))?(?:(?P<niettest2>[^\n\r;.]{0,150})(?P<modifier2>voorwaardelijk|proeftijd|niet|vervangend|indien|hechtenis|wederrechtelijk))?'

    pp = PunishmentPattern()

    # Check whether the structured regex is the same to the full regex after formatting
    diff_pattern(pp.pattern, PATTERN_FULL)