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
    def __init__(self):
        self.retries = {}
        self.connections = set()
        self.connection_msg_count = {}

    def send(self, packet, network):
        self.retries[packet.msg_id] = 0

        src = packet.path[0]
        dst = packet.path[-1]
        connection = frozenset({src, dst})

        if connection not in self.connection_msg_count:
            self.connection_msg_count[connection] = 0
        self.connection_msg_count[connection] += 1
        msg_num = self.connection_msg_count[connection]

        packet.payload = f"MSG {msg_num} ({src}→{dst})"

        if connection in self.connections:
            print(f"Connection {src}↔{dst} already established, skipping handshake")
            packet.packet_type = "TCP_DATA"
            packet.locked = False
            packet.handshake_complete = True
            return [packet]

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
                return "retransmitting", []

        return "ok", []

class TransportLayer:
    def __init__(self, protocol):
        self.protocol = protocol

    def send(self, packet, network):
        return self.protocol.send(packet, network)

    def update(self, packet, network):
        return self.protocol.update(packet, network)
    