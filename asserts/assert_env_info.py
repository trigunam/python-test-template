from suite.test_case import TestCase
from suite.util import TEST_ENV_INFO, TEST_LOGIN_PAGE


class EnvInfo(TestCase):
    def __init__(self, test_suite):
        super().__init__(test_suite)

    def name(self):
        return TEST_ENV_INFO

    def assert_case(self):
        self.web_driver.save_screenshot('ss_home')
        self.logger.info(
            'Assert env_info in Self Service landing page.')
        env_info = str(
            self.web_driver.find_element_by_id('responsive-navbar-nav').text)

        self.logger.debug('Assert env_info... %s', env_info)

        iam_url = self.config['iam_url']
        self.logger.debug('Assert iam_url to be %s', iam_url)
        assert env_info.find(iam_url) > 0
        self.logger.debug('Asserted iam_url to be %s', iam_url)

        domain = self.config['domain']
        self.logger.debug('Assert domain to be %s', domain)
        assert env_info.find(domain) > 0
        self.logger.debug('Asserted domain to be %s', domain)

        environment = self.config['environment']
        self.logger.debug('Assert environment to be %s', environment)
        assert env_info.find(environment) > 0
        self.logger.debug('Asserted environment to be %s', environment)

        release = self.config['release']
        self.logger.debug('Assert release to be %s', release)
        assert env_info.find(release) > 0
        self.logger.debug('Asserted release to be %s', release)

        self.web_driver.save_screenshot('user_logged_in')

        self.logout(self.config['username'] if self.name(
        ) == TEST_LOGIN_PAGE else self.config['smoke_test_user'])
        self.web_driver.save_screenshot('user_logged_out')

        self.logger.info(
            'Asserted env_info in Self Service landing page is successful.')
