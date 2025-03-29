from fastapi.testclient import TestClient
from fastapi import status
from .main import myapp


client = TestClient(myapp)


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'msg': 'Hello World'}


def test_create_wallet():
    balance = 111
    response = client.post('/api/v1/wallets/create', json={'balance': balance})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['balance'] == balance


def test_create_invalid_balance_wallet():
    balance = -111
    response = client.post('/api/v1/wallets/create', json={'balance': balance})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail':
                               [{'type': 'greater_than_equal',
                                 "loc": ['body', 'balance'],
                                 'msg': 'Input should be greater than or equal to 0',
                                 'input': balance,
                                 'ctx': {'ge': 0}}
                                ]
                               }


def test_get_balance():
    # balance = 111
    wallet_uuid = 1
    # client.post('/api/v1/wallets/create', json={'balance': balance})
    response = client.get(f'/api/v1/wallets/{wallet_uuid}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == wallet_uuid


def test_get_invalid_id_balance():
    wallet_uuid = '-1'
    response = client.get(f'/api/v1/wallets/{wallet_uuid}')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {"detail":
                               [{'type': 'greater_than_equal',
                                 'loc': ["path", 'wallet_uuid'],
                                 'msg': 'Input should be greater than or equal to 1',
                                 'input': wallet_uuid,
                                 'ctx': {'ge': 1}}
                                ]
                               }


def test_get_nonexistent_wallet():
    wallet_uuid = 99999
    response = client.get(f'/api/v1/wallets/{wallet_uuid}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Кошелек не найден'}


def test_change_balance():
    wallet_uuid = 1
    balance = 555
    operation = 'DEPOSIT'
    url = (f'http://127.0.0.1:9000/api/v1/wallets/{wallet_uuid}/operation?'
           f'operation_type={operation}&operation_sum={balance}')
    response = client.post(url)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()['id'] == wallet_uuid


def test_change_nonexistent_balance():
    wallet_uuid = -1
    balance = 555
    operation = 'DEPOSIT'
    url = (f'http://127.0.0.1:9000/api/v1/wallets/{wallet_uuid}/operation?'
           f'operation_type={operation}&operation_sum={balance}')
    response = client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Кошелек не найден'}


def test_change_inalid_query_balance():
    wallet_uuid = 1
    balance = 555
    operation = ''
    url = (f'http://127.0.0.1:9000/api/v1/wallets/{wallet_uuid}/operation?'
           f'operation_sum={balance}')
    response = client.post(url)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail':
                               [{'input': {'operation_sum': str(balance)},
                                 'loc': ['query', 'operation_type'],
                                 'msg': 'Field required',
                                 'type': 'missing'}
                                ]}
    url = (f'http://127.0.0.1:9000/api/v1/wallets/{wallet_uuid}/operation?'
           f'operation_type={operation}&operation_sum={balance}')
    response = client.post(url)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail':
                               [{'ctx': {'expected': '\'DEPOSIT\' or \'WITHDRAW\''},
                                 'input': '',
                                 'loc': ['query', 'operation_type'],
                                 'msg': 'Input should be \'DEPOSIT\' or \'WITHDRAW\'',
                                 'type': 'literal_error'}
                                ]}
