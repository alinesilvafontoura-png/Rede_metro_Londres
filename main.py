import os
from LondonNetwork import LondonNetworkGraph


def main():
    print("Bem-vindo à Rede de Metro de Londres\n")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta do projeto

    metro = LondonNetworkGraph()
    metro.stations(os.path.join(BASE_DIR, 'data', 'stations.csv'))
    metro.connections(os.path.join(BASE_DIR, 'data', 'connections.csv'))
    print(
        f"Carregadas {metro.n_stations()} estações e {metro.n_edges()} ligações.\n")

    while True:
        print("--- MENU PRINCIPAL ---")
        print("1. Calcular distância entre estações")
        print("2. Estatísticas da rede")
        print("3. Visualizar mapa")
        print("0. Sair\n")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == '1':
            print("\nCalcular distância entre duas estações")
            id_a = input("ID da estação de partida: ").strip()
            id_b = input("ID da estação de destino: ").strip()
            if id_a in metro.station_info and id_b in metro.station_info:
                nome_a = metro.station_info[id_a]['name']
                nome_b = metro.station_info[id_b]['name']
                dist = metro.calculate_distance(id_a, id_b)
                print(
                    f"\nDistância entre {nome_a} e {nome_b}: {dist:.2f} km\n")
            else:
                print("\nID não encontrado!\n")

        elif opcao == '2':
            print("\nEstatísticas da Rede")
            print(f"  - Número de estações:    {metro.n_stations()}")
            print(f"  - Número de ligações:    {metro.n_edges()}")
            print(f"  - Grau médio:            {metro.mean_degree():.2f}")
            print(f"  - Peso médio:            {metro.mean_weight():.2f}\n")

        elif opcao == '3':
            print("\nA gerar mapa...")
            metro.visualize(
                os.path.join(BASE_DIR, 'data', 'lines.csv'),
                output_file=os.path.join(
                    BASE_DIR, 'visualizations', 'london_tube_map.html')
            )
            print("Abre o ficheiro 'visualizations/london_tube_map.html' no browser!\n")

        elif opcao == '0':
            print("A sair...")
            break

        else:
            print("Opção inválida! Tenta novamente.\n")


if __name__ == '__main__':
    main()
