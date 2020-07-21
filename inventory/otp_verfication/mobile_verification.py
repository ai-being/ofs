# SWAMI KARUPPASWAMI THUNNAI
import string
import random
from flask import Flask
from flask import render_template, request
from database.get_connection import get_connection

import requests

# email Verification
# from inventory.gmail_otp import gmail_otp

# rights
from inventory.power.rights import rights

def send_sms(phone, message):
    """
    This function will send the sms to the phone number using MSG91 gateway

    :param phone: The phone number for which the message is to be sent.

    :param message: The content of the message.

    :return: True if the message is sent else will return False.
    """
    api_key = "323534AjkWWancwy5e6f571bP1"
    try:
        r = requests.get("http://api.msg91.com/api/sendhttp.php", params={
            "country": "91",
            "sender": "kanitk",
            "route": "4",
            "mobiles": phone,
            "authkey": api_key,
            "message": message
        })
        print(r.status_code)
        if r.status_code == 200:
            return True
        return False
    except Exception as e:
        return False

def mobile_verfication():

    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
        customer_details=cursor.fetchone()
        phone=customer_details['duplicate_mobile']

        otp = list(string.digits)
        otp.remove('0')
        otp_text = ""
        for i in range(0, 5):
            otp_text += random.choice(otp)
            # print(otp_text)
        if (send_sms(phone, "OTP: {}".format(otp_text))) == True:
            cursor.execute("UPDATE customer_login set mobile_otp=%s where id=%s and active=1",(otp_text,rights()))
            connection.commit()
            return True
        else:
            return False
    except:
        return False
    finally:
        cursor.close()
        connection.close()


def otp_verification():
    otp = request.form["otp"]
    phone = request.form["phone"]

    connection=get_connection()
    cursor=connection.cursor()
    try:
        if int(otp)>0:

            cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
            customer_details=cursor.fetchone()

            if (customer_details['duplicate_mobile']== phone) & (str(customer_details['mobile_otp'])==otp):
                
                cursor.execute("UPDATE customer_login set mobile_verfication=1 ,mobile_otp=0,phone=%s where id=%s and active=1",(phone,rights()))
                connection.commit()
                
                return True
            else:
                return 'wrong'
        else:
            return False
    except:
        False
    finally:
        cursor.close()
        connection.close()

# def email_verfication():

#     connection=get_connection()
#     cursor=connection.cursor()
#     try:
#         cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
#         customer_details=cursor.fetchone()
#         email=customer_details['duplicate_email']

#         otp = list(string.digits)
#         otp.remove('0')
#         otp_text = ""
#         for i in range(0, 5):
#             otp_text += random.choice(otp)
#             # print(otp_text)
#         if (gmail_otp.A.send_mail(email, 'OTP Verification', "OTP: {}".format(otp_text))) == True:
#             cursor.execute("UPDATE customer_login set email_otp=%s where id=%s and active=1",(otp_text,rights()))
#             connection.commit()
#             return True
#         else:
#             return False
#     except:
#         return False
#     finally:
#         cursor.close()
#         connection.close()

# def otp_email_verification():
#     otp = request.form["otp_email"]
#     email = request.form["email"]

#     connection=get_connection()
#     cursor=connection.cursor()
#     try:
#         if int(otp)>0:
#             print('pass')
#             cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
#             customer_details=cursor.fetchone()

#             if (customer_details['duplicate_email']== email) & (str(customer_details['email_otp'])==otp):
#                 print('paass')
#                 cursor.execute("UPDATE customer_login set email_verification=1 ,email_otp=0,email=%s where id=%s and active=1",(email,rights()))
#                 connection.commit()
                
#                 return True
#             else:
#                 return 'wrong'
#         else:
#             return False
#     except:
#         False
#     finally:
#         cursor.close()
#         connection.close()