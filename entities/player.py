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

        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_animation_speed = 100
        self.damage_frame_index = 0
        
        self.knockback_velocity = 0
        self.knockback_timer = 0
        self.knockback_duration = 300
        
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

    def start_dash(self):
        if self.is_on_ground and self.dash_timer <= 0:
            self.dash_timer = DASH_TIME_MS
            self.dash_velocity = DASH_SPEED * self.facing_direction

    def shoot(self):
        if self.shoot_cooldown > 0:
            return
            
        if self.shoot_sound:
            self.shoot_sound.play()
        
        self.shoot_timer = 150
        self.shoot_cooldown = 150
        
        offset_x = 15 * SPRITE_SCALE
        world_px = self.world_x + (offset_x if self.facing_direction == 1 else -offset_x)
        
        arm_height_offset = -2 * SPRITE_SCALE
        screen_py = self.rect.centery + arm_height_offset
        
        pellet = Pellet(self.pellet_image, world_px, screen_py, self.facing_direction)
        
        if self.projectiles is not None:
            self.projectiles.add(pellet)

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

    def apply_physics(self, dt):
        self.world_x += self.velocity_x
        if self.world_x < 0:
            self.world_x = 0

        self.velocity_y += GRAVITY
        self.rect.y += int(self.velocity_y)

        if self.rect.bottom >= GROUND_Y and self.velocity_y >= 0:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.is_on_ground = True
        else:
            if self.rect.bottom < GROUND_Y:
                self.is_on_ground = False

        if self.dash_timer > 0:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_velocity = 0

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

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

    def update(self, dt, keys):
        if not self.is_alive:
            return
            
        self.handle_input(keys)
        self.apply_physics(dt)
        self.update_knockback(dt)
        self.update_damage_animation(dt)
        self.animate(dt)
        self.update_damage_effects(dt)

    def take_damage(self, damage=2):
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

    def update_damage_effects(self, dt):
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt

    def reset_health(self):
        self.current_health = self.max_health
        self.is_alive = True
        self.invincibility_timer = 0
        self.damage_flash_timer = 0
        
        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_frame_index = 0
        self.knockback_velocity = 0
        self.knockback_timer = 0

    def update_damage_animation(self, dt):
        if not self.is_taking_damage:
            return
        
        self.damage_animation_timer += dt
        
        if self.damage_animation_timer >= self.damage_animation_speed:
            self.damage_animation_timer = 0
            self.damage_frame_index += 1
            
            if self.damage_frame_index >= len(self.damage_sprites.get('right', [])):
                self.is_taking_damage = False
                self.damage_frame_index = 0

    def update_knockback(self, dt):
        if self.knockback_timer > 0:
            self.knockback_timer -= dt
            
            self.world_x += self.knockback_velocity
            
            self.knockback_velocity *= 0.9
            
            if self.knockback_timer <= 0:
                self.knockback_velocity = 0

    def force_damage_animation_test(self):
        self.is_taking_damage = True
        self.damage_animation_timer = 0
        self.damage_frame_index = 0