"""Sistema de inimigos do jogo"""
import pygame
import random
from config.settings import *
from entities.projectile import EnemyProjectile


class Enemy(pygame.sprite.Sprite):
    """Inimigo que atira projéteis no jogador."""
    
    def __init__(self, world_x, sprite_sheet, projectile_image):
        super().__init__()
        self.world_x = world_x
        self.world_y = GROUND_Y
        self.sprite_sheet = sprite_sheet
        self.projectile_image = projectile_image
        
        # Estado do inimigo
        self.health = 10
        self.max_health = 10
        self.is_alive = True
        self.has_seen_player = False
        
        # Animação
        self.animation_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150  # ms por frame
        
        # Tiro - VALORES CORRIGIDOS
        self.shoot_timer = 0
        self.shoot_cooldown = 2000  # 2 segundos entre tiros
        self.can_shoot = False
        
        # Carrega animações
        self._load_animations()
        
        # Inicializa sprite
        self.image = self.animation_frames[0] if self.animation_frames else pygame.Surface((32, 32))
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2  # Será atualizado pela câmera
        self.rect.bottom = self.world_y
        
        # Grupo de projéteis (será definido externamente)
        self.projectiles = None
        print(f"[Enemy] Criado na posição {self.world_x}")
        
    def _load_animations(self):
        """Carrega as animações do inimigo."""
        # Coordenadas dos frames na sprite sheet
        frame_rects = [
            (4, 1, 47, 61),    # Frame 1
            (144, 1, 47, 61),   # Frame 2
            (191, 1, 47, 61),   # Frame 3
            (284, 1, 53, 32),   # Frame 4
            (7, 75, 53, 62),  # Frame 5
            (70, 75, 53, 64),  # Frame 6
            (133, 75, 45, 64),  # Frame 7
        ]
        
        # Extrai e escala os frames
        for i, rect in enumerate(frame_rects):
            try:
                x, y, w, h = rect
                # Verifica se o frame está dentro dos limites da sprite sheet
                if (x + w <= self.sprite_sheet.get_width() and 
                    y + h <= self.sprite_sheet.get_height()):
                    
                    frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
                    
                    # CORREÇÃO: Remove fundo branco e converte para alpha
                    frame.set_colorkey((255, 255, 255))  # Remove fundo branco
                    frame = frame.convert_alpha()
                    
                    # Escala o frame
                    scaled_frame = pygame.transform.scale(frame, (w * SPRITE_SCALE, h * SPRITE_SCALE))
                    self.animation_frames.append(scaled_frame)
                else:
                    # Frame fora dos limites, cria frame temporário
                    raise Exception(f"Frame {i+1} fora dos limites da sprite sheet")
                    
            except Exception as e:
                print(f"[Enemy] Erro no frame {i+1}: {e}")
                # Frame temporário melhorado SEM fundo branco
                temp_frame = pygame.Surface((32 * SPRITE_SCALE, 32 * SPRITE_SCALE), pygame.SRCALPHA)
                temp_frame.fill((0, 0, 0, 0))  # Totalmente transparente
                
                # Desenha um robô simples
                center_x, center_y = 16 * SPRITE_SCALE, 16 * SPRITE_SCALE
                pygame.draw.circle(temp_frame, (100, 100, 200), (center_x, center_y), 12 * SPRITE_SCALE)
                pygame.draw.rect(temp_frame, (80, 80, 180), 
                            (center_x - 8 * SPRITE_SCALE, center_y + 8 * SPRITE_SCALE, 
                                16 * SPRITE_SCALE, 8 * SPRITE_SCALE))
                
                self.animation_frames.append(temp_frame)
    
    def update_screen_position(self, camera_x):
        """Atualiza a posição do inimigo na tela baseado na câmera."""
        self.rect.centerx = int(self.world_x - camera_x)
        self.rect.bottom = int(self.world_y)
    
    def is_visible_on_screen(self, camera_x):
        """Verifica se o inimigo está visível na tela."""
        screen_x = self.world_x - camera_x
        return -100 < screen_x < WINDOW_WIDTH + 100
    
    def check_player_visibility(self, player_world_x, camera_x):
        """Verifica se o jogador está visível e inicia animação se necessário."""
        if not self.has_seen_player and self.is_visible_on_screen(camera_x):
            # Jogador entrou no campo de visão
            distance_to_player = abs(player_world_x - self.world_x)
            if distance_to_player < 500:  # Aumenta o range de detecção
                self.has_seen_player = True
                self.can_shoot = True
                self.shoot_timer = 0  # IMPORTANTE: Zera o timer para permitir tiro imediato
                print(f"[Enemy] Jogador detectado! Distância: {distance_to_player}, Posição inimigo: {self.world_x}, Posição jogador: {player_world_x}")

    
    def shoot_at_player(self, player_world_x, player_screen_y):
        """Atira um projétil em direção ao jogador."""
        if not self.can_shoot or not self.is_alive:
            return
        
        print(f"[Enemy] DISPARANDO no frame 6! Frame atual: {self.current_frame}")
        
        # Calcula direção do tiro
        direction_x = 1 if player_world_x > self.world_x else -1
        
        # Posição inicial do projétil (na altura do inimigo)
        projectile_world_x = self.world_x + (20 * SPRITE_SCALE * direction_x)
        projectile_screen_y = self.rect.centery  # Altura do centro do inimigo
        
        # Cria projétil
        projectile = EnemyProjectile(self.projectile_image, projectile_world_x, projectile_screen_y, direction_x)
        
        # Adiciona o projétil
        if self.projectiles is not None:
            self.projectiles.add(projectile)
            print(f"[Enemy] Projétil criado no frame 6! Direção: {direction_x}")
        
        # Reset do timer
        self.shoot_timer = self.shoot_cooldown
    
    def take_damage(self, damage=1):
        """Aplica dano ao inimigo."""
        if not self.is_alive:
            return False
            
        self.health -= damage
        print(f"[Enemy] Levou dano! Vida: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.is_alive = False
            print(f"[Enemy] Inimigo eliminado!")
            return True  # Inimigo morreu
        
        return False
    
    def update(self, dt, player_world_x, player_screen_y, camera_x):
        """Atualiza o inimigo."""
        if not self.is_alive:
            return
        
        # Atualiza posição na tela
        self.update_screen_position(camera_x)
        
        # Verifica se pode ver o jogador
        self.check_player_visibility(player_world_x, camera_x)
        
        # Se viu o jogador, anima e atira
        if self.has_seen_player:
            # Atualiza animação
            previous_frame = self.current_frame  # Salva o frame anterior
            
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.image = self.animation_frames[self.current_frame]
                
                # NOVO: Dispara APENAS quando muda para o frame 6 (índice 5)
                if self.current_frame == 5 and previous_frame != 5:  # Frame 6 (índice 5)
                    if self.can_shoot and self.shoot_timer <= 0 and self.is_visible_on_screen(camera_x):
                        self.shoot_at_player(player_world_x, player_screen_y)
            
            # Atualiza timer de tiro
            if self.shoot_timer > 0:
                self.shoot_timer -= dt
    
    def check_collision_with_projectile(self, projectile_rect):
        """Verifica colisão com projétil do jogador."""
        return self.rect.colliderect(projectile_rect)
    
    def render(self, screen):
        """Desenha o inimigo na tela."""
        if self.is_alive:
            screen.blit(self.image, self.rect)
            
            # Desenha barra de vida se levou dano
            if self.health < self.max_health:
                self._draw_health_bar(screen)
    
    def _draw_health_bar(self, screen):
        """Desenha barra de vida do inimigo."""
        bar_width = 40
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 10
        
        # Fundo da barra (vermelho)
        pygame.draw.rect(screen, (200, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de vida (verde)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (50, 200, 50), 
                        (bar_x, bar_y, int(bar_width * health_ratio), bar_height))


class EnemyManager:
    """Gerencia todos os inimigos do jogo."""
    
    def __init__(self, sprite_sheet, projectile_image):
        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.sprite_sheet = sprite_sheet
        self.projectile_image = projectile_image
        
        # Configurações de spawn
        self.spawn_distance = 600  # Distância entre spawns
        self.last_spawn_x = 800    # Primeiro inimigo aparece após 800px
        
    def spawn_enemy(self, world_x):
        """Spawna um novo inimigo."""
        enemy = Enemy(world_x, self.sprite_sheet, self.projectile_image)
        enemy.projectiles = self.enemy_projectiles
        self.enemies.add(enemy)
        print(f"[EnemyManager] Novo inimigo spawnado em {world_x}px")
    
    def update(self, dt, player_world_x, player_screen_y, camera_x, player_projectiles):
        """Atualiza todos os inimigos."""
        # Spawna novos inimigos se necessário
        if player_world_x > self.last_spawn_x - 1000:  # Spawna com antecedência
            self.spawn_enemy(self.last_spawn_x)
            self.last_spawn_x += self.spawn_distance + random.randint(-200, 200)  # Variação
        
        # Atualiza inimigos
        for enemy in self.enemies.sprites():
            enemy.update(dt, player_world_x, player_screen_y, camera_x)
            
            # Remove inimigos muito atrás
            if enemy.world_x < player_world_x - 1000:
                enemy.kill()
        
        # Atualiza projéteis dos inimigos
        self.enemy_projectiles.update(dt, camera_x)
        
        # Verifica colisões entre projéteis do jogador e inimigos
        self._check_player_projectile_collisions(player_projectiles)
        
        # Remove inimigos mortos
        for enemy in self.enemies.sprites():
            if not enemy.is_alive:
                enemy.kill()
    
    def _check_player_projectile_collisions(self, player_projectiles):
        """Verifica colisões entre projéteis do jogador e inimigos."""
        for projectile in player_projectiles.sprites():
            for enemy in self.enemies.sprites():
                if enemy.is_alive and enemy.check_collision_with_projectile(projectile.rect):
                    # Projétil acertou o inimigo
                    enemy.take_damage(1)
                    projectile.kill()  # Remove o projétil
                    break
    
    def check_enemy_projectile_collision(self, player_rect):
        """Verifica se algum projétil inimigo acertou o jogador."""
        for projectile in self.enemy_projectiles.sprites():
            if projectile.rect.colliderect(player_rect):
                projectile.kill()  # Remove o projétil
                return True  # Jogador foi atingido
        return False
    
    def render(self, screen, camera_x):
        """Renderiza todos os inimigos."""
        # Desenha inimigos
        for enemy in self.enemies.sprites():
            if enemy.is_visible_on_screen(camera_x):
                enemy.render(screen)
        
        # Desenha projéteis dos inimigos
        self.enemy_projectiles.draw(screen)