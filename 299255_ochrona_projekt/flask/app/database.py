


import sqlite3
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
# cursor.execute("DROP TABLE user")
# cursor.execute("DROP TABLE note")
# cursor.execute("CREATE TABLE user(id INTEGER PRIMARY KEY AUTOINCREMENT, login varchar(80) NOT NULL UNIQUE, password varchar(200) )")
# cursor.execute("CREATE TABLE note(id INTEGER PRIMARY KEY AUTOINCREMENT, content varchar(1000) NOT NULL UNIQUE, permission varchar(200) )")




