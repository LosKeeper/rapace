/*** firewall.p4 ***/

#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parser.p4"

/********** Checksum verification control **********/
control FwVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  
        
    }
}

/********** Ingress control **********/
control FwIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    bit<32> tmp;
    register<bit<32>>(1) total_packets;
    register<bit<32>>(1) filtered_packets;

    action drop() {
        mark_to_drop(standard_metadata);
        filtered_packets.read(tmp, 0);
        filtered_packets.write(0, tmp + 1);
        total_packets.read(tmp, 0);
        total_packets.write(0, tmp + 1);
    }

    action count() {
        total_packets.read(tmp, 0);
        total_packets.write(0, tmp + 1);
    }

    table filter_table {
        key = {
            meta.srcAddr: exact;
            meta.dstAddr: exact;
            meta.protocol: exact;
            meta.srcPort: exact;
            meta.dstPort: exact;
        }
        actions = {
            drop;
            count;
        }
        size = 1024; 
    }

    apply {
        if (hdr.ipv4.isValid()) {
            meta.srcAddr = hdr.ipv4.srcAddr;
            meta.dstAddr = hdr.ipv4.dstAddr;
            meta.protocol = hdr.ipv4.protocol;
            if (hdr.ipv4.protocol == TYPE_TCP) {
                meta.srcPort = hdr.tcp.srcPort;
                meta.dstPort = hdr.tcp.dstPort;
            } else if (hdr.ipv4.protocol == TYPE_UDP) {
                meta.srcPort = hdr.udp.srcPort;
                meta.dstPort = hdr.udp.dstPort;
            }
            filter_table.apply();
        }
    }
}

/********** Egress control **********/
control FwEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        
    }
}

/********** Checksum computation control **********/
control FwComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {

    }
}

/********** Processing **********/
V1Switch(
    AllParser(),
    FwVerifyChecksum(),
    FwIngress(),
    FwEgress(),
    FwComputeChecksum(),
    AllDeparser()
) main;