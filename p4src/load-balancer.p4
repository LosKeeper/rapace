/*** load-balancer.p4 ***/

#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parser.p4"
#include "include/checksum.p4"

/********** Ingress control **********/
control LbIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    
    bit<32> tmp;
    register<bit<32>>(1) total_packets;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action set_nhop(egressSpec_t port) {
        //set the output port that we also get from the table
        standard_metadata.egress_spec = port;
    }

    action random_nhop(bit<16> num_nhops) {
        // calculate a random number modulo the number of out ports
        hash(meta.hash,
        HashAlgorithm.crc16,
        (bit<1>)0,
        { meta.srcAddr,
          meta.dstAddr,
          meta.srcPort,
          meta.dstPort,
          meta.protocol},   
        num_nhops);

        // count
        total_packets.read(tmp, 0);
        total_packets.write(0, tmp + 1);
    }

    // forward the packet to the corresponding port according to the hash
    table load_balancer {
        key = {
            meta.hash: exact;
        }
        actions = {
            drop;
            set_nhop;
        }
        size = 1024;
    }

    // filter on the incoming port, if it is a port out, forward it
    // otherwise, apply load_balancer table and generate a random number 
    table entry_port {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            set_nhop;
            random_nhop;
            drop;
        }
        size = 1024;
        default_action = drop;
    }

    apply {
        if (hdr.ipv4.isValid()){
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

            switch (entry_port.apply().action_run){
                random_nhop: {
                    load_balancer.apply();
                }
            }
        }
    }
}

/********** Egress control **********/
control LbEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        
    }
}

/********** Processing **********/
V1Switch(
    AllParser(),
    AllVerifyChecksum(),
    LbIngress(),
    LbEgress(),
    AllComputeChecksum(),
    AllDeparser()
) main;