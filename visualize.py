import folium


class Visualize:
    def __init__(self, graph, station_info):
        self.graph = graph                  # grafo partilhado com LondonNetwork
        self.station_info = station_info    # dicionário partilhado com LondonNetwork

    def visualize(self, file_lines, output_file='visualizations/london_tube_map.html'):
        # carregar cores e nomes das linhas
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

        mapa = folium.Map(location=[51.5074, -0.1278],
                          zoom_start=11, tiles='CartoDB positron')

        arestas_vistas = set()
        for edges_list in self.graph._iter_edges():
            for edge in edges_list:
                start, end = edge.get_vs()
                line_id = int(edge.get_info())
                edge_key = (min(start, end), max(start, end), line_id)
                if edge_key in arestas_vistas:
                    continue
                arestas_vistas.add(edge_key)
                if start not in self.station_info or end not in self.station_info:
                    continue
                coord_start = [self.station_info[start]
                               ['lat'], self.station_info[start]['lon']]
                coord_end = [self.station_info[end]
                             ['lat'], self.station_info[end]['lon']]
                colour = lines_info.get(line_id, {}).get('colour', '#888888')
                line_name = lines_info.get(line_id, {}).get(
                    'name', f'Line {line_id}')
                folium.PolyLine(locations=[coord_start, coord_end], color=colour,
                                weight=3, opacity=0.8, tooltip=line_name).add_to(mapa)

        for sid, info in self.station_info.items():
            folium.CircleMarker(location=[info['lat'], info['lon']], radius=4,
                                color='white', fill=True, fill_color='#333333',
                                fill_opacity=0.9, weight=1.5,
                                tooltip=folium.Tooltip(info['name'], sticky=False)).add_to(mapa)

        legend_html = """<div style="position:fixed; bottom:30px; left:30px;
            background-color:white; border:1px solid #ccc; border-radius:8px;
            padding:12px 16px; font-family:Arial,sans-serif; font-size:12px;
            z-index:1000; box-shadow:2px 2px 6px rgba(0,0,0,0.2);
            max-height:300px; overflow-y:auto;">
            <b style="font-size:13px;">London Underground</b><br><br>"""
        for lid, info in sorted(lines_info.items()):
            legend_html += f"""<div style="margin-bottom:5px;">
                <span style="display:inline-block; width:20px; height:10px;
                background-color:{info['colour']}; border-radius:3px;
                margin-right:6px; vertical-align:middle;"></span>{info['name']}</div>"""
        legend_html += "</div>"
        folium.Element(legend_html).add_to(mapa)

        if output_file:
            mapa.save(output_file)
            print(f"Mapa guardado em: {output_file}")
        return mapa

    def visualize_path(self, path, file_lines, output_file='visualizations/simulation.html'):
        # mapa base sem guardar
        mapa = self.visualize(file_lines, output_file=None)

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            coord_u = [self.station_info[u]['lat'],
                       self.station_info[u]['lon']]
            coord_v = [self.station_info[v]['lat'],
                       self.station_info[v]['lon']]
            folium.PolyLine(locations=[coord_u, coord_v], color='yellow',
                            weight=6, opacity=1, tooltip="Caminho ótimo").add_to(mapa)

        origem = self.station_info[path[0]]
        folium.Marker(location=[origem['lat'], origem['lon']],
                      popup=f"Origem: {origem['name']}",
                      icon=folium.Icon(color='green')).add_to(mapa)

        destino = self.station_info[path[-1]]
        folium.Marker(location=[destino['lat'], destino['lon']],
                      popup=f"Destino: {destino['name']}",
                      icon=folium.Icon(color='red')).add_to(mapa)

        if output_file:
            mapa.save(output_file)
            print(f"Caminho guardado em: {output_file}")
        return mapa

    def visualize_mst(self, mst_edges, file_lines, output_file='visualizations/kruskal_mst.html'):
        """Visualiza a MST sobreposta à rede original.
        As arestas da MST ficam verdes e mais espessas.
        As arestas da rede original mantêm as cores das linhas.
        """
        # Desenha a rede original primeiro (com as cores das linhas)
        mapa = self.visualize(file_lines, output_file=None)

        # Desenhar arestas da MST por cima (verde e mais espessas)
        for u, v, edge, cost in mst_edges:
            if u not in self.station_info or v not in self.station_info:
                continue
            coord_u = [self.station_info[u]['lat'],
                       self.station_info[u]['lon']]
            coord_v = [self.station_info[v]['lat'],
                       self.station_info[v]['lon']]
            folium.PolyLine(
                locations=[coord_u, coord_v],
                color='#00FF00',     # verde brilhante para a MST
                weight=5,            # mais espesso que a rede original
                opacity=1,
                tooltip=f"MST: {self.station_info[u]['name']} → {self.station_info[v]['name']}"
            ).add_to(mapa)

        # Legenda para distinguir MST da rede original
        legend_html = """<div style="position:fixed; top:30px; right:30px;
            background-color:white; border:2px solid #00CC00; border-radius:8px;
            padding:12px 16px; font-family:Arial,sans-serif; font-size:13px;
            z-index:1000; box-shadow:2px 2px 6px rgba(0,0,0,0.3);">
            <b>🌲 Árvore Geradora Mínima (Kruskal)</b><br>
            <span style="display:inline-block; width:30px; height:5px;
            background-color:#00FF00; vertical-align:middle; margin-right:6px;
            border-radius:2px;"></span>Arestas MST<br>
            <span style="display:inline-block; width:30px; height:3px;
            background-color:#888888; vertical-align:middle; margin-right:6px;
            border-radius:2px;"></span>Rede original</div>"""
        folium.Element(legend_html).add_to(mapa)

        if output_file:
            mapa.save(output_file)
            print(f"MST guardada em: {output_file}")
        return mapa
