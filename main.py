from LondonNetwork import LondonNetwork


def main():
    print("🇬🇧  Bem-vindo à Rede de Metro de Londres\n")

    # Carregar dados
    metro = LondonNetwork()
    metro.stations('stations.csv')
    metro.connections('connections.csv')
    metro.load_stations_info('stations.csv')

    print(
        f"✅  Carregadas {metro.n_stations()} estações e {metro.n_edges()} ligações.\n")

    while True:
        print("--- MENU PRINCIPAL ---")
        print("1. Calcular distância entre estações")
        print("2. Estatísticas da rede")
        print("0. Sair\n")

        opcao = input("Escolhe uma opção: ").strip()

        if opcao == '1':
            print("\n🔍  Calcular distância entre duas estações")
            print("(Exemplo: Baker Street = 11, Oxford Circus = 163)\n")

            id_a = input("ID da estação de partida: ").strip()
            id_b = input("ID da estação de destino:   ").strip()

            if id_a in metro.station_info and id_b in metro.station_info:
                nome_a = metro.station_info[id_a]['name']
                nome_b = metro.station_info[id_b]['name']
                dist = metro.calculate_distance(id_a, id_b)
                print(
                    f"\n📏  Distância entre {nome_a} e {nome_b}: {dist:.2f} km\n")
            else:
                print("\n⚠️   ID não encontrado! Verifica se o ID existe.\n")

        elif opcao == '2':
            print("\n📊  Estatísticas da Rede")
            print(f"   - Número de estações: {metro.n_stations()}")
            print(f"   - Número de ligações:  {metro.n_edges()}")
            print(f"   - Grau médio:          {metro.mean_degree():.2f}")
            print()

        elif opcao == '0':
            print("A sair... 👋")
            break

        else:
            print("Opção inválida! Tenta novamente.\n")


if __name__ == '__main__':
    main()
