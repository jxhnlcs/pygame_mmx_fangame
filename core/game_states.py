"""Sistema de estados do jogo"""
import pygame
from enum import Enum
from config.settings import *


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class StateManager:
    """Gerencia os estados do jogo."""
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        
    def change_state(self, new_state):
        """Muda para um novo estado."""
        self.previous_state = self.current_state
        self.current_state = new_state
        
    def get_current_state(self):
        """Retorna o estado atual."""
        return self.current_state
        
    def get_previous_state(self):
        """Retorna o estado anterior."""
        return self.previous_state


class MenuScreen:
    """Tela de menu inicial."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_menu = pygame.font.SysFont('Arial', 24)
        self.font_subtitle = pygame.font.SysFont('Arial', 18)
        
        self.selected_option = 0
        self.options = ["INICIAR JOGO", "SAIR"]
        
        # Cores
        self.title_color = (100, 150, 255)
        self.selected_color = (255, 255, 100)
        self.normal_color = (200, 200, 200)
        self.subtitle_color = (150, 150, 150)
        
    def handle_input(self, keys, key_pressed):
        """Processa input do menu."""
        action = None
        
        # Debug: vamos verificar o que está chegando
        up_pressed = key_pressed.get(pygame.K_UP, False)
        down_pressed = key_pressed.get(pygame.K_DOWN, False)
        
        if up_pressed:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            print(f"[DEBUG] UP pressionado, opção: {self.selected_option}")
            
        if down_pressed:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            print(f"[DEBUG] DOWN pressionado, opção: {self.selected_option}")
            
        if key_pressed.get(pygame.K_RETURN, False):
            if self.selected_option == 0:  # INICIAR JOGO
                action = "start_game"
            elif self.selected_option == 1:  # SAIR
                action = "quit"
                
        if key_pressed.get(pygame.K_ESCAPE, False):
            action = "quit"
            
        return action
        
    def render(self):
        """Renderiza o menu."""
        self.screen.fill((20, 30, 50))
        
        # Título
        title_text = self.font_title.render("MEGA MAN X", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_subtitle.render("Runner Demo", True, self.subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Opções do menu
        start_y = 250
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 50))
            self.screen.blit(text, text_rect)
            
            # Indicador de seleção
            if i == self.selected_option:
                indicator = self.font_menu.render("►", True, self.selected_color)
                indicator_rect = indicator.get_rect(center=(text_rect.left - 30, text_rect.centery))
                self.screen.blit(indicator, indicator_rect)
        
        # Controles
        controls_text = "↑/↓ Navegar | ENTER Selecionar | ESC Sair"
        controls_surface = self.font_subtitle.render(controls_text, True, self.subtitle_color)
        controls_rect = controls_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(controls_surface, controls_rect)


class PauseScreen:
    """Tela de pause."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_menu = pygame.font.SysFont('Arial', 20)
        
        self.selected_option = 0
        self.options = ["CONTINUAR", "REINICIAR", "MENU PRINCIPAL"]
        
        # Cores
        self.title_color = (255, 255, 255)
        self.selected_color = (255, 255, 100)
        self.normal_color = (200, 200, 200)
        
    def handle_input(self, keys, key_pressed):
        """Processa input do pause."""
        action = None
        
        # Debug para pause
        up_pressed = key_pressed.get(pygame.K_UP, False)
        down_pressed = key_pressed.get(pygame.K_DOWN, False)
        
        if up_pressed:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            print(f"[DEBUG PAUSE] UP pressionado, opção: {self.selected_option}")
            
        if down_pressed:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            print(f"[DEBUG PAUSE] DOWN pressionado, opção: {self.selected_option}")
            
        if key_pressed.get(pygame.K_RETURN, False):
            if self.selected_option == 0:  # CONTINUAR
                action = "resume"
            elif self.selected_option == 1:  # REINICIAR
                action = "restart"
            elif self.selected_option == 2:  # MENU PRINCIPAL
                action = "menu"
                
        if key_pressed.get(pygame.K_ESCAPE, False):
            action = "resume"
            
        return action
        
    def render(self, background_surface=None):
        """Renderiza a tela de pause."""
        # Desenha o jogo em pausa no fundo (escurecido)
        if background_surface:
            darkened = background_surface.copy()
            dark_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            dark_overlay.set_alpha(128)
            dark_overlay.fill((0, 0, 0))
            darkened.blit(dark_overlay, (0, 0))
            self.screen.blit(darkened, (0, 0))
        else:
            self.screen.fill((40, 40, 60))
        
        # Painel central
        panel_rect = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, 
                                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, (30, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, (100, 120, 150), panel_rect, 3)
        
        # Título
        title_text = self.font_title.render("PAUSE", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.top + 60))
        self.screen.blit(title_text, title_rect)
        
        # Opções
        start_y = panel_rect.centery - 20
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, text_rect)
            
            # Indicador
            if i == self.selected_option:
                indicator = self.font_menu.render("►", True, self.selected_color)
                indicator_rect = indicator.get_rect(center=(text_rect.left - 25, text_rect.centery))
                self.screen.blit(indicator, indicator_rect)


class GameOverScreen:
    """Tela de game over."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 42, bold=True)
        self.font_stats = pygame.font.SysFont('Arial', 20)
        self.font_menu = pygame.font.SysFont('Arial', 18)
        
        self.selected_option = 0
        self.options = ["TENTAR NOVAMENTE", "MENU PRINCIPAL"]
        
        # Cores
        self.title_color = (255, 100, 100)
        self.stats_color = (200, 200, 255)
        self.selected_color = (255, 255, 100)
        self.normal_color = (200, 200, 200)
        
        # Estatísticas do jogo
        self.distance = 0
        self.time_played = 0
        
    def set_stats(self, distance, time_played):
        """Define as estatísticas finais."""
        self.distance = distance
        self.time_played = time_played
        
    def handle_input(self, keys, key_pressed):
        """Processa input do game over."""
        action = None
        
        if key_pressed.get(pygame.K_UP, False):
            self.selected_option = (self.selected_option - 1) % len(self.options)
            
        if key_pressed.get(pygame.K_DOWN, False):
            self.selected_option = (self.selected_option + 1) % len(self.options)
            
        if key_pressed.get(pygame.K_RETURN, False):
            if self.selected_option == 0:  # TENTAR NOVAMENTE
                action = "restart"
            elif self.selected_option == 1:  # MENU PRINCIPAL
                action = "menu"
                
        if key_pressed.get(pygame.K_ESCAPE, False):
            action = "menu"
            
        return action
        
    def render(self):
        """Renderiza a tela de game over."""
        self.screen.fill((40, 20, 20))
        
        # Título
        title_text = self.font_title.render("GAME OVER", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Estatísticas
        stats_y = 200
        distance_text = f"Distância Percorrida: {int(self.distance)} pixels"
        time_text = f"Tempo Jogado: {int(self.time_played / 1000)}s"
        
        distance_surface = self.font_stats.render(distance_text, True, self.stats_color)
        time_surface = self.font_stats.render(time_text, True, self.stats_color)
        
        distance_rect = distance_surface.get_rect(center=(WINDOW_WIDTH // 2, stats_y))
        time_rect = time_surface.get_rect(center=(WINDOW_WIDTH // 2, stats_y + 30))
        
        self.screen.blit(distance_surface, distance_rect)
        self.screen.blit(time_surface, time_rect)
        
        # Opções
        start_y = 320
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, text_rect)
            
            # Indicador
            if i == self.selected_option:
                indicator = self.font_menu.render("►", True, self.selected_color)
                indicator_rect = indicator.get_rect(center=(text_rect.left - 25, text_rect.centery))
                self.screen.blit(indicator, indicator_rect)
        
        # Instruções
        instructions = "ENTER Selecionar | ESC Menu Principal"
        instructions_surface = self.font_menu.render(instructions, True, (150, 150, 150))
        instructions_rect = instructions_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(instructions_surface, instructions_rect)