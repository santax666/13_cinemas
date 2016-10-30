
# Cinemas

Данный скрипт:
* получает список фильмов с [Афиши][], и количество кинотеатров, в которых идет фильм;
* для каждого фильма определяется рейтинг, а также количество оценок с сайта [Кинопоиска][];
* фильмы сортируются по рейтингу. Можно указать параметр -r, который будет показывать только фильмы, идущие в большом количестве кинотеатров (а значит, для них проще найти сеанс);
* выводит 10 самых популярных фильмов;
* можно указать город, для которого необходимо получить фильмы, через параметр -c.

* получение данных реализовано через API сайтов [Афиши][] и [Кинопоиска][]: применяется в официальных мобильных приложениях [Афиша — гид по развлечениям][] и [КиноПоиск][].

## Запуск

Введите в терминале:

    python3.5 cinemas.py
    python3.5 cinemas.py -r
    python3.5 cinemas.py -c Йошкар-Ола

## Зависимости

Скрипт написан на языке Python 3, поэтому требует его наличия.

Для выполнения HTTP-запросов должен быть установлен модуль [requests][].

Для обработки параметров в командной строке должен быть установлен модуль [argparse][].

Для получения сессионого ключа (для работы с API афиши)  должен быть установлен модуль [pyDes][].

Для работы с API кинопоиска (вычисление MD5-суммы, указание текущего времени у клиента) должен быть установлены модули [hashlib][] и [datetime][].

## Поддержка

Если у вас возникли сложности или вопросы по использованию скрипта, создайте 
[обсуждение][] в данном репозитории или напишите на электронную почту 
<IvanovVI87@gmail.com>.

## Документация

Документацию к модулю requests можно получить по [ссылке1][].

Документацию к модулю argparse можно получить по [ссылке2][].

Документацию к модулю pyDes можно получить по [ссылке3][].

Документацию к модулю hashlib можно получить по [ссылке4][].

Документацию к модулю datetime можно получить по [ссылке5][].


[Афиши]: http://www.afisha.ru/
[Кинопоиска]: https://www.kinopoisk.ru/
[Афиша — гид по развлечениям]: https://play.google.com/store/apps/details?id=ru.afisha.android&hl=ru
[КиноПоиск]: https://play.google.com/store/apps/details?id=ru.kinopoisk
[requests]: https://pypi.python.org/pypi/requests/2.11.1
[argparse]: https://pypi.python.org/pypi/argparse/1.4.0
[pyDes]: https://pypi.python.org/pypi/pyDes/
[hashlib]: https://pypi.python.org/pypi/hashlib/20081119
[datetime]: https://pypi.python.org/pypi/DateTime/4.1.1
[обсуждение]: https://github.com/santax666/13_cinemas/issues
[ссылке1]: http://docs.python-requests.org/en/master/
[ссылке2]: https://docs.python.org/3/library/argparse.html
[ссылке3]: http://twhiteman.netfirms.com/des.html
[ссылке4]: https://docs.python.org/3/library/hashlib.html
[ссылке5]: https://docs.python.org/3/library/datetime.html
