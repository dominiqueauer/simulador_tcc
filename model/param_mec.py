import math
import numpy as np
import pandas as pd


class ParamMec:
    def __init__(self, veiculo):
        self.veiculo = veiculo
        self.coeficiente_aderencia_pista = None
        self.distribuicao_frenagem_alpha = None
        self.fator_inercia_rotacional = None
        self.temperatura_ambiente = None
        self.base_parametros_mecanicos = None
        self.altura_cg = None  # m
        self.dist_entre_eixos_l = None  # m
        self.dist_cg_traseiro_lb = None  # m
        self.massa = None  # kg
        self.area_frontal = None  # m^2
        self.coef_arrasto_aero_cd = None  # coeficiente de arrasto aerodinâmico
        self.raio_pneu = None  # m
        self.eff_transmissao = None
        self.razao_transmissao = None
        self.densidade_ar_rho_a = None  # kg/m^3
        self.aceleracao_gravidade = None

    def le_parametros_mec(self, caminho):
        self.base_parametros_mecanicos = pd.read_excel(caminho, sheet_name="Parâmetros Mecânicos")
        self.base_parametros_mecanicos = self.base_parametros_mecanicos.set_index('Parâmetro')

        # Guardando os parâmetros mecânicos em atributos
        self.altura_cg = self.base_parametros_mecanicos.loc['altura CG', 'Valor']
        self.dist_entre_eixos_l = self.base_parametros_mecanicos.loc['distância entre eixos', 'Valor']
        self.dist_cg_traseiro_lb = self.base_parametros_mecanicos.loc['distância CG eixo traseiro', 'Valor']
        self.massa = self.base_parametros_mecanicos.loc['massa veículo + piloto', 'Valor']
        self.area_frontal = self.base_parametros_mecanicos.loc['área frontal', 'Valor']
        self.coef_arrasto_aero_cd = self.base_parametros_mecanicos.loc['coeficiente de arrasto aerodinâmico', 'Valor']
        self.raio_pneu = self.base_parametros_mecanicos.loc['raio do pneu', 'Valor']
        self.eff_transmissao = self.base_parametros_mecanicos.loc['eficiência da transmissão', 'Valor']
        self.razao_transmissao = self.base_parametros_mecanicos.loc['razão de transmissão', 'Valor']
        self.densidade_ar_rho_a = self.base_parametros_mecanicos.loc['densidade do ar', 'Valor']
        self.aceleracao_gravidade = self.base_parametros_mecanicos.loc['aceleração da gravidade', 'Valor']
        self.temperatura_ambiente = self.base_parametros_mecanicos.loc['temperatura ambiente', 'Valor']
        self.coeficiente_aderencia_pista = self.base_parametros_mecanicos.loc['coeficiente de aderência à pista', 'Valor']

    def calcula_fator_inercia_rotacional(self):
        self.fator_inercia_rotacional = 1 + 0.04 + 0.0025 * self.razao_transmissao
    
    def calcula_distribuicao_frenagem_otima(self):
        self.distribuicao_frenagem_alpha = 1 - ((self.coeficiente_aderencia_pista * self.altura_cg + self.dist_cg_traseiro_lb) / self.dist_entre_eixos_l)
