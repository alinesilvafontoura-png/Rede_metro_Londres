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
                self.station_info[station_id] = {
                    'name': name, 'lat': latitude, 'lon': longitude}

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

    def n_edges_line(self):
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

        def mean_weight(self, weight='uniform'):
        weighted_edges = []
        seen = set()  # set é mais eficiente que lista para verificar duplicados

        for edges in self.graph._iter_edges():
            for edge in edges:
                u, v = edge.get_vs()
                edge_id = frozenset([u, v])  # identifica a aresta pelos vértices, não pela linha
                if edge_id in seen:
                    continue
                seen.add(edge_id)
                if weight == 'uniform':  # weight aqui é o PARÂMETRO (não sobrescrito)
                    w = 1
                elif weight == 'distance':
                    w = self.calculate_distance(u, v)
                else:
                     w = int(edge.get_info())

                weighted_edges.append(w)  # append de w, não de weight

        if not weighted_edges:  # FORA do loop
            return 0

        return sum(weighted_edges) / len(weighted_edges)  # FORA do loop

    def mean_degree(self):
        degree = []  # numa lista é guardado os graus de cada nó
        # em cada nó em _iter_vertex (usamos este porque dá acesso a todos os nós)
        for node in self.graph._iter_vertex():
            # adicionamos a lista o seu grau
            degree.append(self.graph.degree(node))
        # somamos tudo dividindo pelo número total de nós
        mean_degree = sum(degree)/self.n_stations()
        return mean_degree

        def visualize(self, file_lines, output_file='london_tube_map.html'):
        # 1. Carregar cores e nomes das linhas
        lines_info = {}
        with open(file_lines, 'r') as f:
            next(f)
            for row in f:
                row = row.strip()
                if not row:
                    continue
                data = row.split(',')
                line_id = int(data[0].strip('"'))
                name = data[1].strip('"')
                colour = '#' + data[2].strip().strip('"')
                lines_info[line_id] = {'name': name, 'colour': colour}

        # 2. Criar mapa centrado em Londres
        mapa = folium.Map(
            location=[51.5074, -0.1278],
            zoom_start=11,
            tiles='CartoDB positron'
        )

        # 3. Desenhar ligações entre estações
        arestas_vistas = set()

        for edges_list in self.graph._iter_edges():  # lista de arestas de cada vértice
            for edge in edges_list:
                start, end = edge.get_vs()  # (chave_origem, chave_destino)
                line_id = int(edge.get_info())  # peso = id da linha

                # Evitar desenhar a mesma aresta duas vezes
                edge_key = (min(start, end), max(start, end), line_id)
                if edge_key in arestas_vistas:
                    continue
                arestas_vistas.add(edge_key)

                # Saltar se faltar informação de alguma estação
                if start not in self.station_info or end not in self.station_info:
                    continue

                coord_start = [self.station_info[start]['lat'],
                               self.station_info[start]['lon']]
                coord_end = [self.station_info[end]['lat'],
                             self.station_info[end]['lon']]

                colour = lines_info.get(line_id, {}).get('colour', '#888888')
                line_name = lines_info.get(line_id, {}).get('name', f'Line {line_id}')

                folium.PolyLine(
                    locations=[coord_start, coord_end],
                    color=colour,
                    weight=3,
                    opacity=0.8,
                    tooltip=line_name
                ).add_to(mapa)

                # 4. Marcadores das estações
                # 4. Marcadores das estações
                for sid, info in self.station_info.items():
                    folium.CircleMarker(
                        location=[info['lat'], info['lon']],
                        radius=4,
                        color='white',
                        fill=True,
                        fill_color='#333333',
                        fill_opacity=0.9,
                        weight=1.5,
                        tooltip=folium.Tooltip(info['name'], sticky=False)
                    ).add_to(mapa)

                # 5. Legenda
                legend_html = """
                        <div style="
                            position: fixed; bottom: 30px; left: 30px;
                            background-color: white; border: 1px solid #ccc;
                            border-radius: 8px; padding: 12px 16px;
                            font-family: Arial, sans-serif; font-size: 12px;
                            z-index: 1000; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
                            max-height: 300px; overflow-y: auto;
                        ">
                        <b style="font-size:13px;">London Underground</b><br><br>
                        """
                for lid, info in sorted(lines_info.items()):
                    legend_html += f"""
                            <div style="margin-bottom:5px;">
                                <span style="display:inline-block; width:20px; height:10px;
                                    background-color:{info['colour']}; border-radius:3px;
                                    margin-right:6px; vertical-align:middle;"></span>
                                {info['name']}
                            </div>
                            """
                legend_html += "</div>"
                mapa.get_root().html.add_child(folium.Element(legend_html))

                # 6. Guardar
                mapa.save(output_file)
                print(f"Mapa guardado em: {output_file}")
                return mapa


