# from curses.ascii import ETB
# from glob import iglob
import math 
import numpy as np
import pandas as pd

from model import Veiculo

if __name__ == '__main__':
    carro = Veiculo()

    caminho_str = 'Testes/template.xlsm'
    carro.le_dados_planilha(caminho=caminho_str)

    # 1
    carro.converte_vel_veiculo_kph_mps()
    # 2
    carro.calcula_aceleracao_veiculo()
    carro.calcula_e_extrapola_distancia_total()
    # 3
    carro.calcula_coef_resist_rolagem_f()
    # 4
    carro.calcula_vel_motor()
    # 5

    # 6, 7, 8
    carro.calcula_forca_trativa()
    # 9
    carro.define_estado_motor()
    # 10
    carro.motor.calcula_tudo_motor()
    # 11
    carro.baterias.calcula_potencia_saida_baterias()
    # 12
    carro.calcula_energias_inicial()
    # 13
    carro.baterias.calcula_carga_bat()
    carro.calcula_energia_baterias()

    # Segunda_rodada
    # Inicializa_segunda_rodada
    carro.inicializa_segunda_rodada()

    # 10
    carro.motor.calcula_tudo_motor(segunda_rodada=True)
    # 11
    carro.baterias.calcula_potencia_saida_baterias(segunda_rodada=True)
    # 12
    carro.calcula_energias_inicial(segunda_rodada=True)
    # 13
    carro.calcula_energia_baterias(segunda_rodada=True)

    carro.dump_resultados(versao='0.1')










    para = 0
    