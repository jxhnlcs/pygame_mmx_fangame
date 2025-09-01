import pygame
import random
from config.settings import *
from entities.projectile import EnemyProjectile


class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, world_x, sprite_sheet, projectile_image, shoot_sound=None, death_sound=None):
        super().__init__()
        self.world_x = world_x
        self.world_y = GROUND_Y
        self.sprite_sheet = sprite_sheet
        self.projectile_image = projectile_image
        
        # ADICIONADO: Sons do inimigo
        self.shoot_sound = shoot_sound
        self.death_sound = death_sound
        
        self.health = 10
        self.max_health = 10
        self.is_alive = True
        self.has_seen_player = False
        
        self.animation_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150
        
        self.shoot_timer = 0
        self.shoot_cooldown = 2000
        self.can_shoot = False
        
        # MODIFICADO: Sistema de tiro completamente aleatório
        self.shot_heights = ["ground", "low", "mid", "high"]
        
        # ADICIONADO: Sistema de velocidades variadas
        self.shot_speeds = {
            "slow": 3.0,     # Velocidade mínima
            "normal": 5.0,   # Velocidade normal (aumentada)
            "fast": 7.0,     # Velocidade rápida (aumentada)
            "very_fast": 9.0 # Velocidade muito rápida (aumentada)
        }
        
        # MODIFICADO: Probabilidades ajustadas para mais ação
        self.speed_probabilities = [
            ("slow", 15),      # 15% chance de tiro lento (era 40%)
            ("normal", 35),    # 35% chance de tiro normal
            ("fast", 35),      # 35% chance de tiro rápido (era 20%)
            ("very_fast", 15)  # 15% chance de tiro muito rápido (era 5%)
        ]
        
        self._load_animations()
        
        self.image = self.animation_frames[0] if self.animation_frames else pygame.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = self.world_y
        
        self.projectiles = None

    def _load_animations(self):
        frame_rects = [
            (4, 1, 47, 61),    
            (144, 1, 47, 61),   
            (191, 1, 47, 61),   
            (284, 1, 53, 32),   
            (7, 75, 53, 62),  
            (70, 75, 53, 64),  
            (133, 75, 45, 64),  
        ]
        
        for i, rect in enumerate(frame_rects):
            try:
                x, y, w, h = rect
                if (x + w <= self.sprite_sheet.get_width() and 
                    y + h <= self.sprite_sheet.get_height()):
                    
                    frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
                    
                    frame.set_colorkey((255, 255, 255))
                    frame = frame.convert_alpha()
                    
                    scaled_frame = pygame.transform.scale(frame, (w * SPRITE_SCALE, h * SPRITE_SCALE))
                    self.animation_frames.append(scaled_frame)
                else:
                    raise Exception(f"Frame {i+1} fora dos limites da sprite sheet")
                    
            except Exception as e:
                temp_frame = pygame.Surface((32 * SPRITE_SCALE, 32 * SPRITE_SCALE), pygame.SRCALPHA)
                temp_frame.fill((0, 0, 0, 0))
                
                center_x, center_y = 16 * SPRITE_SCALE, 16 * SPRITE_SCALE
                pygame.draw.circle(temp_frame, (100, 100, 200), (center_x, center_y), 12 * SPRITE_SCALE)
                pygame.draw.rect(temp_frame, (80, 80, 180), 
                            (center_x - 8 * SPRITE_SCALE, center_y + 8 * SPRITE_SCALE, 
                                16 * SPRITE_SCALE, 8 * SPRITE_SCALE))
                
                self.animation_frames.append(temp_frame)
    
    def update_screen_position(self, camera_x):
        self.rect.centerx = int(self.world_x - camera_x)
        self.rect.bottom = int(self.world_y)
    
    def is_visible_on_screen(self, camera_x):
        screen_x = self.world_x - camera_x
        return -100 < screen_x < WINDOW_WIDTH + 100
    
    def check_player_visibility(self, player_world_x, camera_x):
        if not self.has_seen_player and self.is_visible_on_screen(camera_x):
            distance_to_player = abs(player_world_x - self.world_x)
            if distance_to_player < 500:
                self.has_seen_player = True
                self.can_shoot = True
                self.shoot_timer = 0

    def _get_random_shot_height(self):
        """Retorna uma altura de tiro completamente aleatória."""
        shot_type = random.choice(self.shot_heights)
        
        if shot_type == "ground":
            # Tiro no nível do chão - player precisa pular
            return GROUND_Y - 15
        elif shot_type == "low":
            # Tiro baixo - dash pode passar por baixo
            return GROUND_Y - 35
        elif shot_type == "mid":
            # Tiro médio - pulo pequeno ou dash
            return GROUND_Y - 55
        elif shot_type == "high":
            # Tiro alto - dash passa por baixo com folga
            return GROUND_Y - 75
        else:
            # Fallback
            return self.rect.centery

    def _get_random_shot_speed(self):
        """Retorna uma velocidade de tiro aleatória baseada nas probabilidades."""
        # Gera um número aleatório de 0 a 100
        rand_num = random.randint(1, 100)
        
        # Calcula as faixas baseadas nas probabilidades
        cumulative = 0
        for speed_type, probability in self.speed_probabilities:
            cumulative += probability
            if rand_num <= cumulative:
                return self.shot_speeds[speed_type]
        
        # Fallback para velocidade lenta
        return self.shot_speeds["slow"]

    def shoot_at_player(self, player_world_x, player_screen_y):
        if not self.can_shoot or not self.is_alive:
            return
        
        # ADICIONADO: Toca som de disparo
        if self.shoot_sound:
            try:
                self.shoot_sound.play()
            except Exception as e:
                print(f"Erro ao tocar som de disparo do inimigo: {e}")
        
        direction_x = 1 if player_world_x > self.world_x else -1
        
        projectile_world_x = self.world_x + (20 * SPRITE_SCALE * direction_x)
        
        # MODIFICADO: Altura e velocidade completamente aleatórias
        projectile_screen_y = self._get_random_shot_height()
        projectile_speed = self._get_random_shot_speed()
        
        # MODIFICADO: Cria projétil com velocidade personalizada
        projectile = EnemyProjectile(
            self.projectile_image, 
            projectile_world_x, 
            projectile_screen_y, 
            direction_x,
            speed=projectile_speed  # Passa a velocidade customizada
        )
        
        if self.projectiles is not None:
            self.projectiles.add(projectile)
        
        self.shoot_timer = self.shoot_cooldown
    
    def take_damage(self, damage=1):
        if not self.is_alive:
            return False
            
        self.health -= damage
        
        if self.health <= 0:
            self.is_alive = False
            
            # ADICIONADO: Toca som de morte
            if self.death_sound:
                try:
                    self.death_sound.play()
                except Exception as e:
                    print(f"Erro ao tocar som de morte do inimigo: {e}")
            
            return True
        
        return False
    
    def update(self, dt, player_world_x, player_screen_y, camera_x):
        if not self.is_alive:
            return
        
        self.update_screen_position(camera_x)
        
        self.check_player_visibility(player_world_x, camera_x)
        
        if self.has_seen_player:
            previous_frame = self.current_frame
            
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.image = self.animation_frames[self.current_frame]
                
                if self.current_frame == 5 and previous_frame != 5:
                    if self.can_shoot and self.shoot_timer <= 0 and self.is_visible_on_screen(camera_x):
                        self.shoot_at_player(player_world_x, player_screen_y)
            
            if self.shoot_timer > 0:
                self.shoot_timer -= dt
    
    def check_collision_with_projectile(self, projectile_rect):
        return self.rect.colliderect(projectile_rect)
    
    def render(self, screen):
        if self.is_alive:
            screen.blit(self.image, self.rect)
            
            if self.health < self.max_health:
                self._draw_health_bar(screen)
    
    def _draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 10
        
        pygame.draw.rect(screen, (200, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (50, 200, 50), 
                        (bar_x, bar_y, int(bar_width * health_ratio), bar_height))


class EnemyManager:
    
    def __init__(self, sprite_sheet, projectile_image, shoot_sound=None, death_sound=None):
        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.sprite_sheet = sprite_sheet
        self.projectile_image = projectile_image
        
        # ADICIONADO: Sons para inimigos
        self.shoot_sound = shoot_sound
        self.death_sound = death_sound
        
        self.spawn_distance = 600
        self.last_spawn_x = 800
        
    def spawn_enemy(self, world_x):
        # MODIFICADO: Passa sons para o inimigo
        enemy = Enemy(
            world_x, 
            self.sprite_sheet, 
            self.projectile_image,
            shoot_sound=self.shoot_sound,
            death_sound=self.death_sound
        )
        enemy.projectiles = self.enemy_projectiles
        self.enemies.add(enemy)
    
    def update(self, dt, player_world_x, player_screen_y, camera_x, player_projectiles):
        if player_world_x > self.last_spawn_x - 1000:
            self.spawn_enemy(self.last_spawn_x)
            self.last_spawn_x += self.spawn_distance + random.randint(-200, 200)
        
        for enemy in self.enemies.sprites():
            # REVERTIDO: Volta para player_screen_y
            enemy.update(dt, player_world_x, player_screen_y, camera_x)
            
            if enemy.world_x < player_world_x - 1000:
                enemy.kill()
        
        self.enemy_projectiles.update(dt, camera_x)
        
        self._check_player_projectile_collisions(player_projectiles)
        
        for enemy in self.enemies.sprites():
            if not enemy.is_alive:
                enemy.kill()
    
    def _check_player_projectile_collisions(self, player_projectiles):
        for projectile in player_projectiles.sprites():
            for enemy in self.enemies.sprites():
                if enemy.is_alive and enemy.check_collision_with_projectile(projectile.rect):
                    enemy.take_damage(1)
                    projectile.kill()
                    break
    
    def check_enemy_projectile_collision(self, player_rect):
        for projectile in self.enemy_projectiles.sprites():
            if projectile.rect.colliderect(player_rect):
                projectile.kill()
                return True
        return False
    
    def render(self, screen, camera_x):
        for enemy in self.enemies.sprites():
            if enemy.is_visible_on_screen(camera_x):
                enemy.render(screen)
        
        self.enemy_projectiles.draw(screen)
    
    def _create_temp_powerup_sprites(self):
        """Cria sprites temporários para os power-ups."""
        sprite_sheet = pygame.Surface((96, 32))
        sprite_sheet.set_colorkey(MAGENTA_COLORKEY)
        sprite_sheet.fill(MAGENTA_COLORKEY)
        
        # Power-up de vida (vermelho)
        pygame.draw.rect(sprite_sheet, (255, 100, 100), (0, 0, 32, 32))
        pygame.draw.rect(sprite_sheet, (255, 255, 255), (0, 0, 32, 32), 2)
        # Adiciona símbolo de cruz para vida
        pygame.draw.rect(sprite_sheet, (255, 255, 255), (14, 8, 4, 16))  # Vertical
        pygame.draw.rect(sprite_sheet, (255, 255, 255), (8, 14, 16, 4))  # Horizontal
        
        # Power-up de tiro rápido (azul)
        pygame.draw.rect(sprite_sheet, (100, 100, 255), (32, 0, 32, 32))
        pygame.draw.rect(sprite_sheet, (255, 255, 255), (32, 0, 32, 32), 2)
        # Adiciona símbolo de projétil
        pygame.draw.circle(sprite_sheet, (255, 255, 255), (48, 16), 6)
        
        # Power-up de escudo (amarelo)
        pygame.draw.rect(sprite_sheet, (255, 255, 100), (64, 0, 32, 32))
        pygame.draw.rect(sprite_sheet, (255, 255, 255), (64, 0, 32, 32), 2)
        # Adiciona símbolo de escudo
        pygame.draw.circle(sprite_sheet, (255, 255, 255), (80, 16), 8, 3)
        
        return sprite_sheet