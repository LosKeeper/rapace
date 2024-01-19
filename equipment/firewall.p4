/*** firewall.p4 ***/

#include <core.p4>
#include <v1model.p4>

/********** Checksum verification control **********/
control FwVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
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
            // rules add by the user in the api with table_add
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
            hdr.ipv4.protocol: exact;
            hdr.ipv4.srcPort: exact;
            hdr.ipv4.dstPort: exact;
        }
        actions = {
            drop;
            count;
        }
        size = 1024; 
    }

    apply {
        if (hdr.ipv4.isValid()) {
            filter_table.apply();
        }
    }
}

/********** Egress control **********/
control FwEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        bit<16> tmp = hdr.ipv4.srcPort;
        hdr.ipv4.srcPort = hdr.ipv4.dstPort;
        hdr.ipv4.dstPort = tmp;
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
    AllDeparser(),
    FwComputeChecksum()
) main;