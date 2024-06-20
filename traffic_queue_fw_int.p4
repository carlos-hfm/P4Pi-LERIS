/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV6 = 0x86dd;
const bit<16> TYPE_IPV4  = 0x0800;
const bit<8> PROTO_INT_0 = 253;
const bit<8> PROTO_INT_1 = 254;
const bit<8> PROTO_INT_2 = 255;
const bit<8> PROTO_TCP = 6;
const bit<8>  PROTO_UDP = 17;


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
    bit<32>  flowID;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    ipv6_t       ipv6;
    udp_t        udp;
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
          TYPE_IPV4: parse_ipv4;
          TYPE_IPV6: parse_ipv6;
          default: accept;
        }
    }

    state parse_ipv4 {
      packet.extract(hdr.ipv4);
      transition select(hdr.ipv4.protocol) {
        PROTO_UDP: parse_udp;
        PROTO_INT_0: parse_count;
        PROTO_INT_1: parse_count;
        PROTO_INT_2: parse_count;
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
        meta.parser_metadata.remaining = meta.parser_metadata.remaining - 1;
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

    register<bit<3>>(0x1fffe) flow_queue;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action send_back() {
        standard_metadata.egress_spec = standard_metadata.ingress_port;
        bit<48> tmp_mac;
        bit<32> tmp_ip;

        tmp_mac = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = tmp_mac;

        tmp_ip = hdr.ipv4.srcAddr;
        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = tmp_ip;
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

        // setting queue of classified packets 
        if (hdr.ipv4.isValid() && hdr.ipv4.protocol == PROTO_UDP){
            find_flowID_ipv4();
            flow_queue.read(qid, meta.flowID);
            assign_q(qid);
        } else if (hdr.ipv6.isValid() && hdr.ipv6.nextHdr == PROTO_UDP) {
            find_flowID_ipv6();
            flow_queue.read(qid, meta.flowID);
            assign_q(qid);
        }

        // setting queue of INT packets
        if (hdr.ipv4.isValid()){
            if (hdr.ipv4.protocol == PROTO_INT_1) {
                qid = 1;
                assign_q(qid);
            } else if (hdr.ipv4.protocol == PROTO_INT_2) {
                qid = 2;
                assign_q(qid);
            }
        }

        // forwarding 
        if (hdr.nodeCount.isValid() && standard_metadata.instance_type == PKT_INSTANCE_TYPE_INGRESS_RECIRC) {
            send_back();
        } else {
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

    counter(8, CounterType.packets) pqueues;

    action my_recirculate() {
        recirculate_preserving_field_list(0);
    }

    action add_swtrace() {
        hdr.nodeCount.count = hdr.nodeCount.count + 1;
        hdr.INT.push_front(1);
        hdr.INT[0].setValid();
        //1 para downlink, 2 para uplink
        if (hdr.nodeCount.count == 2){
            hdr.INT[0].swid = 1;
        } else {
            hdr.INT[0].swid = 2;
        }
        hdr.INT[0].ingress_port = (ingress_port_v)standard_metadata.ingress_port;
        hdr.INT[0].egress_port = (egress_port_v)standard_metadata.egress_port;
        hdr.INT[0].egress_spec = (egressSpec_v)standard_metadata.egress_spec;
        hdr.INT[0].ingress_global_timestamp = (ingress_global_timestamp_v)standard_metadata.ingress_global_timestamp;
        hdr.INT[0].egress_global_timestamp = (egress_global_timestamp_v)standard_metadata.egress_global_timestamp;
        hdr.INT[0].enq_timestamp = (enq_timestamp_v)standard_metadata.enq_timestamp;
        hdr.INT[0].enq_qdepth = (enq_qdepth_v)standard_metadata.enq_qdepth;
        hdr.INT[0].deq_timedelta = (deq_timedelta_v)standard_metadata.deq_timedelta;
        hdr.INT[0].deq_qdepth = (deq_qdepth_v)standard_metadata.deq_qdepth;

        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 32;

     }

    apply {
        
        // counting number of pkts passed in each queue
        if (standard_metadata.qid == 0){
            pqueues.count(0);
        } else if (standard_metadata.qid == 1){
            pqueues.count(1);
        } else if (standard_metadata.qid == 2){
            pqueues.count(2);
        }

        // saving queues metadata and recirculating
        if (hdr.nodeCount.isValid()) {
            add_swtrace();
            if (hdr.nodeCount.count < 2){
                my_recirculate();
            }
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
        packet.emit(hdr.nodeCount);
        packet.emit(hdr.INT);
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