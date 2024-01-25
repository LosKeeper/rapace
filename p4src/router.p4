
#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parser.p4"

/********** Checksum verification control **********/
control RVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  

    }
}

/********** Ingress control **********/
control RIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    // Counter of number of packet received
    register<count_t>(64) num_packet_received;

    // Counter of number of packet encapsulated
    register<count_t>(64) num_packet_encapsulated;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action set_nhop(egressSpec_t port) {
        //set the output port that we also get from the table
        standard_metadata.egress_spec = port;
        //decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table set_nhop {
        key = {
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            set_nhop;
            drop;
        }
        size = 1024;
        default_action = drop;
    }

    apply {
        if(hdr.ipv4.isValid() && hdr.ipv4.ttl > 1){
            // Get the number of packet received
            count_t current_count_in;
            num_packet_received.read(current_count_in, (bit<32>)standard_metadata.ingress_port);
            current_count_in = current_count_in + 1;

            // Update the number of packet received
            num_packet_received.write((bit<32>)standard_metadata.ingress_port, current_count_in);

            // Get the number of packet encapsulated


            // Route the packet
            set_nhop.apply().action_run
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

/********** Checksum computation control **********/
control RComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {

    }
        
}


/********** Processing **********/
V1Switch(
    AllParser(),
    RVerifyChecksum(),
    RIngress(),
    REgress(),
    RComputeChecksum(),
    AllDeparser()
) main;