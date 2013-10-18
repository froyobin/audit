#!/usr/bin/python
import time
from offer_data import offer_instance_data
import offer_data
import audit_db
import sys
import ConfigParser
import log
import string
import signal
import os

class core_work:
    first = True
    def __init__(self):
        self.pre= offer_data.virtual_mach()
        self.need_loged_instance = []
        self.ins_timestamp={}
        cf=ConfigParser.ConfigParser()
        cf.read('config.ini')
        
        self.HOST_IP = cf.get("database","HOST_IP")
        self.USER = cf.get("database","USER")
        self.PASSWD = cf.get("database","PASSWD")
        self.PORT = string.atoi(cf.get("database","PORT"))
        self.DB = cf.get("database","DB")
        self.DEBUG = cf.get("debug","DEBUG")
        
        
        self.interval = string.atoi(cf.get("speed","interval"))
        paramlist=self.load_all_params(cf)
        self.speedparam = paramlist[0][:]
        self.cpuparam = paramlist[1][:]
        print self.speedparam
        print self.cpuparam
        self.myloghandle = log.mylog("audit.log")

    def load_all_params(self,cf):
        returnlist=[]
        categroy = ["speed","CPU"]
        i=0
        param_list_all = [['maxdkrd','maxdkwr','maxntrd','maxntwr'],['cputime','cpuusage']]
        for paramlist in param_list_all:
            innlist=[]
            for param in paramlist:
                innlist.append(string.atoi(cf.get(categroy[i],param)))
            i = i+1
            returnlist.append(innlist)
        return returnlist
    def removeinstance(self,instance):
        self.instance_need_handle(instance,"DELINS")
        self.disk_need_handle(instance,"DISCONNECT")
        self.net_need_handle(instance,"DISCONNECT")


    def delinstance_to_db_prepare(self):
        i=0
        old = self.old
        new = self.new
        ###WATCH OUT!!!! as this algorithm only consider that at this moment only some 
        ### instances are removed and no instances add at this moment
        ### the extream condition is that at this sample time some instance are created and some are removed!!
        ### like old: 1 3 6 7 and new :1 3 8 . we remove 6 and 7 but add a new instance 8
        while len(old) != len(new):
            try:
                if old[i].instance_uuid == new[i].instance_uuid:
                    i = i+1
                    continue
                else:
                    self.removeinstance(old[i])
                    try:
                        del(self.ins_timestamp[old[i].instance_uuid])
                    except KeyError:
                        self.myloghandle.write_log("trying to del non-exist timestamp","INFO")
                        pass
                    old.remove(old[i])
            except IndexError:
                    self.removeinstance(old[i])
                    
                    
                    try:
                        del(self.ins_timestamp[old[i].instance_uuid])
                    except KeyError:
                        self.myloghandle.write_log("trying to del non-exist timestamp","INFO")
                        pass
                    
                    old.remove(old[i])


    def newaddinstance(self,instance,state):
        if state =="NEW":
            self.instance_need_handle(instance,"ADDNEW")
            self.disk_need_handle(instance,"ATTACHED")
            self.net_need_handle(instance,"ATTACHED")
        if state == "GENERAL":
            self.instance_need_handle(instance,"NORMAL")
            self.disk_need_handle(instance,"INUSE")
            self.net_need_handle(instance,"INUSE")



    def instance_to_db_prepare(self,instance_info_list,number):

        old = self.old
        new = self.new
        i=0
        while len(old) !=len(new):
            try:
                if old[i].instance_uuid == new[i].instance_uuid:
                    i = i+1
                    continue
                else:
                    self.newaddinstance(new[i],"NEW")
                    #self.ins_timestamp[new[i].instance_uuid]=time.time()
                    self.updatetime(new[i].instance_uuid)
                    old.insert(i,new[i])
                    
                
            except IndexError:
                    self.myloghandle.write_log("ADD","DEBUG");
                    self.newaddinstance(new[i],"NEW")
                    #self.ins_timestamp[new[i].instance_uuid]=time.time()
                    self.updatetime(new[i].instance_uuid)
                    old.append(new[i])

    
    def instance_need_handle(self,instance_detail,cases):
        
        
        case_dic = {'ADDNEW':lambda :self.handleinstance(instance_detail,5),\
                'UNKNOW':lambda :self.unknow(),\
                'NORMAL':lambda :self.handleinstance(instance_detail,1),\
                'DELINS':lambda :self.handleinstance(instance_detail,-1)}
        
        case_dic[cases]()

    

    
    def net_need_handle(self,detail,state):
        
        mydb = audit_db.auditDB(self.HOST_IP,self.USER,self.PASSWD,self.PORT,self.DB)
        i=0
        for card_names in detail.net_cards:
            store_list = []
            net_card_info = detail.net_card_info_list[i]
            store_list.append(detail.instance_uuid)
            store_list.append(detail.log_time)
            store_list.append(net_card_info[0]/1000)
            store_list.append(net_card_info[1])
            store_list.append(net_card_info[2])
            store_list.append(net_card_info[3])
            store_list.append(net_card_info[4]/1000)
            store_list.append(net_card_info[5])
            store_list.append(net_card_info[6])
            store_list.append(net_card_info[7])
            store_list.append(net_card_info[8]/1000)
            store_list.append(net_card_info[9]/1000)
            store_list.append(card_names['dev'])
            store_list.append(card_names['name'])
            store_list.append(state)
            """
            if state== "ATTACHED":
                store_list.append("ATTACHED")
            if state =="DISCONNECT":
                store_list.append("DISCONNECT")
            if state =="INUSE":
                store_list.append("INUSE")
            """
            mydb.store_in_db_net_state(store_list)
            if state == "ATTACHED":
                self.myloghandle.write_log(" ADD NEW NET CARD %s into DATABASE SUCCESSFULLY"  % card_names['name'],"INFO")
            if state == "DISCONNECT":
                self.myloghandle.write_log("DISCONNECT NET CARD %s into DATABASE SUCCESSFULLY"  %card_names['name'],"INFO")
        mydb.disconnect()


    def disk_need_handle(self,detail,state):
       
        mydb = audit_db.auditDB(self.HOST_IP,self.USER,self.PASSWD,self.PORT,self.DB)
        for diskinfo in detail.disk_stat:
            store_list = []
            store_list.append(detail.instance_uuid)
            store_list.append((diskinfo['wr_total_times'])/1000000000L)
            store_list.append(diskinfo['rd_operations'])
            store_list.append((diskinfo['flush_total_times'])/10000L)
            store_list.append(diskinfo['rd_total_times']/10000L)
            store_list.append(diskinfo['rd_bytes']/1000L)
            store_list.append(diskinfo['flush_operations'])
            store_list.append(diskinfo['wr_operations'])
            store_list.append(diskinfo['wr_bytes']/1000L)
            store_list.append(diskinfo['diskname'])
            store_list.append(state)
            """
            if state== "ATTACHED":
                store_list.append("ATTACHED")
            if state =="DISCONNECT":
                store_list.append("DISCONNECT")
            if state =="INUSE":
                store_list.append("INUSE")
            """
            store_list.append(detail.log_time)
            store_list.append(diskinfo['wr_speed'])
            store_list.append(diskinfo['rd_speed'])
            mydb.store_in_db_disk_state(store_list)
            if state == 5:
                self.myloghandle.write_log( "FIND NEW DISK %s into DATABASE SUCCESSFULLY"  % (diskinfo['diskname']),"INFO")
            if state == -1:
                self.myloghandle.write_log("DISCONNECT DISK %s into DATABASE SUCCESSFULLY"  % (diskinfo['diskname']),"INFO")
        mydb.disconnect()

    def handleinstance(self,detail,state):
        store_list=[]
        store_list.append(detail.instance_uuid)
        store_list.append(detail.log_time)
        store_list.append(detail.cpu_time)
        store_list.append(detail.domain_name)
        if state ==1:
            store_list.append(detail.machine_state)
        else:
            store_list.append(state)
        store_list.append(detail.instance_memtotal)
        store_list.append(detail.instance_memcur)
        store_list.append(detail.cpu_num)
        store_list.append(detail.hardware[0][0].split(':')[1])
        store_list.append(detail.hardware[0][1].split(':')[1])
        store_list.append(detail.cpu_time)
        mydb = audit_db.auditDB(self.HOST_IP,self.USER,self.PASSWD,self.PORT,self.DB)
        mydb.store_in_db_static(store_list)
        mydb.disconnect()
        if state == 5:
            self.myloghandle.write_log("ADD NEW INSTANCE %s into DATABASE SUCCESSFULLY"  % detail.domain_name,"INFO")
        if state == -1:
            self.myloghandle.write_log("TERMINATE INSTANCE %s into DATABASE SUCCESSFULLY"  % detail.domain_name,"INFO")
        if state == 1:
            self.myloghandle.write_log("GENERAL INSTANCE %s INFO" % detail.instance_uuid,"INFO")

        
        




    def debug_log(self,msg):
        if self.DEBUG == True:
            sys.stdout.write(msg)
            sys.stdout.flush()


    def unknow(self):
        self.myloghandle.write_log("ERROR UNKNOW command","ERROR")

    
    def loged_to_db(self,instance):
        self.newaddinstance(instance,"GENERAL")

    def updatetime(self,key):
        self.ins_timestamp[key]=time.time()
    
    def log_instance(self,key):
        update_list = self.new
        for instance in update_list:
            if instance.instance_uuid == key:
                self.loged_to_db(instance)
                
        self.updatetime(key)



    def expire_time_check(self,old,new):
        timenow = time.time()
        for (k,updatedtime) in self.ins_timestamp.items():
            if timenow-updatedtime >(60*self.interval):
                self.log_instance(k)
            else:
                continue


    def check_by_comparison(self,old,new):
        disk_status_add_remove=False
        for i in range(0,len(new)):
        
            #########disk add remove check#############
            if len(new[i].disk_stat)>len(old[i].disk_stat):
                self.myloghandle.write_log("VOLUME ADD DETECTED","INFO")
                self.add_to_log_list(i)
                disk_status_add_remove = True
                continue
            if len(new[i].disk_stat)<len(old[i].disk_stat):
                self.myloghandle.write_log("VOLUME REMOVE DETECTED","INFO")
                self.add_to_log_list(i)
                disk_status_add_remove = True
                continue
            #########disk add remove check END#############
            if disk_status_add_remove == True:
                continue
            ####most interesting way of handle data
            checklist=['machine_state','instance_memtotal','instance_memcur','cpu_time',]
            for j in checklist:
                mstrnew = 'a=new[%d].%s' %(i,j)
                exec mstrnew
                mstrold = 'b=old[%d].%s' %(i,j)
                exec mstrold
                if a!=b:
                   self.myloghandle.write_log(("%s FROM %d TO %d"%(j,b,a)),"INFO")
                   self.add_to_log_list(i)
                break
            


    
    def add_to_log_list(self,i):
        try :
            self.need_loged_instance.index(i)
        except ValueError:
            self.need_loged_instance.append(i)


    def check_by_statistics(self,new):
        i=0       
        disk_found=False
        net_found = False
        for i in range(0,len(new)):
            #check disk first
            for disk in new[i].disk_stat:
                if disk['wr_speed']>self.speedparam[1] or disk['rd_speed'] >self.speedparam[0]:
                    self.add_to_log_list(i)
                    self.myloghandle.write_log("exceed block speed detected!","INFO")
                    # any of the disk that meet the requirement will cause the whole instance to be logged
                    disk_found = True
                    break
            if disk_found == True:
                continue
        # new we check the network
            for netcard in new[i].net_card_info_list:
                if (netcard[8]>self.speedparam[2]) or (netcard[9]>self.speedparam[3]):
                    net_found=True
                    self.myloghandle.write_log("exceed net speed detected!","INFO")
                    self.add_to_log_list(i)
                    break
                if net_found== True:
                    continue
        
        #return self.need_loged_instance

    def loged_each_instance(self,new):
        
        print self.need_loged_instance

        del(self.need_loged_instance[:])


    def inspect_each_instance(self,old,new):
        
        #we first check the static values of each instance
            #self.myloghandle.write_log("new %d"%len(eachinstance.disk_stat),"INFO")
            #self.myloghandle.write_log("old %d"%len(old[i].disk_stat),"INFO")
            
        self.check_by_statistics(new)
        

        self.check_by_comparison(old,new)

        self.loged_each_instance(new)

        self.expire_time_check(old,new)



    def check_instance_start_stop(self,tmp,pre):
        if len(self.new) > len(self.old):
            number = len(self.new) - len(self.old)
            self.instance_to_db_prepare(tmp.instance_info_list,number)
        else:
            if len(self.new) < len(self.old):
                self.delinstance_to_db_prepare()
            else:
                self.inspect_each_instance(self.old,self.new)
                #print tmp.instance_info_list[1].hardware[0][0].split(':')[1]
                #tmp = self.old.instance_info_list[:]
                #tmp = self.new.instance_info_list[:]
                #self.debug_log("do something")
        return
    
    def create_timestamp(self):
        for instance in self.old:
            self.ins_timestamp[instance.instance_uuid] = time.time()
    def core_loop(self):
        #pre = offer_data.virtual_mach()
        while True:
            if self.first ==True:
                self.first = False
                pre = offer_instance_data()
                self.old = pre.instance_info_list
                self.create_timestamp()
                self.myloghandle.write_log("System started.....","INFO")
                continue
            else:
                tmp = offer_instance_data()
                self.new = tmp.instance_info_list
                
                """
                 do something
                """
                self.check_instance_start_stop(tmp,pre)

                pre= tmp
                self.old = pre.instance_info_list
            time.sleep(2)
def signalhandle(signum,fram):
    print "USER TERMINATED"
    os.system("stty -F /dev/tty echo") 
    os.system("stty -F /dev/tty -cbreak")

    sys.exit()
if __name__ == '__main__':
    signal.signal(signal.SIGINT,signalhandle)
    do_work = core_work()
    do_work.core_loop()
