from asserts.assert_login import Login
from suite.util import TEST_LOGIN_PAGE


class LoginPage(Login):
    def __init__(self, test_suite):
        super().__init__(test_suite)

    def name(self):
        return TEST_LOGIN_PAGE

    def assert_case(self):
        self.logger.debug('Assert SS UI login button click...')
        super().assert_case()
        self.logger.info('Asserted Login redirection successful...')
