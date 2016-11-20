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
        votes, rating = get_kinopoisk_film_rating(film_name)
        films_list.append((rating, cinema_count, votes, film_name,))
    return films_list


def get_kinopoisk_film_rating(film_name):
    search_url = 'https://www.kinopoisk.ru/search/handler-chromium-extensions'
    payload = {'query': film_name, 'go': 1}
    film_data = requests.get(search_url, params=payload).content
    soup = BeautifulSoup(film_data, 'html.parser')
    rating = getattr(soup.find('span', {'class': 'rating_ball'}), 'text', 0)
    votes = getattr(soup.find('span', {'class': 'ratingCount'}), 'text', 0)
    return votes, float(rating)


def find_popular_films(films, rating):
    popular_films_number = 10
    popular_films = sorted(films, key=lambda x: x[rating], reverse=True)
    return popular_films[:popular_films_number]


def output_movies_to_console(films, rating):
    out = ('рейтингу кинопоиска', 'числу кинотеатров',)
    print('Популярные фильмы по {0} в городе Москва:'.format(out[rating]))
    for film_num, film in enumerate(films, 1):
        print('{0}) "{1}", рейтинг: {2}, голосов: {3}, число кинотеатров: {4}'
              .format(film_num, film[3], film[0], film[2], film[1]))


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    cinema_rating = namespace.r

    films_list = get_films_from_afisha_page()
    films = find_popular_films(films_list, cinema_rating)
    output_movies_to_console(films, cinema_rating)
