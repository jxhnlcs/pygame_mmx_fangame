"""Sistema de câmera"""
from config.settings import WINDOW_WIDTH


class Camera:
    """Gerencia a câmera do jogo."""
    
    def __init__(self):
        self.x = 0.0

    def update(self, player):
        """Atualiza a posição da câmera para seguir o jogador."""
        # A câmera sempre segue o jogador, mantendo-o no centro da tela
        # Corrigido: remove o max(0, ...) que causava o bug
        self.camera_x = player.world_x - WINDOW_WIDTH // 2

    def get_x(self):
        """Retorna a posição X da câmera."""
        return self.camera_x