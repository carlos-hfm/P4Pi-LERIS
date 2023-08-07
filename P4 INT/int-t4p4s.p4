#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> IP_PROTO = 253;

#define MAX_HOPS 10

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/


typedef bit<48> macAddr_v;
typedef bit<32> ip4Addr_v;

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


header ethernet_h {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_h {
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
    ip4Addr_v srcAddr;
    ip4Addr_v dstAddr;
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
    ethernet_h         ethernet;
    ipv4_h             ipv4;
    nodeCount_h        nodeCount;
    InBandNetworkTelemetry_h[MAX_HOPS] INT;
}

struct mac_learn_digest {
    bit<48> srcAddr;
    bit<9>  ingress_port;
}

parser ParserImpl(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            IP_PROTO: parse_count;
            default: accept;
        }
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

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

     action add_swtrace() {
        bit<48> tmp;
        hdr.nodeCount.count = hdr.nodeCount.count + 1;
        hdr.INT.push_front(1);
        hdr.INT[0].setValid();
        hdr.INT[0].swid = 1;
        hdr.INT[0].ingress_port = (ingress_port_v)standard_metadata.ingress_port;
        hdr.INT[0].egress_port = (egress_port_v)standard_metadata.egress_port;
        hdr.INT[0].egress_spec = (egressSpec_v)standard_metadata.egress_spec;
        //hdr.INT[0].ingress_global_timestamp = (ingress_global_timestamp_v)standard_metadata.ingress_global_timestamp;
        tmp = (ingress_global_timestamp_v)standard_metadata.ingress_global_timestamp;
        //hdr.INT[0].egress_global_timestamp = (egress_global_timestamp_v)standard_metadata.egress_global_timestamp;
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
            swtrace.apply();
        }
    }
}



control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    action simple_forward(){
        if (standard_metadata.ingress_port == 0){
            standard_metadata.egress_port = 1;
        } else {
            standard_metadata.egress_port = 0;
        }

        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }


    action forward(bit<9> port) {
        standard_metadata.egress_port = port;
    }

    action bcast() {
        standard_metadata.egress_port = 9w100; // Broadcast port
    }

    action mac_learn() {
        digest<mac_learn_digest>((bit<32>)1024, { hdr.ethernet.srcAddr, standard_metadata.ingress_port });
    }

    action drop() {
        mark_to_drop( standard_metadata );
        exit;
    }

    action _nop() {
    }

    table dmac {
        actions = {
            forward;
            bcast;
            drop;
        }
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        default_action = bcast();
        size = 512;
    }

    table smac {
        actions = {
            mac_learn;
            _nop;
            drop;
        }
        key = {
            hdr.ethernet.srcAddr: exact;
        }
        default_action = mac_learn();
        size = 512;
    }

    apply {
        if (hdr.nodeCount.isValid()){
            //simple_forward();
            //send_back();
        } else {
            smac.apply();
            dmac.apply();
        }
    }

}

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.INT);
        packet.emit(hdr.nodeCount);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ethernet);
    }
}

control verifyChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

control computeChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

V1Switch(ParserImpl(), verifyChecksum(), ingress(), egress(), computeChecksum(), DeparserImpl()) main;