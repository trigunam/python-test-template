from suite.test_case import TestCase
from suite.util import TEST_LANDING_PAGE


class LandingPage(TestCase):
    def __init__(self, test_suite):
        super().__init__(test_suite)

    def name(self):
        return TEST_LANDING_PAGE

    def assert_case(self):
        self.logger.debug(
            'Assert SS UI landing page with the title "Self-Service User Interface".'
        )
        assert "Self-Service User Interface" in self.web_driver.title()
        self.logger.debug(
            'Asserted SS UI landing page with the title "Self-Service User Interface".'
        )

        self.logger.info("Navigation to landing page is successful.")
