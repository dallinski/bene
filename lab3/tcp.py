from src.sim import Sim
from src.connection import Connection
from src.tcppacket import TCPPacket

import math

class TcpTahoe(Connection):

    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None):
        Connection.__init__(self,transport,source_address,source_port,
                            destination_address,destination_port,app)
        self.send_buffer = ''
        self.received_ack_number = 0
        self.unacked_packet_count = 0
        self.mss = 1000
        self.sequence = 0
        self.received_sequences = set([])
        self.receive_buffer = []
        self.ack = 0
        self.cwnd = 0
        self.threshold = 100000
        self.timer = None
        self.timeout = 0.1
        self.max_sequence = math.pow(2,64)

        self.rate_file = open ('output/rate%d.txt' % source_port, 'w+')
        self.sequence_file = open('output/sequence%d.txt' % source_port, 'w+')
        self.window_file = open('output/window%d.txt' % source_port, 'w+')
        self.ack_file = open('output/acks%d.txt' % source_port, 'w+')

    def handle_packet(self,packet):
        # handle ACK (the sender getting ACKs and sending sequences)
        if packet.ack_number > self.received_ack_number:
            self.handle_ack(packet)
        
        # handle data (the receiver getting sequences and sending back ACKs)
        if packet.length > 0:
            self.handle_sequence(packet)

    def send(self,data):
        self.send_buffer += data
        self.cwnd = self.mss
        self.send_if_possible()

    def send_if_possible(self):
        if not self.send_buffer:
            return
        if self.unacked_packet_count >= self.cwnd:
            return
        while self.unacked_packet_count < self.cwnd:
            packet = self.send_one_packet(self.sequence)
            self.increment_sequence(packet.length)
            self.unacked_packet_count += self.mss

    def increment_sequence(self,length):
        self.sequence += length
        if self.sequence >= self.max_sequence:
            self.sequence = self.sequence - self.max_sequence

    def send_one_packet(self, sequence):
        print >> self.window_file, Sim.scheduler.current_time(), self.cwnd/self.mss
        # get one packet worth of data
        body = self.send_buffer[sequence:(sequence + self.mss)]
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=body,
                           sequence=sequence,ack_number=self.sequence)
        # send the packet
        Sim.trace("%d sending TcpTahoe segment to %d for %d" % (self.source_address,self.destination_address,packet.sequence))
        self.transport.send_packet(packet)
        # set a timer if it's not already going
        if not self.timer:
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)
        return packet

    def retransmit(self,event):
        if self.received_ack_number < len(self.send_buffer):
            Sim.trace("%d retransmission timer fired" % (self.source_address))
            self.loss_event()
            packet = self.send_one_packet(self.received_ack_number)
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)

    def loss_event(self):
        Sim.trace("Before loss event: cwnd = %d. Source port = %d" % ((self.cwnd/self.mss), self.source_port))
        self.threshold = max(self.cwnd/2, self.mss)
        self.cwnd = self.mss
        Sim.trace("After  loss event: cwnd = %d. Source port = %d" % ((self.cwnd/self.mss), self.source_port))

    def cancel_timer(self):
        if self.timer:
            try:
                Sim.scheduler.cancel(self.timer)
            except:
                pass
            self.timer = None

    # the sender getting an ACK from the receiver
    def handle_ack(self, packet):
        print >> self.ack_file, Sim.scheduler.current_time(), packet.ack_number,  packet.length
        Sim.trace("%d received TcpTahoe ACK from %d for %d" % (packet.destination_address,packet.source_address,packet.ack_number))
        new_bytes = packet.ack_number - self.received_ack_number
        self.unacked_packet_count -= new_bytes

        if self.cwnd >= self.threshold:
            self.cwnd += (self.mss*new_bytes)/self.cwnd
            self.threshold = self.cwnd
        else:
			self.cwnd += new_bytes

        self.cancel_timer()
        self.timer = Sim.scheduler.add(delay=self.timeout, event='new_ack_data', handler=self.retransmit)
        self.send_if_possible()
        self.received_ack_number = packet.ack_number

    # the receiver getting a sequence from the sender
    def handle_sequence(self, packet):
        print >> self.sequence_file, Sim.scheduler.current_time(), packet.ack_number,  packet.length
        Sim.trace("%d received TcpTahoe segment from %d for %d" % (packet.destination_address,packet.source_address,packet.sequence))
        self.received_sequences.add(packet.sequence)
        self.receive_buffer.append(packet)

        # cumulative ack
        sequence_list = sorted(self.received_sequences)
        for i in range(self.ack/self.mss, len(sequence_list)):
            if sequence_list[i] == self.ack:
                tempPacket = [p for p in self.receive_buffer if p.sequence == self.ack][0]
                self.increment_ack(tempPacket.sequence + tempPacket.length)
                print >> self.rate_file, Sim.scheduler.current_time(), self.ack, tempPacket.length
                self.app.handle_packet(tempPacket)
        
        self.send_ack()

    def increment_ack(self,sequence):
        self.ack = sequence
        if self.ack >= self.max_sequence:
            self.ack = 0

    def send_ack(self):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           sequence=self.sequence,ack_number=self.ack)
        # send the packet
        Sim.trace("%d sending TcpTahoe ACK to %d for %d" % (self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)
