import numpy as np
import pandas as pd

class Baterias:
    def __init__(self, veiculo):
        self.capacidade_celula = None
        self.celulas_serie = None
        self.ramos_paralelos = None
        self.tensao_celula = None
        self.veiculo = veiculo
        self.potencia_saida_baterias = None
        self.carga_nom_bat = None
        self.base_parametros_baterias = None
        self.lim_bat_min = None
        self.lim_bat_max = None

    def le_parametros_baterias(self, caminho):
        self.base_parametros_baterias = pd.read_excel(caminho, sheet_name="Parâmetros Baterias")
        self.base_parametros_baterias = self.base_parametros_baterias.set_index('Parâmetro')

        # Guardando os parâmetros mecânicos em atributos
        # self.carga_nom_bat = self.base_parametros_baterias.loc['energia máxima', 'Valor']
        # self.lim_bat_min = self.base_parametros_baterias.loc['limite de carga mínimo', 'Valor']
        # self.lim_bat_max = self.base_parametros_baterias.loc['limite de carga máximo', 'Valor']
        self.celulas_serie = self.base_parametros_baterias.loc['células em série', 'Valor']
        self.ramos_paralelos = self.base_parametros_baterias.loc['ramos em paralelo', 'Valor']
        self.tensao_celula = self.base_parametros_baterias.loc['tensão célula', 'Valor']
        self.capacidade_celula = self.base_parametros_baterias.loc['capacidade por célula', 'Valor']

    def calcula_potencia_saida_baterias(self, segunda_rodada=False):
        self.potencia_saida_baterias = self.veiculo.motor.potencia_entrada_motor * self.veiculo.param_elet. \
            qtd_motores / self.veiculo.param_elet.eff_inv
        if not segunda_rodada:
            self.veiculo.base_dados_simulacao['potencia_saida_baterias'] = self.potencia_saida_baterias
        else:
            self.veiculo.base_segunda_rodada['potencia_saida_baterias'] = self.potencia_saida_baterias

    def calcula_carga_bat(self):
        self.carga_nom_bat = int(self.celulas_serie * self.ramos_paralelos * self.tensao_celula * self.capacidade_celula)
