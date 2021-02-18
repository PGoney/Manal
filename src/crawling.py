import requests
import re
import logging

from enum import Enum
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Guysome(object):
    _base_url = "https://xn--o39an51b2re.com"
    _headers = {
        "Content-Type" : "text/html; charset=utf-8",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
    }

    @classmethod
    def crawling(cls, dayTime: datetime, site="melon", chart="realchart"):
        if site == "melon":
            return cls._crawling_melon(chart, dayTime)

    @classmethod
    def _crawling_melon(cls, chart, dayTime):
        url = f'{cls._base_url}/melon/{chart}/{dayTime.strftime("%Y/%m/%d/%H")}/'

        response = requests.get(url, headers=cls._headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        ranking_list = []

        for row in soup.select('table > tbody > tr'):
            id_ = int(re.findall('\\d+', row.attrs['onclick'])[0])
            rank = int(row.select('.ranking > p > span')[1].text)

            ranking = {
                "MUSIC_ID" : id_,
                "DATE" : dayTime,
                "RANK" : rank
            }

            ranking_list.append(ranking)

        return ranking_list

class Melon(object):
    _base_url = "https://www.melon.com"
    _headers = {
        "Content-Type" : "text/html; charset=utf-8",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
    }

    @classmethod
    def crawling_music_detail(cls, music_id):
        url = f'{cls._base_url}/song/detail.htm?songId={music_id}'

        response = requests.get(url, headers=cls._headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
            
        ret = {
            "MUSIC" : {
                "ID" : music_id,
                "NAME" : None,
                "RELEASE_DATE" : None
            },
            "ARTIST" : [],
            "ALBUM" : None,
            "GENRE" : [],
            "COMPOSER" : [],
            "SONGWRITER" : [],
            "ARRANGER" : []
        }
        music = ret['MUSIC']

        entry = soup.find('div', 'entry')

        info = entry.find('div', 'info')
        music_name = info.find('div', class_='song_name')
        music_name.strong.decompose()
        music['NAME'] = music_name.text.strip()
        artist_id = [ int(re.findall('\\d+', artist.attrs['href'])[0]) for artist in info.find_all('a', class_='artist_name') ]
        ret['ARTIST'] = set(artist_id)

        meta = entry.find('dl', 'list')
        dd = meta.find_all('dd')
        ret['ALBUM'] = int(re.findall('\\d+', dd[0].find('a').attrs['href'])[0])
        release_date = dd[1].text
        music['RELEASE_DATE'] = datetime.strptime(release_date, "%Y.%m.%d")
        ret['GENRE'] = set(dd[2].text.split(", "))

        list_person = soup.find('ul', class_='list_person')
        if list_person != None:
            composer = []
            songwriter = []
            arranger = []
            for entry in list_person.find_all('div', class_='entry'):
                com_artist_index = int(re.findall('\\d+', entry.find('a', class_='artist_name').attrs['href'])[0])
                com_type = entry.find('span', 'type').text
                if com_type == '작곡':
                    composer.append(com_artist_index)
                elif com_type == '작사':
                    songwriter.append(com_artist_index)
                elif com_type == '편곡':
                    arranger.append(com_artist_index)
                else:
                    logging.warning(f'There is another type of composition: {com_type}')
            ret['COMPOSER'] = set(composer)
            ret['SONGWRITER'] = set(songwriter)
            ret['ARRANGER'] = set(arranger)

        return ret

    @classmethod
    def crawling_artist_detail(cls, artist_id):
        url = f'{cls._base_url}/artist/detail.htm?artistId={artist_id}'

        response = requests.get(url, headers=cls._headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        ret = {
            'ARTIST' : {
                'ID' : artist_id,
                'NAME' : None,
                'COUNTRY' : None
            },
            'GROUP_ID' : [],
            'TYPE' : [],
            'GENRE' : [],
            'COMPANY_BELONG' : []
        }
        artist = ret['ARTIST']
        
        name = soup.find('p', class_='title_atist')
        name.strong.decompose()
        name = name.text.strip()
        artist['NAME'] = name

        section_atistinfo03 = soup.find('div', class_='section_atistinfo03')
        list_define = section_atistinfo03.find('dl', class_='list_define')
        dt = list_define.find_all('dt')
        dd = list_define.find_all('dd')
        for i in range(0, len(dt)):
            t = dt[i].text
            d = dd[i]
            if t == '유형':
                ret['TYPE'] = set([ type_.strip() for type_ in d.text.split('|') ])
            elif t == '장르':
                ret['GENRE'] = set(d.text.split(', '))
            elif t == '소속사명':
                ret['COMPANY_BELONG'] = set(d.text.split(', '))
            elif t == '소속그룹':
                ret['GROUP_ID'] = set([ int(re.findall('\\d+', group.attrs['href'])[0]) for group in d.find_all('a') ])

        section_atistinfo04 = soup.find('div', class_='section_atistinfo04')
        list_define = section_atistinfo04.find('dl', class_='list_define')
        dt = list_define.find_all('dt')
        dd = list_define.find_all('dd')
        for i in range(0, len(dt)):
            t = dt[i].text
            d = dd[i].text
            if t == '국적':
                artist['COUNTRY'] = d

        return ret

    @classmethod
    def crawling_album_detail(cls, album_id):
        url = f'{cls._base_url}/album/detail.htm?albumId={album_id}'

        response = requests.get(url, headers=cls._headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        ret = {
            'ALBUM' : {
                'ID' : album_id,
                'TYPE' : None,
                'NAME' : None,
                'RELEASE_DATE' : None,
                'IMAGE_SRC' : None
            },
            'ARTIST' : [],
            'GENRE' : [],
            'COMPANY_PUBLISH' : [],
            'COMPANY_PLAN' : []
        }
        album = ret['ALBUM']

        thumb = soup.find('div', 'thumb')
        img = thumb.find('img')
        album['IMAGE_SRC'] = img.attrs['src']

        entry = soup.find('div', 'entry')
        info = entry.find('div', 'info')
        
        type_ = info.find('span', 'gubun').text.strip()
        album['TYPE'] = type_

        name = info.find('div', 'song_name')
        name.strong.decompose()
        name = name.text.strip()
        album['NAME'] = name

        artist_id = [ int(re.findall('\\d+', artist.attrs['href'])[0]) for artist in info.find_all('a', 'artist_name') ]
        ret['ARTIST'] = set(artist_id)

        meta = entry.find('dl', 'list')
        dt = meta.find_all('dt')
        dd = meta.find_all('dd')
        for i in range(0, len(dt)):
            t = dt[i].text
            d = dd[i]
            if t == '발매일':
                release_date = datetime.strptime(d.text, "%Y.%m.%d")
                album['RELEASE_DATE'] = release_date
            elif t == '장르':
                ret['GENRE'] = set(d.text.split(', '))
            elif t == '발매사':
                ret['COMPANY_PUBLISH'] = set(d.text.split(', '))
            elif t == '기획사':
                ret['COMPANY_PLAN'] = set(d.text.split(', '))

        return ret