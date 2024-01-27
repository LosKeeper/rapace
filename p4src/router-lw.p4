
#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parser.p4"

/********** Checksum verification control **********/
control RLwVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  

    }
}

/********** Ingress control **********/
control RLwIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    // // Counter of number of packet received
    // register<count_t>(64) num_packet_received;

    // // Counter of number of packet encapsulated
    // register<count_t>(64) num_packet_encapsulated;

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
    }

    action set_nhop_router(egressSpec_t port) {
        // set the output port that we also get from the table
        standard_metadata.egress_spec = port;

        // decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
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
            // Get the number of packet received
            // count_t current_count_in;
            // num_packet_received.read(current_count_in, (bit<32>)standard_metadata.ingress_port);
            // current_count_in = current_count_in + 1;

            // Update the number of packet received
            // num_packet_received.write((bit<32>)standard_metadata.ingress_port, current_count_in);

            // route the packet
            ipv4_lpm.apply();
        }
    }
}

/********** Egress control **********/
control RLwEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        
    }
}

/********** Checksum computation control **********/
control RLwComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        update_checksum(
            hdr.ipv4.isValid(),
                { hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.dscp,
                hdr.ipv4.ecn,
                hdr.ipv4.totalLen,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr },
                hdr.ipv4.hdrChecksum,
                HashAlgorithm.csum16);
    }
}


/********** Processing **********/
V1Switch(
    AllParser(),
    RLwVerifyChecksum(),
    RLwIngress(),
    RLwEgress(),
    RLwComputeChecksum(),
    AllDeparser()
) main;