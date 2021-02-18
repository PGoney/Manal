import logging
import time
import requests.exceptions

from datetime import datetime, timedelta
from sqlite3 import IntegrityError

from crawling import Guysome, Melon
from sql import con_melon

logger = logging.getLogger(__name__)

def ranking(con, dayTime):
    c = con.cursor()

    logger.info(f'Crawling ranking data of Melon at Guysome, date is {dayTime.strftime("%Y-%m-%d %H")}')
    ranking_list = Guysome.crawling(dayTime, site='melon', chart='realchart')
    logger.info(f'Ranking data of Melon at Guysome: #={len(ranking_list)}')

    logger.debug(f'Insert value at RANKING table')
    for ranking in ranking_list:
        c.execute(f'INSERT OR IGNORE INTO RANKING VALUES(?, ?, ?)', tuple(ranking.values()))

def artist(con, artist_id):
    c = con.cursor()

    c.execute(f'SELECT * FROM ARTIST WHERE ID={artist_id}')
    if c.fetchone() != None:
        return 0

    crawled_data = Melon.crawling_artist_detail(artist_id)
    artist = crawled_data['ARTIST']
    type_list = crawled_data['TYPE']
    genre_list = crawled_data['GENRE']
    company_belong = crawled_data['COMPANY_BELONG']

    logger.debug(f'Artist data of Melon: {crawled_data}')
    c.execute(f'INSERT INTO ARTIST VALUES(?, ?, ?)', tuple(artist.values()))

    for type_ in type_list:
        c.execute(f'INSERT INTO ARTIST_TYPE VALUES(?, ?)', (artist_id, type_))

    for genre in genre_list:
        c.execute(f'INSERT OR IGNORE INTO GENRE (NAME) VALUES("{genre}")')
        c.execute(f'SELECT ID FROM GENRE WHERE NAME="{genre}"')
        genre_id = c.fetchone()[0]
        c.execute(f'INSERT INTO ARTIST_GENRE VALUES(?, ?)', (artist_id, genre_id))

    for company in company_belong:
        c.execute(f'INSERT OR IGNORE INTO COMPANY (NAME) VALUES("{company}")')
        c.execute(f'SELECT ID FROM COMPANY WHERE NAME="{company}"')
        company_id = c.fetchone()[0]
        c.execute(f'INSERT INTO BELONG VALUES(?, ?)', (artist_id, company_id))

    return 1

def album(con, album_id):
    c = con.cursor()

    c.execute(f'SELECT * FROM ALBUM WHERE ID={album_id}')
    if c.fetchone() != None:
        return ( 0, 0 )

    crawled_data = Melon.crawling_album_detail(album_id)
    album = crawled_data['ALBUM']
    artist_id_list = crawled_data['ARTIST']
    genre_list = crawled_data['GENRE']
    company_publish = crawled_data['COMPANY_PUBLISH']
    company_plan = crawled_data['COMPANY_PLAN']

    logger.debug(f'Album data of Melon: {crawled_data}')
    c.execute(f'INSERT INTO ALBUM VALUES(?, ?, ?, ?, ?)', tuple(album.values()))

    artist_count = 0
    for artist_id in artist_id_list:
        artist_count += artist(con, artist_id)
        c.execute(f'INSERT INTO PARTICIPATE VALUES(?, ?)', (artist_id, album_id))

    for genre in genre_list:
        c.execute(f'INSERT OR IGNORE INTO GENRE (NAME) VALUES("{genre}")')
        c.execute(f'SELECT ID FROM GENRE WHERE NAME="{genre}"')
        genre_id = c.fetchone()[0]
        c.execute(f'INSERT INTO ALBUM_GENRE VALUES(?, ?)', (album_id, genre_id))

    for company in company_publish:
        c.execute(f'INSERT OR IGNORE INTO COMPANY (NAME) VALUES("{company}")')
        c.execute(f'SELECT ID FROM COMPANY WHERE NAME="{company}"')
        company_id = c.fetchone()[0]
        c.execute(f'INSERT INTO PUBLISH VALUES(?, ?)', (album_id, company_id))

    for company in company_plan:
        c.execute(f'INSERT OR IGNORE INTO COMPANY (NAME) VALUES("{company}")')
        c.execute(f'SELECT ID FROM COMPANY WHERE NAME="{company}"')
        company_id = c.fetchone()[0]
        c.execute(f'INSERT INTO PLAN VALUES(?, ?)', (album_id, company_id))

    return ( 1, artist_count )

def music(con, music_id):
    c = con.cursor()

    c.execute(f'SELECT * FROM MUSIC WHERE ID={music_id}')
    if c.fetchone() != None:
        return ( 0, 0, 0 )

    crawled_data = Melon.crawling_music_detail(music_id)
    music = crawled_data['MUSIC']
    album_id = crawled_data['ALBUM']
    artist_id_list = crawled_data['ARTIST']
    genre_list = crawled_data['GENRE']
    composer_list = crawled_data['COMPOSER']
    songwriter_list = crawled_data['SONGWRITER']
    arranger_list = crawled_data['ARRANGER']

    logger.debug(f'Music data of Melon: {crawled_data}')
    c.execute(f'INSERT INTO MUSIC VALUES(?, ?, ?)', tuple(music.values()))

    ( album_count, artist_count) = album(con, album_id)
    c.execute(f'INSERT INTO TRACK VALUES(?, ?)', (album_id, music_id))

    for artist_id in artist_id_list:
        artist_count += artist(con, artist_id)
        c.execute(f'INSERT INTO SING VALUES(?, ?)', (artist_id, music_id))

    for genre in genre_list:
        c.execute(f'INSERT OR IGNORE INTO GENRE (NAME) VALUES("{genre}")')
        c.execute(f'SELECT ID FROM GENRE WHERE NAME="{genre}"')
        genre_id = c.fetchone()[0]
        c.execute(f'INSERT INTO MUSIC_GENRE VALUES(?, ?)', (music_id, genre_id))

    for composer_id in composer_list:
        artist_count += artist(con, composer_id)
        c.execute(f'INSERT INTO COMPOSE VALUES(?, ?)', (composer_id, music_id))

    for songwriter_id in songwriter_list:
        artist_count += artist(con, songwriter_id)
        c.execute(f'INSERT INTO SONGWRITE VALUES(?, ?)', (songwriter_id, music_id))

    for arranger_id in arranger_list:
        artist_count += artist(con, arranger_id)
        c.execute(f'INSERT INTO ARRANGE VALUES(?, ?)', (arranger_id, music_id))

    return ( 1, album_count, artist_count )

def run(start_dayTime, end_dayTime):
    c = con_melon.cursor()

    dayTime = start_dayTime
    while dayTime <= end_dayTime:
        ranking(con_melon, dayTime)
        con_melon.commit()
        logger.debug(f'Commit DB: melon.db')
        dayTime += timedelta(hours=1)

    c.execute(f'SELECT DISTINCT MUSIC_ID FROM RANKING WHERE MUSIC_ID')
    music_id_list = c.fetchall()

    try:
        logger.info(f'Music data of Melon: #={len(music_id_list)}')
        logger.info(f'Crawling music data of Melon')
        count = [ 0, 0, 0 ]
        for music_id in music_id_list:
            m_count = music(con_melon, music_id[0])
            count[0] +=  m_count[0]
            count[1] += m_count[1]
            count[2] += m_count[2]
            con_melon.commit()
            logger.debug(f'Commit DB: melon.db')
        logger.info(f'Inserted music data of Melon at MUSIC table: #={count[0]}')
        logger.info(f'Inserted album data of Melon at ALBUM table: #={count[1]}')
        logger.info(f'Inserted artist data of Melon at ARTIST table: #={count[2]}')
    except requests.exceptions.HTTPError as e:
        print(e)

    con_melon.close()

if __name__ == '__main__':
    start_dayTime = datetime(2020, 3, 23, 0)
    end_dayTime = datetime(2020, 4, 5, 23)

    run(start_dayTime, end_dayTime)