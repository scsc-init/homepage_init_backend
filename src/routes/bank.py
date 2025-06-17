from fastapi import APIRouter, HTTPException
import os
from datetime import datetime, timedelta, timezone
import httpx
import random

from src.model import BankingAccountDetails
from src.db import SessionDep

CLIENT_ID = os.getenv("OPENBANK_CLIENT_ID")
CLIENT_SECRET = os.getenv("OPENBANK_CLIENT_SECRET")
USERCODE=os.getenv("OPENBANK_USERCODE")
API_SECRET=os.getenv("API_SECRET")

bank_router = APIRouter(tags=['bank'])

# only the **president** should have permission for this
@bank_router.get("/api/bank/auth-url")
async def get_oauth_url():
    base_url = "https://testapi.openbanking.or.kr/oauth/2.0/authorize" # change later from testapi to openapi

    client_id = CLIENT_ID
    redirect_uri = "http://localhost:8080/bank/callback" # change host later, no api prefix for this
    scope = "login%20inquiry"
    state = ''.join([str(random.choice(range(10))) for _ in range(32)]) # random 32-byte
    auth_type = "0"

    query_string = (f"?response_type=code"f"&client_id={client_id}"f"&redirect_uri={redirect_uri}"f"&scope={scope}"f"&state={state}"f"&auth_type={auth_type}")

    url = base_url + query_string

    return {"auth_url": url}


# only accessible through callback
@bank_router.get("/bank/callback")
async def oauth_callback(code: str, scope: str, state: str, session: SessionDep):
    token_url = "https://testapi.openbanking.or.kr/oauth/2.0/token" # change from testapi to openapi later

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data={"code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": "http://localhost:8080/bank/callback", "grant_type": "authorization_code"})

    if response.status_code != 200 or response.json()["rsp_code"]:
        raise HTTPException(status_code=400, detail="token request failed")

    data = response.json()

    banking_data = BankingAccountDetails(
        id=1,
        access_token = data["access_token"],
        refresh_token = data["refresh_token"],
        user_seq_no = data["user_seq_no"],
        access_token_expire = datetime.now(timezone.utc) + timedelta(seconds=int(data["expires_in"])),
        scope = data["scope"]
    )
    
    session.add(banking_data)
    session.commit()

    return {"message": "token properly requested and saved to db"}



async def get_valid_access_token(session: SessionDep):
    data = session.get(BankingAccountDetails, 1)
    if not data: raise HTTPException(404, detail="deposit account not found")
    token = data.access_token
    fintech_use_num = data.fintech_use_num

    if data.access_token_expire > datetime.now():
        if fintech_use_num:
            return token, fintech_use_num
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://testapi.openbanking.or.kr/v2.0/user/me", headers={"Authorization": "Bearer "+token["access_token"]}, data={"user_seq_no": token["user_seq_no"]})
            
        if response.status_code != 200 or response.json()["rsp_code"]:
            raise HTTPException(status_code=404, detail="user data request failed")
        
        data.fintech_use_num = response.json()["res_list"][0]["fintech_use_num"]
        session.add(data)
        session.commit()
            
        return token, response.json()["res_list"][0]["fintech_use_num"]

    token_url = "https://testapi.openbanking.or.kr/oauth/2.0/token" # change from testapi to openapi later

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": data.refresh_token, "scope": "login inquiry", "grant_type": "refresh_token"})
    
    if response.status_code != 200 or response.json()["rsp_code"]:
        raise HTTPException(status_code=400, detail="token request failed")

    new_data = response.json()
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://testapi.openbanking.or.kr/v2.0/user/me", headers={"Authorization": "Bearer "+new_data["access_token"]}, data={"user_seq_no": new_data["user_seq_no"]})
        
    if response.status_code != 200 or response.json()["rsp_code"]:
        raise HTTPException(status_code=400, detail="user data request failed")
    
    data.fintech_use_num = response.json()["res_list"][0]["fintech_use_num"]
    session.add(data)
    
    banking_data = BankingAccountDetails(
        id=1,
        access_token = new_data["access_token"],
        refresh_token = new_data["refresh_token"],
        user_seq_no = new_data["user_seq_no"],
        access_token_expire = datetime.now(timezone.utc) + timedelta(seconds=int(new_data["expires_in"])),
        scope = new_data["scope"]
    )
    
    session.add(banking_data)
    session.commit()

    return new_data["access_token"], response.json()["res_list"][0]["fintech_use_num"]


@bank_router.get("/api/bank/inquiry")
async def get_user_payment(depositer: str, from_date: str, to_date: str, session: SessionDep):
    trx_url = "https://testapi.openbanking.or.kr/v2.0/account/transaction_list/fin_num"
    
    token, fintech_use_num = await get_valid_access_token()
    
    data = session.get(BankingAccountDetails, 1)
    if not data: raise HTTPException(404, detail="deposit account not found")
    
    if not data.tran_id_tail: data.tran_id_tail = 0
    data.tran_id_tail = (data.tran_id_tail + random.choice((1, 2, 3))) % 1000000000
    tran_id = str(USERCODE) + 'U' + f'{data.tran_id_tail:09}'
    session.add(data)
    session.commit()
    
    now = datetime.now()
    formatted_datetime = now.strftime("%Y%m%d%H%M%S")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(trx_url, headers= {"Authorization": "Bearer "+token}, data={"bank_tran_id": tran_id, "fintech_use_num": fintech_use_num, "inquiry_type": "I", "inquiry_base": "D", "from_date": from_date, "to_date": to_date, "sort_order": "D", "tran_dtime": formatted_datetime})
    
    if response.status_code != 200 or response.json()["rsp_code"]:
        raise HTTPException(status_code=400, detail="inquiry failed")
    
    for deposit_hist in response.json()["res_list"]:
        if deposit_hist["depositer"] == depositer:
            return {"trx_true": "true"}
    return {"trx_true": "false"}