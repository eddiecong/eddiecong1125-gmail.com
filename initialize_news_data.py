import os 
import psycopg2

url = os.popen("heroku config:get DATABASE_URL -a eddiecloud").read()[:-1]
conn = psycopg2.connect(url, sslmode = 'require')

cursor = conn.cursor()

order = ''' CREATE TABLE NEWS_TABLE(
    title varchar(100) PRIMARY KEY,
    content varchar(10000),
    date varchar(100)
);'''

cursor.execute(order)
conn.commit()

cursor.close()
conn.close()