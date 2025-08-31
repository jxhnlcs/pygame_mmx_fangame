"""Classe dos projéteis do jogo"""
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


class EnemyProjectile(pygame.sprite.Sprite):
    
    def __init__(self, image, world_x, screen_y, direction, speed=3.0):  # MODIFICADO: Parâmetro speed adicionado
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        
        self.world_x = world_x
        self.rect.centery = screen_y
        
        # MODIFICADO: Velocidade customizável
        self.speed = speed
        self.direction = direction
        
        # ADICIONADO: Efeito visual baseado na velocidade
        self._apply_speed_visual_effect()
    
    def _apply_speed_visual_effect(self):
        """Aplica efeito visual baseado na velocidade do projétil."""
        if self.speed <= 3.5:
            # Projéteis lentos - cor normal (laranja)
            pass  # Mantém a cor original
        elif self.speed <= 5.0:
            # Projéteis normais - um pouco mais brilhante
            self._tint_image((255, 200, 100))
        elif self.speed <= 6.5:
            # Projéteis rápidos - cor vermelha
            self._tint_image((255, 100, 100))
        else:
            # Projéteis muito rápidos - cor branca brilhante
            self._tint_image((255, 255, 200))
    
    def _tint_image(self, color):
        """Aplica uma cor de matiz à imagem do projétil."""
        # Cria uma superfície colorida
        tinted = self.image.copy()
        color_surface = pygame.Surface(tinted.get_size())
        color_surface.fill(color)
        
        # Aplica o blend
        tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        self.image = tinted
    
    def update(self, dt, camera_x):
        # MODIFICADO: Usa velocidade customizada
        self.world_x += self.speed * self.direction
        
        # Atualiza posição na tela baseada na câmera
        self.rect.centerx = int(self.world_x - camera_x)
        
        # Remove projétil se saiu da tela
        if self.rect.right < -100 or self.rect.left > WINDOW_WIDTH + 100:
            self.kill()