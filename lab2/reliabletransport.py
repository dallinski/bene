from src.sim import Sim
from src.connection import Connection
from src.tcppacket import TCPPacket

import math

class ExperimentStats():
    def __init__(self):
        self.queueing_delay = []
        self.file_size = 0

    def set_size(self, size):
        self.file_size = size

    def size(self): # in bytes
        return self.file_size

    def size_in_bits(self):
        return self.size() * 8

    def add(self, delay):
        self.queueing_delay.append(delay)

    def average(self):
        return float(sum(self.queueing_delay)) / len(self.queueing_delay)

    def throughput(self, time):
        return float(self.size_in_bits()) / time

class ReliableTransport(Connection):
    stats = ExperimentStats()

    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,window_size,app=None):
        Connection.__init__(self,transport,source_address,source_port,
                            destination_address,destination_port,app)
        self.send_buffer = ''
        self.next_sequence_num = 0
        self.received_ack_number = 0
        self.unacked_packet_count = 0
        self.mss = 1000
        self.sequence = 0
        self.received_sequences = set([])
        self.receive_buffer = []
        self.ack = 0
        self.timer = None
        self.timeout = 1
        self.max_sequence = math.pow(2,64)
        self.window_size = window_size

    def handle_packet(self,packet):
        # handle ACK (the sender getting ACKs and sending sequences)
        if packet.ack_number > self.received_ack_number:
            self.handle_ack(packet)
        
        # handle data (the receiver getting sequences and sending back ACKs)
        if packet.length > 0:
            self.handle_sequence(packet)

    def send(self,data):
        self.send_buffer += data
        self.send_if_possible()

    def send_if_possible(self):
        if not self.send_buffer:
            return
        if self.unacked_packet_count * 1000 >= self.window_size:
            return
        packet = self.send_one_packet(self.sequence)
        self.increment_sequence(packet.length)
        self.unacked_packet_count += 1

    def send_one_packet(self, sequence):
        # get one packet worth of data
        body = self.send_buffer[sequence:(sequence + self.mss)]
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=body,
                           sequence=sequence,ack_number=self.ack)
        # send the packet
        Sim.trace("%d sending ReliableTransport segment to %d for %d" % (self.source_address,self.destination_address,packet.sequence))
        self.transport.send_packet(packet)
        # set a timer if it's not already going
        if not self.timer:
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)
        return packet

    def send_ack(self):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           sequence=self.sequence,ack_number=self.ack)
        # send the packet
        Sim.trace("%d sending ReliableTransport ACK to %d for %d" % (self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)

    def increment_sequence(self,length):
        self.sequence += length
        if self.sequence >= self.max_sequence:
            self.sequence = self.sequence - self.max_sequence

    def increment_ack(self,sequence):
        self.ack = sequence
        if self.ack >= self.max_sequence:
            self.ack = 0
        return True

    def retransmit(self,event):
        if self.received_ack_number < len(self.send_buffer):
            Sim.trace("%d retransmission timer fired" % (self.source_address))
            packet = self.send_one_packet(self.received_ack_number)
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)

    def cancel_timer(self):
        if self.timer:
            Sim.scheduler.cancel(self.timer)
            self.timer = None

    # the sender getting an ACK from the receiver
    def handle_ack(self, packet):
        Sim.trace("%d received ReliableTransport ACK from %d for %d" % (packet.destination_address,packet.source_address,packet.ack_number))
        self.unacked_packet_count -= ((packet.ack_number - self.received_ack_number) / self.mss)
        self.cancel_timer()
        self.timer = Sim.scheduler.add(delay=self.timeout, event='new_ack_data', handler=self.retransmit)
        self.received_ack_number = packet.ack_number
        self.send_if_possible()

    # the receiver getting a sequence from the sender
    def handle_sequence(self, packet):
        # print "We want sequence number:%d\nGot sequence number:%d\n" % (self.ack, packet.sequence)
        Sim.trace("%d received ReliableTransport segment from %d for %d" % (packet.destination_address,packet.source_address,packet.sequence))
        ReliableTransport.stats.add(packet.queueing_delay)
        self.received_sequences.add(packet.sequence)
        self.receive_buffer.append(packet)

        # cumulative ack
        sequence_list = sorted(self.received_sequences)
        for i in range(self.ack/self.mss, len(sequence_list)):
            if sequence_list[i] == self.ack:
                tempPacket = [p for p in self.receive_buffer if p.sequence == self.ack][0]
                self.increment_ack(tempPacket.sequence + tempPacket.length)
                self.app.handle_packet(tempPacket)
        
        self.send_ack()
