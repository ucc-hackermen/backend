from distutils.command.config import config
from fastapi import FastAPI
from typing import Optional
from models import *
import firebase_admin
from firebase_admin import credentials, auth, firestore
import secrets


# initialize firebase
cred = credentials.Certificate("ucc-lost-and-found-firebase-adminsdk-9s9pv-d3a082fbc6.json")
firebase_app = firebase_admin.initialize_app(cred)
db = firestore.client(firebase_app)

app = FastAPI(title="UCC Lost and Found API", description="API for UCC Lost and Found", version="0.1.0")


# Definition of routes
# Login using firebase
@app.post("/login")
def login(user: User):
    print("Login")
    # check if user (email) is on firestore
    try:
        if(not user.email.endswith("ucc.edu.gh")):
            return {"data": "Only UCC students can use this app"}
        userInfo = auth.get_user_by_email(user.email, firebase_app)
        # find user by uid on firestore
        print(user.dict())
        user_dict = user.dict()
        user_ref = db.collection('Users').document(userInfo.uid)
        user_doc = user_ref.get()
        if(user_doc.exists):
            user_dict["email"] = user_doc.dict()["email"]
            user_dict["token"] = user_doc.dict()["token"]
        else:
            user_dict["token"] = secrets.token_urlsafe(16)
        user_ref.set(user_dict)
        return {"data": {"success": True, "message": "User logged in successfully", "token": user_dict["token"]}}
    except:
        print("User not found")
        pass


@app.get("/adverts")
def get_adverts():
    docs = db.collection('Adverts').stream()
    adverts = []
    for doc in docs:
        adverts.append(doc.to_dict())
    return {"data": adverts}


@app.post("/adverts")
def create_advert(advert: Advert):
    print(advert.dict())
    adt = advert.dict()
    adt['key'] = secrets.token_hex(16)
    userToken = adt['user']
    user_ref = db.collection('Users').where('token', '==', userToken).stream()
    for doc in user_ref:
        adt['user'] = doc.to_dict()
        db.collection('Adverts').add(adt)
        return {"data": {"success": True, "message": "Advert created successfully"}}
    return {"data": {"success": False, "message": "User not found"}}

@app.put("/adverts/{key}")
def update_advert(key: str, advert: Advert):
    print(advert.dict())
    adt = advert.dict()
    adverts = db.collection('Adverts').where('key', '==', key).stream()
    for doc in adverts:
        adt.pop("user")
        db.collection('Adverts').document(doc.id).set(adt, merge=True)
        return {"data": {"success": True, "message": "Advert updated successfully", "advert": adt}}
    return {"data": {"success": False, "message": "User not found"}}