#!/usr/bin/python
#-*- coding: utf8 -*-
from __future__ import division
import libvirt
import time
from lxml import etree
import xml.etree.ElementTree as ET
import lxml.html as lh
import sys
import string
#conn = libvirt.open(None)
class instance_info:
    def __init__(self):
        self.log_message = ''
        self.vcpu_time=0
        self.node_cpu_time=0
        self.pcputime=0
        self.total_pcpu_valuepre=0
        #self.total_vcpu_valuepre=0
        self.total_pcpu_value=0
        self.net_need_update=True
        self.total_vcpu_value=0
        self.total_vcpu_valuepre=0
        self.cpustatflag=1




        self.log_time = ''
        self.cpu_time = 0
        self.domain_name = ''
        self.machine_state = 0
        self.instance_uuid = ''
        self.instance_memtotal = ''
        self.instance_memcur = ''
        self.cpu_num = ''
        self.net_cards = []
        self.net_card_rxtx= [0]*8
        self.hardware = [[] for i in range(6)]
        self.net_rxrate = 0
        self.net_txrate = 0
        self.cpuusage = 0
        self.disk_stat = []
        self.net_card_info_list = []
class virtual_mach:
    terminated = False;
    def __init__(self):
        self.conn = libvirt.openReadOnly('qemu:///system')
        #self.log_message = ''
        #self.vcpu_time=0
        #self.node_cpu_time=0
        #self.cpustatflag=1
        #self.pcputime=0
        #self.total_pcpu_valuepre=0
        #self.total_vcpu_valuepre=0
        #self.total_pcpu_value=0
        #self.total_vcpu_value=0
        self.instance_info_list=[]

        if self.conn == None:
            print 'Failed to open connection to the hypervisor'
            sys.exit(1)
    def list_dom_ID(self):
        try:
            domid = self.conn.listDomainsID()
            return domid
        except:
            print 'Failed to find the main domain'
            sys.exit(1)
    def create_instances_space_data(self,list_domains):
        for i in range(0,len(list_domains)):
            self.instance_info_list.append(instance_info())
        
    def do_aut_net(self,a,b,c,d):
        """put the rules when we need to log for the rate of the network"""
        return True

    def do_log_routine(self,i,number):
        #net_cards_list=[]
        self.instance_info_list[i].log_message = "************doms %d***************\nLog time:"%number
        self.instance_info_list[i].log_message += time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.instance_info_list[i].log_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        try:
            self.instance_info_list[i].domainx = self.conn.lookupByID(number)
        except:
            self.terminated=True
            return []
        
        domain_info = self.instance_info_list[i].domainx.info()
        self.instance_info_list[i].cpu_time = ((domain_info[4])/1000000000L)
        self.instance_info_list[i].log_message += '\nCPU Time: %d (S)' %self.instance_info_list[i].cpu_time
        self.instance_info_list[i].log_message+="\nInstance Name :"
        try:
            xml_data =  self.instance_info_list[i].domainx.XMLDesc(4)#search type
            self.instance_info_list[i].xml_data = xml_data
        except:
            self.terminated=True
            return []
        after_xml = etree.fromstringlist(xml_data)
        self.instance_info_list[i].domain_name = after_xml.findtext('name')
        self.instance_info_list[i].log_message += self.instance_info_list[i].domain_name 
        try:
            self.instance_info_list[i].machine_state= self.instance_info_list[i].domainx.isActive()
        except:
            self.terminated=True
            return []
        self.instance_info_list[i].log_message +=  '\nmachine status: %d' %self.instance_info_list[i].machine_state
        self.instance_info_list[i].instance_uuid = after_xml.findtext('uuid')
        self.instance_info_list[i].log_message +=  '\nuuid: '+self.instance_info_list[i].instance_uuid
        self.instance_info_list[i].instance_memtotal= after_xml.findtext('memory')
        self.instance_info_list[i].log_message += '\nmemory total: '+after_xml.findtext('memory')
        self.instance_info_list[i].instance_memcur = after_xml.findtext('currentMemory')
        self.instance_info_list[i].log_message += '\ncurrent Memory: '+after_xml.findtext('currentMemory')
        self.instance_info_list[i].cpu_num= after_xml.findtext('vcpu')
        self.instance_info_list[i].log_message += '\nCPU number: '+after_xml.findtext('vcpu')
        #print self.log_message
        #*******************************#
        #root = tree.getroot()
        checklist = ['type','boot','source','mac','target dev']
        #nowantsee = ['network','path']
        tree = ET.ElementTree(after_xml)#here we use afte_xml watch out!
        for j in range(0,len(checklist)):
            for elem in tree.iter(tag=checklist[j]):
                list= elem.attrib.items()
                for p in range(0,len(list)):
                    if list[p][0] =='network' or list[p][0]=='path':
                        continue
                    self.instance_info_list[i].log_message +='\n'+list[p][0]+': '+list[p][1]
                    device_string = list[p][0]+':'+list[p][1]
                    self.instance_info_list[i].hardware[j].append(device_string)
        """
        for elem in tree.iter(tag='target'):
            if 'dev' in elem.attrib:
                #print elem.attrib['dev']
                list_get= elem.attrib.items()
                for i in range(0,len(list_get)):
                    if list_get[i][1][:3] == 'vne':
                        self.instance_info_list[i].log_message += '\nvnet name: '+list_get[i][1]
                        net_cards_list.append(list_get[i][1])
                        self.instance_info_list[i].net_cards.append(list_get[i][1])
            else:
                continue
        """
        for interfaces in tree.find('devices').findall('interface'):

            #for value in tmplist:
            #    print value
            tmp_dic={}
            tmp_dic['dev']=interfaces.find('target').attrib['dev']
            tmp_dic['name']=interfaces.find('alias').attrib['name']
            self.instance_info_list[i].net_cards.append(tmp_dic)
       #root = ET.fromstring(self.instance_info_list[i].xml_data)#here we use afte_xml watch out!
       #devices_root = root.find('devices')

        return [] ##*****only return the last net card information********
    def net_card_statistic(self,j,net_cards):
        #net_card_info = [[0 for jj in xrange(0,10)] for ii in xrange(0,len(self.instance_info_list[j].net_cards))]
        for names in self.instance_info_list[j].net_cards:
            self.do_net_card_statistic(j,names['dev'])
    def do_net_card_statistic(self,j,net_cards):
            #print self.log_message
            #net_de = self.conn.networkLookupByName('default')
            #print self.conn.interfaceLookupByName('vnet0')
            #network = self.conn.listAllNetworks(0)
            #print network[0].name()
            net_card_info = [0]*10
            item_list = ['rx bytes: ','rx packages: ','rx errors: ',\
                    'rx drops: ','tx bytes: ','tx packages: ','tx errors: ',\
                    'tx drops: ']
            try:
                network_info = self.instance_info_list[j].domainx.interfaceStats(net_cards)
            except:
                self.terminated = True
                return

            time.sleep(1)
            rx_b = network_info[0]
            tx_b = network_info[4]           
            try:
                network_info = self.instance_info_list[j].domainx.interfaceStats(net_cards)
            except:
                self.terminated = True
                return
            self.instance_info_list[j].log_message += "\n........%s..............." %net_cards
            for i in range(0,len(network_info)):
                self.instance_info_list[j].log_message += '\n'+item_list[i]+str(network_info[i])
                #net_card_info[i] = str(network_info[i])
                net_card_info[i] = (network_info[i])

            self.instance_info_list[j].net_need_update=self.do_aut_net(network_info[0],rx_b,network_info[4],tx_b)
            self.instance_info_list[j].log_message += "\nrx rate is %d Kbytes "%((network_info[0]-rx_b)/60/2)
            net_card_info[8]  = string.atof('%.2f' %((network_info[0]-rx_b)/60/2))
            net_card_info[9] =  string.atof('%.2f' %((network_info[4]-tx_b)/60/2))
            self.instance_info_list[j].log_message += "\ntx rate is %d Kbytes"%((network_info[4]-tx_b)/60/2)
            self.instance_info_list[j].log_message +="\n................................."
            self.instance_info_list[j].net_card_info_list.append(net_card_info)
    def write_log(self,i):
       # if self.instance_info_list[i].net_need_update == True:
           print self.instance_info_list[i].log_message
           #sys.stdout.write('.')
           #sys.stdout.flush()
    def cpu_mem_statistic(self,i):
        #This is  statistic only for virtual machine
        try:
            dic_value =  self.instance_info_list[i].domainx.getCPUStats(1,0)
        except:
            self.terminated = True
            return
        #self.instance_info_list[i].total_vcpu_valuepre = self.instance_info_list[i].total_vcpu_value
        self.instance_info_list[i].total_vcpu_valuepre = dic_value[0]['cpu_time']
        time.sleep(1)
        try:
            dic_value =  self.instance_info_list[i].domainx.getCPUStats(1,0)
        except:
            self.terminated = True
            return
        #self.instance_info_list[i].total_vcpu_valuepre = self.instance_info_list[i].total_vcpu_value
        self.instance_info_list[i].total_vcpu_value = dic_value[0]['cpu_time']
        usage = 0
        #if self.instance_info_list[i].cpustatflag == 0:
        usage =  (self.instance_info_list[i].total_vcpu_value-self.instance_info_list[i].total_vcpu_valuepre)//100000
   
        #dic_value_list =  self.conn.getCPUStats(0,0)
        #print dic_value_list
        #for i in range(0,len(dic_value_list)):
        #    dic_value =  dic_value_list[i]
        #    self.total_pcpu_valuepre = self.total_pcpu_value
        #    self.total_pcpu_value += dic_value['cpu_time']
        #if self.cpustatflag == 0:
        #    print "****"
        #    print self.total_pcpu_value-self.total_pcpu_valuepre
 #           usage = (self.total_vcpu_value-self.total_vcpu_valuepre)/(self.total_pcpu_value-self.total_pcpu_valuepre)
          #  print usage*100
        self.instance_info_list[i].cpustatflag = 0;
        self.instance_info_list[i].cpuusage = usage
        self.instance_info_list[i].log_message += "\nCPU usage:   " +str(usage)
        #print "****************dom   %i****************" %i
        #print "\nCPU usage:"+str(usage)
        #print "****************************************"
        #print dic_value
        #value_list = dic_value.values()
        #total_node_cpu_time = value_list[0]+value_list[2]+value_list[1]+value_list[3]
        #total_node_cpu_time = value_list[0]+value_list[2]
        #delta_a=0
        #delta_b=0
        #percentage=0
	#if self.vcpu_time!=0:
	#    delta_a = cpu_time_of_dom-self.vcpu_time
    #        print "aaaa"+str(cpu_time_of_dom)
    #        print "bbbb"+str(self.vcpu_time)
            #print "++++++"+str(delta_a)
	 #   self.vcpu_time = cpu_time_of_dom
	 #   delta_b = total_node_cpu_time-self.node_cpu_time
	  #  self.node_cpu_time = total_node_cpu_time
      #      percentage = delta_a/delta_b
	#else:
     #       self.vcpu_time = cpu_time_of_dom
     #       self.node_cpu_time = total_node_cpu_time
        #print delta_a
        #print delta_b
	#print percentage
     #   print cpu_time_of_dom*100/total_node_cpu_time
#print "total"+str(total_node_cpu_time)
#list_dom = self.conn.getCPUStats(0,0)
#list_value =  list_dom.items()
        #for i in range(0,len(list_value)):
        #    vcpu_time_total =  list_value[i]['vcpu_time']
        #    cpu_time_total =  list_value[i]['cpu_time']
        #self.log_message += '\n'+"cpu usage %d"%((vcpu_time_total*100/cpu_time_total))+'%'
        #print vcpu_time_total
        #print cpu_time_total

        #vmem_stats = self.domainx.memoryStats()
        #print vmem_stats
        #node_info = self.conn.getInfo()[1]#get the total memory
        #print node_info
        #print self.conn.getFreeMemory()
        #print self.conn.getMemoryStats(0,0)
        """ 
        print self.conn.listNetworks()
        """

            #print self.log_message
            #print net_de.bridgeName()
            #print net_de.name()
            #print net_de.XMLDesc(0)


            #print net_cards_list
        #re    net_cards_list
        #for elem in tree.iter(tag='target'):
        #    print elem.tag,elem.attrib
        #print self.log_message
        #print root[3].tag
        #print self.log_message


#	def handle_net_work():
    #list_NIC()
   #print vcpus(self);
    def handle_block_devices(self,i):
       #tree = ET.ElementTree(self.instance_info_list[i].xml_data)#here we use afte_xml watch out!
       root = ET.fromstring(self.instance_info_list[i].xml_data)#here we use afte_xml watch out!
       devices_root = root.find('devices')
       for disks in devices_root.findall('disk'):
           disk_data = disks[2].attrib
           try:
               ret = self.instance_info_list[i].domainx.blockStatsFlags(disk_data['dev'],0)
               ret['diskname']=disk_data['dev']
               self.instance_info_list[i].disk_stat.append(ret)
               #print ret
           except:
            self.terminated = True
            return
           self.instance_info_list[i].log_message += "\n..................%s....................." %(disk_data['dev'])
           self.instance_info_list[i].log_message += "\ntotal read write time: " +str(ret['wr_total_times'])
           self.instance_info_list[i].log_message += "\nread operations: " +str(ret['rd_operations'])
           self.instance_info_list[i].log_message += "\nflush_total_times: " +str(ret['flush_total_times'])
           self.instance_info_list[i].log_message += "\nrd_total_times: " +str(ret['rd_total_times'])
           self.instance_info_list[i].log_message += "\nrd_bytes: " +str(ret['rd_bytes'])
           self.instance_info_list[i].log_message += "\nflush_operations: " +str(ret['flush_operations'])
           self.instance_info_list[i].log_message += "\nwr_operations: " +str(ret['wr_operations'])
           self.instance_info_list[i].log_message += "\nwr_bytes: " +str(ret['wr_bytes'])
           self.instance_info_list[i].log_message += "\n..........................................."

       return 




def offer_instance_data():
    main_w = virtual_mach()
    list_doms = main_w.list_dom_ID()
    main_w.create_instances_space_data(list_doms)
    for i in range(0,len(list_doms)):
        if main_w.terminated == False:
            net_card_name = main_w.do_log_routine(i,list_doms[i])
        if main_w.terminated == False:
            main_w.net_card_statistic(i,net_card_name)
        if main_w.terminated == False:
            main_w.cpu_mem_statistic(i)
        if main_w.terminated == False:
            main_w.handle_block_devices(i)
        if main_w.terminated == False:
            main_w.write_log(i)
    return main_w



if __name__ == '__main__':
    
    while True:
        offer_instance_data()
        main_w = virtual_mach()
        list_doms = main_w.list_dom_ID()
        main_w.create_instances_space_data(list_doms)
        for i in range(0,len(list_doms)):
            if main_w.terminated == False:
                net_card_name = main_w.do_log_routine(i,list_doms[i])
            if main_w.terminated == False:
                main_w.net_card_statistic(i,net_card_name)
            if main_w.terminated == False:
                main_w.cpu_mem_statistic(i)
            if main_w.terminated == False:
                main_w.handle_block_devices(i)
            if main_w.terminated == False:
               main_w.write_log(i)
        time.sleep(3)
