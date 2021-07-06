import requests


def bot_hook(hook_url, content):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {'text': content, 'username': 'algospace'}
    print(hook_url, content)
    response = requests.post(hook_url, json=data, headers=headers)
    print(response.text)
    return response
