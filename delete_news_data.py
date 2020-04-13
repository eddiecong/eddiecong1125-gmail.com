import os 
import psycopg2

url = os.popen("heroku config:get DATABASE_URL -a eddiecloud").read()[:-1]
conn = psycopg2.connect(url, sslmode = 'require')

cursor = conn.cursor()

#table_columns = '(user_name, temperature)'
order =  ''' DROP TABLE NEWS_TABLE;'''

cursor.execute(order)
conn.commit()

print("successfully delete")


cursor.close()
conn.close()