import hashlib
salt='jeeva$kani*vichu&69'
salt=hashlib.sha512(salt.encode("utf-8")).hexdigest()
username="kani"
password='HDFyNO'
username=username+salt
username_hash = hashlib.sha512(username.encode("utf-8")).hexdigest()
username_hash=salt+username_hash+salt
username_hash=  hashlib.sha512(username_hash.encode("utf-8")).hexdigest()
print(username_hash)


password=password+salt
password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
password_hash=salt+password_hash+salt
password_hash=  hashlib.sha512(password_hash.encode("utf-8")).hexdigest()
print(password_hash)