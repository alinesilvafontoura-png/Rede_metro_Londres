import heapq  # fila de prioridade para aceder sempre ao nó de menor custo
import os
import networkx as nx  # biblioteca de grafos para a implementação alternativa do Dijkstra
from LondonNetwork import LondonNetwork


class Dijkstra:
    def __init__(self, london_network):
        # guarda a rede de Londres para aceder às suas informações
        self.network = london_network
        self._graph = london_network.graph  # acesso direto ao grafo interno da rede

    def count_lines(self, path):
        count = 0      # contador de mudanças de linha
        current = None  # linha atual (começa sem linha definida)

        # percorre cada par de estações consecutivas no caminho
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]     # estação atual e a seguinte

            # percorre as arestas da estação u
            for edge in self._graph._graph[u]:
                if edge.opposite(u) == v:        # encontra a aresta que liga u a v
                    line = edge.get_info()        # obtém o id da linha desta aresta
                    if current is not None and line != current:  # se a linha mudou
                        count += 1               # regista uma mudança de linha
                    current = line               # atualiza a linha atual
                    break                        # aresta encontrada, não é necessário continuar
        return count

    def dijkstra(self, start, end, weight_type='uniform'):
        # inicializa todas as estações com custo infinito (ainda não visitadas)
        best_value = {v: float("inf") for v in self._graph._iter_vertex()}
        best_value[start] = 0  # a estação de origem tem custo 0

        # guarda o vértice anterior no caminho ótimo para cada estação
        previous = {v: None for v in self._graph._iter_vertex()}

        visited = []         # lista de estações já processadas
        # fila de prioridade: (custo, estação, linha_atual)
        # a linha_atual é necessária para calcular a penalização de line_penalty
        # começa com a origem a custo 0 e sem linha definida
        queue = [(0, start, None)]

        while queue:  # enquanto houver estações por explorar
            current_cost, vertex, current_line = heapq.heappop(
                queue)  # retira a estação de menor custo

            if vertex in visited:
                continue            # ignora estações já processadas

            visited.append(vertex)  # marca a estação como visitada

            if vertex == end:
                break  # caminho até ao destino encontrado, pode parar

            # explora os vizinhos da estação atual
            for edge in self._graph._graph[vertex]:
                # estação do outro lado da aresta
                neighbor = edge.opposite(vertex)
                edge_line = edge.get_info()           # linha desta aresta

                if weight_type == 'uniform':
                    edge_cost = 1  # todas as arestas têm o mesmo custo: minimiza nº de estações
                elif weight_type == 'distance':
                    edge_cost = self.network.calculate_distance(
                        vertex, neighbor)  # custo = distância geográfica em km
                elif weight_type == 'line_penalty':
                    dist = self.network.calculate_distance(
                        vertex, neighbor)  # distância base
                    alpha = 5  # fator de penalização por mudança de linha
                    # penaliza se a linha da aresta é diferente da linha usada para chegar aqui
                    penalty = alpha if (
                        current_line is not None and edge_line != current_line) else 0
                    edge_cost = dist + penalty  # custo total = distância + penalização
                else:
                    edge_cost = 1  # fallback para custo uniforme

                new_cost = current_cost + edge_cost  # custo acumulado até ao vizinho

                # encontrou um caminho melhor para o vizinho
                if new_cost < best_value[neighbor]:
                    # atualiza o melhor custo conhecido
                    best_value[neighbor] = new_cost
                    # regista de onde viemos para reconstruir o caminho
                    previous[neighbor] = vertex
                    # adiciona o vizinho à fila com a linha desta aresta
                    heapq.heappush(queue, (new_cost, neighbor, edge_line))

        # reconstrói o caminho do destino até à origem seguindo os antecessores
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = previous[node]
        path.reverse()           # inverte para obter o caminho da origem para o destino
        return path, best_value[end]  # devolve o caminho e o custo total

    def dijkstra_nx(self, start, end, weight_type='uniform'):
        graph_nx = nx.Graph()  # cria um grafo NetworkX vazio

        for vertex in self._graph._iter_vertex():   # percorre todos os vértices da rede
            # percorre as arestas de cada vértice
            for edge in self._graph._graph[vertex]:
                neighbor = edge.opposite(vertex)     # estação vizinha

                if weight_type == 'uniform':
                    edge_cost = 1  # custo uniforme
                elif weight_type == 'distance':
                    edge_cost = self.network.calculate_distance(
                        vertex, neighbor)  # distância geográfica
                elif weight_type == 'line_penalty':
                    alpha = 5
                    edge_cost = self.network.calculate_distance(
                        vertex, neighbor) + alpha  # distância + penalização fixa
                else:
                    edge_cost = 1

                # adiciona a aresta ao grafo NetworkX com o custo calculado
                graph_nx.add_edge(vertex, neighbor, weight=edge_cost)

        # aplica o Dijkstra do NetworkX sobre o grafo construído
        # sequência de estações do caminho ótimo
        path = nx.dijkstra_path(graph_nx, start, end, weight='weight')
        cost = nx.dijkstra_path_length(
            graph_nx, start, end, weight='weight')  # custo total do caminho
        return path, cost

    def simulate(self, start, end, weight_type='uniform', use_nx=False):
        if use_nx:
            # usa a implementação NetworkX
            path, cost = self.dijkstra_nx(start, end, weight_type)
        else:
            # usa a implementação própria
            path, cost = self.dijkstra(start, end, weight_type)

        n_stations = len(path)           # número total de estações no percurso
        # número de mudanças de linha no percurso
        changes = self.count_lines(path)

        # apresenta os resultados com os nomes das estações em vez dos ids
        print(
            f"Caminho: {[self.network.station_info[s]['name'] for s in path]}")
        print(f"Nº estações: {n_stations}")
        print(f"Custo total: {cost:.4f}")
        print(f"Mudanças de linha: {changes}")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.network.visualize_path(
            path,
            os.path.join(BASE_DIR, 'data/lines.csv'),
            output_file=os.path.join(
                BASE_DIR, 'visualizations/simulation.html')
        )

        return path, cost, n_stations, changes


if __name__ == "__main__":
    # pasta onde está este ficheiro
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # construir a rede antes de criar o Dijkstra
    network = LondonNetwork()
    network.stations(os.path.join(BASE_DIR, 'data/stations.csv'))
    network.connections(os.path.join(BASE_DIR, 'data/connections.csv'))

    dijkstra = Dijkstra(network)  # criado depois de carregar os dados

    # estações de teste (confirma os ids no teu stations.csv)
    BAKER_STREET = '11'   # Baker Street
    VICTORIA = '274'  # Victoria
    KINGS_CROSS = '130'  # King's Cross St. Pancras
    BRIXTON = '49'   # Brixton
    HAMMERSMITH = '100'  # Hammersmith
    LIVERPOOL_ST = '144'  # Liverpool Street

    print("\n=== TESTE 1 — Trajeto curto (mesma linha) ===")
    print("Baker Street → King's Cross | uniforme vs distância\n")
    for wt in ['uniform', 'distance']:
        path, cost, n, changes = dijkstra.simulate(
            BAKER_STREET, KINGS_CROSS, weight_type=wt)
        print(f"  [{wt}] custo={cost:.4f} | estações={n} | mudanças={changes}\n")

    print("\n=== TESTE 2 — Trajeto longo (linhas diferentes) ===")
    print("Brixton → Hammersmith | uniforme vs distância vs line_penalty\n")
    for wt in ['uniform', 'distance', 'line_penalty']:
        path, cost, n, changes = dijkstra.simulate(
            BRIXTON, HAMMERSMITH, weight_type=wt)
        print(f"  [{wt}] custo={cost:.4f} | estações={n} | mudanças={changes}\n")

    print("\n=== TESTE 3 — Trajeto com múltiplos transbordos ===")
    print("Victoria → Liverpool Street | uniforme vs line_penalty\n")
    for wt in ['uniform', 'line_penalty']:
        path, cost, n, changes = dijkstra.simulate(
            VICTORIA, LIVERPOOL_ST, weight_type=wt)
        print(f"  [{wt}] custo={cost:.4f} | estações={n} | mudanças={changes}\n")

    print("\n=== TESTE 4 — Comparação implementação própria vs NetworkX ===")
    print("Baker Street → Victoria | distância\n")
    path_own, cost_own, n_own, ch_own = dijkstra.simulate(
        BAKER_STREET, VICTORIA, weight_type='distance', use_nx=False)
    path_nx,  cost_nx,  n_nx,  ch_nx = dijkstra.simulate(
        BAKER_STREET, VICTORIA, weight_type='distance', use_nx=True)
    print(
        f"  Próprio  → custo={cost_own:.4f} | estações={n_own} | mudanças={ch_own}")
    print(
        f"  NetworkX → custo={cost_nx:.4f} | estações={n_nx} | mudanças={ch_nx}")
    print(f"  Caminhos iguais: {path_own == path_nx}")
