"""Classe do projétil (pellet)"""
import pygame
from config.settings import WINDOW_WIDTH, PELLET_SPEED


class Pellet(pygame.sprite.Sprite):
    """Projétil disparado pelo jogador."""
    
    def __init__(self, image, world_x, screen_y, direction):
        super().__init__()
        self.image = image
        self.velocity_x = PELLET_SPEED * direction
        self.world_x = world_x
        self.screen_y = screen_y
        self.rect = self.image.get_rect()

    def update(self, dt, camera_x):
        """Atualiza a posição do projétil."""
        self.world_x += self.velocity_x
        
        # Converte para posição na tela
        self.rect.centerx = int(self.world_x - camera_x)
        self.rect.centery = int(self.screen_y)
        
        # Remove se saiu da tela
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()