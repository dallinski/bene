import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet


class DelayHandler(object):

    def handle_packet(self, packet):
        print Sim.scheduler.current_time(), packet.ident, packet.created, Sim.scheduler.current_time() - packet.created, packet.transmission_delay, packet.propagation_delay, packet.queueing_delay


def ThreeNodeSetup(band1, band2, prop1, prop2):
    Sim.scheduler.reset()

    # setup network
    n1 = node.Node()
    n2 = node.Node()
    n3 = node.Node()
    l = link.Link(address=1, startpoint=n1, endpoint=n2, bandwidth=band1, propagation=prop1)
    n1.add_link(l)
    n1.add_forwarding_entry(address=2, link=l)
    l = link.Link(address=2, startpoint=n2, endpoint=n1, bandwidth=band1, propagation=prop1)
    n2.add_link(l)
    n2.add_forwarding_entry(address=1, link=l)

    l = link.Link(address=3, startpoint=n2, endpoint=n3, bandwidth=band2, propagation=prop2)
    n2.add_link(l)
    n2.add_forwarding_entry(address=4, link=l)
    l = link.Link(address=4, startpoint=n3, endpoint=n2, bandwidth=band2, propagation=prop2)
    n3.add_link(l)
    n3.add_forwarding_entry(address=3, link=l)

    d = DelayHandler()
    n3.add_protocol(protocol="delay", handler=d)

    return n1, n2, n3


def ScenarioOne():
    # set up nodes
    n1, n2, n3 = ThreeNodeSetup(1000000, 1000000, .1, .1)

    # send 1000 packets
    for i in range(1,1001):
        p = packet.Packet(destination_address=4, ident=i, protocol='delay', length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n2.handle_packet)

    # run the simulation
    Sim.scheduler.run()


def ScenarioOneUpgraded():
    # set up nodes
    n1, n2, n3 = ThreeNodeSetup(1000000000, 1000000000, .1, .1)

    # send 1000 packets
    for i in range(1,1001):
        p = packet.Packet(destination_address=4, ident=i, protocol='delay', length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n2.handle_packet)

    # run the simulation
    Sim.scheduler.run()


def ScenarioTwo():
    # set up nodes
    n1, n2, n3 = ThreeNodeSetup(1000000, 256000, .1, .1)

    # send 1000 packets
    for i in range(1,1001):
        p = packet.Packet(destination_address=4, ident=i, protocol='delay', length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n2.handle_packet)

    # run the simulation
    Sim.scheduler.run()

if __name__ == '__main__':
    print "\nScenario 1"
    ScenarioOne()
    print "\nScenario 1 upgraded to 1 Gbps"
    ScenarioOneUpgraded()
    print "\nScenario 2"
    ScenarioTwo()
