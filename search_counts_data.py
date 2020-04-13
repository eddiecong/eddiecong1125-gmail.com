import os 
import psycopg2

url = os.popen("heroku config:get DATABASE_URL -a eddiecloud").read()[:-1]
conn = psycopg2.connect(url, sslmode = 'require')

cursor = conn.cursor()

#table_columns = '(user_name, temperature)'
order =  ''' SELECT * FROM COUNTS_TABLE;'''

cursor.execute(order)
raw = cursor.fetchall()

conn.commit()

count = cursor.rowcount
print(count, "successfully load")
print(raw)
print(raw[0])
print(raw[0][0])

cursor.close()
conn.close()