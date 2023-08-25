import mysql.connector

user = input("Enter your MySQL username : ")
password = input("Enter your MySQL password : ")
my_db = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd=password,
)
init_cursor = my_db.cursor()

init_cursor.execute('CREATE DATABASE CDMS')
my_db.commit()
my_db.close()

my_db = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd=password,
    database="CDMS"
)
cursor = my_db.cursor()

query = "CREATE TABLE IF NOT EXISTS auth (userid varchar(15) primary key,password varchar(20), type varchar(10))"
cursor.execute(query)
my_db.commit()

query = "CREATE TABLE IF NOT EXISTS details (userid varchar(15) primary key,name varchar(30), dept varchar(30), year varchar(15), tutorid varchar(15))"
cursor.execute(query)
my_db.commit()

query = "CREATE TABLE IF NOT EXISTS dues (userid varchar(15) primary key,Canteen int,Store int,Bus int,Office int,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"
cursor.execute(query)
my_db.commit()

print("Setup complete")