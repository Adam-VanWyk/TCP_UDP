import random


class Protocol:

    def send(self, packet, network):
        pass

    def update(self, packet, network):
        pass


class UDPProtocol:
    def send(self, packet, network):
        return packet  

    def update(self, packet, network):
        start = packet.path[packet.current_index]
        end = packet.path[packet.current_index + 1]
        edge = (start, end)

        if edge not in packet.checked_edges:
            packet.checked_edges.add(edge)
            if random.random() < network.edge_loss[edge]:
                packet.dropped = True
                return "dropped"

        return "ok"
    
class TCPProtocol:
    def __init__(self):
        self.retries = {}

    def send(self, packet, network):
        self.retries[packet.msg_id] = 0
        return packet

    def update(self, packet, network):
        start = packet.path[packet.current_index]
        end = packet.path[packet.current_index + 1]
        edge = (start, end)

        if edge not in packet.checked_edges:
            packet.checked_edges.add(edge)
            if random.random() < network.edge_loss[(start, end)]:
                self.retries[packet.msg_id] += 1
                retries = self.retries[packet.msg_id]
                if retries >= 5:
                    return "dropped"
                packet.checked_edges.discard(edge)
            return "retransmitting"
        
        self.retries[packet.msg_id] = 0
        return "ok"

class TransportLayer:
    def __init__(self, protocol):
        self.protocol = protocol

    def send(self, packet, network):
        return self.protocol.send(packet, network)

    def update(self, packet, network):
        return self.protocol.update(packet, network)