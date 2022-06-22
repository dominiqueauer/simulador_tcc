import numpy as np
import pandas as pd


class ParamElet:
    def __init__(self, veiculo):
        self.veiculo = veiculo
        self.base_parametros_elet = None
        self.p_nom_hardware = None
        self.eff_inv = None
        self.qtd_motores = None

    def le_parametros_elet(self, caminho):
        self.base_parametros_elet = pd.read_excel(caminho, sheet_name="Parâmetros Elétricos")
        self.base_parametros_elet = self.base_parametros_elet.set_index('Parâmetro')

        # Guardando os parâmetros mecânicos em atributos
        self.eff_inv = self.base_parametros_elet.loc['Eficiência do inversor', 'Valor']
        self.qtd_motores = self.base_parametros_elet.loc['Quantidade de motores', 'Valor']

