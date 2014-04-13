import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import packet

from networks.network import Network

def log(string):
    if False:
        print string

class DVRoutingApp(object):

    def __init__(self, node):
        self.node = node
        self.prev_dv_table = None
        self.broadcast("")
        self.timer = Sim.scheduler.add(delay=30, event='broadcast', handler=self.broadcast)
        self.neighbor_timeouts = {}

    def setup_forwarding_entries(self):
        dv_table = self.node.distance_vector_table()
        if not self.node.neighbors_dv_tables:
            return 
        for neighbor in self.node.neighbors_dv_tables:
            neighbor_table = self.node.neighbors_dv_tables[neighbor]
            if not neighbor_table:
                continue
            link = self.node.get_link(neighbor.hostname)
            for dest_node_name in neighbor_table:
                if dest_node_name == self.node.hostname:
                    continue
                try:
                    distance_from_self_node = dv_table[dest_node_name]
                except:
                    log("%s    %s is unreachable" % (self.node.hostname, dest_node_name))
                    continue
                dest_addr = self.get_dest_addr(self.node, dest_node_name, distance_from_self_node)
                if dest_addr in self.node.forwarding_table:
                    log("%s Already have a forwarding table entry to destination %s" % (self.node.hostname, dest_node_name))
                    continue
                self.node.add_forwarding_entry(dest_addr, link)
                log("%s After updating forwarding_table entry to destination %s" % (self.node.hostname, dest_node_name))
                print_forwarding_table(self.node)
        return dv_table

    def get_dest_addr(self, start_node, dest_node_name, cur_distance):
        dest_addr = start_node.get_address(dest_node_name)
        if dest_addr:
            log("%s dest_addr (%s) using link %s->%s" % (self.node.hostname, dest_addr, start_node.hostname, dest_node_name))
            return dest_addr
        else:
            for neighbor in start_node.neighbors_dv_tables:
                n_dv_table = start_node.neighbors_dv_tables[neighbor]
                try:
                    new_distance = n_dv_table[dest_node_name]
                except:
                    new_distance = float("inf")  

                if new_distance < cur_distance:
                    log("%s %s says it is closer to %s than self.node" % (self.node.hostname, neighbor.hostname, dest_node_name))
                    return self.get_dest_addr(neighbor, dest_node_name, new_distance)

    def add_dv_table(self, node, dv_table):
        self.node.neighbors_dv_tables[node] = dv_table
        body = {"node": node}
        p = packet.Packet(
            source_address=self.node.get_address(self.node.hostname),
            destination_address=0, ident='bcast', ttl=1, protocol='timeout', length=100, body=body)
        self.neighbor_timeouts[node] = Sim.scheduler.add(delay=90, event=p, handler=self.check_neighbors)

    def receive_packet(self, p):
        if not isinstance(p.body, dict):
            Sim.trace("This shouldn't ever get called. %s %s %s" % (self.node.hostname,p.ident, p.body))
            return
        self.add_dv_table(p.body["node"], p.body["dv_table"])
        cur_table = self.node.distance_vector_table()
        if cur_table != self.prev_dv_table:
            Sim.trace("Update distance vector table for %s to %s" % (self.node.hostname, cur_table))
            self.prev_dv_table = cur_table
            self.setup_forwarding_entries()
            self.broadcast('broadcast')

    def broadcast(self, event):
        body = {"node": self.node, "dv_table": self.prev_dv_table}
        p = packet.Packet(
            source_address=self.node.get_address(self.node.hostname),
            destination_address=0, ident='bcast', ttl=1, protocol='dvrouting', length=100, body=body)
        Sim.scheduler.add(delay=0, event=p, handler=self.node.send_packet)
        self.timer = Sim.scheduler.add(delay=30, event='broadcast', handler=self.broadcast)
        Sim.trace("Broadcasting %s's distance vector table" % (self.node.hostname))

    def check_neighbors(self, event):
        node = event.body["node"]
        self.node.neighbors_dv_tables[node] = {}
        self.node.forwarding_table = {}
        self.setup_forwarding_entries()

def print_forwarding_table(node):
    log("%s |^^^^^^^^^^^^Forwarding Table^^^^^^^^^^^^|" % node.hostname)
    for i in node.forwarding_table:
        link = node.forwarding_table[i]
        log("   |    DestAddr:%s, LinkAddr:%s, %s->%s      |" % (i, link.address, link.startpoint.hostname, link.endpoint.hostname))
    log("   |________________________________________|")


class Main(object):

    def __init__(self):
        self.run(self.parse_options())

    def parse_options(self):
        # setup network
        if sys.argv[1] == 'row':
            return Network('five-nodes-in-a-row.txt')
        elif sys.argv[1] == 'ring':
            return Network('five-nodes-in-a-ring.txt')
        elif sys.argv[1] == 'fifteen':
            return Network('../networks/fifteen-nodes.txt')
        else:
            return 'You must specify the network!\nOptions: "row", "ring", "fifteen"'

    def get_nodes(self, net):
        n1 = net.get_node('n1')
        n2 = net.get_node('n2')
        n3 = net.get_node('n3')
        n4 = net.get_node('n4')
        n5 = net.get_node('n5')
        nodes = [n1, n2, n3, n4, n5]
        if len(net.nodes) == 15:
            n6 = net.get_node('n6')
            n7 = net.get_node('n7')
            n8 = net.get_node('n8')
            n9 = net.get_node('n9')
            n10 = net.get_node('n10')
            n11 = net.get_node('n11')
            n12 = net.get_node('n12')
            n13 = net.get_node('n13')
            n14 = net.get_node('n14')
            n15 = net.get_node('n15')
            nodes = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15]
        return nodes

    def setup_broadcast_app(self, nodes, net):
        if len(nodes) == 5:
            n1, n2, n3, n4, n5 = nodes
        elif len(nodes) == 15:
            n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15 = nodes
        n1.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n1))
        n2.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n2))
        n3.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n3))
        n4.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n4))
        n5.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n5))
        if len(nodes) == 15:
            n6.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n6))
            n7.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n7))
            n8.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n8))
            n9.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n9))
            n10.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n10))
            n11.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n11))
            n12.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n12))
            n13.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n13))
            n14.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n14))
            n15.add_protocol(protocol="dvrouting", handler=DVRoutingApp(n15))

    def take_down_link(self, packet):
        start_node = packet.body["start"]
        end_node = packet.body["end"]
        link = start_node.get_link(end_node)
        start_node.delete_link(link)

    def run(self, net):
        if not isinstance(net, Network):
            print net
            return

        # parameters
        Sim.scheduler.reset()
        Sim.set_debug(True)

        # get nodes
        nodes = self.get_nodes(net)

        # setup broadcast application
        self.setup_broadcast_app(nodes, net)

        if sys.argv[1] == 'row':
            p = packet.Packet(
                source_address=1, destination_address=5, ident=1,
                ttl=len(nodes), protocol='somethingelse', length=100, body="First message. From n1 -> n4")
            Sim.scheduler.add(delay=1, event=p, handler=nodes[0].send_packet)
            p2 = packet.Packet(
                source_address=1, destination_address=7, ident=2,
                ttl=len(nodes), protocol='somethingelse', length=100, body="Second message. From n2 -> n5")
            Sim.scheduler.add(delay=33, event=p2, handler=nodes[1].send_packet)
            p3 = packet.Packet(
                source_address=1, destination_address=2, ident=3,
                ttl=len(nodes), protocol='somethingelse', length=100, body="third message. From n3 -> n1")
            Sim.scheduler.add(delay=34, event=p3, handler=nodes[2].send_packet)
            p4 = packet.Packet(
                source_address=1, destination_address=4, ident=4,
                ttl=len(nodes), protocol='somethingelse', length=100, body="Fourth message. From n4 -> n2")
            Sim.scheduler.add(delay=35, event=p4, handler=nodes[3].send_packet)
        elif sys.argv[1] == 'ring':
            p = packet.Packet(
                source_address=1, destination_address=9, ident=1,
                ttl=len(nodes), protocol='somethingelse', length=100, body="First message. From n1 -> n4")
            Sim.scheduler.add(delay=1, event=p, handler=nodes[0].send_packet)
            p2 = packet.Packet(
                source_address=1, destination_address=1, ident=2,
                ttl=len(nodes), protocol='somethingelse', length=100, body="Second message. From n2 -> n5")
            Sim.scheduler.add(delay=33, event=p2, handler=nodes[1].send_packet)
            p3 = packet.Packet(
                source_address=1, destination_address=3, ident=3,
                ttl=len(nodes), protocol='somethingelse', length=100, body="third message. From n3 -> n1")
            Sim.scheduler.add(delay=34, event=p3, handler=nodes[2].send_packet)
            p4 = packet.Packet(
                source_address=1, destination_address=6, ident=4,
                ttl=len(nodes), protocol='somethingelse', length=100, body="Fourth message. From n2 -> n4")
            Sim.scheduler.add(delay=35, event=p4, handler=nodes[1].send_packet)
        elif sys.argv[1] == 'fifteen':
            p = packet.Packet(
                source_address=1, destination_address=17, ident=1,
                ttl=len(nodes), protocol='somethingelse', length=100, body="First message. From n1 -> n4 -> n5 -> n12")
            Sim.scheduler.add(delay=1, event=p, handler=nodes[0].send_packet)

            # body2 = {"start": nodes[3], "end": nodes[4]}
            # p1 = packet.Packet(
            #     source_address=1, destination_address=17, ident=2,
            #     ttl=len(nodes), protocol='somethingelse', length=100, body=body2)
            # Sim.scheduler.add(delay=28, event=p1, handler=self.take_down_link)

            p2 = packet.Packet(
                source_address=1, destination_address=35, ident=3,
                ttl=len(nodes), protocol='somethingelse', length=100, body="Second message. From n11 -> n4 -> n5 -> n3 -> n14 -> n15")
            Sim.scheduler.add(delay=33, event=p2, handler=nodes[10].send_packet)
            p3 = packet.Packet(
                source_address=1, destination_address=18, ident=4,
                ttl=len(nodes), protocol='somethingelse', length=100, body="third message. From n9 -> n6 -> n1 -> n4 -> n5 -> n13")
            Sim.scheduler.add(delay=34, event=p3, handler=nodes[8].send_packet)
            p4 = packet.Packet(
                source_address=1, destination_address=4, ident=5,
                ttl=len(nodes), protocol='somethingelse', length=100, body="Fourth message. From n3 -> n2 -> n1 -> n10")
            Sim.scheduler.add(delay=35, event=p4, handler=nodes[2].send_packet)

        # run the simulation
        Sim.scheduler.run()

if __name__ == '__main__':
    m = Main()
