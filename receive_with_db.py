#!/usr/bin/env python3

from scapy.all import Packet, bind_layers, BitField, ShortField, IntField, Ether, IP, UDP, sendp, get_if_hwaddr, sniff, PacketListField

import os
from influxdb_client_3 import InfluxDBClient3, Point

import sys


class InBandNetworkTelemetry(Packet):
    fields_desc = [
        BitField("switchID_t", 0, 31),
        BitField("ingress_port", 0, 9),
        BitField("egress_port", 0, 9),
        BitField("egress_spec", 0, 9),
        BitField("ingress_global_timestamp", 0, 48),
        BitField("egress_global_timestamp", 0, 48),
        BitField("enq_timestamp", 0, 32),
        BitField("enq_qdepth", 0, 19),
        BitField("deq_timedelta", 0, 32),
        BitField("deq_qdepth", 0, 19)
    ]
    """any thing after this packet is extracted is padding"""

    def extract_padding(self, p):
        return "", p


class NodeCount(Packet):
    name = "nodeCount"
    fields_desc = [ShortField("count", 0),
                   PacketListField("INT", [], InBandNetworkTelemetry, count_from=lambda pkt: (pkt.count * 1))]


class INTP4Pi:
    def __init__(self):
        self.downlink_enq_qdepth = 0
        self.downlink_deq_qdepth = 0
        self.downlink_deq_timedelta = 0
        self.uplink_enq_qdepth = 0
        self.uplink_deq_qdepth = 0
        self.uplink_deq_timedelta = 0


def handle_pkt(pkt, client, database):
    # pkt.show2()
    #print("Packet - INT Header:")
    if NodeCount in pkt:
        dataINT = INTP4Pi()
        for int_pkt in pkt[NodeCount].INT:
            telemetry = int_pkt[InBandNetworkTelemetry]
            if telemetry.switchID_t == 1:
                print("Downlink - Interface WiFi")
                dataINT.downlink_enq_qdepth = telemetry.enq_qdepth
                dataINT.downlink_deq_qdepth = telemetry.deq_qdepth
                dataINT.downlink_deq_timedelta = telemetry.deq_timedelta
            else:
                print("Uplink - Interface Cabeada")
                dataINT.uplink_enq_qdepth = telemetry.enq_qdepth
                dataINT.uplink_deq_qdepth = telemetry.deq_qdepth
                dataINT.uplink_deq_timedelta = telemetry.deq_timedelta

            print("Enqueue Timestamp:", telemetry.enq_timestamp)
            print("Enqueue Queue Depth:", telemetry.enq_qdepth)
            print("Dequeue Timedelta:", telemetry.deq_timedelta)
            print("Dequeue Queue Depth:", telemetry.deq_qdepth)
            if telemetry.switchID_t == 1:
                print("------------------------------")
            else:
                print("\n")

        if pkt[NodeCount].count == 2:
            point = (
                Point("Experimentos")
                .tag("ID", sys.argv[1])
                .field("downlink enq_qdepth", dataINT.downlink_enq_qdepth)
                .field("downlink deq_qdepth", dataINT.downlink_deq_qdepth)
                .field("downlink deq_timedelta", dataINT.downlink_deq_timedelta)
                .field("uplink enq_qdepth", dataINT.uplink_enq_qdepth)
                .field("uplink deq_qdepth", dataINT.uplink_deq_qdepth)
                .field("uplink deq_timedelta", dataINT.uplink_deq_timedelta)
            )
            #client.write(database=database, record=point)
        


def connectDB():
    token = os.environ.get("INFLUXDB_TOKEN")
    org = "Research"
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"

    client = InfluxDBClient3(host=host, token=token, org=org)
    #client = 1
    return client


def main():
    if len(sys.argv) == 2:
        client = connectDB()
        #client = 1
        database = "CG-Monitoramento"

        iface = 'Wi-Fi'  # interface de entrada, alterar para Ethernet quando necessário

        bind_layers(IP, NodeCount, proto=253)  # Correção na nomenclatura da classe
        bind_layers(Ether, IP)

        print("Esperando pacotes...")
        sniff(filter="ip proto 253", iface=iface, prn=lambda x: handle_pkt(x, client, database))
    else:
        print("Espera-se 1 argumento: ID do experimento...")


if __name__ == '__main__':
    main()
