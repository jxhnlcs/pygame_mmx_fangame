"""Classe do jogador (Mega Man X)"""
import pygame
from config.settings import *
from utils.sprite_utils import *
from entities.projectile import Pellet


class Player(pygame.sprite.Sprite):
    """Jogador principal - Mega Man X."""
    
    def __init__(self, sprite_sheet, animation_rects, buster_sheet, buster_rects):
        super().__init__()
        self._load_animations(sprite_sheet, animation_rects, buster_sheet, buster_rects)
        self._init_sprite()
        self._init_physics()
        self._init_animation_state()
        self._init_timers()
        self._init_input_state()
        
        # Referência para grupo de projéteis (será definida externamente)
        self.projectiles = None
        
        # Som de disparo (será definido externamente)
        self.shoot_sound = None

    def _load_animations(self, sprite_sheet, animation_rects, buster_sheet, buster_rects):
        """Carrega todas as animações do jogador."""
        # Animação de corrida
        run_frames = slice_surface_padded(
            sprite_sheet, animation_rects['run'], pad=(0, 1, 0, 1)
        )
        self.run_right = scale_frames(run_frames, SPRITE_SCALE)
        self.run_left = flip_frames_horizontal(self.run_right)

        # Animação de pulo
        jump_frames = slice_surface_padded(
            sprite_sheet, animation_rects['jump'], pad=(0, 10, 0, 2)
        )
        self.jump_right = scale_frames(jump_frames, SPRITE_SCALE)
        self.jump_left = flip_frames_horizontal(self.jump_right)

        # Animação de dash
        dash_frames = slice_surface_padded(
            sprite_sheet, animation_rects['dash'], pad=(0, 2, 0, 2)
        )
        self.dash_right = scale_frames(dash_frames, SPRITE_SCALE)
        self.dash_left = flip_frames_horizontal(self.dash_right)

        # Animação de tiro
        shoot_frames = slice_surface_padded(
            sprite_sheet, animation_rects['shoot'], pad=(0, 2, 0, 2)
        )
        self.shoot_right = scale_frames(shoot_frames, SPRITE_SCALE)
        self.shoot_left = flip_frames_horizontal(self.shoot_right)

        # Projétil (do buster sheet)
        pellet_frames = slice_surface_padded(
            buster_sheet, [buster_rects['pellet']], pad=(0, 0, 0, 0)
        )
        self.pellet_image = scale_frames(pellet_frames, SPRITE_SCALE)[0]

        # Frame parado (sprite específico para idle)
        if 'idle' in animation_rects:
            idle_frames = slice_surface_padded(
                sprite_sheet, [animation_rects['idle']], pad=(0, 1, 0, 1)
            )
            idle_scaled = scale_frames(idle_frames, SPRITE_SCALE)
            self.idle_image = idle_scaled[0]
        else:
            # Fallback: usar primeiro frame da corrida
            self.idle_image = self.run_right[0]

    def _init_sprite(self):
        """Inicializa o sprite."""
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = (WINDOW_WIDTH // 2, GROUND_Y)

    def _init_physics(self):
        """Inicializa variáveis de física."""
        self.world_x = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = RUN_SPEED
        self.facing_direction = 1  # 1 = direita, -1 = esquerda
        self.is_on_ground = True

    def _init_animation_state(self):
        """Inicializa estado das animações."""
        self.animation_timer = 0
        self.animation_index = 0
        self.jump_timer = 0
        self.jump_index = 0

    def _init_timers(self):
        """Inicializa timers de ações."""
        self.dash_timer = 0
        self.shoot_timer = 0
        self.shoot_cooldown = 0

    def _init_input_state(self):
        """Inicializa estado das teclas para detectar pressionamentos únicos."""
        self.keys_pressed = {
            'dash': False,
            'jump': False,
            'shoot': False
        }

    def start_dash(self):
        """Inicia o dash se possível."""
        if self.is_on_ground and self.dash_timer <= 0:
            self.dash_timer = DASH_TIME_MS
            self.speed = DASH_SPEED

    def shoot(self):
        """Dispara um projétil se possível."""
        if self.shoot_cooldown > 0:
            return
            
        # Toca som de disparo
        if self.shoot_sound:
            self.shoot_sound.play()
        
        # Reduzido o cooldown para tiros mais rápidos
        self.shoot_timer = 150
        self.shoot_cooldown = 150
        
        # Calcula posição do projétil (à frente do braço estendido)
        offset_x = 15 * SPRITE_SCALE
        world_px = self.world_x + (offset_x if self.facing_direction == 1 else -offset_x)
        
        # Ajusta altura para o braço estendido
        arm_height_offset = -2 * SPRITE_SCALE
        screen_py = self.rect.centery + arm_height_offset
        
        pellet = Pellet(self.pellet_image, world_px, screen_py, self.facing_direction)
        
        if self.projectiles is not None:
            self.projectiles.add(pellet)

    def handle_input(self, keys):
        """Processa entrada do jogador."""
        # Movimento horizontal (apenas setas direcionais)
        self.velocity_x = 0
        
        if keys[pygame.K_LEFT]:
            self.velocity_x -= self.speed
            self.facing_direction = -1
            
        if keys[pygame.K_RIGHT]:
            self.velocity_x += self.speed
            self.facing_direction = 1

        # Pulo (Z) - apenas um pressionamento por vez
        if keys[pygame.K_z] and not self.keys_pressed['jump'] and self.is_on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.is_on_ground = False
            self.jump_index = 0
            self.jump_timer = 0
            self.keys_pressed['jump'] = True
        elif not keys[pygame.K_z]:
            self.keys_pressed['jump'] = False

        # Dash (X) - apenas um pressionamento por vez
        if keys[pygame.K_x] and not self.keys_pressed['dash']:
            self.start_dash()
            self.keys_pressed['dash'] = True
        elif not keys[pygame.K_x]:
            self.keys_pressed['dash'] = False

        # Tiro (A) - apenas um pressionamento por vez
        if keys[pygame.K_a] and not self.keys_pressed['shoot']:
            self.shoot()
            self.keys_pressed['shoot'] = True
        elif not keys[pygame.K_a]:
            self.keys_pressed['shoot'] = False

    def apply_physics(self, dt):
        """Aplica física ao jogador."""
        # Movimento horizontal (espaço do mundo)
        self.world_x += self.velocity_x
        if self.world_x < 0:
            self.world_x = 0

        # Movimento vertical (espaço da tela)
        self.velocity_y += GRAVITY
        self.rect.y += int(self.velocity_y)

        # Colisão com o chão
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.is_on_ground = True

        # Atualização de timers
        if self.dash_timer > 0:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.speed = RUN_SPEED  # Fim do dash

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def animate(self, dt):
        """Atualiza animação do jogador."""
        is_moving = abs(self.velocity_x) > 0.1

        # Animação de dash (prioridade máxima no chão)
        if self.is_on_ground and self.dash_timer > 0:
            frames = self.dash_right if self.facing_direction == 1 else self.dash_left
            frame_index = 1 if self.dash_timer < DASH_TIME_MS * 0.6 else 0
            set_image_keep_feet(self, frames[frame_index])
            return

        # Animação no ar
        if not self.is_on_ground:
            self._animate_jump(dt)
            return

        # Animação no chão (corrida/parado + pose de tiro)
        self._animate_ground(dt, is_moving)

    def _animate_jump(self, dt):
        """Anima o jogador no ar."""
        frames = self.jump_right if self.facing_direction == 1 else self.jump_left
        
        if self.velocity_y < -3:
            # Subindo: cicla pelos primeiros 3 frames lentamente
            self.jump_timer += dt
            if self.jump_timer > JUMP_ANIM_SPEED:
                self.jump_timer = 0
                self.jump_index = (self.jump_index + 1) % 3
            frame_index = self.jump_index
            
        elif -3 <= self.velocity_y <= 3:
            # No ápice: frame 3
            frame_index = 3
            self.jump_index = 3
            self.jump_timer = 0
            
        else:
            # Caindo: avança pelos frames finais
            self.jump_timer += dt
            if self.jump_timer > JUMP_ANIM_SPEED:
                self.jump_timer = 0
                self.jump_index = min(self.jump_index + 1, len(frames) - 1)
            frame_index = max(4, self.jump_index)

        set_image_keep_feet(self, frames[frame_index])

    def _animate_ground(self, dt, is_moving):
        """Anima o jogador no chão."""
        frames = self.run_right if self.facing_direction == 1 else self.run_left
        
        if is_moving:
            # Animação de corrida
            self.animation_timer += dt
            if self.animation_timer > RUN_ANIM_SPEED:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(frames)
            image = frames[self.animation_index]
        else:
            # Parado
            self.animation_index = 0
            image = self.idle_image if self.facing_direction == 1 else self.run_left[0]

        # Se estiver atirando no chão, substitui pela pose de tiro
        if self.shoot_timer > 0:
            shoot_frames = self.shoot_right if self.facing_direction == 1 else self.shoot_left
            image = shoot_frames[0]

        set_image_keep_feet(self, image)

    def update(self, dt, keys):
        """Atualização principal do jogador."""
        self.handle_input(keys)
        self.apply_physics(dt)
        self.animate(dt)