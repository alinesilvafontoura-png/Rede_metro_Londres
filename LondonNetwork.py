import math
import os
from Graph import Graph
from read_data import ReadData
from visualize import Visualize


class LondonNetwork:
    def __init__(self):
        self.station_info = {}  # dicionário com informações de cada estação
        self.graph = Graph()    # grafo que representa a rede
        self._reader = ReadData(self.graph, self.station_info)       # partilha graph e station_info
        self._visualizer = Visualize(self.graph, self.station_info)  # partilha graph e station_info

    # ── leitura ────────────────────────────────────────────────────────

    def stations(self, file_stations):
        self._reader.stations(file_stations)  # delega a leitura das estações ao ReadData

    def connections(self, file_connections):
        self._reader.connections(file_connections)  # delega a leitura das ligações ao ReadData

    def lines(self, file_lines):
        return self._reader.lines(file_lines)  # delega a leitura das linhas ao ReadData

    # ── visualização ───────────────────────────────────────────────────

    def visualize(self, file_lines, output_file='visualizations/london_tube_map.html'):
        return self._visualizer.visualize(file_lines, output_file)  # delega ao Visualize

    def visualize_path(self, path, file_lines, output_file='visualizations/simulation.html'):
        return self._visualizer.visualize_path(path, file_lines, output_file)  # delega ao Visualize

    # ── métricas ───────────────────────────────────────────────────────

    def calculate_distance(self, id1, id2):
        """Calcula a distância em km entre duas estações (fórmula Haversine)."""
        s1 = self.station_info.get(id1)
        s2 = self.station_info.get(id2)
        if not s1 or not s2:
            return None
        raio = 6371.0  # raio da Terra em km
        lat1, lon1 = math.radians(float(s1['lat'])), math.radians(float(s1['lon']))
        lat2, lon2 = math.radians(float(s2['lat'])), math.radians(float(s2['lon']))
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return raio * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def n_stations(self):
        return self.graph.edge_count()  # número total de ligações

    def n_edges(self):
        return self.graph.vertex_count()

    def n_edges_line(self):
        edge_line = {}
        for edges in self.graph._iter_edges():  # CORRETO: self.graph._iter_edges()
            for edge in edges:
                line = edge.get_info()
                if line not in edge_line:
                    edge_line[line] = 0
                edge_line[line] += 1
        for line in edge_line:
            edge_line[line] = edge_line[line] // 2  # divide por 2 para evitar contagem dupla
        return edge_line

    def mean_weight(self, weight='uniform'):
        weighted_edges = []
        seen = set()
        for edges in self.graph._iter_edges():  # CORRETO: self.graph._iter_edges()
            for edge in edges:
                u, v = edge.get_vs()
                edge_id = frozenset([u, v])  # identifica a aresta pelos vértices
                if edge_id in seen:
                    continue
                seen.add(edge_id)
                if weight == 'uniform':
                    w = 1
                elif weight == 'distance':
                    w = self.calculate_distance(u, v)
                else:
                    w = int(edge.get_info())
                weighted_edges.append(w)
        if not weighted_edges:
            return 0
        return sum(weighted_edges) / len(weighted_edges)

    def mean_degree(self):
        degree = [self.graph.degree(node) for node in self.graph._iter_vertex()]  # CORRETO: self.graph._iter_vertex()
        if not degree:
            return 0
        return sum(degree) / self.n_stations()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta onde está este ficheiro

    network = LondonNetwork()
    network.stations(os.path.join(BASE_DIR, 'data/stations.csv'))
    network.connections(os.path.join(BASE_DIR, 'data/connections.csv'))

    print("=== INFORMAÇÕES GERAIS DA REDE ===")
    print(f"Nº de estações: {network.n_stations()}")
    print(f"Nº de ligações: {network.n_edges()}")
    print(f"Grau médio: {network.mean_degree():.2f}")
    print(f"Peso médio (uniforme): {network.mean_weight('uniform'):.2f}")
    print(f"Peso médio (distância): {network.mean_weight('distance'):.2f}")
    print(f"Ligações por linha: {network.n_edges_line()}")

    print("\n=== VISUALIZAÇÃO DA REDE ===")
    network.visualize(
        os.path.join(BASE_DIR, 'data/lines.csv'),
        output_file=os.path.join(BASE_DIR, 'visualizations/london_tube_map.html'))

