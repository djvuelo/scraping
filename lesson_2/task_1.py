import json
from bs4 import BeautifulSoup as soap
import requests
from os import path
import re
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/92.0.4515.159 Safari/537.36'
}
VACANCIES_DICT = {
    'name': [],
    'salary_from': [],
    'salary_to': [],
    'salary_valuta': [],
    'source': [],
    'link': []
}


def hh_areas():
    """hh.ru таблица гео"""
    if not path.exists('hh_cached_areas.json'):
        t = requests.get('https://hh.ru/shards/search_areas', headers=HEADERS)

        with open('hh_cached_areas.json', 'w', encoding='UTF-8') as hh_cached_areas:
            hh_cached_areas.write(json.dumps(t.json(), indent=4))

        return t.json()
    else:
        with open('hh_cached_areas.json', 'r', encoding='UTF-8') as hh_cached_areas:
            return json.loads("".join(hh_cached_areas))


def hh_search_page(vacancy_name, area=113, page=0):
    """hh.ru поиск вакансий
    :param vacancy_name: Название вакансии, должности или компании
    :param area: ID местоположения (default 113 - по всей России)
    :param page: сколько страниц будет просмотрено
    """
    hh = requests.Session()
    for i in range(0, page):

        params = {'fromSearchLine': 'true', 'area': area,
                  'st': 'searchVacancy', 'text': vacancy_name, 'page': i}
        t = hh.get('https://hh.ru/search/vacancy', params=params, headers=HEADERS)
        print(f"Страница {i} - статус: {t.status_code}")

        if not t.ok:
            break

        bs = soap(t.text, 'html.parser')
        vacancies = bs.find_all('div', class_='vacancy-serp-item')

        compensation_regex = re.compile(r'((?:[0-9 ]+\s0+))[\s]+–?((?:[а-я ]+))', re.IGNORECASE)

        for vacancy in vacancies:
            VACANCIES_DICT['name'].append(vacancy.find('a').text)
            VACANCIES_DICT['link'].append(vacancy.find('a').get('href'))
            compensation = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if compensation:
                compensation = compensation_regex.findall(compensation.text.replace('\u202f', ' '))
                if len(compensation) == 2:
                    VACANCIES_DICT['salary_from'].append(compensation[0][0].lstrip())
                    VACANCIES_DICT['salary_to'].append(compensation[1][0].lstrip())
                    VACANCIES_DICT['salary_valuta'].append(compensation[1][1].lstrip())
                else:
                    VACANCIES_DICT['salary_from'].append('-')
                    VACANCIES_DICT['salary_to'].append('-')
                    VACANCIES_DICT['salary_valuta'].append('-')
            else:
                VACANCIES_DICT['salary_from'].append('-')
                VACANCIES_DICT['salary_to'].append('-')
                VACANCIES_DICT['salary_valuta'].append('-')
            VACANCIES_DICT['source'].append('hh.ru')


def hh_questions():
    """Контрольные вопросы для выборки"""
    # выбор региона
    areas = hh_areas()
    area_letter = input('Введите букву с которой начинается Ваш город, республика или область(например: М или О):')
    for index, area in enumerate(areas[area_letter.upper()]):
        print(f"{index + 1}. {area['title']}")

    area_index = input('Введите цифру под которой подходящий для Вас субьект(например: 1 или 2):')
    area_id = areas[area_letter.upper()][int(area_index) - 1]['id']

    # выбор профессии
    prof = input('Введите профессию должность или компанию(например: Python или Сварщик):')
    page_count = input('Сколько страниц посмотреть?:')
    return prof, area_id, int(page_count)


if __name__ == '__main__':
    hh_search_page(*hh_questions())

    df = pd.DataFrame(data=VACANCIES_DICT)
    print(df)

    with open('pandas_output.csv', 'w', encoding='UTF-8') as pd_out:
        pd_out.write(df.to_csv(index=False))
