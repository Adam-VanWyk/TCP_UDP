from graph import GraphManager
from renderer import Renderer
from simulation import Message
import networkx as nx
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
                        print(f"Selected first node: {selected_node}")
                    else:
                        if selected_node == clicked:
                            print("same node, ignore")
                            selected_node = None
                            continue
                        print(f"Sending message: {selected_node} → {clicked}")
                        #messages.append(Message(selected_node, clicked)) try node paths
                        try:
                            path = nx.shortest_path(gm.graph, selected_node, clicked)
                            print(f"Path: {path}")
                            #messages.append(Message(path))
                            msg = Message(path)
                            start_node = path[0]
                            gm.queues[start_node].append(msg)
                        except nx.NetworkXNoPath:
                            print("No path.")
                        selected_node = None
        # Queue handling
        for node in gm.queues:
            queue = gm.queues[node]
            if queue:
                msg = queue[0]
                done = msg.update()

                if msg.state == "moving":
                    messages.append(msg)
                    queue.pop(0)
                elif done:
                    queue.pop(0)

        # message movement
        for msg in messages[:]:
            done = msg.update()

            if done:
                messages.remove(msg)
                print("Message delivered")
            else:
                if msg.progress == 0.0 and msg.state == "waiting":
                    messages.remove(msg)
                    next_node = msg.path[msg.current_index]
                    gm.queues[next_node].append(msg)

        renderer.draw(messages, selected_node)

    pygame.quit()


if __name__ == "__main__":
    main()
