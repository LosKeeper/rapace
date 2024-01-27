/*** checksum.p4 ***/

/********** Checksum verification control **********/
control AllVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  
        
    }
}

/********** Checksum computation control **********/
control AllComputeChecksum(inout headers hdr, inout metadata meta) {
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

        update_checksum(
            hdr.ipv4_icmp.isValid(),
                { hdr.ipv4_icmp.version,
                hdr.ipv4_icmp.ihl,
                hdr.ipv4_icmp.dscp,
                hdr.ipv4_icmp.ecn,
                hdr.ipv4_icmp.totalLen,
                hdr.ipv4_icmp.identification,
                hdr.ipv4_icmp.flags,
                hdr.ipv4_icmp.fragOffset,
                hdr.ipv4_icmp.ttl,
                hdr.ipv4_icmp.protocol,
                hdr.ipv4_icmp.srcAddr,
                hdr.ipv4_icmp.dstAddr },
                hdr.ipv4_icmp.hdrChecksum,
                HashAlgorithm.csum16);

        update_checksum(
            hdr.icmp.isValid(),
                { hdr.icmp.type,
                hdr.icmp.code,
                hdr.icmp.unused,
                hdr.ipv4.version,
            hdr.ipv4.ihl,
                hdr.ipv4.dscp,
                hdr.ipv4.ecn,
                hdr.ipv4.totalLen,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.hdrChecksum,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                hdr.tcp.srcPort,
                hdr.tcp.dstPort,
                hdr.tcp.seqNo
                },
                hdr.icmp.checksum,
                HashAlgorithm.csum16);
    }
}