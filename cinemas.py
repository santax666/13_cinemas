import requests
import time
import json
import operator
import argparse
from bs4 import BeautifulSoup


def create_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s [аргументы]',
                                     description='Поиск популярных фильмов'
                                                 ' с помощью %(prog)s')
    parser.add_argument('-r', action='store_true',
                        help='рейтинг по числу кинотеатров, где идет фильм')
    parser.add_argument('-c', '--city', default='Москва', help="Ваш город")
    return parser


def send_get_request(url):
    response = requests.get(url)
    return response


def fetch_afisha_page(domain):
    films_list = []
    url = 'http:{0}schedule_cinema/'.format(domain)
    class_for_films = 'object s-votes-hover-area collapsed'
    class_for_name = 'usetags'
    class_for_cinema = 'b-td-item'
    page = send_get_request(url).content
    soup = BeautifulSoup(page, 'html.parser')
    films_html = soup.find_all('div', {'class': class_for_films})
    for film in films_html:
        film_name = film.find('h3', {'class': class_for_name}).text
        cinema_count = len(film.find_all('td', {'class': class_for_cinema}))
        films_list.append([film_name, cinema_count])
    return films_list


def parse_afisha_list(films):
    for film in films:
        film_rating = fetch_movie_info(film[0])
        if film_rating is not None:
            film.extend(film_rating.copy())
        else:
            film.extend([0, 0])
    return films


def create_query_string(film_name):
    domain = 'suggest-kinopoisk.yandex.net'
    resurs = 'kinopoisk'
    template = 'https://{0}/suggest-kinopoisk?srv={1}&part={2}&_={3}'
    timestamp = int(time.time())
    url = (template.format(domain, resurs, film_name, timestamp))
    return url


def fetch_movie_info(film_name):
    url = create_query_string(film_name)
    films_list = send_get_request(url).json()[2]
    if not len(films_list) == 0:
        film_dict = json.loads(films_list[0])
        votes = film_dict.get('rating', {}).get('votes')
        if votes is None:
            votes = 0
        rate = film_dict.get('rating', {}).get('rate')
        if rate is None:
            rate = 0
        return [votes, rate]


def find_popular_films(films, cinema_rating):
    popular_films_number = 10
    if cinema_rating:
        films.sort(key=operator.itemgetter(1, 3), reverse=True)
    else:
        films.sort(key=operator.itemgetter(3), reverse=True)
    return films[:popular_films_number]


def output_movies_to_console(films, rating, city):
    output_text = ('рейтингу кинопоиска', 'числу кинотеатров',)
    print('Популярные фильмы по {0} в городе {1}:'
          .format(output_text[rating], city))
    for film_num, film in enumerate(films, 1):
        print('{0}) "{1}", рейтинг Кинопоиска: {2}, число кинотеатров: {3}'
              .format(film_num, film[0], film[3], film[1]))


def get_city_url(name):
    city_classes = ['js-geographyplaceid dd-link ',
                    'js-geographyplaceid dd-link bold']
    afisha_url = 'http://www.afisha.ru/finderror/'
    afisha_page = send_get_request(afisha_url).content
    afisha_page = afisha_page.decode('utf-8').lower()
    name = name.lower()
    soup = BeautifulSoup(afisha_page, 'html.parser')
    cities_bloсk = soup.find('span', {'class': city_classes},
                             text=name)
    return cities_bloсk['data-href']


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    cinema_rating = namespace.r
    city = namespace.city

    url_domain = get_city_url(city)
    films_name_list = fetch_afisha_page(url_domain)
    films_info = parse_afisha_list(films_name_list)
    films = find_popular_films(films_info, cinema_rating)
    output_movies_to_console(films, cinema_rating, city)
