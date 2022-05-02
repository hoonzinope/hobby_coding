import pymysql

password = "PASSWORD"
yackhu_db = pymysql.connect(
    user='hoonzi', 
    passwd=password, 
    host='hostAddress', 
    db='hoonzidata', 
    charset='utf8'
)

cursor = yackhu_db.cursor(pymysql.cursors.DictCursor)
select_sql = """
SELECT title, url, type FROM `urldata` ;
"""

cursor.execute(select_sql)
result = cursor.fetchall()
print(result)