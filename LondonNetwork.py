from Graph import Graph
import math


class LondonNetwork:
    def __init__(self):
        self.station_info = {}
        self.graph = Graph()

    def stations(self, file_stations):
        with open(file_stations, 'r') as file:
            # salta o cabeçalho
            next(file)
            for line in file:  # por cada linha do ficheiro
                data = line.strip().split(',')  # escreve uma informação por linha
                station_id = data[0]
                latitude = float(data[1])
                longitude = float(data[2])
                name = data[3]

                # no grafo é adicionado um nó que guarda estas informações
                self.graph.add_vertex(station_id, payload={
                                      'lat': latitude, 'lon': longitude, 'name': name})

    def connections(self, file_connections):
        with open(file_connections, 'r') as file:
            # salta o cabeçalho
            next(file)
            for row in file:
                data = row.strip().split(',')
                line_id = int(data[0])
                station1 = data[1]
                station2 = data[2]

                # no grafo é adicionado uma aresta que segue estas orientações
                self.graph.add_edge(station1, station2, weight=line_id)

    def lines(self, file_lines):
        lines = {}
        with open(file_lines, 'r') as file:
            next(file)
            for row in file:
                data = row.strip().split(',')
                line_id = int(data[0])
                name = data[1]
                lines[line_id] = name
        return lines

    def load_stations_info(self, file_stations):
        """Lê o ficheiro e guarda info das estações (nome, coordenadas)."""
        with open(file_stations, 'r') as file:
            next(file)  # salta cabeçalho
            for line in file:
                data = line.strip().split(',')
                station_id = data[0]
                latitude = float(data[1])
                longitude = float(data[2])
                name = data[3]
                self.station_info[station_id] = {
                    'name': name, 'lat': latitude, 'lon': longitude}

    def calculate_distance(self, id1, id2):
        """Calcula a distância em km entre duas estações (fórmula Haversine)."""
        s1 = self.station_info.get(id1)
        s2 = self.station_info.get(id2)
        if not s1 or not s2:
            return None

        R = 6371.0  # Raio da Terra em km
        lat1, lon1 = math.radians(
            float(s1['lat'])), math.radians(float(s1['lon']))
        lat2, lon2 = math.radians(
            float(s2['lat'])), math.radians(float(s2['lon']))

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * \
            math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

# utilização dos métodos provenientes de Graph
    def n_stations(self):
        return self.graph.vertex_count()

    def n_edges(self):
        return self.graph.edge_count()

    def n_edge_line(self):
        edge_line = {}  # criar um dicionário
        for edges in self.graph._iter_edges():  # edges= lista de arestas de um vértie
            for edge in edges:  # edge= uma aresta individual
                line = edge.get_info()  # devolver o peso
                if line not in edge_line:  # senão estiver no dicionário
                    edge_line[line] = 0  # começar a contagem de arestas
                edge_line[line] += 1
        for line in edge_line:
            # para evitar a contagem duplicada (estação de chegada e saída) dividimos por 2
            edge_line[line] = edge_line[line]//2
        return edge_line

    def mean_weight(self):
        weighted_edges = []  # guardamos as informações numa lista
        for edges in self.graph._iter_edges():
            for edge in edges:  # por casa aresta
                weight = int(edge.get_info())  # vou buscar o seu peso
                weighted_edges.append(weight)  # adicionar à lista
        # soma total a dividir pelo total, e para evitar contar o mesmo peso duas vezes divido por 2
        return sum(weighted_edges)/(len(weighted_edges)) // 2

    def mean_degree(self):
        degree = []  # numa lista é guardado os graus de cada nó
        # em cada nó em _iter_vertex (usamos este porque dá acesso a todos os nós)
        for node in self.graph._iter_vertex():
            # adicionamos a lista o seu grau
            degree.append(self.graph.degree(node))
        # somamos tudo dividindo pelo número total de nós
        mean_degree = sum(degree)/self.n_stations()
        return mean_degree
