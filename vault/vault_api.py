#! /usr/bin/python
"""
Helper to create/read vault information.
"""
import base64
import json
import logging
import subprocess
import sys
import hvac
from jinja2 import Environment, FileSystemLoader
import os
from subprocess import Popen, PIPE

LOGGER = logging.getLogger('deploy')


def write_app_config(cf_user, cf_pass, deploy_config, config_data):
    """Writes data required for setting up vault service for app deployment.
    :param cf_user: CF user id
    :param cf_pass: CF password
    :param deploy_config: YML data containing deployment destination config
                          format example: configurations/custom/deployment_config.yml
    :param config_data: YML data containing secrets.
                        Format example: configurations/custom/vault_input_to_config.yml
    """
    client, vault_info = get_hvac_client(cf_user, cf_pass, deploy_config)
    space_secret_path = vault_info["space_secret_path"]
    write_iam_app_config(client, space_secret_path,
                         deploy_config['vault']['group'], config_data)
    client.close()


def write_deployment_input(cf_user, cf_pass, deploy_config, file_path):
    """Writes config data(secrets) from file to vault as pre-deployment set up.
    :param cf_user: CF user id
    :param cf_pass: CF password
    :param deploy_config: YML data containing deployment destination config
                          format example: configurations/deployment_config.yml
                          data is written under 'vault:deploy_config'
    :param file_path: Path to secrets file. Example: configurations/vault_input_to_config_manifest_template.yml.j2
    """
    client, vault_info = get_hvac_client(cf_user, cf_pass, deploy_config)
    # Include vault_group for the path.
    write_file_to_vault(client, vault_info["service_secret_path"], deploy_config, file_path)
    client.adapter.close()


def read_deployment_input(cf_user, cf_pass, deploy_config):
    """Reads config data(secrets) from vault and returns as text
    :param cf_user: CF user id
    :param cf_pass: CF password
    :param deploy_config: YML data containing deployment destination config
                          format example: configurations/deployment_config.yml
                          data stored under 'vault:deploy_config' is read.
    :return: secret data in string format
    """
    client, vault_info = get_hvac_client(cf_user, cf_pass, deploy_config)
    data = read_file_from_vault(client, vault_info["service_secret_path"],
                                deploy_config['vault']['config_data_path'])
    client.close()
    if data:
        return base64.b64decode(data['data']['file'])


def get_hvac_client(cf_user, cf_passwd, deploy_config):
    """ Get hvac client and path details such as space_secret_path

    :param cf_user:
    :param cf_passwd:
    :param deploy_config:
    :return: hvac based client, vault credentials/path
    """
    cf_host = deploy_config['host']
    credentials = get_vault_credentials(cf_host, cf_user, cf_passwd, deploy_config)
    role_id = credentials["role_id"]
    secret_id = credentials["secret_id"]
    vproxy_endpoint = credentials["endpoint"]
    client = hvac.Client(vproxy_endpoint)
    token_output = client.auth_approle(role_id=role_id, secret_id=secret_id)
    client.token = token_output['auth']['client_token']

    return client, credentials


def cf_cli_login(api, host, space, org, username, password):
    """ Attempts CF login with given user name and password.
        WARNING: DO NOT CALL THIS WITH INVALID CREDENTIALS
    """
    command = ["cf", "login", "-a", api,
               "-u", username,
               "-p", password,
               "-o", org,
               "-s", space]
    p = Popen(command, shell=False, stdout=PIPE).communicate()[0]
    return username, password


def get_vault_credentials(cf_host, cf_user, cf_passwd, deploy_config):
    """ Get vault credentials by querying service key on CF

    :param cf_host: CF API host
    :param cf_user: CF user id
    :param cf_passwd: CF password
    :param deploy_config: YML data containing deployment destination config
                          format example: configurations/deployment_config.yml
                          data stored under 'vault:deploy_config' is read.
    :return: vault credentials
    """
    api_host = 'api.{}'.format(cf_host)
    login_host = 'login.{}'.format(cf_host)
    org = deploy_config['org_name']
    space = deploy_config['space_name']

    vault_service_name = deploy_config['vault']['service']
    broker = deploy_config['vault']['broker_name']
    plan = deploy_config['vault']['plan']

    cf_cli_login(api_host, login_host, space, org, cf_user, cf_passwd)
    create_service = ["cf", "create-service", broker, plan, vault_service_name]
    output = subprocess.Popen(create_service, shell=False,
                              stdout=subprocess.PIPE).communicate()[0]
    exit_if_error(output)

    vault_service_key = '{}-service-key'.format(vault_service_name)
    create_service_key = ["cf", "create-service-key", vault_service_name, vault_service_key]
    output = subprocess.Popen(create_service_key, shell=False,
                              stdout=subprocess.PIPE).communicate()[0]
    exit_if_error(output)

    service_key = ["cf", "service-key", vault_service_name, vault_service_key]
    key_out = subprocess.Popen(service_key, shell=False, stdout=subprocess.PIPE).communicate()[0]

    credentials = json.loads("{" + (key_out.decode("utf-8")).split("{")[-1])
    return credentials


def exit_if_error(output):
    """Check if output contains string OK if not,exit"""
    if b'OK' not in output:
        LOGGER.error('Error:%s', output)
        sys.exit(1)


def read_file_from_vault(client, secret_path, group):
    """ Read data from vault
    :param client:
    :param secret_path:
    :param group:
    :return:
    """
    data = client.read("{}/{}".format(secret_path.strip('/v1/'), group))
    return data


def write_iam_app_config(client, vault_path, group, env_input_config_yml):
    """ Write application configuration secrets to vault
    :param client: hvac client
    :param vault_path: path to write to
    :param env_input_config_yml: YML data with secrets
    :return:
    """
    vault_iam = '{0}/{1}'.format(vault_path.strip('/v1/'), 'iam')
    write_iam_credentials(client, vault_iam, env_input_config_yml)

    if group:
        subgroups = group.split(" ")
        for subgroup in subgroups:
            subgroup_path = '{0}/{1}'.format(vault_iam, subgroup)
            if subgroup == 'sign_certs':
                client.write(subgroup_path,
                             algorithm=env_input_config_yml['sign_certs']['algorithm'],
                             expiry=env_input_config_yml['sign_certs']['expiry'],
                             private_key=env_input_config_yml['sign_certs']['private_key'])
            else:
                write_iam_credentials(client, subgroup_path, env_input_config_yml)


def write_iam_credentials(client, path, env_input_config_yml):
    """ Write credentials data to given vault path """
    data = client.read(path)

    if data is None:
        client.write(path,
                     openam_host=env_input_config_yml['openam_host'],
                     openam_username=env_input_config_yml['openam_username'],
                     openam_userpass=env_input_config_yml['openam_userpass'],
                     oauth_clientid=env_input_config_yml['oauth_clientid'],
                     oauth_clientpass=env_input_config_yml['oauth_clientpass'],
                     openidm_host=env_input_config_yml['openidm_host'],
                     openidm_username=env_input_config_yml['openidm_username'],
                     openidm_userpass=env_input_config_yml['openidm_userpass'],
                     api_secret_key=env_input_config_yml['api_secret_key'],
                     api_shared_key=env_input_config_yml['api_shared_key'],
                     encryption_key=env_input_config_yml['encryption_key'],
                     notification_host=env_input_config_yml['notification_host'],
                     am_service_account_id=env_input_config_yml.get('am_service_account_id'),
                     am_service_account_secret=env_input_config_yml.get('am_service_account_secret'),
                     am_publisher_id=env_input_config_yml.get('am_publisher_id'))
    else:
        response_data = data.get('data')
        notification_service_id = response_data.get('am_service_account_id')

        if notification_service_id is None:

            client.write(path,
                         openam_host=env_input_config_yml['openam_host'],
                         openam_username=env_input_config_yml['openam_username'],
                         openam_userpass=env_input_config_yml['openam_userpass'],
                         oauth_clientid=env_input_config_yml['oauth_clientid'],
                         oauth_clientpass=env_input_config_yml['oauth_clientpass'],
                         openidm_host=env_input_config_yml['openidm_host'],
                         openidm_username=env_input_config_yml['openidm_username'],
                         openidm_userpass=env_input_config_yml['openidm_userpass'],
                         api_secret_key=env_input_config_yml['api_secret_key'],
                         api_shared_key=env_input_config_yml['api_shared_key'],
                         encryption_key=env_input_config_yml['encryption_key'],
                         notification_host=env_input_config_yml['notification_host'],
                         am_service_account_id=env_input_config_yml.get('am_service_account_id'),
                         am_service_account_secret=env_input_config_yml.get('am_service_account_secret'),
                         am_publisher_id=env_input_config_yml.get('am_publisher_id'))

        else:
            client.write(path,
                         openam_host=env_input_config_yml['openam_host'],
                         openam_username=env_input_config_yml['openam_username'],
                         openam_userpass=env_input_config_yml['openam_userpass'],
                         oauth_clientid=env_input_config_yml['oauth_clientid'],
                         oauth_clientpass=env_input_config_yml['oauth_clientpass'],
                         openidm_host=env_input_config_yml['openidm_host'],
                         openidm_username=env_input_config_yml['openidm_username'],
                         openidm_userpass=env_input_config_yml['openidm_userpass'],
                         api_secret_key=env_input_config_yml['api_secret_key'],
                         api_shared_key=env_input_config_yml['api_shared_key'],
                         encryption_key=env_input_config_yml['encryption_key'],
                         notification_host=env_input_config_yml['notification_host'],
                         am_service_account_id=response_data.get('am_service_account_id'),
                         am_service_account_secret=response_data.get('am_service_account_secret'),
                         am_publisher_id=response_data.get('am_publisher_id'))

    LOGGER.info('Vault path[%s] updated with credentials.', path)


def write_file_to_vault(client, vault_path, deploy_config, file_path):
    """ Writes file content in b64 format to vault

    :param client: hvac client
    :param vault_path: vault secret path
    :param vault_group: Where configs will be stored for future. Example
                        deployment_config.yml : vault:deployment_config
    :param file_path: Path to secrets file. Example: configurations/vault_input_to_config_manifest_template.yml.j2
    :return:
    """
    head, jinja_template_file_name = os.path.split(file_path)
    j2 = Environment(loader=FileSystemLoader(head), trim_blocks=True)
    template = j2.get_template(jinja_template_file_name)
    beautifull_content = str(template.render(**deploy_config))
    file_content = base64.b64encode(beautifull_content.encode('utf-8'))

    vault_group_path = '/'.join([deploy_config['vault']['group'], deploy_config['vault']['config_data_path']])
    path = '{0}/{1}'.format(vault_path.strip('/v1/'), vault_group_path)

    client.write(path, file=file_content.decode('utf-8'))


def is_post_deployment_required(cf_user, cf_pass, deploy_config, config_data):
    return read_app_config(cf_user, cf_pass, deploy_config)


def read_app_config(cf_user, cf_pass, deploy_config, secret_path='service_secret_path'):
    client, vault_info = get_hvac_client(cf_user, cf_pass, deploy_config)
    service_secret_path = vault_info[secret_path]
    vault = deploy_config.get('vault')
    group = vault.get('group')
    config_data_path = vault.get('config_data_path')

    vault_path = '/'.join([service_secret_path.strip('/v1/'), group, config_data_path])

    data = client.read(vault_path)
    decoded_data = None
    if data is not None:
        response_data = data.get('data').get('file')
        decoded_data = base64.b64decode(response_data)

    client.adapter.close()

    return decoded_data


def read_iam_app_config(client, vault_path):
    data = client.read(vault_path)
    response_data = data.get('data')
    notification_service_id = response_data.get('am_service_account_id')
    publisher_id = response_data.get('am_publisher_id')

    LOGGER.info('Service id found is [%s]', notification_service_id)
    LOGGER.info('Publisher id found is [%s]', publisher_id)

    return notification_service_id, publisher_id
