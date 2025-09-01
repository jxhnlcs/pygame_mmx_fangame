import pygame
import random
import math  # ADICIONADO: Import do módulo math
from config.settings import *

class PowerUpType:
    HEALTH = "health"
    RAPID_FIRE = "rapid_fire"
    SHIELD = "shield"

class PowerUp(pygame.sprite.Sprite):
    
    def __init__(self, world_x, powerup_type, sprite_sheet):
        super().__init__()
        self.world_x = world_x
        self.world_y = GROUND_Y - 40  # Fica 40px acima do chão
        self.powerup_type = powerup_type
        self.sprite_sheet = sprite_sheet
        
        # Animação de flutuação
        self.float_timer = 0
        self.float_amplitude = 8  # Pixels de movimento vertical
        self.float_speed = 0.003  # Velocidade da flutuação
        self.base_y = self.world_y
        
        # Efeito de brilho
        self.glow_timer = 0
        self.glow_speed = 0.005
        
        # Carrega sprite baseado no tipo (coordenadas temporárias)
        self._load_sprite()
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.centery = self.world_y
        
        # Duração do power-up (para alguns tipos)
        self.duration = 0
        self.is_active = False
    
    def _load_sprite(self):
        """Carrega o sprite baseado no tipo de power-up."""
        # Coordenadas temporárias - você pode ajustar depois
        sprite_coords = {
            PowerUpType.HEALTH: (7, 81, 17, 17),      # Vermelho - vida
            PowerUpType.RAPID_FIRE: (15, 64, 15, 15), # Azul - tiro rápido
            PowerUpType.SHIELD: (21, 35, 19, 15)      # Amarelo - escudo
        }
        
        x, y, w, h = sprite_coords.get(self.powerup_type, (0, 0, 32, 32))
        
        # Cria um sprite temporário colorido se não conseguir carregar
        try:
            self.image = self.sprite_sheet.subsurface((x, y, w, h))
            self.image = pygame.transform.scale(self.image, (w * SPRITE_SCALE, h * SPRITE_SCALE))
        except:
            # Sprite temporário colorido
            self.image = pygame.Surface((32 * SPRITE_SCALE, 32 * SPRITE_SCALE))
            color = self._get_temp_color()
            self.image.fill(color)
            # Adiciona uma borda
            pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 2)
    
    def _get_temp_color(self):
        """Retorna cor temporária baseada no tipo."""
        colors = {
            PowerUpType.HEALTH: (255, 100, 100),     # Vermelho
            PowerUpType.RAPID_FIRE: (100, 100, 255), # Azul
            PowerUpType.SHIELD: (255, 255, 100)      # Amarelo
        }
        return colors.get(self.powerup_type, (200, 200, 200))
    
    def update(self, dt, camera_x):
        """Atualiza a animação e posição do power-up."""
        # Animação de flutuação - CORRIGIDO: Usa math.sin em vez de pygame.math.sin
        self.float_timer += dt * self.float_speed
        float_offset_y = math.sin(self.float_timer) * self.float_amplitude
        self.world_y = self.base_y + float_offset_y
        
        # Atualiza posição na tela
        self.rect.centerx = int(self.world_x - camera_x)
        self.rect.centery = int(self.world_y)
        
        # Efeito de brilho (opcional)
        self.glow_timer += dt * self.glow_speed
        
        # Remove se saiu da tela
        if self.rect.right < -100 or self.rect.left > WINDOW_WIDTH + 100:
            self.kill()
    
    def apply_effect(self, player):
        """Aplica o efeito do power-up no jogador."""
        if self.powerup_type == PowerUpType.HEALTH:
            # Recupera 2 de vida
            player.heal(2)
            return f"+2 VIDA!"
            
        elif self.powerup_type == PowerUpType.RAPID_FIRE:
            # Tiro rápido por 10 segundos
            player.activate_rapid_fire(10000)  # 10 segundos em ms
            return "TIRO RÁPIDO!"
            
        elif self.powerup_type == PowerUpType.SHIELD:
            # Escudo por 15 segundos
            player.activate_shield(15000)  # 15 segundos em ms
            return "ESCUDO ATIVO!"
        
        return "POWER-UP!"

class PowerUpManager:
    
    def __init__(self, sprite_sheet):
        self.powerups = pygame.sprite.Group()
        self.sprite_sheet = sprite_sheet
        
        # Controle de spawn
        self.spawn_distance = 800  # Distância entre power-ups
        self.last_spawn_x = 1000   # Posição do último spawn
        self.spawn_variation = 200 # Variação aleatória na distância
    
    def update(self, dt, player_world_x, camera_x):
        """Atualiza todos os power-ups."""
        # Spawn de novos power-ups
        if player_world_x > self.last_spawn_x - 600:
            self._spawn_random_powerup()
        
        # Atualiza power-ups existentes
        for powerup in self.powerups.sprites():
            powerup.update(dt, camera_x)
            
            # Remove power-ups muito atrás
            if powerup.world_x < player_world_x - 1000:
                powerup.kill()
    
    def _spawn_random_powerup(self):
        """Spawna um power-up aleatório."""
        # Escolhe tipo aleatório com probabilidades diferentes
        powerup_types = [
            (PowerUpType.HEALTH, 50),     # 50% chance de vida
            (PowerUpType.RAPID_FIRE, 30), # 30% chance de tiro rápido
            (PowerUpType.SHIELD, 20)      # 20% chance de escudo
        ]
        
        # Seleção baseada em probabilidade
        rand_num = random.randint(1, 100)
        cumulative = 0
        selected_type = PowerUpType.HEALTH
        
        for ptype, probability in powerup_types:
            cumulative += probability
            if rand_num <= cumulative:
                selected_type = ptype
                break
        
        # Cria o power-up
        spawn_x = self.last_spawn_x + random.randint(-self.spawn_variation, self.spawn_variation)
        powerup = PowerUp(spawn_x, selected_type, self.sprite_sheet)
        self.powerups.add(powerup)
        
        # Atualiza próxima posição de spawn
        self.last_spawn_x += self.spawn_distance + random.randint(-100, 100)
    
    def check_player_collision(self, player):
        """Verifica colisões entre player e power-ups."""
        collected_powerups = pygame.sprite.spritecollide(player, self.powerups, True)
        
        messages = []
        for powerup in collected_powerups:
            message = powerup.apply_effect(player)
            messages.append(message)
        
        return messages
    
    def draw(self, screen):
        """Desenha todos os power-ups."""
        for powerup in self.powerups.sprites():
            screen.blit(powerup.image, powerup.rect)