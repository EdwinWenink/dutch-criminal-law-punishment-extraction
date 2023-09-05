"""
This script writes out a set of randomly selected cases for in-depth manual evaluation.
"""

import sys
import random
import pandas as pd

from src.extract_punishments import label_hoofdstraf
from src.punishment_pattern import PunishmentPattern
from src.utils import get_logger

log = get_logger(__name__)


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
        old_val_cases = beslissingen.loc[old_val_ECLIs, 'data']
        old_val_ECLIs = list(old_val_cases.index)

    if n_samples > 0:
        log.info("Randomly sampling %s cases.", n_samples)
        random.seed(seed)
        idx = random.sample(range(len(beslissingen)), k=n_samples)
        cases = beslissingen.iloc[idx]['data']
        ECLIs = list(beslissingen.index[idx])

        if old_val_ECLIs:
            # Assert there's no overlap before merging
            intersection = set(old_val_ECLIs) & set(ECLIs)
            assert len(intersection) == 0, intersection

        log.info("Randomly selected cases for validation: %s %s", ECLIs, len(ECLIs))

    # Merge if applicable
    if old_val_ECLIs and ECLIs:
        log.info("Merging randomly selected cases with manually provided cases.")
        cases = pd.concat([old_val_cases, cases], axis=0)
        ECLIs = old_val_ECLIs + ECLIs
    elif old_val_ECLIs:
        log.info("Using manually provided cases only.")
        ECLIs = old_val_ECLIs
        cases = old_val_cases

    if not ECLIs:
        log.error("You have not selected any cases for manual evaluation. Terminating.")
        return

    log.info("All selected cases for validation:", set(ECLIs), len(set(ECLIs)))
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
