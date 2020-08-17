# SWAMI KARUPPASWAMI THUNNAI

from database.get_connection import get_connection
from flask import request, redirect, url_for, session

def bill_insert(today,id):
    

    try:
        connection=get_connection()
        cursor=connection.cursor()
        
        rowcount = request.form['rowcount']
                
        invoice_no=request.form['invoice_no']
        billdate=request.form['billdate']
        due_date=request.form['duedate']
        customername=request.form['customername']
        customer_type=request.form['customer_type']
        address=request.form['address']
        shipaddress=request.form['shipaddress']
        gst='null'
        total=request.form['total']
        cgst=request.form['cgst']
        sgst=request.form['sgst']
        igst=request.form['igst']
        roundoff=request.form['roundoff']
        grand_total=request.form['grandtot']
        state=request.form['state']
        city=request.form['city']

        #===============payment function==========================
        
        balance=request.form['balance']
        paid=request.form['paid']
        fine=0

        status1='Payment Not Completed!'
        status2='Payment Completed'

        bill_type='bill'
        details='cash'
        notes='none'
        deposit_to='cash'

        activeyes=0
        activeno=1


        #==============================================#
        #       active 0 == Not completed              #
        #       active 1 == paid                       #
        #==============================================#

        if customer_type!='customer':
            cursor.execute("INSERT into customer value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(today,customername,customername,"null","null",address,state,city,"null","null",'0'))
            connection.commit()
            customername=cursor.lastrowid
            customer_type='customer'
        # print((invoice_no))
        # print((billdate))
        # print((due_date))
        # print((customername))
        # print((customer_type))
        # print((address))
        # print((shipaddress))
        # print((total))
        # print((cgst))
        # print((sgst))
        # print((igst))
        # print((roundoff))
        # print((grand_total))
        # print('pass1')
        if id == None:
            cursor.execute("INSERT into bill value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(today,(invoice_no),billdate,due_date,(customername),customer_type,(address),(shipaddress),gst,(total),(cgst),(sgst),(igst),(roundoff),(grand_total),state,city))
            customer_id=cursor.lastrowid
            connection.commit()

            if customer_type == 'customer':                 
                paymentdetail_add(billdate,today,customername,invoice_no,details,status1,status2,notes,deposit_to,bill_type,balance,fine,grand_total,activeno,activeyes)

            # ============================== paymenyt add ======================================

            
        else:

            # ==========================================================================================================================================================================================================================

            if customer_type == 'customer':

                customer_id=id

                cursor.execute("SELECT * from bill,payment_details where payment_details.type='bill' and payment_details.invoice_no=bill.invoice_no and payment_details.company_name=bill.companyname and bill.id =%s",(id))
                bill_amount=cursor.fetchone()

                old_billamount=bill_amount['bill_amount']
                old_paid=bill_amount['paid_amount']

                amount_dif=float(grand_total) - float(old_billamount)
                paid_diff=float(paid) - float(old_paid)

                new_billamount=float(old_billamount)+amount_dif
                new_totalamount=float(bill_amount['total_amount'])+amount_dif
                new_balance=float(bill_amount['balance_amount'])+amount_dif-paid_diff
                
                new_paid=new_totalamount-new_balance

                if float(new_balance) == 0:
                    cursor.execute("UPDATE payment_details set bill_amount=%s,total_amount=%s,paid_amount=%s,balance_amount=%s,active_status=%s where id=%s",(new_billamount,new_totalamount,new_paid,new_balance,activeno,bill_amount['payment_details.id']))
                    connection.commit()
                else:
                    cursor.execute("UPDATE payment_details set bill_amount=%s,total_amount=%s,paid_amount=%s,balance_amount=%s,active_status=%s where id=%s",(new_billamount,new_totalamount,new_paid,new_balance,activeyes,bill_amount['payment_details.id']))
                    connection.commit()
            # ==========================================================================================================================================================================================================================
            cursor.execute("UPDATE bill set date=%s,invoice_no=%s,bill=%s,due_date=%s,companyname=%s,customer_type=%s,address=%s,shipping=%s,gst=%s,total=%s,cgst=%s,sgst=%s,igst=%s,roundoff=%s,grand_total=%s,state=%s,city=%s where id=%s",
                (today,invoice_no,billdate,due_date,customername,customer_type,address,shipaddress,gst,total,cgst,sgst,igst,roundoff,grand_total,state,city,id))
            connection.commit()

            cursor.execute("SELECT * from bill where bill.id =%s",(id))
            invoice_number=cursor.fetchone()
            
            cursor.execute("SELECT * from bill_info where bill_info.invoice_no =%s",(invoice_number['invoice_no']))
            item=cursor.fetchall()
            
            for i in item:

                qty=i['quantity']

                cursor.execute("SELECT * from product where product.id =%s",(i['product_name']))
                oldstock=cursor.fetchone()
                
                newstock=float(oldstock['stock'])+float(qty)

                
                cursor.execute("UPDATE product set stock=%s where product.id=%s",(newstock,i['product_name']))
                connection.commit()
            cursor.execute("DELETE from bill_info where bill_info.invoice_no=%s",(invoice_number['invoice_no']))
            connection.commit()
        
        for i in range(0, int(rowcount)):
            
            try:
                
                code=request.form['productcode_'+str(i)]
                name=request.form['name_'+str(i)]
                mrp=0
                qty=request.form['quantity_'+str(i)]
                value=request.form['value_'+str(i)]
                discount=request.form['dis_'+str(i)]
                after_dis=request.form['afterdis_'+str(i)]
                pretotal=request.form['prevalue_'+str(i)]
                gst=request.form['gst_'+str(i)]
                amount=request.form['amount_'+str(i)]
                unit=request.form['unit_'+str(i)]
                
                cursor.execute("SELECT * from product where id=%s",(name))
                item_name=cursor.fetchone()
                oldstock=item_name['stock']

                newstock=float(oldstock)-float(qty)
                
                cursor.execute("UPDATE product set stock=%s where id=%s",(newstock,name))
                
                cursor.execute("INSERT into bill_info value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(today,invoice_no,billdate,0,code,name,mrp,qty,value,discount,after_dis,pretotal,gst,amount,unit))
                connection.commit()
            except:
                i+=1
        return customer_id
    finally:
    	#print("ok")
        cursor.close()
        connection.close()
        

def purchase_adds(id):
    try:

        connection=get_connection()
        cursor=connection.cursor()

        bill_no=request.form['bill_no']
        bill_date=request.form['bill_date']
        lr_no=request.form['lr_no']
        lr_date=request.form['lr_date']
        transpodate=request.form['ac_date']
        transport_name=request.form['transport_name']
        vendorname=request.form['vendorname']
        Narration=request.form['Narrations']
        
        total=request.form['total']
        cgst=request.form['cgst']
        sgst=request.form['sgst']
        igst=request.form['igst']
        INSURANCE=request.form['INSURANCE']
        inucgst=request.form['inucgst']
        inusgst=request.form['inusgst']
        roundoff=request.form['roundoff']
        gndtot=request.form['gndtot']

        rowcount=request.form['rowcount']
        print(rowcount)
        # print(id)

        #===============payment function==========================
        
        balance=request.form['balance']
        paid=request.form['paid']
        fine=0

        status1='Payment Not Completed!'
        status2='Payment Completed'

        bill_type='purchase'
        details='cash'
        notes='none'
        deposit_to='cash'

        activeyes=0
        activeno=1

        customer_type='customer'


        #==============================================#
        #       active 0 == Not completed              #
        #       active 1 == paid                       #
        #==============================================#

        if int(id)==0:
            cursor.execute('INSERT INTO purchase_head value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(bill_no,bill_date,transpodate,lr_no,lr_date,transport_name,vendorname,Narration,total,cgst,sgst,igst,INSURANCE,inucgst,inusgst,roundoff,gndtot))
            connection.commit()

            if customer_type == 'customer':
                paymentdetail_add(bill_date,bill_date,vendorname,bill_no,details,status1,status2,notes,deposit_to,bill_type,balance,fine,gndtot,activeno,activeyes)

        else:
            # ==========================================================================================================================================================================================================================

            if customer_type == 'customer':
                cursor.execute("SELECT * from purchase_head,payment_details where payment_details.type='purchase' and payment_details.invoice_no=purchase_head.bill_no and purchase_head.id =%s",(id))
                bill_amount=cursor.fetchone()

                old_billamount=bill_amount['bill_amount']
                old_paid=bill_amount['paid_amount']

                amount_dif=float(gndtot) - float(old_billamount)
                paid_diff=float(paid) - float(old_paid)

                new_billamount=float(old_billamount)+amount_dif
                new_totalamount=float(bill_amount['total_amount'])+amount_dif
                new_balance=float(bill_amount['balance_amount'])+amount_dif-paid_diff
                
                new_paid=new_totalamount-new_balance

                if new_balance == 0:
                    cursor.execute("UPDATE payment_details set bill_amount=%s,total_amount=%s,paid_amount=%s,balance_amount=%s,active_status=%s where id=%s",(new_billamount,new_totalamount,new_paid,new_balance,activeno,bill_amount['payment_details.id']))
                    connection.commit()
                else:
                    cursor.execute("UPDATE payment_details set bill_amount=%s,total_amount=%s,paid_amount=%s,balance_amount=%s,active_status=%s  where id=%s",(new_billamount,new_totalamount,new_paid,new_balance,activeyes,bill_amount['payment_details.id']))
                    connection.commit()

            # ==========================================================================================================================================================================================================================
            cursor.execute("UPDATE purchase_head set bill_no=%s,date=%s,ac=%s,lr_no=%s,lr_date=%s,transport_name=%s,suppiler_name=%s,Naration=%s,total=%s,cgst=%s,sgst=%s,igst=%s,insurance=%s,in_cgst=%s,in_sgst=%s,roundoff=%s,grand_total=%s where id=%s",
                (bill_no,bill_date,transpodate,lr_no,lr_date,transport_name,vendorname,Narration,total,cgst,sgst,igst,INSURANCE,inucgst,inusgst,roundoff,gndtot,id))
            connection.commit()

            cursor.execute("SELECT * from purchase_head where id=%s",(id))
            p_head=cursor.fetchone()

            cursor.execute("SELECT * from purchase_body where bill_no=%s",(p_head['bill_no']))
            p_body=cursor.fetchall()

            for i in p_body:
                cursor.execute("SELECT * from product where id=%s",(i['item']))
                product=cursor.fetchone()

                oldstock=float(product['stock'])

                newstock=oldstock-float(i['qty'])

                cursor.execute("UPDATE product set stock=%s where id=%s",(newstock,product['id']))
                connection.commit()

            cursor.execute("DELETE from purchase_body where bill_no=%s",(p_head['bill_no']))
            connection.commit()

        for i in range(0, int(rowcount)):
            print(i)
            try:
                productname=request.form['productname_'+str(i)]
                qty=request.form['quantity_'+str(i)]
                unit=request.form['unit_'+str(i)]
                value=request.form['value_'+str(i)]
                rate=request.form['rate_'+str(i)]
                gst=request.form['gst_'+str(i)]

                cursor.execute("INSERT INTO purchase_body value(null,%s, %s, %s, %s, %s,%s,%s)",(bill_no,productname,qty,unit,rate,value,gst))
                connection.commit()

                cursor.execute("SELECT * from product where product.id=%s ",(productname))
                product=cursor.fetchone()

                stock=int(int(product['stock']))+int(qty)

                print(stock)
                cursor.execute("UPDATE product SET stock=%s where product.id=%s",(stock,product['id']))
                connection.commit()
            except:
                print('wrong')
                i+=1

        return 'True'
        
    finally:
        #print("ok")
        cursor.close()
        connection.close()


def paymentdetail_add(billdate,today,customername,invoice_no,details,status1,status2,notes,deposit_to,bill_type,balance,fine,grand_total,activeno,activeyes):
    
    try:
        connection=get_connection()
        cursor=connection.cursor()

        paid=float(grand_total)- float(balance)
        print(paid)
        if float(paid) != 0 :

            print('pass')
            
            cursor.execute("INSERT into payment_details value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(billdate,customername,invoice_no,grand_total,status1,grand_total,paid,balance,fine,activeyes,bill_type))
            
            cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,null,%s,%s)",(billdate,today,customername,invoice_no,details,status1,details,details,notes,deposit_to,paid,activeno,bill_type))
            connection.commit()

        else:
            cursor.execute("INSERT into payment_details value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(billdate,customername,invoice_no,grand_total,status1,grand_total,paid,balance,fine,activeno,bill_type))
                
            # cursor.execute("INSERT into payment_records value(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,null,%s,%s)",(billdate,today,customername,invoice_no,details,status1,details,details,notes,deposit_to,paid,activeno,bill_type))
            connection.commit()
    finally:
        cursor.close()
        connection.close()
