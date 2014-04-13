from sim import Sim

import copy

class Node(object):
    def __init__(self,hostname):
        self.hostname = hostname
        self.links = []
        self.protocols = {}
        self.forwarding_table = {}
        self.neighbors_dv_tables = {}

    def distance_vector_table(self):
        dv_table = {self.hostname: 0, }
        if not self.neighbors_dv_tables:
            return dv_table
        for neighbor in self.neighbors_dv_tables:
            neighbor_table = self.neighbors_dv_tables[neighbor]
            if not neighbor_table:
                continue
            link = self.get_link(neighbor.hostname)
            for dest_node_name in neighbor_table:
                if dest_node_name == self.hostname:
                    continue
                new_distance = neighbor_table[dest_node_name]
                if dest_node_name not in dv_table:
                    dv_table[dest_node_name] = new_distance + 1
                else:  # already in the dv_table
                    if dv_table[dest_node_name] > new_distance + 1:
                        dv_table[dest_node_name] = new_distance + 1
        return dv_table

    ## Links ## 

    def add_link(self,link):
        self.links.append(link)

    def delete_link(self,link):
        if link not in self.links:
            return
        self.links.remove(link)

    def get_link(self,name):
        for link in self.links:
            if link.endpoint.hostname == name:
                return link
        return None

    def get_address(self,name):
        for link in self.links:
            if link.endpoint.hostname == name:
                return link.address
        return 0

    ## Protocols ## 

    def add_protocol(self,protocol,handler):
        self.protocols[protocol] = handler

    def delete_protocol(self,protocol):
        if protocol not in self.protocols:
            return
        del self.protocols[protocol]

    ## Forwarding table ##

    def add_forwarding_entry(self,address,link):
        self.forwarding_table[address] = link

    def delete_forwarding_entry(self,address,link):
        if address not in self.forwarding_table:
            return
        del self.forwarding_table[address]

    ## Handling packets ##

    def send_packet(self,packet):
        # if this is the first time we have seen this packet, set its
        # creation timestamp
        if packet.created == None:
            packet.created = Sim.scheduler.current_time()

        # forward the packet
        self.forward_packet(packet)

    def receive_packet(self,packet):
        # handle broadcast packets
        if packet.destination_address == 0:
            Sim.trace("%s received packet" % (self.hostname))
            self.deliver_packet(packet)
        else:
            # check if unicast packet is for me
            for link in self.links:
                if link.address == packet.destination_address:
                    Sim.trace("%s received packet" % (self.hostname))
                    self.deliver_packet(packet)
                    return

        # decrement the TTL and drop if it has reached the last hop
        packet.ttl = packet.ttl - 1
        if packet.ttl <= 0:
            Sim.trace("%s dropping packet due to TTL expired" % (self.hostname))
            return

        # forward the packet
        self.forward_packet(packet)


    def deliver_packet(self,packet):
        if packet.protocol not in self.protocols:
            print 'the packet ("%s") was delivered' % packet.body
            return
        self.protocols[packet.protocol].receive_packet(packet)


    def forward_packet(self,packet):
        if packet.destination_address == 0:
            # broadcast the packet
            self.forward_broadcast_packet(packet)
        else:
            # forward the packet
            self.forward_unicast_packet(packet)

    def forward_unicast_packet(self,packet):
        if packet.destination_address not in self.forwarding_table:
            Sim.trace("%s no routing entry for %d" % (self.hostname,packet.destination_address))
            print "%s |^^^^^^^^^^^^Forwarding Table^^^^^^^^^^^^|" % self.hostname
            for i in self.forwarding_table:
                link = self.forwarding_table[i]
                print "   |    DestAddr:%s, LinkAddr:%s, %s->%s      |" % (i, link.address, link.startpoint.hostname, link.endpoint.hostname)
            print "   |________________________________________|"
            return
        link = self.forwarding_table[packet.destination_address]
        Sim.trace("%s forwarding packet to %d" % (self.hostname,packet.destination_address))
        link.send_packet(packet)

    def forward_broadcast_packet(self,packet):
        for link in self.links:
            Sim.trace("%s forwarding broadcast packet to %s" % (self.hostname,link.endpoint.hostname))
            packet_copy = copy.copy(packet)
            link.send_packet(packet_copy)
