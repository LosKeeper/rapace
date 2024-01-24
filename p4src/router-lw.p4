/*** load-balancer.p4 ***/

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
    apply {

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