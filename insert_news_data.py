import os 
import psycopg2

url = os.popen("heroku config:get DATABASE_URL -a eddiecloud").read()[:-1]
conn = psycopg2.connect(url, sslmode = 'require')

cursor = conn.cursor()

#table_columns = '(user_name, temperature)'
order =  ''' INSERT INTO NEWS_TABLE (title, content, date)
             VALUES ('疫情速递', '衞生署衞生防護中心公布，截至今日（四月八日）下午四時，中心正調查25宗新增2019冠狀病毒病確診個案，至今本港個案累計961宗（包括960宗確診個案和一宗疑似個案）。今日公布的新增個案涉及11男14女，年齡介乎兩個月至71歲，當中15人曾於潛伏期身處外地，四人為留學生。','4月9日');'''

cursor.execute(order)
conn.commit()

count = cursor.rowcount
print(count, "successfully insert")

cursor.close()
conn.close()