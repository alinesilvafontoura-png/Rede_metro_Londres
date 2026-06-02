

class ReadData:
    def __init__(self, graph, station_info):
        self.graph = graph              # grafo partilhado com LondonNetworkGraph
        self.station_info = station_info  # dicionário partilhado com LondonNetworkGraph

    def stations(self, file_stations):
        with open(file_stations, 'r') as file:
            next(file)  # salta o cabeçalho
            for line in file:
                data = line.strip().split(',')
                station_id = data[0]
                latitude = float(data[1])
                longitude = float(data[2])
                name = data[3]
                # adiciona o vértice ao grafo com as suas coordenadas e nome
                self.graph.add_vertex(station_id, payload={
                                      'lat': latitude, 'lon': longitude, 'name': name})
                # guarda as informações da estação no dicionário
                self.station_info[station_id] = {
                    'name': name, 'lat': latitude, 'lon': longitude}

    def connections(self, file_connections):
        with open(file_connections, 'r') as file:
            next(file)  # salta o cabeçalho
            for row in file:
                data = row.strip().split(',')
                station1 = data[0]
                station2 = data[1]
                line_id = int(data[2])
                # adiciona a aresta entre as duas estações com o id da linha como peso
                self.graph.add_edge(station1, station2, weight=line_id)

    def lines(self, file_lines):
        lines = {}
        with open(file_lines, 'r') as file:
            next(file)  # salta o cabeçalho
            for row in file:
                data = row.strip().split(',')
                line_id = int(data[0])
                name = data[1]
                lines[line_id] = name  # mapeia id da linha para o seu nome
        return lines
