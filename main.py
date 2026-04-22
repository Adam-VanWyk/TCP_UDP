from graph import GraphManager
from renderer import Renderer
from simulation import Message, Packet
from transport import TransportLayer, UDPProtocol, TCPProtocol

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
    transport = TransportLayer(UDPProtocol()) # basic

    #Get user input for graph creation
    num_nodes, edges = get_user_graph()
    gm.create_graph(num_nodes, edges)

    renderer = Renderer(gm)
    packets = []

    selected_node = None
# main loop of game/interaction -----------------------------------------
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    gm.set_network_mode("low")
                elif event.key == pygame.K_2:
                    gm.set_network_mode("medium")
                elif event.key == pygame.K_3:
                    gm.set_network_mode("high")
                
                elif event.key == pygame.K_u:
                    transport.protocol = UDPProtocol()
                    print("Using UDP")
                elif event.key == pygame.K_t:
                    transport.protocol = TCPProtocol()
                    print("Using TCP")

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
                            #msg = Message(path, gm)
                            packet = Packet(path, msg_id=id(path))
                            transport.send(packet, gm)

                            gm.stats["sent"] += 1
                            start_node = path[0]

                            packets.append(packet)
                            #gm.queues[start_node].append(packet)
                        except nx.NetworkXNoPath:
                            print("No path.")
                        selected_node = None
        # Queue handling
        # for node in gm.queues:
        #     queue = gm.queues[node]
        #     if queue:
        #         msg = queue[0]
        #         done = msg.update()

        #         if msg.state == "moving":
        #             messages.append(msg)
        #             queue.pop(0)
        #         elif done:
        #             queue.pop(0)

        # # message movement
        # for msg in messages[:]:
        #     done = msg.update()

        #     if done:
        #         messages.remove(msg)
        #         gm.stats["delivered"] += 1
        #         print("Message delivered")
        #     else:
        #         if msg.progress == 0.0 and msg.state == "waiting":
        #             messages.remove(msg)
        #             next_node = msg.path[msg.current_index]
        #             gm.queues[next_node].append(msg)

        for packet in packets[:]:
            result = transport.update(packet, gm)

            if result == "dropped":
                packets.remove(packet)
                gm.stats["dropped"] += 1
                continue

            if result == "retransmitting":
                packet.progress = 0.0
                continue
            
            start = packet.path[packet.current_index]
            end = packet.path[packet.current_index + 1]

            latency = gm.edge_latency[(start, end)]
            packet.progress += 0.1 / latency


            if packet.progress >= 1.0:
                packet.progress = 0.0
                packet.current_index += 1

            if packet.current_index >= len(packet.path) - 1:
                packets.remove(packet)
                gm.stats["delivered"] += 1

            #packet.step_forward(gm)     
        # re-queue behavior (keeps your visual system working)
                # messages.remove(packet)
                # next_node = packet.path[packet.current_index]
                # gm.queues[next_node].append(packet)

        renderer.draw(packets, selected_node)

        # print(
        #     f"Sent: {gm.stats['sent']} | "
        #     f"Delivered: {gm.stats['delivered']} | "
        #     f"Dropped: {gm.stats['dropped']}"

        # )

    pygame.quit()


if __name__ == "__main__":
    main()
