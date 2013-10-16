#!/usr/bin/python
import MySQLdb
HOST_IP='192.168.172.10'
USER='AuditUser'
PASSWD='1234'
PORT=3306
DB='audit_db'

class auditDB:
    def __init__(self,HOST_IP,USER,PASSWD,PORT,DB):
        try:
            self.conn=MySQLdb.connect(host=HOST_IP,user=USER,passwd=PASSWD,port=PORT,db=DB)
            self.cur=self.conn.cursor()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    def store_in_db(self,store_data):
        self.cur.execute('insert into test_table(value,\
                msg) values(%s,%s)',store_data)
        self.conn.commit()
    
    def store_in_db_static(self,store_data):
        self.cur.execute('insert into audit_static_data(UUID,LOGED_TIME,CPUTIME,\
                INSTANCE_NAME,MACHINE_STATE,\
                MEM_TOTAL,MEM_CUR,\
                CPU_NUM,ARCH,\
                MACHINE,CPU_USAGE) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',store_data)
        #self.cur.execute('insert into audit_static_data(UUID,LOGED_TIME) values(%s,%s)',store_data)
        self.conn.commit()
    
    def disconnect(self):
        self.cur.close()
        self.conn.close()
    


if __name__ == '__main__':
    mydb = auditDB(HOST_IP,USER,PASSWD,PORT,DB)
    myd=[3332,'hell']
    mydb.store_in_db(myd)

