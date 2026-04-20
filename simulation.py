# Class for messages and their atributes

class Message:
    def __init__(self, path, speed=0.01):
        self.path = path
        self.current_index = 0
        self.progress = 0.0
        self.speed = speed
    def update(self):
        self.progress += self.speed

        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_index += 1

            if self.current_index >= len(self.path) -1: # if reached final node
                return True
            
        return False
    def get_current_edge(self):
        return(
            self.path[self.current_index],
            self.path[self.current_index+1]
        )