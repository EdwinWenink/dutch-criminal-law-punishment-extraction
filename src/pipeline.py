from src.caseloader import CaseLoader
from src.dataloader import DataLoader
from src.caseclassifier import CaseClassifier
from src.feature_extraction import Features
from src.caseparser import CaseParser
from src.utils.utils import get_logger, construct_ECLI_query
import src.utils.evaluation as eval
from downstream_task.new.downstream.embedders import SectionEmbedder
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import random
import glob
import os
import csv

# from hydra.utils import get_original_cwd

def pipeline(config: DictConfig, **kwargs) -> None:
    '''
    This pipeline reads all relevant parameters from configurations files
    and sets up the pipeline from data loading to prediction
    '''

    # Initialize logging
    log = get_logger(__name__)

    # Data directory
    data_dir = config.data_dir

    # Make the data folder if it does not exist yet
    os.makedirs(data_dir, exist_ok=True)

    # Construct ECLI-index query from parameters
    # query = construct_ECLI_query(config.query)

    # Case loader (not used currently)
    # TODO flag whether you want to query or load data from disk
    # caseloader = CaseLoader(data_dir)

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
