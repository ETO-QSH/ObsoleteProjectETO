
import sqlite3

def sqlite3_get_last_data(db_path,sql):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try: 
        cur.execute(sql) 
        
        person_all = cur.fetchall()
        last_data = person_all[-3]

        print(last_data)
        print("type(last_data):", type(last_data))
        print("last_data:", )
        
        last_text = last_data[6]
        return last_text

    except Exception as e:
        print('查询失败:', e)

    finally:
        cur.close()
        con.close()


db_path = 'D:\MailMasterData\pb09801651@126.com_9966\search.db'
sql = 'select * from Search_content'

last_text = sqlite3_get_last_data(db_path, sql)
print(last_text)
