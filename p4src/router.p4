/*** load-balancer.p4 ***/

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

    action ecmp_group(bit<14> ecmp_group_id, bit<16> num_nhops){
        // Set the ecmp group id
        hash(meta.ecmp_hash,
	    HashAlgorithm.crc16,
	    (bit<1>)0,
	    { hdr.ipv4.srcAddr,
	      hdr.ipv4.dstAddr,
          hdr.tcp.srcPort,
          hdr.tcp.dstPort,
          hdr.ipv4.protocol},
	    num_nhops);

    }

    action set_nhop(macAddr_t dstAddr, egressSpec_t port){
        // Set the destination MAC address
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        // Set the source MAC address
        hdr.ethernet.dstAddr = dstAddr;

        // Set the output port
        standard_metadata.egress_spec = port;

        // Update the number of packet encapsulated
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    // Table to encapsulate the packet
    table ecmp_group_to_nhop {
        key = {
            meta.ecmp_group_id: exact;
            meta.ecmp_hash: exact;
        }
        actions = {
            drop;
            set_nhop;
        }
        size = 1024;
    }

    // Table to route the packet
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            set_nhop;
            ecmp_group;
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