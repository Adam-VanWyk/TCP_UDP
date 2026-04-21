# Class for messages and their atributes
import random

class Message:
    def __init__(self, path, graph_manager, speed=0.01, wait_time=30):
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