import requests
import json


def oauth_sign_in():
    url = 'https://accounts.google.com/o/oauth2/v2/auth'
    headers = {
        'apiKey': 'AIzaSyA-I2fU4g1JV-uigmYwWLR_JfTtCArD2hQ',
        'clientId': '960438879076-s4q7e8bn9r8fr44qee0fadbde3g25vup.apps.googleusercontent.com',
        'scope': 'https://www.googleapis.com/auth/youtube.force-ssl',
        'discoveryDocs': 'https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest'
    }
    params = {
        'client_id': 'X4P3IQByPNT7csybetiVXRqF',
        'access_type': 'offline',
        'response_type': 'token',
        'scope': 'https://www.googleapis.com/auth/youtube.readonly',
        'include_granted_scopes': 'true',
        'state': 'pass-through value'
    }
    response = requests.get(url, params=headers)
    print(response.text)

oauth_sign_in()