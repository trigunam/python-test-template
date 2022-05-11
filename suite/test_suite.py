import logging
from datetime import datetime

from suite.util import setup_logger, print_separator
from suite.drivers import Driver
from config import test_cases

logger = logging.getLogger('test_suite')


class TestSuite:
    def __init__(self):
        """
        Initialize test suite.
        """
        self.test_results = []
        self.execution_time = []
        self.response_time = []
        self.test_passed = []
        self.test_failed = test_cases()

        self.config = None
        self.iamss_url = None

        self.web_driver = None

        self.logger = logger
        self.log_level = 'DEBUG'

        self.all_tests = []

    def initialize(self, url, deploy_config, log_level):
        setup_logger(logger, log_level)

        self.logger = logger
        self.log_level = log_level

        self.config = deploy_config
        self.iamss_url = url

        self.web_driver = Driver(self.config['smoke_test_driver'],
                                 self.config['page_load_timeout'],
                                 self.config['smoke_test_result'],
                                 self.log_level)

        retry = self.web_driver.get(self.iamss_url, deploy_config['smoke_test_retry'])

        if retry <= 0:
            self.print_final_execution_summary()

        return self

    def add_test_case(self, test_case):
        self.all_tests.append(test_case)

    def execute_all(self):
        for test in self.all_tests:
            test.execute()

    def print_final_execution_summary(self):
        execution_summary = self.print_execution_summary()

        total_test_cases = len(test_cases())
        total_test_passed = len(self.test_passed)
        total_test_failed = len(self.test_failed)
        total_test_not_executed = total_test_cases - (total_test_passed + total_test_failed)

        end_time = datetime.utcnow()
        self.logger.info('\n'.join([execution_summary, '', '',
                                    'APPLICATION: {}'.format(self.config['applications']['iam_self_service_name']),
                                    'RELEASE: {}'.format(self.config['version']),
                                    'ENVIRONMENT: {}'.format(self.config['environment']),
                                    'REGION: {}'.format(self.config['domain']), '', '',
                                    'QUICK SUMMARY',
                                    'EXECUTION TIMESTAMP: {}'.format(str(end_time)),
                                    print_separator('-'),
                                    'TOTAL TEST CASES: {}'.format(total_test_cases),
                                    'TOTAL TEST CASES EXECUTED: {}'.format(len(self.execution_time)),
                                    'TOTAL TEST CASES PASSED: {}'.format(total_test_passed),
                                    'TOTAL TEST CASES FAILED: {}'.format(total_test_failed),
                                    'TOTAL TEST CASES NOT EXECUTED: {}'.format(total_test_not_executed)]))
        self.web_driver.quit()

    def print_execution_summary(self):
        exec_summary_head = ' '.join([print_separator('#'), 'EXECUTION SUMMARY', print_separator('#')])
        header = '\t\t'.join(['TEST CASE NAME', 'STATUS', 'EXECUTION TIME', 'RESPONSE TIME', 'END POINT'])

        summary = []
        for test_case, result, exec_time, resp_time in zip(test_cases(), self.test_results, self.execution_time,
                                                           self.response_time):
            summary.append(' '.join([test_case, result, exec_time, resp_time, self.iamss_url]))
            summary.append('\n')

        return '\n'.join(['', exec_summary_head, header, print_separator('='), ''.join(summary), print_separator('=')])
