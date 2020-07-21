# SWAMI KARUPPASWAMI THUNNAI

import time
import jwt
from functools import wraps
from flask import session, redirect
from database.get_connection import get_connection


def get_inventory_token(inventory_id,token_user, password):
    inventory_secret = "jeeva$kani*vichu&69_7#%%^"
    expiry = time.time() + 259200
    token = {"inventory_id": inventory_id,'token_user':token_user, "expiry": expiry}
    encoded_token = jwt.encode(token, key=password+inventory_secret)
    return encoded_token.decode("utf-8")


def inventory_token(_function):

  @wraps(_function)
  def wrapper_function(*args, **kwargs):
      if "inventory_token" not in session:
          return redirect("/contest")
      token = session["inventory_token"]
      try:
          decoded_token = jwt.decode(token, verify=False)
      except jwt.DecodeError:
          return redirect("/contest")
      admin_id = decoded_token["inventory_id"]
      expiry_time = decoded_token["expiry"]
      if time.time() > expiry_time:
          return redirect("/contest")
      try:
          connection = get_connection()
          cursor = connection.cursor()
          cursor.execute("SELECT password from customer_login where customer_login.id=%s limit 1", (admin_id ))
          result = cursor.fetchone()
          if result is None:
              return redirect("/contest")
          password_hash = result["password"]
      finally:
          cursor.close()
          connection.close()
      try:
          inventory_secret = "jeeva$kani*vichu&69_7#%%^"
          jwt.decode(token, key=password_hash+inventory_secret)
      except jwt.DecodeError:
          return redirect("/contest")
      return _function(*args, **kwargs)
  return wrapper_function

