"""Classe do jogador (Mega Man X) com dash melhorado"""
import pygame
from config.settings import *
from utils.sprite_utils import *
from entities.projectile import Pellet


class Player(pygame.sprite.Sprite):
    """Jogador principal - Mega Man X."""
    
    def __init__(self, sprite_sheet, animation_rects, buster_sheet, buster_rects):
        super().__init__()
        
        # PRIMEIRO: Inicializa como dicionário vazio (não sobrescreve depois)
        self.damage_sprites = {'right': [], 'left': []}
        
        # DEPOIS: Carrega as animações (que vai preencher damage_sprites)
        self._load_animations(sprite_sheet, animation_rects, buster_sheet, buster_rects)
        
        self._init_sprite()
        self._init_physics()
        self._init_animation_state()
        self._init_timers()
        self._init_input_state()

        # Sistema de vida
        self.max_health = 16
        self.current_health = self.max_health
        self.is_alive = True
        self.invincibility_timer = 0
        self.invincibility_duration = 1000
        self.damage_flash_timer = 0
        self.original_image = None

        # Sistema de dano visual (NÃO redefine damage_sprites aqui!)
        # REMOVIDO: self.damage_sprites = {'right': [], 'left': []}  # Esta linha estava sobrescrevendo!
        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_animation_speed = 100
        self.damage_frame_index = 0
        
        # Knockback
        self.knockback_velocity = 0
        self.knockback_timer = 0
        self.knockback_duration = 300
        
        # Sons (definidos externamente)
        self.damage_sound = None
        self.death_sound = None
        self.projectiles = None
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

        # NOVO: Animação de dano (igual as outras)
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
            print(f"[Player] Sprites de dano carregados: {len(damage_right)} frames")
        else:
            self.damage_sprites = {'right': [], 'left': []}
            print("[Player] Sprites de dano não encontrados em animation_rects")

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
            self.idle_image_left = pygame.transform.flip(self.idle_image, True, False)
        else:
            # Fallback: usar primeiro frame da corrida
            self.idle_image = self.run_right[0]
            self.idle_image_left = self.run_left[0]

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
        self.dash_velocity = 0  # Nova variável para velocidade do dash
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
            # Define velocidade do dash na direção que está olhando
            self.dash_velocity = DASH_SPEED * self.facing_direction
            print(f"[DEBUG] Dash iniciado! Direção: {self.facing_direction}, Velocidade: {self.dash_velocity}")

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
        # TESTE TEMPORÁRIO - Pressione T para testar animação de dano
        if keys[pygame.K_t] and not self.keys_pressed.get('test_damage', False):
            print("[TEST] Forçando animação de dano!")
            self.is_taking_damage = True
            self.damage_animation_timer = 0
            self.damage_frame_index = 0
            self.keys_pressed['test_damage'] = True
        elif not keys[pygame.K_t]:
            self.keys_pressed['test_damage'] = False
        
        # Movimento horizontal (apenas setas direcionais)
        self.velocity_x = 0
        
        # Se não estiver em dash, processa movimento normal
        if self.dash_timer <= 0:
            if keys[pygame.K_LEFT]:
                self.velocity_x -= self.speed
                self.facing_direction = -1
                
            if keys[pygame.K_RIGHT]:
                self.velocity_x += self.speed
                self.facing_direction = 1
        else:
            # Durante o dash, usa a velocidade do dash
            self.velocity_x = self.dash_velocity

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

        # Colisão com o chão (será verificada pelo obstacle manager)
        if self.rect.bottom >= GROUND_Y and self.velocity_y >= 0:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.is_on_ground = True
        else:
            # Se não está no chão, não está no chão
            if self.rect.bottom < GROUND_Y:
                self.is_on_ground = False

        # Atualização de timers
        if self.dash_timer > 0:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                # Fim do dash - para a velocidade do dash
                self.dash_velocity = 0
                print("[DEBUG] Dash terminou!")

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def animate(self, dt):
        """Atualiza animação do jogador."""
        # DEBUG FORÇADO
        print(f"[DEBUG ANIMATE] is_taking_damage: {self.is_taking_damage}")
        print(f"[DEBUG ANIMATE] damage_sprites disponíveis: {len(self.damage_sprites.get('right', []))}")
        
        # PRIORIDADE MÁXIMA: Animação de dano - COM DEBUG DETALHADO
        if self.is_taking_damage:
            print("[DEBUG ANIMATE] ENTROU na animação de dano!")
            
            if not self.damage_sprites:
                print("[DEBUG ANIMATE] ERROR: damage_sprites é None/vazio")
                return
                
            if 'right' not in self.damage_sprites:
                print("[DEBUG ANIMATE] ERROR: 'right' não existe em damage_sprites")
                return
                
            frames = self.damage_sprites['right'] if self.facing_direction == 1 else self.damage_sprites['left']
            
            if not frames:
                print("[DEBUG ANIMATE] ERROR: lista de frames está vazia")
                return
                
            if self.damage_frame_index >= len(frames):
                print(f"[DEBUG ANIMATE] ERROR: damage_frame_index {self.damage_frame_index} >= {len(frames)}")
                self.damage_frame_index = 0  # Corrige o índice
                
            current_frame = frames[self.damage_frame_index]
            print(f"[DEBUG ANIMATE] Aplicando sprite de dano frame {self.damage_frame_index}, tamanho: {current_frame.get_size()}")
            
            set_image_keep_feet(self, current_frame)
            return  # IMPORTANTE: Sair aqui para não executar outras animações
        
        print("[DEBUG ANIMATE] NÃO está tomando dano, usando animação normal")
        
        # Se chegou aqui, não está tomando dano
        is_moving = abs(self.velocity_x) > 0.1

        # Animação de dash (prioridade alta no chão)
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
            image = self.idle_image if self.facing_direction == 1 else self.idle_image_left

        # Se estiver atirando no chão, substitui pela pose de tiro
        if self.shoot_timer > 0:
            shoot_frames = self.shoot_right if self.facing_direction == 1 else self.shoot_left
            image = shoot_frames[0]

        set_image_keep_feet(self, image)

    def update(self, dt, keys):
        """Atualização principal do jogador."""
        if not self.is_alive:
            return
            
        self.handle_input(keys)
        self.apply_physics(dt)
        self.update_knockback(dt)
        self.update_damage_animation(dt)  # DEVE vir ANTES do animate()
        self.animate(dt)  # animate() deve usar o estado atualizado
        self.update_damage_effects(dt)

    def take_damage(self, damage=2):
        """Aplica dano ao jogador com knockback e efeitos visuais."""
        if self.invincibility_timer > 0 or not self.is_alive:
            print("[DEBUG] take_damage ignorado (invencibilidade ou morto)")
            return False
        
        print("[DEBUG] ============ TAKE_DAMAGE EXECUTADO ============")
        
        # Aplica o dano
        self.current_health -= damage
        self.invincibility_timer = self.invincibility_duration
        self.damage_flash_timer = 200
        
        # FORÇAR animação de dano
        self.is_taking_damage = True
        self.damage_animation_timer = 0
        self.damage_frame_index = 0
        
        print(f"[DEBUG] Estado após take_damage:")
        print(f"  is_taking_damage: {self.is_taking_damage}")
        print(f"  damage_frame_index: {self.damage_frame_index}")
        print(f"  damage_sprites['right']: {len(self.damage_sprites.get('right', []))} frames")
        
        # Knockback
        knockback_force = -3.0 if self.facing_direction == 1 else 3.0
        self.knockback_velocity = knockback_force
        self.knockback_timer = self.knockback_duration
        
        # Som
        if self.damage_sound:
            self.damage_sound.play()
        
        # Morte
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
            if self.death_sound:
                self.death_sound.play()
            return True
        
        return False

    def update_damage_effects(self, dt):
        """Atualiza efeitos visuais de dano."""
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt

    def reset_health(self):
        """Reseta a vida do jogador."""
        self.current_health = self.max_health
        self.is_alive = True
        self.invincibility_timer = 0
        self.damage_flash_timer = 0
        
        # NOVO: Reset dos efeitos de dano
        self.is_taking_damage = False
        self.damage_animation_timer = 0
        self.damage_frame_index = 0
        self.knockback_velocity = 0
        self.knockback_timer = 0

    def update_damage_animation(self, dt):
        """Atualiza a animação de dano."""
        if not self.is_taking_damage:
            return
        
        print(f"[DEBUG UPDATE_DAMAGE] Atualizando animação: timer={self.damage_animation_timer}, speed={self.damage_animation_speed}")
        
        self.damage_animation_timer += dt
        
        # Avança para o próximo frame de dano
        if self.damage_animation_timer >= self.damage_animation_speed:
            self.damage_animation_timer = 0
            self.damage_frame_index += 1
            
            print(f"[DEBUG UPDATE_DAMAGE] Avançando para frame {self.damage_frame_index}")
            
            # Se chegou ao fim da animação de dano
            if self.damage_frame_index >= len(self.damage_sprites.get('right', [])):
                self.is_taking_damage = False
                self.damage_frame_index = 0
                print("[DEBUG UPDATE_DAMAGE] Animação de dano FINALIZADA!")

    def update_knockback(self, dt):
        """Atualiza o efeito de knockback."""
        if self.knockback_timer > 0:
            self.knockback_timer -= dt
            
            # Aplica o knockback
            self.world_x += self.knockback_velocity
            
            # Diminui gradualmente o knockback
            self.knockback_velocity *= 0.9
            
            # Para o knockback quando o timer acabar
            if self.knockback_timer <= 0:
                self.knockback_velocity = 0

    def force_damage_animation_test(self):
        """Método temporário para testar animação de dano."""
        print("[TEST] Forçando animação de dano...")
        self.is_taking_damage = True
        self.damage_animation_timer = 0
        self.damage_frame_index = 0
        print(f"[TEST] Estado após forçar: is_taking_damage={self.is_taking_damage}, frames disponíveis={len(self.damage_sprites.get('right', []))}")
