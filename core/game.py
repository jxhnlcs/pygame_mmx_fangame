import pygame
import sys
from pathlib import Path

from config.settings import *
from entities.player import Player
from graphics.camera import Camera
from graphics.renderer import GameRenderer
from core.game_states import StateManager, GameState, MenuScreen, PauseScreen, GameOverScreen
from entities.enemies import EnemyManager
from entities.powerups import PowerUpManager

class Game:
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        self.state_manager = StateManager()
        self.menu_screen = MenuScreen(self.screen)
        self.pause_screen = PauseScreen(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        
        self.previous_keys = pygame.key.get_pressed()
        self.key_pressed = {}
        
        self.distance = 0.0
        self.start_time = 0
        self.total_time = 0
        self.running = True
        self.game_surface = None
        
        self.camera = None
        self.renderer = None
        self.player = None
        self.projectiles = None
        self.enemy_manager = None
        self.powerup_manager = None  # ADICIONADO
        self.sprite_sheet = None
        self.buster_sheet = None
        self.enemy_sheet = None
        self.enemy_projectile_image = None
        self.powerup_sprite_sheet = None  # ADICIONADO
        self.background = None
        self.shoot_sound = None

    def _initialize_game_components(self):
        if self.camera is None:
            self.camera = Camera()
            self.renderer = GameRenderer(self.screen)
            self._load_assets()
            self._create_entities()
            self._setup_audio()
            
            self.enemy_manager = EnemyManager(self.enemy_sheet, self.enemy_projectile_image)
            # ADICIONADO: Inicializa manager de power-ups
            self.powerup_manager = PowerUpManager(self.powerup_sprite_sheet)

    def _load_assets(self):
        sheet_path = Path(__file__).parent.parent / "assets" / "spritesheets" / "mmx_xsheet.png"
        self.sprite_sheet = pygame.image.load(str(sheet_path)).convert()
        self.sprite_sheet.set_colorkey(MAGENTA_COLORKEY)
        
        buster_path = Path(__file__).parent.parent / "assets" / "spritesheets" / "mmx1-buster.png"
        self.buster_sheet = pygame.image.load(str(buster_path)).convert_alpha()
        
        # ADICIONADO: Carrega sprite sheet dos power-ups
        powerup_path = Path(__file__).parent.parent / "assets" / "spritesheets" / "mmx1_items.png"
        try:
            self.powerup_sprite_sheet = pygame.image.load(str(powerup_path)).convert_alpha()
        except:
            # Se não encontrar, cria sprites temporários
            self.powerup_sprite_sheet = self._create_temp_powerup_sprites()
        
        self._load_enemy_assets()
        self._load_sound_effects()
        
        try:
            bg_path = Path(__file__).parent.parent / "assets" / "background.png"
            if bg_path.exists():
                self.background = pygame.image.load(str(bg_path)).convert()
            else:
                self.background = None
        except Exception as e:
            self.background = None

    def _load_enemy_assets(self):
        try:
            enemy_path = Path(__file__).parent.parent / "assets" / "spritesheets" / "enemy_sheet.png"
            
            if enemy_path.exists():
                self.enemy_sheet = pygame.image.load(str(enemy_path)).convert()
                self.enemy_sheet.set_colorkey(MAGENTA_COLORKEY)
            else:
                self.enemy_sheet = self._create_temp_enemy_sprite()
            
            self.enemy_projectile_image = self._create_enemy_projectile_image()
            
        except Exception as e:
            self.enemy_sheet = self._create_temp_enemy_sprite()
            self.enemy_projectile_image = self._create_enemy_projectile_image()

    def _create_temp_enemy_sprite(self):
        sheet = pygame.Surface((224, 32))
        sheet.fill(MAGENTA_COLORKEY)
        sheet.set_colorkey(MAGENTA_COLORKEY)
        
        for i in range(7):
            x = i * 32
            color = (100 + i * 20, 100 + i * 10, 200)
            pygame.draw.circle(sheet, color, (x + 16, 16), 12)
            pygame.draw.rect(sheet, (80, 80, 180), (x + 8, 20, 16, 8))
        
        return sheet

    def _create_enemy_projectile_image(self):
        projectile = pygame.Surface((12, 12))
        projectile.fill(MAGENTA_COLORKEY)
        projectile.set_colorkey(MAGENTA_COLORKEY)
        pygame.draw.circle(projectile, (255, 150, 50), (6, 6), 5)
        pygame.draw.circle(projectile, (255, 200, 100), (6, 6), 3)
        return pygame.transform.scale(projectile, (12 * 2, 12 * 2))

    def _load_sound_effects(self):
        try:
            pygame.mixer.init()
            
            sound_effects_path = Path(__file__).parent.parent / "assets" / "sound-effects"
            
            shoot_sound_path = sound_effects_path / "shoots"
            sound_files = list(shoot_sound_path.glob("*.wav")) + list(shoot_sound_path.glob("*.mp3"))
            
            if sound_files:
                self.shoot_sound = pygame.mixer.Sound(str(sound_files[0]))
            else:
                self.shoot_sound = None
            
            damage_sound_path = sound_effects_path / "damage"
            damage_sound_files = list(damage_sound_path.glob("hurt*.wav")) + list(damage_sound_path.glob("hurt*.mp3"))
            if damage_sound_files:
                self.damage_sound = pygame.mixer.Sound(str(damage_sound_files[0]))
            else:
                self.damage_sound = None
            
            death_sound_files = list(damage_sound_path.glob("die*.wav")) + list(damage_sound_path.glob("die*.mp3"))
            if death_sound_files:
                self.death_sound = pygame.mixer.Sound(str(death_sound_files[0]))
            else:
                self.death_sound = None
                
        except Exception as e:
            self.shoot_sound = None
            self.damage_sound = None
            self.death_sound = None

    def _create_entities(self):
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
            'idle': (321, 15, 36, 36),
            'damage': [(39, 702, 24, 37), (64, 701, 26, 37), (91, 696, 37, 46), (64, 701, 26, 37), (91, 696, 37, 46)]
        }
        
        buster_rects = {
            'pellet': (61, 3, 10, 8)
        }

        self.player = Player(self.sprite_sheet, animation_rects, self.buster_sheet, buster_rects)
        
        self.player.shoot_sound = getattr(self, 'shoot_sound', None)
        self.player.damage_sound = getattr(self, 'damage_sound', None)
        self.player.death_sound = getattr(self, 'death_sound', None)
        
        self.projectiles = pygame.sprite.Group()
        self.player.projectiles = self.projectiles

    def _setup_audio(self):
        try:
            bgm_path = Path(__file__).parent.parent / 'assets' / 'bgm' / 'bgm.mp3'
            if bgm_path.exists():
                pygame.mixer.init()
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.play(-1)
        except Exception as e:
            pass

    def _reset_game(self):
        self.distance = 0.0
        self.start_time = pygame.time.get_ticks()
        self.total_time = 0
        
        if self.player:
            self.player.world_x = 0.0
            self.player.velocity_x = 0.0
            self.player.velocity_y = 0.0
            self.player.rect.midbottom = (WINDOW_WIDTH // 2, GROUND_Y)
            self.player.is_on_ground = True
            self.player.facing_direction = 1
            self.player.reset_health()
            
        if self.camera:
            self.camera.x = 0.0
            
        if self.projectiles:
            self.projectiles.empty()
            
        if self.enemy_manager:
            self.enemy_manager = EnemyManager(self.enemy_sheet, self.enemy_projectile_image)
        
        # ADICIONADO: Reset do manager de power-ups
        if self.powerup_manager:
            self.powerup_manager = PowerUpManager(self.powerup_sprite_sheet)

    def _update_input_detection(self):
        current_keys = pygame.key.get_pressed()
        
        self.key_pressed = {}
        
        keys_to_monitor = [
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_z, pygame.K_x, pygame.K_a
        ]
        
        for key in keys_to_monitor:
            self.key_pressed[key] = current_keys[key] and not self.previous_keys[key]
        
        self.previous_keys = current_keys

    def _check_game_over_conditions(self):
        if not self.player or not self.player.is_alive:
            return True
            
        if self.enemy_manager:
            if self.enemy_manager.check_enemy_projectile_collision(self.player.rect):
                died = self.player.take_damage(4)
                return died
                
            if self.player.rect.top > WINDOW_HEIGHT + 100:
                self.player.is_alive = False
                return True
                
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_menu_state(self, keys):
        action = self.menu_screen.handle_input(keys, self.key_pressed)
        
        if action == "start_game":
            self._initialize_game_components()
            self._reset_game()
            self.start_time = pygame.time.get_ticks()
            self.state_manager.change_state(GameState.PLAYING)
        elif action == "quit":
            self.running = False

    def handle_playing_state(self, dt, keys):
        if self.key_pressed.get(pygame.K_ESCAPE, False):
            self.game_surface = self.screen.copy()
            self.state_manager.change_state(GameState.PAUSED)
            return
        
        self.player.update(dt, keys)
        self.camera.update(self.player)
        self.projectiles.update(dt, self.camera.get_x())
        
        self.enemy_manager.update(dt, self.player.world_x, self.player.rect.centery, 
                                 self.camera.get_x(), self.projectiles)
        
        # ADICIONADO: Atualiza power-ups
        self.powerup_manager.update(dt, self.player.world_x, self.camera.get_x())
        
        # ADICIONADO: Verifica colisões com power-ups
        powerup_messages = self.powerup_manager.check_player_collision(self.player)
        
        self.distance = self.player.world_x
        self.total_time = pygame.time.get_ticks() - self.start_time
        
        if self._check_game_over_conditions():
            self.game_over_screen.set_stats(self.distance, self.total_time)
            self.state_manager.change_state(GameState.GAME_OVER)

    def handle_paused_state(self, keys):
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
        action = self.game_over_screen.handle_input(keys, self.key_pressed)
        
        if action == "restart":
            self._reset_game()
            self.start_time = pygame.time.get_ticks()
            self.state_manager.change_state(GameState.PLAYING)
        elif action == "menu":
            self.state_manager.change_state(GameState.MENU)

    def update(self, dt, keys):
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
        current_state = self.state_manager.get_current_state()
        
        if current_state == GameState.MENU:
            self.menu_screen.render()
        elif current_state == GameState.PLAYING:
            self.renderer.clear_screen()
            self.renderer.draw_background(self.background, self.camera.get_x())
            self.renderer.draw_ground(self.camera.get_x())
            
            self.enemy_manager.render(self.screen, self.camera.get_x())
            
            # ADICIONADO: Desenha power-ups
            self.powerup_manager.draw(self.screen)
            
            self.renderer.draw_player(self.player)
            self.renderer.draw_projectiles(self.projectiles)
            self.renderer.draw_hud(self.distance, self.player)
            
        elif current_state == GameState.PAUSED:
            self.pause_screen.render(self.game_surface)
        elif current_state == GameState.GAME_OVER:
            self.game_over_screen.render()
    
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            
            self._update_input_detection()
            keys = pygame.key.get_pressed()
            
            self.handle_events()
            self.update(dt, keys)
            self.render()

        pygame.quit()
        sys.exit()