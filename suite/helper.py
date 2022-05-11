#!/usr/bin/env python

import logging

from asserts.assert_env_info import EnvInfo
from asserts.assert_landing_page import LandingPage
from asserts.assert_login_page import LoginPage
from asserts.assert_org_admin_info import OrgAdminInfo
from suite.test_suite import TestSuite

logger = logging.getLogger('execution')


def execute_test_cases(iamss_url, deploy_config, log_level):
    """Execute tests with the following steps:
        1. Start a timer (datetime.utcnow())
        2. Execute a test case
            Open a page
            Assert the content
        3. End the timer
        4. Record Response Time (endTime - startTime)
        5. Record execution time (endTime)
        6. Execution status (pass / fail)
        7. Execution end point

    :param iamss_url:
    :param deploy_config:
    :param log_level:
    :return:
    """

    test_suite = TestSuite().initialize(iamss_url, deploy_config, log_level)
    test_suite.add_test_case(LandingPage(test_suite))
    test_suite.add_test_case(LoginPage(test_suite))
    test_suite.add_test_case(EnvInfo(test_suite))
    test_suite.add_test_case(OrgAdminInfo(test_suite))

    test_suite.execute_all()

    test_suite.print_final_execution_summary()
