import pandas as pd


class Limitacoes:
    def __init__(self, veiculo):
        self.veiculo = veiculo
        self.torque_motor_max_ref = None
        self.base_limitacoes = None
        self.vel_min_regen = None
        self.lim_bat_regen_min = None
        self.lim_bat_regen_max = None
        self.torque_regen_max_ref = None

    def le_limitacoes(self, caminho):
        self.base_limitacoes = pd.read_excel(caminho, sheet_name="Limitações")
        self.base_limitacoes = self.base_limitacoes.set_index('Parâmetro')

        # Guardando limitações em atributos
        self.vel_min_regen = self.base_limitacoes.loc['velocidade mínima para frenagem regenerativa', 'Valor']
        self.lim_bat_regen_max = self.base_limitacoes.loc['máxima porcentagem de carga do acumulador para regeneração',
                                                          'Valor']
        self.lim_bat_regen_min = self.base_limitacoes.loc['mínima porcentagem de carga do acumulador para regeneração',
                                                          'Valor']
        self.torque_regen_max_ref = self.base_limitacoes.loc['referência de torque máximo de frenagem', 'Valor']
        self.torque_motor_max_ref = self.base_limitacoes.loc['referência de torque máximo de motorização', 'Valor']
