import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from schemas.users import UserModel

import firebase_admin
from firebase_admin import credentials, auth

import pyrebase
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    docs_url='/'
)


#Configure Firebase
if not firebase_admin._apps:    #If Firebase has not been initialized in this project
    cred = credentials.Certificate("firebaseKey.json")
    firebase_admin.initialize_app(cred)


firebaseConfig = {
  "apiKey": os.getenv('FIREBASE_API_KEY'),
  "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
  "projectId": os.getenv('FIREBASE_PROJECT_ID'),
  "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
  "messagingSenderId": os.getenv('FIREBASE_MESSAGING_ID'),
  "appId": os.getenv('FIREBASE_APP_ID'),
  "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID'),
  "databaseURL": ""   #Added manually since pyrebase will search for the key
};

firebase = pyrebase.initialize_app(
firebaseConfig
)


@app.post('/register')
async def register_user(data: UserModel):
    email = data.email
    password = data.password

    try:
        user = auth.create_user(
            email=email,
            password= password
        )

        return JSONResponse(
            content= {
                'message': "User registered successfully",
                'id': user.uid
            },
            status_code=201
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail=f"User with email {email} already exists")


@app.post('/login')
async def login_user(data: UserModel):
    email = data.email
    password = data.password

    try:
        signInAuth = firebase.auth()

        user = signInAuth.sign_in_with_email_and_password(
            email=email,
            password= password
        )

        token = user['idToken']

        return JSONResponse(
            content= {
                'token': token
            },
            status_code=200
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid credentials")



@app.post('/verify-token')
def verifyToken(request: Request):
    headers = request.headers
    token= headers.get('authorization')

    user = auth.verify_id_token(token)

    return {'user': user['user_id']}