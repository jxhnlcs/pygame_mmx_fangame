"""Classe principal do jogo"""
import pygame
import sys
from pathlib import Path

from config.settings import *
from entities.player import Player
from graphics.camera import Camera
from graphics.renderer import GameRenderer


class Game:
    """Classe principal que gerencia o jogo."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        self.camera = Camera()
        self.renderer = GameRenderer(self.screen)
        
        self._load_assets()
        self._create_entities()
        self._setup_audio()
        
        self.distance = 0.0
        self.running = True

    def _load_assets(self):
        """Carrega todos os recursos do jogo."""
        # Carrega sprite sheet
        sheet_path = Path(__file__).parent.parent / "assets" / "mmx_xsheet.png"
        self.sprite_sheet = pygame.image.load(str(sheet_path)).convert()
        self.sprite_sheet.set_colorkey(MAGENTA_COLORKEY)

    def _create_entities(self):
        """Cria as entidades do jogo."""
        # Define os retângulos das animações
        animation_rects = {
            'run': [(106, 108, 30, 33), (137, 108, 20, 33), (158, 108, 23, 33), 
                   (181, 108, 32, 33), (213, 108, 34, 33), (247, 108, 26, 33), 
                   (276, 108, 22, 33), (298, 108, 25, 33), (326, 108, 30, 33), 
                   (357, 108, 34, 33), (391, 108, 29, 33)],
            'jump': [(168, 66, 29, 34), (202, 63, 24, 37), (231, 61, 15, 39), 
                    (253, 61, 18, 39), (274, 61, 23, 39), (299, 61, 27, 39), 
                    (331, 62, 24, 38), (356, 68, 30, 32)],
            'dash': [(317, 163, 38, 26), (361, 158, 38, 31)],
            'shoot': [(133, 66, 30, 34), (168, 66, 29, 34)],
            'pellet': (112, 73, 14, 3)
        }

        # Cria o jogador
        self.player = Player(self.sprite_sheet, animation_rects)
        
        # Grupo de projéteis
        self.projectiles = pygame.sprite.Group()
        self.player.projectiles = self.projectiles

    def _setup_audio(self):
        """Configura o áudio do jogo."""
        try:
            bgm_path = Path(__file__).parent.parent / 'assets' / 'bgm.mp3'
            if bgm_path.exists():
                pygame.mixer.init()
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f'[BGM] Falha ao carregar bgm.mp3: {e}')

    def handle_events(self):
        """Processa os eventos do jogo."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt, keys):
        """Atualiza todos os elementos do jogo."""
        # Atualiza jogador
        self.player.update(dt, keys)
        
        # Atualiza câmera
        self.camera.update(self.player)
        
        # Atualiza projéteis
        self.projectiles.update(dt, self.camera.get_x())
        
        # Atualiza distância
        self.distance = self.player.world_x
        
        # Verifica se deve sair
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def render(self):
        """Renderiza todos os elementos do jogo."""
        self.renderer.clear_screen()
        self.renderer.draw_ground(self.camera.get_x())
        self.renderer.draw_player(self.player)
        self.renderer.draw_projectiles(self.projectiles)
        self.renderer.draw_hud(self.distance)
        
        pygame.display.flip()

    def run(self):
        """Loop principal do jogo."""
        while self.running:
            dt = self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            
            self.handle_events()
            self.update(dt, keys)
            self.render()

        pygame.quit()
        sys.exit()