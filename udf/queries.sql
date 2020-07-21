
create database if not exists basic_inventory(CREATE DADABASE basic_inventory);

#use meerakunjnew;

create table if not exists admin_login
(
    id bigint primary key auto_increment,
    name text,
    email text,
    phone char(10) unique key,
    username char(128) unique key,
    password char(128),
    level text
);

create table if not exists customer_login
(
    id bigint primary key auto_increment,
    name text,
    email text,
    phone char(10) unique key,
    username char(128) unique key,
    password char(128),
    level text,
    mobile_verfication int,
    email_verification int,
    active int,
    mobile_otp int,
    email_otp int,
    duplicate_mobile text,
    duplicate_email text
);


insert into admin_login values(null, "kani",'thamaraikani69@gmail.com','9789301757',"d6163c4dbf3e1348280fe6f321104c6a176bd22cc7b2d458b4e05eb304a58ab6b8a2a6eafefcf60b56aa04c5d539e244aab45333c19f57ae1fb1eb7901c96ad7","7b4c30e5d0e30195367882baa550c592edfd5a494d8409660ef3c0eb72d5f3bc8a4ba3b3a6b9ceebb264d7cbb06c7b3e245fd7ffeb9daab0c150540bdf2418bb",'1');
insert into customer_login values(null, "kani",'thamaraikani69@gmail.com','9789301757',"d6163c4dbf3e1348280fe6f321104c6a176bd22cc7b2d458b4e05eb304a58ab6b8a2a6eafefcf60b56aa04c5d539e244aab45333c19f57ae1fb1eb7901c96ad7","7b4c30e5d0e30195367882baa550c592edfd5a494d8409660ef3c0eb72d5f3bc8a4ba3b3a6b9ceebb264d7cbb06c7b3e245fd7ffeb9daab0c150540bdf2418bb",'1','1','1','1','0','0',null,null);

create table if not exists customer 
    (
        id bigint primary key auto_increment,
        date date,
        customername text,
        companyname text,
        email text,
        phone text,
        address text,
        state text,
        city text,
        town text,
        gst text,
        dueperiod bigint
    );

create table if not exists vendor 
    (
        id bigint primary key auto_increment,
        date date,
        customername text,
        companyname text,
        email text,
        phone text,
        address text,
        state text,
        city text,
        town text,
        gst text
    );


create table if not exists product 
    (
        id bigint primary key auto_increment,
        date date,
        product_code text,
        product_name text,
        vendor_id text,
        gst text,
        purchase_price text,
        sales_price text,
        opening_stock double,
        stock double,
        stock_alert text,
        unit text
    );


create table if not exists bill 
    (
        id bigint primary key auto_increment,
        date date,
        invoice_no bigint,
        bill date,
        due_date date,
        companyname text,
        customer_type text,
        address text,
        shipping text,
        gst text,
        total double,
        cgst double,
        sgst double,
        igst double,
        roundoff double,
        grand_total bigint,
        state text,
        city text

    );

create table if not exists bill_info 
    (
        id bigint primary key auto_increment,
        date date,
        invoice_no bigint,
        bill date,
        sno text,
        product_code text,
        product_name text,
        mrp text,
        quantity text,
        value double,
        discount double,
        after_dis double,
        pretotal double,
        gst bigint,
        amount double,
        unit text
    );

create table if not exists unit(id text, unit text);

create table if not exists purchase_head(
    id bigint primary key auto_increment,
    bill_no bigint,
    date date,
    ac date,
    lr_no text,
    lr_date date,
    transport_name text,
    suppiler_name text,
    naration text,
    total DOUBLE(10,2),
    cgst DOUBLE(10,2),
    sgst  DOUBLE(10,2),
    igst DOUBLE(10,2),
    insurance DOUBLE(10,2),
    in_cgst  DOUBLE(10,2),
    in_sgst DOUBLE(10,2),
    roundoff DOUBLE(10,2),
    grand_total DOUBLE(10,2)

);
create table if not exists purchase_body(
    id bigint primary key auto_increment,
    bill_no bigint,
    item text,
    qty text,
    unit text,
    rate DOUBLE(10,2),
    value DOUBLE(10,2),
    gst double

);

create table if not exists payment_details(
    id bigint primary key auto_increment,
    date date,
    company_name text,
    invoice_no text,
    bill_amount float(10,2),
    status text,
    total_amount DOUBLE(10,2),
    paid_amount DOUBLE(10,2),
    balance_amount DOUBLE(10,2),
    fine_amount DOUBLE(10,2),
    active_status int,
    type text

);

create table if not exists payment_records(
    id bigint primary key auto_increment,
    date date,
    check_date date,
    company_name text,
    invoice_no text,
    details text,
    status text,
    referenece text,
    payment_mode text,
    notes text,
    deposit_to text,
    paid_amount DOUBLE(10,2),
    attachment blob,
    active_status int,
    type text

);

create table if not exists bank_details(
    id bigint primary key auto_increment,
    short_name text,
    bank_name text,
    ifsc_code text,
    account_no text,
    branch text,
    account_holder_name text


);

create table if not exists company_detail(
    id bigint primary key auto_increment,
    companyname text,
    address1 text,
    address2 text,
    state text,
    pincode text,
    mobilenumber text,
    faxnumber text,
    phonenumber text,
    email text,
    website text,
    branchcode text,
    gst text,
    statecode text,
    proverb text,
    target text
);
