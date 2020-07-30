import sqlite3
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB = os.path.join(BASE_DIR, 'test_db.sqlite')

SQLS = [
    # """SELECT/**/*/**/FROM/**/users""",
    # """DROP/**/TABLE/**/faketable"""
    # """/*! MYSQL Special SQL *"""
    # """SELECT /*!32302 1/0,*/ 1 FROM users"""
    # """10; DROP TABLE members/*"""
    # """SELECT * FROM users; DROP faketable --""",
    # """SELECT IF(1=1,'true','false')"""
    # """IF (1=1) SELECT 'true' ELSE SELECT 'false'"""
    # """SELECT * FROM users WHERE %s""" % hex(1)
    # """SELECT 0x5045"""
    # """SELECT name + '-' + password FROM users"""
    # """SELECT name || '-' || password FROM users"""
    # """SELECT CONCAT('0x',HEX('c:\\boot.ini'))"""
    # """SELECT LOAD_FILE(0x633A5C626F6F742E696E69)"""
    # """SELECT name, password FROM users UNION ALL SELECT name, followers FROM friends"""
    # """SELECT name FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name = 'tablenameforcolumnnames')"""
    """SELECT table_name, column_name FROM information_schema.columns WHERE table_name='tablename'"""
]

PARTIALS = [
    # """SELECT * FROM users where id=%s""" % """3;DROP members --"""
    # """SELECT * FROM users WHERE id='%s""" % """' UNION SELECT 1, 'test', 'test', 1 --"""
    # """SELECT * FROM users GROUP BY name %s""" % """' HAVING 1=1 --"""
    # """SELECT * FROM users %s""" % """GROUP BY users.name, users.password HAVING 1=1 --"""
]

SQLS = SQLS + PARTIALS

db = sqlite3.connect(DB)

sql = random.choice(SQLS)
cursor = db.execute(sql)

print('SQL statement:', sql)
print(list(cursor))
