from auth_client.authenticate import Authenticate
from auth_client.client import OAuth2Client
from suite.input_validator import InputValidator


def update_client(authorize_url, deploy_config):
    """Updates the OAuth2 Client with the authorize_url/authorize

    :param authorize_url: URL used to update
    :param deploy_config: Deployment configuration to use to update client.

    :return: None
    """
    if InputValidator(deploy_config, ['username', 'password',
                                      'client_id', 'client_secret',
                                      'iam_url', 'idm_url',
                                      'token_api_version', 'client_api_version'
                                      ]):
        username = deploy_config['org_admin_usr']
        password = deploy_config['org_admin_pwd']
        client_id = deploy_config['client_id']
        client_secret = deploy_config['client_secret']

        auth = Authenticate(deploy_config['iam_url'])\
            .add_headers(client_id, client_secret, deploy_config['token_api_version'])\
            .login(username, password)
        if 'access_token' in auth:
            try:
                authorize_url = '{}/authorize'.format(authorize_url)
                client_update_res = OAuth2Client(deploy_config['idm_url'])\
                    .add_headers(deploy_config['client_api_version'], auth['access_token'])\
                    .get_client(client_id).update_client(authorize_url)

                if client_update_res is not None and 'existing' not in client_update_res and 'id' not in client_update_res:
                    err_msg = client_update_res
                    if 'issue' in client_update_res:
                        err_msg = client_update_res['issue'][0]['diagnostics']
                    print('OAuth2 Client {} failed to update for redirect_uri "{}". Error found to be: "{}"'
                          .format(client_id, authorize_url, err_msg))
            except ValueError as e:
                print(e)
        elif 'error' in auth:
            print('OAuth2 Client {} failed to update for redirect_uri "{}". Error found to be: "{}"'
                  .format(client_id, authorize_url, auth['error_description']))
        else:
            print('OAuth2 Client {} failed to update for redirect_uri "{}". Error found to be: "{}"'
                  .format(client_id, authorize_url, auth))


if __name__ == '__main__':
    update_client('12345', {
        'username': '',
        'password': '',
        'client_id': '',
        'client_secret': '',
        'iam_url': '',
        'idm_url': '',
        'token_api_version': 2,
        'client_api_version': 1
    })
