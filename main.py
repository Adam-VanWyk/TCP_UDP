from graph import GraphManager
from renderer import Renderer
from simulation import Message, Packet
from transport import TransportLayer, UDPProtocol, TCPProtocol

import networkx as nx
import pygame
import random


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
    gm.current_protocol = "udp"
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
                    gm.current_protocol = "udp"
                    print("Using UDP")
                elif event.key == pygame.K_t:
                    transport.protocol = TCPProtocol()
                    gm.current_protocol = "tcp"
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
                            
                            packet = Packet(path, msg_id=id(path),
                                             payload="")
                            gm.stats["sent"] += 1
                            new_packets = transport.send(packet, gm)
                            packets.extend(new_packets)

                        except nx.NetworkXNoPath:
                            print("No path.")
                        selected_node = None
        
        for packet in packets[:]:
            result, spawned = transport.update(packet, gm)
            packets.extend(spawned)

            if result == "dropped":
                packets.remove(packet)
                gm.stats["dropped"] += 1
                # Still unlock next in chain even on drop
                if packet.triggers_id:
                    for p in packets:
                        if p.msg_id == packet.triggers_id:
                            p.locked = False
                            if p.packet_type == "TCP_DATA":
                                p.handshake_complete = True
                continue

            if result in ("retransmitting", "waiting"):
                packet.progress = 0.0
                continue

            if packet.current_index >= len(packet.path) - 1:
                continue

            start   = packet.path[packet.current_index]
            end     = packet.path[packet.current_index + 1]
            latency = gm.edge_latency[(start, end)]
            packet.progress += 0.007 / latency

            if packet.progress >= 1.0:
                packet.progress = 0.0
                packet.current_index += 1

            if packet.current_index >= len(packet.path) - 1:
                if packet.packet_type == "TCP_DATA":
                    edge = (packet.path[-2], packet.path[-1])
                    if random.random() < gm.edge_corruption[edge]:
                        packet.corrupted = True
                        print(f"Packet {packet.payload} corrupted on arrival!")

                #packet.skip_corruption = False
                if packet.corrupted:
            # Send NACK back to sender
                    nack_path = list(reversed(packet.path))
                    nack = Packet(
                        nack_path,
                        msg_id=str(packet.msg_id) + "_nack",
                        packet_type="TCP_NACK"
                    )
                    nack.original_msg_id = packet.msg_id
                    packets.append(nack)
                    packet.locked = True
                    packet.corrupted = False
                    packet.retransmit_count += 1
                    print(f"NACK sent, retransmitting {packet.payload}")
                elif packet.packet_type == "TCP_NACK":
                    packets.remove(packet)
                    print(f"NACK received at sender, data already retransmitting")
                    for p in packets:
                        if p.msg_id == packet.original_msg_id:
                            p.locked = False
                            p.current_index = 0
                            p.progress = 0.0
                            p.checked_edges.clear()
                            print(f"Resending {p.payload}")
                            break

                else:
                    packets.remove(packet)
                    if packet.packet_type in ("UDP", "TCP_DATA"):
                        gm.stats["delivered"] += 1
                        if packet.payload:
                            print(f"Delivered: '{packet.payload}' via {packet.packet_type}")
                    if packet.triggers_id:
                        for p in packets:
                            if p.msg_id == packet.triggers_id:
                                p.locked = False
                                if p.packet_type == "TCP_DATA":
                                    p.handshake_complete = True

        renderer.draw(packets, selected_node)

    pygame.quit()


if __name__ == "__main__":
    main()
