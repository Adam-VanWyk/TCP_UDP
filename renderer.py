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

    def draw(self, messages, selected_node=None):
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

        # Draw messages
        for msg in messages:
            print("DEGBUG packet state", msg.current_index, msg.path)
            edge = msg.get_current_edge()
            print("DEBUG edge:", edge)
            
            edge = msg.get_current_edge()
            if edge is None:
                continue
            start_node, end_node = edge
            
            start_pos = self._to_screen(self.graph_manager.pos[start_node])
            end_pos = self._to_screen(self.graph_manager.pos[end_node])

            x = start_pos[0] + (end_pos[0] - start_pos[0]) * msg.progress
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * msg.progress

            pygame.draw.circle(self.screen, (255, 100, 100), (int(x), int(y)), 6)

        # draw stats 
        stats = self.graph_manager.stats

        sent = stats["sent"]
        delivered = stats["delivered"]
        dropped = stats["dropped"]

        delivery_rate = (delivered / sent * 100) if sent > 0 else 0

        lines = [
            f"Mode: {self.graph_manager.network_mode.upper()}",
            f"Sent: {sent}",
            f"Delivered: {delivered}",
            f"Dropped: {dropped}",
            f"Delivery Rate: {delivery_rate:.1f}%"
        ]
        pygame.draw.rect(self.screen, (0, 0, 0), (5, 5, 180, 90), border_radius=8)

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10 + i * 20))
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
