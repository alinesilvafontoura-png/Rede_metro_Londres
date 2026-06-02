# Metro de Londres – Algoritmos de Procura

**Trabalho 2 EDA 25/26**

---

## Organização dos ficheiros

```
.
├── README.md                    # Este ficheiro
│
├── main.py                      # Fase 1: carrega a rede e apresenta estatísticas + mapa
├── Dijkstra.py                  # Fase 2: implementação própria e NetworkX do Dijkstra
├── Kruskal.py                   # Fase 3: algoritmo de Kruskal (MST) + UnionFind
│
├── LondonNetwork.py             # Classe LondonNetworkGraph (Fase 1)
├── Graph.py                     # TAD Grafo fornecido (Vertex, Edge, Graph)
├── read_data.py                 # ReadData: leitura dos CSVs
├── visualize.py                 # Visualize: mapas interativos com Folium
├── requirements.txt             # Dependências do projeto
│
├── data/
│   ├── stations.csv              # 308 estações (id, latitude, longitude, nome)
│   ├── connections.csv           # ligações (station1, station2, line)
│   └── lines.csv                 # 13 linhas de metro (id, nome, cor)
│
└── visualizations/
    ├── london_tube_map.html      # Mapa completo da rede
    ├── simulation.html           # Caminho ótimo do Dijkstra
    ├── kruskal_uniform.html      # MST com custo uniforme
    ├── kruskal_distance.html     # MST com custo geográfico
    └── kruskal_line_penalty.html # MST com custo geo + penalização
```

---

## Dependências

```bash
pip install -r requirements.txt
```

O ficheiro `requirements.txt` inclui `folium` e `networkx`.

> **Nota:** `folium` é necessário para os mapas HTML interativos. Se não estiver instalado,
> os cálculos funcionam na mesma, mas a visualização não será gerada.

---

## Como executar

### Fase 1 – Modelação e Visualização da Rede

```bash
python main.py
```

Apresenta no terminal:

- Número de estações e ligações
- Grau médio das estações
- Peso médio das arestas
- Ligações por linha de metro

Gera o ficheiro `visualizations/london_tube_map.html` — abrir no browser para ver o mapa
interativo com todas as linhas nas suas cores oficiais.

---

### Fase 2 – Algoritmo de Dijkstra

```bash
python Dijkstra.py
```

Executa automaticamente três simulações e compara as três funções de custo:

1. **Uniforme** – minimiza número de estações
2. **Geográfico (Haversine)** – minimiza distância em km
3. **Geo + Penalização de transbordo** – equilibra distância e número de mudanças de linha

Gera `visualizations/simulation.html` com o caminho ótimo destacado a amarelo.

#### Usar o Dijkstra no próprio código

```python
from LondonNetwork import LondonNetworkGraph
from Dijkstra import Dijkstra

net = LondonNetworkGraph()
net.stations('data/stations.csv')
net.connections('data/connections.csv')

dijkstra = Dijkstra(net)

# Implementação própria com custo geográfico
path, cost = dijkstra.dijkstra('11', '273', weight_type='distance')

# NetworkX (sem suporte a line_penalty)
path_nx, cost_nx = dijkstra.dijkstra_nx('11', '273', weight_type='distance')

# Simulação completa com visualização
dijkstra.simulate('11', '273', weight_type='distance')
```

---

### Fase 3 – Algoritmo de Kruskal (MST)

```bash
python Kruskal.py
```

Calcula a Árvore Geradora Mínima (MST) para as três funções de custo e apresenta:

- Número de arestas da rede original vs MST
- Custo total da rede original vs MST
- Poupança
- Linhas utilizadas e mudanças de linha

Gera ficheiros HTML onde arestas da MST aparecem verdes e mais espessas sobre a rede original.

#### Usar o Kruskal no próprio código

```python
from LondonNetwork import LondonNetworkGraph
from Kruskal import Kruskal

net = LondonNetworkGraph()
net.stations('data/stations.csv')
net.connections('data/connections.csv')

kruskal = Kruskal(net)

# Calcular MST com custo geográfico
mst_edges, total_cost = kruskal.kruskal(weight_type='distance')

# Simulação completa com visualização
kruskal.simulate(
    weight_type='distance',
    file_lines='data/lines.csv',
    output_file='visualizations/kruskal_distance.html'
)
```

---

## Classe `LondonNetworkGraph` – Métodos principais

| Método                                              | Descrição                                                 |
| --------------------------------------------------- | --------------------------------------------------------- |
| `stations(file)`                                    | Carrega estações do CSV                                   |
| `connections(file)`                                 | Carrega ligações do CSV                                   |
| `lines(file)`                                       | Carrega informação das linhas do CSV                      |
| `calculate_distance(id1, id2)`                      | Distância geográfica (Haversine) entre duas estações (km) |
| `n_stations()`                                      | Número total de estações                                  |
| `n_edges()`                                         | Número total de ligações                                  |
| `n_edges_line()`                                    | Dicionário com o número de ligações por linha             |
| `mean_weight(weight_type)` | Peso médio das arestas conforme a função de custo |
| `mean_degree()`                                     | Grau médio das estações                                   |
| `visualize(file_lines, output_file)`                | Gera mapa HTML da rede completa                           |
| `visualize_path(path, file_lines, output_file)`     | Gera mapa com caminho destacado                           |
| `visualize_mst(mst_edges, file_lines, output_file)` | Gera mapa com a MST sobreposta                            |

---

## Funções de custo disponíveis

Parâmetro `weight_type`, disponível em Dijkstra e Kruskal:

| Valor            | Descrição                                                |
| ---------------- | -------------------------------------------------------- |
| `'uniform'`      | Peso 1 por aresta – minimiza nº de estações              |
| `'distance'`     | Distância Haversine (km) – minimiza distância geográfica |
| `'line_penalty'` | Geo + penalização α=5 km por transbordo                  |

---

## Arquitetura do código

```
LondonNetworkGraph          usa internamente →   Graph (TAD fornecido)
        │
        ├── Dijkstra            (heap binário, implementação própria + NetworkX)
        ├── Kruskal             (implementação própria + UnionFind)
        ├── ReadData            (leitura dos CSVs)
        └── Visualize           (mapas Folium interativos)
```

Todo o código segue as diretrizes **PEP 8** e está documentado com comentários em português.
