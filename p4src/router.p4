/*** router.p4 ***/

#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parser.p4"
#include "include/checksum.p4"

#define IP_ICMP_PROTO 1
#define ICMP_TTL_EXPIRED 11

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

    action set_nhop_router(macAddr_t dstAddr, egressSpec_t port) {
        // set the source mac address with the previous destination mac adddress
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        // set the destination mac address with the one we get from the table
        hdr.ethernet.dstAddr = dstAddr;
        // set the output port that we also get from the table
        standard_metadata.egress_spec = port;
        // decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

        // count
        total_packets.read(tmp, 0);
        total_packets.write(0, tmp + 1);
    }

    action set_src_icmp_ip (bit<32> src_ip){
        hdr.ipv4_icmp.srcAddr = src_ip;
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

    table icmp_ingress_port {
        key = {
            standard_metadata.ingress_port: exact;
        }

        actions = {
            set_src_icmp_ip;
            NoAction;
        }
        size=64;
        default_action=NoAction;
    }

    apply {
        if(hdr.ipv4.isValid() && hdr.ipv4.ttl > 1){
            // Forward packet
            ipv4_lpm.apply();
        }
        else if (hdr.ipv4.isValid() && hdr.tcp.isValid() && hdr.ipv4.ttl == 1) {

            // Set new headers valid
            hdr.ipv4_icmp.setValid();
            hdr.icmp.setValid();

            // Set egress port == ingress port
            standard_metadata.egress_spec = standard_metadata.ingress_port;

            //Ethernet: Swap map addresses
            bit<48> tmp_mac = hdr.ethernet.srcAddr;
            hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
            hdr.ethernet.dstAddr = tmp_mac;

            //Building new Ipv4 header for the ICMP packet
            //Copy original header (for simplicity)
            hdr.ipv4_icmp = hdr.ipv4;
            //Set destination address as traceroute originator
            hdr.ipv4_icmp.dstAddr = hdr.ipv4.srcAddr;
            //Set src IP to the IP assigned to the switch interface
            icmp_ingress_port.apply();

            //Set protocol to ICMP
            hdr.ipv4_icmp.protocol = IP_ICMP_PROTO;
            //Set default TTL
            hdr.ipv4_icmp.ttl = 64;
            //And IP Length to 56 bytes (normal IP header + ICMP + 8 bytes of data)
            hdr.ipv4_icmp.totalLen= 56;

            //Create ICMP header with
            hdr.icmp.type = ICMP_TTL_EXPIRED;
            hdr.icmp.code = 0;

            //make sure all the packets are length 70.. so wireshark does not complain when tpc options,etc
            truncate((bit<32>)70);
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