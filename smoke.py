#!/usr/bin/env python

"""
Command line script for smoke test deployment
"""

import logging
import time
from sys import exit

from suite.helper import execute_test_cases
from suite.util import setup_logger, parse_args

from auth_client.auth_client_helper import update_client

import os
import yaml
from vault import vault_api as vs

logger = logging.getLogger('smoke')

# ---- Read arguments and execute deployment ------------
start = time.time()
args = parse_args()

with open(args.config) as _f:
    deploy_config = yaml.safe_load(_f.read())

log_level = deploy_config['smoke_test_log_level']
setup_logger(logger, log_level)

username = deploy_config['smoke_test_user']
password = deploy_config['smoke_test_pwd']

admin_user = deploy_config['org_admin_user']
admin_pwd = deploy_config['org_admin_pwd']

# construct iamss_url from config.
domain = deploy_config['domain']
host_name = '-'.join(
    [deploy_config['host_names']['iam_self_service_name'], str(deploy_config['version']).replace('.', '')])
if deploy_config['use_blue_green_as_host']:
    host_name += ''.join(['-', deploy_config['blue_green']])
authorize_url = ''.join(['https://', host_name, '.', domain])
# route_url needs to added to the client
authorize_route_url = ''.join(['https://', deploy_config['route_names']
                               ['iam_self_service_name'], '.', domain])

page_load_timeout = deploy_config['page_load_timeout']
redirect_load_timeout = deploy_config['redirect_load_timeout']

deploy_config['username'] = username
deploy_config['password'] = password

deploy_config['org_admin_usr'] = admin_user
deploy_config['org_admin_pwd'] = admin_pwd

logger.info('Smoke test started for... %s,'
            ' page_load_timeout = %d secs,'
            ' redirect_load_timeout = %d secs, ',
            authorize_url, page_load_timeout, redirect_load_timeout)

# Update client with the redirect uri.
logger.info(
    'Updating client {} with authorize url {}/authorize from host...'.format(deploy_config['client_id'], authorize_url))

if not deploy_config['client_secret']:
    vault_data = vs.read_app_config(
        os.environ['CF_USN'], os.environ['CF_PWD'], deploy_config).decode('ascii')
    config_yaml = yaml.safe_load(vault_data)
    deploy_config['iam_url'] = config_yaml['iam_url']
    deploy_config['idm_url'] = config_yaml['idm_url']
    deploy_config['client_secret'] = config_yaml['client_secret']

update_client(authorize_url, deploy_config)

execute_test_cases(authorize_url, deploy_config, log_level)

# # once the smoke test is done the url can be updated with the route url
update_client(authorize_route_url, deploy_config)

end = time.time()
logger.info("Smoke test completed in : %f s", round(end - start))
exit(0)
