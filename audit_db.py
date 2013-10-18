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
        self.conn.commit()
    

    def store_in_db_disk_state(self,store_data):
        self.cur.execute('insert into disk_status(UUID,TOTAL_RW_TIME,\
                READ_OP,FLUSH_TOTAL_TIMES,\
                RD_TOTAL_TIMES,RD_KB,FLUSH_OPS,\
                WR_OPS,WR_KB,DISKNAME,DISK_STAT,LOGTIME,\
                DISK_WR_SPEED,DISK_RD_SPEED) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',store_data)
        self.conn.commit()
    
    def store_in_db_net_state(self,store_data):
        self.cur.execute('insert into net_cards(UUID,LOG_TIME,RX_KB,\
                RX_PACKAGES,RX_ERROR,RX_DROP,\
                TX_KB,TX_PACKAGES,TX_ERROR,TX_DROP,\
                RX_RATE_KB,TX_RATE_KB,DEV_NAME,ALIAS_NAME,STATE) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',store_data)
        self.conn.commit()
                
    def disconnect(self):
        self.cur.close()
        self.conn.close()
    


if __name__ == '__main__':
    mydb = auditDB(HOST_IP,USER,PASSWD,PORT,DB)
    myd=[3332,'hell']
    mydb.store_in_db(myd)

