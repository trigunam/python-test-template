from suite.test_case import TestCase
from suite.util import TEST_LOGIN_PAGE


class Login(TestCase):
    def __init__(self, test_suite):
        super().__init__(test_suite)

    def assert_case(self):
        self.web_driver.save_screenshot('prelogin')
        self.web_driver.find_element_by_xpath(
            '//*[contains(text(),"Login")]').click()

        self.wait_timeout(self.config['page_load_timeout'])
        self.logger.debug('Waiting for Login page is completed.')
        self.web_driver.save_screenshot('login')

        self.logger.debug(
            'Asserted SS UI login button clicked...')

        # For smoke test user, logout, so that org admin can login.
        a_smoke_test_user = self.name() == TEST_LOGIN_PAGE
        user = self.config['username'] if a_smoke_test_user else self.config['smoke_test_user']
        password = self.config['password'] if a_smoke_test_user else self.config['smoke_test_pwd']

        self.logger.info(
            'Showing Login page. Enter credentials in Login Page.')
        self.web_driver.send_keys('//*[@id="idToken1"]', user)
        self.web_driver.send_keys('//*[@id="idToken2"]', password)
        self.logger.debug(
            'Credentials are entered in Login Page for username...%s', user)
        self.web_driver.save_screenshot('login_filled')

        self.logger.debug('Assert Login page, login button click...')
        self.web_driver.find_element_by_xpath(
            '//*[@id="loginButton_0"]').click()

        self.logger.debug('Asserted Login page, login button clicked...')
        self.web_driver.save_screenshot('login_clicked')

        self.logger.debug('Assert Login redirection...')
        self.wait_timeout(self.config['redirect_load_timeout'])

        # Check for consent page
        # If consent exists then save it and proceed.
        # If consent doesnt exists then proceed
        try:
            self.web_driver.find_element_by_xpath(
                '//*[@id="saveConsent"]').click()
            self.web_driver.find_element_by_xpath(
                '//button[@value="allow"]').click()
        except Exception as error:
            print('Ignore as Save consent is not found and proceed....', error)

        self.logger.debug(
            'Waiting for Login successful redirection is completed.')
        self.web_driver.save_screenshot('redirected_ss_home')
