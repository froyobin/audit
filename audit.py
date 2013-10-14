#!/usr/bin/python
#-*- coding: utf8 -*-
from __future__ import division
import libvirt
import time
from lxml import etree
import xml.etree.ElementTree as ET
import lxml.html as lh
import sys
#conn = libvirt.open(None)
class instance_info:
    def __init__(self):
        self.log_message = ''
        self.vcpu_time=0
        self.node_cpu_time=0
        self.cpustatflag=1
        self.pcputime=0
        self.total_pcpu_valuepre=0
        self.total_vcpu_valuepre=0
        self.total_pcpu_value=0
        self.total_vcpu_value=0
        self.net_need_update=True
        
class virtual_mach:
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
            self.instance_info_list.append(instance_info)
        

    def do_log_routine(self,i,number):
        net_cards_list=[]
        self.instance_info_list[i].log_message = "************doms %d***************\nLog time:"%number
        self.instance_info_list[i].log_message += time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.instance_info_list[i].domainx = self.conn.lookupByID(number)
        #domain_info = self.instance_info_list[i].domainx.info()
        self.instance_info_list[i].log_message+="\nDomain Name :"
        xml_data =  self.instance_info_list[i].domainx.XMLDesc(4)#search type
        afte_xml = etree.fromstringlist(xml_data)
        self.instance_info_list[i].log_message += afte_xml.findtext('name') 
        self.instance_info_list[i].log_message += '\nmachine status: %d'%self.instance_info_list[i].domainx.isActive()
        self.instance_info_list[i].log_message += '\nuuid :'+afte_xml.findtext('uuid')
        self.instance_info_list[i].log_message += '\nmemory total: '+afte_xml.findtext('memory')
        self.instance_info_list[i].log_message += '\ncurrent Memory: '+afte_xml.findtext('currentMemory')
        self.instance_info_list[i].log_message += '\nCPU number: '+afte_xml.findtext('vcpu')
        #print self.log_message
        #*******************************#
        #root = tree.getroot()
        checklist = ['type','boot','source','mac']
        #nowantsee = ['network','path']
        tree = ET.ElementTree(afte_xml)#here we use afte_xml watch out!
        for j in range(0,len(checklist)):
            for elem in tree.iter(tag=checklist[j]):
                list= elem.attrib.items()
                for i in range(0,len(list)):
                    if list[i][0] =='network' or list[i][0]=='path':
                        continue
                    self.instance_info_list[i].log_message +='\n'+list[i][0]+': '+list[i][1]
        for elem in tree.iter(tag='target'):
            if 'dev' in elem.attrib:
                #print elem.attrib['dev']
                list_get= elem.attrib.items()
                for i in range(0,len(list_get)):
                    if list_get[i][1][:3] == 'vne':
                        self.instance_info_list[i].log_message += '\nvnet name: '+list_get[i][1]
                        net_cards_list.append(list_get[i][1])
            else:
                continue
        return list_get[i][1]
    def net_card_statistic(self,net_cards):
            #print self.log_message
            #net_de = self.conn.networkLookupByName('default')
            #print self.conn.interfaceLookupByName('vnet0')
            #network = self.conn.listAllNetworks(0)
            #print network[0].name()
            item_list = ['rx bytes: ','rx packages: ','rx errors: ',\
                    'rx drops: ','tx bytes: ','tx packages: ','tx errors: ',\
                    'tx drops: ']

            network_info = self.domainx.interfaceStats(net_cards)
            time.sleep(1)
            rx_b = network_info[0]
            tx_b = network_info[4]           
            network_info = self.domainx.interfaceStats(net_cards)
            for i in range(0,len(network_info)):
                self.log_message += '\n'+item_list[i]+str(network_info[i])
            self.net_need_update=self.do_aut_net(network_info[0],rx_b,network_info[4],tx_b)
            self.log_message += "\nrx rate is %d Kbytes "%((network_info[0]-rx_b)/60/2)
            self.log_message += "\ntx rate is %d Kbytes"%((network_info[4]-tx_b)/60/2)
    def do_aut_net(self,a,b,c,d):
        """put the rules when we need to log for the rate of the network"""
        return True
    def write_log(self,i):
       # if self.instance_info_list[i].net_need_update == True:
            print self.instance_info_list[i].log_message
    def cpu_mem_statistic(self):
        #This is  statistic only for virtual machine
        dic_value =  self.domainx.getCPUStats(1,0)
        self.total_vcpu_valuepre = self.total_vcpu_value
        self.total_vcpu_value = dic_value[0]['cpu_time']
        usage = 0
        if self.cpustatflag == 0:
            usage =  (self.total_vcpu_value-self.total_vcpu_valuepre)//10000000
   
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
        self.cpustatflag = 0;
        self.log_message += "\nCPU usage:   " +str(usage)
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
if __name__ == '__main__':
    main_w = virtual_mach()
    while True:
        list_doms = main_w.list_dom_ID()
        main_w.create_instances_space_data(list_doms)
        for i in range(0,len(list_doms)):
            net_card_name = main_w.do_log_routine(i,list_doms[i])
            #main_w.net_card_statistic(net_card_name)
            #main_w.cpu_mem_statistic()
            main_w.write_log(i)
            #handle_net_work()
        time.sleep(3)
