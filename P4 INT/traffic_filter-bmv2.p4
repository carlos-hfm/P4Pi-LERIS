/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4  = 0x0800;
const bit<16> TYPE_ARP   = 0x0806;
const bit<8>  PROTO_ICMP = 1;
const bit<8>  PROTO_TCP = 6;
const bit<8>  PROTO_UDP = 17;
const bit<8> IP_PROTO = 253;

// ARP RELATED CONSTS
const bit<16> ARP_HTYPE = 0x0001;    // Ethernet Hardware type is 1
const bit<16> ARP_PTYPE = TYPE_IPV4; // Protocol used for ARP is IPV4
const bit<8>  ARP_HLEN  = 6;         // Ethernet address size is 6 bytes
const bit<8>  ARP_PLEN  = 4;         // IP address size is 4 bytes
const bit<16> ARP_REQ = 1;           // Operation 1 is request
const bit<16> ARP_REPLY = 2;         // Operation 2 is reply

#define MAX_HOPS 10

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

typedef bit<31> switchID_v;
typedef bit<9> ingress_port_v;
typedef bit<9> egress_port_v;
typedef bit<9>  egressSpec_v;
typedef bit<48>  ingress_global_timestamp_v;
typedef bit<48>  egress_global_timestamp_v;
typedef bit<32>  enq_timestamp_v;
typedef bit<19> enq_qdepth_v;
typedef bit<32> deq_timedelta_v;
typedef bit<19> deq_qdepth_v;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header arp_t {
  bit<16>   h_type;
  bit<16>   p_type;
  bit<8>    h_len;
  bit<8>    p_len;
  bit<16>   op_code;
  macAddr_t src_mac;
  ip4Addr_t src_ip;
  macAddr_t dst_mac;
  ip4Addr_t dst_ip;
  }

header icmp_t {
    bit<8> icmp_type;
    bit<8> icmp_code;
    bit<16> checksum;
    bit<16> identifier;
    bit<16> sequence_number;
    bit<64> timestamp;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<8>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}
header nodeCount_h{
    bit<16>  count;
}

header InBandNetworkTelemetry_h {
    switchID_v swid;
    ingress_port_v ingress_port;
    egress_port_v egress_port;
    egressSpec_v egress_spec;
    ingress_global_timestamp_v ingress_global_timestamp;
    egress_global_timestamp_v egress_global_timestamp;
    enq_timestamp_v enq_timestamp;
    enq_qdepth_v enq_qdepth;
    deq_timedelta_v deq_timedelta;
    deq_qdepth_v deq_qdepth;
}


struct ingress_metadata_t {
    bit<16>  count;
}

struct parser_metadata_t {
    bit<16>  remaining;
}

struct metadata {
    ingress_metadata_t   ingress_metadata;
    parser_metadata_t   parser_metadata;
}

struct headers {
    ethernet_t   ethernet;
    arp_t        arp;
    ipv4_t       ipv4;
    tcp_t        tcp;
    udp_t        udp;
    icmp_t       icmp;
    nodeCount_h        nodeCount;
    InBandNetworkTelemetry_h[MAX_HOPS] INT;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
          TYPE_ARP: parse_arp;
          TYPE_IPV4: parse_ipv4;
          default: accept;
        }
    }

    state parse_arp {
      packet.extract(hdr.arp);
        transition select(hdr.arp.op_code) {
          ARP_REQ: accept;
          default: accept;
      }
    }


    state parse_ipv4 {
      packet.extract(hdr.ipv4);
      transition select(hdr.ipv4.protocol) {
        PROTO_ICMP: parse_icmp;
        PROTO_TCP: parse_tcp;
        PROTO_UDP: parse_udp;
        IP_PROTO: parse_count;

        default: accept;
      }
    }

    state parse_tcp {
      packet.extract(hdr.tcp);
      transition accept;
    }

    state parse_udp {
      packet.extract(hdr.udp);
      transition accept;
    }

    state parse_icmp {
      packet.extract(hdr.icmp);
      transition accept;
    }

    state parse_count{
        packet.extract(hdr.nodeCount);
        meta.parser_metadata.remaining = hdr.nodeCount.count;
        transition select(meta.parser_metadata.remaining) {
            0 : accept;
            default: parse_int;
        }
    }

    state parse_int {
        packet.extract(hdr.INT.next);
        meta.parser_metadata.remaining = meta.parser_metadata.remaining  - 1;
        transition select(meta.parser_metadata.remaining) {
            0 : accept;
            default: parse_int;
        }
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    table eth_dstMac_filter {
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }


    table eth_srcMac_filter {
        key = {
            hdr.ethernet.srcAddr: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table eth_proto_filter {
        key = {
            hdr.ethernet.etherType: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table ip_proto_filter {
        key = {
            hdr.ipv4.protocol: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table ip_dstIP_filter {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table ip_srcIP_filter {
        key = {
            hdr.ipv4.srcAddr: lpm;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table tcp_srcPort_filter {
        key = {
            hdr.tcp.srcPort: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table tcp_dstPort_filter {
        key = {
            hdr.tcp.dstPort: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table udp_srcPort_filter {
        key = {
            hdr.udp.srcPort: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table udp_dstPort_filter {
        key = {
            hdr.udp.dstPort: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        bit<8> dropped = 0;
        if (hdr.ethernet.isValid()){
          if (eth_srcMac_filter.apply().hit || eth_dstMac_filter.apply().hit || eth_proto_filter.apply().hit)
            dropped = 1;
          if (hdr.ipv4.isValid() && dropped == 0){
            if (ip_srcIP_filter.apply().hit || ip_dstIP_filter.apply().hit || ip_proto_filter.apply().hit)
              dropped = 1;
            if (hdr.tcp.isValid() && dropped == 0){
              if (tcp_srcPort_filter.apply().hit || tcp_dstPort_filter.apply().hit)
                dropped = 1;
            }
            else if (hdr.udp.isValid() && dropped == 0){
              if(udp_srcPort_filter.apply().hit && udp_dstPort_filter.apply().hit)
                dropped = 1;
            }
          }
          if (dropped != 1)
            standard_metadata.egress_spec = (standard_metadata.ingress_port+1)%2;
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    
    action add_swtrace() {
        bit<48> tmp;
        hdr.nodeCount.count = hdr.nodeCount.count + 1;
        hdr.INT.push_front(1);
        hdr.INT[0].setValid();
        hdr.INT[0].swid = 1;
        hdr.INT[0].ingress_port = (ingress_port_v)standard_metadata.ingress_port;
        hdr.INT[0].egress_port = (egress_port_v)standard_metadata.egress_port;
        hdr.INT[0].egress_spec = (egressSpec_v)standard_metadata.egress_spec;
        hdr.INT[0].ingress_global_timestamp = (ingress_global_timestamp_v)standard_metadata.ingress_global_timestamp;
        tmp = (ingress_global_timestamp_v)standard_metadata.ingress_global_timestamp;
        hdr.INT[0].egress_global_timestamp = (egress_global_timestamp_v)standard_metadata.egress_global_timestamp;
        tmp = (egress_global_timestamp_v)standard_metadata.egress_global_timestamp;
        hdr.INT[0].enq_timestamp = (enq_timestamp_v)standard_metadata.enq_timestamp;
        hdr.INT[0].enq_qdepth = (enq_qdepth_v)standard_metadata.enq_qdepth;
        hdr.INT[0].deq_timedelta = (deq_timedelta_v)standard_metadata.deq_timedelta;
        hdr.INT[0].deq_qdepth = (deq_qdepth_v)standard_metadata.deq_qdepth;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 32;

     }

     table swtrace {
        actions = {
                add_swtrace;
                NoAction;
        }
        default_action = add_swtrace();
     }
    
    apply {
        if (hdr.nodeCount.isValid()) {
            add_swtrace();
            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
            hdr.nodeCount.count = hdr.nodeCount.count + 1;
        }
      }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
     }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.arp);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.udp);
        packet.emit(hdr.tcp);
        packet.emit(hdr.icmp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;