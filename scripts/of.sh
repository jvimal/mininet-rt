#!/bin/sh
cd ~jvimal/openflow
controller/controller -v ptcp: 2>&1 1> /tmp/controller.log &
udatapath/ofdatapath -i "$1" punix:/tmp/ofsock 2>&1 1> /tmp/ofdp.log &
secchan/ofprotocol unix:/tmp/ofsock tcp:127.0.0.1 2>&1 1> /tmp/ofp.log &

