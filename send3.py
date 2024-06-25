#!/usr/bin/env python3

import argparse
import sys
import socket
import random
import struct

from time import sleep
from scapy.all import Packet, bind_layers, BitField, ShortField, IntField, XByteField, PacketListField, FieldLenField, Raw, Ether, IP, UDP, sendp, get_if_hwaddr, sniff


class InBandNetworkTelemetry(Packet):
    fields_desc = [ BitField("switchID_t", 0, 31),
                    BitField("ingress_port",0, 9),
                    BitField("egress_port",0, 9),
                    BitField("egress_spec", 0, 9),
                    BitField("priority", 0, 3),
                    BitField("qid", 0, 5),
                    BitField("ingress_global_timestamp", 0, 48),
                    BitField("egress_global_timestamp", 0, 48),
                    BitField("enq_timestamp",0, 32),
                    BitField("enq_qdepth",0, 19),
                    BitField("deq_timedelta", 0, 32),
                    BitField("deq_qdepth", 0, 19)
                  ]
    def extract_padding(self, p):
                return "", p

class nodeCount(Packet):
  name = "nodeCount"
  fields_desc = [ ShortField("count", 0),
                  PacketListField("INT", [], InBandNetworkTelemetry, count_from=lambda pkt:(pkt.count*1))]

def main():

    dstIP0 = '10.10.10.1'
    dstIP1 = '10.10.10.2' 
    dstIP2 = '10.10.10.3'  
    dstMAC = "e0:69:95:72:c8:41"
    iface = 'Wi-Fi'

    bind_layers(IP, nodeCount, proto = 253)
    pkt0 = Ether(src=get_if_hwaddr(iface), dst=dstMAC) / IP(
        dst=dstIP0, proto=253) / nodeCount(count=0, INT=[])
    
    #bind_layers(IP, nodeCount, proto = 254)
    pkt1 = Ether(src=get_if_hwaddr(iface), dst=dstMAC) / IP(
        dst=dstIP1, proto=253) / nodeCount(count=0, INT=[])
    
    #bind_layers(IP, nodeCount, proto = 255)
    pkt2 = Ether(src=get_if_hwaddr(iface), dst=dstMAC) / IP(
        dst=dstIP2, proto=253) / nodeCount(count=0, INT=[])

    while True:
        sendp(pkt0, iface=iface)
        pkt0.show2()
        sendp(pkt1, iface=iface)
        pkt1.show2()
        sendp(pkt2, iface=iface)
        pkt2.show2()
        sleep(1)

if __name__ == '__main__':
    main()