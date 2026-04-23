import random
from simulation import Packet

class Protocol:

    def send(self, packet, network):
        pass

    def update(self, packet, network):
        pass


class UDPProtocol:
    def send(self, packet, network):
        packet.packet_type = "UDP"
        return [packet]  

    def update(self, packet, network):
        start = packet.path[packet.current_index]
        end = packet.path[packet.current_index + 1]
        edge = (start, end)

        if edge not in packet.checked_edges:
            packet.checked_edges.add(edge)
            if random.random() < network.edge_loss[edge]:
                packet.dropped = True
                return "dropped", []

        return "ok", []
    
class TCPProtocol:
    MAX_RETRIES = 5
    DEFAULT_RTT = 15000
    RTT_MULTIPLIER = 1.5
    def __init__(self):
        self.retries = {}
        self.connections = set()
        self.connection_msg_count = {}
        self.connection_seq_num = {}
        self.connection_rtt = {}        
        self.connection_rtt_samples = {}

    def record_rtt(self, connection, rtt_sample):
        if connection not in self.connection_rtt_samples:
            self.connection_rtt_samples[connection] = []
        self.connection_rtt_samples[connection].append(rtt_sample)
        # Rolling average over last 5 samples
        samples = self.connection_rtt_samples[connection][-5:]
        self.connection_rtt[connection] = sum(samples) / len(samples)
        print(f"RTT sample: {rtt_sample:.0f}ms, avg RTT: {self.connection_rtt[connection]:.0f}ms")

    def get_timeout(self, connection):
        if connection not in self.connection_rtt:
            return self.DEFAULT_RTT
        return self.connection_rtt[connection] * self.RTT_MULTIPLIER


    def send(self, packet, network):
        self.retries[packet.msg_id] = 0

        src = packet.path[0]
        dst = packet.path[-1]
        connection = frozenset({src, dst})

        if connection not in self.connection_msg_count:
            self.connection_msg_count[connection] = 0
            self.connection_seq_num[connection] = 0

        self.connection_msg_count[connection] += 1
        self.connection_seq_num[connection] += 1
        msg_num = self.connection_msg_count[connection]
        seq_num = self.connection_seq_num[connection]

        packet.payload = f"MSG {msg_num} ({src}→{dst})"
        packet.seq_num = seq_num

        if connection in self.connections:
            print(f"Connection {src}↔{dst} already established, skipping handshake")
            packet.packet_type = "TCP_DATA"
            packet.locked = False
            packet.handshake_complete = True
            return [packet]
        
        print(f"New connection {src}↔{dst}, starting handshake")
        path = packet.path
        reverse = list(reversed(path))
        base_id = packet.msg_id

        syn     = Packet(path,    msg_id=str(base_id)+"_syn",     packet_type="TCP_SYN")
        syn_ack = Packet(reverse, msg_id=str(base_id)+"_synack",  packet_type="TCP_SYN_ACK")
        ack     = Packet(path,    msg_id=str(base_id)+"_ack",     packet_type="TCP_ACK")

        syn.triggers_id = syn_ack.msg_id
        syn_ack.triggers_id = ack.msg_id
        ack.triggers_id = base_id

        syn_ack.locked = True
        ack.locked = True

        packet.packet_type = "TCP_DATA"
        packet.locked = True
        packet.handshake_complete = False

        self.connections.add(connection)
        return [syn, syn_ack, ack, packet]

    def update(self, packet, network):
        if packet.locked:
            return "waiting", []
        
        if packet.retransmit_cooldown > 0:
            packet.retransmit_cooldown -= 1
            return "waiting", []

        if packet.packet_type != "TCP_DATA":
            return "ok", []

        start = packet.path[packet.current_index]
        end = packet.path[packet.current_index + 1]
        edge = (start, end)

        if edge not in packet.checked_edges:
            packet.checked_edges.add(edge)
            if random.random() < network.edge_loss[edge]:
                if packet.msg_id not in self.retries:
                    self.retries[packet.msg_id] = 0
                self.retries[packet.msg_id] += 1
                retries = self.retries[packet.msg_id]
                print(f"Packet lost on {start}→{end}, retry #{retries}")
                if retries >= self.MAX_RETRIES:
                    return "dropped", []
                packet.checked_edges.discard(edge)
                packet.progress = 0.0
                connection = frozenset({packet.path[0], packet.path[-1]})
                timeout_ms = self.get_timeout(connection)
                packet.retransmit_cooldown = int(timeout_ms / 1000 * 60)
                return "retransmitting", []

        return "ok", []

class TransportLayer:
    def __init__(self, protocol):
        self.protocol = protocol

    def send(self, packet, network):
        return self.protocol.send(packet, network)

    def update(self, packet, network):
        return self.protocol.update(packet, network)
    