import math

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .param_mec import ParamMec
from .param_elet import ParamElet
from .motor import Motor
from .baterias import Baterias
from .limitacoes import Limitacoes
# from . import ParamMec, ParamElet, Motor, Baterias, Limitacoes
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D


class Veiculo:
    def __init__(self) -> None:
        self.energia_recuperada = None
        self.status_violacoes_bat = None
        self.energia_cons_bat = None
        self.status_motor_novo = None
        self.energia_baterias = None
        self.energia_regenerativa_max = None
        self.energia_frenagem_traseira = None
        self.energia_frenagem_dianteira = None
        self.energia_total_max = None
        self.status_motor = None

        self.aceleracao_veiculo = None
        self.energia_frenagem_max = None
        self.forca_trativa = None
        self.coef_resist_rolagem = None
        self.vel_motor = None
        self.base_dados_simulacao = None
        self.base_segunda_rodada = None
        self.velocidade = None
        self.distancia_percorrida = None
        self.param_mec = ParamMec(veiculo=self)
        self.param_elet = ParamElet(veiculo=self)
        self.motor = Motor(veiculo=self)
        self.baterias = Baterias(veiculo=self)
        self.limitacoes = Limitacoes(veiculo=self)

    def le_dados_planilha(self, caminho: str):
        self.base_dados_simulacao = pd.read_excel(caminho, sheet_name="Entrada velocidade")
        self.motor.le_parametros_motor(caminho=caminho)
        self.motor.le_frequencias_motor(caminho=caminho)
        self.param_mec.le_parametros_mec(caminho=caminho)
        self.param_elet.le_parametros_elet(caminho=caminho)
        self.baterias.le_parametros_baterias(caminho=caminho)
        self.limitacoes.le_limitacoes(caminho=caminho)

    # função 1 - OK
    # converte velocidades de km/h para m/s
    def converte_vel_veiculo_kph_mps(self):
        self.base_dados_simulacao['speed_ms'] = self.base_dados_simulacao['speed'] / 3.6

    # função 2 - TERMINAR
    def calcula_e_extrapola_distancia_total(self):

        self.distancia_percorrida = self.base_dados_simulacao['speed_ms'] * self.base_dados_simulacao['diff_tempo']
        self.base_dados_simulacao['distancia_percorrida'] = self.distancia_percorrida
        self.base_dados_simulacao['distancia_percorrida_acumulada'] = self.base_dados_simulacao[
            'distancia_percorrida'].cumsum()

        # if self.distancia_percorrida < self.base_dados_simulacao['distância para extrapolar']:
        #     append speed
        #     append soma tempo[end] + tempo
        #     agora vetor completo e pronto para outros cálculos

    # calcula coeficiente de resistência à rolagem em função da velocidade

    # função 3
    def calcula_coef_resist_rolagem_f(self):
        self.coef_resist_rolagem = 0.01 * (1 + self.base_dados_simulacao['speed_ms'] / 100)
        self.base_dados_simulacao['coef_resist_rolagem'] = self.coef_resist_rolagem

    # função 4 - OK
    # calcula velocidade do motor considerando a razão de transmissão
    def calcula_vel_motor(self):
        # rpm = m/s * 60 / 2 * pi * r
        self.vel_motor = ((self.base_dados_simulacao['speed_ms'] * 60 * self.param_mec.razao_transmissao) / (
                2 * math.pi * self.param_mec.raio_pneu))

        self.base_dados_simulacao['vel_motor'] = self.vel_motor
        self.motor.set_velocidade(velocidade_motor=self.vel_motor)
        # self.motor.calcula_escorregamento_motor()

    # função 5
    def calcula_aceleracao_veiculo(self):
        self.base_dados_simulacao['speed_0'] = self.base_dados_simulacao['speed_ms'].shift(1)
        self.base_dados_simulacao['elapsedTime_0'] = self.base_dados_simulacao['elapsedTime'].shift(1)

        self.aceleracao_veiculo = self.base_dados_simulacao.apply(
            lambda var: self.calcula_derivada_numerica(y1=var['speed_ms'], y0=var['speed_0'],
                                                       x1=var['elapsedTime'], x0=var['elapsedTime_0']), axis=1)

        # calcula intervalo de tempo
        self.base_dados_simulacao['diff_tempo'] = (
                self.base_dados_simulacao['elapsedTime']
                - self.base_dados_simulacao['elapsedTime_0'].fillna(0)
        )

    # funções 6 e 7: calcula_fator_inercia_rotacional e calcula_distribuicao_frenagem_otima
    # função 8 - OK
    # calcula a força trativa do veículo: N
    def calcula_forca_trativa(self):
        self.param_mec.calcula_fator_inercia_rotacional()
        self.forca_trativa = self.param_mec.massa * self.coef_resist_rolagem * self.param_mec.aceleracao_gravidade + \
                             (
                                     1 / 2) * self.param_mec.densidade_ar_rho_a * self.param_mec.coef_arrasto_aero_cd * self.param_mec.area_frontal * (
                                     self.base_dados_simulacao['speed_ms'] ** 2) + \
                             self.param_mec.massa * self.param_mec.fator_inercia_rotacional * self.aceleracao_veiculo

        self.base_dados_simulacao['forca_trativa'] = self.forca_trativa

    # função 9 - verificar
    # verifica qual o estado do veículo com limitação de velocidade
    def define_estado_motor(self):
        self.status_motor = []
        self.status_motor.append(0)
        for posicao in range(1, len(self.base_dados_simulacao['speed'])):
            if (self.base_dados_simulacao['speed'][posicao] - self.base_dados_simulacao['speed'][posicao - 1]) <= 0:
                if self.base_dados_simulacao['speed'][posicao] >= self.limitacoes.vel_min_regen:
                    self.status_motor.append(1)  # regenerando
                else:
                    self.status_motor.append(0)  # desligado
            else:
                self.status_motor.append(2)  # motorizando

        self.base_dados_simulacao['status motor'] = self.status_motor

    # função 10: rodar tudo da classe motor
    # função 11: rodar calcula_potencia_saida_baterias

    # função 12:

    def calcula_energias_inicial(self, segunda_rodada=False):

        if not segunda_rodada:
            base_dados = self.base_dados_simulacao
            status = pd.Series(self.status_motor)
        else:
            base_dados = self.base_segunda_rodada
            status = pd.Series(self.status_motor_novo)

        # deltatempo * força trativa * vel / eff transmissão
        # energia mecânica total
        # J = s * W = s * N * m / s
        self.energia_total_max = base_dados['diff_tempo'] * base_dados['forca_trativa'] * base_dados[
            'speed_ms'] / self.param_mec.eff_transmissao / 3600

        # energia frenagem eixo dianteiro
        # deltatempo * alpha * força trativa * vel / eff transmissão
        self.energia_frenagem_dianteira = (1 - self.param_mec.distribuicao_frenagem_alpha) * base_dados['diff_tempo'] * \
                                          base_dados['forca_trativa'] * base_dados[
                                              'speed_ms'] / self.param_mec.eff_transmissao / 3600
        self.energia_frenagem_dianteira.loc[status == 2] = 0
        self.energia_frenagem_dianteira = np.abs(self.energia_frenagem_dianteira)

        # energia frenagem recuperável max -> eixo traseiro
        # deltatempo * (1-alpha) * força trativa * vel / eff transmissão
        self.energia_regenerativa_max = self.param_mec.distribuicao_frenagem_alpha * base_dados['diff_tempo'] * \
                                        base_dados['forca_trativa'] * base_dados[
                                            'speed_ms'] / self.param_mec.eff_transmissao / 3600
        self.energia_regenerativa_max = np.abs(self.energia_regenerativa_max)
        self.energia_regenerativa_max.loc[status != 1] = 0

        self.energia_cons_bat = base_dados['diff_tempo'] * base_dados['potencia_saida_baterias'] / 3600
        self.energia_cons_bat.loc[status != 2] = 0

        base_dados['energia_total_max'] = self.energia_total_max
        base_dados['energia_frenagem_dianteira'] = self.energia_frenagem_dianteira
        base_dados['energia_regenerativa_max'] = self.energia_regenerativa_max

        base_dados['energia_cons_bat'] = self.energia_cons_bat

    # função 13
    def calcula_energia_baterias(self, segunda_rodada=False):

        if not segunda_rodada:
            status_motor = self.status_motor
        else:
            status_motor = self.status_motor_novo

        self.energia_baterias = []
        self.status_motor_novo = []
        self.status_violacoes_bat = []
        self.energia_recuperada = []

        # Wh
        self.energia_baterias.append(self.baterias.carga_nom_bat)
        self.status_motor_novo.append(self.status_motor[0])
        self.status_violacoes_bat.append(0)
        self.energia_recuperada.append(0)

        for posicao in range(1, len(self.energia_regenerativa_max)):
            # caso desligado, energia atual = energia anterior
            if status_motor[posicao] == 0:
                self.energia_baterias.append(self.energia_baterias[posicao - 1])
                self.status_motor_novo.append(0)
                self.status_violacoes_bat.append(0)
                self.energia_recuperada.append(0)

            # caso regenerando, verifica se a energia no acumulador ultrapassa o limite superior definido
            # senão, energia atual = energia anterior + energia regenerada
            elif status_motor[posicao] == 1:
                if (self.energia_baterias[posicao - 1] + np.abs(self.energia_regenerativa_max[posicao])) > (
                        self.baterias.carga_nom_bat * self.limitacoes.lim_bat_regen_max / 100):
                    self.status_motor_novo.append(0)
                    self.energia_baterias.append(self.energia_baterias[posicao - 1])
                    self.status_violacoes_bat.append(1)
                    self.energia_recuperada.append(0)
                else:
                    self.status_motor_novo.append(1)
                    self.energia_baterias.append(
                        self.energia_baterias[posicao - 1] + np.abs(self.energia_regenerativa_max[posicao]))
                    self.status_violacoes_bat.append(0)
                    self.energia_recuperada.append(np.abs(self.energia_regenerativa_max[posicao]))

            # caso motorizando, verifica se a energia no acumulador fica inferior ao limite inferior definido
            # senão, energia atual = energia anterior - energia gasta
            elif status_motor[posicao] == 2:
                if (self.energia_baterias[posicao - 1] - np.abs(self.energia_cons_bat[posicao])) < (
                        self.baterias.carga_nom_bat * self.limitacoes.lim_bat_regen_min / 100):
                    self.status_motor_novo.append(0)
                    self.energia_baterias.append(self.energia_baterias[posicao - 1])
                    self.status_violacoes_bat.append(2)
                    self.energia_recuperada.append(0)
                else:
                    self.status_motor_novo.append(2)
                    self.energia_baterias.append(
                        self.energia_baterias[posicao - 1] - np.abs(self.energia_cons_bat[posicao]))
                    self.status_violacoes_bat.append(0)
                    self.energia_recuperada.append(0)

        if not segunda_rodada:
            self.base_dados_simulacao['status_violacoes_bat'] = self.status_violacoes_bat
            self.base_dados_simulacao['energia_baterias_wh'] = self.energia_baterias
            self.base_dados_simulacao['status_motor_novo'] = self.status_motor_novo
            self.corrige_status_novo()
            self.status_motor_novo = self.base_dados_simulacao['status_motor_novo']
            self.base_dados_simulacao['energia recuperada'] = self.energia_recuperada
        else:
            self.base_segunda_rodada['status_violacoes_bat'] = self.status_violacoes_bat
            self.base_segunda_rodada['energia_baterias_wh'] = self.energia_baterias
            self.base_segunda_rodada['status_motor_novo'] = self.status_motor_novo
            self.base_segunda_rodada['energia recuperada'] = self.energia_recuperada

    def corrige_status_novo(self):
        self.base_dados_simulacao.reset_index(drop=True, inplace=True)

        indice_final = None
        for idx, elem in enumerate(self.base_dados_simulacao['status_violacoes_bat']):
            if elem == 2:
                indice_final = idx
                break

        filtro_zerar = self.base_dados_simulacao.index > indice_final

        self.base_dados_simulacao.loc[filtro_zerar, 'status_motor_novo'] = 0

    # função 14: repassa por 10.5 até 10.10, 11 e 12

    @staticmethod
    def calcula_derivada_numerica(y1, y0, x1, x0):
        derivada = (y1 - y0) / (x1 - x0)
        return derivada

    def dump_resultados(self, versao, path_output='outputs'):
        arquivo_dump = f'{path_output}/resultados_versao_{versao}_{str(self.limitacoes.vel_min_regen)}.xlsx'

        with pd.ExcelWriter(arquivo_dump) as writer:
            self.base_dados_simulacao.to_excel(writer, index=False, sheet_name='Primeira Rodada')
            self.base_segunda_rodada.to_excel(writer, index=False, sheet_name='Segunda Rodada')

        self.plota_imagens()

        print(f'\nSimulação finalizada. Arquivo disponibilizado em \"{arquivo_dump}\".')

    def inicializa_segunda_rodada(self):
        self.base_segunda_rodada = self.base_dados_simulacao.copy()
        del self.base_segunda_rodada['status motor']

    def plota_imagens(self):
        # preenche vetores constantes para comparação
        tamanho = len(self.base_dados_simulacao['distancia_percorrida_acumulada'])

        lim_corrente_sup = self.limitacoes.torque_motor_max_ref * self.motor.corrente_nom / 100
        lim_corrente_inf = - self.limitacoes.torque_regen_max_ref * self.motor.corrente_nom / 100

        lim_corrente_sup_array = [lim_corrente_sup for _ in range(tamanho)]
        lim_corrente_inf_array = [lim_corrente_inf for _ in range(tamanho)]

        # cria figuras para plotar
        drivecycle = plt.figure(figsize=(13.69, 9.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['speed'])
        drivecycle.suptitle('Drivecycle', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Velocidade (km/h)', fontsize=10)

        balanco_energias_dist = plt.figure(figsize=(13.69, 9.27))
        plt.plot(self.base_dados_simulacao['distancia_percorrida_acumulada'],
                 self.base_dados_simulacao['energia_baterias_wh'])
        balanco_energias_dist.suptitle('Balanço de energia do acumulador no percurso', fontsize=12)
        plt.xlabel('Distância (m)', fontsize=10)
        plt.ylabel('Energia (Wh)', fontsize=10)

        energia_cons_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['energia_cons_bat'])
        energia_cons_tempo.suptitle('Energia consumida no percurso', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Energia (Wh)', fontsize=10)

        energia_rec_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['energia recuperada'])
        energia_rec_tempo.suptitle('Energia recuperada no percurso', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Energia (Wh)', fontsize=10)

        energia_rec_vs_diant_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['energia_frenagem_dianteira'], self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['energia recuperada'])
        energia_rec_vs_diant_tempo.suptitle('Energia de frenagem recuperada no eixo traseiro versus Energia de frenagem no eixo dianteiro', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Energia (Wh)', fontsize=10)

        corrente_torque_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['corrente_rotor'], self.base_dados_simulacao['elapsedTime'],
                 lim_corrente_inf_array, self.base_dados_simulacao['elapsedTime'],
                 lim_corrente_sup_array)
        corrente_torque_tempo.suptitle('Corrente de torque no percurso', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Corrente (A)', fontsize=10)

        # corrente_torque_sem_limit_tempo = plt.figure(figsize=(11.69, 8.27))
        # plt.plot(self.base_dados_simulacao['elapsedTime'],
        #          self.base_dados_simulacao['corrente_rotor_temp'], self.base_dados_simulacao['elapsedTime'],
        #          lim_corrente_inf_array, self.base_dados_simulacao['elapsedTime'],
        #          lim_corrente_sup_array)
        # corrente_torque_sem_limit_tempo.suptitle('Corrente de torque (sem limitações) no percurso', fontsize=12)
        # plt.xlabel('Tempo (s)', fontsize=10)
        # plt.ylabel('Corrente (A)', fontsize=10)

        corrente_total_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'], 2 *
                 self.base_dados_simulacao['corrente_estator'])
        corrente_total_tempo.suptitle('Corrente nas baterias no percurso', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Corrente (A)', fontsize=10)

        # rendimento_motor_tempo = plt.figure(figsize=(11.69, 8.27))
        # plt.plot(self.base_dados_simulacao['elapsedTime'], 2 *
        #          self.base_dados_simulacao[''])
        # corrente_total_tempo.suptitle('Rendimento dos motores', fontsize=12)
        # plt.xlabel('Tempo (s)', fontsize=10)
        # plt.ylabel('%', fontsize=10)

        temperatura_motor_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['temperatura_motor'])
        temperatura_motor_tempo.suptitle('Temperatura do motor no percurso', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Temperatura (°C)', fontsize=10)

        forca_total_tempo = plt.figure(figsize=(11.69, 8.27))
        plt.plot(self.base_dados_simulacao['elapsedTime'],
                 self.base_dados_simulacao['forca_trativa'])
        forca_total_tempo.suptitle('Força total no percurso', fontsize=12)
        plt.xlabel('Tempo (s)', fontsize=10)
        plt.ylabel('Força trativa (N)', fontsize=10)

        forca_vel = plt.figure(figsize=(11.69, 8.27))
        plt.scatter(self.base_dados_simulacao['speed'],
                 self.base_dados_simulacao['forca_trativa'], s=10, c='green')
        forca_vel.suptitle('Força versus Velocidade', fontsize=12)
        plt.xlabel('Velocidade (km/h)', fontsize=10)
        plt.ylabel('Força trativa (N)', fontsize=10)

        # fig = plt.figure()
        # forca_vel_tempo = fig.add_subplot(111, projection='3d')
        # forca_vel_tempo.scatter(self.base_dados_simulacao['forca_trativa'], self.base_dados_simulacao['speed'], self.base_dados_simulacao['elapsedTime'])
        # # forca_vel_tempo.set_title('Força e Velocidade versus tempo', fontsize=12)
        # forca_vel_tempo.set_ylabel('Velocidade (km/h)', fontsize=10)
        # forca_vel_tempo.set_xlabel('Força trativa (N)', fontsize=10)
        # forca_vel_tempo.set_zlabel('Tempo (s)', fontsize=10)

        # textos página inicial
        txt1 = '\n\n\n\nParâmetros da simulação: \n\n '
        txt2 = 'Velocidade mínima para frenagem: ' + str(self.limitacoes.vel_min_regen) + ' km/h \n'
        txt3 = 'Limitação mínima do banco de baterias: ' + str(self.limitacoes.lim_bat_regen_min) + ' % \n'
        txt4 = 'Limitação máxima do banco de baterias: ' + str(self.limitacoes.lim_bat_regen_max) + ' % \n'
        txt5 = 'Referência de torque positivo máxima: ' + str(self.limitacoes.torque_motor_max_ref) + ' % \n'
        txt6 = 'Referência de torque negativo máxima: ' + str(self.limitacoes.torque_regen_max_ref) + ' % \n'

        txt = txt1 + txt2 + txt3 + txt4 + txt5 + txt6

        # valores consolidados:
        distancia_total = self.base_dados_simulacao['distancia_percorrida_acumulada'].iloc[-1]

        temp_media = self.base_dados_simulacao['temperatura_motor'].mean()
        temp_max = self.base_dados_simulacao['temperatura_motor'].max()
        energia_final = self.energia_baterias[-1]
        energia_total_consumida = sum(self.energia_cons_bat)
        energia_total_recuperada = sum(self.energia_recuperada)
        # energia_total_freios_mec = sum(np.abs(self.energia_frenagem_dianteira))
        violacoes_corrente_max_motor = np.count_nonzero(pd.Series(self.motor.status_violacoes_motor) == 1)
        violacoes_corrente_regen_motor = np.count_nonzero(pd.Series(self.motor.status_violacoes_motor) == 2)
        violacoes_bat_max = np.count_nonzero((self.base_dados_simulacao['status_violacoes_bat'] == 1))
        violacoes_bat_min = np.count_nonzero((self.base_dados_simulacao['status_violacoes_bat'] == 2))
        vel_media = self.base_dados_simulacao['speed'].mean()

        txt7 = '\n\n\nValores consolidados: \n\n '
        vel_media = 'Velocidade média: ' + str(np.round(vel_media, decimals=2)) + ' km/h \n'
        dist = 'Distância total percorrida: ' + str(np.round(distancia_total, decimals=2)) + ' m \n'
        txt8 = 'Energia total consumida: ' + str(np.round(energia_total_consumida, decimals=2)) + ' Wh \n'
        txt9 = 'Energia total recuperada: ' + str(np.round(energia_total_recuperada, decimals=2)) + ' Wh \n'
        txt10 = 'Energia final no banco de baterias: ' + str(np.round(energia_final, decimals=2)) + ' Wh \n'
        txt11 = 'Temperatura máxima nos motores: ' + str(np.round(temp_max, decimals=2)) + ' °C \n'
        txt12 = 'Temperatura média nos motores: ' + str(np.round(temp_media, decimals=2)) + ' °C \n'
        txt13 = 'Quantidade de violações à corrente máxima de motorização: ' + str(violacoes_corrente_max_motor) + '\n'
        txt14 = 'Quantidade de violações à corrente máxima de recuperação: ' + str(
            violacoes_corrente_regen_motor) + '\n'
        txt15 = 'Quantidade de violações à limitação máxima do banco de baterias: ' + str(
            violacoes_bat_max) + '\n'
        txt16 = 'Quantidade de violações à limitação mínima do banco de baterias: ' + str(
            violacoes_bat_min) + '\n'

        txt_2 = txt7 + vel_media + dist + txt8 + txt9 + txt10 + txt11 + txt12 + txt13 + txt14 + txt15 + txt16

        # cria pdf
        pp = PdfPages('outputs/resultados.pdf')
        firstpage = plt.figure(figsize=(11.69, 8.27))
        firstpage.clf()
        print(txt + txt_2)
        firstpage.text(0.5, 0.3, txt + txt_2, transform=firstpage.transFigure, size=12, ha="center")

        pp.savefig(firstpage)
        pp.savefig(drivecycle)
        pp.savefig(balanco_energias_dist)
        pp.savefig(energia_cons_tempo)
        pp.savefig(energia_rec_tempo)
        pp.savefig(energia_rec_vs_diant_tempo)
        pp.savefig(corrente_torque_tempo)
        pp.savefig(corrente_total_tempo)
        pp.savefig(temperatura_motor_tempo)
        pp.savefig(forca_total_tempo)
        pp.savefig(forca_vel)
       # pp.savefig(fig)

        pp.close()
