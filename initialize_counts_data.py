import os 
import psycopg2

url = os.popen("heroku config:get DATABASE_URL -a eddiecloud").read()[:-1]
conn = psycopg2.connect(url, sslmode = 'require')

cursor = conn.cursor()

order = ''' CREATE TABLE COUNTS_TABLE(
    district varchar(100) PRIMARY KEY,
    count varchar(10)
);'''

cursor.execute(order)
conn.commit()

cursor.close()
conn.close()