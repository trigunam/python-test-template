#!/usr/bin/env python

import logging
import argparse

TEST_LANDING_PAGE = '01. SS_LANDING_PAGE'
TEST_LOGIN_PAGE = '02. SS_LOGIN_PAGE'
TEST_ENV_INFO = '03. SS_ENV_INFO'
TEST_ORG_ADMIN_USER = '04. SS_ORG_ADMIN_USER'


def setup_logger(log_object, level):
    """
    Setup logger with a level for the logger.
    :param log_object:
    :param level:
    :return:
    """
    log_object.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log_object.addHandler(ch)


def save_screenshot(driver, result, filename):
    driver.save_screenshot(''.join([result, '/', filename, '.png']))


def print_separator(separator, size=50):
    return ''.join([separator for x in range(size)])


def parse_args():
    """Function to define and parse arguments.

    Returns:
        options: parsed options set in cli.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-c',
                        '--config',
                        dest='config',
                        required=True,
                        action='store',
                        help='Path to file containing configurations for '
                             'deployment in YML format.\n'
                             'For Example: configurations/custom/deployment_config.yml')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    logger = logging.getLogger('util')
    setup_logger(logger, 'DEBUG')
    logger.info('This message is for information')
    logger.debug('This message is for debugging')
