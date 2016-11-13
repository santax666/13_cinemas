import requests
import argparse
from bs4 import BeautifulSoup


def create_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s [аргументы]',
                                     description='Поиск популярных фильмов'
                                                 ' с помощью %(prog)s')
    parser.add_argument('-r', action='store_true',
                        help='рейтинг по числу кинотеатров, где идет фильм')
    return parser


def get_films_from_afisha_page():
    films_list = []
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    block = {'films': 'object s-votes-hover-area collapsed', 'name': 'usetags',
             'cinemas': 'b-td-item'}
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    films_html = soup.find_all('div', {'class': block['films']})
    for film in films_html:
        film_name = film.find('h3', {'class': block['name']}).text
        cinema_count = len(film.find_all('td', {'class': block['cinemas']}))
        film_kp_id = ''.join(get_kinopoisk_film_id(film_name))
        votes, rating = get_kinopoisk_film_rating(film_kp_id)
        films_list.append([film_name, cinema_count, votes, rating])
    return films_list


def get_kinopoisk_film_id(film_name):
    search_url = 'https://www.kinopoisk.ru/search/handler-chromium-extensions'
    payload = {'query': film_name, 'go': 1}
    film_data = requests.get(search_url, params=payload, allow_redirects=False)
    film_url = film_data.headers.get ('Location')
    yield '0' if film_url is None else film_url.split('/')[4]


def get_kinopoisk_film_rating(film_id):
    rating_kp_url = 'https://rating.kinopoisk.ru/{0}.xml'
    if film_id == '0':
        return 0, 0
    rating_page = requests.get(rating_kp_url.format(film_id)).content
    soup = BeautifulSoup(rating_page, 'xml')
    return soup.kp_rating['num_vote'], float(soup.kp_rating.text)


def find_popular_films(films, cinema_rating):
    POPULAR_FILMS_NUMBER = 10
    if cinema_rating:
        films.sort(key=lambda x: x[1], reverse=True)
    else:
        films.sort(key=lambda x: x[3], reverse=True)
    return films[:POPULAR_FILMS_NUMBER]


def output_movies_to_console(films, rating):
    out = ('рейтингу кинопоиска', 'числу кинотеатров',)
    print('Популярные фильмы по {0} в городе Москва:'.format(out[rating]))
    for film_num, film in enumerate(films, 1):
        print('{0}) "{1}", рейтинг: {2}, число кинотеатров: {3}'
              .format(film_num, film[0], film[3], film[1]))


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    cinema_rating = namespace.r

    films_list = get_films_from_afisha_page()
    films = find_popular_films(films_list, cinema_rating)
    output_movies_to_console(films, cinema_rating)
