"""Utilitários para manipulação de sprites"""
import pygame


def slice_surface_padded(sheet, rects, pad=(0, 0, 0, 0)):
    """Corta cada rect exatamente e aplica padding em uma surface transparente."""
    frames = []
    for (x, y, w, h) in rects:
        left, top, right, bottom = pad
        crop = sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
        surf = pygame.Surface((w + left + right, h + top + bottom)).convert()
        surf.fill((255, 0, 255))
        surf.set_colorkey((255, 0, 255))
        surf.blit(crop, (left, top))
        frames.append(surf)
    return frames


def scale_frames(frames, scale):
    """Escala uma lista de frames."""
    scaled_frames = []
    for frame in frames:
        width, height = frame.get_size()
        scaled_frame = pygame.transform.scale(
            frame, (int(width * scale), int(height * scale))
        )
        scaled_frames.append(scaled_frame)
    return scaled_frames


def flip_frames_horizontal(frames):
    """Espelha uma lista de frames horizontalmente."""
    return [pygame.transform.flip(frame, True, False) for frame in frames]


def set_image_keep_feet(sprite, new_image):
    """Troca a imagem do sprite mantendo os pés na mesma posição."""
    bottom_center = sprite.rect.midbottom
    sprite.image = new_image
    sprite.rect = sprite.image.get_rect()
    sprite.rect.midbottom = bottom_center
