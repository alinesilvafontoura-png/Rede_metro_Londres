from Graph import Graph


class LondonNetwork:
    def __init__(self):
        self.graph=Graph()


    def stations (self, file_stations):
        with open(file_stations,'r') as file:
            for line in file:                                           #por cada linha do ficheiro
                data = line.strip().split(',')                          #escreve uma informação por linha
                station_id = data[0]
                latitude = float(data[1])
                longitude = float(data[2])
                name = data[3]

                self.graph.add_vertex(station_id, payload={'lat':latitude,'lon': longitude,'name':name}) #no grafo é adicionado um nó que guarda estas informações

    def connections (self, file_connections):
        with open(file_connections, 'r') as file:
            next(file)                                                  # salta o cabeçalho
            for row in file:
                data = row.strip().split(',')
                line_id = int(data[0])
                station1 = data[1]
                station2 = data[2]

                self.graph.add_edge(station1, station2, weight=line_id)  #no grafo é adicionado uma aresta que segue estas orientações


    def lines (self, file_lines):
        lines={}
        with open(file_lines, 'r') as file:
            next(file)
            for row in file:
                data = row.strip().split(',')
                line_id = int(data[0])
                name = data[1]
                lines[line_id] = name
        return lines

#utilização dos métodos provenientes de Graph
    def n_stations(self):
        return self.graph.vertex_count()

    def n_edges(self):
        return self.graph.edge_count()

    def n_edge_line(self):
        edge_line={}                                #criar um dicionário
        for edges in self.graph._iter_edges():      #edges= lista de arestas de um vértie
            for edge in edges:                      #edge= uma aresta individual
                line=edge.get_info()                #devolver o peso
                if line not in edge_line:           #senão estiver no dicionário
                    edge_line[line]=0               #começar a contagem de arestas
                edge_line[line]+=1
        for line in edge_line:
            edge_line[line]=edge_line[line]//2      #para evitar a contagem duplicada (estação de chegada e saída) dividimos por 2
        return edge_line

    def mean_weight(self):
        weighted_edges=[]                        #guardamos as informações numa lista
        for edges in self.graph._iter_edges():
            for edge in edges:                   #por casa aresta
                weight=int(edge.get_info())      #vou buscar o seu peso
                weighted_edges.append(weight)    #adicionar à lista
        return sum(weighted_edges)/(len(weighted_edges)) //2  #soma total a dividir pelo total, e para evitar contar o mesmo peso duas vezes divido por 2


    def mean_degree(self):
        degree=[]                                   #numa lista é guardado os graus de cada nó
        for node in self.graph._iter_vertex():      #em cada nó em _iter_vertex (usamos este porque dá acesso a todos os nós)
            degree.append(self.graph.degree(node))  #adicionamos a lista o seu grau
        mean_degree=sum(degree)/self.n_stations()   #somamos tudo dividindo pelo número total de nós
        return mean_degree



