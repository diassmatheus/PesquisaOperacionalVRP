import random
import copy
import os
import time


def le_arquivo(nome_arq):
    with open(nome_arq, 'r', encoding='UTF-8') as f:
        linhas = f.readlines()
        tamanhos = linhas[1].strip().split(';')
        qtd_pontos = int(tamanhos[0])
        qtd_caminhoes = int(tamanhos[1])
        del linhas[:3]
        caminhoes = list()
        for i in range(qtd_caminhoes):
            v_linha = linhas[i].strip().split(';')
            capacidade = int(v_linha[1])
            custo_var = float(v_linha[2])
            custo_fix = int(v_linha[3])
            caminhoes.append([i, capacidade, custo_var, custo_fix])
        del linhas[:qtd_caminhoes + 1]
        coordenadas = list()
        for i in range(qtd_pontos + 1):
            v_linha = linhas[i].strip().split(';')
            coord_x = int(v_linha[1])
            coord_y = int(v_linha[2])
            demanda = int(v_linha[3])
            coordenadas.append([i, coord_x, coord_y, demanda])
        del linhas[:qtd_pontos + 2]
        mat_dist = list()
        for i in range(qtd_pontos + 1):
            v_linha = linhas[i].strip().split(';')
            mat_dist.append(v_linha)

    return caminhoes, coordenadas, mat_dist


def gera_solucao_inicial(caminhoes, coordenadas, mat_dist):
    i = 0
    qtd_caminhoes = len(caminhoes)
    aleatorio_caminhoes = list()
    aleatorio_pontos = list()
    score_relativo = list()
    lista_id = list()
    selecao_cam = list()
    soma_score = 0
    for i in range(qtd_caminhoes):
        id_cam = caminhoes[i][0]
        capac = caminhoes[i][1]
        custo_var = caminhoes[i][2]
        custo_fix = caminhoes[i][3]
        score = (capac / custo_var) ** 5
        aleatorio_caminhoes.append([id_cam, capac, custo_var, custo_fix, score])
        lista_id.append(id_cam)
        i += 1
        soma_score += score

    for id,itens in enumerate(aleatorio_caminhoes):
        relativo = aleatorio_caminhoes[id][-1]/soma_score
        score_relativo.append(relativo)
    # print(f'Score Relativo caminhões: {score_relativo}')

    while lista_id:
        escolhido = random.choices(list(zip(lista_id, score_relativo)), k=1)
        cam_escolhido, id_score = escolhido[0]
        selecao_cam.append(cam_escolhido)
        indice = lista_id.index(cam_escolhido)
        del lista_id[indice]
        del score_relativo[indice]
    # print(f"Seleção dos caminhões (id's): {selecao_cam}")
    selecao_cam_infos = list()
    for caminhao_selecionado in selecao_cam:
        for caminhao_info_original in caminhoes:
            if caminhao_info_original[0] == caminhao_selecionado:
                selecao_cam_infos.append(caminhao_info_original)
                break
    # print(f"Seleçao dos caminhões (todas as infos): {selecao_cam_infos}")


    qtd_pontos = len(mat_dist)
    for i in range(len(mat_dist)):
        for j in range(len(mat_dist[i])):
            mat_dist[i][j] = int(mat_dist[i][j])
    mat_prob = list()
    for linha in mat_dist:
        linha_prob = list()
        linha_prob_aux = list()
        maior_valor = max(linha)
        for ponto in linha:
            if ponto == 0:
                ponto_prob = 0
            else:
                ponto_prob = (maior_valor - ponto) ** 5
            linha_prob_aux.append(ponto_prob)
        soma_linha = sum(linha_prob_aux)
        for ponto_prob in linha_prob_aux:
            ponto_prob2 = ponto_prob / soma_linha if soma_linha > 0 else 0
            linha_prob.append(ponto_prob2)
        mat_prob.append(linha_prob)
    # print(f"Matriz de probabilidades dos pontos: {mat_prob}")

    pontos_nao_visitados = list(set(range(1, qtd_pontos))) # Começando em 1 para excluir o depósito
    rotas = list()
    mat_prob_edit = copy.deepcopy(mat_prob)
    for linha in mat_prob_edit:
        linha[0] *= 0
    for caminhao in selecao_cam_infos:
        rota_atual = list()
        ponto_atual = 0
        capac_restante = caminhao[1]
        while capac_restante > 0 and len(pontos_nao_visitados) > 0:
            proximo_ponto = random.choices(range(qtd_pontos), weights=[max(x, 0.000000000000000000001) for x in mat_prob_edit[ponto_atual]])[0]
            # print(f'Próximo ponto sorteado: {proximo_ponto}')
            # print(f'Demanda do ponto:{coordenadas[proximo_ponto][3]}')
            if coordenadas[proximo_ponto][3] <= capac_restante:
                rota_atual.append(proximo_ponto)
                # print("Ponto aceito")
                # pontos_nao_visitados.remove(proximo_ponto)
                if proximo_ponto in pontos_nao_visitados:
                    pontos_nao_visitados.remove(proximo_ponto)
                for linha in mat_prob_edit:
                    linha[proximo_ponto] *= 0
                # print(f"Pontos não visitados: {pontos_nao_visitados}")
                # print(f"Vetor de probabilidades: {mat_prob_edit[proximo_ponto]}")
                capac_restante -= coordenadas[proximo_ponto][3]
                ponto_atual = proximo_ponto
            else:
                # print("Ponto recusado")
                break
        if len(rota_atual) != 0:
            rotas.append(rota_atual)
    # print(f'Selecao_cam_infos{selecao_cam_infos}')
    # print(rotas)
    return selecao_cam_infos, rotas, selecao_cam


def calcula_custo(selecao_cam_infos, rotas, mat_dist):
    # mat_dist está incluso o deposito
    pontos = list()
    custo = list()

    for id, ponto in enumerate(selecao_cam_infos):
        custo.append(selecao_cam_infos[id][2:])
    # print(custo)

    for id,rota in enumerate(rotas):
        pontos.append(rotas[id][:])
    # print(pontos)

    for _ in range(len(pontos)):
        pontos[_].insert(0, 0)
        pontos[_].append(0)
    dist_total = list()
    # print(pontos)
    for rota in pontos:
        distancia_rota = list()
        for i in range(len(rota) - 1):
            anterior = rota[i]
            proximo = rota[i + 1]
            distancia = int(mat_dist[anterior][proximo])
            distancia_rota.append(distancia)
        dist_total.append(distancia_rota)
    # print(dist_total)

    soma_dist = list()
    for distancias in dist_total:
        soma = sum(distancias)
        if soma > 0:
            soma_dist.append(soma)
    # print(soma_dist)

    resultados = list()
    for soma, valores in zip(soma_dist, custo):
        multiplicador = valores[0]
        resultado = soma * multiplicador
        resultados.append(resultado)

    # print(resultados)

    resultado_rota = list()
    for soma, valores in zip(resultados, custo):
        usado = valores[1]
        resultado = soma + usado
        resultado_rota.append(resultado)

    valor_total = round(sum(resultado_rota), 2)
    # print(resultado_rota)
    # print(valor_total)

    pontos_rota = list()
    for i, rota in enumerate(pontos):
        pontos_rota.append(rota[1:-1])

    # print(pontos_rota)
    id_caminhoes = list()
    for idx, valores in enumerate(selecao_cam_infos):
        id_caminhoes.append(valores[0])

    # print(id_caminhoes)

    return valor_total, id_caminhoes, pontos_rota

def gera_inicial_n_vezes(caminhoes, coordenadas, mat_dist, qtd_tentativas):

    melhor_solucao = None
    melhor_valor = float('inf')
    id_cam1 = None
    relatorio_sol_ini = list()

    for i in range(qtd_tentativas):
        selecao_cam_infos, rotas, selecao_cam = gera_solucao_inicial(caminhoes, coordenadas, mat_dist)
        # print(selecao_cam_infos)
        valor_candidato, id_caminhoes, rota = calcula_custo(selecao_cam_infos, rotas, mat_dist)
        relatorio_sol_ini.append(i + 1)
        relatorio_sol_ini.append(valor_candidato)
        # Verifica se é uma solução melhor
        if valor_candidato < melhor_valor:
            melhor_solucao = rotas
            melhor_valor = valor_candidato
            id_cam1 = id_caminhoes
        relatorio_sol_ini.append(melhor_valor)
    # print(f'{valor_candidato}')
    # print(f'Relatório:{relatorio}')
    # print(f'Melhor valor da solução inicial com n iterações:{melhor_valor}')
    # print(f'Melhor solução inicial com n iterações:{melhor_solucao}')
    # print(f'ID dos caminhões na ordem selecionada:{id_cam}')
    # Retorna a solução gerada
    return melhor_solucao, melhor_valor, id_cam1, relatorio_sol_ini



# Realiza a troca de dois pontos em uma solução
def troca_pontos_intra(solucao, p1, p2):
    copia_solucao = solucao[:]
    copia_solucao[p1] = solucao[p2]
    copia_solucao[p2] = solucao[p1]
    return copia_solucao


def gera_vizinhanca_intra_rotas(melhor_solucao, melhor_valor, id_cam, caminhoes, mat_dist):
    for rotas in melhor_solucao:
        # Quantidade de pontos na solução
        qtd_pontos = len(rotas)
        # Armazena o melhor vizinho e o seu valor
        melhor_vizinho = rotas
        melhor_vizinho_valor = melhor_valor
        contador = 0
        # Gera todos os vizinhos
        for p1 in range(qtd_pontos - 1):
            for p2 in range(p1 + 1, qtd_pontos):
                # Gera o vizinho realizando a troca dos pontos
                sol_vizinha = troca_pontos_intra(rotas, p1, p2)
                # Reconstroi a solução total com o novo vizinho
                nova_solucao = copy.deepcopy(melhor_solucao)
                nova_solucao[contador] = sol_vizinha
                # Traz as informações dos caminhões na ordem especificada para calculo do custo
                id_cam_info = list()
                for i in id_cam:
                    id_cam_aux = list()
                    id_cam_aux.append(caminhoes[i][0])
                    id_cam_aux.append(caminhoes[i][1])
                    id_cam_aux.append(caminhoes[i][2])
                    id_cam_aux.append(caminhoes[i][3])
                    id_cam_info.append(id_cam_aux)
                #print(id_cam_info)
                # Avalia o vizinho')
                sol_vizinha_valor, x, y = calcula_custo(id_cam_info, nova_solucao, mat_dist)
                # Verifica se o novo vizinho é o melhor vizinho
                if sol_vizinha_valor < melhor_vizinho_valor:
                    melhor_vizinho = nova_solucao
                    melhor_vizinho_valor = sol_vizinha_valor
                #print(id_cam_info)
        contador += 1
        # Retorna o melhor vizinho encontrado
        # print(f'Nova solução encontrada:{melhor_vizinho}')
        # print(f'Valor da nova solução:{melhor_vizinho_valor}')
        return melhor_vizinho, melhor_vizinho_valor


# Executa uma iteração do Hill-Climbing (gera vizinhança até parar de melhorar)
def iteracao_hill_climbing_intra_rota(melhor_solucao, melhor_valor, id_cam, caminhoes, mat_dist):
    # Quantidade de pontos do problema
    qtd_pontos = len(mat_dist)
    # Gera a solução inicial da iteração
    sol_candidata = melhor_solucao
    sol_candidata_valor = melhor_valor
    # Variável que indica se chegamos no ótimo local
    otimo_local = False
    # Gera vizinhança até chegar no ótimo local
    while not otimo_local:
        # Encontra o melhor vizinho da solução candidata
        melhor_vizinho, melhor_vizinho_valor = gera_vizinhanca_intra_rotas(melhor_solucao, melhor_valor, id_cam, caminhoes, mat_dist)
        # Testa se o melhor vizinho é melhor que a solução candidata
        if melhor_vizinho_valor < sol_candidata_valor:
            # Se entrar aqui, não é ótimo local (teve melhoria)
            sol_candidata = melhor_vizinho
            sol_candidata_valor = melhor_vizinho_valor
        else:
            # Se entrar aqui, então chegou no ótimo local
            otimo_local = True
    # Retorna a solução da iteração
    # print(f'{sol_candidata}')
    # print(f'{sol_candidata_valor}')
    # print()
    return sol_candidata, sol_candidata_valor

# Roda todas as iterações do Hill-climbing
def solver_hill_climbing(caminhoes, coordenadas, mat_dist, qtd_iteracoes):
    relatorio_hill_climbing = list()
    iteracao = 0
    melhor_solucao_global = None
    melhor_valor_global = float('inf')
    melhor_sequencia = None
    # Gera N soluções iniciais
        # gera_inicial_n_vezes(parametros)
    # Roda todas as iterações inter-rotas
        # iteracao_hill_climbing_inter_rota(parametros)
    # Roda todas as iterações intra-rotas
    for _ in range(qtd_iteracoes):
        iteracao += 1
        relatorio_hill_climbing.append(iteracao)
        # Gera solluções iniciais
        melhor_solucao_ini, melhor_valor_ini, id_cam2, relatorio_sol_ini = gera_inicial_n_vezes(caminhoes, coordenadas, mat_dist, qtd_iteracoes)
        relatorio_hill_climbing.append(melhor_valor_ini)
        # Encontra o ótimo local da iteração
        sol_iteracao, sol_iteracao_valor = iteracao_hill_climbing_intra_rota(melhor_solucao_ini, melhor_valor_ini, id_cam2, caminhoes, mat_dist)
        relatorio_hill_climbing.append(sol_iteracao_valor)
        # Testa se este novo ótimo local é o melhor de todos
        if sol_iteracao_valor < melhor_valor_global:
            melhor_solucao_global = sol_iteracao
            melhor_valor_global = sol_iteracao_valor
            melhor_sequencia = id_cam2
        relatorio_hill_climbing.append(melhor_valor_global)
    print(f'Melhor Valor: {melhor_valor_global}')
    print(f'Rotas: {melhor_solucao_global}')
    print(f'Ordem Caminhões: {melhor_sequencia}')
    # Retorna a melhor solução encontrada
    return melhor_solucao_global, melhor_valor_global, melhor_sequencia, relatorio_hill_climbing


def salva_solucao(arq_solucao, valor_total, selecao_cam, pontos_rota, arq_relatorio, relatorio):
    caminhao_mais_rota = []
    # print(f'{selecao_cam}')
    for caminhao, rota in zip(selecao_cam, pontos_rota):
        sublista = [caminhao] + rota
        caminhao_mais_rota.append(sublista)
        # print(f'{sublista}')

    with open(arq_solucao, "w+", encoding="utf8") as f:
        f.write(f"{valor_total}\n")
        # print(valor_total)
        info_id = 0
        for linha in caminhao_mais_rota:
            for info in linha:
                if info_id == 0:
                    f.write(f"{info}")
                else:
                    f.write(f";{info}")
                info_id += 1
            info_id = 0
            f.write(f"\n")
        # print(linha)

    #Salvando relatório
    iteracoes = [relatorio[i:i+4] for i in range(0, len(relatorio), 4)]

    with open(arq_relatorio, "w+", encoding="utf8") as g:
        g.write(f'ITERAÇÃO;')
        g.write(f'INICIAL;')
        g.write(f'LOCAL;')
        g.write(f'GLOBAL\n')
        for linha in iteracoes:
            quantidade = linha
            cont = 1
            for rel in quantidade:
                if cont == 1:
                    g.write(f'{rel}')
                else:
                    g.write(f';{rel}')
                cont += 1
            g.write(f'\n')




def resolve_instancia(arq_inst, arq_sol, arq_rel, qtd_iteracoes):
    caminhoes, coordenadas, mat_dist = le_arquivo(arq_inst)
    # selecao_cam_infos, rotas, selecao_cam = gera_solucao_inicial(caminhoes, coordenadas, mat_dist)
    # valor_total, id_caminhoes, pontos_rota = calcula_custo(selecao_cam_infos, rotas, mat_dist)
    # melhor_solucao, melhor_valor, id_cam, relatorio = gera_inicial_n_vezes(caminhoes, coordenadas, mat_dist, qtd_iteracoes)
    melhor_solucao_global, melhor_valor_global, id_cam3, relatorio_hill_climbing = solver_hill_climbing(caminhoes, coordenadas, mat_dist, qtd_iteracoes)
    salva_solucao(arq_sol, melhor_valor_global, id_cam3, melhor_solucao_global, arq_rel, relatorio_hill_climbing)





def main():
    pasta_instancias = 'Instancias/'
    pasta_solucoes = 'Solucoes/'
    pasta_relatorios = 'Relatorios/'
    arquivos = os.listdir(pasta_instancias)
    arquivos.sort()
    for arquivo in arquivos:
        print(arquivo)
        t_ini = time.time()
        resolve_instancia(pasta_instancias + arquivo, pasta_solucoes + arquivo, pasta_relatorios + arquivo, 100)
        t_fim = time.time()
        print(f'Tempo de execução: {t_fim - t_ini :.2f} ')
        print()


if __name__ == '__main__':
    main()