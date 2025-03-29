from fastapi import FastAPI, Query, Path, HTTPException, status
from typing import Annotated
from app.db import engine, SessionDep
from app import models as md


myapp = FastAPI()


@myapp.on_event('startup')
def on_startup():
    md.create_db_and_tables(engine)


@myapp.get('/')
async def read_main():
    return {'msg': 'Hello World'}


@myapp.post('/api/v1/wallets/create',
            response_model=md.WalletPublic,
            status_code=status.HTTP_201_CREATED)
def create_wallet(wallet: md.WalletBase,
                  session: SessionDep):
    db_wallet = md.Wallet.model_validate(wallet)
    session.add(db_wallet)
    session.commit()
    session.refresh(db_wallet)
    return db_wallet


@myapp.get('/api/v1/wallets/{wallet_uuid}',
           response_model=md.WalletPublic,
           status_code=status.HTTP_200_OK)
def get_balance(wallet_uuid: Annotated[int, Path(title="ID нужного кошелька", ge=1)],
                session: SessionDep):
    wallet = session.get(md.Wallet, wallet_uuid)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Кошелек не найден')
    return wallet


@myapp.post('/api/v1/wallets/{wallet_uuid}/operation',
            response_model=md.WalletPublic,
            status_code=status.HTTP_202_ACCEPTED)
def change_balance(wallet_uuid: int,
                   filter_query: Annotated[md.FilterParams, Query()],
                   session: SessionDep):
    wallet_db = session.get(md.Wallet, wallet_uuid)
    if not wallet_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Кошелек не найден')
    wallet_data = wallet_db.model_dump()
    query_data = filter_query.model_dump()
    if query_data['operation_type'] == 'DEPOSIT':
        new_balance = wallet_data['balance'] + query_data['operation_sum']
    elif query_data['operation_type'] == 'WITHDRAW':
        new_balance = wallet_data['balance'] - query_data['operation_sum']
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Не выбран тип операции')
    wallet_db.sqlmodel_update({'id': wallet_uuid, 'balance': new_balance})
    session.add(wallet_db)
    session.commit()
    session.refresh(wallet_db)
    return wallet_db
