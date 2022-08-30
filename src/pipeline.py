from src.caseloader import CaseLoader
from src.dataloader import DataLoader
from src.caseparser import CaseParser
from src.utils import get_logger, construct_ECLI_query
from src.extract_punishments import extract_all_punishment_vectors
from omegaconf import DictConfig
from pathlib import Path
import os


def pipeline(config: DictConfig, **kwargs) -> None:
    '''
    This pipeline reads all relevant parameters from configurations files
    and passes them to the appropriate classes
    '''

    # Initialize logging
    log = get_logger(__name__)

    # Data directory
    data_dir = config.data_dir

    # Make the data folder if it does not exist yet
    os.makedirs(data_dir, exist_ok=True)

    # Construct ECLI-index query from parameters
    query = construct_ECLI_query(config.query)
    log.info(f"Query: {query}")

    # Where to store the cases
    query_dir = Path(data_dir) / 'query'

    # Initialize classes for retrieving cases from rechtspraak.nl
    caseloader = CaseLoader(query_dir)

    if not config.skip_query:
        # Submit query that returns an atom feed with results
        # `retrieve_all` flag recurses the request if there are more than `max` results
        caseloader.query_ECLI_index(query, retrieve_all=True)

        # Request the returned cases from the atom feed
        # For convenience this function also returns the path where the cases are stored
        case_dir = caseloader.request_cases_from_feed(check_section_labels=True)
    else:
        case_dir = query_dir / 'cases'

    if not config.caseparser.skip:
        # Config for parsing the xml of the downloaded cases
        level = config.caseparser.level
        include_section_titles = config.caseparser.include_section_titles
        # ['Hoger beroep', 'Cassatie', 'Cassatie in het belang der wet', 'Raadkamer',
        # 'Artikel 81 RO-zaken', 'Wraking', 'Beschikking']
        exclude_procedures = config.caseparser.exclude_procedures
        data_to_key = config.caseparser.data_key

        # Initialize the xml parser
        parser = CaseParser(data_key=data_to_key,
                            level=level,
                            include_section_titles=include_section_titles,
                            exclude_procedures=exclude_procedures)

        # Parse all the returned cases
        df = parser.parse_all_cases(case_dir, write_case_text=False)

        # Inspect unlabeled sections ('other' / 'overig')
        # parser.inspect_overig_labels(df)  # NOTE Do this with level='section'!

        # Write to csv
        with open(query_dir / 'parsed_data.csv', encoding='utf-8', mode='w') as f:
            df.to_csv(f)


    # For each case decision extract all punishment and their heights as a vector
    # and write them to the csv

    # TODO make strafmaat_label part of the PARSING pipeline

    # Read data loader parameters from config
    # cased_data = config.dataloader.cased_data  # whether to read in cased input file
    reduce_to_sentences = config.dataloader.reduce_to_sentences  # Do we explode paragraph data to sentence level?
    binary_label = config.dataloader.binary_label  # Whether to convert class labels into a 2-class problem
    drop_columns = config.dataloader.drop_columns  # whether to drop 'overig' class
    drop_types = config.dataloader.drop_types  # type labels to drop
    target = config.dataloader.target  # Target class
    data_key = config.dataloader.data_key  # Key of the column containing data
    data_fn = config.dataloader.data_fn  # Name of the csv or json containing the data
    min_samples_per_class = config.dataloader.min_samples_per_class  # If None, no rows are dropped

    # Initialize data loader
    dataloader = DataLoader(data_dir=query_dir,
                            data_key=data_key,
                            target=target,
                            data_fn=data_fn,
                            reduce_to_sentences=reduce_to_sentences,
                            min_samples_per_class=min_samples_per_class)

    # Load data
    df = dataloader.load(drop_columns=drop_columns,
                         drop_types=drop_types,
                         reduce_to_sentences=reduce_to_sentences,
                         binary_label=binary_label)  # loads data_fn by default

    log.info(df.columns)

    # Extract punishment vectors
    # TODO maybe option to skip?
    df = extract_all_punishment_vectors(df)
    df.to_csv(dataloader.data_path)
