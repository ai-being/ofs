# SWAMI KARUPPASWAMI THUNNAI
import hashlib
from database.get_connection import get_connection
from flask import request, redirect, url_for, session
from inventory.power.rights import rights,user_encryption,password_encryption


def signup_value(salt):
    name=request.form['name']
    mobilenumber=request.form['mobilenumber']
    email=request.form['email']
    username=request.form['username']
    password=request.form['pass']
    repeat_pass=request.form['repeat_pass']

    connection=get_connection()
    cursor=connection.cursor()
    try:
        if password==repeat_pass:
            cursor.execute("SELECT * from customer_login where phone=%s and active=1",(mobilenumber))
            mobile_check=cursor.fetchone()

            cursor.execute("SELECT * from customer_login where email=%s and active=1",(email))
            email_check=cursor.fetchone()
            if mobile_check == None:
                if email_check == None:
                    username_hash=user_encryption(username)

                    password_hash=password_encryption(password)

                    #=====================================================================================
                                                            # [0-----Flase]
                                                            # [1------True]
                    #=====================================================================================
                    cursor.execute("SELECT * from customer_login where username=%s and active=1",(username_hash))
                    user_check=cursor.fetchone()

                    if user_check ==None:
                        cursor.execute("INSERT into customer_login Value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,email,mobilenumber,username_hash,password_hash,0,0,0,1,0,0,0,0))
                        connection.commit()
                        return 'Registered Successfully!'
                    else:
                        return 'Already username Registered'            
                else:
                    return 'Already email Registered'
            else:
                return 'Already mobile number Registered'
        else:
            return 'password mismatch'
    finally:
        cursor.close()
        connection.close()
    

def sign_update(salt):
    name=request.form['name']
    mobilenumber=request.form['mobilenumber']
    email=request.form['email']
    username=request.form['username']
    oldpass=request.form['oldpass']
    password=request.form['pass']
    repeat_pass=request.form['repeat_pass']
    connection=get_connection()
    cursor=connection.cursor()
    pass_change=request.form.get('pass_change')

    if pass_change == 'no':

        cursor.execute("SELECT * from customer_login where id=%s and password=%s and active=1",(rights(),password_encryption(oldpass)))
        customer_details=cursor.fetchone()


        if customer_details == None:
            return 'wrong password'
        else:
            password=oldpass
            repeat_pass=oldpass
    try:
        if password==repeat_pass:

            cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
            customer_details=cursor.fetchone()

            cursor.execute("SELECT * from customer_login where phone=%s and active=1 and id!=%s",(mobilenumber,rights()))
            mobile_check=cursor.fetchone()

            cursor.execute("SELECT * from customer_login where email=%s and active=1 and id!=%s",(email,rights()))
            email_check=cursor.fetchone()
            #===============================================================================================================================#
            #================================================================customer update============================================#
            if mobile_check == None:
                #================================================================email verification============================================#
                if email_check == None:

                    username_hash=user_encryption(username)

                    oldpassword_hash=password_encryption(oldpass)

                    password_hash=password_encryption(password)

                    #=====================================================================================
                                                            # [0-----Flase]
                                                            # [1------True]
                    #=====================================================================================
                    cursor.execute("SELECT * from customer_login where password=%s and active=1 and id=%s",(oldpassword_hash,rights()))
                    pass_check=cursor.fetchone()
                    #================================================================password verification============================================#
                    if pass_check != None: 
                        cursor.execute("SELECT * from customer_login where username=%s and active=1 and id!=%s",(username_hash,rights()))
                        user_check=cursor.fetchone()
                        #================================================================username verification verification============================================#
                        if user_check ==None:
                            #================================================================ verified customer check============================================#
                            if customer_details['mobile_verfication'] == 1 | customer_details['email_verification'] == 1 : 
                                #================================================================mobile nukber changing verification============================================#

                                cursor.execute("UPDATE customer_login set name=%s,password=%s where id=%s and active=1",(name,password_hash,rights()))
                                connection.commit()
                                return 'Update Successfully!'
                            else:

                                cursor.execute("UPDATE customer_login set name=%s,email=%s,phone=%s,password=%s where id=%s and active=1",(name,email,mobilenumber,password_hash,rights()))
                                connection.commit()

                                return 'Update Successfully!'
                        else:
                            return 'Already username Registered please change'
                    else:
                        return'password Wrong' 
                else:
                    return 'Already email Registered please change'
            else:   
                return 'Already mobile number Registered please change'
        else:
            return 'password mismatch'
    finally:
        cursor.close()
        connection.close()