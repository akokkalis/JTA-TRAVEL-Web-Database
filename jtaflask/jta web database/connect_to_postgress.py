db_host = 'ec2-54-235-139-166.compute-1.amazonaws.com'
db_name = 'd7jhk67r50asm2'
db_user = 'wwnmnjlbecvvmw'
db_pass= '165cbb7be54b5378524ff18d83c157c408c2649f2b37bf2e0e4d094a828914ec'

import psycopg2

conn = psycopg2.connect(dbname = db_name, user = db_user, password = db_pass, host = db_host)
cur = conn.cursor()
cur.execute('SELECT * FROM guides;')
print(cur.fetchall())
conn.commit()


cur.close()
conn.close()