import cmath

import numpy as np
import math
import pandas as pd


class Motor:
    def __init__(self, veiculo):
        self.fluxo_magnetizacao = None
        self.base_frequencias_motor = None
        self.frequencias_motor = None
        self.status_motor_2 = None

        self.potencia_entreferro_motor = None
        self.temperatura_motor = None
        self.veiculo = veiculo
        self.rendimento_motor = None
        self.potencia_saida_motor_mec = None

        self.tau_termico_motor = None
        self.capacitancia_termica_motor = None
        self.resistencia_termica_motor = None
        self.potencia_perdas_motor = None
        self.maxima_elevacao_temp_motor = None
        self.massa_motor = None
        self.i_vazio = None
        self.base_parametros_motor = None

        self.potencia_entrada_motor = None
        self.potencia_saida_motor = None
        self.corrente_rotor = None
        self.corrente_estator = None
        self.impedancia_equivalente = None
        self.impedancia_estator = None
        self.res_rotor_escorregamento = None
        self.impedancia_rotor = None
        self.vel_motor = None
        self.escorregamento_motor = None
        self.polos = None
        self.vel_sincrona = None
        self.impedancia_magnetizacao = None

        self.reat_magnetizacao = None
        self.res_magnetizacao = None
        self.reat_estator = None
        self.res_estator = None
        self.reat_rotor = None
        self.res_rotor = None

        self.torque_nom = None
        self.p_nom = None
        self.corrente_nom = None
        self.v_nom = None
        self.vel_nom = None
        self.freq_nom = None
        self.corrente_vazio = None

    def le_parametros_motor(self, caminho):
        self.base_parametros_motor = pd.read_excel(caminho, sheet_name="Parâmetros Motor")
        self.base_parametros_motor = self.base_parametros_motor.set_index('Parâmetro')

        # Guardando os parâmetros do motor em atributos
        self.torque_nom = self.base_parametros_motor.loc['torque nominal', 'Valor']
        self.p_nom = self.base_parametros_motor.loc['potência nominal motor', 'Valor']
        self.corrente_nom = self.base_parametros_motor.loc['corrente nominal motor', 'Valor']
        self.corrente_vazio = self.base_parametros_motor.loc['corrente a vazio', 'Valor']
        self.v_nom = self.base_parametros_motor.loc['tensão alimentação motor', 'Valor']
        self.freq_nom = self.base_parametros_motor.loc['frequência nominal', 'Valor']
        self.vel_nom = self.base_parametros_motor.loc['velocidade nominal', 'Valor']
        self.res_estator = self.base_parametros_motor.loc['resistência do estator R1', 'Valor']
        self.reat_estator = self.base_parametros_motor.loc['reatância do estator X1', 'Valor']
        self.res_magnetizacao = self.base_parametros_motor.loc['resistência do núcleo Rc', 'Valor']
        self.reat_magnetizacao = self.base_parametros_motor.loc['reatância de magnetização Xm', 'Valor']
        self.res_rotor = self.base_parametros_motor.loc['resistência do rotor R2', 'Valor']
        self.reat_rotor = self.base_parametros_motor.loc['reatância do rotor X2', 'Valor']
        self.massa_motor = self.base_parametros_motor.loc['massa do motor', 'Valor']
        self.maxima_elevacao_temp_motor = self.base_parametros_motor.loc[
            'máxima elevação de temperatura motor', 'Valor']
        self.fluxo_magnetizacao = self.base_parametros_motor.loc['fluxo nominal de magnetização', 'Valor']

    def calcula_tudo_motor(self, segunda_rodada=False):

        self.calcula_potencia_saida_motor_mec(segunda_rodada)

        # self.define_frequencia()

        if not segunda_rodada:
            self.calcula_vel_sincrona()

            self.calcula_escorregamento_motor()

            # self.define_estado_motor_2()

            self.calcula_impedancia_equivalente()

        self.calcula_correntes_motor_com_potencia_mec(segunda_rodada)

        self.calcula_potencia_entrada_motor(segunda_rodada)

        self.calcula_potencia_perdas_motor(segunda_rodada)

        self.calcula_rendimento_motor(segunda_rodada)

        self.calcula_temperatura_motor(segunda_rodada)

    def procura_mais_proximo(self, vel_motor, pot_saida):
        base_frequencia = self.base_frequencias_motor
        tolerancia = 300

        # filtra base
        filtro = np.logical_and(base_frequencia['min'] <= pot_saida, base_frequencia['max'] >= pot_saida)

        # trata potencia fora dos valores mapeados
        if all(np.logical_not(filtro)):
            return self.freq_nom

        base_frequencia = base_frequencia[filtro].reset_index(drop=True)
        base_frequencia['diff'] = base_frequencia['media'] - pot_saida
        base_frequencia['diff_abs'] = np.abs(base_frequencia['diff'])
        min_value = base_frequencia['diff_abs'].min()

        filtro_retorno = base_frequencia['diff_abs'] == min_value
        # base_frequencia = base_frequencia[filtro_retorno].reset_index(drop=True)
        base_retorno = base_frequencia[filtro_retorno].reset_index(drop=True)
        if len(base_retorno) == 1:
            return float(base_retorno['Frequency'])
        else:
            raise Exception('Meu deus, meu senhor, me ajuda, por favor')

    def define_frequencia(self):

        base_veiculo = self.veiculo.base_dados_simulacao

        # ORIGINAL
        # self.veiculo.base_dados_simulacao['frequencia_motor'] = base_veiculo.apply(lambda x: self.procura_mais_proximo(vel_motor=x['vel_motor'], pot_saida=x['potencia_saida_motor_mec']), axis=1)

        para = 0

    # 1
    # calcula velocidade síncrona a partir da velocidade nominal do motor
    def calcula_vel_sincrona(self):
        self.polos = np.floor(120 * self.freq_nom / self.vel_nom)
        self.vel_sincrona = 120 * self.freq_nom / self.polos
        # frequência variável

    #        self.frequencias_motor = self.veiculo.base_dados_simulacao['frequencia_motor']
    #        self.vel_sincrona = 120 * self.frequencias_motor / self.polos

    # 2 (já chamado pelo Veículo)
    # define velocidade do motor a partir da razão de transmissão
    def set_velocidade(self, velocidade_motor):
        self.vel_motor = velocidade_motor

    # 3
    # calcula escorregamento a partir da velocidade síncrona e velocidade do motor
    def calcula_escorregamento_motor(self):
        self.escorregamento_motor = (self.vel_sincrona - self.vel_motor) / self.vel_sincrona
        #        self.escorregamento_motor = pd.Series([0.03 for _ in self.escorregamento_motor])
        self.veiculo.base_dados_simulacao['escorregamento_motor'] = self.escorregamento_motor

    # 4
    # calcula impedância equivalente do circuito equivalente do motor
    def calcula_impedancia_equivalente(self):
        self.impedancia_magnetizacao = (complex(0, self.reat_magnetizacao) + self.res_magnetizacao) / (
                complex(0, self.reat_magnetizacao) * self.res_magnetizacao)

        self.res_rotor_escorregamento = self.res_rotor / self.escorregamento_motor
        self.veiculo.base_dados_simulacao['res_rotor_escorregamento'] = self.res_rotor_escorregamento

        self.impedancia_rotor = self.res_rotor_escorregamento + (complex(0, self.reat_rotor))
        self.veiculo.base_dados_simulacao['impedancia_rotor'] = self.impedancia_rotor

        self.impedancia_estator = self.res_estator + (complex(0, self.reat_estator))

        # equivalente = rotor//magnetizacao + estator
        self.impedancia_equivalente = (self.impedancia_rotor * self.impedancia_magnetizacao) / (
                self.impedancia_rotor + self.impedancia_magnetizacao) + self.impedancia_estator
        self.veiculo.base_dados_simulacao['impedancia_equivalente'] = self.impedancia_equivalente

    # calcula as correntes que circulam pelo motor a partir da tensão e impedância equivalentes
    #   def calcula_correntes_motor(self):
    #       self.corrente_estator = self.v_nom / ((math.sqrt(3)) * self.impedancia_equivalente)
    #       self.corrente_rotor = self.corrente_estator - self.corrente_vazio

    # calcula a potência de saída do motor a partir das correntes, impedâncias e escorregamento calculados
    #   def calcula_potencia_saida_motor(self):
    #       self.potencia_saida_motor = 3 * self.corrente_rotor ** 2 * self.res_rotor * (1 - self.escorregamento_motor) / \
    #                                   self.escorregamento_motor

    # função 5
    # provavelmente essa potência será para dois motores, dividir pela quantidade
    def calcula_potencia_saida_motor_mec(self, segunda_rodada):

        self.veiculo.param_mec.calcula_distribuicao_frenagem_otima()

        if segunda_rodada:
            status_motor = self.veiculo.status_motor_novo.copy()
        else:
            status_motor = self.veiculo.status_motor.copy()

        self.potencia_saida_motor_mec = pd.Series([np.nan for _ in range(len(status_motor))])

        filtro_status_0 = [elem == 0 for elem in status_motor]
        filtro_status_1 = [elem == 1 for elem in status_motor]
        filtro_status_2 = [elem == 2 for elem in status_motor]

        # if status == 1
        self.potencia_saida_motor_mec.loc[filtro_status_1] = - np.abs(
            self.veiculo.param_mec.distribuicao_frenagem_alpha *
            self.veiculo.base_dados_simulacao.loc[
                filtro_status_1, 'speed_ms'] *
            self.veiculo.forca_trativa.loc[
                filtro_status_1] / (
                    self.veiculo.param_elet.qtd_motores * self.veiculo.param_mec.eff_transmissao))

        # else if status == 2
        self.potencia_saida_motor_mec.loc[filtro_status_2] = np.abs(
            self.veiculo.base_dados_simulacao.loc[filtro_status_2, 'speed_ms'] *
            self.veiculo.forca_trativa.loc[filtro_status_2] / (
                    self.veiculo.param_elet.qtd_motores * self.veiculo.param_mec.eff_transmissao))

        # else if status == 0
        self.potencia_saida_motor_mec.loc[filtro_status_0] = 0

        if segunda_rodada:
            self.veiculo.base_segunda_rodada['potencia_saida_motor_mec'] = self.potencia_saida_motor_mec
        else:
            self.veiculo.base_dados_simulacao['potencia_saida_motor_mec'] = self.potencia_saida_motor_mec

    # função 6
    # calcula correntes considerando a potência mecânica e as limitações de torque negativo e positivo
    def calcula_correntes_motor_com_potencia_mec(self, segunda_rodada):
        corrente_rotor_temp = np.sqrt(np.abs((np.abs(self.potencia_saida_motor_mec) * self.escorregamento_motor)
                                             / (3 * (1 - self.escorregamento_motor) * self.res_rotor)))

        corrente_rotor_temp.fillna(0, inplace=True)

        self.corrente_rotor = []
        self.corrente_estator = []
        self.status_violacoes_motor = []

        if segunda_rodada:
            status = self.veiculo.status_motor_novo
        else:
            status = self.veiculo.status_motor

        for posicao in range(len(corrente_rotor_temp)):
            # desligado
            if status[posicao] == 0:
                self.corrente_rotor.append(0)
                self.corrente_estator.append(0)
                self.status_violacoes_motor.append(0)
            # regenerando
            elif status[posicao] == 1:
                if corrente_rotor_temp[posicao] > (
                        self.veiculo.limitacoes.torque_regen_max_ref * self.corrente_nom / 100):

                    valor = - self.veiculo.limitacoes.torque_regen_max_ref * self.corrente_nom / 100
                    self.corrente_rotor.append(valor)
                    valor = - math.sqrt((valor ** 2 - ((self.corrente_vazio * self.fluxo_magnetizacao / 100) ** 2)))
                    self.status_violacoes_motor.append(1)
                else:
                    valor = - corrente_rotor_temp[posicao]
                    self.corrente_rotor.append(valor)

                    if (corrente_rotor_temp[posicao] ** 2 - ((self.corrente_vazio * self.fluxo_magnetizacao / 100) ** 2)) > 0:
                        valor = math.sqrt((corrente_rotor_temp[posicao] ** 2 - ((self.corrente_vazio * self.fluxo_magnetizacao / 100) ** 2)))
                    else:
                        valor = math.sqrt((((self.corrente_vazio * self.fluxo_magnetizacao / 100) ** 2) - corrente_rotor_temp[posicao] ** 2 ))
                    self.status_violacoes_motor.append(0)
                self.corrente_estator.append(valor)
            # motorizando
            else:
                if corrente_rotor_temp[posicao] > (
                        self.veiculo.limitacoes.torque_motor_max_ref * self.corrente_nom / 100):
                    valor = self.veiculo.limitacoes.torque_motor_max_ref * self.corrente_nom / 100
                    self.corrente_rotor.append(valor)
                    valor = math.sqrt(valor ** 2 + (self.corrente_vazio * self.fluxo_magnetizacao / 100) ** 2)
                    self.corrente_estator.append(valor)
                    self.status_violacoes_motor.append(2)

                else:
                    self.corrente_rotor.append(corrente_rotor_temp[posicao])

                    valor = math.sqrt(corrente_rotor_temp[posicao] ** 2 + (self.corrente_vazio * self.fluxo_magnetizacao / 100) ** 2)
                    self.corrente_estator.append(valor)
                    self.status_violacoes_motor.append(0)

        if segunda_rodada:
            self.veiculo.base_segunda_rodada['corrente_rotor_temp'] = corrente_rotor_temp
            self.veiculo.base_segunda_rodada['corrente_rotor'] = self.corrente_rotor
            self.veiculo.base_segunda_rodada['corrente_estator'] = self.corrente_estator
            self.veiculo.base_segunda_rodada['status violações motor'] = self.status_violacoes_motor
        else:
            self.veiculo.base_dados_simulacao['corrente_rotor_temp'] = corrente_rotor_temp
            self.veiculo.base_dados_simulacao['corrente_rotor'] = self.corrente_rotor
            self.veiculo.base_dados_simulacao['corrente_estator'] = self.corrente_estator
            self.veiculo.base_dados_simulacao['status violações motor'] = self.status_violacoes_motor

    # função 7 - OK
    # calcula a potência demandada por cada motor
    def calcula_potencia_entrada_motor(self, segunda_rodada):

        self.potencia_entrada_motor = np.abs(math.sqrt(3) * self.v_nom * pd.Series(self.corrente_estator) * np.cos(
            pd.Series([cmath.phase(elem) for elem in self.impedancia_equivalente])))

        if not segunda_rodada:
            self.veiculo.base_dados_simulacao['potencia_entrada_motor'] = self.potencia_entrada_motor
            # self.veiculo.base_dados_simulacao['cosseno'] = pd.Series(
            #    np.cos([cmath.phase(elem) for elem in self.impedancia_equivalente]))
            # self.potencia_entreferro_motor = 3 * (pd.Series(self.corrente_estator) ** 2) * self.res_rotor
            # self.veiculo.base_dados_simulacao['potencia_entreferro_motor'] = self.potencia_entreferro_motor
        else:
            self.veiculo.base_segunda_rodada['potencia_entrada_motor'] = self.potencia_entrada_motor
            # self.veiculo.base_segunda_rodada['cosseno'] = pd.Series(
            #     np.cos([cmath.phase(elem) for elem in self.impedancia_equivalente]))
            # self.potencia_entreferro_motor = 3 * (pd.Series(self.corrente_estator) ** 2) * self.res_rotor
            # self.veiculo.base_segunda_rodada['potencia_entreferro_motor'] = self.potencia_entreferro_motor
            # self.potencia_entrada_motor = self.potencia_entreferro_motor

    # função 8
    def calcula_potencia_perdas_motor(self, segunda_rodada):

        self.potencia_perdas_motor = self.potencia_entrada_motor - self.potencia_saida_motor_mec
        if not segunda_rodada:
            self.veiculo.base_dados_simulacao['potencia_perdas_motor'] = self.potencia_perdas_motor
        else:
            self.veiculo.base_segunda_rodada['potencia_perdas_motor'] = self.potencia_perdas_motor

    # função 9
    def calcula_rendimento_motor(self, segunda_rodada):
        self.rendimento_motor = np.abs(self.potencia_saida_motor_mec) / np.abs(self.potencia_entrada_motor)
        if not segunda_rodada:
            self.veiculo.base_dados_simulacao['rendimento_motor'] = self.rendimento_motor
        else:
            self.veiculo.base_segunda_rodada['rendimento_motor'] = self.rendimento_motor

    # 10
    # calcula temperatura motor, se regenerando ou motorizando (aquece) e se desligado (resfria)

    def calcula_temperatura_motor(self, segunda_rodada):
        self.resistencia_termica_motor = np.abs(
            (self.maxima_elevacao_temp_motor - self.veiculo.param_mec.temperatura_ambiente) \
            / np.abs(self.potencia_perdas_motor))
        verifica_res_inf = self.resistencia_termica_motor == np.inf

        # se infinito, valor alto
        if any(pd.Series(verifica_res_inf)):
            self.resistencia_termica_motor.loc[verifica_res_inf] = 10000000

        # massa * calor específico do ferro (kg * J/kg°C =  J/°C)
        self.capacitancia_termica_motor = self.massa_motor * 460
        self.tau_termico_motor = self.resistencia_termica_motor * self.capacitancia_termica_motor

        if not segunda_rodada:
            status_motor = self.veiculo.status_motor.copy()
        else:
            status_motor = self.veiculo.status_motor_novo.copy()

        self.temperatura_motor = []

        self.temperatura_motor.append(self.veiculo.param_mec.temperatura_ambiente)

        for posicao in range(1, len(self.veiculo.base_dados_simulacao)):
            status = status_motor[posicao]
            if status == 0:
                val_temperatura_motor = self.calcula_temperatura_status_0(posicao)
            elif (status == 1) or (status == 2):
                val_temperatura_motor = self.calcula_temperatura_status_1_e_2(posicao)
            else:
                raise Exception('status inválido')

            self.temperatura_motor.append(val_temperatura_motor)

        if not segunda_rodada:
            self.veiculo.base_dados_simulacao['temperatura_motor'] = self.temperatura_motor
        else:
            self.veiculo.base_segunda_rodada['temperatura_motor'] = self.temperatura_motor

    def calcula_temperatura_status_1_e_2(self, posicao):
        fator_1 = np.abs(self.potencia_perdas_motor[posicao]) * self.resistencia_termica_motor[posicao]
        fator_2 = (
                1 - math.e ** (
                (-1) * self.veiculo.base_dados_simulacao['diff_tempo'][posicao] / self.tau_termico_motor[posicao])
        )
        fator_3 = self.veiculo.param_mec.temperatura_ambiente
        val_temperatura_motor = fator_1 * fator_2 + fator_3
        return val_temperatura_motor

    # motor desligado não tem perdas
    def calcula_temperatura_status_0(self, posicao):
        fator_1 = (
                self.temperatura_motor[posicao - 1]
                - self.veiculo.param_mec.temperatura_ambiente
        )
        fator_2 = (
                math.e ** (
                (-1) * (self.veiculo.base_dados_simulacao['diff_tempo'][posicao] / self.tau_termico_motor[posicao]))
        )
        fator_3 = (
                self.temperatura_motor[posicao - 1]
        )
        val_temperatura_motor = fator_1 * fator_2 + fator_3
        return val_temperatura_motor

    def define_estado_motor_2(self):
        self.status_motor_2 = []
        self.status_motor_2.append(0)
        for posicao in range(1, len(self.escorregamento_motor)):
            if self.escorregamento_motor[posicao] > 0:
                if self.escorregamento_motor[posicao] >= 1:
                    self.status_motor_2.append(0)  # desligado
                else:
                    self.status_motor_2.append(2)  # motorizando
            else:
                self.status_motor_2.append(1)  # regenerando

        self.veiculo.base_dados_simulacao['status motor_2'] = self.status_motor_2

    def le_frequencias_motor(self, caminho):
        self.base_frequencias_motor = pd.read_excel(caminho, sheet_name="Frequências")

