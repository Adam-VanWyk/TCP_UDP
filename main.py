from graph import GraphManager
from renderer import Renderer
from simulation import Message
import pygame

def get_user_graph():
    num_nodes = int(input("Number of nodes: "))
    num_edges = int(input("Number of edges: "))

    edges = []
    for _ in range(num_edges):
        while True:
            u, v = map(int, input("Edge (u v): ").split())

            if u == v:
                print("No self loops.")
            elif (u, v) in edges or (v, u) in edges:
                print("Edge already exists.")
            elif 0 <= u < num_nodes and 0 <= v < num_nodes:
                edges.append((u, v))
                break
            else: 
                print(f"Invalid edge, nodes must be between 0-{num_nodes -1}")

    return num_nodes, edges


def main():
    gm = GraphManager()

    #Get user input for graph creation
    num_nodes, edges = get_user_graph()
    gm.create_graph(num_nodes, edges)

    renderer = Renderer(gm)
    messages = []

    selected_node = None
# main loop of game/interaction -----------------------------------------
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = renderer.get_clicked_node(pygame.mouse.get_pos())

                if clicked is not None:
                    if selected_node is None:
                        selected_node = clicked
                    else:
                        messages.append(Message(selected_node, clicked))
                        selected_node = None

        # Update messages
        for msg in messages[:]:
            if msg.update():
                messages.remove(msg)

        renderer.draw(messages)

    pygame.quit()


if __name__ == "__main__":
    main()
