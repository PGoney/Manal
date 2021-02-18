import json
import sqlite3
import logging

from datetime import datetime

from common import Singleton

logger = logging.getLogger(__name__)

class _SQL(object):
    def __init__(self, title):
        self._conn = sqlite3.connect(f'{title}.db')
        logger.debug(f'Connect DB: {title}.db')
        
        with open(f'{title}.json', 'r', encoding='utf-8') as f:
            structure = json.load(f)
        tables = [ _Table(table) for table in structure['table'] ]

        c = self._conn.cursor()
        for table in tables:
            c.execute(table.ddl_create())
            logger.debug(f'Create table: {table._name} ( {", ".join(attr._name for attr in table._attributes)} )')
            
        self._conn.commit()
        logger.debug(f'Commit DB: {title}.db')

class _Table(object):
    def __init__(self, table: dict):
        self._name = table['name']
        self._attributes = [ _Attribute(attr) for attr in table['attribute'] ]

    def ddl_create(self):
        has_auto_increment = False
        for attr in self._attributes:
            if attr._auto_increment:
                has_auto_increment = True
                break

        if has_auto_increment:
            ret = f'CREATE TABLE IF NOT EXISTS {self._name} ('
            ret += ', '.join([ str(attr) for attr in self._attributes ])
            for attr in self._attributes:
                if attr._forein_key:
                    ret += f', FOREIGN KEY ({attr._name}) REFERENCES {attr._forein_key["references"]["table"]}({attr._forein_key["references"]["attribute"]})'
            ret += ')'
        else:
            ret = f'CREATE TABLE IF NOT EXISTS {self._name} ('
            ret += ', '.join([ str(attr) for attr in self._attributes ])
            ret += f', PRIMARY KEY({", ".join([ attr._name for attr in self._attributes if attr._primary_key ])})'
            for attr in self._attributes:
                if attr._forein_key:
                    ret += f', FOREIGN KEY ({attr._name}) REFERENCES {attr._forein_key["references"]["table"]}({attr._forein_key["references"]["attribute"]})'
            ret += ')'

        return ret

class _Attribute(object):
    def __init__(self, attribute: dict):
        self._name = attribute['name']
        self._type = attribute['type']
        self._auto_increment = attribute.get('auto-increment')
        self._unique = attribute.get('unique')
        self._default = attribute.get('default')
        self._primary_key = attribute.get('primary_key')
        self._forein_key = attribute.get('forein_key')

    def __str__(self):
        ret = f'{self._name} {self._type}'
        if self._auto_increment:
            ret += f' PRIMARY KEY AUTOINCREMENT'
        if self._unique:
            ret += f' UNIQUE'
        if self._default:
            ret += f' DEFAULT "{self._default}"'
        return ret

class _MelonSQL(_SQL, metaclass=Singleton):
    def __init__(self):
        super().__init__('melon')

con_melon = _MelonSQL()._conn

# def open():
#     global conn
#     conn = sqlite3.connect('melon.db')

# def close():
#     conn.close()

# def init():
#     c = conn.cursor()

#     c.execute('''
#         CREATE TABLE IF NOT EXISTS MUSIC (
#             ID  INTEGER,
#             NAME    TEXT,
#             RELEASE_DATE    NUMERIC,
#             LYRICS  TEXT,
#             PRIMARY KEY (ID)
#         )
#     ''')

#     c.execute('''
#         CREATE TABLE IF NOT EXISTS ALBUM (
#             ID  INTEGER,
#             TYPE    TEXT
#             NAME    TEXT,
#             RELEASE_DATE    NUMERIC,
#             INTRODUCE   TEXT,
#             PRIMARY KEY (ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS ARTIST (
#             ID INTEGER,
#             NAME    TEXT,
#             COUNTRY TEXT,
#             GROUP_ID   INTEGER,
#             PRIMARY KEY (ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS COMPOSITION (
#             MUSIC_ID    INTEGER,
#             NAME    TEXT,
#             TYPE    TEXT,
#             PRIMARY KEY (MUSIC_ID, NAME, TYPE)
#             FOREIGN KEY (MUSIC_ID) REFERENCES MUSIC(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS GENRE (
#             ID  INTEGER PRIMARY KEY AUTOINCREMENT,
#             NAME    TEXT
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS RANKING (
#             MUSIC_ID    INTEGER,
#             DATE    NUMERIC,
#             RANK    INTEGER,
#             PRIMARY KEY (DATE, RANK),
#             FOREIGN KEY (MUSIC_ID) REFERENCES MUSIC(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS COMPANY (
#             ID  INTEGER PRIMARY KEY AUTOINCREMENT,
#             NAME    TEXT
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS TRACK (
#             MUSIC_ID    INTEGER,
#             ALBUM_ID    INTEGER,
#             PRIMARY KEY (MUSIC_ID, ALBUM_ID),
#             FOREIGN KEY (MUSIC_ID) REFERENCES MUSIC(ID),
#             FOREIGN KEY (ALBUM_ID) REFERENCES ALBUM(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS SING (
#             MUSIC_ID    INTEGER,
#             ARTIST_ID   INTEGER,
#             PRIMARY KEY (MUSIC_ID, ARTIST_ID),
#             FOREIGN KEY (MUSIC_ID) REFERENCES MUSIC(ID),
#             FOREIGN KEY (ARTIST_ID) REFERENCES ARTIST(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS HAS_MUSIC_GENRE (
#             MUSIC_ID    INTEGER,
#             GENRE_ID    INTEGER,
#             PRIMARY KEY (MUSIC_ID, GENRE_ID),
#             FOREIGN KEY (MUSIC_ID) REFERENCES MUSIC(ID),
#             FOREIGN KEY (GENRE_ID) REFERENCES GENRE(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS HAS_ALBUM_GENRE (
#             ALBUM_ID    INTEGER,
#             GENRE_ID    INTEGER,
#             PRIMARY KEY (ALBUM_ID, GENRE_ID),
#             FOREIGN KEY (ALBUM_ID) REFERENCES ALBUM(ID),
#             FOREIGN KEY (GENRE_ID) REFERENCES GENRE(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS HAS_ARTIST_GENRE (
#             ARTIST_ID    INTEGER,
#             GENRE_ID    INTEGER,
#             PRIMARY KEY (ARTIST_ID, GENRE_ID),
#             FOREIGN KEY (ARTIST_ID) REFERENCES ARTIST(ID),
#             FOREIGN KEY (GENRE_ID) REFERENCES GENRE(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS PARTICIPATE (
#             ALBUM_ID    INTEGER,
#             ARTIST_ID    INTEGER,
#             PRIMARY KEY (ALBUM_ID, ARTIST_ID),
#             FOREIGN KEY (ALBUM_ID) REFERENCES ALBUM(ID),
#             FOREIGN KEY (ARTIST_ID) REFERENCES ARTIST(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS ARTIST_TYPE (
#             ARTIST_ID    INTEGER,
#             NAME    TEXT,
#             PRIMARY KEY (ARTIST_ID, NAME),
#             FOREIGN KEY (ARTIST_ID) REFERENCES ARTIST(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS BELONG (
#             ARTIST_ID    INTEGER,
#             COMPANY_ID  INTEGER,
#             PRIMARY KEY (ARTIST_ID, COMPANY_ID),
#             FOREIGN KEY (ARTIST_ID) REFERENCES ARTIST(ID),
#             FOREIGN KEY (COMPANY_ID) REFERENCES COMPANY(ID)
#         )
#     ''')
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS PUBLISH (
#             ALBUM_ID    INTEGER,
#             COMPANY_ID  INTEGER,
#             TYPE    TEXT,
#             PRIMARY KEY (ALBUM_ID, COMPANY_ID, TYPE),
#             FOREIGN KEY (ALBUM_ID) REFERENCES ALBUM(ID),
#             FOREIGN KEY (COMPANY_ID) REFERENCES COMPANY(ID)
#         )
#     ''')

#     conn.commit()