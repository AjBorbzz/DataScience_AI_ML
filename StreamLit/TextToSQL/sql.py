import sqlite3

connection = sqlite3.connect("student.db")

cursor = connection.cursor()

table_info = """
Create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT);
"""

cursor.execute(table_info)

cursor.execute('''INSERT INTO STUDENT values('Aj Borbe', 'Cybersecurity', 'A',98)''')
cursor.execute('''INSERT INTO STUDENT values('Mei Borbe', 'QA Analyst', 'C',96)''')
cursor.execute('''INSERT INTO STUDENT values('Cehz Borbe', 'Digital Marketing', 'B',97)''')
cursor.execute('''INSERT INTO STUDENT values('Pring Sta Ana', 'Digital Marketing', 'B',97)''')

data = cursor.execute('''SELECT * FROM STUDENT''')

print("The inserted records are")
for row in data:
    print(row)

connection.commit()
connection.close()

