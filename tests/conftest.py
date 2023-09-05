"""
Configuration file for pytest.
"""

import logging

import pytest

from src.extract_punishments import PunishmentPattern


def pytest_runtest_setup(item):
    """Initialize logger per test item."""
    # Get the logger for the current test
    logger = logging.getLogger(item.nodeid)

    # Log a message for the start of the test
    logger.info("Starting test: %s", item.name)


@pytest.fixture(scope='session')
def punishment_pattern() -> PunishmentPattern:
    return PunishmentPattern()