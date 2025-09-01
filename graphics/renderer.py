"""Sistema de renderização atualizado"""
import pygame
import math  # ADICIONADO: Import para os cálculos do escudo
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
        
        # MODIFICADO: Sistema de repetição infinita com offset inicial
        parallax_speed = 0.3  # Background se move mais devagar que a câmera
        
        # ADICIONADO: Offset inicial para começar a imagem mais à direita
        initial_offset = bg_width * 0.7  # Começa a imagem 70% deslocada para a direita
        bg_x_offset = ((camera_x * parallax_speed) + initial_offset) % bg_width
        
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
        controls_text = "</> correr | Z pular | X dash | A atirar | ESC pause"
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
        health_text = f"VIDA: {player.current_health}/{player.max_health}"
        health_surface = pygame.font.SysFont('Arial', 16).render(health_text, True, UI_TEXT_COLOR)
        self.screen.blit(health_surface, (bar_x + bar_width + 10, bar_y + 2))
        
        # ADICIONADO: Indicadores de power-ups ativos
        self._draw_powerup_indicators(player, bar_x, bar_y + 30)
    
    def _draw_powerup_indicators(self, player, x, y):
        """Desenha indicadores dos power-ups ativos."""
        indicator_width = 60
        indicator_height = 15
        spacing = 5
        current_x = x
        
        # Indicador de tiro rápido
        if player.rapid_fire_timer > 0:
            # Barra de progresso do tiro rápido
            progress = player.rapid_fire_timer / 10000  # 10 segundos total
            fill_width = int(indicator_width * progress)
            
            pygame.draw.rect(self.screen, (100, 100, 255), 
                           (current_x, y, indicator_width, indicator_height))
            pygame.draw.rect(self.screen, (200, 200, 255), 
                           (current_x, y, fill_width, indicator_height))
            
            text = pygame.font.SysFont('Arial', 12).render("DISPAROS RÁPIDOS", True, (255, 255, 255))
            self.screen.blit(text, (current_x + 2, y + 1))
            
            current_x += indicator_width + spacing
        
        # Indicador de escudo - MODIFICADO: Melhor feedback visual
        if player.has_shield:
            # Barra de progresso do escudo
            progress = player.shield_timer / 15000  # 15 segundos total
            fill_width = int(indicator_width * progress)
            
            # MODIFICADO: Cores diferentes baseadas no tempo restante
            if progress > 0.6:
                # Escudo forte (verde-amarelo)
                shield_color = (100, 255, 100)
                fill_color = (150, 255, 150)
            elif progress > 0.3:
                # Escudo médio (amarelo)
                shield_color = (255, 255, 100)
                fill_color = (255, 255, 150)
            else:
                # Escudo fraco (vermelho piscando)
                if int(player.shield_flash_timer / 100) % 2:
                    shield_color = (255, 100, 100)
                    fill_color = (255, 150, 150)
                else:
                    shield_color = (200, 80, 80)
                    fill_color = (220, 120, 120)
            
            pygame.draw.rect(self.screen, shield_color, 
                           (current_x, y, indicator_width, indicator_height))
            pygame.draw.rect(self.screen, fill_color, 
                           (current_x, y, fill_width, indicator_height))
            
            # MODIFICADO: Texto com aviso quando está fraco
            if progress <= 0.3:
                text = pygame.font.SysFont('Arial', 10).render("ACABANDO!", True, (255, 255, 255))
            else:
                text = pygame.font.SysFont('Arial', 12).render("ESCUDO", True, (0, 0, 0))

            self.screen.blit(text, (current_x + 2, y + 1))

    def draw_player(self, player):
        """Desenha o jogador na tela."""
        if player and player.is_alive:
            # ADICIONADO: Desenha círculo do escudo antes do jogador
            if player.has_shield:
                self._draw_shield_circle(player)
            
            self.screen.blit(player.image, player.rect)

    def _draw_shield_circle(self, player):
        """Desenha o círculo visual do escudo em volta do jogador."""
        # Configurações do círculo
        shield_radius = 75  # Raio do círculo do escudo
        center_x = player.rect.centerx
        center_y = player.rect.centery
        
        # Calcula progresso do escudo (0.0 a 1.0)
        progress = player.shield_timer / 15000 if player.shield_timer > 0 else 0
        
        # ADICIONADO: Cores diferentes baseadas no tempo restante
        if progress > 0.6:
            # Escudo forte (azul-ciano)
            shield_color = (100, 200, 255)
            glow_color = (150, 220, 255)
        elif progress > 0.3:
            # Escudo médio (amarelo)
            shield_color = (255, 255, 100)
            glow_color = (255, 255, 150)
        else:
            # Escudo fraco (vermelho-laranja piscando)
            if int(player.shield_flash_timer / 100) % 2:
                shield_color = (255, 100, 100)
                glow_color = (255, 150, 150)
            else:
                shield_color = (255, 150, 100)
                glow_color = (255, 200, 150)
        
        # CORRIGIDO: Usa math.sin em vez de pygame.math.sin
        pulse_factor = abs(math.sin(player.shield_flash_timer * 0.01)) * 0.3 + 0.7
        current_radius = int(shield_radius * pulse_factor)
        
        # ADICIONADO: Desenha múltiplos círculos para efeito de brilho
        # Círculo externo (brilho suave)
        glow_radius = current_radius + 8
        glow_alpha = 30
        
        # Cria surface temporária para o brilho com alpha
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*glow_color, glow_alpha), 
                         (glow_radius, glow_radius), glow_radius)
        
        # Desenha o brilho
        glow_rect = glow_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(glow_surface, glow_rect)
        
        # ADICIONADO: Círculo principal do escudo (transparente)
        shield_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
        
        # Círculo preenchido com transparência
        pygame.draw.circle(shield_surface, (*shield_color, 60), 
                         (current_radius, current_radius), current_radius)
        
        # Borda do círculo (mais opaca)
        pygame.draw.circle(shield_surface, (*shield_color, 120), 
                         (current_radius, current_radius), current_radius, 3)
        
        # ADICIONADO: Efeito de "energia" - círculos menores rotativos
        for i in range(6):  # 6 pontos de energia
            angle = (player.shield_flash_timer * 0.005 + i * (2 * math.pi / 6)) % (2 * math.pi)
            energy_x = center_x + math.cos(angle) * (current_radius - 8)
            energy_y = center_y + math.sin(angle) * (current_radius - 8)
            
            # Desenha pequenos círculos de energia
            energy_size = 3 if progress > 0.3 else 2
            pygame.draw.circle(self.screen, shield_color, 
                             (int(energy_x), int(energy_y)), energy_size)
        
        # Desenha o círculo principal
        shield_rect = shield_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(shield_surface, shield_rect)
        
        # ADICIONADO: Efeito especial quando escudo está quase acabando
        if progress <= 0.2 and progress > 0:
            # Círculos de aviso piscando
            if int(player.shield_flash_timer / 50) % 2:
                warning_radius = current_radius + 15
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (center_x, center_y), warning_radius, 2)

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