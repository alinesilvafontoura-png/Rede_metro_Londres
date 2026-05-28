import os
from LondonNetwork import LondonNetwork


class UnionFind:
    # Estrutura Union-Find para detetar ciclos no algoritmo de Kruskal.
    # Funciona como uma floresta de conjuntos:
    # - find(x): encontra em que conjunto está x
    # - union(x, y): une dois conjuntos

    def __init__(self, vertices):
        # cada vértice começa como seu próprio pai
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}     # profundidade de cada árvore

    def find(self, x):
        # Encontra a raiz do conjunto de x (com compressão de caminho)
        if self.parent[x] != x:
            # compressão: aponta direto para a raiz
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        # Une os conjuntos de x e y. Devolve True se a união foi feita, False se já estavam juntos
        rx, ry = self.find(x), self.find(y)   # encontra as raízes
        if rx == ry:
            return False                         # já estão no mesmo conjunto → formaria ciclo

        # União por rank: a árvore mais pequena aponta para a maior
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx                     # ry passa a apontar para rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1                   # se igual rank, incrementa
        return True


class Kruskal:
    # Algoritmo de Kruskal para encontrar a Árvore Geradora Mínima (MST)

    def __init__(self, london_network):
        self.network = london_network
        self._graph = london_network.graph

    def _get_edge_cost(self, u, v, edge, weight_type):
        # Calcula o custo de uma aresta conforme a função de custo escolhida
        if weight_type == 'uniform':
            # Custo uniforme: todas as arestas valem 1 (minimiza nº de estações)
            return 1
        elif weight_type == 'distance':
            # Custo baseado na distância geográfica (minimiza km percorridos)
            return self.network.calculate_distance(u, v)
        elif weight_type == 'line_penalty':
            # Custo = distância + penalização por linha
            # Linhas com ID maior são mais penalizadas
            alpha = 5                                 # fator de penalização
            dist = self.network.calculate_distance(u, v)
            line_id = int(edge.get_info())
            return dist + alpha * line_id
        return 1  # fallback

    def kruskal(self, weight_type='uniform'):
        # Algoritmo de Kruskal para encontrar a MST.
        #
        # Passos:
        # 1. Recolher todas as arestas e calcular o seu custo
        # 2. Ordenar arestas por custo (do mais barato ao mais caro)
        # 3. Escolher iterativamente a aresta mais barata que não cria ciclo
        # 4. Usar Union-Find para verificar se cria ciclo
        #
        # Devolve: (mst_edges, total_cost)

        # Passo 1: Recolher todas as arestas únicas com o seu custo
        edges = []
        seen = set()
        for vertex in self._graph._iter_vertex():
            for edge in self._graph._graph[vertex]:
                u, v = edge.get_vs()
                edge_id = frozenset([u, v])
                if edge_id in seen:
                    continue                      # evitar contagem dupla
                seen.add(edge_id)
                cost = self._get_edge_cost(u, v, edge, weight_type)
                edges.append((cost, u, v, edge))

        # Passo 2: Ordenar arestas por custo (da mais barata à mais cara)
        edges.sort(key=lambda x: x[0])

        # Passo 3 e 4: Kruskal com Union-Find
        uf = UnionFind(self._graph._iter_vertex())
        mst_edges = []       # arestas selecionadas para a MST
        total_cost = 0

        for cost, u, v, edge in edges:
            if uf.union(u, v):                   # se NÃO cria ciclo, adicionar à MST
                mst_edges.append((u, v, edge, cost))
                total_cost += cost

        return mst_edges, total_cost

    def count_line_changes(self, mst_edges):
        # Conta o número de mudanças de linha na MST
        lines_used = set()
        for u, v, edge, cost in mst_edges:
            lines_used.add(int(edge.get_info()))
        # Se há N linhas diferentes, há N-1 mudanças
        return max(0, len(lines_used) - 1)

    def original_network_cost(self, weight_type='uniform'):
        # Calcula o custo total da rede original para comparação com a MST
        total = 0
        seen = set()
        for vertex in self._graph._iter_vertex():
            for edge in self._graph._graph[vertex]:
                u, v = edge.get_vs()
                edge_id = frozenset([u, v])
                if edge_id in seen:
                    continue
                seen.add(edge_id)
                total += self._get_edge_cost(u, v, edge, weight_type)
        return total

    def simulate(self, weight_type='uniform', file_lines=None, output_file=None):
        # Executa o Kruskal e mostra os resultados completos
        print(f"\n{'='*55}")
        print(f"  KRUSKAL — Função de custo: {weight_type}")
        print(f"{'='*55}")

        mst_edges, total_cost = self.kruskal(weight_type)

        # Número de arestas (únicas, sem contagem dupla)
        seen = set()
        for vertex in self._graph._iter_vertex():
            for edge in self._graph._graph[vertex]:
                u, v = edge.get_vs()
                seen.add(frozenset([u, v]))
        n_original = len(seen)    # arestas únicas na rede original
        n_mst = len(mst_edges)

        # Custo da rede original
        original_cost = self.original_network_cost(weight_type)

        # Contagem de mudanças de linha
        line_changes = self.count_line_changes(mst_edges)

        # Linhas utilizadas
        lines_used = set()
        for u, v, edge, cost in mst_edges:
            lines_used.add(int(edge.get_info()))

        print(f"  Arestas na rede original:  {n_original}")
        print(f"  Arestas na MST:             {n_mst}")
        print(f"  Custo total rede original:  {original_cost:.4f}")
        print(f"  Custo total da MST:         {total_cost:.4f}")
        print(
            f"  Poupança:                   {original_cost - total_cost:.4f}")
        print(f"  Linhas utilizadas:          {len(lines_used)}")
        print(f"  Mudanças de linha:          {line_changes}")

        # Visualização (se fornecido o ficheiro de linhas)
        if file_lines and output_file:
            self.network.visualize_mst(
                mst_edges, file_lines, output_file=output_file
            )

        return mst_edges, total_cost


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    network = LondonNetwork()
    network.stations(os.path.join(BASE_DIR, 'data', 'stations.csv'))
    network.connections(os.path.join(BASE_DIR, 'data', 'connections.csv'))

    kruskal = Kruskal(network)

    # Testar com as 3 funções de custo
    for wt in ['uniform', 'distance', 'line_penalty']:
        mst_edges, total_cost = kruskal.simulate(
            weight_type=wt,
            file_lines=os.path.join(BASE_DIR, 'data', 'lines.csv'),
            output_file=os.path.join(
                BASE_DIR, f'visualizations/kruskal_{wt}.html')
        )

    print("\n✅ Kruskal concluído!")
