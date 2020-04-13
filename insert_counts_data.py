import os 
import psycopg2

url = os.popen("heroku config:get DATABASE_URL -a eddiecloud").read()[:-1]
conn = psycopg2.connect(url, sslmode = 'require')

cursor = conn.cursor()

#table_columns = '(user_name, temperature)'
order =  ''' INSERT INTO COUNTS_TABLE (district, count)
             VALUES ('港岛', '19'), ('九龙', '349') , ('新界', '429');
         '''

cursor.execute(order)
conn.commit()

count = cursor.rowcount
print(count, "successfully insert")

cursor.close()
conn.close()