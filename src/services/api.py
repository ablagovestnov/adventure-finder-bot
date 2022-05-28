import requests

class Api():
    api_url = 'https://rolecon.ru'
    path = ''
    secondary_path = ''
    http = False
    def __init__(self):
        self.http = requests
        self.path = '/'.join([self.api_url, self.secondary_path])

    def create(self):
        return False

    def read(self):
        return requests.get(self.path)

    def update(self):
        return False

    def delete(self):
        return False
