import pygame
import math

WIDTH, HEIGHT = 800, 600
NODE_RADIUS = 25
# Pygame class to control locational logic
class Renderer:
    def __init__(self, graph_manager):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Graph Visualizer")
        self.clock = pygame.time.Clock()
        self.graph_manager = graph_manager
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, packets, selected_node=None):
        self.screen.fill((30, 30, 30))

    # Draw edges
        for edge in self.graph_manager.graph.edges():
            p1 = self._to_screen(self.graph_manager.pos[edge[0]])
            p2 = self._to_screen(self.graph_manager.pos[edge[1]])
            pygame.draw.line(self.screen, (200, 200, 200), p1, p2, 2)

    # Draw nodes
        for node in self.graph_manager.graph.nodes():
            pos = self._to_screen(self.graph_manager.pos[node])
            color = (100, 200, 255)
            if node == selected_node:
                color = (255, 255, 100)
            pygame.draw.circle(self.screen, color, pos, NODE_RADIUS)
            label = self.font.render(str(node), True, (30, 30, 30))
            self.screen.blit(label, (pos[0] - label.get_width()//2, pos[1] - label.get_height()//2))

        # Draw messages
        for packet in packets:
            #print("DEGBUG packet state", msg.current_index, msg.path)
            edge = packet.get_current_edge()
            
            if edge is None:
                continue
            start_node, end_node = edge
            start_pos = self._to_screen(self.graph_manager.pos[start_node])
            end_pos = self._to_screen(self.graph_manager.pos[end_node])

            x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * packet.progress)
            y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * packet.progress)
            ptype = packet.packet_type


            if ptype == "UDP":
                pygame.draw.circle(self.screen, (255, 100, 100), (x, y), 7)

            elif ptype == "TCP_SYN":
                # Yellow square
                pygame.draw.rect(self.screen, (255, 220, 50), (x-6, y-6, 12, 12))

            elif ptype == "TCP_SYN_ACK":
                # Yellow square, outlined
                pygame.draw.rect(self.screen, (255, 220, 50), (x-6, y-6, 12, 12), 2)

            elif ptype == "TCP_DATA":
                # Blue square
                color = (255, 80, 80) if packet.corrupted else (80, 140, 255)
                pygame.draw.rect(self.screen, color, (x-7, y-7, 14, 14))

            elif ptype == "TCP_ACK":
                # Small green square
                pygame.draw.rect(self.screen, (80, 220, 120), (x-4, y-4, 8, 8))

            elif ptype == "TCP_NACK":
                # Orange square
                pygame.draw.rect(self.screen, (255, 140, 50), (x-6, y-6, 12, 12))

            # Draw label above packet
            label_text = {
                "UDP": "UDP", 
                "TCP_SYN": "SYN", 
                "TCP_SYN_ACK": "SYN-ACK",
                "TCP_DATA": packet.payload or "DATA", 
                "TCP_ACK": packet.payload if packet.payload else "ACK", 
                "TCP_NACK": packet.payload if packet.payload else "NACK"
            }.get(ptype, "")
            if label_text:
                surf = self.font.render(label_text, True, (255, 255, 255))
                self.screen.blit(surf, (x - surf.get_width()//2, y - 20))


        # draw stats 
        stats = self.graph_manager.stats

        sent = stats["sent"]
        delivered = stats["delivered"]
        dropped = stats["dropped"]
        delivery_rate = (delivered / sent * 100) if sent > 0 else 0
        
        lines = [
            f"Protocol: {self.graph_manager.current_protocol.upper()}",
            f"Mode: {self.graph_manager.network_mode.upper()}",
            f"Sent: {sent}",
            f"Delivered: {delivered}",
            f"Dropped: {dropped}",
            f"Delivery Rate: {delivery_rate:.1f}%"
        ]
        pygame.draw.rect(self.screen, (0, 0, 0), (5, 5, 260, 120), border_radius=8)

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10 + i * 18))
        pygame.display.flip()
        self.clock.tick(60)

    # Adding user input by clicking nodes to apply messages
    def get_clicked_node(self, mouse_pos):
        for node in self.graph_manager.graph.nodes():
            node_pos = self._to_screen(self.graph_manager.pos[node])
            dist = math.dist(mouse_pos, node_pos)

            print(f"Mouse: {mouse_pos}, Node: {node}: {node_pos}, Dist: {dist}")

            if dist <= NODE_RADIUS:
                print(f"Clicked node {node}")
                return node
            
        print("\n")
        return None

    def _to_screen(self, pos):
        x = int(pos[0] * 300 + WIDTH // 2)
        y = int(pos[1] * 300 + HEIGHT // 2)
        return (x, y)
