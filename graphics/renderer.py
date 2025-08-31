"""Sistema de renderização atualizado"""
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

    def draw_background(self, background_img, camera_x):
        """Desenha o background com efeito parallax e repetição infinita."""
        if not background_img:
            return
        
        bg_width = background_img.get_width()
        bg_height = background_img.get_height()
        
        # MODIFICADO: Sistema de repetição infinita
        # Calcula quantas repetições são necessárias para cobrir a tela
        parallax_speed = 0.3  # Background se move mais devagar que a câmera
        bg_x_offset = (camera_x * parallax_speed) % bg_width
        
        # Número de cópias necessárias para cobrir toda a tela
        copies_needed = (WINDOW_WIDTH // bg_width) + 2  # +2 para garantir cobertura total
        
        # Desenha múltiplas cópias do background
        for i in range(copies_needed):
            bg_x = (i * bg_width) - bg_x_offset
            
            # Posição Y para alinhar com o topo da tela
            bg_y = 0
            
            # Se a imagem for muito alta, corta para mostrar só a parte de cima
            if bg_height > WINDOW_HEIGHT:
                # Cria uma versão cortada mostrando só a parte superior
                cropped_bg = background_img.subsurface((0, 0, bg_width, WINDOW_HEIGHT))
                self.screen.blit(cropped_bg, (bg_x, bg_y))
            else:
                # Se a imagem couber na tela, desenha normalmente
                self.screen.blit(background_img, (bg_x, bg_y))
                
                # Se a imagem for menor que a altura da tela, pode repetir verticalmente também
                if bg_height < WINDOW_HEIGHT:
                    remaining_height = WINDOW_HEIGHT - bg_height
                    y_copies = (remaining_height // bg_height) + 1
                    
                    for j in range(1, y_copies + 1):
                        self.screen.blit(background_img, (bg_x, bg_y + (j * bg_height)))

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

    def draw_hud(self, distance, player=None):
        """Desenha a interface do usuário durante o jogo."""
        controls_text = "←/→ correr | Z pular | X dash | A atirar | ESC pause"
        controls_surface = self.font.render(controls_text, True, UI_TEXT_COLOR)
        self.screen.blit(controls_surface, (16, 12))

        # Distância
        distance_text = f"Distância: {int(distance):04d}px"
        distance_surface = self.distance_font.render(distance_text, True, DISTANCE_TEXT_COLOR)
        self.screen.blit(distance_surface, (WINDOW_WIDTH - 260, 10))
        
        # Barra de vida (só desenha se player foi passado)
        if player:
            self._draw_health_bar(player)

    def _draw_health_bar(self, player):
        """Desenha a barra de vida do jogador."""
        # Posição da barra (ajustada para subir um pouco)
        bar_x = 16
        bar_y = 35  # MODIFICADO: Era 45, agora 35 (subiu 10px)
        bar_width = 200
        bar_height = 20
        
        # Fundo da barra (bordas)
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Calcula a largura da barra baseada na vida
        health_ratio = player.current_health / player.max_health
        health_width = int(bar_width * health_ratio)
        
        # Cor da barra baseada na porcentagem de vida
        if health_ratio > 0.6:
            health_color = (50, 200, 50)    # Verde (boa saúde)
        elif health_ratio > 0.3:
            health_color = (200, 200, 50)   # Amarelo (atenção)
        else:
            health_color = (200, 50, 50)    # Vermelho (perigo)
        
        # Desenha a barra de vida se ainda tem vida
        if health_width > 0:
            pygame.draw.rect(self.screen, health_color, 
                            (bar_x, bar_y, health_width, bar_height))
        
        # Texto da vida
        health_text = f"LIFE: {player.current_health}/{player.max_health}"
        health_surface = pygame.font.SysFont('Arial', 16).render(health_text, True, UI_TEXT_COLOR)
        self.screen.blit(health_surface, (bar_x + bar_width + 10, bar_y + 2))

    def draw_player(self, player):
        """Desenha o jogador na tela."""
        if player and player.is_alive:
            self.screen.blit(player.image, player.rect)

    def draw_sprites(self, sprite_group):
        """Desenha um grupo de sprites na tela."""
        for sprite in sprite_group:
            if hasattr(sprite, 'rect') and hasattr(sprite, 'image'):
                self.screen.blit(sprite.image, sprite.rect)

    def draw_projectiles(self, projectile_group):
        """Desenha projéteis na tela."""
        self.draw_sprites(projectile_group)

    def draw_enemies(self, enemy_group):
        """Desenha inimigos na tela."""
        self.draw_sprites(enemy_group)

    def draw_enemy_projectiles(self, projectile_group):
        """Desenha projéteis dos inimigos na tela."""
        self.draw_sprites(projectile_group)