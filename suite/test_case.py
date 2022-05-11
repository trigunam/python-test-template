
import time
import logging
from datetime import datetime

from suite.test_suite import TestSuite
from suite.util import setup_logger


class TestCase(TestSuite):
    def __init__(self, test_suite):
        """
        Initialize test case
        """
        super().__init__()
        self.web_driver = test_suite.web_driver
        self.config = test_suite.config
        self.test_passed = test_suite.test_passed
        self.test_failed = test_suite.test_failed
        self.test_results = test_suite.test_results
        self.execution_time = test_suite.execution_time
        self.response_time = test_suite.response_time
        self.logger = logging.getLogger(self.name())
        setup_logger(self.logger, self.log_level)

    def initialize(self, url, deploy_config, log_level):
        super().initialize(url, deploy_config, log_level)

    def execute(self):
        start_time = datetime.utcnow()
        try:
            self.assert_case()
            self.test_results.append('PASSED')
            self.test_passed.append('PASSED')
            self.test_failed.pop()
        except AssertionError as err:
            self.logger.error('{}'.format(err))
            self.test_results.append('FAILED')

        end_time = datetime.utcnow()
        self.execution_time.append(str(end_time))
        self.response_time.append(str(end_time - start_time))

    def assert_case(self):
        """Individual test cases will have asserts
        :return:
        """
        pass

    def logout(self, user):
        self.logger.info('logging out... %s', user)
        self.web_driver.save_screenshot('logging_out')
        self.web_driver.find_element_by_xpath(
            '//*[@id="logout"]').click()
        self.web_driver.save_screenshot('drop_down_user')
        self.web_driver.find_element_by_xpath(
            '//*[@id="logout_option"]').click()
        self.web_driver.save_screenshot('successful_logout')

    def wait_timeout(self, timeout):
        while timeout >= 0:
            time.sleep(1)
            self.logger.debug('Waiting for %d secs for page response', timeout)
            timeout -= 1

    def name(self):
        """
        Name is implemented in respective test case classes
        :return:
        """
        return 'SS_DEFAULT_PAGE'
