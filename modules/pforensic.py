#!/usr/bin/env python2.7
#coding=UTF-8

# Copyright (c) 2016 Angelo Moura
#
# This file is part of the program PytheM
#
# PytheM is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

from scapy.all import *
import sys
import os
import termcolor
from utils import color

class PcapReader(object):

	name = "Simple pcap analyzer"
	desc = "Use some functions to analyze a pcap file"
	version = "0.3"

	def __init__(self, file):
		self.file = file
		self.packets = rdpcap(file)

	def printHelp(self):
		print
		print color("	[ PytheM - Leitor Forense de arquivos pcap ]","grey")
		print
		print color("	ARQUIVO - [ {} ]".format(self.file),"red")
		print
		print
		print color("[*] help:   			Print the help message","blue")
		print
		print
		print color("[*] clear:			Clean the screen, same as GNU/Linux OS 'clear'","blue")
		print
		print
		print color("[*] exit/quit:			Return to pythem","blue")
		print
		print
		print color("[*] show:			Display all the packets and their index numbers.","blue")
		print
		print
		print color("[*] conversations:		Display pictogram with conversations between hosts from the analyzed file.","blue")
		print
		print
		print color("[*] filter			Run the PytheM custom filter in the packets.","blue")
		print
		print
		print color("[*] packetdisplay [num]:	Display the full content of index selected packet.","blue")
		print
		print
		print color("[*] packetload [num]:		Display the payload of index selected packet.","blue")
		print


	def filter_lookup(self,p):
		if IP in p:
			ip_src = p[IP].src
			ip_dst = p[IP].dst
			if p.haslayer(Raw):
				print
				print "----------------------------------------------[PAYLOAD]-------------------------------------------------------\n"
				print str(ip_src) + "---->" + str(ip_dst) + "\n" 
				print "\n".join(p.sprintf("{Raw:%Raw.load%}\n").split(r"\r\n")) 		
				print "-------------------------------------------------------------------------------------------------------------"
				print

	def custom_filter(self,packets):
		for p in packets:
			if p.haslayer(Ether):
				pkt = "\r\n\n\n--------------------------[Packet]--------------------------\r\n"
				end = "\r\n------------------------------------------------------------\r\n"

			if p.haslayer(ARP):

				if p[ARP].op == 1:
					print pkt
					print "[ARP] Request: " + p[ARP].psrc + " who has " + p[ARP].pdst + "?"
					print end
				if p[ARP].op == 2:
					print pkt
					print "[ARP] Response: " + p[ARP].psrc + " is at " + p[ARP].hwsrc
					print end

			elif p.haslayer(IP):
				ip_src = p[IP].src
				ip_dst = p[IP].dst

				if p.haslayer(UDP):
					sport = p[UDP].sport
					dport = p[UDP].dport
					if p.haslayer(DNS) and p.getlayer(DNS).qr == 0:
		        		        pkt += "[IPv4] {}:{} ----> {}:{} \n".format(ip_src,sport,ip_dst,dport)
						print pkt
						print "[DNS Query]"
						print "[DNS] qname: {}".format(p.getlayer(DNS).qd.qname)
						print end

					elif p.haslayer(DNSRR):
		        		        pkt += "[IPv4] {}:{} <---- {}:{} \n".format(ip_dst,dport,ip_src,sport)
						print pkt
						print "[DNS Layer]"
						print
						print "[DNS Response]"
						print "[DNS] rrname: {} = rdata: {}".format(p[DNSRR].rrname,p[DNSRR].rdata)
						print end



				elif p.haslayer(TCP) and p.haslayer(Raw):
					flags = {'F':'FIN','S':'SYN','R':'RST','P':'PSH','A':'ACK','U':'URG','E':'ECE','C':'CWR'}
					dport = p[TCP].dport
					sport = p[TCP].sport
					ack = p[TCP].ack
					seq = p[TCP].seq
					preflag = [flags[x] for x in p.sprintf('%TCP.flags%')]
					flag = "/".join(preflag)
					chksum = p[TCP].chksum
					load = p[Raw].load
					if load.startswith('GET') or load.startswith('POST') or load.startswith('HTTP') or "230" in load:
		        		        pkt += "[IPv4] {}:{} ----> {}:{} | {} \n".format(ip_src,sport,ip_dst,dport,flag)
						print pkt
						print "[TCP - LOAD]"
						print "[Raw] Load:\n\n{}".format(load)
						print end

				elif p.haslayer(ICMP):
					type = p[ICMP].type
					code = p[ICMP].code
		        		pkt += "[IPv4] {}:{} ----> {}:{} \n".format(ip_src,sport,ip_dst,dport)
					print pkt
					print "[ICMP] Type: {}".format(type)
					print end

	def start(self):
		while True:
			try:
				console = termcolor.colored("pforensic>","yellow", attrs=["bold"])
				self.command = raw_input("{} ".format(console))
				self.argv = self.command.split()
				self.input_list = [str(a) for a in self.argv]

				try:
                                	if self.input_list[0]  == 'packetdisplay':
                                	        try:
                                                	self.packets[int(self.input_list[1])].show()
						except Exception as e:
                            				print "[!] Exception caught: {}".format(e)

					elif self.input_list[0] == "filter":
						try:
							self.custom_filter(self.packets)
						except Exception as e:
							print "[!] Exception caught: {}".format(e)

					elif self.input_list[0] == 'packetload':
						try:
							print "[+] Packet {} payload: ".format(self.input_list[1])
							self.filter_lookup(self.packets[int(self.input_list[1])])

						except Exception as e: 
                            				print "[!] Exception caught: {}".format(e)

					elif self.input_list[0]  == 'exit':
						break
					elif self.input_list[0] == 'quit':
						break
					elif self.input_list[0] == 'help':
						self.printHelp()
					elif self.input_list[0] == 'clear':
						os.system('clear')
					elif self.input_list[0] == 'ls':
						os.system('ls')
					elif self.input_list[0] == 'summary':
						try:
                            				self.packets.summary()
						except Exception as e: 
                            				print "[!] Exception caught: {}".format(e)
					elif self.input_list[0] == 'show':
						try:
                            				self.packets.show()
						except Exception as e: 
                            				print "[!] Exception caught: {}".format(e)	
					elif self.input_list[0] == 'conversations':
						try:
                            				self.packets.conversations()
						except Exception as e: 
                            				print "[!] Exception caught: {}".format(e)
					else:
						print "[-] Select a valid option."				

                        	except IndexError:
					pass
			except KeyboardInterrupt:
                               	 break





