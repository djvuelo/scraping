import requests
import json

'''Вывод списка и сохранение репозиториев у Linus Torvalds'''
url = 'https://api.github.com/users/torvalds/repos'
response = requests.get(url)
less_repos = []
if response.ok:
    repos = response.json()
    less_repos = [{'name': repo['name'], 'language': repo['language']} for repo in repos]
    with open('repos.json', 'w', encoding='UTF-8') as repos_file:
        repos_file.write(json.dumps(less_repos, indent=4))
