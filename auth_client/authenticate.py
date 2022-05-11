import requests
import base64
from json import JSONDecodeError


class Authenticate:
    def __init__(self, url):
        self.url = url
        self.headers = {}

    def add_headers(self, client_id, client_secret, api_version):
        client_creds = (
            base64.encodebytes(":".join([client_id, client_secret]).encode("ascii"))
            .decode("ascii")
            .replace("\n", "")
        )

        self.headers = headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic {}".format(client_creds),
            "api-version": str(api_version),
        }
        return self

    def login(self, username, password):
        iam_url = "/".join([self.url, "authorize/oauth2/token"])
        res = requests.post(
            iam_url,
            headers=self.headers,
            data="grant_type=password&username={}&password={}".format(
                username, password
            ),
        )
        if res.status_code == 200:
            print("Authentication successful.")
        else:
            print("Failed to authenticate.")

        try:
            return res.json()
        except JSONDecodeError:
            return res.content.decode("ascii")


if __name__ == "__main__":
    print(Authenticate("").add_headers("", "", 2).login("", ""))
