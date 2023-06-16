import requests, os, weakref
from bs4 import BeautifulSoup

from log.metaclass import MethodLoggerMeta


class Downloader(object, metaclass=MethodLoggerMeta):
    def __init__(self, needs_login, login_payload, base_url, download_postfix, login_postfix, csrf_attr, headers):
        self.base_url = base_url
        self.download_postfix = download_postfix
        self.login_postfix = login_postfix
        self.login_payload = login_payload
        self.csrf_attr = csrf_attr
        self.headers = headers
        self.needs_login = needs_login
        self.session = requests.Session()
        self._finalizer = weakref.finalize(self, self.close_session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._finalizer()

    def close_session(self):
        self.session.close()

    @property
    def login_url(self):
        return self.base_url + self.login_postfix

    @property
    def download_url(self):
        return self.base_url + self.download_postfix

    def download(self, destination_file):
        try:
            self.set_csrf()
        except CSRFNotFoundException as e:
            raise e
        if self.needs_login:
            try:
                self.login()
            except LoginException as e:
                raise e

        content = self.get_content_to_download()
        destination_dir = os.path.dirname(destination_file)
        self.ensure_dirs(destination_dir)
        self.write(content, destination_file, "wb")

    def login(self):
        login_payload = self.get_login_payload()
        response = self.post(url=self.login_url,
                             data=login_payload,
                             headers=self.headers)

        if not response.ok:
            raise LoginException(error=response.reason, url=self.login_url, payload=self.login_payload)

    def get_content_to_download(self):
        response = self.get(
            url=self.download_url
        )
        return response.content

    def ensure_dirs(self, destination):
        os.makedirs(destination, exist_ok=True)

    def write(self, content, destination, mode):
        with open(destination, mode) as f:
            f.write(content)

    def get_login_payload(self):
        return self.login_payload

    def set_csrf(self):
        response = self.get(self.base_url)
        try:
            csrf = self.get_attr(response.content, self.csrf_attr)
        except IndexError as e:
            raise CSRFNotFoundException(attr=self.csrf_attr, url=self.base_url)
        self.login_payload[self.csrf_attr] = csrf

    def get_attr(self, content, attr):
        attrs = self.get_attrs(content, attr)
        try:
            attr = attrs[0]["value"]
        except IndexError as e:
            raise e
        return attr

    def get_attrs(self, content, attr):
        soup = BeautifulSoup(content, 'html.parser')
        attrs = soup.find_all(attrs={"name": attr})
        return attrs

    def get(self, url):
        return self.session.get(url)

    def post(self, url, data, headers):
        return self.session.post(
            url,
            data=data,
            headers=headers
        )


class LoginException(Exception):
    def __init__(self, error, url, payload):
        self.payload = payload
        self.url = url
        self.error = error
        self.message = f"Error: {self.error}. Could not login to {self.url} with payload: {self.payload}."
        super().__init__(self.message)


class CSRFNotFoundException(Exception):
    def __init__(self, attr, url):
        self.attr = attr
        self.url = url
        self.message = f"Error: could not find {self.attr} on page: {self.url}"
