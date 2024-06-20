/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV6 = 0x86dd;
const bit<16> TYPE_IPV4  = 0x0800;
const bit<8> IP_PROTO = 253;
const bit<8> PROTO_TCP = 6;
const bit<8>  PROTO_UDP = 17;
const bit<2>  RTP_VERSION = 2;
const bit<1>  RTP_PADDING = 0;
const bit<1>  RTP_EXTENSION = 1;
const bit<4>  RTP_CSRC_COUNTER = 0;


#define PKT_INSTANCE_TYPE_NORMAL 0
#define PKT_INSTANCE_TYPE_INGRESS_CLONE 1
#define PKT_INSTANCE_TYPE_EGRESS_CLONE 2
#define PKT_INSTANCE_TYPE_COALESCED 3
#define PKT_INSTANCE_TYPE_INGRESS_RECIRC 4


#define MAX_HOPS 10

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> flowID_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
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

header ipv6_t {
    bit<4>    version;
    bit<8>    trafficClass;
    bit<20>   flowLabel;
    bit<16>   payloadLen;
    bit<8>    nextHdr;
    bit<8>    hopLimit;
    bit<128>  srcAddr;
    bit<128>  dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

header rtp_t {
    bit<2> version;
    bit<1> padding;
    bit<1> extension;
    bit<4> csrcCounter;
    bit<1> marker;
    bit<7> payloadType;
    bit<16> seqNumber;
    bit<32> timestamp;
    bit<32> ssrcID;
    bit<16> csrcID;

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
    bit<32>  flowID;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    ipv6_t       ipv6;
    udp_t        udp;
    rtp_t        rtp;
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
          TYPE_IPV4: parse_ipv4;
          TYPE_IPV6: parse_ipv6;
          default: accept;
        }
    }

    state parse_ipv4 {
      packet.extract(hdr.ipv4);
      transition select(hdr.ipv4.protocol) {
        PROTO_UDP: parse_udp;
        default: accept;
      }
    }

    state parse_ipv6 {
      packet.extract(hdr.ipv6);
      transition select(hdr.ipv6.nextHdr) {
        PROTO_UDP: parse_udp;
        default: accept;
      }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition parse_rtp;
    }

    state parse_rtp {
        packet.extract(hdr.rtp);
        transition accept;
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

    register<bit<3>>(0x1fffe) flow_queue;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action find_flowID_ipv4() {
        bit<1> base = 0;
        bit<16> max = 0xffff;
        bit<32> hash_IP;
        bit<32> hash_port;

        hash(
             hash_IP,
             HashAlgorithm.crc16,
             base,
             { 
                hdr.ipv4.dstAddr
             },
             max
             );

        hash(
             hash_port,
             HashAlgorithm.crc16,
             base,
             { 
                hdr.udp.dstPort
             },
             max
             );
        
        meta.flowID = hash_IP + hash_port;

    }

    action find_flowID_ipv6() {
        bit<1> base = 0;
        bit<16> max = 0xffff;
        bit<32> hash_IP;
        bit<32> hash_port;

        hash(
             hash_IP,
             HashAlgorithm.crc16,
             base,
             { 
                hdr.ipv6.dstAddr
             },
             max
             );

        hash(
             hash_port,
             HashAlgorithm.crc16,
             base,
             { 
                hdr.udp.dstPort
             },
             max
             );
        
        meta.flowID = hash_IP + hash_port;

    }

    

    action assign_q(bit<3> qid) {
        standard_metadata.priority = qid;
    }

    apply {
        bit<3> qid;

        if (hdr.rtp.version == RTP_VERSION && hdr.rtp.padding == RTP_PADDING && hdr.rtp.extension == RTP_EXTENSION && hdr.rtp.csrcCounter == RTP_CSRC_COUNTER){
            flow_queue.write((bit<32>)0, (bit<3>)1);
        }

        if (hdr.ipv4.isValid() && hdr.ipv4.protocol == PROTO_UDP){
            find_flowID_ipv4();
            flow_queue.read(qid, meta.flowID);
            assign_q(qid);
        } else if (hdr.ipv6.isValid() && hdr.ipv6.nextHdr == PROTO_UDP) {
            find_flowID_ipv6();
            flow_queue.read(qid, meta.flowID);
            assign_q(qid);
        }

        //if (hdr.ipv4.isValid()) hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        standard_metadata.egress_spec = (standard_metadata.ingress_port+1)%2;
        

    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    counter(8, CounterType.packets) pqueues;

    apply {
        if (standard_metadata.qid == 0){
            pqueues.count(0);
        } else if (standard_metadata.qid == 1){
            pqueues.count(1);
        } else if (standard_metadata.qid == 2){
            pqueues.count(2);
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
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv6);
        packet.emit(hdr.udp);
        packet.emit(hdr.rtp);
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