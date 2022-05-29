import json
from urllib.request import urlopen

import requests
from telegram.ext import filters

from src.services.api import Api
from bs4 import BeautifulSoup
class LocationService(Api):
    secondary_path = 'event/json-calendar'
    dicts = {
        'system': dict(),
        'setting': dict(),
        'genre': dict(),
        'master': dict(),
    }
    games = []
    def __init__(self):
        super().__init__()
        self.get_json_calendar()
        self.fill_dictionaries()

    def filter_old_events(self, calendar_item):
        return ('new' in calendar_item['className']) and not(not(calendar_item['id']))

    def enrich_weekeng_game(self, game):
        games = []

        page = BeautifulSoup(requests.get(game['url']).text, 'html')
        # properties
        event_days = page.find_all('div', {'class': 'event-day'})
        for day in event_days:
            time_caption = '' if not(day.find('div', {'class': 'caption'})) else day.find('div', {'class': 'caption'}).text
            content = day.find_all('a', {'class': 'js-game-title'})
            for game in content:
                games.append(
                    self.enrich_single_game(
                        {
                            'time': time_caption,
                            'type': 'weekend',
                            'url': 'https://rolecon.ru' + game.attrs['href'],
                            'id': str(game.attrs['href']).split('/')[-1]
                        }
                    )
                )
        return games

    def enrich_single_game(self, game):
        fields = {
            'Сеттинг:': 'setting',
            'Система:': 'system',
            'Жанр:': 'genre',
            'Программа:': 'program',
            'Игру проводит:': 'master',
            'Места:': 'seats'
        }
        properties = []
        page = BeautifulSoup(requests.get(game['url']).text, 'html')
        # properties
        game['title'] = game.get('title') if not (page.find('h4')) else page.find('h4').text
        if not(game.get('time')):
            game['time'] = (game.get('time') or '') if not(page.find('p',{'class': 'subcaption-h4'})) else page.find('p',{'class': 'subcaption-h4'}).text
        table = page.find('table', {'class': 'table-single'})
        if table:
            for tr in table.find_all('tr'):
                cells = tr.find_all('td')
                properties.append((cells[0].text, cells[1].text))
                if fields.get(cells[0].text):
                    game[fields[cells[0].text]] = cells[1].text
        game['properties'] = properties

        # description
        desc = page.find('div', {'class': 'i-description'})
        if desc:
            if desc.find('div', {'class': 'game-description'}):
                game['description'] = '' if not(desc.find('div', {'class': 'game-description'})) else desc.find('div', {'class': 'game-description'}).text
            if desc.find('div', {'class': 'img'}):
                game['img'] = '' if not (desc.find('div', {'class': 'img'})) else 'https://rolecon.ru' + desc.find('img').attrs['src']

        return game

    def get_json_calendar(self):
        calendar = self.http.get('https://rolecon.ru/event/json-calendar?start=2022-04-25&end=2022-08-06').json()
        calendar = map(
            lambda item: {
                'id': item['id'],
                'title': item['title'],
                'url': 'https://rolecon.ru' + item['url'],
                'start': item['start'],
                'end': item['end'],
                'fullDay': True if item['allDay'] else False,
            },
            list(filter(self.filter_old_events, calendar)),
        )
        for item in list(calendar)[0:3]:
            if "/game" in item['url']:
                item['type'] = 'single'
                self.games.append(self.enrich_single_game(item))
            elif "/lw" in item['url']:
                self.games += self.enrich_weekeng_game(item)

    def fill_dictionaries(self):
        dicts = {
            'system': set(),
            'setting': set(),
            'genre': set(),
            'master': set(),
        }
        for game in self.games:
            if game.get('system'):
                dicts.get('system').add(game.get('system'))
            if game.get('setting'):
                dicts.get('setting').add(game.get('setting'))
            if game.get('genre'):
                dicts.get('genre').add(game.get('genre'))
            if game.get('master'):
                dicts.get('master').add(game.get('master'))

        for idx, d in enumerate(dicts.get('setting')):
            self.dicts['setting'][str(idx)] = d
        for idx, d in enumerate(dicts.get('genre')):
            self.dicts['genre'][str(idx)] = d
        for idx, d in enumerate(dicts.get('system')):
            self.dicts['system'][str(idx)] = d
        for idx, d in enumerate(dicts.get('master')):
            self.dicts['master'][str(idx)] = d

