# SWAMI KARUPPASWAMI THUNNAI

# Author Name: Visweswaran N
# Email: visweswaran.nagasivam98@gmail.com
# Copyright (C): Visweswaran N
# Date: 11-02-2019

import requests


def send_sms(phone, message):
    """
    This function will send the sms to the phone number using MSG91 gateway

    :param phone: The phone number for which the message is to be sent.

    :param message: The content of the message.

    :return: True if the message is sent else will return False.
    """
    api_key = ""
    try:
        r = requests.get("http://api.msg91.com/api/sendhttp.php", params={
            "country": "91",
            "sender": "VISWES",
            "route": "4",
            "mobiles": phone,
            "authkey": api_key,
            "message": message
        })
        if r.status_code == 200:
            return True
        return False
    except Exception as e:
        return False
