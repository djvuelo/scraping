import requests
from requests.exceptions import (Timeout, ConnectionError,
                                 TooManyRedirects, InvalidSchema)
import json
import flask
from os import path
import uuid

"""
Получение моих видео, на которых я поставил лайк.
Использую OAuth2.0 Youtube.
API OAuth2.0 Youtube создано тестовое и пропускает только авторизацию
пользователя prfure@gmail.com.
Ответ от API сохранен в файл response_from_auth_api.json
"""

# данные flask приложения
app = flask.Flask(__name__)
DEBUG = True
CREDENTIALS_FILE = 'credentials.json'
RESPONSE_API_FILE = 'response_from_auth_api.json'

# данные приложения Youtube
CLIENT_ID = '960438879076-s4q7e8bn9r8fr44qee0fadbde3g25vup.apps.googleusercontent.com'
CLIENT_SECRET = 'X4P3IQByPNT7csybetiVXRqF'
SCOPE = 'https://www.googleapis.com/auth/youtube.readonly'
REDIRECT_URI = 'http://127.0.0.1:5000/oauth2callback'


def check_credentials():
    """Проверка ключа авторизации и если вышел срок то обновление"""
    credentials = None
    if not path.exists(CREDENTIALS_FILE):
        return flask.redirect(flask.url_for('oauth2callback'))
    with open(CREDENTIALS_FILE, 'r') as credentials_file:
        credentials = json.loads("".join(credentials_file.readlines()))
    if credentials['expires_in'] <= 0:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        return credentials


def youtube_api(method, params, headers):
    """Функция для работы с методами Youtube API"""
    try:
        response = requests.get(f'https://www.googleapis.com/youtube/v3/{method}', params=params, headers=headers)
        if response.ok:
            return {'success': True, 'response': response.json()}
        else:
            return {'success': False, 'response': response.json()}
    except (Timeout, ConnectionError, TooManyRedirects, InvalidSchema) as error:
        return {'success': False, 'response': error}


@app.route('/')
def index():
    """
    Проверяем авторизацию и запрашиваем все видео которые лайкнул пользователь.
    В данном случае я (prfure@gmail.com)
    """
    credentials = check_credentials()

    if type(credentials) == dict:
        headers = {'Authorization': 'Bearer {}'.format(credentials['access_token'])}
        response = youtube_api(method='videos', params={'myRating': 'like'}, headers=headers)
        if response['success']:
            # сохраняем ответ, а именно все видео которые я лайкнул
            with open(RESPONSE_API_FILE, 'w', encoding='UTF-8') as response_file:
                response_file.write(json.dumps(response, indent=4))

            return str(response)
        else:
            return str(response['response'])
    else:
        return credentials


@app.route('/oauth2callback')
def oauth2callback():
    """
    Авторизация Youtube по методу OAuth2.0
    """
    if 'code' not in flask.request.args:
        auth_uri = (f'https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                    f'&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}')
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        data = {'code': auth_code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'}
        r = requests.post('https://oauth2.googleapis.com/token', data=data)
        with open('credentials.json', 'w', encoding='UTF-8') as credentials_file:
            credentials_file.write(r.text)
        return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    """Точка входа приложения"""
    app.secret_key = str(uuid.uuid4())
    app.debug = False
    app.run(host='127.0.0.1', port=5000, debug=DEBUG)
