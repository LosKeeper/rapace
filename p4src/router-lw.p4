/*** router.p4 ***/

#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parser.p4"
#include "include/checksum.p4"

/********** Ingress control **********/
control RIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    bit<32> tmp;
    register<bit<32>>(1) total_packets;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action set_nhop_host(macAddr_t dstAddr, egressSpec_t port) {
        /* swap mac addresses for the packet to go back to the host */
        // set the destination mac address with the source mac address from the packet
        hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
        // set the source mac address with the one we get from the table 
        hdr.ethernet.srcAddr = dstAddr;
        // set the output port that we also get from the table
        standard_metadata.egress_spec = port;
        // decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

        // count
        total_packets.read(tmp, 0);
        total_packets.write(0, tmp + 1);
    }

    action set_nhop_router(egressSpec_t port) {
        // set the output port that we also get from the table
        standard_metadata.egress_spec = port;

        // decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

        // count
        total_packets.read(tmp, 0);
        total_packets.write(0, tmp + 1);
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            set_nhop_host;
            set_nhop_router;
            drop;
        }
        size = 1024;
        default_action = drop;
    }

    apply {
        if(hdr.ipv4.isValid()){
            // apply tables
            ipv4_lpm.apply();
        }
    }
}

/********** Egress control **********/
control REgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        
    }
}

/********** Processing **********/
V1Switch(
    AllParser(),
    AllVerifyChecksum(),
    RIngress(),
    REgress(),
    AllComputeChecksum(),
    AllDeparser()
) main;