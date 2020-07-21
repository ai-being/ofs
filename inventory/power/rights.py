# SWAMI KARUPPASWAMI THUNNAI
import jwt
import hashlib
import datetime
dates=datetime.datetime.now()
date=dates.date()

from database.get_connection import get_connection
from flask import render_template, request, redirect, url_for, flash,session

salt='jeeva$kani*vichu&69'
salt=hashlib.sha512(salt.encode("utf-8")).hexdigest()

def rights():
    if ("inventory_token" not in session):
        return None
    else:
        token=session["inventory_token"]
        decoded_token=jwt.decode(token,verify=False)
        if ("inventory_id" not in decoded_token) | ("token_user" not in decoded_token):
            return None
        print(decoded_token)
        admin_id=decoded_token["inventory_id"]
        token_user=decoded_token["token_user"]

        username_hash=token_user
        
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute("SELECT id,username from customer_login where customer_login.id=%s",admin_id)
        right=cursor.fetchone()
        if right['username']==username_hash:
            return admin_id
        else:
            return None

def user_encryption(username):
    print(username)
    username=username+salt
    username_hash = hashlib.sha512(username.encode("utf-8")).hexdigest()
    username_hash=salt+username_hash+salt
    username_hash=  hashlib.sha512(username_hash.encode("utf-8")).hexdigest()
    print(username_hash)
    return username_hash

def password_encryption(password):
    print(password)
    password=password+salt
    password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
    password_hash=salt+password_hash+salt
    password_hash=  hashlib.sha512(password_hash.encode("utf-8")).hexdigest()
    print(password_hash)
    return password_hash