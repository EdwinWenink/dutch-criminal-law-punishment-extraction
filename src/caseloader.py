import requests
import os
import regex
import feedparser as fp 
import glob
from pathlib import Path
from argmine.caseparser import CaseParser
from datetime import datetime
from argmine.utils.utils import get_logger, construct_ECLI_query

log = get_logger(__name__)

class CaseLoader:
    '''
    Class for querying the ECLI index of Open Data van de Rechtspraak
    '''

    def __init__(self, out_dir='./data' ):
        '''
        out_dir     optionally specify data subfolder to store query results in
        '''
        super().__init__()

        self.out_dir = Path(out_dir)
        os.makedirs(self.out_dir, exist_ok=True)

        # TODO params to constructor required?
        self.parser = CaseParser()

        # Where the query results will be stored
        self.results = self.out_dir / "results.atom"

        # File where information on the query is stored
        self.query_info = self.out_dir / "query.info"

        # Simple regex for parsing the amount of cases returned by query
        # i.e. not taking into account the provided value for the field 'max'
        self.match_nr = regex.compile(r'\d+')

    def query_ECLI_index(self, query, idx_from=1, retrieve_all = False, already_retrieved=0):
        '''
        This function queries the ECLI index and saves the response to disk
        You can use utils.construct_ECLI_query() for composing the query parameter
        '''
        url = 'http://data.rechtspraak.nl/uitspraken/zoeken?' + query

        # Record information on the query
        if not self.query_info.is_file():
            with open(self.query_info, "w") as f:
                f.write(f"Query: {url}")

        # Modify result feed name with 'from' index
        results = self.out_dir / Path( self.results.stem + f"_from_{idx_from}" + self.results.suffix)

        # If result already exists, do nothing; otherwise query and download the results
        if not results.is_file():
            #log.info("Query:", url)
            print("Query:", url)
            r = requests.get(url, allow_redirects=True)
            print("Retrieving cases starting from index ", idx_from)

            # Parse the returned atom feed to check how many ECLIs match the query
            # and also how many are returned in the feed itself
            d = fp.parse(r.content)
            n_hits = int(self.match_nr.search(d.feed.subtitle).group(0))
            ECLIds = [ entry.id for entry in d.entries ]
            n_retrieved = len(ECLIds)
            already_retrieved += n_retrieved

            with open(results, 'wb') as f:
                f.write(r.content)
            print(f"Query results starting from index {idx_from} saved on disk")
        else:
            print("Query results already present on disk")
            # This case I ALSO need to increment with the amount of ECLIds
            # in the feed that's already on disk. This allows correct querying 
            # if some results are present while others are not.
            d = fp.parse(results)
            ECLIds = [ entry.id for entry in d.entries ]
            n_retrieved = len(ECLIds)
            already_retrieved += n_retrieved
            n_hits = int(self.match_nr.search(d.feed.subtitle).group(0))

        # Progress
        print(f"Retrieved {already_retrieved} cases from total of {n_hits}")

        # If we want to retrieve all cases returned by the query,
        # we need to repeat the query with the 'from' parameter
        if retrieve_all and n_hits > already_retrieved:
            new_idx_from = already_retrieved
            # Repeat the query but now from the first not-returned ECLI
            if 'from' in query:
                new_query = regex.sub(r'from=\d+', f"from={new_idx_from}", query)
            else:
                new_query = query + f'&from={new_idx_from}'

            # Recurse
            self.query_ECLI_index(new_query,
                    idx_from=new_idx_from,
                    retrieve_all=True,
                    already_retrieved=already_retrieved)

    def _request_case(self, ECLI, out_dir=None, check_section_labels=True, verbose=False):
        '''
        ECLI    case identifier string
        '''

        # Make output_dir if it doesn't exist yet
        os.makedirs(out_dir, exist_ok=True)

        if out_dir == None:
            out_dir = self.out_dir

        url = f'https://data.rechtspraak.nl/uitspraken/content?id={ECLI}'
        # Paths cannot contain colons
        ECLI = ECLI.replace(':','-') + '.xml'
        outfile = out_dir / ECLI
        if not outfile.exists():
            # Download content
            if verbose: print("URL: ", url)
            r = requests.get(url, allow_redirects=True)
            if check_section_labels:
                if self.parser.check_section_labels(r.content):
                    with open(outfile, 'wb') as f:
                        f.write(r.content)
                        if verbose: print(f"SAVING {ECLI}") # to {outfile}")
                else:
                    if verbose: print(f"{ECLI} NOT SAVED due to missing section labels")
                    return False
            else:
                with open(outfile, 'wb') as f:
                    f.write(r.content)
                    if verbose: print(f"Saving {ECLI}") # to {outfile}")
        else: 
            if verbose: print("File already exists: ", outfile)

        return True

    def request_cases_from_feed(self, check_section_labels=True):
        '''
        This function requests cases from the returned atom feeds
        from rechtspraak.nl; it saves them to disk if they pass
        a test that checks if they have labelled sections
        '''

        # Result feeds have the format 'results_from_{x}.atom'
        results = list(glob.iglob(str(self.out_dir / 'results_from*atom'), recursive=False))

        if len(results) == 0:
            print("Submit a query first. Results not available.")
            return

        # Where to store the case xmls
        case_dir = self.out_dir / 'cases'

        counter = 0
        all_ECLIds = []
        for result in results:

            # Retrieve a list of ECLI from the result feed stored on disk
            d = fp.parse(result)

            # Retrieve case numbers in the current feed
            ECLIds = [entry.id for entry in d.entries]
            # print("Queried ECLIs: ", len(ECLIds))

            # Keep track of all ECLIds
            all_ECLIds.append(ECLIds)

            # Retrieve each ECLId and store under 'cases'
            for ECLI in ECLIds:
                success = self._request_case(ECLI, case_dir, check_section_labels)
                if success:
                    counter += 1

            print(f"{counter} ECLIs on disk")

        # flatten list
        ECLIds = [ECLI for ECLI_list in all_ECLIds for ECLI in ECLI_list]

        with open(self.out_dir / 'query_ECLIds.txt', 'w') as f:
            f.writelines(f"{ECLI}\n" for ECLI in ECLIds)
            print("All query ECLI written to index")

        # Return the location of the returned cases
        return case_dir

    def request_cases_from_list(self, ECLIds, out_dir=None, check_section_labels=True):
        '''
        This function downloads all ECLIs from an ad-hoc list
        '''
        if out_dir is None:
            out_dir = self.out_dir.parents[0] / datetime.now().strftime("%Y-%H-%M-%S")
        else:
            out_dir = self.out_dir

        os.makedirs(out_dir, exist_ok=True)

        for ECLI in ECLIds:
            self._request_case(ECLI, out_dir, check_section_labels)


if __name__ == '__main__':

    params = {
        'type': 'uitspraak',
        'subject': 'http%3A%2F%2Fpsi.rechtspraak.nl%2Frechtsgebied%23strafrecht',
        # 'date_from': '2020-06-01',
        'date_from': '2021-01-01',
        'date_until': '2022-01-01',
        'max': 1000,
        'return': 'DOC'
    }

    # Construct a query with the parameters from above
    query = construct_ECLI_query(params)
    print("QUERY", query)

    out_dir = Path('./data/new') / 'query_last_year'

    # Initialize classes for retrieving cases from rechtspraak.nl
    caseloader = CaseLoader(out_dir)

    # Submit query that returns an atom feed with results
    # retrieve_all flag recurses the request if there are more than `max` results
    caseloader.query_ECLI_index(query, retrieve_all=True)

    # Request the returned cases from the atom feed
    # For convenience this function also returns the path where the cases are stored
    case_dir = caseloader.request_cases_from_feed(check_section_labels=True)
