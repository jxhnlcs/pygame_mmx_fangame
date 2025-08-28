import pygame
from enum import Enum
from config.settings import *

class ScoreManager:
    
    def __init__(self):
        self.scores_file = "highscores.txt"
        self.max_scores = 10
        self.high_scores = self.load_scores()
    
    def load_scores(self):
        try:
            with open(self.scores_file, 'r') as f:
                scores = []
                for line in f:
                    try:
                        score = float(line.strip())
                        scores.append(score)
                    except ValueError:
                        continue
                return sorted(scores, reverse=True)[:self.max_scores]
        except FileNotFoundError:
            return []
    
    def save_scores(self):
        try:
            with open(self.scores_file, 'w') as f:
                for score in self.high_scores:
                    f.write(f"{score}\n")
        except Exception as e:
            pass
    
    def add_score(self, distance):
        self.high_scores.append(distance)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:self.max_scores]
        self.save_scores()
        
        try:
            position = self.high_scores.index(distance) + 1
            return position
        except ValueError:
            return None
    
    def get_best_score(self):
        return self.high_scores[0] if self.high_scores else 0


class GameOverScreen:
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 42, bold=True)
        self.font_stats = pygame.font.SysFont('Arial', 20)
        self.font_menu = pygame.font.SysFont('Arial', 18)
        self.font_ranking = pygame.font.SysFont('Arial', 16)
        
        self.selected_option = 0
        self.options = ["TENTAR NOVAMENTE", "MENU PRINCIPAL"]
        
        self.title_color = (255, 100, 100)
        self.stats_color = (200, 200, 255)
        self.selected_color = (255, 255, 100)
        self.normal_color = (200, 200, 200)
        self.ranking_color = (150, 255, 150)
        self.new_record_color = (255, 255, 100)
        
        self.distance = 0
        self.time_played = 0
        self.ranking_position = None
        self.is_new_record = False
        
        self.score_manager = ScoreManager()
        
    def set_stats(self, distance, time_played):
        self.distance = distance
        self.time_played = time_played
        
        self.ranking_position = self.score_manager.add_score(distance)
        self.is_new_record = self.ranking_position == 1 and len(self.score_manager.high_scores) > 1
        
    def handle_input(self, keys, key_pressed):
        action = None
        
        if key_pressed.get(pygame.K_UP, False):
            self.selected_option = (self.selected_option - 1) % len(self.options)
            
        if key_pressed.get(pygame.K_DOWN, False):
            self.selected_option = (self.selected_option + 1) % len(self.options)
            
        if key_pressed.get(pygame.K_RETURN, False):
            if self.selected_option == 0:
                action = "restart"
            elif self.selected_option == 1:
                action = "menu"
                
        if key_pressed.get(pygame.K_ESCAPE, False):
            action = "menu"
            
        return action
        
    def render(self):
        self.screen.fill((40, 20, 20))
        
        title_text = self.font_title.render("GAME OVER", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        if self.is_new_record:
            record_text = self.font_stats.render("NOVO RECORDE!", True, self.new_record_color)
            record_rect = record_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
            self.screen.blit(record_text, record_rect)
        
        stats_y = 160
        if self.ranking_position:
            ranking_text = f"Posição no Ranking: {self.ranking_position}º lugar"
            ranking_surface = self.font_stats.render(ranking_text, True, self.ranking_color)
            ranking_rect = ranking_surface.get_rect(center=(WINDOW_WIDTH // 2, stats_y))
            self.screen.blit(ranking_surface, ranking_rect)
            stats_y += 30
        
        distance_text = f"Distância Percorrida: {int(self.distance)} pixels"
        time_text = f"Tempo Jogado: {int(self.time_played / 1000)}s"
        
        distance_surface = self.font_stats.render(distance_text, True, self.stats_color)
        time_surface = self.font_stats.render(time_text, True, self.stats_color)
        
        distance_rect = distance_surface.get_rect(center=(WINDOW_WIDTH // 2, stats_y))
        time_rect = time_surface.get_rect(center=(WINDOW_WIDTH // 2, stats_y + 30))
        
        self.screen.blit(distance_surface, distance_rect)
        self.screen.blit(time_surface, time_rect)
        
        self._draw_high_scores(stats_y + 80)
        
        start_y = 420
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, text_rect)
            
            if i == self.selected_option:
                indicator = self.font_menu.render("►", True, self.selected_color)
                indicator_rect = indicator.get_rect(center=(text_rect.left - 25, text_rect.centery))
                self.screen.blit(indicator, indicator_rect)
        
        instructions = "ENTER Selecionar | ESC Menu Principal"
        instructions_surface = self.font_menu.render(instructions, True, (150, 150, 150))
        instructions_rect = instructions_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(instructions_surface, instructions_rect)
    
    def _draw_high_scores(self, start_y):
        title = self.font_stats.render("MELHORES DISTÂNCIAS", True, self.stats_color)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, start_y))
        self.screen.blit(title, title_rect)
        
        y_offset = start_y + 35
        for i, score in enumerate(self.score_manager.high_scores[:5]):
            position = i + 1
            color = self.new_record_color if position == self.ranking_position else self.normal_color
            
            score_text = f"{position}º - {int(score)} pixels"
            score_surface = self.font_ranking.render(score_text, True, color)
            score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, y_offset + i * 20))
            self.screen.blit(score_surface, score_rect)


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class StateManager:
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        
    def change_state(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state
        
    def get_current_state(self):
        return self.current_state
        
    def get_previous_state(self):
        return self.previous_state


class MenuScreen:
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_menu = pygame.font.SysFont('Arial', 24)
        self.font_subtitle = pygame.font.SysFont('Arial', 18)
        
        self.selected_option = 0
        self.options = ["INICIAR JOGO", "SAIR"]
        
        self.title_color = (100, 150, 255)
        self.selected_color = (255, 255, 100)
        self.normal_color = (200, 200, 200)
        self.subtitle_color = (150, 150, 150)
        
    def handle_input(self, keys, key_pressed):
        action = None
        
        up_pressed = key_pressed.get(pygame.K_UP, False)
        down_pressed = key_pressed.get(pygame.K_DOWN, False)
        
        if up_pressed:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            
        if down_pressed:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            
        if key_pressed.get(pygame.K_RETURN, False):
            if self.selected_option == 0:
                action = "start_game"
            elif self.selected_option == 1:
                action = "quit"
                
        if key_pressed.get(pygame.K_ESCAPE, False):
            action = "quit"
            
        return action
        
    def render(self):
        self.screen.fill((20, 30, 50))
        
        title_text = self.font_title.render("MEGA MAN X", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_subtitle.render("John Lucas ~ Megaman X Runner", True, self.subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        start_y = 250
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 50))
            self.screen.blit(text, text_rect)
            
            if i == self.selected_option:
                indicator = self.font_menu.render("►", True, self.selected_color)
                indicator_rect = indicator.get_rect(center=(text_rect.left - 30, text_rect.centery))
                self.screen.blit(indicator, indicator_rect)
        
        controls_text = "↑/↓ Navegar | ENTER Selecionar | ESC Sair"
        controls_surface = self.font_subtitle.render(controls_text, True, self.subtitle_color)
        controls_rect = controls_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(controls_surface, controls_rect)


class PauseScreen:
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_menu = pygame.font.SysFont('Arial', 20)
        
        self.selected_option = 0
        self.options = ["CONTINUAR", "REINICIAR", "MENU PRINCIPAL"]
        
        self.title_color = (255, 255, 255)
        self.selected_color = (255, 255, 100)
        self.normal_color = (200, 200, 200)
        
    def handle_input(self, keys, key_pressed):
        action = None
        
        up_pressed = key_pressed.get(pygame.K_UP, False)
        down_pressed = key_pressed.get(pygame.K_DOWN, False)
        
        if up_pressed:
            self.selected_option = (self.selected_option - 1) % len(self.options)
            
        if down_pressed:
            self.selected_option = (self.selected_option + 1) % len(self.options)
            
        if key_pressed.get(pygame.K_RETURN, False):
            if self.selected_option == 0:
                action = "resume"
            elif self.selected_option == 1:
                action = "restart"
            elif self.selected_option == 2:
                action = "menu"
                
        if key_pressed.get(pygame.K_ESCAPE, False):
            action = "resume"
            
        return action
        
    def render(self, background_surface=None):
        if background_surface:
            darkened = background_surface.copy()
            dark_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            dark_overlay.set_alpha(128)
            dark_overlay.fill((0, 0, 0))
            darkened.blit(dark_overlay, (0, 0))
            self.screen.blit(darkened, (0, 0))
        else:
            self.screen.fill((40, 40, 60))
        
        panel_rect = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, 
                                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, (30, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, (100, 120, 150), panel_rect, 3)
        
        title_text = self.font_title.render("PAUSE", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.top + 60))
        self.screen.blit(title_text, title_rect)
        
        start_y = panel_rect.centery - 20
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            text = self.font_menu.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text, text_rect)
            
            if i == self.selected_option:
                indicator = self.font_menu.render("►", True, self.selected_color)
                indicator_rect = indicator.get_rect(center=(text_rect.left - 25, text_rect.centery))
                self.screen.blit(indicator, indicator_rect)