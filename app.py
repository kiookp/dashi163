import requests


def get_verification_code():
    url = 'http://localhost:9988/api/find_verification_code'
    data = {
        'type': '1',
        'email': 'your_email_here'
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        verification_code = response.json().get('verification_code')
        if verification_code:
            print('Verification Code:', verification_code)
        else:
            print('No verification code found.')
    else:
        print('Failed to retrieve verification code:', response.status_code)


if __name__ == '__main__':
    get_verification_code()
