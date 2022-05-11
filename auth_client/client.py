import requests
from auth_client.authenticate import Authenticate
from json import JSONDecodeError


class OAuth2Client:
    """
    Updates OAuth2Client for redirect_uri in IAM using /authorize/identity/Client API.
    Usage: Use the following flow of methods to update redirect_uri for an existing client.

    access_token - Use Authenticate to get the access token from IAM API.

    OAuth2Client('idm_url')
        .add_headers(1, 'access_token')
        .get_client('client_name')
        .update_client('redirect_uri')
    """

    def __init__(self, url):
        super(OAuth2Client, self).__init__()
        self.url = ''.join([url, '/authorize/identity/Client'])
        self.api_version = None
        self.access_token = None
        self.headers = {}
        self.client = {}

    def add_headers(self, api_version, access_token):
        self.api_version = api_version
        self.access_token = access_token
        self.headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'api-version': str(api_version),
            'Content-Type': 'application/json'
        }
        return self

    def get_client(self, client_name):
        query = 'name={}'.format(client_name)
        idm_url = ''.join([self.url, '?', query])
        res = requests.get(idm_url, headers=self.headers)
        if res.status_code == 200:
            print('OAuth2Client {} found in idm_url: {}'.format(
                client_name, idm_url))
            self.client = res.json()
        else:
            print('OAuth2Client {} failed to find in idm_url: {}'.format(
                client_name, idm_url))
            try:
                self.client = res.json()
            except JSONDecodeError:
                self.client = res.content.decode('ascii')
        return self

    def update_client(self, redirect_uri):
        if 'entry' not in self.client:
            raise ValueError(
                'OAuth2Client failed to find an entry in Authorize IAM for {}'.format(redirect_uri))
        for entry in self.client['entry']:
            redirect_uris = entry['redirectionURIs']
            if redirect_uri not in redirect_uris:
                redirect_uris.append(redirect_uri)
                entry['redirectionURIs'] = redirect_uris

                res = requests.put(
                    '/'.join([self.url, entry['id']]), headers=self.headers, json=entry)
                res_status_code = res.status_code
                if res_status_code == 200:
                    print('OAuth2 Client {} updated for redirect_uri {}'.format(
                        entry['clientId'], redirect_uri))
                else:
                    print('OAuth2 Client {} failed to update for redirect_uri {}. request status: {}'
                          .format(entry['clientId'], redirect_uri, res_status_code))

                return res.json()
            else:
                print('OAuth2 Client {} has the redirect_uri {}'.format(
                    entry['clientId'], redirect_uri))
                return 'existing'
