"""Classe dos projéteis do jogo"""
import pygame
from config.settings import *


class Pellet(pygame.sprite.Sprite):
    """Projétil do jogador"""
    
    def __init__(self, image, world_x, screen_y, direction):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.centery = screen_y
        
        self.world_x = world_x
        self.direction = direction
        self.speed = PELLET_SPEED
        
    def update(self, dt, camera_x):
        # Movimento baseado na velocidade fixa
        movement = self.speed * (dt / 16.67)  # Normaliza para 60 FPS
        self.world_x += movement * self.direction
        
        # Atualiza posição na tela
        self.rect.centerx = int(self.world_x - camera_x)
        
        # Remove se saiu da tela
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()


class EnemyProjectile(pygame.sprite.Sprite):
    """Projétil do inimigo"""
    
    def __init__(self, image, world_x, screen_y, direction, speed=5.0):
        super().__init__()
        # MODIFICADO: Remove fundo colorido, usa apenas a imagem do projétil
        self.original_image = image.copy()
        self.image = self.original_image
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.centery = screen_y
        
        self.world_x = world_x
        self.world_y = screen_y
        self.direction = direction
        self.speed = speed  # Velocidade customizável
        
        # REMOVIDO: Todas as variáveis de cor de fundo
        # REMOVIDO: self.background_color
        # REMOVIDO: self.background_alpha
        # REMOVIDO: self.pulse_timer
        
    def update(self, dt, camera_x):
        # Movimento baseado na velocidade personalizada
        movement = self.speed * (dt / 16.67)  # Normaliza para 60 FPS
        self.world_x += movement * self.direction
        
        # Atualiza posição na tela
        self.rect.centerx = int(self.world_x - camera_x)
        self.rect.centery = int(self.world_y)
        
        # REMOVIDO: Todo o código de animação de cor de fundo
        # REMOVIDO: self.pulse_timer += dt
        # REMOVIDO: pulse_factor = ...
        # REMOVIDO: current_alpha = ...
        # REMOVIDO: background_surface = ...
        
        # Mantém apenas a imagem original do projétil
        self.image = self.original_image
        
        # Remove se saiu da tela
        if self.rect.right < -50 or self.rect.left > WINDOW_WIDTH + 50:
            self.kill()