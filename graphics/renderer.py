"""Sistema de renderização"""
import pygame
from config.settings import *


class GameRenderer:
    """Responsável por renderizar todos os elementos do jogo."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.distance_font = pygame.font.SysFont(None, 28)

    def clear_screen(self):
        """Limpa a tela com a cor de fundo."""
        self.screen.fill(BACKGROUND_COLOR)

    def draw_ground(self, camera_x):
        """Desenha a plataforma e o chão."""
        # Plataforma principal
        pygame.draw.rect(self.screen, PLATFORM_TOP_COLOR, 
                        (0, GROUND_Y, WINDOW_WIDTH, 12))
        
        # Chão abaixo da plataforma
        pygame.draw.rect(self.screen, PLATFORM_BOTTOM_COLOR, 
                        (0, GROUND_Y + 12, WINDOW_WIDTH, WINDOW_HEIGHT - GROUND_Y - 12))

        # Listras no chão para efeito de movimento
        self._draw_ground_stripes(camera_x)

    def _draw_ground_stripes(self, camera_x):
        """Desenha listras no chão que se movem com a câmera."""
        stripe_width = 60
        offset = int(camera_x) % stripe_width
        
        for x in range(-offset, WINDOW_WIDTH, stripe_width):
            pygame.draw.rect(self.screen, GROUND_STRIPE_COLOR, 
                           (x, GROUND_Y + 16, stripe_width // 3, 6))

    def draw_hud(self, distance):
        """Desenha a interface do usuário."""
        # Controles
        controls_text = "←/→ correr | ESPAÇO pular | SHIFT/X dash | J/Z atirar | ESC sair"
        controls_surface = self.font.render(controls_text, True, UI_TEXT_COLOR)
        self.screen.blit(controls_surface, (16, 12))

        # Distância
        distance_text = f"Distância: {int(distance):04d}px"
        distance_surface = self.distance_font.render(distance_text, True, DISTANCE_TEXT_COLOR)
        self.screen.blit(distance_surface, (WINDOW_WIDTH - 260, 10))

    def draw_player(self, player):
        """Desenha o jogador."""
        self.screen.blit(player.image, player.rect)

    def draw_projectiles(self, projectiles):
        """Desenha todos os projéteis."""
        projectiles.draw(self.screen)