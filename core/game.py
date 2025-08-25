"""Classe principal do jogo com sistema de estados"""
import pygame
import sys
from pathlib import Path

from config.settings import *
from entities.player import Player
from graphics.camera import Camera
from graphics.renderer import GameRenderer
from core.game_states import StateManager, GameState, MenuScreen, PauseScreen, GameOverScreen


class Game:
    """Classe principal que gerencia o jogo com sistema de estados."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Sistema de estados
        self.state_manager = StateManager()
        self.menu_screen = MenuScreen(self.screen)
        self.pause_screen = PauseScreen(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        
        # Sistema de detecção de teclas pressionadas
        self.previous_keys = pygame.key.get_pressed()
        self.key_pressed = {}
        
        # Variáveis de jogo
        self.distance = 0.0
        self.start_time = 0
        self.total_time = 0
        self.running = True
        self.game_surface = None  # Para capturar o jogo para o pause
        
        # Inicialização dos componentes do jogo (será feita quando começar)
        self.camera = None
        self.renderer = None
        self.player = None
        self.projectiles = None
        self.sprite_sheet = None
        self.buster_sheet = None
        self.background = None
        self.shoot_sound = None

    def _initialize_game_components(self):
        """Inicializa os componentes do jogo quando necessário."""
        if self.camera is None:
            self.camera = Camera()
            self.renderer = GameRenderer(self.screen)
            self._load_assets()
            self._create_entities()
            self._setup_audio()

    def _load_assets(self):
        """Carrega todos os recursos do jogo."""
        # Carrega sprite sheet principal
        sheet_path = Path(__file__).parent.parent / "assets" / "spritesheets" / "mmx_xsheet.png"
        self.sprite_sheet = pygame.image.load(str(sheet_path)).convert()
        self.sprite_sheet.set_colorkey(MAGENTA_COLORKEY)
        
        # Carrega sprite sheet do buster
        buster_path = Path(__file__).parent.parent / "assets" / "spritesheets" / "mmx1-buster.png"
        self.buster_sheet = pygame.image.load(str(buster_path)).convert_alpha()
        
        # Carrega efeitos sonoros
        self._load_sound_effects()
        
        # Carrega background
        try:
            bg_path = Path(__file__).parent.parent / "assets" / "background.png"
            if bg_path.exists():
                self.background = pygame.image.load(str(bg_path)).convert()
            else:
                self.background = None
                print("[Background] Arquivo background.png não encontrado")
        except Exception as e:
            self.background = None
            print(f"[Background] Erro ao carregar background: {e}")

    def _load_sound_effects(self):
        """Carrega todos os efeitos sonoros."""
        try:
            pygame.mixer.init()
            
            # Carrega som de disparo
            shoot_sound_path = Path(__file__).parent.parent / "assets" / "sound-effects" / "shoots"
            
            # Procura por arquivos de áudio na pasta shoots
            sound_files = list(shoot_sound_path.glob("*.wav")) + list(shoot_sound_path.glob("*.mp3"))
            
            if sound_files:
                self.shoot_sound = pygame.mixer.Sound(str(sound_files[0]))
                print(f"[SFX] Som de disparo carregado: {sound_files[0].name}")
            else:
                self.shoot_sound = None
                print("[SFX] Nenhum arquivo de som encontrado na pasta shoots")
                
        except Exception as e:
            self.shoot_sound = None
            print(f"[SFX] Erro ao carregar efeitos sonoros: {e}")

    def _create_entities(self):
        """Cria as entidades do jogo."""
        # Define os retângulos das animações
        animation_rects = {
            'run': [(106, 108, 30, 33), (137, 108, 20, 33), (158, 108, 23, 33), 
                   (181, 108, 32, 33), (213, 108, 34, 33), (247, 108, 26, 33), 
                   (276, 108, 22, 33), (298, 108, 25, 33), (326, 108, 30, 33), 
                   (357, 108, 34, 33), (391, 108, 29, 33)],
            'jump': [(168, 66, 29, 34), (202, 63, 24, 37), (229, 58, 19, 43), 
                    (252, 54, 19, 46), (273, 58, 25, 42), (299, 61, 27, 39), 
                    (331, 62, 24, 38), (356, 68, 30, 32)],
            'dash': [(282, 157, 33, 35), (317, 161, 41, 27), (317, 161, 41, 27)],
            'shoot': [(133, 66, 30, 34), (168, 66, 29, 34)],
            'idle': (321, 15, 36, 36)
        }
        
        # Define coordenadas do projétil no buster sheet
        buster_rects = {
            'pellet': (61, 3, 10, 8)
        }

        # Cria o jogador
        self.player = Player(self.sprite_sheet, animation_rects, self.buster_sheet, buster_rects)
        
        # Define som de disparo para o jogador
        self.player.shoot_sound = getattr(self, 'shoot_sound', None)
        
        # Grupo de projéteis
        self.projectiles = pygame.sprite.Group()
        self.player.projectiles = self.projectiles

    def _setup_audio(self):
        """Configura o áudio do jogo."""
        try:
            bgm_path = Path(__file__).parent.parent / 'assets' / 'bgm' / 'bgm.mp3'
            if bgm_path.exists():
                pygame.mixer.init()
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f'[BGM] Falha ao carregar bgm.mp3: {e}')

    def _reset_game(self):
        """Reinicia o jogo."""
        self.distance = 0.0
        self.start_time = pygame.time.get_ticks()
        self.total_time = 0
        
        if self.player:
            # Reinicializa o jogador
            self.player.world_x = 0.0
            self.player.velocity_x = 0.0
            self.player.velocity_y = 0.0
            self.player.rect.midbottom = (WINDOW_WIDTH // 2, GROUND_Y)
            self.player.is_on_ground = True
            self.player.facing_direction = 1
            
        if self.camera:
            self.camera.x = 0.0
            
        if self.projectiles:
            self.projectiles.empty()

    def _update_input_detection(self):
        """Atualiza sistema de detecção de teclas pressionadas."""
        current_keys = pygame.key.get_pressed()
        
        # Detecta teclas que foram pressionadas neste frame
        self.key_pressed = {}
        
        # Lista das teclas que queremos monitorar
        keys_to_monitor = [
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_z, pygame.K_x, pygame.K_a
        ]
        
        for key in keys_to_monitor:
            self.key_pressed[key] = current_keys[key] and not self.previous_keys[key]
        
        # Debug das teclas de seta
        if self.key_pressed.get(pygame.K_UP, False):
            print("[DEBUG] Tecla UP detectada!")
        if self.key_pressed.get(pygame.K_DOWN, False):
            print("[DEBUG] Tecla DOWN detectada!")
        if self.key_pressed.get(pygame.K_RETURN, False):
            print("[DEBUG] Tecla ENTER detectada!")
        
        self.previous_keys = current_keys

    def _check_game_over_conditions(self):
        """Verifica condições de game over."""
        if self.player:
            # Game over se cair muito abaixo do chão
            if self.player.rect.top > WINDOW_HEIGHT + 100:
                return True
        return False

    def handle_events(self):
        """Processa os eventos do jogo."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_menu_state(self, keys):
        """Gerencia o estado do menu."""
        action = self.menu_screen.handle_input(keys, self.key_pressed)
        
        if action == "start_game":
            self._initialize_game_components()
            self._reset_game()
            self.start_time = pygame.time.get_ticks()
            self.state_manager.change_state(GameState.PLAYING)
        elif action == "quit":
            self.running = False

    def handle_playing_state(self, dt, keys):
        """Gerencia o estado de jogo."""
        # Verifica pause
        if self.key_pressed.get(pygame.K_ESCAPE, False):
            # Captura a tela atual para o pause
            self.game_surface = self.screen.copy()
            self.state_manager.change_state(GameState.PAUSED)
            return
        
        # Atualiza jogador
        self.player.update(dt, keys)
        
        # Atualiza câmera
        self.camera.update(self.player)
        
        # Atualiza projéteis
        self.projectiles.update(dt, self.camera.get_x())
        
        # Atualiza distância e tempo
        self.distance = self.player.world_x
        self.total_time = pygame.time.get_ticks() - self.start_time
        
        # Verifica game over
        if self._check_game_over_conditions():
            self.game_over_screen.set_stats(self.distance, self.total_time)
            self.state_manager.change_state(GameState.GAME_OVER)

    def handle_paused_state(self, keys):
        """Gerencia o estado de pause."""
        action = self.pause_screen.handle_input(keys, self.key_pressed)
        
        if action == "resume":
            self.state_manager.change_state(GameState.PLAYING)
        elif action == "restart":
            self._reset_game()
            self.start_time = pygame.time.get_ticks()
            self.state_manager.change_state(GameState.PLAYING)
        elif action == "menu":
            self.state_manager.change_state(GameState.MENU)

    def handle_game_over_state(self, keys):
        """Gerencia o estado de game over."""
        action = self.game_over_screen.handle_input(keys, self.key_pressed)
        
        if action == "restart":
            self._reset_game()
            self.start_time = pygame.time.get_ticks()
            self.state_manager.change_state(GameState.PLAYING)
        elif action == "menu":
            self.state_manager.change_state(GameState.MENU)

    def update(self, dt, keys):
        """Atualiza o jogo baseado no estado atual."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == GameState.MENU:
            self.handle_menu_state(keys)
        elif current_state == GameState.PLAYING:
            self.handle_playing_state(dt, keys)
        elif current_state == GameState.PAUSED:
            self.handle_paused_state(keys)
        elif current_state == GameState.GAME_OVER:
            self.handle_game_over_state(keys)

    def render(self):
        """Renderiza baseado no estado atual."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == GameState.MENU:
            self.menu_screen.render()
        elif current_state == GameState.PLAYING:
            # Renderização normal do jogo
            self.renderer.clear_screen()
            self.renderer.draw_background(self.background, self.camera.get_x())
            self.renderer.draw_ground(self.camera.get_x())
            self.renderer.draw_player(self.player)
            self.renderer.draw_projectiles(self.projectiles)
            self.renderer.draw_hud(self.distance)
        elif current_state == GameState.PAUSED:
            self.pause_screen.render(self.game_surface)
        elif current_state == GameState.GAME_OVER:
            self.game_over_screen.render()
        
        pygame.display.flip()

    def run(self):
        """Loop principal do jogo."""
        while self.running:
            dt = self.clock.tick(FPS)
            
            self._update_input_detection()
            keys = pygame.key.get_pressed()
            
            self.handle_events()
            self.update(dt, keys)
            self.render()

        pygame.quit()
        sys.exit()