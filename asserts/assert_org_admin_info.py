from asserts.assert_login import Login
from suite.util import TEST_ORG_ADMIN_USER


class OrgAdminInfo(Login):
    def __init__(self, test_suite):
        super().__init__(test_suite)

    def name(self):
        return TEST_ORG_ADMIN_USER

    def assert_case(self):
        self.logger.debug('Assert SS UI for org admin info...')
        super().assert_case()
        self.logger.info('Asserted Login redirection successful...')
