import requests


class HttpUtils:

    @staticmethod
    def make_request(endpoint, with_headers=False):
        try:
            headers = None
            if with_headers:
                # TODO: Send headerse which APIs are expecting
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(endpoint, headers=headers)
            return r.text
        except requests.exceptions.RequestException as e:
            print("Could not complete request " + endpoint)
            print(e)
