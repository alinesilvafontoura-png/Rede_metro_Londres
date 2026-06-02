import heapq  # fila de prioridade para aceder sempre ao nó de menor custo
import os
import networkx as nx  # biblioteca de grafos para a implementação alternativa do Dijkstra
from LondonNetwork import LondonNetworkGraph


class Dijkstra:

    def __init__(self, london_network):
        # guarda a rede de Londres para aceder às suas informações
        self.network = london_network

        # acesso direto ao grafo interno da rede
        self._graph = london_network.graph

    def count_lines(self, path):

        count = 0        # contador de mudanças de linha
        current = None   # linha atual

        # percorre pares consecutivos do caminho
        for i in range(len(path) - 1):

            u, v = path[i], path[i + 1]

            # percorre as arestas da estação u
            for edge in self._graph._graph[u]:

                # encontra a aresta que liga u a v
                if edge.opposite(u) == v:

                    line = edge.get_info()

                    # se mudou de linha
                    if current is not None and line != current:
                        count += 1

                    current = line
                    break

        return count

    def dijkstra(self, start, end, weight_type='uniform'):

        # inicializa todas as estações com custo infinito
        best_value = {v: float("inf") for v in self._graph._iter_vertex()}

        # origem começa com custo 0
        best_value[start] = 0

        # guarda o vértice anterior para reconstruir o caminho
        previous = {v: None for v in self._graph._iter_vertex()}

        # conjunto de vértices já processados
        visited = set()

        # fila de prioridade:
        # (custo_total, estação, linha_atual)
        queue = [(0, start, None)]

        while queue:
            # remove o nó de menor custo
            current_cost, vertex, current_line = heapq.heappop(queue)

            # ignora se já foi processado
            if vertex in visited:
                continue

            visited.add(vertex)

            # chegou ao destino
            if vertex == end:
                break

            # explora vizinhos
            for edge in self._graph._graph[vertex]:
                neighbor = edge.opposite(vertex)

                # linha da aresta atual
                edge_line = edge.get_info()

                # calcula distância apenas uma vez
                dist = self.network.calculate_distance(vertex, neighbor)

                # proteção contra dados inválidos
                if dist is None:
                    continue

                # -----------------------------
                # cálculo do custo da aresta
                # -----------------------------

                if weight_type == 'uniform':
                    # todas as arestas custam 1
                    edge_cost = 1

                elif weight_type == 'distance':
                    # custo = distância geográfica
                    edge_cost = dist

                elif weight_type == 'line_penalty':
                    # penalização por mudança de linha
                    alpha = 5
                    penalty = alpha if (
                        current_line is not None and edge_line != current_line) else 0
                    edge_cost = dist + penalty

                else:
                    edge_cost = 1

                # custo acumulado
                new_cost = current_cost + edge_cost

                # encontrou caminho melhor
                if new_cost < best_value[neighbor]:
                    best_value[neighbor] = new_cost
                    # guarda antecessor
                    previous[neighbor] = vertex
                    # adiciona à queue
                    heapq.heappush(queue, (new_cost, neighbor, edge_line))

        # se não existir caminho
        if best_value[end] == float("inf"):
            return [], float("inf")
        # -----------------------------
        # reconstrução do caminho
        # -----------------------------
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = previous[node]

        # inverter:
        # destino -> origem  ==> origem -> destino
        path.reverse()
        return path, best_value[end]

    def dijkstra_nx(self, start, end, weight_type='uniform'):
        # NetworkX não suporta diretamente
        # penalizações dinâmicas por mudança de linha
        if weight_type == 'line_penalty':
            print(
                "\n[AVISO] O NetworkX não suporta "
                "penalizações dinâmicas por mudança de linha."
            )

            print(
                "A calcular usando apenas "
                "'distance' como aproximação.\n"
            )

            weight_type = 'distance'

        # cria grafo NetworkX vazio
        graph_nx = nx.Graph()

        # percorre todos os vértices
        for vertex in self._graph._iter_vertex():

            # percorre arestas do vértice
            for edge in self._graph._graph[vertex]:
                neighbor = edge.opposite(vertex)
                dist = self.network.calculate_distance(vertex, neighbor)
                if dist is None:
                    continue

                # cálculo do custo
                if weight_type == 'uniform':
                    edge_cost = 1

                elif weight_type == 'distance':
                    edge_cost = dist

                else:
                    edge_cost = 1

                # adiciona aresta ao grafo
                graph_nx.add_edge(
                    vertex,
                    neighbor,
                    weight=edge_cost
                )

        # caminho ótimo
        path = nx.dijkstra_path(
            graph_nx,
            start,
            end,
            weight='weight'
        )

        # custo total
        cost = nx.dijkstra_path_length(
            graph_nx,
            start,
            end,
            weight='weight'
        )

        return path, cost

    def simulate(self, start, end, weight_type='uniform', use_nx=False):

        # escolher implementação
        if use_nx:

            path, cost = self.dijkstra_nx(
                start,
                end,
                weight_type
            )

        else:

            path, cost = self.dijkstra(
                start,
                end,
                weight_type
            )

        # nº de estações
        n_stations = len(path)

        # nº de mudanças de linha
        changes = self.count_lines(path)

        # mostrar resultados
        print(
            f"Caminho: "
            f"{[self.network.station_info[s]['name'] for s in path]}"
        )

        print(f"Nº estações: {n_stations}")

        print(f"Custo total: {cost:.4f}")

        print(f"Mudanças de linha: {changes}")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # gerar visualização
        self.network.visualize_path(
            path,
            os.path.join(BASE_DIR, 'data/lines.csv'),
            output_file=os.path.join(
                BASE_DIR,
                'visualizations/simulation.html'
            )
        )

        return path, cost, n_stations, changes


if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # construir rede
    network = LondonNetworkGraph()

    network.stations(
        os.path.join(BASE_DIR, 'data/stations.csv')
    )

    network.connections(
        os.path.join(BASE_DIR, 'data/connections.csv')
    )

    # criar Dijkstra
    dijkstra = Dijkstra(network)

    # ids de teste
    BAKER_STREET = '11'
    VICTORIA = '273'
    KINGS_CROSS = '145'
    BRIXTON = '35'
    HAMMERSMITH = '110'
    LIVERPOOL_ST = '156'

    print("\n=== TESTE 1 — Trajeto curto ===")

    for wt in ['uniform', 'distance']:

        path, cost, n, changes = dijkstra.simulate(
            BAKER_STREET,
            KINGS_CROSS,
            weight_type=wt
        )

        print(
            f"[{wt}] "
            f"custo={cost:.4f} | "
            f"estações={n} | "
            f"mudanças={changes}\n"
        )

    print("\n=== TESTE 2 — Trajeto longo ===")

    for wt in ['uniform', 'distance', 'line_penalty']:

        path, cost, n, changes = dijkstra.simulate(
            BRIXTON,
            HAMMERSMITH,
            weight_type=wt
        )

        print(
            f"[{wt}] "
            f"custo={cost:.4f} | "
            f"estações={n} | "
            f"mudanças={changes}\n"
        )

    print("\n=== TESTE 3 — Comparação com NetworkX ===")

    path_own, cost_own, n_own, ch_own = dijkstra.simulate(
        BAKER_STREET,
        VICTORIA,
        weight_type='distance',
        use_nx=False
    )

    path_nx, cost_nx, n_nx, ch_nx = dijkstra.simulate(
        BAKER_STREET,
        VICTORIA,
        weight_type='distance',
        use_nx=True
    )

    print(
        f"Próprio  → custo={cost_own:.4f} | "
        f"estações={n_own} | "
        f"mudanças={ch_own}"
    )

    print(
        f"NetworkX → custo={cost_nx:.4f} | "
        f"estações={n_nx} | "
        f"mudanças={ch_nx}"
    )

    print(f"Caminhos iguais: {path_own == path_nx}")
