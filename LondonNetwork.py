import math
import os
from Graph import Graph
from read_data import ReadData
from visualize import Visualize


class LondonNetwork:
    def __init__(self):
        self.station_info = {}  # dicionário com informações de cada estação
        self.graph = Graph()    # grafo que representa a rede
        # partilha graph e station_info
        self._reader = ReadData(self.graph, self.station_info)
        # partilha graph e station_info
        self._visualizer = Visualize(self.graph, self.station_info)

    # ── leitura ────────────────────────────────────────────────────────

    def stations(self, file_stations):
        # delega a leitura das estações ao ReadData
        self._reader.stations(file_stations)

    def connections(self, file_connections):
        # delega a leitura das ligações ao ReadData
        self._reader.connections(file_connections)

    def lines(self, file_lines):
        # delega a leitura das linhas ao ReadData
        return self._reader.lines(file_lines)

    # ── visualização ───────────────────────────────────────────────────

    def visualize(self, file_lines, output_file='visualizations/london_tube_map.html'):
        # delega ao Visualize
        return self._visualizer.visualize(file_lines, output_file)

    def visualize_path(self, path, file_lines, output_file='visualizations/simulation.html'):
        # delega ao Visualize
        return self._visualizer.visualize_path(path, file_lines, output_file)

    # ── métricas ───────────────────────────────────────────────────────

    def calculate_distance(self, id1, id2):
        """Calcula a distância em km entre duas estações (fórmula Haversine)."""
        s1 = self.station_info.get(id1)
        s2 = self.station_info.get(id2)
        if not s1 or not s2:
            return None
        raio = 6371.0  # raio da Terra em km
        lat1, lon1 = math.radians(
            float(s1['lat'])), math.radians(float(s1['lon']))
        lat2, lon2 = math.radians(
            float(s2['lat'])), math.radians(float(s2['lon']))
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * \
            math.cos(lat2) * math.sin(dlon / 2) ** 2
        return raio * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def n_stations(self):
        return self.graph.vertex_count()  # número total de estações

    def n_edges(self):
        return self.graph.edge_count()  # número total de ligações

    def n_edges_line(self):
        edge_line = {}
        for edges in self.graph._iter_edges():  # CORRETO: self.graph._iter_edges()
            for edge in edges:
                line = edge.get_info()
                if line not in edge_line:
                    edge_line[line] = 0
                edge_line[line] += 1
        for line in edge_line:
            # divide por 2 para evitar contagem dupla
            edge_line[line] = edge_line[line] // 2
        return edge_line

    def mean_weight(self):
        # Calcula o peso médio das arestas (média dos IDs das linhas)
        total = 0
        count = 0
        seen = set()
        for edges in self.graph._iter_edges():
            for edge in edges:
                u, v = edge.get_vs()
                # identifica a aresta pelos vértices
                edge_id = frozenset([u, v])
                if edge_id in seen:
                    continue
                seen.add(edge_id)
                total += int(edge.get_info())
                count += 1
        if count == 0:
            return 0
        return total / count

    def mean_degree(self):
        # CORRETO: self.graph._iter_vertex()
        degree = [self.graph.degree(node)
                  for node in self.graph._iter_vertex()]
        if not degree:
            return 0
        return sum(degree) / self.n_stations()


if __name__ == "__main__":
    # pasta onde está este ficheiro
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    network = LondonNetwork()
    network.stations(os.path.join(BASE_DIR, 'data/stations.csv'))
    network.connections(os.path.join(BASE_DIR, 'data/connections.csv'))

    print("=== INFORMAÇÕES GERAIS DA REDE ===")
    print(f"Nº de estações: {network.n_stations()}")
    print(f"Nº de ligações: {network.n_edges()}")
    print(f"Grau médio: {network.mean_degree():.2f}")
    print(f"Peso médio: {network.mean_weight():.2f}")
    print(f"Ligações por linha: {network.n_edges_line()}")

    print("\n=== VISUALIZAÇÃO DA REDE ===")
    network.visualize(
        os.path.join(BASE_DIR, 'data/lines.csv'),
        output_file=os.path.join(BASE_DIR, 'visualizations/london_tube_map.html'))
