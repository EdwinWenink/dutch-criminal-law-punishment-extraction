from src.caseloader import CaseLoader
# from src.dataloader import DataLoader
from src.caseparser import CaseParser
from src.utils import get_logger, construct_ECLI_query
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
    log.info("Query:", str(query))

    # Where to store the cases
    query_dir = Path(data_dir) / 'query'

    # Initialize classes for retrieving cases from rechtspraak.nl
    caseloader = CaseLoader(query_dir)

    # Submit query that returns an atom feed with results
    # `retrieve_all` flag recurses the request if there are more than `max` results
    caseloader.query_ECLI_index(query, retrieve_all=True)

    # Request the returned cases from the atom feed
    # For convenience this function also returns the path where the cases are stored
    case_dir = caseloader.request_cases_from_feed(check_section_labels=True)

    # TODO WIP

    '''
    # Read data loader parameters from config
    cased_data = config.dataloader.cased_data  # whether to read in cased input file (hardcoded filename)
    reduce_to_sentences = config.dataloader.reduce_to_sentences  # Do we explode paragraph data to sentence level?
    binary_label = config.dataloader.binary_label  # Whether to convert class labels into a 2-class problem
    drop_columns = config.dataloader.drop_columns  # whether to drop 'overig' class
    drop_types = config.dataloader.drop_types  # type labels to drop
    target = config.dataloader.target  # Target class
    data_key = config.dataloader.data_key  # Key of the column containing data
    data_fn = config.dataloader.data_fn  # Name of the csv or json containing the data
    min_samples_per_class = config.dataloader.min_samples_per_class  # If None, no rows are dropped

    data_path = Path(data_dir) / data_fn

    # Initialize data loader
    dataloader = DataLoader(
            data_dir=data_dir,
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
    '''
