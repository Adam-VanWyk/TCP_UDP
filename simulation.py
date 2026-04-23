# Class for messages and their atributes
import random

class Message:
    def __init__(self, path, graph_manager, speed=0.001, wait_time=30):
        self.path = path
        self.graph_manager = graph_manager
        self.current_index = 0
        self.progress = 0.0
        self.speed = speed

        self.wait_time = wait_time
        self.wait_counter = wait_time
        self.state = "waiting"

    def update(self):
        if self.state == "waiting":
            self.wait_counter -= 1
            if self.wait_counter <= 0:
            
                start = self.path[self.current_index]
                end = self.path[self.current_index + 1]

                loss_prob = self.graph_manager.edge_loss[(start, end)]

                if random.random() < loss_prob:
                    print(f"Packet DROPPED on edge {start} → {end}")
                    self.graph_manager.stats["dropped"] += 1
                    return True  # dropped

                self.state = "moving"
            return False
        
        elif self.state == "moving":
            start = self.path[self.current_index]
            end = self.path[self.current_index + 1]

            latency = self.graph_manager.edge_latency[(start, end)]
            self.progress += self.speed / latency

            if self.progress >= 1.0:
                self.progress = 0.0
                self.current_index += 1

                if self.current_index >= len(self.path) -1: # if reached final node
                    return True
                
                self.state = "waiting"
                self.wait_counter = self.wait_time
            return False
    def get_current_edge(self):
        if self.current_index >= len(self.path) - 1:
            return None #path done
        return(
            self.path[self.current_index],
            self.path[self.current_index+1]
        )
    

class Packet:
    def __init__(self, path, msg_id, packet_type="UDP", payload=None):
        self.path = path
        self.msg_id = msg_id
        self.packet_type = packet_type
        self.payload = payload

        self.current_index = 0
        self.progress = 0.0

        self.acknowledged = False
        self.dropped = False
        self.corrupted = False
        self.checked_edges = set()

        self.locked = False
        self.triggers_id = None
        self.handshake_complete = True
        self.original_msg_id = None
        self.retransmit_count = 0

        self.seq_num = 0
        self.ack_num = 0

        self.original_sent_time = None
        self.sent_time = None
        self.ack_received = False
        self.retransmit_cooldown = 0

    def get_current_edge(self):
        if self.current_index >= len (self.path) - 1:
            return None
        return (self.path[self.current_index],
                self.path[self.current_index + 1])
    