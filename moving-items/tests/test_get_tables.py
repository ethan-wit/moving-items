import pandas as pd
import sqlite3

conn = sqlite3.connect(r'C:\Users\ethan\Downloads\hashBase.db')
cursor = conn.cursor()

#cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#print(cursor. fetchall())

query_all = '''
SELECT * 
FROM Hashes
'''

#print(cursor.executemany(query_all))

#print(pd.read_sql(query_all, conn))

table_info = cursor.execute('PRAGMA TABLE_INFO(Hashes)')

sql = '''
SELECT HASH
FROM HASHES
'''
cursor.execute(sql)
cur_fet = cursor.fetchone()
print(cur_fet[0])

print(cursor.fetchone())
print(type(cur_fet[0]))

