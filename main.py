"""
main.py — Ponto de entrada principal do projeto EDA 25/26
Metro de Londres — Algoritmos de Procura
"""

import os
from LondonNetwork import LondonNetworkGraph
from Dijkstra import Dijkstra

# =============================================================================
# Caminhos base
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
VIZ_DIR  = os.path.join(BASE_DIR, 'visualizations')

FILE_STATIONS    = os.path.join(DATA_DIR, 'stations.csv')
FILE_CONNECTIONS = os.path.join(DATA_DIR, 'connections.csv')
FILE_LINES       = os.path.join(DATA_DIR, 'lines.csv')

# =============================================================================
# Simulações predefinidas (enunciado 3.4.1)
# IDs confirmados no stations.csv
# =============================================================================

SIMULACOES = [
    {
        'tipo'    : 'Trajeto Curto (mesma linha)',
        'origem'  : '11',   # Baker Street
        'destino' : '145',  # King's Cross St. Pancras
    },
    {
        'tipo'    : 'Trajeto Longo (linhas diferentes)',
        'origem'  : '35',   # Brixton
        'destino' : '110',  # Hammersmith
    },
    {
        'tipo'    : 'Trajeto com Múltiplos Transbordos',
        'origem'  : '273',  # Victoria
        'destino' : '156',  # Liverpool Street
    },
]

# =============================================================================
# Utilitários de apresentação
# =============================================================================

def separador(titulo):
    """Imprime um separador visual com título."""
    print('\n' + '=' * 60)
    print(f'  {titulo}')
    print('=' * 60)


def escolher_custo():
    """Pede ao utilizador que escolha a função de custo."""
    print('\n  Funções de custo disponíveis:')
    print('    1. Uniforme      (minimiza nº de estações)')
    print('    2. Distância     (minimiza distância geográfica em km)')
    print('    3. Penalização   (distância + penalização por mudança de linha)')
    opcao = input('\n  Escolhe uma opção (1/2/3): ').strip()
    mapa = {'1': 'uniform', '2': 'distance', '3': 'line_penalty'}
    if opcao not in mapa:
        print('  Opção inválida, tenta novamente.')
        return escolher_custo()
    return mapa[opcao]


def escolher_estacao(network, papel='partida'):
    """Pede ao utilizador o ID de uma estação e valida-o."""
    sid = input(f'\n  ID da estação de {papel}: ').strip()
    if sid not in network.station_info:
        print(f'  Estação "{sid}" não encontrada. Tenta novamente.')
        return escolher_estacao(network, papel)
    return sid


def mostrar_resultado(network, path, cost, n_stations, changes, weight_type, use_nx):
    """Apresenta os resultados de uma simulação de forma formatada."""
    impl = 'NetworkX' if use_nx else 'Implementação própria'
    print(f'\n  Implementação  : {impl}')
    print(f'  Função de custo: {weight_type}')
    print(f'  Caminho        : {" → ".join(network.station_info[s]["name"] for s in path)}')
    print(f'  Nº estações    : {n_stations}')
    print(f'  Custo total    : {cost:.4f}')
    print(f'  Mudanças linha : {changes}')

# =============================================================================
# Menus
# =============================================================================

def menu_estatisticas(network):
    """Mostra estatísticas gerais da rede."""
    separador('Estatísticas da Rede')
    print(f'  Nº de estações : {network.n_stations()}')
    print(f'  Nº de ligações : {network.n_edges()}')
    print(f'  Grau médio     : {network.mean_degree():.2f}')
    print(f'  Peso médio             : {network.mean_weight():.2f}')
    print('\n  Ligações por linha:')
    for linha, count in sorted(network.n_edges_line().items()):
        print(f'    Linha {linha:>2} : {count} ligações')


def menu_dijkstra(network):
    """Menu interativo para correr o algoritmo de Dijkstra."""
    dijkstra = Dijkstra(network)

    while True:
        separador('Dijkstra — Menu')
        print('  1. Implementação própria')
        print('  2. Implementação NetworkX')
        print('  3. Comparar ambas as implementações')
        print('  0. Voltar')
        op = input('\n  Opção: ').strip()

        if op == '0':
            break

        elif op in ('1', '2', '3'):
            origem  = escolher_estacao(network, 'partida')
            destino = escolher_estacao(network, 'destino')
            custo   = escolher_custo()

            output = os.path.join(VIZ_DIR, f'caminho_{origem}_{destino}_{custo}.html')

            if op == '1':
                separador('Resultado — Implementação Própria')
                path, cost, n, changes = dijkstra.simulate(
                    origem, destino, weight_type=custo, use_nx=False
                )
                mostrar_resultado(network, path, cost, n, changes, custo, use_nx=False)
                network.visualize_path(path, FILE_LINES, output_file=output)
                print(f'\n  Visualização guardada em: {output}')

            elif op == '2':
                separador('Resultado — NetworkX')
                path, cost, n, changes = dijkstra.simulate(
                    origem, destino, weight_type=custo, use_nx=True
                )
                mostrar_resultado(network, path, cost, n, changes, custo, use_nx=True)
                network.visualize_path(path, FILE_LINES, output_file=output)
                print(f'\n  Visualização guardada em: {output}')

            elif op == '3':
                separador('Comparação — Própria vs NetworkX')
                path_own, cost_own, n_own, ch_own = dijkstra.simulate(
                    origem, destino, weight_type=custo, use_nx=False
                )
                path_nx, cost_nx, n_nx, ch_nx = dijkstra.simulate(
                    origem, destino, weight_type=custo, use_nx=True
                )
                print('\n  [Implementação Própria]')
                mostrar_resultado(network, path_own, cost_own, n_own, ch_own, custo, use_nx=False)
                print('\n  [NetworkX]')
                mostrar_resultado(network, path_nx, cost_nx, n_nx, ch_nx, custo, use_nx=True)
                print(f'\n  Caminhos iguais: {path_own == path_nx}')
                # guarda a visualização do caminho próprio
                network.visualize_path(path_own, FILE_LINES, output_file=output)
                print(f'\n  Visualização guardada em: {output}')
        else:
            print('  Opção inválida.')


def menu_visualizacoes(network):
    """Menu para gerar visualizações do mapa."""
    while True:
        separador('Visualizações — Menu')
        print('  1. Mapa completo da rede')
        print('  0. Voltar')
        op = input('\n  Opção: ').strip()

        if op == '0':
            break
        elif op == '1':
            output = os.path.join(VIZ_DIR, 'london_tube_map.html')
            network.visualize(FILE_LINES, output_file=output)
            print(f'  Mapa guardado em: {output}')
        else:
            print('  Opção inválida.')


# =============================================================================
# Simulações automáticas (enunciado 3.4.1)
# =============================================================================

def simulacoes_automaticas(network):
    """
    Corre todas as simulações predefinidas para os três tipos de trajeto,
    com todas as funções de custo, usando ambas as implementações.
    Guarda as visualizações em /visualizations.
    """
    separador('Simulações Automáticas — Fase 2')
    dijkstra = Dijkstra(network)

    custos = ['uniform', 'distance', 'line_penalty']

    for sim in SIMULACOES:
        origem  = sim['origem']
        destino = sim['destino']
        nome_o  = network.station_info[origem]['name']
        nome_d  = network.station_info[destino]['name']

        print(f'\n{"─" * 60}')
        print(f'  {sim["tipo"]}')
        print(f'  {nome_o} ({origem})  →  {nome_d} ({destino})')
        print(f'{"─" * 60}')

        for custo in custos:
            print(f'\n  Custo: {custo}')

            # implementação própria
            path_own, cost_own, n_own, ch_own = dijkstra.simulate(
                origem, destino, weight_type=custo, use_nx=False
            )
            mostrar_resultado(network, path_own, cost_own, n_own, ch_own, custo, use_nx=False)

            # networkx
            path_nx, cost_nx, n_nx, ch_nx = dijkstra.simulate(
                origem, destino, weight_type=custo, use_nx=True
            )
            mostrar_resultado(network, path_nx, cost_nx, n_nx, ch_nx, custo, use_nx=True)

            print(f'  Caminhos iguais: {path_own == path_nx}')

            # guarda visualização do caminho próprio
            output = os.path.join(VIZ_DIR, f'sim_{origem}_{destino}_{custo}.html')
            network.visualize_path(path_own, FILE_LINES, output_file=output)
            print(f'  Visualização: {output}')


# =============================================================================
# Menu principal
# =============================================================================

def menu_principal(network):
    """Loop principal do programa."""
    while True:
        separador('MENU PRINCIPAL — Metro de Londres')
        print('  1. Estatísticas da rede')
        print('  2. Algoritmo de Dijkstra')
        print('  3. Visualizar mapa completo')
        print('  4. Correr todas as simulações automáticas')
        print('  0. Sair')
        op = input('\n  Opção: ').strip()

        if op == '0':
            print('\n  Até logo!\n')
            break
        elif op == '1':
            menu_estatisticas(network)
        elif op == '2':
            menu_dijkstra(network)
        elif op == '3':
            menu_visualizacoes(network)
        elif op == '4':
            simulacoes_automaticas(network)
        else:
            print('  Opção inválida.')


# =============================================================================
# Ponto de entrada
# =============================================================================

if __name__ == '__main__':
    print('\nBem-vindo à Rede de Metro de Londres\n')

    # carrega a rede
    network = LondonNetworkGraph()
    network.stations(FILE_STATIONS)
    network.connections(FILE_CONNECTIONS)

    print(f'  Carregadas {network.n_stations()} estações e {network.n_edges()} ligações.')

    menu_principal(network)