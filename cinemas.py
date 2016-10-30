import requests
import argparse
import pyDes as coding
import hashlib
import datetime


def create_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s [аргументы]',
                                     description='Поиск популярных фильмов'
                                                 ' с помощью %(prog)s')
    parser.add_argument('-r', action='store_true',
                        help='рейтинг по числу кинотеатров, где идет фильм')
    parser.add_argument('-c', '--city', default='Москва', help='Ваш город')
    return parser


def get_afisha_request_value():
    url = 'http://api.afisha.ru/mobile/Service.aspx'
    auth = {'X-Afisha-Phone-Platform': 'Android', 'X-Afisha-Session-Id': '-1',
            'X-Afisha-App-Name': 'Android-Afisha', 'X-Afisha-App-Ver': '2.3.9',
            'X-Afisha-Protocol-Ver': '1.3', 'X-Afisha-Phone-Id': 'q1w2e3r4',
            'X-Afisha-Phone-Name': 'J', 'X-Afisha-Phone-Resolution': '480x800',
            'X-Afisha-Phone-Platform-Version': '4.2.2'}
    responce = requests.get(url, params=auth)
    return responce.headers['X-Afisha-Session-Request']


def afisha_api(session, contents):
    url = 'http://api.afisha.ru/mobile/Service.aspx'
    payload = {'X-Afisha-Phone-Id': 'q1w2e3r4', 'X-Afisha-Session-Id': session}
    responce = requests.post(url, params=payload, data=contents)
    return responce.json()


def get_afisha_session_value(request_value):
    SECRET = bytes([45, 56, 38, 71, 42, 105, 50, 77])
    INT_2_POW_64 = 18446744073709551616
    request_bytes = int(request_value).to_bytes(8, byteorder='little')
    cipher = coding.des(SECRET, coding.ECB, pad=None, padmode=coding.PAD_NORMAL)
    byte_array = cipher.encrypt(request_bytes)
    session = int.from_bytes(byte_array, byteorder='little', signed=True)
    if session < 0:
        session += INT_2_POW_64
    return session


def get_afisha_city_id(session, city):
    cities_headers = {'action': 'city_list'}
    cities = afisha_api(session, cities_headers)
    city_dict = next((x for x in cities if city == x['name'].lower()), None)
    return '2' if city_dict is None else city_dict['id']


def get_afisha_films_shedule(session, city):
    sort_by = {'alphabet': '2', 'rating': '3', 'popularity': '5'}
    films_shedule_headers = {'action': 'theme_schedule', 'cityId': city,
                             'themeId': '2', 'count': '1000', 'start': '0',
                             'sortOrder': sort_by['popularity']}
    return afisha_api(session, films_shedule_headers)['list']


def get_cinemas_where_is_film(session, film, city):
    sort_by = {'alphabet': '2', 'rating': '3', 'popularity': '5'}
    film_cinemas_header = {'action': 'schedule', 'clsId': '16',
                           'scheduleFormat': '2', 'cityId': city,
                           'sortOrder': sort_by['rating'], 'id': film}
    return afisha_api(session, film_cinemas_header)


def get_afisha_film_params(session, film, city):
    header = {'action': 'product', 'clsId': '16', 'cityId': city, 'id': film}
    return afisha_api(session, header)[0]


def get_films_info(session, films, city):
    films_list = []
    votes = rating = 0
    for film in films:
        film_in_cinemas = get_cinemas_where_is_film(session, film['id'], city)
        cinemas_count = film_in_cinemas['maxCount']
        afisha_film_info = get_afisha_film_params(session, film['id'], city)
        name_ru = afisha_film_info.get('name')
        name_en = afisha_film_info.get('nameOrg')
        year = afisha_film_info.get('year')
        kp_films = get_kinopoisk_films_list(name_ru)
        if kp_films is not None:
            film_filter = [x for x in kp_films if year == x.get('year') and (
                name_ru == x.get('nameRU') or name_en == x.get('nameEN'))]
            kp_film = None if len(film_filter) == 0 else film_filter[0]
            if kp_film is not None:
                votes = kp_film.get('ratingVoteCount', '0')
                rating = kp_film.get('rating', '0')
                if rating.endswith('%'):
                    rating = float(rating.strip('%')) / 100
                else:
                    rating = float(rating)
        films_list.append((name_ru, year, votes, rating, cinemas_count,))
    return films_list


def get_kinopoisk_films_list(film):
    url = 'https://ext.kinopoisk.ru/ios/3.4.1/getKPLiveSearch'
    uuid_str = 'ee21fde7832c7d4d43dc3fafc6449e6c'
    api_secret = 'samuraivbolote'
    now_time = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
    str_for_key = 'getKPLiveSearch?keyword={0}&uuid={1}{2}' \
                  .format(requests.utils.quote(film), uuid_str, api_secret)
    key = hashlib.md5((str_for_key).encode('utf-8')).hexdigest()
    cookies = {'Cookie': 'user_country=ru; PHPSESSID=7150234fb38f731e0c6f8cff',
               'Cookie2: $Version': '1'}
    headers = {'device': 'android', 'Image-Scale': '1.5', 'countryID': '2',
               'cityID': '1', 'Android-Api-Version': '17',
               'User-Agent': 'ru.kinopoisk/3.4.3', 'clientDate': now_time}
    payload = {'keyword': film, 'key': key, 'uuid': uuid_str}
    films = requests.get(url, params=payload, headers=headers, cookies=cookies)
    if 'ETag' in films.headers:
        films_list = films.json()['data']['items']
        return None if len(films_list) == 0 else films_list


def find_popular_films(films, cinema_rating):
    POPULAR_FILMS_NUMBER = 10
    if cinema_rating:
        films.sort(key=lambda x: x[4], reverse=True)
    else:
        films.sort(key=lambda x: x[3], reverse=True)
    return films[:POPULAR_FILMS_NUMBER]


def output_movies_to_console(films, rating, city):
    out = ('рейтингу кинопоиска', 'числу кинотеатров',)
    print('Популярные фильмы по {0} в городе {1}:'.format(out[rating], city))
    for film_num, film in enumerate(films, 1):
        print('{0}) "{1}" ({2}), рейтинг: {3}, число кинотеатров: {4}'
              .format(film_num, film[0], film[1], film[3], film[4]))


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    cinema_rating = namespace.r
    city = namespace.city

    session_request = get_afisha_request_value()
    session_id = get_afisha_session_value(session_request)
    city_id = get_afisha_city_id(session_id, city.lower())
    films_today = get_afisha_films_shedule(session_id, city_id)
    films_info = get_films_info(session_id, films_today, city_id)
    films = find_popular_films(films_info, cinema_rating)
    output_movies_to_console(films, cinema_rating, city)
