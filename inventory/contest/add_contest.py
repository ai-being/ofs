# SWAMI KARUPPASWAMI THUNNAI

from database.get_connection import get_connection
from flask import request, redirect, url_for, session


def save_contest(rights,today,title,companyname,description,reward_amount,total_participate,entry_fee,com_startdate,com_enddate,parti_enddate,status_code):

    try:
        connection=get_connection()
        cursor=connection.cursor()

        try:
            cursor.execute("INSERT into contest_add value('null',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s",(rights,today,title,companyname,description,reward_amount,total_participate,entry_fee,com_startdate,com_enddate,parti_enddate,status_code))
            connection.commit()
            return True
        except:
            return False

    finally:

        cursor.close()
        connection.close()
