from pathlib import Path
import random

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from nltk.tokenize import sent_tokenize

from src.utils import get_logger, construct_mask

log = get_logger(__name__)


class DataLoader:
    '''
    This class contains functions for loading in data files
    and also contains some functions for basic preprocessing
    and data exploration

    get_Xy() is the main API to get a training data set and target labels
    '''

    # TODO provide a generator function to retrieve data lazily

    def __init__(self, data_dir='./data/new/',
                 data_fn='section_data_2021.csv',
                 data_key='data',
                 document_key='ECLI',
                 section_key='section_id',
                 target='type',
                 reduce_to_sentences=False,
                 min_samples_per_class=None):
        super().__init__()
        self.data_dir = Path(data_dir)
        self.data_fn = data_fn
        self.reduce_to_sentences = reduce_to_sentences
        self.data_key = data_key
        self.document_key = document_key
        self.section_key = section_key
        self.min_samples_per_class = min_samples_per_class
        self.target = target

    @property
    def data_path(self):
        return self.data_dir / self.data_fn

    def set_target(self, target):
        self.target = target

    def load(self, fn=None, drop_columns=None, drop_types=None, binary_label=None, **kwargs):
        '''
        Load csv or json data at self.data_dir / self.data_fn.
        Whether to load csv or json is determined based on the file extension.
        self.data_fn can be overridden by providing the `fn` parameter

        Some info on data used in this project

        OpenDataUitspraken from TNO
        ---------------------------

        TODO

        Paragraph data:
        ---------------

        Unnamed: 0          onduidelijk; dit lijkt een index die met 850 ipv 0 begint; maar ook af en toe een nummer overslaat
        case_id             ECLI case identifier
        wetboek_reference   referentie naar wetboek artikelen (TODO: één of meerdere?)
        data                text van de betreffende paragraaf
        paragraph_id        numeriek id; betekenis onduidelijk; loopt niet op van 1 .. max
        type                label van { 'oordeel', 'standpunt', 'overweging', 'tussenkop', 'NaN' } -> alle NaN naar filteren map ik op 'overig'
        ml_type             type zoals voorspeld door een ongenoemde ML algoritme
        ml_confidence       confidence in ML classificatie
        topic               topic label; precieze betekenis lijkt per type te verschillen
        id                  row id


        Data from CaseLoader and CaseParser:
        ------------------------------------

        id                  simple incremental integer id
        section_id          position of section in the whole case text
        ECLI                ECLI case identifier
        title               Title of section
        type                Role of section in case text (e.g. "aanklacht" or "beslissing")
        data                Section text
        articles            Articles referred to in section (currently for type "wettelijke voorschriften")
        subject             Domain of law
        procedure           Type of case, e.g. "Hoger beroep" or "Wraking"

        Raises
        ------
        KeyError:
            Raised when self.document_key is not a column name in the data source

        '''
        if fn is not None:
            data_fn = fn
            filepath = self.data_dir / data_fn
            log.info("Overwriting default data file")
        else:
            filepath = self.data_path

        log.info("Loading data from %s:", filepath)
        if not filepath.is_file():
            log.error("Data not found at %s. Provide a valid filepath.", filepath)
            raise FileNotFoundError

        if filepath.suffix == '.csv':
            df = pd.read_csv(filepath, sep=",", header="infer", encoding='utf-8')
        elif filepath.suffix == '.json':
            df = pd.read_json(filepath)
        else:
            log.warning("No data loaded: data must be either csv or json")
            return pd.DataFrame()

        if drop_columns:
            for col in drop_columns:
                try:
                    df = df.drop(columns=col)
                    log.info("Column %s dropped.", col)
                except Exception:
                    log.warning("Tried to drop column %s, but it was not in the dataframe.", col)

        if drop_types:
            for type in drop_types:
                df = df[df['type'] != type]
                log.info("Dropping type '%s'", type)

        # Convert to a binary problem by taking a single value of the target variable
        # and then defining all other values as "other"
        # NOTE Places after drop_types, but before checking min samples per class
        if binary_label:
            log.info("Creating binary type labels")
            df.loc[df[self.target] != binary_label, 'type'] = 'other'

        if self.min_samples_per_class:
            df = self.drop_sparse_labels(df, target=self.target)

        if self.reduce_to_sentences:
            df = self.split_into_sentences(df)

        if self.document_key not in df.keys():
            raise KeyError(f"The document key {self.document_key} is not present in the dataframe columns")

        # Set the document identifier as the dataframe key
        df.set_index(self.document_key, inplace=True)

        log.info("Selected columns: %s", list(df.columns))
        log.info("Selected section types: %s", np.unique(df['type'].values))
        return df

    def create_typed_paragraph_dataset(self, df, fn='paragraph_data_types.csv'):
        '''
        Takes a subset of the paragraph data
        1. either paragraphs with a 'type' entry
        2. or paragraphs with NAs that *do* belong to an annotated case
            - These NAs will be labeled as 'overig'
        '''

        # Drop type 'tussenkop'
        df = df[df['type'] != 'tussenkop']

        # Get a new dataframe with only labelled paragraphs
        df_types = df[~df['type'].isna()]
        log.info(f"Paragraphs with type annotations: {len(df_types)}")

        # Voor een dataset willen we evenveel paragrafen met een "other" class, d.w.z. de negatieve class
        # anders is dit model niet bruikbaar op rauwe teksten
        # We kunnen er niet vanuitgaan dat afwezigheid van een label "other" betekent
        # We moeten dus denk ik kijken naar de artikelen die wél gelabelde paragrafen hebben
        # En voor elk van die artikelen paragrafen met type NA vinden en die als 'overig' labelen
        # TODO deze redenering is nog niet gevalideerd!
        cases_with_type_labels = df_types['case_id'].unique()
        dataset = df[df['case_id'].isin(cases_with_type_labels)]
        log.info(f"{len(dataset)}")

        # Fill in NA values for type as category 'overig'
        dataset['type'] = dataset['type'].fillna('overig')  # Gives a warning, but I think it's a false positive warning

        log.info(f"Paragraph types on {len(dataset['case_id'].unique())} unique cases")

        # Schrijf nieuwe dataset naar csv
        dataset.to_csv(self.data_dir / fn, index=False)
        return dataset

    def load_typed_paragraph_dataset(self, fn='paragraph_data_types.csv', binary_label=False, drop_overig=False):
        '''
        loads a subset of the paragraph dataset that has type labels
        with the option to aggregrate the labels into a binary category
        '''

        filepath = self.data_dir / fn

        if not filepath.is_file():
            log.info("Creating typed data set")
            df = self.create_typed_paragraph_dataset(self.load(fn), fn)
        else:
            log.info("Loading typed data set from disk %s. Binary labels %s.", filepath, binary_label)
            df = pd.read_csv(filepath, sep=",", header="infer")

        if binary_label:
            log.info("Creating binary type labels")
            df.loc[df['type'] != 'overig', 'type'] = 'argumentative'

        if drop_overig:
            try:
                df = df[df['type'] != 'overig']
            except Exception as e:
                log.info("No 'overig' column present")

        if self.reduce_to_sentences:
            df = self.split_into_sentences(df)

        # TODO train, test split (before sampling)?
        # since my data set is not huge, I should just do a form of stratified cross-validation

        # TODO balanced flag; undersample majority class ONLY on training data
        # Alternative: leave dataset as is but do balanced sampling later

        return df

    def split_into_sentences(self, df):
        '''
        A function that splits text into sentences with preservation of labels
        i.e. each text label is transfered to the individual sentences
        '''
        # Convert text to a list of sentences
        df[self.data_key] = df[self.data_key].apply(lambda x: [sent for sent in sent_tokenize(x)])

        # Explode the list of sentences so each sentence gets its own row
        df = df.explode(self.data_key, ignore_index=True)
        df.rename(columns={"Unnamed: 0": "sentence_id"}, inplace=True)
        return df

    def drop_sparse_labels(self, df, target='type'):
        targets = df[target]
        for label in targets.unique():
            if sum(targets == label) < self.min_samples_per_class:
                log.warning(f"Dropping due to too few samples: {label}")
                df = df[targets != label]
        return df

    def get_Xy(self, df, target=None, data_key=None) -> tuple:
        '''
        Get raw text data X and define a column as the
        classification target y; encode the target labels
        '''

        if data_key is None:
            data_key = self.data_key  # default is 'data'
            log.info("Using default data key %s:", data_key)

        if df is None:
            # Fallback option
            log.warning("No dataframe passed. Loading fallback option.")
            df = self.load()  # loads data_fn by default

        if target is None:
            target = self.target

        log.info("Creating X and y with target %s:", target)

        X = df[data_key].values  # called 'paragraph' in original json, 'data' in processed version
        le = LabelEncoder()

        # If we target labels are strings, convert nan values to str as well (nan by default is of type float)
        target = df[target]
        target_type = type(target[target.notna()][0])
        if target.isna().any():
            log.info("Nan values detected in target labels.")
            if target_type is str:
                log.info("Converting nan values in target labels to string type.")
                target = target.fillna('nan')

        # Encode labels
        y = le.fit_transform(target)

        # Also return the fitted labelencoder so you can use inverse transform
        return X, y, le

    def get_X(self, df, concat_sections=False, **kwargs) -> list:
        '''
        This function only loads raw text data without labels.
        Optionally concatenates sections belonging to the same document into a single document text.
        Optionally provide a section filter in the kwargs, see docstring for `get_text()`
        '''

        # Get unique index values without losing order
        reference_ids = list(dict.fromkeys(df.index))

        X = []
        for id in reference_ids:
            text = self.get_text(df, document_id=id, concat_sections=concat_sections, **kwargs)
            if isinstance(text, str):
                X.append(text)
            if isinstance(text, list):
                X.extend(text)
        return X

    def get_text(self, df, document_id: str, concat_sections: bool = True,
                 concat_term="\n\n", **kwargs) -> list:
        """ Returns the text belonging to a single reference document.

        A reference document with `document_id` contains multiple sections. This function
        returns the text fragments sorted on `self._section_key`. This function also
        allows you to return the document text as a list of section texts when
        `concat_sections` is False.

        Parameters
        ----------
        document_id: str
            The unique identifier used for the document.
        concat_sections: bool (Default True)
            If the reference data consists out of document sections, this boolean determines whether the return value
            is a list of sections/paragraphs/sentences/... or concatenated as a single string (using the `concat_term`).
        concat_term: str (Default "\n\n")
            How the different sections should be concatenated/joined if `concat_sections=True`.
        **kwargs: dict
            If a 'filter' keyword parameter is provided, only use a selection of the sections
            associated with a document for reconstructing a document text. The filter should
            be specified as a dictionary that specifies a column name and a flat list with
            the values to keep, of the form: `filter = {'column_to_filter_on': ['keep_me', 'keep_me_too']}`
            An index mask will be automatically constructed for each document based on the provided information.

        Returns
        -------
        text: str, list
            Returns a document text or a list of document section texts.

        Raises
        ------
        KeyError:
            Raised when the document ID is not found in the reference data.

        """

        if document_id not in df.index:
            raise KeyError(f"The document ID {document_id} is not present in the data index.")

        # Test for presence of section_key
        if (self.section_key is None) or (self.section_key not in df.keys()):
            log.info("Section id is either None or not present in the input data source")
            log.error("This function currently requires a section_key")
            return None

        # We explicitly include the section id to allow sorting of sections
        # df_doc = df.loc[document_id, [self.section_key, self.data_key]]
        df_doc = df.loc[document_id]

        # Option to filter out certain sections when computing
        # an embedding for the whole document
        if 'filter' in kwargs.keys():
            filter = kwargs['filter']
            if len(filter.keys()) > 1:
                log.warning("Only filtering on a single column is supported")
            filter_on_column = list(filter.keys())[0]
            input = np.array(df_doc[filter_on_column])
            values_to_keep = filter[filter_on_column]
            mask = construct_mask(input, values_to_keep)
            df_doc = df_doc.iloc[mask]

        # Sort based on the section index
        df_doc.set_index(self.section_key, inplace=True)
        df_doc.sort_index(inplace=True)

        if concat_sections:
            return concat_term.join(df_doc[self.data_key])  # str
        else:
            return list(df_doc[self.data_key])  # list

    def sample_example_from_type(self, df, type='overig', verbose=True):
        df_type = df[df['type'] == type]
        rows = len(df_type)
        i = random.randint(0, rows-1)
        sample = df_type.iloc[i]
        if verbose:
            log.info("\n%s", sample)
            log.info("\nTEXT:\n%s", sample[self.data_key])
        return sample
