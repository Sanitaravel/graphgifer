import os
from queue import Queue
import shutil

import imageio
from graphviz import Digraph

from datetime import datetime

num_nodes = None
num_edges = None
graph = None

count_images = 0


def clear_graph_images():
    folder = './graph_images'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def from_images_to_gif():
    images = []
    _, _, filenames = next(os.walk('./graph_images'))
    tmp = []
    for filename in sorted(filenames):
        if filename[-3:] == 'png':
            tmp.append(filename)
    filenames = sorted(tmp, key=lambda x: int(x[:-7]))
    for filename in filenames:
        images.append(imageio.imread(f'./graph_images/{filename}'))
    kargs = {'duration': 1}
    imageio.mimsave(f'./graph_gifs/{datetime.now().strftime("%m-%d-%Y, %H.%M.%S")}.gif', images, **kargs)
    clear_graph_images()


def freeze_graph(colors, option):
    global num_nodes, graph, count_images
    if option == 2:
        color = ['white', 'gray', 'black']
        dot = Digraph(
            name='Graph',
            format='png',
            engine='neato'
        )
        for node in range(num_nodes):
            dot.node(
                name=f'{node}',
                label=f'<<font color="black">{node + 1}</font>>' if colors[node] in [0,
                                                                                     1] else f'<<font color="white">{node + 1}</font>>',
                style='filled',
                fillcolor=color[colors[node]],
            )

        for index, reachable_nodes in enumerate(graph):
            for node in reachable_nodes:
                dot.edge(str(index), str(node))

        dot.render(f'./graph_images/{count_images}.gv')
        count_images += 1
    else:
        color = ['white', 'gray', 'black']
        dot = Digraph(
            name='Graph',
            format='png',
        )
        for node in range(num_nodes):
            dot.node(
                name=f'{node}',
                label=f'<<font color="black">{node + 1}</font>>' if colors[node] in [0,
                                                                                     1] else f'<<font color="white">{node + 1}</font>>',
                style='filled',
                fillcolor=color[colors[node]],
            )

        for index, reachable_nodes in enumerate(graph):
            for node in reachable_nodes:
                dot.edge(str(index), str(node))

        dot.render(f'./graph_images/{count_images}.gv')
        count_images += 1


def read_num_nodes():
    while True:
        try:
            n = int(input("Input Number of Nodes: "))
        except ValueError:
            print("It's not a number!")
        else:
            if n <= 0:
                print("Number of Nodes Must Be More Than Zero!")
            else:
                return n


def read_num_edges():
    while True:
        try:
            m = int(input("Input Number of Edges: "))
        except ValueError:
            print("It's not a number!")
        else:
            if m <= 0:
                print("Number of Edges Must Be More Than Zero!")
            else:
                return m


def read_edge(edge_id):
    global num_nodes, num_edges
    while True:
        try:
            a, b = map(int, input(f"[{edge_id/num_edges*100:.2f}%] Enter start and end points of edge: ").split())
        except ValueError:
            print("It's not a number!")
        else:
            if a <= 0 or b <= 0:
                print("Number of Node Must Be More Than Zero!")
            if a > num_nodes or b > num_nodes:
                print("Number of Node Must Be Less Than Amount of Nodes!")
            else:
                break
    return a, b


def is_graph_with_cycles(g):
    global num_nodes
    cl = [0] * num_nodes

    def check_cycle_dfs(v):
        cl[v] = 1
        for to in g[v]:
            if cl[to] == 0:
                if check_cycle_dfs(to):
                    return True
            elif cl[to] == 1:
                return True
        cl[v] = 2
        return False

    for i in range(num_nodes):
        if check_cycle_dfs(i):
            return True
    return False


def read_graph(n, m, option):
    while True:
        g = [[] for i in range(n)]
        for idx in range(m):
            a, b = read_edge(idx)
            if option in [1, 2]:
                g[a - 1].append(b - 1)
            else:
                g[a - 1].append(b - 1)
                g[b - 1].append(a - 1)
        if option != 2:
            return g
        else:
            if not is_graph_with_cycles(g):
                print("[100.00%] Graph is correct")
                return g
            else:
                print("Graph has cycles")
                continue


def set_graph(option):
    global num_edges, num_nodes, graph
    num_nodes = read_num_nodes()
    num_edges = read_num_edges()
    graph = read_graph(num_nodes, num_edges, option)


def mode_dfs():
    global num_nodes, graph
    color = [0] * num_nodes
    freeze_graph(color, 1)

    def dfs(v):
        color[v] = 1
        freeze_graph(color, 1)
        for to in graph[v]:
            if color[to] == 0:
                dfs(to)
        color[v] = 2
        freeze_graph(color, 1)

    for i in range(num_nodes):
        if color[i] == 0:
            dfs(i)


def mode_bfs():
    global num_nodes, graph
    q = Queue()
    color = [0] * num_nodes

    def bfs(s):
        q.put(s)
        color[s] = 1
        freeze_graph(color, 2)
        while not q.empty():
            v = q.get()
            color[v] = 2
            freeze_graph(color, 2)
            for to in graph[v]:
                if color[to] == 0:
                    color[to] = 1
                    freeze_graph(color, 2)
                    q.put(to)

    for i in range(num_nodes):
        if color[i] == 0:
            bfs(i)


def mode_top_sort():
    global num_nodes, graph
    used = [False] * num_nodes
    ans = []

    def dfs(v):
        used[v] = True
        for to in graph[v]:
            if not used[to]:
                dfs(to)
        ans.append(v)

    for i in range(num_nodes):
        if not used[i]:
            dfs(i)

    ans = reversed(ans)

    color = [0] * num_nodes
    freeze_graph(color, option=1)
    for num in ans:
        color[num] = 1
        freeze_graph(color, option=1)
        color[num] = 2
        freeze_graph(color, option=1)


def main():
    print(
        """
        Hello!
        
        This program draw some algorithms on graph.
        
        Enter your graph as adjacency list.
        """
    )
    option = int(input(
        """
        Type 1, if you want to see DFS Traversal of a Directed Graph.
        Type 2, if you want to see Topological Sort of a Directed Acyclic Graph.
        Type 3, if you want to see BFS Traversal of an Undirected Graph.
        """
    ))
    set_graph(option)

    if option == 1:
        mode_dfs()
    elif option == 2:
        mode_top_sort()
    elif option == 3:
        mode_bfs()

    from_images_to_gif()


if __name__ == '__main__':
    main()
