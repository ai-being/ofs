# SWAMI KARUPPASWAMI THUNNAI
from flask import send_file
from datetime import date, timedelta,datetime
import hashlib
from flask import request, redirect, url_for, session,flash
from flask import render_template
from flask import Blueprint
import jwt
import random
import string
from database.get_connection import get_connection
from inventory.token_validator import get_inventory_token, inventory_token
# signup & update
from inventory.signup.signup import signup_value,sign_update
# contest
from inventory.contest.add_contest import save_contest
# rights
from inventory.power.rights import rights,user_encryption,password_encryption
# Otp Verification
from inventory.otp_verfication.mobile_verification import mobile_verfication,otp_verification,send_sms

# bill info
from inventory.bill.bill_entry import bill_insert,purchase_adds
# email Verification
# from inventory.gmail_otp.gmail_otp import send_mail
#salt
salt='jeeva$kani*vichu&69'
salt=hashlib.sha512(salt.encode("utf-8")).hexdigest()
#===============================================================================# Starts #========================================  


inventory = Blueprint("inventory", __name__, url_prefix="/inventory")

today=date.today()



#===============================================================================# login template #========================================  
@inventory.route("/")
def render_login():

	if rights() != None:
			return render_template("inventory/dashboard.html")
	else:
		return render_template("inventory/login.html")

#===============================================================================# forgot password #========================================  
@inventory.route("/forget_password",methods=['POST','GET'])
def forget_password():

	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=='POST':
			phone=request.form['user_phone']
			username=user_encryption(phone)

			cursor.execute("SELECT * from customer_login where phone=%s and active=1",(phone))
			database_number=cursor.fetchone()

			if database_number == None:
				cursor.execute("SELECT * from customer_login where username=%s and active=1",(username))
				database_number=cursor.fetchone()

				if database_number == None:
					flash_message('Invaild mobile_number and password')
					return(redirect(url_for('inventory.render_login')))

			mobile_number=database_number['phone']

			temp_password=''.join([random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)for n in range(6)])
			message='New password:'+temp_password

			print(password_encryption(temp_password))

			if send_sms(mobile_number,message) == True:
				cursor.execute('UPDATE customer_login set password=%s where id=%s and active=1',(password_encryption(temp_password),database_number['id']))
				connection.commit()
				return redirect(url_for('inventory.render_login'))
			else:
				print('something wrong')

		else:
			return render_template("inventory/forget_password.html")

	finally:
		cursor.close()
		connection.close()

#===============================================================================# sign-up #========================================  

		
#===============================================================================# sign-up #========================================  
@inventory.route("/create_user", methods=["POST","GET"])
@inventory_token
def create_user():
	if request.method=='POST':

		flash_message = signup_value(salt)

		if flash_message == "Registered Successfully!":
			flash("Registered Successfully!")
			return redirect(url_for('inventory.render_login'))
		else:
			flash(flash_message)
			return redirect(url_for('inventory.create_user'))
	else:
		return render_template("inventory/signup.html")

@inventory.route("/signup", methods=["POST","GET"])
@inventory_token
def signup():
	try:
		connection=get_connection()
		cursor=connection.cursor()

		if rights() != None:
			if request.method=='POST':

				flash_message=sign_update(salt)
				print(flash_message)
				if flash_message == 'Update Successfully!':
					session.clear()
					flash('Update Successfully!')
					return redirect(url_for('inventory.render_login'))
				else:
					flash(flash_message)
					return redirect(url_for('inventory.signup'))
			else:
				cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
				customer_details=cursor.fetchone()
				
				return render_template("inventory/signup_update.html",customer_details=customer_details)
			
		else:
			return redirect(url_for('inventory.render_login'))
	except:
		return redirect(url_for('inventory.signup'))
	finally:
		cursor.close()
		connection.close()

#===============================================================================# login #========================================  


#===============================================================================# login #========================================  

@inventory.route("/login", methods=["POST"])
def login():

	connection = get_connection()
	cursor = connection.cursor()

	try:

		
		username = request.form["username"]
		password = request.form["pass"]

		username_hash=user_encryption(username)
		password_hash=password_encryption(password)

		

		cursor.execute("SELECT id from customer_login where username=%s and password=%s and active=1",(username_hash, password_hash))
		result = cursor.fetchone()

		if result is None:
			
			flash('Invaild username and password')
			return redirect(url_for("inventory.render_login"))

		session["inventory_token"] = get_inventory_token(result["id"],username_hash, password_hash)

		return redirect(url_for("inventory.dashboard"))
	except:
		return redirect(url_for("inventory.render_login"))
	finally:
		cursor.close()
		connection.close()

# #===============================================================================# dash board #========================================  

# @inventory.route("/dashboard", methods=["POST","GET"])
# @inventory_token
# def dashboard():
# 	if rights() != None:
# 		return render_template('inventory/dashboard.html')
# 	else:
# 		return redirect(url_for('inventory.render_login'))


#===============================================================================# logout #========================================  
@inventory.route("/logout", methods=["POST","GET"])
@inventory_token
def logout():
	session.clear()
	return redirect(url_for('inventory.render_login'))

#===============================================================================#===============================================================================
#===============================================================================# mobile_verification #========================================  
@inventory.route("/mobile_verify", methods=["POST","GET"])
@inventory_token
def mobile_verify():

	connection=get_connection()
	cursor=connection.cursor()
	try:
		cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
		customer_details=cursor.fetchone()
		
		if customer_details['mobile_verfication']==1:
			flash("Already Verified")
			return redirect(url_for('inventory.signup'))
		else:
			mobile_number=customer_details['phone']
			return render_template('inventory/mobile_verify.html',mobile_number=mobile_number,key='mobile_key')
	except:
		return redirect(url_for('inventory.signup'))
	finally:
		cursor.close()
		connection.close()
#===============================================================================# change number #========================================  		
@inventory.route("/change_number", methods=["POST","GET"])
@inventory_token
def change_number():

	connection=get_connection()
	cursor=connection.cursor()
	try:
		cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
		customer_details=cursor.fetchone()
		
		mobile_number=customer_details['phone']
		return render_template('inventory/mobile_verify.html',mobile_number=mobile_number,key='mobile_key')
	except:
		return redirect(url_for('inventory.signup'))
	finally:
		cursor.close()
		connection.close()


@inventory.route("/change_username", methods=["POST","GET"])
@inventory_token
def change_username():

	connection=get_connection()
	cursor=connection.cursor()
	try:

		if request.method=='POST':
			old_username=request.form['old_username']
			new_username=request.form['new_username']

			cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
			data_username=cursor.fetchone()
			cursor.execute("SELECT * from customer_login where username=%s and id!=%s and active=1",(user_encryption(new_username),rights()))
			username_check=cursor.fetchone()

			if username_check==None:

				if user_encryption(old_username)==data_username['username']:

					cursor.execute("UPDATE customer_login set username=%s where id=%s",(user_encryption(new_username),rights()))
					connection.commit()

					session.clear()
					flash('Update Successfully!')
					return redirect(url_for('inventory.render_login'))
				else:
					flash('old_username wrong!')
					return redirect(url_for('inventory.change_username'))
			else:
				flash('username Already Exist!')
				return redirect(url_for('inventory.change_username'))
		else:
			return render_template('/inventory/change_username.html')
	finally:
		cursor.close()
		connection.close()
#===============================================================================# otp stage1 #========================================  
@inventory.route("/verify", methods=["POST","GET"])
@inventory_token
def otp_verify():

	connection=get_connection()
	cursor=connection.cursor()
	try:
		cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
		customer_details=cursor.fetchone()

		
		mobile_number=request.form['phone']

		cursor.execute("SELECT phone from customer_login where phone=%s and id!=%s and active=1",(mobile_number,rights()))
		phone_check=cursor.fetchone()

		if phone_check == None:

			cursor.execute("UPDATE customer_login set duplicate_mobile=%s where id=%s and active=1",(mobile_number,rights()))
			connection.commit()
			
			if mobile_verfication()==True:
				return render_template("/inventory/otp.html", phone=mobile_number,key='mobile_key')
			else:
				return '<h1>oops try after soometimes</h1>'

		else:
			flash("Already mobile number Registered")
			return redirect(url_for("inventory.signup"))
	except:
		return redirect(url_for("inventory.signup"))
	finally:
		cursor.close()
		connection.close()
#===============================================================================# otp final state #========================================  
@inventory.route("/otp", methods=["POST","GET"])
@inventory_token
def otp():

	flash_message=otp_verification()
	if flash_message == True:
		flash('Verify Successfully!')
		return redirect(url_for("inventory.signup"))
	elif flash_message=='wrong':
		flash(flash_message)
		return redirect(url_for("inventory.otp_verify"))
	else:
		flash('Data mismach!')
		return redirect(url_for("inventory.signup"))

#===============================================================================# gmail verification #===============================================================================
@inventory.route("/gmail_verify", methods=["POST","GET"])
@inventory_token
def gmail_verify():

	connection=get_connection()
	cursor=connection.cursor()
	try:
		cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
		customer_details=cursor.fetchone()
		
		if customer_details['email_verification']==1:
			flash("Already Verified")
			return redirect(url_for('inventory.signup'))
		else:
			email=customer_details['email']
			return render_template('inventory/mobile_verify.html',email=email,key='email_key')
	except:
		return redirect(url_for('inventory.signup'))
	finally:
		cursor.close()
		connection.close()
#===============================================================================#===============================================================================
#===============================================================================# email otp stage1 #========================================  
@inventory.route("/emailverify", methods=["POST","GET"])
@inventory_token
def email_otp_verify():

	connection=get_connection()
	cursor=connection.cursor()
	try:
		cursor.execute("SELECT * from customer_login where id=%s and active=1",(rights()))
		customer_details=cursor.fetchone()

		
		email=request.form['email']

		cursor.execute("SELECT email from customer_login where email=%s and id!=%s and active=1",(email,rights()))
		email_check=cursor.fetchone()

		if email_check == None:

			cursor.execute("UPDATE customer_login set duplicate_email=%s where id=%s and active=1",(email,rights()))
			connection.commit()
			
			if email_verfication()==True:
				return render_template("/inventory/otp.html", email=email,key='email_key')
			else:
				return '<h1>oops try after soometimes</h1>'

		else:
			flash("Already mobile number Registered")
			return redirect(url_for("inventory.signup"))
	except:
		return redirect(url_for("inventory.signup"))
	finally:
		cursor.close()
		connection.close()

#===============================================================================# otp final state #========================================  
@inventory.route("/otp_email", methods=["POST","GET"])
@inventory_token
def otp_email():

	flash_message=otp_email_verification()
	if flash_message == True:
		flash('Verify Successfully!')
		return redirect(url_for("inventory.signup"))
	elif flash_message=='wrong':
		flash(flash_message)
		return redirect(url_for("inventory.email_otp_verify"))
	else:
		flash('Data mismach!')
		return redirect(url_for("inventory.signup"))


#===============================================================================# customer add #========================================  
@inventory.route("/customer_add", methods=["POST","GET"])
@inventory_token
def customer_add():
	
	if request.method=="POST":
		customer_name=request.form['customername']
		companyname=request.form['companyname']
		email=request.form['email']
		phonenumber=request.form['phonenumber']
		address=request.form['textarea-input']
		state=request.form['stt']
		city=request.form['city']
		town=request.form['town']
		gst=request.form['gst']
		dueperiod=request.form['dueperiod']

		try:
			connection=get_connection()
			cursor=connection.cursor()

			cursor.execute("INSERT into customer value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(today,customer_name,companyname,email,phonenumber,address,state,city,town,gst,dueperiod))
			connection.commit()

			return redirect(url_for("inventory.customer_add"))

		finally:

			cursor.close()
			connection.close()

	else:
		return render_template("inventory/customeradd.html")

# =============================================customer view================================#
@inventory.route("/customer_view/", methods=["POST","GET"])
@inventory_token
def customer_view():
	try:
		connection=get_connection()
		cursor=connection.cursor()
 
		cursor.execute("SELECT * from customer")
		customer_list=cursor.fetchall()

		return render_template("inventory/customer_list.html",customer_list=customer_list)	
	finally:
		cursor.close()
		connection.close()
	
# =============================================customer edit================================#
@inventory.route("/customer_edit/<int:customer_id>", methods=["POST","GET"])
@inventory_token
def customer_edit(customer_id):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=="POST":

			customer_name=request.form['customername']
			companyname=request.form['companyname']
			email=request.form['email']
			phonenumber=request.form['phonenumber']
			address=request.form['textarea-input']
			state=request.form['stt']
			city=request.form['city']
			town=request.form['town']
			gst=request.form['gst']
			dueperiod=request.form['dueperiod']

			cursor.execute("UPDATE customer set customername=%s,companyname=%s,email=%s,phone=%s,address=%s,state=%s,city=%s,town=%s,gst=%s,dueperiod=%s where id=%s",(customer_name,companyname,email,phonenumber,address,state,city,town,gst,dueperiod,customer_id))
			connection.commit()
			return redirect(url_for('inventory.customer_edit',customer_id=customer_id))

		else:
			cursor.execute("SELECT * from customer where id=%s",(customer_id))
			customer_list=cursor.fetchone()

			return render_template("inventory/customer_edit.html",customer_list=customer_list)	
	finally:
		cursor.close()
		connection.close()

# =============================================customer delete================================#
@inventory.route("/customer_delete/<int:customer_id>", methods=["POST","GET"])
@inventory_token
def customer_delete(customer_id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("DELETE from customer where id =%s",(customer_id))
		connection.commit()

		return redirect(url_for('inventory.customer_view'))
	finally:
		cursor.close()
		connection.close()


# =============================================vendor view================================#
@inventory.route("/vendor_view/", methods=["POST","GET"])
@inventory_token
def vendor_view():
	try:
		connection=get_connection()
		cursor=connection.cursor()
 
		cursor.execute("SELECT * from vendor")
		vendor_list=cursor.fetchall()

		return render_template("inventory/vendor_list.html",vendor_list=vendor_list)	
	finally:
		cursor.close()
		connection.close()
	
# =============================================vendor edit================================#
@inventory.route("/vendor_edit/<int:vendor_id>", methods=["POST","GET"])
@inventory_token
def vendor_edit(vendor_id):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=="POST":

			vendor_name=request.form['customername']
			companyname=request.form['companyname']
			email=request.form['email']
			phonenumber=request.form['phonenumber']
			address=request.form['textarea-input']
			state=request.form['stt']
			city=request.form['city']
			town=request.form['town']
			gst=request.form['gst']

			cursor.execute("UPDATE vendor set customername=%s,companyname=%s,email=%s,phone=%s,address=%s,state=%s,city=%s,town=%s,gst=%s where id=%s",(vendor_name,companyname,email,phonenumber,address,state,city,town,gst,vendor_id))
			connection.commit()
			return redirect(url_for('inventory.vendor_edit',vendor_id=vendor_id))

		else:
			cursor.execute("SELECT * from vendor where id=%s",(vendor_id))
			vendor_list=cursor.fetchone()

			return render_template("inventory/vendor_edit.html",vendor_list=vendor_list)	
	finally:
		cursor.close()
		connection.close()

#===============================================================================# vendor add #========================================  
@inventory.route("/vendor_add", methods=["POST","GET"])
@inventory_token
def vendor_add():
	
	if request.method=="POST":
		customer_name=request.form['customername']
		companyname=request.form['companyname']
		email=request.form['email']
		phonenumber=request.form['phonenumber']
		address=request.form['textarea-input']
		state=request.form['stt']
		city=request.form['city']
		town=request.form['town']
		gst=request.form['gst']

		try:

			connection=get_connection()
			cursor=connection.cursor()

			cursor.execute("INSERT into vendor value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(today,customer_name,companyname,email,phonenumber,address,state,city,town,gst))
			connection.commit()

			return redirect(url_for("inventory.vendor_add"))

		finally:

			cursor.close()
			connection.close()

	else:
		return render_template("inventory/vendoradd.html")

# =============================================vendor delete================================#
@inventory.route("/vendor_delete/<int:vendor_id>", methods=["POST","GET"])
@inventory_token
def vendor_delete(vendor_id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("DELETE from vendor where id =%s",(vendor_id))
		connection.commit()

		return redirect(url_for('inventory.vendor_view'))
	finally:
		cursor.close()
		connection.close()

#===============================================================================# product add #========================================  
@inventory.route("/product_add", methods=["POST","GET"])
@inventory_token
def product_add():

	try:

			connection=get_connection()
			cursor=connection.cursor()
	
			if request.method=="POST":
				code=request.form['productcode']
				name=request.form['productname']
				vendorname=request.form['vendorname']
				gst=request.form['gst']
				purchase_price=request.form['purchase_price']
				sellingprice=request.form['sellingprice']
				opening_stock=request.form['opening_stock']
				stock_alert=request.form.get('stockalert')
				unit=request.form['unit']
				

				cursor.execute("INSERT into product value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(today,code,name,vendorname,gst,purchase_price,sellingprice,opening_stock,opening_stock,stock_alert,unit))
				connection.commit()

				return redirect(url_for("inventory.product_add"))

				

			else:

				cursor.execute("SELECT * from vendor ")
				vendor_list=cursor.fetchall()

				cursor.execute("SELECT * from unit ")
				unit=cursor.fetchall()

				return render_template("inventory/productadd.html",vendor_list=vendor_list,unit=unit)
	finally:

					cursor.close()
					connection.close()



# =============================================product view================================#
@inventory.route("/product_view/", methods=["POST","GET"])
@inventory_token
def product_view():
	try:
		connection=get_connection()
		cursor=connection.cursor()
 
		cursor.execute("SELECT * from product")
		product_list=cursor.fetchall()

		return render_template("inventory/product_list.html",product_list=product_list)	
	finally:
		cursor.close()
		connection.close()
	
# =============================================product edit================================#
@inventory.route("/product_edit/<int:product_id>", methods=["POST","GET"])
@inventory_token
def product_edit(product_id):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=="POST":

			code=request.form['productcode']
			name=request.form['productname']
			vendorname=request.form['vendorname']
			gst=request.form['gst']
			purchase_price=request.form['purchase_price']
			sellingprice=request.form['sellingprice']
			opening_stock=request.form['opening_stock']
			stock_alert=request.form.get('stockalert')
			unit=request.form['unit']

			cursor.execute("SELECT * from product where id =%s",(product_id))
			product_view=cursor.fetchone()

			old_openingstock=product_view['opening_stock']
			old_stock=product_view['stock']
			new_stock=old_stock+(float(opening_stock)-old_openingstock)

			cursor.execute("UPDATE product set product_code=%s,product_name=%s,vendor_id=%s,gst=%s,purchase_price=%s,sales_price=%s,opening_stock=%s,stock=%s,stock_alert=%s,unit=%s where id=%s",(code,name,vendorname,gst,purchase_price,sellingprice,opening_stock,new_stock,stock_alert,unit,product_id))
			connection.commit()
			return redirect(url_for('inventory.product_edit',product_id=product_id))

		else:
			cursor.execute("SELECT * from product where id=%s",(product_id))
			product_list=cursor.fetchone()

			cursor.execute("SELECT * from vendor ")
			vendor_list=cursor.fetchall()

			cursor.execute("SELECT * from unit")
			unit=cursor.fetchall()

			return render_template("inventory/product_edit.html",product_list=product_list,vendor_list=vendor_list,unit=unit)	
	finally:
		cursor.close()
		connection.close()

# =============================================product delete================================#
@inventory.route("/product_delete/<int:product_id>", methods=["POST","GET"])
@inventory_token
def product_delete(product_id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("DELETE from product where id =%s",(product_id))
		connection.commit()

		return redirect(url_for('inventory.product_view'))
	finally:
		cursor.close()
		connection.close()

#===============================================================================# bill print #========================================  
@inventory.route("/bill_print/<int:customer_id>", methods=["POST","GET"])
@inventory_token
def bill_print(customer_id):

	try:

		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from bill where id=%s",(customer_id))
		bill=cursor.fetchone()

		cursor.execute("SELECT * from bill_info,product where product.id=bill_info.product_name and bill_info.invoice_no=%s",(bill['invoice_no']))
		bill_info=cursor.fetchall()

		if bill['customer_type']=='customer':
			cursor.execute("SELECT * from customer where id=%s",(bill['companyname']))
			company_name=cursor.fetchone()['companyname']
		else:
			company_name=bill['companyname']

		return render_template("inventory/billprint.html",company_name=company_name,bill=bill,bill_info=bill_info)
	finally:
		cursor.close()
		connection.close()
#===============================================================================# vendor add #========================================  
@inventory.route("/bill_add", methods=["POST","GET"])
@inventory_token
def bill_add():

	try:

			connection=get_connection()
			cursor=connection.cursor()
	
			if request.method=="POST":

				id=None
				customer_id=bill_insert(today,id)
				return redirect(url_for('inventory.bill_print',customer_id=customer_id))
				


				

			else:

				cursor.execute("SELECT * from customer ")
				customer_list=cursor.fetchall()

				cursor.execute("SELECT * from product ")
				product_list=cursor.fetchall()

				cursor.execute("SELECT * from unit ")
				unit=cursor.fetchall()

				cursor.execute("SELECT MAX(invoice_no) from bill where customer_type='customer' ")
				billno=cursor.fetchone()['MAX(invoice_no)']

				
				if billno == None:
					billno=1
				else:
					billno=int(billno)+1
				
				return render_template("inventory/billing.html",unit=unit,product_list=product_list,customer_list=customer_list,billno=billno,today=today)
	finally:

					cursor.close()
					connection.close()

# =============================================bill view================================#

@inventory.route("/bill_view/", methods=["POST","GET"])
@inventory_token
def bill_view():
	try:
		connection=get_connection()
		cursor=connection.cursor()
 		
		cursor.execute("SELECT bill.*,customer.companyname as company_name from bill,customer where bill.companyname=customer.id and customer_type='customer' ")
		bill_list=cursor.fetchall()

		return render_template("inventory/bill_list.html",bill_list=bill_list)	
	finally:
		cursor.close()
		connection.close()

# =============================================bill edit================================#
@inventory.route("/bill_edit/<int:bill_id>", methods=["POST","GET"])
@inventory_token
def bill_edit(bill_id):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=="POST":

			
			customer_id=bill_insert(today,id)
			return redirect(url_for('inventory.bill_print',customer_id=customer_id))

		else:
			cursor.execute("SELECT * from bill,payment_details where payment_details.type='bill' and payment_details.invoice_no=bill.invoice_no and payment_details.company_name=bill.companyname and bill.id=%s and bill.customer_type='customer' ",(bill_id))
			bill_list=cursor.fetchone()

			invoice_no=bill_list['invoice_no']

			cursor.execute("SELECT * from bill_info where bill_info.invoice_no=%s",(invoice_no))
			billinfo_list=cursor.fetchall()

			cursor.execute("SELECT * from customer ")
			customer_list=cursor.fetchall()

			cursor.execute("SELECT * from product ")
			product_list=cursor.fetchall()

			cursor.execute("SELECT * from unit ")
			unit=cursor.fetchall()

			return render_template("inventory/bill_edit.html",unit=unit,billinfo_list=billinfo_list,bill_list=bill_list,customer_list=customer_list,product_list=product_list)	
	finally:
		cursor.close()
		connection.close()
# =============================================bill edit================================#
@inventory.route("/bill_delete/<int:bill_id>", methods=["POST","GET"])
@inventory_token
def bill_delete(bill_id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from bill where id=%s",(bill_id))
		bill=cursor.fetchone()

		cursor.execute("SELECT * from bill_info where bill_info.invoice_no=%s",(bill['invoice_no']))
		bill_info=cursor.fetchall()


		if bill != None:
			cursor.execute("DELETE from bill where id=%s",(bill_id))
			connection.commit()
			cursor.execute("DELETE from payment_details where invoice_no=%s and company_name=%s and type='bill'",(bill['invoice_no'],bill['companyname']))
			cursor.execute("DELETE from payment_records where invoice_no=%s and company_name=%s and type='bill'",(bill['invoice_no'],bill['companyname']))
			connection.commit()

		if bill_info != None:

			for i in bill_info:

				cursor.execute("SELECT * from product where id=%s",(i['product_name']))
				product=cursor.fetchone()

				old_stock=float(product['stock'])
				qty=float(i['quantity'])

				new_stock=old_stock+qty

				cursor.execute("UPDATE product set stock=%s where id=%s ",(new_stock,i['product_name']))
				connection.commit()

			cursor.execute("DELETE from bill_info where invoice_no=%s",(bill['invoice_no']))
			connection.commit()

		return redirect(url_for("inventory.bill_view"))
	finally:
		cursor.close()
		connection.close()


# # =============================================purchase add================================#
@inventory.route("/purchase_add", methods=["POST","GET"])
@inventory_token
def purchase_add():

	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from unit ")
		unit=cursor.fetchall()

		cursor.execute("SELECT * from product ")
		material=cursor.fetchall()

		cursor.execute("SELECT * from vendor ")
		suppiler_venname=cursor.fetchall()

		cursor.execute("SELECT MAX(bill_no) from purchase_head")
		purchase_head = cursor.fetchone()

		bill_no=purchase_head["MAX(bill_no)"]

		if bill_no == None:
			bill_no=1
		else:
			bill_no=int(bill_no)+1

		id=0
		return render_template("inventory/purchase_add.html",today=today,bill_no=bill_no,suppiler_venname=suppiler_venname,unit=unit,id=id,material=material)
	finally:
		cursor.close()
		connection.close()

#------------------------------------purchase---------------------------#

@inventory.route("/purchase_entry",methods=["POST","GET"])
@inventory_token
def purchase_entry():
    

	connection = get_connection()
	cursor = connection.cursor()

	# cursor.execute("SELECT * from purchase_head")
	# purchase_head=cursor.fetchall()
	try:
		connection=get_connection()
		cursor=connection.cursor()

		id=0

		purchase_check=purchase_adds(id)
		print(purchase_check)
		if purchase_check == 'True':
			return redirect(url_for('inventory.purchase_add'))


	finally:
		cursor.close()
		connection.close()


@inventory.route("/purchase_view/",methods=["POST","GET"])
@inventory_token
def purchase_view():

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * from purchase_head ")
        purchase=cursor.fetchall()
        
        return render_template('inventory/purchase_view.html',purchase=purchase)
       

    finally:
       cursor.close()
       connection.close()

@inventory.route("/purchase_edit/<int:purchase_id>",methods=["POST","GET"])
@inventory_token
def purchase_edit(purchase_id):

	connection = get_connection()
	cursor = connection.cursor()

	try:

		cursor.execute("SELECT * from purchase_head,payment_details where payment_details.type='purchase' and payment_details.invoice_no=purchase_head.bill_no  and purchase_head.id=%s",(purchase_id))
		detail_head=cursor.fetchone()

		cursor.execute("SELECT * from purchase_body where purchase_body.bill_no=%s",(detail_head['bill_no']))
		detail_body=cursor.fetchall()

		cursor.execute("SELECT * from vendor")
		suppiler_venname=cursor.fetchall()

		cursor.execute("SELECT * from unit")
		unit=cursor.fetchall()

		cursor.execute("SELECT * from product")
		material=cursor.fetchall()


		id=purchase_id

		return render_template("inventory/purchase_edit.html",detail_head=detail_head,detail_body=detail_body,suppiler_venname=suppiler_venname,unit=unit,material=material)

	finally:
		cursor.close()
		connection.close()

@inventory.route("/purchase_saveedit/<int:purchase_id>",methods=["POST","GET"])
@inventory_token
def purchase_saveedit(purchase_id):

	if request.method=="POST":

		try:
			connection=get_connection()
			cursor=connection.cursor()

			id=purchase_id

			purchase_check=purchase_adds(id)
			print(purchase_check)
			if purchase_check == 'True':
				return redirect(url_for("inventory.purchase_edit",purchase_id=purchase_id))


		finally:
			cursor.close()
			connection.close()
	return redirect(url_for("inventory.purchase_edit",purchase_id=purchase_id))

@inventory.route("/purchase_delete/<int:purchase_id>",methods=["POST","GET"])
@inventory_token
def purchase_delete(purchase_id):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from purchase_head,vendor where vendor.customername=purchase_head.suppiler_name and purchase_head.id=%s",(purchase_id))
		p_head=cursor.fetchone()	

		cursor.execute("SELECT * from purchase_body where bill_no=%s",(p_head['bill_no']))
		p_body=cursor.fetchall()

		cursor.execute("DELETE from payment_details where invoice_no=%s and company_name=%s and type='purchase' ",(p_head['bill_no'],p_head['vendor.companyname']))
		cursor.execute("DELETE from payment_records where invoice_no=%s and company_name=%s and type='purchase'",(p_head['bill_no'],p_head['vendor.companyname']))
		connection.commit()

		for i in p_body:

			cursor.execute("SELECT * from product where id=%s",(i['item']))
			product=cursor.fetchone()

			oldstock=float(product['stock'])

			newstock=oldstock-float(i['qty'])

			cursor.execute("UPDATE product set stock=%s where id=%s",(newstock,product['id']))
			connection.commit()

		cursor.execute("DELETE from purchase_head where id=%s",(purchase_id))
		cursor.execute("DELETE from purchase_body where bill_no=%s",(p_head['bill_no']))
		connection.commit()
		return redirect(url_for("inventory.purchase_view"))

	finally:
		cursor.close()
		connection.close()
# ===================================================== unit group ============================== #
@inventory.route("/unit_add", methods=["POST","GET"])
@inventory_token
def unit_add():

    name=request.form['name']
    print(name)
    try:
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute("insert into unit value (%s,%s)",(name,name))
        connection.commit()
        return redirect(url_for('inventory.unit'))
    
    finally:
        cursor.close()
        connection.close()



@inventory.route("/unit", methods=["POST","GET"])
@inventory_token
def unit():
    id = request.args.get("id")
    print(id)
    add=request.form.get('updateitem')
    print(add)
    if id != None:
        if 'delete' == request.form.get('delete') :
            
            connection=get_connection()
            cursor=connection.cursor()
            cursor.execute("DELETE from unit where id=%s",(id))
            unit=connection.commit()
            
            return redirect(url_for("inventory.unit"))
            

        elif 'add' == request.form.get('add'):   
            
            return render_template("inventory/unit_add.html",id=id)
            
            
        elif 'update item' == request.form.get('updateitem'):

            
            update_item=request.form['unit_name']
            print(update_item)
            connection=get_connection()
            cursor=connection.cursor()
            cursor.execute("update unit set id=%s,unit=%s where id=%s",(update_item,update_item,id))
            connection.commit()
            print('update')
            
            return redirect(url_for("inventory.unit"))
            
        else:
            
            try:
                connection=get_connection()
                cursor=connection.cursor()
                cursor.execute("select unit.* from unit")
                unit=cursor.fetchall()
                print(unit)
                return render_template("inventory/unit.html",unit=unit)
            finally:
                cursor.close()
                connection.close()
            return render_template("inventory/unit.html")
            

    else:
        
        try:
            connection=get_connection()
            cursor=connection.cursor()
            cursor.execute("select unit.* from unit")
            unit=cursor.fetchall()
            print(unit)
            return render_template("inventory/unit.html",unit=unit)
        finally:
            cursor.close()
            connection.close()
        return render_template("inventory/unit.html")

# =============================================================# payment #================================================
@inventory.route("/payment_add", methods=["POST","GET"])
@inventory_token
def payment_add():

	try:

		connection=get_connection()
		cursor=connection.cursor()

		if request.method=='POST':

			company_name=request.form['company_name']
			return redirect("/inventory/payment_link?id={}".format(int(company_name)))
			
		else:
			cursor.execute("SELECT payment_details.*,customer.*,customer.customername as cmp from payment_details,customer where customer.id=payment_details.company_name and payment_details.type='bill'")
			payment_details=cursor.fetchall()

			cursor.execute("SELECT * from customer")
			customerdetails=cursor.fetchall()

		return render_template('inventory/payment.html',payment_details=payment_details,customerdetails=customerdetails)


	finally:
		cursor.close()
		connection.close()

# =============================================================# payment #================================================
@inventory.route("/payment_link", methods=["POST","GET"])
@inventory_token
def payment_link():

	try:
		
		connection=get_connection()
		cursor=connection.cursor()

		company_name=request.args.get('id')

		cursor.execute("SELECT *,customer.companyname as cmp from customer,payment_details where customer.id=payment_details.company_name and payment_details.type='bill' and payment_details.company_name=%s",(company_name))
		payment_details=cursor.fetchall()
		
		cursor.execute("SELECT * from payment_records where type='bill' and company_name=%s",(company_name))
		payment_records=cursor.fetchall()

		cursor.execute("SELECT * from customer")
		customerdetails=cursor.fetchall()

		cursor.execute("SELECT * from bank_details")
		bankdetails=cursor.fetchall()

		key='bill'
		return render_template('inventory/payment.html',bankdetails=bankdetails,payment_records=payment_records,key=key,payment_details=payment_details,customerdetails=customerdetails,company_name=company_name)

	finally:
		cursor.close()
		connection.close()

#
# =============================================================# payment_entry #================================================
@inventory.route("/payment_entry", methods=["POST","GET"])
@inventory_token
def payment_entry():

	try:

		connection=get_connection()
		cursor=connection.cursor()
		# print(request.method)
		
		bill=request.form.getlist('bill_no')
		
		if bill == []:
			return redirect("/inventory/payment_add")
		else:

			bankcharges=request.form['bankcharges']
			paydate=request.form['paydate']
			cheque=request.form['cheque']
			paymode=request.form['paymode']
			depositto=request.form['depositto']
			reference=request.form['reference']
			notes=request.form['notes']
			poupload=request.form['poupload']
			paystatus=request.form['paystatus']
			company_name=request.form['company_name']

			receipt=[]

			for i in bill:
				invoice_no=request.form['invoicenumber_'+str(i)]
				companyname=request.form['company_name_'+str(i)]
				amount=request.form['amountreceive_'+str(i)]
				cd=request.form['cd_'+str(i)]

				#  payment
				cursor.execute("SELECT * from payment_details where invoice_no=%s",(invoice_no))
				payment_details=cursor.fetchone()

				total=payment_details['total_amount']
				paid_amount=payment_details['paid_amount']
				balance_amount=payment_details['balance_amount']
				fine_amount=payment_details['fine_amount']

				activeyes=0
				activeno=1


		        #==============================================#
		        #       active 0 == Not completed              #
		        #       active 1 == paid                       #
		        #==============================================#
				
				if paystatus=='paid':
					detail='amount'
					status_record='paid'

					if float(amount) > 0:

						new_paid_amount=float(paid_amount)+float(amount)

						new_balance_amount=float(total)-float(new_paid_amount)
						# print(new_balance_amount)
						if new_balance_amount == 0:
		
							active=activeno
							status='payment completed!'
						else:
							active=activeyes
							status='payment not completed!'


						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,amount,'null',activeno,'bill'))
						lastrow_id=cursor.lastrowid
						receipt.append(lastrow_id)
						cursor.execute("UPDATE payment_details set status=%s,paid_amount=%s,balance_amount=%s,active_status=%s where invoice_no=%s",(status,new_paid_amount,new_balance_amount,active,invoice_no))

						connection.commit()

					if float(cd)>0:

						detail='cash discount'
						status_record='paid'

						new_paid_amount=float(paid_amount)+float(cd)

						new_balance_amount=float(total)-float(new_paid_amount)

						if new_balance_amount == 0:
							active=activeno
							status='payment completed!'
						else:
							active=activeyes
							status='payment not completed!'

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'bill'))
						lastrow_id=cursor.lastrowid
						receipt.append(lastrow_id)
						cursor.execute("UPDATE payment_details set paid_amount=%s,balance_amount=%s,active_status=%s where invoice_no=%s",(new_paid_amount,new_balance_amount,active,invoice_no))

						connection.commit()

					if float(bankcharges)>0:

						print('fine')
						detail='fine amount'
						status_record='paid'

						new_balance_amount=float(balance_amount)+float(bankcharges)
						new_total=float(total)+float(bankcharges)
						new_fineamount=float(fine_amount)+float(bankcharges)

						print(new_balance_amount)
						print(new_total)
						if float(balance_amount) == 0:
							active=activeno
							status='payment completed!'
						else:
							active=activeyes
							status='payment not completed!'
						
						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'bill'))
						lastrow_id=cursor.lastrowid
						receipt.append(lastrow_id)
						cursor.execute("UPDATE payment_details set total_amount=%s,balance_amount=%s,fine_amount=%s,active_status=%s where invoice_no=%s",(new_total,new_balance_amount,new_fineamount,active,invoice_no))

						connection.commit()

				else:
					detail='amount'
					status_record='waiting'

					if float(amount) > 0:

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,amount,'null',activeyes,'bill'))
						lastrow_id=cursor.lastrowid
						receipt.append(lastrow_id)
						connection.commit()

					if float(cd)>0:

						detail='cash discount'
						status_record='waiting'

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'bill'))
						lastrow_id=cursor.lastrowid
						receipt.append(lastrow_id)
						connection.commit()

					if float(bankcharges)>0:

						detail='fine amount'
						status_record='waiting'

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'bill'))
						lastrow_id=cursor.lastrowid
						receipt.append(lastrow_id)
						connection.commit()

		        #==============================================#
		        #       active 0 == Not completed              #
		        #       active 1 == paid                       #
		        #==============================================#

			print(receipt)	
			receipt_data=[]
			for r in receipt:
				cursor.execute("SELECT * from payment_records where id=%s",(r))
				payment_records=cursor.fetchone()
				
				cursor.execute("SELECT * from payment_details,customer where customer.id = payment_details.company_name and payment_details.invoice_no=%s and payment_details.type='bill'",(int(payment_records['invoice_no'])))
				payment_details=cursor.fetchone()
				
				if int(payment_records['invoice_no'])==int(payment_details['invoice_no']):
					pay_id=r
					date=payment_records['date']
					company_name=payment_details['company_name']
					address=payment_details['address']
					phonenumber=payment_details['phone']
					email=payment_details['email']
					gst_number=payment_details['gst']
					payment_mode=payment_records['payment_mode']
					status=payment_records['status']
					amount=payment_records['paid_amount']
					cheque_date=payment_records['check_date']

					receipt_data.append([pay_id,date,company_name,address,phonenumber,email,gst_number,payment_mode,status,amount,cheque])
			return render_template("inventory/payment_recepit.html",receipt_data=receipt_data)
				# payment_recepit.html
			# return redirect("/inventory/payment_link?id={}".format(int(company_name)))
			# return redirect("/inventory/payment_link?id={}".format(int(payment_add())))

	finally:
		cursor.close()
		connection.close()
# ======================================================= more bill view========================
@inventory.route("/more_billview/<int:bill_no>", methods=["POST","GET"])
@inventory_token
def more_billview(bill_no):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from payment_records where type='bill' and invoice_no=%s",(bill_no))
		payment_records=cursor.fetchall()

		return render_template('inventory/more_billview.html',payment_records=payment_records)
	finally:
		cursor.close()
		connection.close()
#=========================================================# payment record #==========================
@inventory.route("/payment_record_edit", methods=["POST","GET"])
@inventory_token
def payment_record_edit():

	try:
		connection=get_connection()
		cursor=connection.cursor()
	

		id=request.args.get('id')
		cursor.execute("SELECT * from payment_records where payment_records.type='bill' and id =%s",(id))
		payment_records=cursor.fetchone()
		cursor.execute("SELECT * from payment_details where invoice_no=%s and type='bill'",(payment_records['invoice_no']))
		payment_details=cursor.fetchone()

		company_name=payment_details['company_name']
		paid=payment_records['paid_amount']
		total_amount=payment_details['total_amount']
		paid_amount=payment_details['paid_amount']
		balance_amount=payment_details['balance_amount']
		fine_amount=payment_details['fine_amount']

		if request.form.get('delete')=='delete':

			if payment_records['active_status']==1:

				if payment_records['status']=='fine amount':

					new_total=float(total_amount)-float(paid)
					new_balance_amount=float(balance_amount)-float(paid)

					new_fineamount=float(fine_amount)-float(paid)
					cursor.execute("UPDATE payment_details set total_amount=%s,balance_amount=%s,fine_amount=%s where invoice_no=%s and type='bill'",(new_total,new_balance_amount,new_fineamount,payment_records['invoice_no']))
					cursor.execute("DELETE from payment_records where id =%s",(id))
					connection.commit()
				else:
					new_paid_amount=float(paid_amount)-float(paid)
					new_balance_amount=float(balance_amount)+float(paid)

					cursor.execute("UPDATE payment_details set paid_amount=%s,balance_amount=%s where invoice_no=%s and type='bill'",(new_paid_amount,new_balance_amount,payment_records['invoice_no']))
					cursor.execute("DELETE from payment_records where id =%s",(id))
					connection.commit()
			# active= waiting delete
			else:
					cursor.execute("DELETE from payment_records where id=%s",(id))
					connection.commit()

		if request.form.get('paid')=='paid':

			if payment_records['active_status']==0:

				if payment_records['status']=='fine amount':

					new_total=float(total_amount)+float(paid)
					new_balance_amount=float(balance_amount)+float(paid)

					new_fineamount=float(fine_amount)+float(paid)
					cursor.execute("UPDATE payment_details set total_amount=%s,balance_amount=%s,fine_amount=%s where invoice_no=%s and type='bill'",(new_total,new_balance_amount,new_fineamount,payment_records['invoice_no']))
					cursor.execute("UPDATE payment_records set active_status=1,status='paid' where id =%s",(id))
					connection.commit()
				else:
					new_paid_amount=float(paid_amount)+float(paid)
					new_balance_amount=float(balance_amount)-float(paid)

					cursor.execute("UPDATE payment_details set paid_amount=%s,balance_amount=%s where invoice_no=%s and type='bill'",(new_paid_amount,new_balance_amount,payment_records['invoice_no']))
					cursor.execute("UPDATE payment_records set active_status=1,status='paid' where id =%s",(id))
					connection.commit()
			# active= waiting delete
			
			

		if request.form.get('cancel')=='cancel':

			if payment_records['active_status']==0:

				if payment_records['status']=='fine amount':

					cursor.execute("UPDATE payment_records set active_status=2,status='cancelled' where id =%s",(id))
					connection.commit()
				else:
					
					cursor.execute("UPDATE payment_records set active_status=2,status='cancelled' where id =%s",(id))
					connection.commit()
			# active= waiting delete
		return redirect(url_for("inventory.more_billview",bill_no=payment_records['invoice_no']))
	finally:
		cursor.close()
		connection.close()

# =============================================================# purchase paymnet #================================================
@inventory.route("/purchase_payment", methods=["POST","GET"])
@inventory_token
def purchase_payment():

	try:

		connection=get_connection()
		cursor=connection.cursor()

		if request.method=='POST':
			
			company_name=request.form['company_name']
			return redirect("/inventory/purchase_payment_link?id={}".format((company_name)))
			
		else:
			
			cursor.execute("SELECT *,payment_details.company_name as cmp from payment_details where type='purchase'")
			payment_details=cursor.fetchall()

			cursor.execute("SELECT * from vendor")
			customerdetails=cursor.fetchall()
			
			cursor.execute("SELECT * from bank_details")
			bankdetails=cursor.fetchall()

		return render_template('inventory/purchase_payment.html',payment_details=payment_details,customerdetails=customerdetails,bankdetails=bankdetails)


	finally:
		cursor.close()
		connection.close()
# =============================================================# purchasepayment #================================================
@inventory.route("/purchase_payment_link", methods=["POST","GET"])
@inventory_token
def purchase_payment_link():

	try:
		
		connection=get_connection()
		cursor=connection.cursor()

		company_name=request.args.get('id')
		print(company_name)
		cursor.execute("SELECT *,vendor.companyname as cmp from vendor,payment_details where vendor.companyname=payment_details.company_name and payment_details.type='purchase' and payment_details.company_name=%s",(company_name))
		payment_details=cursor.fetchall()
		
		cursor.execute("SELECT * from vendor")
		customerdetails=cursor.fetchall()

		cursor.execute("SELECT * from payment_records where type='purchase' and company_name=%s",(company_name))
		payment_records=cursor.fetchall()

		cursor.execute("SELECT * from bank_details")
		bankdetails=cursor.fetchall()

		key='purchase'
		return render_template('inventory/purchase_payment.html',bankdetails=bankdetails,payment_records=payment_records,key=key,payment_details=payment_details,customerdetails=customerdetails,company_name=company_name)

	finally:
		cursor.close()
		connection.close()

 # =============================================================# purchase_payment_entry #================================================
@inventory.route("/purchase_payment_entry", methods=["POST","GET"])
@inventory_token
def purchase_payment_entry():

	try:

		connection=get_connection()
		cursor=connection.cursor()

		bill=request.form.getlist('bill_no')
		print(bill)
		if bill == []:
			return redirect("/inventory/purchase_payment")
		else:

			bankcharges=request.form['bankcharges']
			paydate=request.form['paydate']
			cheque=request.form['cheque']
			paymode=request.form['paymode']
			depositto=request.form['depositto']
			reference=request.form['reference']
			notes=request.form['notes']
			poupload=request.form['poupload']
			paystatus=request.form['paystatus']
			company_name=request.form['company_name']
			for i in bill:
				invoice_no=request.form['invoicenumber_'+str(i)]
				companyname=request.form['company_name_'+str(i)]
				amount=request.form['amountreceive_'+str(i)]
				cd=request.form['cd_'+str(i)]

				#  payment
				cursor.execute("SELECT * from payment_details where invoice_no=%s",(invoice_no))
				payment_details=cursor.fetchone()

				total=payment_details['total_amount']
				paid_amount=payment_details['paid_amount']
				balance_amount=payment_details['balance_amount']
				fine_amount=payment_details['fine_amount']

				activeyes=0
				activeno=1


		        #==============================================#
		        #       active 0 == Not completed              #
		        #       active 1 == paid                       #
		        #==============================================#
				
				if paystatus=='paid':
					detail='amount'
					status_record='paid'

					if float(amount) > 0:

						new_paid_amount=float(paid_amount)+float(amount)

						new_balance_amount=float(total)-float(new_paid_amount)
						print(new_balance_amount)
						if new_balance_amount == 0:
		
							active=activeno
							status='payment completed!'
						else:
							active=activeyes
							status='payment not completed!'


						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,amount,'null',activeno,'purchase'))
						cursor.execute("UPDATE payment_details set status=%s,paid_amount=%s,balance_amount=%s,active_status=%s where invoice_no=%s",(status,new_paid_amount,new_balance_amount,active,invoice_no))

						connection.commit()

					if float(cd)>0:

						detail='cash discount'
						status_record='paid'

						new_paid_amount=float(paid_amount)+float(cd)

						new_balance_amount=float(total)-float(new_paid_amount)

						if new_balance_amount == 0:
							active=activeno
							status='payment completed!'
						else:
							active=activeyes
							status='payment not completed!'

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'purchase'))
						cursor.execute("UPDATE payment_details set paid_amount=%s,balance_amount=%s,active_status=%s where invoice_no=%s",(new_paid_amount,new_balance_amount,active,invoice_no))

						connection.commit()

					if float(bankcharges)>0:

						print('fine')
						detail='fine amount'
						status_record='paid'

						new_balance_amount=float(balance_amount)+float(bankcharges)
						new_total=float(total)+float(bankcharges)
						new_fineamount=float(fine_amount)+float(bankcharges)

						print(new_balance_amount)
						print(new_total)
						if float(balance_amount) == 0:
							active=activeno
							status='payment completed!'
						else:
							active=activeyes
							status='payment not completed!'
						print('fine2')
						print(status)
						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'purchase'))
						cursor.execute("UPDATE payment_details set total_amount=%s,balance_amount=%s,fine_amount=%s,active_status=%s where invoice_no=%s",(new_total,new_balance_amount,new_fineamount,active,invoice_no))

						connection.commit()

				else:
					detail='amount'
					status_record='waiting'

					if float(amount) > 0:

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,amount,'null',activeyes,'purchase'))
						
						connection.commit()

					if float(cd)>0:

						detail='cash discount'
						status_record='waiting'

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'purchase'))
						
						connection.commit()

					if float(bankcharges)>0:

						detail='fine amount'
						status_record='waiting'

						cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(paydate,cheque,companyname,invoice_no,detail,status_record,reference,paymode,notes,depositto,cd,'null',activeno,'purchase'))
						
						connection.commit()

		        #==============================================#
		        #       active 0 == Not completed              #
		        #       active 1 == paid                       #
		        #==============================================#

				
			return redirect("/inventory/purchase_payment_link?id={}".format((company_name)))
			# return redirect("/inventory/payment_link?id={}".format(int(payment_add())))

	finally:
		cursor.close()
		connection.close()

# ======================================================= more bill view========================
@inventory.route("/more_purchaseview/<int:bill_no>", methods=["POST","GET"])
@inventory_token
def more_purchaseview(bill_no):

	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from payment_records where type='purchase' and invoice_no=%s",(bill_no))
		payment_records=cursor.fetchall()

		return render_template('inventory/more_purchaseview.html',payment_records=payment_records)
	finally:
		cursor.close()
		connection.close()
#=========================================================# payment record #==========================
@inventory.route("/purchase_record_edit", methods=["POST","GET"])
@inventory_token
def purchase_record_edit():

	try:
		connection=get_connection()
		cursor=connection.cursor()
	

		id=request.args.get('id')
		cursor.execute("SELECT * from payment_records where payment_records.type='purchase' and id =%s",(id))
		payment_records=cursor.fetchone()
		cursor.execute("SELECT * from payment_details where invoice_no=%s and type='purchase'",(payment_records['invoice_no']))
		payment_details=cursor.fetchone()

		company_name=payment_details['company_name']
		paid=payment_records['paid_amount']
		total_amount=payment_details['total_amount']
		paid_amount=payment_details['paid_amount']
		balance_amount=payment_details['balance_amount']
		fine_amount=payment_details['fine_amount']

		if request.form.get('delete')=='delete':

			if payment_records['active_status']==1:

				if payment_records['status']=='fine amount':

					new_total=float(total_amount)-float(paid)
					new_balance_amount=float(balance_amount)-float(paid)

					new_fineamount=float(fine_amount)-float(paid)
					cursor.execute("UPDATE payment_details set total_amount=%s,balance_amount=%s,fine_amount=%s where invoice_no=%s and type='purchase'",(new_total,new_balance_amount,new_fineamount,payment_records['invoice_no']))
					cursor.execute("DELETE from payment_records where id =%s",(id))
					connection.commit()
				else:
					new_paid_amount=float(paid_amount)-float(paid)
					new_balance_amount=float(balance_amount)+float(paid)

					cursor.execute("UPDATE payment_details set paid_amount=%s,balance_amount=%s where invoice_no=%s and type='purchase'",(new_paid_amount,new_balance_amount,payment_records['invoice_no']))
					cursor.execute("DELETE from payment_records where id =%s",(id))
					connection.commit()
			# active= waiting delete
			else:
					cursor.execute("DELETE from payment_records where id=%s",(id))
					connection.commit()

		if request.form.get('paid')=='paid':

			if payment_records['active_status']==0:

				if payment_records['status']=='fine amount':

					new_total=float(total_amount)+float(paid)
					new_balance_amount=float(balance_amount)+float(paid)

					new_fineamount=float(fine_amount)+float(paid)
					cursor.execute("UPDATE payment_details set total_amount=%s,balance_amount=%s,fine_amount=%s where invoice_no=%s and type='purchase'",(new_total,new_balance_amount,new_fineamount,payment_records['invoice_no']))
					cursor.execute("UPDATE payment_records set active_status=1,status='paid' where id =%s",(id))
					connection.commit()
				else:
					new_paid_amount=float(paid_amount)+float(paid)
					new_balance_amount=float(balance_amount)-float(paid)

					cursor.execute("UPDATE payment_details set paid_amount=%s,balance_amount=%s where invoice_no=%s and type='purchase'",(new_paid_amount,new_balance_amount,payment_records['invoice_no']))
					cursor.execute("UPDATE payment_records set active_status=1,status='paid' where id =%s",(id))
					connection.commit()
			# active= waiting delete
			
			

		if request.form.get('cancel')=='cancel':

			if payment_records['active_status']==0:

				if payment_records['status']=='fine amount':

					cursor.execute("UPDATE payment_records set active_status=2,status='cancelled' where id =%s",(id))
					connection.commit()
				else:
					
					cursor.execute("UPDATE payment_records set active_status=2,status='cancelled' where id =%s",(id))
					connection.commit()
			# active= waiting delete
		
		return redirect(url_for("inventory.more_purchaseview",bill_no=payment_records['invoice_no']))
	finally:
		cursor.close()
		connection.close()

#========================================================# report #========================================
@inventory.route("/stock_report", methods=["POST","GET"])
@inventory_token
def stock_report():

	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from product")
		product=cursor.fetchall()

		cursor.execute("SELECT * from purchase_head,purchase_body WHERE purchase_body.bill_no=purchase_head.bill_no")
		purchase=cursor.fetchall()

		cursor.execute("SELECT * from bill_info")
		bill=cursor.fetchall()
		
		if request.method == "POST":
			product_id=request.form['item']


			cursor.execute("SELECT * from product where id=%s",product_id)
			open_stock=cursor.fetchone()

			table=[]
			for i in purchase:
				for j in product:
					if int(j['id'])==int(i['item']):
						if int(j['id'])==int(product_id):
							date=i['date']
							date=str(date)
							product_name=j['product_name']
							code=j['product_code']
							qty=i['qty']
							item_id=j['id']
							stock=j['opening_stock']
							types='purchase'

							table.append([date,product_name,code,qty,stock,item_id,types])

			for i in bill:
				for j in product:
					if int(j['id'])==int(i['product_name']):
						if int(j['id'])==int(product_id):
							date=i['date']
							date=str(date)
							product_name=j['product_name']
							code=j['product_code']
							qty=i['quantity']
							stock=j['opening_stock']
							item_id=j['id']
							types='bill'

							table.append([date,product_name,code,qty,stock,item_id,types])
			
			table=(sorted(table,key=lambda x: datetime.strptime(x[0], '%Y-%m-%d')))
			

			# http://127.0.0.1:5000/inventory/stock_report
			# http://127.0.0.1:5000/inventory/customer_sales_report
			
			graphvalue=[]
			date_set=[]

			for j in table:
				date_set.append(j[0])
			date_set=set(date_set)

			
			for j in date_set:
				stock=0
				for i in table:
					# datetime.strptime(monthloop,'%Y-%m-%d').date()
					if j==i[0]:
						if i[6]=='purchase':
							stock+=int(i[3])
						else:
							stock-=int(i[3])

				graphvalue.append({"country":(j),"visits":(stock)})
			
			print(graphvalue)

			material_name=open_stock['product_name']

			key='fine'

			return render_template("inventory/stock_report.html",material_name=material_name,graphvalue=graphvalue,key=key,table=table,product=product,open_stock=open_stock)

		else:
			key='normal'

			return render_template("inventory/stock_report.html",key=key,product=product)
	finally:
		cursor.close()
		connection.close()

#========================================================# item report #========================================
@inventory.route("/item_report", methods=["POST","GET"])
@inventory_token
def item_report():
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from product")
		product=cursor.fetchall()

		if request.method=="POST":

			product_id=request.form['item']

			if product_id == "ALL":
				# cursor.execute("SELECT * from product where id=%s",(product_id))
				# product_name=cursor.fetchone()['product_name']

				cursor.execute("SELECT * from bill_info,product where product.id=bill_info.product_name")
				sales_item=cursor.fetchall()
			else:
				# cursor.execute("SELECT * from product where id=%s",(product_id))
				# product_name=cursor.fetchone()['product_name']

				cursor.execute("SELECT * from bill_info,product where product.id=bill_info.product_name and bill_info.product_name=%s",(product_id))
				sales_item=cursor.fetchall()

			graphvalue=[]
			date_set=[]
			
			for j in sales_item:
				date_set.append(str(j['date']))
			date_set=set(date_set)

			
			for j in date_set:
				stock=0
				for i in sales_item:
					# datetime.strptime(monthloop,'%Y-%m-%d').date()

					if j==str(i['date']):
						stock+=int(i['quantity'])

				graphvalue.append({"country":(j),"visits":(stock)})
			
			print(graphvalue)
			if product_id=="ALL":
				material_name="ALL"
			else:
				cursor.execute("SELECT* from product where id=%s",(product_id))
				material_name=cursor.fetchone()['product_name']

			key='1'

			return render_template("inventory/item_sales.html",material_name=material_name,graphvalue=graphvalue,product=product,key=key,sales_item=sales_item)

		else:

			key='0'
			
			return render_template("inventory/item_sales.html",product=product,key=key)
	finally:
		cursor.close()
		connection.close()

#========================================================# customer sales report #========================================
@inventory.route("/customer_sales_report", methods=["POST","GET"])
@inventory_token
def customer_sales_report():
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from customer")
		customer=cursor.fetchall()

		if request.method=="POST":

			customer_id=request.form['customer']

			if customer_id =="ALL":

				# cursor.execute("SELECT * from customer where id=%s",(customer_id))
				# customer_name=cursor.fetchone()['companyname']

				cursor.execute("SELECT * from bill,customer where customer.id=bill.companyname and bill.customer_type='customer' ")
				sales_customer=cursor.fetchall()
			else:

				# cursor.execute("SELECT * from customer where id=%s",(customer_id))
				# customer_name=cursor.fetchone()['companyname']

				cursor.execute("SELECT * from bill,customer where customer.id=bill.companyname and bill.companyname=%s and bill.customer_type='customer' ",(customer_id))
				sales_customer=cursor.fetchall()

			graphvalue=[]
			date_set=[]
			
			for j in sales_customer:
				date_set.append(str(j['date']))
			date_set=set(date_set)

			
			# print(sales_customer)
			for j in date_set:
				stock=0
				for i in sales_customer:
					# datetime.strptime(monthloop,'%Y-%m-%d').date()

					if j==str(i['date']):
						stock+=int(i['grand_total'])

				graphvalue.append({"country":(j),"visits":(stock)})
			
			print(graphvalue)

			if customer_id=="ALL":
				customer_name="ALL"
			else:
				cursor.execute("SELECT * from customer where id=%s",(customer_id))
				customer_name=cursor.fetchone()['companyname']

			key='1'

			return render_template("inventory/customer_sales.html",customer_name=customer_name,graphvalue=graphvalue,customer=customer,key=key,sales_customer=sales_customer)

		else:

			key='0'
			
			return render_template("inventory/customer_sales.html",customer=customer,key=key)
	finally:
		cursor.close()
		connection.close()
#========================================================# product stock #========================================
@inventory.route("/product_stock", methods=["POST","GET"])
@inventory_token
def product_stock():
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from product ")
		product=cursor.fetchall()

		key='1'
		return render_template("inventory/product_stock.html",product=product,key=key)
	finally:
		cursor.close()
		connection.close()
#========================================================# allcustomer sales #========================================
@inventory.route("/allcustomer_sales", methods=["POST","GET"])
@inventory_token
def allcustomer_sales():
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("SELECT * from bill_info,product where product.id=bill_info.product_name ")
		product=cursor.fetchall()

		cursor.execute("SELECT * from bill,customer where customer.id=bill.companyname ")
		customer=cursor.fetchall()

		cursor.execute("SELECT * from bill_info,bill,product WHERE product.id=bill_info.product_name AND bill.invoice_no=bill_info.invoice_no AND bill_info.invoice_no=%s",(0))
		unknown_customer=cursor.fetchall()

		# cursor.execute("SELECT * from bill_info,product where product.id=bill_info.product_name")
		# unknown_product=cursor.fetchall()
		# print(product)
		# print(customer)
		bill=[]
		for i in customer:
			for j in product:
				if int(i['invoice_no'])==int(j['invoice_no']):
					date=i['date']
					invoice_no=j['invoice_no']
					customer_name=i['customer.companyname']
					product_name=j['product.product_name']
					qty=j['quantity']
					price=j['value']
					amount=j['amount']

					bill.append([date,invoice_no,customer_name,product_name,qty,price,amount])
		print(bill)

		key='1'
		return render_template("inventory/allcustomer_sales.html",bill=bill,unknown_customer=unknown_customer,key=key)
	finally:
		cursor.close()
		connection.close()
#========================================================# bank #========================================
@inventory.route("/bank", methods=["POST","GET"])
@inventory_token
def bank():
	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=="POST":

			if request.form['bankname'] == "":
				return redirect(url_for('inventory.bank'))
			else:
				short_name=request.form['shortname']
				bank_name=request.form['bankname']
				account_number=request.form['accountnumber']
				ifsc=request.form['ifsccode']
				branch=request.form['branch']
				name=request.form['name']

				cursor.execute("INSERT INTO bank_details value(null,%s,%s,%s,%s,%s,%s)",(str(short_name),str(bank_name),str(account_number),str(ifsc),str(branch),str(name)))
				connection.commit()

				return redirect(url_for('inventory.bank'))
		else:

			id=None

			cursor.execute("SELECT * from bank_details")
			bankdetails=cursor.fetchall()

		return render_template('inventory/bank.html',bankdetails=bankdetails,id=id)

	finally:
		cursor.close()
		connection.close()

#========================================================# bankedit #========================================
@inventory.route("/bankedit/<int:id>", methods=["POST","GET"])
@inventory_token
def bankedit(id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		

		cursor.execute("SELECT * from bank_details where id=%s",(id))
		bankedit=cursor.fetchone()

		cursor.execute("SELECT * from bank_details")
		bankdetails=cursor.fetchall()


		return render_template("inventory/bank.html",id=id,bankedit=bankedit,bankdetails=bankdetails)

	finally:
		cursor.close()
		connection.close()

@inventory.route("/bankupdate/<int:id>", methods=["POST","GET"])
@inventory_token
def bankupdate(id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		if request.method=="POST":

			if request.form['bankname'] == "":
				return redirect(url_for('inventory.bank'))
			else:
				short_name=request.form['shortname']
				bank_name=request.form['bankname']
				account_number=request.form['accountnumber']
				ifsc=request.form['ifsccode']
				branch=request.form['branch']
				name=request.form['name']
				cursor.execute("UPDATE bank_details set short_name=%s,bank_name=%s,ifsc_code=%s,account_no=%s,branch=%s,account_holder_name=%s where id=%s",(str(short_name),str(bank_name),str(ifsc),str(account_number),str(branch),str(name),id))
				connection.commit()

				return redirect(url_for('inventory.bankedit',id=id))

	finally:
		cursor.close()
		connection.close()


@inventory.route("/bankdelete/<int:id>", methods=["POST","GET"])
@inventory_token
def bankdelete(id):
	try:
		connection=get_connection()
		cursor=connection.cursor()

		cursor.execute("DELETE from bank_details where id=%s",(id))
		connection.commit()

		return redirect(url_for("inventory.bank"))
	finally:
		cursor.close()
		connection.close()

# ============================================================== company details =================================
@inventory.route("/companydetail",methods=["POST","GET"])
@inventory_token
def companydetail():

    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute("SELECT * from company_detail")
    cmpy=cursor.fetchone()

    if cmpy==None:

        if request.form.get('ADD')=='ADD':
            company_name=request.form['company_name']
            address1=request.form['address1']
            address2=request.form['address2']
            state=request.form['state']
            pincode=request.form['pincode']
            mobilenumber=request.form['mobilenumber']
            faxnumber=request.form['faxnumber']
            website=request.form['website']
            phonenumber=request.form['phonenumber']
            email=request.form['email']
            branchcode=request.form['branchcode']
            gstin=request.form['gstin']
            satecode=request.form['satecode']
            proverb=request.form['proverb']
            target=request.form['target']

            cursor.execute("INSERT into company_detail value('null',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(company_name,address1,address2,state,pincode,mobilenumber,faxnumber,phonenumber,email,website,branchcode,gstin,satecode,proverb,target))
            connection.commit()

            return redirect(url_for('inventory.companydetail'))

        else:
            key='new'
            return render_template("inventory/company.html",key=key)
    else:
        if request.form.get('UPDATE')=='UPDATE':
            company_name=request.form['company_name']
            address1=request.form['address1']
            address2=request.form['address2']
            state=request.form['state']
            pincode=request.form['pincode']
            mobilenumber=request.form['mobilenumber']
            faxnumber=request.form['faxnumber']
            website=request.form['website']
            phonenumber=request.form['phonenumber']
            email=request.form['email']
            branchcode=request.form['branchcode']
            gstin=request.form['gstin']
            satecode=request.form['satecode']
            proverb=request.form['proverb']
            target=request.form['target']
            id=request.form['id']
            print(satecode)
            cursor.execute("UPDATE company_detail SET companyname=%s,address1=%s,address2=%s,state=%s,pincode=%s,mobilenumber=%s,faxnumber=%s,phonenumber=%s,email=%s,website=%s,branchcode=%s,gst=%s,statecode=%s,proverb=%s,target=%s where id=%s",(company_name,address1,address2,state,pincode,mobilenumber,faxnumber,phonenumber,email,website,branchcode,gstin,satecode,proverb,target,id))
            connection.commit()
            return redirect(url_for('inventory.companydetail'))

        else:
            print(cmpy)
            key='old'
            return render_template("inventory/company.html",key=key,cmpy=cmpy)

#----------------------------------------------------------Dashboard-----------------------------

@inventory.route("/dashboard", methods=["GET","POST"])
@inventory_token
def dashboard():
    
    dashboard_name='kani'
    # print(dashboard_name)
    connection=get_connection()
    cursor=connection.cursor()
    id =request.form.get('ADD')
    if id == "ADD":
        target=request.form['target']
        cursor.execute("SELECT * from company_detail")
        cmpy_details = cursor.fetchone()
        if cmpy_details == None:
            return redirect(url_for('inventory.companydetail'))
        cursor.execute('UPDATE company_detail set target=%s',(target))
        connection.commit()
    try:
        #---------------------------------------------------total sales----------------------------
        cursor.execute("SELECT grand_total from bill")
        grnd_tot=cursor.fetchall()

        cursor.execute("SELECT grand_total from purchase_head")
        pur_tot=cursor.fetchall()

        cursor.execute("SELECT companyname from customer")
        cus_tot=cursor.fetchall()

        gnt_tot=0
        gnd_pur=0
        gnd_cus=len(cus_tot)

        for i in grnd_tot:
            gnt_tot=gnt_tot+i['grand_total']

        for i in pur_tot:
            gnd_pur=gnd_pur+i['grand_total']


        #----------------------------------------------------------interior section------------------
        cursor.execute("SELECT bill from bill")
        date_table=cursor.fetchall()

        date_sort=[]
        sales_value={}
        for i in date_table:
            date_sort.append(i['bill'])
        date_sort=set(date_sort)

        count=0
        for i in date_sort:

            cursor.execute("SELECT grand_total from bill where bill=%s",(i))
            amount=cursor.fetchall()

            value=0
            for j in amount:
                value=value+j['grand_total']
            sales_value[count]={'date':i,'amount':value}
            count=count+1
        
        #-------------------------------------------- monthly sales report--------------------------------
        cursor.execute("SELECT MIN(bill) from bill")
        sdate=cursor.fetchone()['MIN(bill)']

        cursor.execute("SELECT MAX(bill) from bill")
        edate=cursor.fetchone()['MAX(bill)']
        if edate==None:
            edate=today
            sdate=today
        cursor.execute("SELECT * from bill")
        tables=cursor.fetchall()

        salesmonthtable=[]
        months=((edate.year-sdate.year)*12)+(edate.month-sdate.month)

        month=str(sdate).split('-')[1]
        year=str(sdate).split('-')[0]

        # count1=0
        for j in range(months+1):
            if int(month)>=10:
                if int(month) >12:
                    month=int(month/12)
                    year=int(year)+1
                    monthloop=(str(year)+'-'+'0'+str(month)+'-1')

                   
                else:
                    
                    monthloop=(str(year)+'-'+str(month)+'-1')
                month=int(month)+1
            else:
                if int(month) >12:
                    month=int(month/12)
                    year=int(year)+1
                    monthloop=(str(year)+'-'+'0'+str(month)+'-1')

                   
                else:
                    month=int(month)
                    monthloop=(str(year)+'-'+'0'+str(month)+'-1')
                month=int(month)+1

            
            # print('month loop',monthloop)
            
            grandtotal=0

            day=datetime.strptime(monthloop,'%Y-%m-%d').date()
            # print(day)
            for i in tables:
                # print('date',i['bill'])
                invoicemonth=str(i['bill']).split('-')[1]
                invoiceyear=str(i['bill']).split('-')[0]
                invoiceloop=(str(invoiceyear)+'-'+str(invoicemonth)+'-1')
                # print('month loop',monthloop)
                # print('invoice loop',invoiceloop)
                if (monthloop) == (invoiceloop):
                    
                    grandtotal=grandtotal+i['grand_total']

            
            salesmonthtable.append({'country':monthloop,'visits':grandtotal})
            # count1+=1/
        # print(salesmonthtable)

        #---------------------------------------------------------------------------------------------item sales graph-------------------------
        cursor.execute("SELECT * from product ")
        item_list=cursor.fetchall()

        itemstore=[]
        for i in item_list:
            cursor.execute("SELECT * FROM bill_info where product_name=%s",(i['id']))
            itemvalue=cursor.fetchall()

            itemamt=0
            for j in itemvalue:
                itemamt=itemamt+j['pretotal']

            itemstore.append({'network':i['product_name'],'MAU':itemamt})

        cursor.execute("SELECT * from product ")
        item_list=cursor.fetchall()

    #---------------------------------------------------------------------------------------------in active customer graph-------------------------
        cursor.execute("SELECT * from customer ")
        cmp_list=cursor.fetchall()

        cmpstore=[]
        for i in cmp_list:
            cursor.execute("SELECT MAX(bill),grand_total FROM bill where companyname=%s",(i['id']))
            cmpvalue=cursor.fetchone()
            # days=today - cmpvalue['MAX(bill)'] 
            # print(days[0])
            
            cmpstore.append({'country':'date: '+str(cmpvalue['MAX(bill)'])+'\ncustomer: '+i['companyname'],'visits':cmpvalue['grand_total']})
        # print(cmpstore)

        #---------------------------------------------------------------------------------------------customer sales graph-------------------------
        cursor.execute("SELECT * from customer")
        cus_list=cursor.fetchall()

        custore=[]
        for i in cus_list:
            cursor.execute("SELECT * FROM bill where companyname=%s",(i['id']))
            cusvalue=cursor.fetchall()

            cusamt=0
            for j in cusvalue:
                cusamt=cusamt+j['grand_total']

            custore.append({'network':i['companyname'],'MAU':cusamt})

        cursor.execute("SELECT * from product ")
        cus_list=cursor.fetchall()
        # print(custore)

        #---------------------------------------------------------------------------------------------in active item graph-------------------------
        cursor.execute("SELECT * from product ")
        mat_list=cursor.fetchall()

        matstore=[]
        for i in mat_list:
            cursor.execute("SELECT MAX(date),pretotal FROM bill_info where product_name=%s",(i['id']))
            matvalue=cursor.fetchone()
            
            matstore.append({'country':'Date: '+str(matvalue['MAX(date)'])+'\nItem name: '+i['product_name'],'visits':matvalue['pretotal']})
        # print(matstore)


        #-----------------------------------------------------------------------------------------reorderlevel-------------------------------#
        cursor.execute("SELECT * from product ")
        matre_list=cursor.fetchall()

        matrestore=[]
        for i in matre_list:
        	# i['reorder_level']
            if 10>=i['stock']:
                matrestore.append({"country":i['product_name'],"visits":i['stock']})

        

        #-----------------------------------------------------------------------------------------payment pending details---------------------#
        cursor.execute("SELECT *,customer.companyname as company_name,customer.id as cusid,bill.due_date as b_duedate from customer,bill where customer.id=bill.companyname")
        cusdetail=cursor.fetchall()
        # print(cusdetail)
        detail=dict()
        
        for i in cusdetail:
            # if i['b_duedate'] >= today:
            if str(type(i['b_duedate']))=="<class 'str'>":
                pass
            else:
                if i['b_duedate'] <= today:
                    cursor.execute("SELECT * from payment_details where payment_details.invoice_no=%s and payment_details.company_name=%s and payment_details.type='bill'",(i['invoice_no'],i['bill.companyname']))
                    payment_detail=cursor.fetchone()
                    # print('poo')
                    # print(i['invoice_no'])
                    if payment_detail==None:
                    	pass
                    else:
	                    if i['company_name'] not in detail:

	                        print('ok')
	                        print(payment_detail['balance_amount'])
	                        detail[i['company_name']]={"date":i['b_duedate'],"company_name":i['company_name'],'balance':payment_detail['balance_amount'],'paid':payment_detail['paid_amount']}
	                        print('ok')
	                    else:
	                        detail[i['company_name']]['balance']+=payment_detail['balance_amount']
	                        detail[i['company_name']]['paid']+=payment_detail['paid_amount']
        
        
         #-----------------------------------------------------------------------------------------tdy sales details---------------------#
        cursor.execute("SELECT * from customer,bill where customer.id=bill.companyname and bill.bill=%s",(today))
        salesdetail=cursor.fetchall()

        cursor.execute("SELECT target from company_detail")
        tar=cursor.fetchone()
        if tar==None:
            target=0
        else:
            target=tar['target']

        # print('sales',salesdetail)
        print(salesmonthtable)
        return render_template("inventory/dashboard.html",target=target,dashboard_name=dashboard_name,gnt_tot=gnt_tot,gnd_pur=gnd_pur,gnd_cus=gnd_cus,salesdetail=salesdetail,detail=detail,matrestore=matrestore,matstore=matstore,custore=custore,count=count,sales_value=sales_value,salesmonthtable=salesmonthtable,itemstore=itemstore,cmpstore=cmpstore)
    finally:
        cursor.close()
        connection.close()
