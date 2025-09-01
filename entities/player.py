import pygame
from config.settings import *
from utils.sprite_utils import *
from entities.projectile import Pellet


class Player(pygame.sprite.Sprite):
    
    def __init__(self, sprite_sheet, animation_rects, buster_sheet, buster_rects):
        super().__init__()
        
        self.damage_sprites = {'right': [], 'left': []}
        
        self._load_animations(sprite_sheet, animation_rects, buster_sheet, buster_rects)
        
        self._init_sprite()
        self._init_physics()
        self._init_animation_state()
        self._init_timers()
        self._init_input_state()

        self.max_health = 16
        self.current_health = self.max_health
        self.is_alive = True
        self.invincibility_timer = 0
        self.invincibility_duration = 1000
        self.damage_flash_timer = 0
        self.original_image = None

        # ADICIONADO: Power-ups
        self.has_shield = False
        self.shield_timer = 0
        self.rapid_fire_timer = 0
        self.normal_shoot_cooldown = 150
        self.rapid_shoot_cooldown = 50  # Tiro mais rápido

        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_animation_speed = 100
        self.damage_frame_index = 0
        
        self.knockback_velocity = 0
        self.knockback_timer = 0
        self.knockback_duration = 300
        
        # Efeitos visuais
        self.shield_flash_timer = 0
        
        self.damage_sound = None
        self.death_sound = None
        self.projectiles = None
        self.shoot_sound = None

    def _load_animations(self, sprite_sheet, animation_rects, buster_sheet, buster_rects):
        run_frames = slice_surface_padded(
            sprite_sheet, animation_rects['run'], pad=(0, 1, 0, 1)
        )
        self.run_right = scale_frames(run_frames, SPRITE_SCALE)
        self.run_left = flip_frames_horizontal(self.run_right)

        jump_frames = slice_surface_padded(
            sprite_sheet, animation_rects['jump'], pad=(0, 10, 0, 2)
        )
        self.jump_right = scale_frames(jump_frames, SPRITE_SCALE)
        self.jump_left = flip_frames_horizontal(self.jump_right)

        dash_frames = slice_surface_padded(
            sprite_sheet, animation_rects['dash'], pad=(0, 2, 0, 2)
        )
        self.dash_right = scale_frames(dash_frames, SPRITE_SCALE)
        self.dash_left = flip_frames_horizontal(self.dash_right)

        shoot_frames = slice_surface_padded(
            sprite_sheet, animation_rects['shoot'], pad=(0, 2, 0, 2)
        )
        self.shoot_right = scale_frames(shoot_frames, SPRITE_SCALE)
        self.shoot_left = flip_frames_horizontal(self.shoot_right)

        if 'damage' in animation_rects:
            damage_frames = slice_surface_padded(
                sprite_sheet, animation_rects['damage'], pad=(0, 1, 0, 1)
            )
            damage_right = scale_frames(damage_frames, SPRITE_SCALE)
            damage_left = flip_frames_horizontal(damage_right)
            
            self.damage_sprites = {
                'right': damage_right,
                'left': damage_left
            }
        else:
            self.damage_sprites = {'right': [], 'left': []}

        pellet_frames = slice_surface_padded(
            buster_sheet, [buster_rects['pellet']], pad=(0, 0, 0, 0)
        )
        self.pellet_image = scale_frames(pellet_frames, SPRITE_SCALE)[0]

        if 'idle' in animation_rects:
            idle_frames = slice_surface_padded(
                sprite_sheet, [animation_rects['idle']], pad=(0, 1, 0, 1)
            )
            idle_scaled = scale_frames(idle_frames, SPRITE_SCALE)
            self.idle_image = idle_scaled[0]
            self.idle_image_left = pygame.transform.flip(self.idle_image, True, False)
        else:
            self.idle_image = self.run_right[0]
            self.idle_image_left = self.run_left[0]

    def _init_sprite(self):
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = (WINDOW_WIDTH // 2, GROUND_Y)

    def _init_physics(self):
        self.world_x = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = RUN_SPEED
        self.facing_direction = 1
        self.is_on_ground = True

    def _init_animation_state(self):
        self.animation_timer = 0
        self.animation_index = 0
        self.jump_timer = 0
        self.jump_index = 0

    def _init_timers(self):
        self.dash_timer = 0
        self.dash_velocity = 0
        self.shoot_timer = 0
        self.shoot_cooldown = 0

    def _init_input_state(self):
        self.keys_pressed = {
            'dash': False,
            'jump': False,
            'shoot': False
        }

    def handle_input(self, keys):
        if keys[pygame.K_t] and not self.keys_pressed.get('test_damage', False):
            self.is_taking_damage = True
            self.damage_animation_timer = 0
            self.damage_frame_index = 0
            self.keys_pressed['test_damage'] = True
        elif not keys[pygame.K_t]:
            self.keys_pressed['test_damage'] = False
        
        self.velocity_x = 0
        
        if self.dash_timer <= 0:
            if keys[pygame.K_LEFT]:
                self.velocity_x -= self.speed
                self.facing_direction = -1
                
            if keys[pygame.K_RIGHT]:
                self.velocity_x += self.speed
                self.facing_direction = 1
        else:
            self.velocity_x = self.dash_velocity

        if keys[pygame.K_z] and not self.keys_pressed['jump'] and self.is_on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.is_on_ground = False
            self.jump_index = 0
            self.jump_timer = 0
            self.keys_pressed['jump'] = True
        elif not keys[pygame.K_z]:
            self.keys_pressed['jump'] = False

        if keys[pygame.K_x] and not self.keys_pressed['dash']:
            self.start_dash()
            self.keys_pressed['dash'] = True
        elif not keys[pygame.K_x]:
            self.keys_pressed['dash'] = False

        if keys[pygame.K_a] and not self.keys_pressed['shoot']:
            self.shoot()
            self.keys_pressed['shoot'] = True
        elif not keys[pygame.K_a]:
            self.keys_pressed['shoot'] = False

    def animate(self, dt):
        if self.is_taking_damage:
            if not self.damage_sprites:
                return
                
            if 'right' not in self.damage_sprites:
                return
                
            frames = self.damage_sprites['right'] if self.facing_direction == 1 else self.damage_sprites['left']
            
            if not frames:
                return
                
            if self.damage_frame_index >= len(frames):
                self.damage_frame_index = 0
                
            current_frame = frames[self.damage_frame_index]
            
            set_image_keep_feet(self, current_frame)
            return
        
        is_moving = abs(self.velocity_x) > 0.1

        if self.is_on_ground and self.dash_timer > 0:
            frames = self.dash_right if self.facing_direction == 1 else self.dash_left
            frame_index = 1 if self.dash_timer < DASH_TIME_MS * 0.6 else 0
            set_image_keep_feet(self, frames[frame_index])
            return

        if not self.is_on_ground:
            self._animate_jump(dt)
            return

        self._animate_ground(dt, is_moving)
        
    def _animate_jump(self, dt):
        frames = self.jump_right if self.facing_direction == 1 else self.jump_left
        
        if self.velocity_y < -3:
            self.jump_timer += dt
            if self.jump_timer > JUMP_ANIM_SPEED:
                self.jump_timer = 0
                self.jump_index = (self.jump_index + 1) % 3
            frame_index = self.jump_index
            
        elif -3 <= self.velocity_y <= 3:
            frame_index = 3
            self.jump_index = 3
            self.jump_timer = 0
            
        else:
            self.jump_timer += dt
            if self.jump_timer > JUMP_ANIM_SPEED:
                self.jump_timer = 0
                self.jump_index = min(self.jump_index + 1, len(frames) - 1)
            frame_index = max(4, self.jump_index)

        set_image_keep_feet(self, frames[frame_index])

    def _animate_ground(self, dt, is_moving):
        frames = self.run_right if self.facing_direction == 1 else self.run_left
        
        if is_moving:
            self.animation_timer += dt
            if self.animation_timer > RUN_ANIM_SPEED:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(frames)
            image = frames[self.animation_index]
        else:
            self.animation_index = 0
            image = self.idle_image if self.facing_direction == 1 else self.idle_image_left

        if self.shoot_timer > 0:
            shoot_frames = self.shoot_right if self.facing_direction == 1 else self.shoot_left
            image = shoot_frames[0]

        set_image_keep_feet(self, image)

    def start_dash(self):
        """Inicia o dash se as condições forem atendidas."""
        if self.is_on_ground and self.dash_timer <= 0:
            self.dash_timer = DASH_TIME_MS
            self.dash_velocity = DASH_SPEED * self.facing_direction

    def heal(self, amount):
        """Cura o jogador em uma quantidade específica."""
        self.current_health = min(self.current_health + amount, self.max_health)
    
    def activate_rapid_fire(self, duration_ms):
        """Ativa tiro rápido por um tempo determinado."""
        self.rapid_fire_timer = duration_ms
    
    def activate_shield(self, duration_ms):
        """Ativa escudo por um tempo determinado."""
        self.has_shield = True
        self.shield_timer = duration_ms

    def shoot(self):
        """Cria um projétil quando o jogador atira."""
        # Usa cooldown baseado no power-up
        current_cooldown = self.rapid_shoot_cooldown if self.rapid_fire_timer > 0 else self.normal_shoot_cooldown
        
        if self.shoot_cooldown > 0:
            return
            
        if self.shoot_sound:
            self.shoot_sound.play()
        
        self.shoot_timer = 150
        self.shoot_cooldown = current_cooldown  # MODIFICADO: Usa cooldown variável
        
        # Offset horizontal para que o projétil saia da frente do jogador
        offset_x = 15 * SPRITE_SCALE
        world_px = self.world_x + (offset_x if self.facing_direction == 1 else -offset_x)
        
        # Altura do projétil (na altura do braço do jogador)
        arm_height_offset = -2 * SPRITE_SCALE
        screen_py = self.rect.centery + arm_height_offset
        
        # Cria o projétil
        pellet = Pellet(self.pellet_image, world_px, screen_py, self.facing_direction)
        
        # Adiciona ao grupo de projéteis
        if self.projectiles is not None:
            self.projectiles.add(pellet)

    def apply_physics(self, dt):
        """Aplica física de movimento e gravidade ao jogador."""
        # Movimento horizontal
        self.world_x += self.velocity_x
        if self.world_x < 0:
            self.world_x = 0

        # Gravidade e movimento vertical
        self.velocity_y += GRAVITY
        self.rect.y += int(self.velocity_y)

        # Colisão com o chão
        if self.rect.bottom >= GROUND_Y and self.velocity_y >= 0:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.is_on_ground = True
        else:
            if self.rect.bottom < GROUND_Y:
                self.is_on_ground = False

        # Atualiza timers de dash
        if self.dash_timer > 0:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_velocity = 0

        # Atualiza timers de tiro
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def update(self, dt, keys):
        """Atualiza o jogador a cada frame."""
        if not self.is_alive:
            return
        
        # ADICIONADO: Atualiza timers de power-ups
        self._update_powerup_timers(dt)
        
        self.handle_input(keys)
        self.apply_physics(dt)
        self.update_knockback(dt)
        self.update_damage_animation(dt)
        self.animate(dt)
        self.update_damage_effects(dt)
    
    def _update_powerup_timers(self, dt):
        """Atualiza os timers dos power-ups."""
        # Timer de tiro rápido
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_timer = 0
        
        # Timer de escudo
        if self.shield_timer > 0:
            self.shield_timer -= dt
            self.shield_flash_timer += dt
            if self.shield_timer <= 0:
                self.shield_timer = 0
                self.has_shield = False
                self.shield_flash_timer = 0

    def update_damage_effects(self, dt):
        """Atualiza efeitos visuais de dano e invulnerabilidade."""
        # Atualiza timer de invulnerabilidade
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincibility_timer = 0
        
        # Atualiza efeito de flash de dano
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            if self.damage_flash_timer <= 0:
                self.damage_flash_timer = 0
        
        # Efeito visual durante invulnerabilidade (piscar)
        if self.invincibility_timer > 0:
            # Faz o sprite piscar durante a invulnerabilidade
            flash_rate = 100  # Velocidade do piscar em ms
            if int(self.invincibility_timer / flash_rate) % 2:
                # Torna o sprite semi-transparente
                if hasattr(self, 'original_image') and self.original_image:
                    temp_image = self.original_image.copy()
                    temp_image.set_alpha(128)  # 50% transparente
                    self.image = temp_image
                else:
                    # Backup: usa a imagem atual
                    temp_image = self.image.copy()
                    temp_image.set_alpha(128)
                    self.image = temp_image
            else:
                # Restaura opacidade normal
                if hasattr(self, 'original_image') and self.original_image:
                    self.image = self.original_image.copy()
                else:
                    # Restaura alpha normal
                    self.image.set_alpha(255)
        else:
            # Garante que o sprite esteja com opacidade normal
            if hasattr(self, 'original_image') and self.original_image:
                self.image = self.original_image.copy()
            else:
                self.image.set_alpha(255)

    def update_knockback(self, dt):
        """Atualiza o efeito de knockback quando o jogador toma dano."""
        if self.knockback_timer > 0:
            self.knockback_timer -= dt
            
            # Aplica velocidade de knockback
            self.world_x += self.knockback_velocity * (dt / 16.67)  # Normaliza para 60 FPS
            
            # Reduz gradualmente a velocidade de knockback
            decay_factor = 0.95
            self.knockback_velocity *= decay_factor
            
            # Para o knockback quando o timer acaba
            if self.knockback_timer <= 0:
                self.knockback_timer = 0
                self.knockback_velocity = 0

    def update_damage_animation(self, dt):
        """Atualiza a animação de dano do jogador."""
        if self.is_taking_damage and len(self.damage_sprites['right']) > 0:
            self.damage_animation_timer += dt
            
            if self.damage_animation_timer >= self.damage_animation_speed:
                self.damage_animation_timer = 0
                self.damage_frame_index += 1
                
                # Verifica se a animação de dano terminou
                direction_key = 'right' if self.facing_direction == 1 else 'left'
                if self.damage_frame_index >= len(self.damage_sprites[direction_key]):
                    self.damage_frame_index = 0
                    self.is_taking_damage = False
                else:
                    # Atualiza o sprite para o frame de dano atual
                    self.image = self.damage_sprites[direction_key][self.damage_frame_index]

    def take_damage(self, damage=2):
        # Se tem escudo, não toma dano
        if self.has_shield:
            return False
        
        if self.invincibility_timer > 0 or not self.is_alive:
            return False
        
        self.current_health -= damage
        self.invincibility_timer = self.invincibility_duration
        self.damage_flash_timer = 200
        
        self.is_taking_damage = True
        self.damage_animation_timer = 0
        self.damage_frame_index = 0
        
        knockback_force = -3.0 if self.facing_direction == 1 else 3.0
        self.knockback_velocity = knockback_force
        self.knockback_timer = self.knockback_duration
        
        if self.damage_sound:
            self.damage_sound.play()
        
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
            if self.death_sound:
                self.death_sound.play()
            return True
        
        return False

    def reset_health(self):
        """Reseta a vida e estado do jogador para uma nova partida."""
        self.current_health = self.max_health
        self.is_alive = True
        self.invincibility_timer = 0
        self.damage_flash_timer = 0
        self.original_image = None
        
        # ADICIONADO: Reset dos power-ups
        self.has_shield = False
        self.shield_timer = 0
        self.rapid_fire_timer = 0
        self.shield_flash_timer = 0
        
        # Reset de estado de dano
        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_frame_index = 0
        
        # Reset de knockback
        self.knockback_velocity = 0
        self.knockback_timer = 0
        
        # Reset de timers de ação
        self.dash_timer = 0
        self.dash_velocity = 0
        self.shoot_timer = 0
        self.shoot_cooldown = 0
        
        # Reset de estado de input
        self.keys_pressed = {
            'dash': False,
            'jump': False,
            'shoot': False,
            'test_damage': False
        }

    def force_damage_animation_test(self):
        """Força a animação de dano para teste."""
        self.is_taking_damage = True
        self.damage_animation_timer = 0
        self.damage_frame_index = 0