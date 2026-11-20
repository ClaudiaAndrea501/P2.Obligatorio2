import math
import json
import random
import sys

import pygame

import ajustes
from vision import Vision


# Define la posición de los botones y paneles interactivos de cada pantalla.
RANKING_BUTTON_RECT = (914, 7, 38, 38)
PAUSE_BUTTON_RECT = (870, 7, 38, 38)
RETURN_MENU_BUTTON_RECT = (798, 7, 68, 38)
MENU_BUTTON_RECTS = {
    "JUGAR": (72, 258, 232, 60),
    "CÓMO JUGAR": (72, 332, 232, 60),
    "RANKING": (72, 406, 232, 60),
    "SALIR": (72, 480, 232, 60),
}
INSTRUCTIONS_PANEL_RECT = (160, 110, 640, 420)
INSTRUCTIONS_CLOSE_RECT = (742, 126, 38, 38)
RANKING_PANEL_RECT = (128, 126, 704, 470)


# Representa la posición de la mano que el jugador usa para interactuar.
class Player:
    # Inicia el marcador de contacto en el centro y cerca de la parte inferior.
    def __init__(self):
        self.x = ajustes.WINDOW_WIDTH / 2
        self.y = ajustes.WINDOW_HEIGHT - 95
        self.radius = ajustes.PLAYER_RADIUS

    # Sigue la posición detectada suavizando los cambios bruscos.
    def follow(self, target):
        if target is None:
            return
        target_x, target_y = target
        self.x += (target_x - self.x) * ajustes.PLAYER_SMOOTHING
        self.y += (target_y - self.y) * ajustes.PLAYER_SMOOTHING


# Representa cada botella que cae y su estado durante la partida.
class FallingObject:
    # Inicializa la variante indicada con posición y velocidad aleatorias.
    def __init__(self, bottle_variant):
        self.bottle_variant = bottle_variant
        width, height = self.bounds_size
        self.x = random.randint(width // 2, ajustes.WINDOW_WIDTH - width // 2)
        self.y = height // 2
        self.crushed = False
        self.crushed_time = 0.0
        self.hand_touched_open = False
        self.radius = ajustes.BOTTLE_COLLISION_RADIUS
        self.speed = random.uniform(*ajustes.OBJECT_SPEED_RANGE)
        self.phase = random.uniform(0, math.tau)

    # Devuelve el tamaño usado para mantener la botella dentro de la pantalla.
    @property
    def bounds_size(self):
        return (48, ajustes.BOTTLE_SPRITE_SIZE[1])

    # Usa una silueta más baja mientras se muestra una botella aplastada.
    @property
    def sprite_size(self):
        if self.crushed:
            return (48, 18)
        return ajustes.BOTTLE_SPRITE_SIZE

    # Indica si la botella todavía está dentro de los límites visibles.
    @property
    def is_fully_visible(self):
        width, height = self.sprite_size
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (int(self.x), int(self.y))
        return (
            rect.left >= 0
            and rect.top >= 0
            and rect.right <= ajustes.WINDOW_WIDTH
            and rect.bottom <= ajustes.WINDOW_HEIGHT
        )

    # Mueve la botella y gestiona el tiempo durante el que se ve aplastada.
    def update(self, delta_time):
        if self.crushed:
            self.crushed_time = max(0, self.crushed_time - delta_time)
            if self.crushed_time == 0:
                self.y = ajustes.WINDOW_HEIGHT + self.sprite_size[1]
            return
        self.y += self.speed * delta_time
        self.phase += delta_time * ajustes.BOTTLE_PHASE_SPEED
        self.x = max(
            self.bounds_size[0] // 2,
            min(
                self.x + math.sin(self.phase) * ajustes.BOTTLE_SWAY * delta_time,
                ajustes.WINDOW_WIDTH - self.bounds_size[0] // 2,
            ),
        )

    # Dibuja la botella normal o su versión aplastada.
    def draw(self, surface, bottle_sprites, crushed_bottle_sprites):
        center = (int(self.x), int(self.y))
        sprites = crushed_bottle_sprites if self.crushed else bottle_sprites
        sprite = sprites[self.bottle_variant]
        surface.blit(sprite, sprite.get_rect(center=center))

    # Marca la botella como aplastada una sola vez.
    def crush(self):
        if self.crushed:
            return False
        self.crushed = True
        self.crushed_time = ajustes.CRUSHED_BOTTLE_DISPLAY_SECONDS
        return True


# Dibuja una botella vectorial y la escala al tamaño usado por el juego.
def create_bottle_sprite(body_color, edge_color, cap_color, cap_edge_color):
    scale = 3
    width, height = ajustes.BOTTLE_SPRITE_SIZE
    sprite = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)

    # Convierte coordenadas del dibujo a píxeles de la imagen ampliada.
    def point(x, y):
        return int(x * scale), int(y * scale)

    # Traza el contorno del cuerpo y el cuello de la botella.
    body = [
        point(14, 11),
        point(22, 11),
        point(23, 16),
        point(27, 20),
        point(30, 27),
        point(30, 45),
        point(28, 49),
        point(8, 49),
        point(6, 45),
        point(6, 27),
        point(9, 20),
        point(13, 16),
    ]
    pygame.draw.polygon(sprite, body_color, body)
    pygame.draw.polygon(sprite, edge_color, body, max(1, scale))
    pygame.draw.rect(sprite, body_color, (*point(13, 8), 10 * scale, 8 * scale))
    pygame.draw.rect(
        sprite,
        edge_color,
        (*point(13, 8), 10 * scale, 8 * scale),
        max(1, scale),
    )
    # Añade la tapa y sus ranuras para diferenciar mejor cada botella.
    pygame.draw.rect(sprite, cap_color, (*point(11, 2), 14 * scale, 8 * scale))
    pygame.draw.rect(
        sprite,
        cap_edge_color,
        (*point(11, 2), 14 * scale, 8 * scale),
        max(1, scale),
    )
    for x in range(13, 25, 3):
        pygame.draw.line(
            sprite,
            cap_edge_color,
            point(x, 3),
            point(x, 8),
            max(1, scale // 2),
        )
    # Dibuja reflejos para dar volumen al cuerpo de la botella.
    pygame.draw.line(
        sprite,
        ajustes.BOTTLE_HIGHLIGHT_COLOR,
        point(10, 25),
        point(10, 43),
        scale,
    )
    pygame.draw.line(
        sprite,
        ajustes.BOTTLE_HIGHLIGHT_COLOR,
        point(12, 21),
        point(14, 18),
        max(1, scale // 2),
    )
    pygame.draw.line(
        sprite,
        ajustes.BOTTLE_HIGHLIGHT_COLOR,
        point(9, 45),
        point(13, 47),
        max(1, scale // 2),
    )
    return pygame.transform.smoothscale(sprite, ajustes.BOTTLE_SPRITE_SIZE).convert_alpha()


# Crea la imagen aplanada que se muestra después de aplastar una botella.
def create_crushed_bottle_sprite(bottle_sprite):
    return pygame.transform.smoothscale(bottle_sprite, (48, 18)).convert_alpha()


# Renderiza texto y lo alinea respecto de la posición indicada.
def draw_text(
    surface,
    text,
    font,
    color,
    position,
    centered=False,
    right_aligned=False,
):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if centered:
        rect.center = position
    elif right_aligned:
        rect.topright = position
    else:
        rect.topleft = position
    surface.blit(image, rect)
    return rect


# Ajusta el texto a un rectángulo y devuelve la coordenada vertical final.
def draw_wrapped_text(
    surface,
    text,
    font,
    color,
    rect,
    line_spacing=3,
    centered=False,
):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        candidate = f"{current_line} {word}".strip()
        if current_line and font.size(candidate)[0] > rect.width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)

    y = rect.top
    for line in lines:
        image = font.render(line, True, color)
        line_rect = image.get_rect()
        if centered:
            line_rect.midtop = (rect.centerx, y)
        else:
            line_rect.topleft = (rect.left, y)
        surface.blit(image, line_rect)
        y += font.get_linesize() + line_spacing
    return y


# Dibuja un botón con sombra, borde y texto centrado.
def draw_menu_button(surface, rect, label, font, color):
    pygame.draw.rect(surface, (28, 19, 38, 235), rect.move(0, 5), border_radius=17)
    pygame.draw.rect(surface, color, rect, border_radius=17)
    pygame.draw.rect(
        surface,
        (226, 205, 244),
        rect,
        width=2,
        border_radius=17,
    )
    if label == "JUGAR":
        pygame.draw.polygon(
            surface,
            (255, 255, 255),
            [
                (rect.left + 23, rect.centery - 11),
                (rect.left + 23, rect.centery + 11),
                (rect.left + 42, rect.centery),
            ],
        )
        draw_text(
            surface,
            label,
            font,
            (255, 255, 255),
            (rect.centerx + 14, rect.centery),
            centered=True,
        )
    else:
        draw_text(
            surface,
            label,
            font,
            (255, 255, 255),
            rect.center,
            centered=True,
        )


# Dibuja la pantalla inicial, sus instrucciones y los botones del menú.
def draw_start_screen(surface, title_font, subtitle_font, body_font, button_font):
    # Construye el panel principal y presenta el título y la descripción.
    pygame.draw.rect(surface, (24, 21, 29, 190), surface.get_rect())
    panel = pygame.Rect(40, 28, 880, 584)
    pygame.draw.rect(surface, (19, 16, 25, 235), panel.move(0, 7), border_radius=28)
    pygame.draw.rect(surface, (79, 48, 101, 238), panel, border_radius=28)
    pygame.draw.rect(
        surface,
        (222, 195, 239),
        panel,
        width=3,
        border_radius=28,
    )

    draw_text(
        surface,
        "MISIÓN RECICLAJE",
        title_font,
        (255, 255, 255),
        (panel.centerx, 58),
        centered=True,
    )
    draw_text(
        surface,
        "Botellas",
        subtitle_font,
        (238, 213, 255),
        (panel.centerx, 105),
        centered=True,
    )
    draw_text(
        surface,
        "¡La misión de reciclaje comienza ahora!",
        body_font,
        (255, 255, 255),
        (panel.centerx, 146),
        centered=True,
    )
    draw_wrapped_text(
        surface,
        "Usá tu mano frente a la cámara para aplastar las botellas correctas.",
        body_font,
        (245, 239, 250),
        pygame.Rect(92, 178, 776, 44),
        centered=True,
    )

    # Muestra las instrucciones dentro de un panel propio.
    instructions = pygame.Rect(338, 228, 548, 340)
    pygame.draw.rect(surface, (50, 33, 65, 245), instructions, border_radius=22)
    pygame.draw.rect(
        surface,
        (192, 150, 218),
        instructions,
        width=2,
        border_radius=22,
    )
    header = pygame.Rect(instructions.left, instructions.top, instructions.width, 56)
    pygame.draw.rect(
        surface,
        (128, 78, 159),
        header,
        border_top_left_radius=20,
        border_top_right_radius=20,
    )
    draw_text(
        surface,
        "CÓMO JUGAR",
        subtitle_font,
        (255, 255, 255),
        (header.centerx, header.centery),
        centered=True,
    )

    copy = (
        "Antes de comenzar: colocá la mano abierta frente a la cámara y asegurate que haya buena iluminación.",
        "Cerrá la mano para aplastar las botellas indicadas en cada nivel.",
        "Tenés tres vidas para completar la misión y 8 niveles que completar.",
    )
    y = instructions.top + 76
    for paragraph in copy:
        y = draw_wrapped_text(
            surface,
            paragraph,
            body_font,
            (255, 255, 255),
            pygame.Rect(instructions.left + 25, y, instructions.width - 50, 80),
            line_spacing=1,
        ) + 5

    # Dibuja los botones disponibles en el menú.
    button_colors = {
        "JUGAR": (16, 166, 207),
        "CÓMO JUGAR": (133, 78, 167),
        "RANKING": (19, 174, 145),
        "SALIR": (118, 79, 151),
    }
    for label, button_rect in MENU_BUTTON_RECTS.items():
        draw_menu_button(
            surface,
            pygame.Rect(button_rect),
            label,
            button_font,
            button_colors[label],
        )


# Presenta las instrucciones en una capa que se puede cerrar desde el menú.
def draw_instructions_overlay(surface, title_font, body_font):
    panel = pygame.Rect(INSTRUCTIONS_PANEL_RECT)
    # Dibuja el fondo y el encabezado del panel emergente.
    pygame.draw.rect(surface, (18, 14, 25, 245), panel.move(0, 7), border_radius=24)
    pygame.draw.rect(surface, (100, 62, 126), panel, border_radius=24)
    pygame.draw.rect(surface, (226, 203, 242), panel, width=3, border_radius=24)
    header = pygame.Rect(panel.left, panel.top, panel.width, 70)
    pygame.draw.rect(
        surface,
        (132, 79, 165),
        header,
        border_top_left_radius=22,
        border_top_right_radius=22,
    )
    draw_text(
        surface,
        "CÓMO JUGAR",
        title_font,
        (255, 255, 255),
        (panel.centerx, header.centery),
        centered=True,
    )

    # Añade el botón de cierre y el texto de ayuda.
    pygame.draw.rect(
        surface,
        (18, 151, 190),
        pygame.Rect(INSTRUCTIONS_CLOSE_RECT),
        border_radius=12,
    )
    draw_text(
        surface,
        "X",
        body_font,
        (255, 255, 255),
        pygame.Rect(INSTRUCTIONS_CLOSE_RECT).center,
        centered=True,
    )

    copy = (
        "Antes de comenzar: colocá la mano abierta frente a la cámara y asegurate que haya buena iluminación.",
        "Cerrá la mano para aplastar las botellas indicadas en cada nivel.",
        "Tenés tres vidas para completar la misión y 8 niveles que completar.",
    )
    y = panel.top + 96
    for paragraph in copy:
        y = draw_wrapped_text(
            surface,
            paragraph,
            body_font,
            (255, 255, 255),
            pygame.Rect(panel.left + 34, y, panel.width - 68, 80),
            line_spacing=2,
        ) + 12
    draw_text(
        surface,
        "Presioná Esc para volver",
        body_font,
        (238, 213, 255),
        (panel.centerx, panel.bottom - 24),
        centered=True,
    )


# Elige una botella objetivo o una variante incorrecta para el nivel.
def spawn_object(target_variant):
    variants = tuple(ajustes.BOTTLE_VARIANTS)
    if random.random() < ajustes.BOTTLE_TARGET_CHANCE:
        variant = target_variant
    else:
        other_variants = tuple(
            variant for variant in variants if variant != target_variant
        )
        variant = random.choice(other_variants)
    return FallingObject(variant)


# Devuelve los valores iniciales para comenzar una partida nueva.
def reset_game():
    return (
        Player(),
        [],
        0,
        0,
        ajustes.STARTING_LIVES,
        ajustes.LEVELS[0]["time_limit"],
        0.0,
        "playing",
    )


# Carga el ranking, valida sus datos y devuelve las mejores puntuaciones.
def load_ranking():
    if not ajustes.RANKING_PATH.exists():
        return []

    # Rechaza archivos JSON dañados en lugar de ocultar el error.
    try:
        ranking_data = json.loads(ajustes.RANKING_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"El archivo de ranking no tiene un formato valido: {ajustes.RANKING_PATH}"
        ) from error

    # Comprueba que cada registro tenga un nombre y un puntaje válidos.
    if not isinstance(ranking_data, list) or any(
        not isinstance(entry, dict)
        or not isinstance(entry.get("name"), str)
        or type(entry.get("score")) is not int
        or entry["score"] < 0
        for entry in ranking_data
    ):
        raise RuntimeError(
            f"El archivo de ranking contiene datos invalidos: {ajustes.RANKING_PATH}"
        )

    return sorted(
        ranking_data,
        key=lambda entry: (-entry["score"], entry["name"].casefold()),
    )[:ajustes.MAX_RANKING_ENTRIES]


# Agrega una puntuación, conserva el orden y guarda el ranking en disco.
def save_ranking_score(ranking, player_name, score):
    updated_ranking = [*ranking, {"name": player_name, "score": score}]
    updated_ranking.sort(key=lambda entry: (-entry["score"], entry["name"].casefold()))
    updated_ranking = updated_ranking[:ajustes.MAX_RANKING_ENTRIES]
    ajustes.RANKING_PATH.write_text(
        json.dumps(updated_ranking, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return updated_ranking


# Comprueba si el puntaje entra entre las posiciones disponibles del ranking.
def qualifies_for_ranking(ranking, score):
    return (
        len(ranking) < ajustes.MAX_RANKING_ENTRIES
        or score > ranking[-1]["score"]
    )


# Genera el fondo degradado de la barra superior del juego.
def create_hud_background():
    width, height = ajustes.WINDOW_WIDTH, 112
    background = pygame.Surface((width, height))
    start_color = (129, 79, 159)
    end_color = (78, 47, 105)
    for x in range(width):
        ratio = x / max(1, width - 1)
        color = tuple(
            round(start + (end - start) * ratio)
            for start, end in zip(start_color, end_color)
        )
        pygame.draw.line(background, color, (x, 0), (x, height - 1))
    return background


# Dibuja un corazón que representa una vida en la interfaz.
def draw_life_heart(surface, center, color):
    x, y = center
    pygame.draw.circle(surface, color, (x - 5, y - 3), 5)
    pygame.draw.circle(surface, color, (x + 5, y - 3), 5)
    pygame.draw.polygon(
        surface,
        color,
        [(x - 10, y), (x + 10, y), (x, y + 12)],
    )


# Dibuja la información de nivel, tiempo, vidas y controles durante la partida.
def draw_hud(
    surface,
    small_font,
    level_index,
    level_bottles,
    lives,
    remaining,
    game_state,
    bottle_hud_sprites,
    hud_background,
):
    level = ajustes.LEVELS[level_index]
    hud_color = (255, 255, 255)
    warning_color = (255, 205, 132)

    # Pinta el fondo de la barra y separa sus secciones informativas.
    surface.blit(hud_background, (0, 0))
    pygame.draw.line(
        surface,
        (222, 195, 239),
        (0, 109),
        (ajustes.WINDOW_WIDTH, 109),
        2,
    )
    info_cards = (
        pygame.Rect(18, 8, 270, 34),
        pygame.Rect(300, 8, 270, 34),
        pygame.Rect(582, 8, 210, 34),
    )
    warning_active = (
        game_state == "playing" and remaining <= ajustes.TIME_WARNING_SECONDS
    )
    for card in info_cards:
        card_color = (
            (112, 62, 86)
            if warning_active and card == info_cards[2]
            else (71, 47, 88)
        )
        pygame.draw.rect(
            surface,
            card_color,
            card,
            border_radius=12,
        )
        pygame.draw.rect(
            surface,
            (205, 177, 225),
            card,
            width=2,
            border_radius=12,
        )
    draw_text(
        surface,
        f"BOTELLAS  {level_bottles}/{level['bottles_to_collect']}",
        small_font,
        hud_color,
        info_cards[0].center,
        centered=True,
    )
    draw_text(
        surface,
        f"NIVEL {level_index + 1}/{len(ajustes.LEVELS)}",
        small_font,
        hud_color,
        info_cards[1].center,
        centered=True,
    )
    draw_text(
        surface,
        f"TIEMPO  {max(0, math.ceil(remaining)):02d}",
        small_font,
        warning_color if warning_active else hud_color,
        info_cards[2].center,
        centered=True,
    )

    # Muestra el objetivo del nivel y las vidas disponibles.
    target_card = pygame.Rect(18, 50, 620, 52)
    lives_card = pygame.Rect(654, 50, 288, 52)
    for card in (target_card, lives_card):
        pygame.draw.rect(surface, (71, 47, 88), card, border_radius=15)
        pygame.draw.rect(
            surface,
            (205, 177, 225),
            card,
            width=2,
            border_radius=15,
        )
    target_sprite = bottle_hud_sprites[level["bottle_variant"]]
    target_label_width = small_font.size("APLASTA:")[0]
    target_name_width = small_font.size(level["name"])[0]
    target_sprite_width = target_sprite.get_width()
    target_content_width = (
        target_label_width + 12 + target_sprite_width + 8 + target_name_width
    )
    target_left = target_card.centerx - target_content_width // 2
    target_center_y = target_card.centery
    draw_text(
        surface,
        "APLASTA:",
        small_font,
        hud_color,
        (target_left + target_label_width // 2, target_center_y),
        centered=True,
    )
    sprite_left = target_left + target_label_width + 12
    surface.blit(
        target_sprite,
        target_sprite.get_rect(
            midleft=(sprite_left, target_center_y),
        ),
    )
    draw_text(
        surface,
        level["name"],
        small_font,
        hud_color,
        (
            sprite_left + target_sprite_width + 8 + target_name_width // 2,
            target_center_y,
        ),
        centered=True,
    )
    lives_label_width = small_font.size("VIDAS")[0]
    hearts_width = (lives - 1) * 36 + 20 if lives else 0
    lives_content_width = lives_label_width + (16 + hearts_width if lives else 0)
    lives_left = lives_card.centerx - lives_content_width // 2
    draw_text(
        surface,
        "VIDAS",
        small_font,
        hud_color,
        (lives_left + lives_label_width // 2, lives_card.centery),
        centered=True,
    )
    for index in range(lives):
        heart_x = lives_left + lives_label_width + 16 + 10 + index * 36
        draw_life_heart(surface, (heart_x, lives_card.centery), (224, 74, 73))

    # Dibuja los botones para volver al inicio, abrir el ranking y pausar.
    draw_menu_button(
        surface,
        pygame.Rect(RETURN_MENU_BUTTON_RECT),
        "SALIR",
        small_font,
        (118, 79, 151),
    )
    ranking_button = pygame.Rect(RANKING_BUTTON_RECT)
    pygame.draw.rect(surface, (19, 174, 145), ranking_button, border_radius=12)
    pygame.draw.rect(
        surface,
        (226, 205, 244),
        ranking_button,
        width=2,
        border_radius=12,
    )
    trophy_color = (255, 218, 91)
    pygame.draw.polygon(
        surface,
        trophy_color,
        [
            (ranking_button.left + 11, ranking_button.top + 8),
            (ranking_button.right - 11, ranking_button.top + 8),
            (ranking_button.right - 13, ranking_button.top + 21),
            (ranking_button.centerx, ranking_button.top + 26),
            (ranking_button.left + 13, ranking_button.top + 21),
        ],
    )
    pygame.draw.arc(
        surface,
        trophy_color,
        pygame.Rect(ranking_button.left + 5, ranking_button.top + 10, 12, 14),
        math.pi / 2,
        math.pi * 1.5,
        2,
    )
    pygame.draw.arc(
        surface,
        trophy_color,
        pygame.Rect(ranking_button.right - 17, ranking_button.top + 10, 12, 14),
        -math.pi / 2,
        math.pi / 2,
        2,
    )
    pygame.draw.rect(
        surface,
        trophy_color,
        (ranking_button.centerx - 2, ranking_button.top + 24, 4, 5),
    )
    pygame.draw.rect(
        surface,
        trophy_color,
        (ranking_button.centerx - 7, ranking_button.top + 29, 14, 3),
    )

    pause_button = pygame.Rect(PAUSE_BUTTON_RECT)
    pygame.draw.rect(surface, (16, 166, 207), pause_button, border_radius=12)
    pygame.draw.rect(
        surface,
        (226, 205, 244),
        pause_button,
        width=2,
        border_radius=12,
    )
    if game_state == "paused":
        pygame.draw.polygon(
            surface,
            trophy_color,
            [
                (pause_button.left + 13, pause_button.top + 9),
                (pause_button.left + 13, pause_button.bottom - 9),
                (pause_button.right - 10, pause_button.centery),
            ],
        )
    else:
        pygame.draw.rect(
            surface,
            trophy_color,
            (pause_button.left + 11, pause_button.top + 10, 5, 18),
            border_radius=1,
        )
        pygame.draw.rect(
            surface,
            trophy_color,
            (pause_button.left + 22, pause_button.top + 10, 5, 18),
            border_radius=1,
        )


# Muestra las puntuaciones ordenadas y el resultado personal si corresponde.
def draw_ranking_overlay(
    surface,
    font,
    small_font,
    ranking,
    personal_score=None,
    return_to_game=False,
    return_to_menu=False,
):
    panel = pygame.Rect(128, 126, 704, 470)
    # Dibuja el panel y el encabezado del ranking.
    pygame.draw.rect(surface, (19, 16, 25), panel.move(0, 7), border_radius=24)
    pygame.draw.rect(surface, (79, 48, 101), panel, border_radius=24)
    pygame.draw.rect(surface, (222, 195, 239), panel, width=3, border_radius=24)
    header = pygame.Rect(panel.left, panel.top, panel.width, 92)
    pygame.draw.rect(
        surface,
        (128, 78, 159),
        header,
        border_top_left_radius=22,
        border_top_right_radius=22,
    )
    pygame.draw.rect(
        surface,
        (18, 166, 207),
        (panel.left, header.bottom - 8, panel.width, 8),
    )
    draw_text(
        surface,
        "RANKING DE JUGADORES",
        font,
        (255, 255, 255),
        (panel.centerx, panel.top + 34),
        centered=True,
    )
    draw_text(
        surface,
        "LOS 5 MEJORES",
        small_font,
        (238, 213, 255),
        (panel.centerx, panel.top + 68),
        centered=True,
    )

    # Dibuja una fila por puntaje con su posición, nombre y cantidad de botellas.
    for index, entry in enumerate(ranking):
        row = pygame.Rect(
            panel.left + 28,
            panel.top + 112 + index * 49,
            panel.width - 56,
            42,
        )
        row_color = (97, 67, 117) if index % 2 == 0 else (83, 56, 103)
        pygame.draw.rect(surface, row_color, row, border_radius=12)
        pygame.draw.rect(surface, (176, 143, 201), row, width=1, border_radius=12)
        rank_color = (18, 166, 207) if index == 0 else (19, 174, 145)
        pygame.draw.circle(surface, rank_color, (row.left + 23, row.centery), 15)
        draw_text(
            surface,
            str(index + 1),
            small_font,
            (255, 255, 255),
            (row.left + 23, row.centery),
            centered=True,
        )
        name_image = small_font.render(entry["name"], True, (255, 255, 255))
        surface.blit(name_image, name_image.get_rect(midleft=(row.left + 52, row.centery)))
        score_image = small_font.render(
            f"{entry['score']} botellas",
            True,
            (238, 213, 255),
        )
        surface.blit(
            score_image,
            score_image.get_rect(midright=(row.right - 18, row.centery)),
        )

    # Informa cuando el ranking está vacío y resalta un puntaje reciente.
    if not ranking:
        draw_text(
            surface,
            "Aun no hay puntajes guardados.",
            small_font,
            (238, 213, 255),
            (panel.centerx, panel.top + 190),
            centered=True,
        )
    if personal_score is not None:
        score_box = pygame.Rect(
            panel.left + 28,
            panel.bottom - 80,
            panel.width - 56,
            42,
        )
        pygame.draw.rect(surface, (19, 174, 145), score_box, border_radius=13)
        draw_text(
            surface,
            f"Tu puntaje: {personal_score} botellas",
            small_font,
            (255, 255, 255),
            score_box.center,
            centered=True,
        )
    if return_to_menu:
        prompt = "Presiona Esc para volver al inicio"
    elif return_to_game:
        prompt = "Haz clic en la copa para volver"
    else:
        prompt = "Presiona R para volver a jugar"
    draw_text(
        surface,
        prompt,
        small_font,
        (238, 213, 255),
        (panel.centerx, panel.bottom - 24),
        centered=True,
    )


# Dibuja la capa que oscurece la partida y explica cómo reanudarla.
def draw_pause_overlay(surface, font, small_font):
    panel = pygame.Rect(160, 222, 640, 210)
    pygame.draw.rect(surface, (19, 16, 25), panel.move(0, 7), border_radius=24)
    pygame.draw.rect(surface, (79, 48, 101), panel, border_radius=24)
    pygame.draw.rect(surface, (222, 195, 239), panel, width=3, border_radius=24)
    header = pygame.Rect(panel.left, panel.top, panel.width, 76)
    pygame.draw.rect(
        surface,
        (128, 78, 159),
        header,
        border_top_left_radius=22,
        border_top_right_radius=22,
    )
    draw_text(
        surface,
        "JUEGO EN PAUSA",
        font,
        (255, 255, 255),
        (panel.centerx, panel.top + 38),
        centered=True,
    )
    draw_text(
        surface,
        "Pulsa el botón de pausa para continuar",
        small_font,
        (238, 213, 255),
        (panel.centerx, panel.top + 138),
        centered=True,
    )


# Presenta el objetivo y las reglas breves antes de iniciar cada nivel.
def draw_level_intro(
    surface,
    level_index,
    lives,
    seconds_until_start,
    bottle_intro_sprites,
    title_font,
    subtitle_font,
    body_font,
):
    level = ajustes.LEVELS[level_index]

    # Dibuja el fondo, el marco y el encabezado con el número de nivel.
    pygame.draw.rect(surface, (24, 21, 29, 190), surface.get_rect())
    panel = pygame.Rect(70, 48, 820, 544)
    pygame.draw.rect(surface, (19, 16, 25, 235), panel.move(0, 7), border_radius=28)
    pygame.draw.rect(surface, (79, 48, 101, 238), panel, border_radius=28)
    pygame.draw.rect(
        surface,
        (222, 195, 239),
        panel,
        width=3,
        border_radius=28,
    )
    header = pygame.Rect(panel.left, panel.top, panel.width, 78)
    pygame.draw.rect(
        surface,
        (128, 78, 159),
        header,
        border_top_left_radius=26,
        border_top_right_radius=26,
    )
    draw_text(
        surface,
        f"NIVEL {level_index + 1} / {len(ajustes.LEVELS)}",
        title_font,
        (255, 255, 255),
        header.center,
        centered=True,
    )

    # Muestra la botella que se debe aplastar en el nivel.
    bottle_card = pygame.Rect(110, 158, 264, 354)
    pygame.draw.rect(surface, (50, 33, 65), bottle_card, border_radius=22)
    pygame.draw.rect(
        surface,
        (192, 150, 218),
        bottle_card,
        width=2,
        border_radius=22,
    )
    draw_text(
        surface,
        "BOTELLA OBJETIVO",
        subtitle_font,
        (238, 213, 255),
        (bottle_card.centerx, bottle_card.top + 34),
        centered=True,
    )
    pygame.draw.circle(
        surface,
        (91, 63, 110),
        (bottle_card.centerx, bottle_card.centery + 2),
        105,
    )
    target_sprite = bottle_intro_sprites[level["bottle_variant"]]
    surface.blit(target_sprite, target_sprite.get_rect(center=bottle_card.center))
    draw_text(
        surface,
        level["name"],
        body_font,
        (255, 255, 255),
        (bottle_card.centerx, bottle_card.bottom - 26),
        centered=True,
    )

    # Resume el objetivo, el tiempo, las vidas y las reglas del nivel.
    details = pygame.Rect(398, 158, 452, 354)
    pygame.draw.rect(surface, (50, 33, 65), details, border_radius=22)
    pygame.draw.rect(
        surface,
        (192, 150, 218),
        details,
        width=2,
        border_radius=22,
    )
    draw_text(
        surface,
        "APLASTA SOLO",
        subtitle_font,
        (100, 221, 255),
        (details.centerx, details.top + 37),
        centered=True,
    )
    draw_text(
        surface,
        level["name"],
        subtitle_font,
        (255, 255, 255),
        (details.centerx, details.top + 81),
        centered=True,
    )
    draw_text(
        surface,
        f"OBJETIVO: {level['bottles_to_collect']} botellas",
        body_font,
        (255, 255, 255),
        (details.centerx, details.top + 132),
        centered=True,
    )
    draw_text(
        surface,
        f"TIEMPO: {level['time_limit']} segundos",
        body_font,
        (255, 255, 255),
        (details.centerx, details.top + 166),
        centered=True,
    )
    draw_text(
        surface,
        f"VIDAS RESTANTES: {lives}/{ajustes.STARTING_LIVES}",
        body_font,
        (255, 255, 255),
        (details.centerx, details.top + 200),
        centered=True,
    )
    pygame.draw.line(
        surface,
        (192, 150, 218),
        (details.left + 24, details.top + 230),
        (details.right - 24, details.top + 230),
        2,
    )
    draw_wrapped_text(
        surface,
        "Mostrá la mano abierta para identificar las botellas indicadas.",
        body_font,
        (238, 213, 255),
        pygame.Rect(details.left + 18, details.top + 240, details.width - 36, 52),
        line_spacing=0,
        centered=True,
    )
    draw_wrapped_text(
        surface,
        "Las botellas aplastadas de otro color quitan una vida.",
        body_font,
        (238, 213, 255),
        pygame.Rect(details.left + 18, details.top + 296, details.width - 36, 52),
        line_spacing=0,
        centered=True,
    )

    # Indica cuánto falta para que comience la partida.
    countdown = pygame.Rect(398, 526, 452, 42)
    pygame.draw.rect(surface, (16, 166, 207), countdown, border_radius=15)
    pygame.draw.rect(
        surface,
        (226, 205, 244),
        countdown,
        width=2,
        border_radius=15,
    )
    draw_text(
        surface,
        f"COMIENZA EN {max(1, math.ceil(seconds_until_start))}",
        body_font,
        (255, 255, 255),
        countdown.center,
        centered=True,
    )


# Inicializa los recursos y ejecuta el ciclo principal del juego.
def main():
    # Prepara Pygame y detiene el inicio si no se puede activar el audio.
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as error:
        pygame.quit()
        raise RuntimeError(f"No se pudo iniciar el audio: {error}") from error

    # Crea la ventana, las superficies de dibujo, las fuentes y el reloj.
    display_flags = pygame.FULLSCREEN if ajustes.FULLSCREEN else 0
    display_size = (0, 0) if ajustes.FULLSCREEN else (
        ajustes.WINDOW_WIDTH,
        ajustes.WINDOW_HEIGHT,
    )
    display = pygame.display.set_mode(display_size, display_flags)
    screen = pygame.Surface(
        (ajustes.WINDOW_WIDTH, ajustes.WINDOW_HEIGHT),
        pygame.SRCALPHA,
    )
    display_overlay = pygame.Surface(display.get_size(), pygame.SRCALPHA)
    pygame.display.set_caption(ajustes.WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, ajustes.FONT_SIZE)
    small_font = pygame.font.Font(None, ajustes.SMALL_FONT_SIZE)
    menu_title_font = pygame.font.Font(None, 48)
    menu_subtitle_font = pygame.font.Font(None, 32)
    menu_body_font = pygame.font.Font(None, 22)
    menu_button_font = pygame.font.Font(None, 27)

    # Carga sonidos y prepara las variantes de botella para cada pantalla.
    hud_background = create_hud_background()
    collect_sound = pygame.mixer.Sound(str(ajustes.SOUND_COLLECT_PATH))
    hit_sound = pygame.mixer.Sound(str(ajustes.SOUND_HIT_PATH))
    collect_sound.set_volume(0.45)
    hit_sound.set_volume(0.55)
    bottle_sprites = {
        variant: create_bottle_sprite(*colors)
        for variant, colors in ajustes.BOTTLE_VARIANTS.items()
    }
    bottle_hud_sprites = {
        variant: pygame.transform.smoothscale(sprite, (25, 36))
        for variant, sprite in bottle_sprites.items()
    }
    bottle_intro_sprites = {
        variant: pygame.transform.smoothscale(sprite, (150, 220))
        for variant, sprite in bottle_sprites.items()
    }
    crushed_bottle_sprites = {
        variant: create_crushed_bottle_sprite(sprite)
        for variant, sprite in bottle_sprites.items()
    }
    ranking = load_ranking()

    # Abre la cámara y comunica el error si no está disponible.
    vision = Vision(ajustes.CAMERA_INDEX, display.get_size())
    if not vision.is_opened:
        vision.release()
        pygame.quit()
        raise RuntimeError(
            "No se pudo abrir la cámara. Conectala y revisá los permisos antes de ejecutar el juego."
        )

    # Inicializa el estado del menú, el nivel y los datos de la partida.
    player, objects, level_bottles, total_bottles, lives, remaining, spawn_elapsed, game_state = reset_game()
    game_state = "menu"
    level_index = 0
    level_banner_time = ajustes.LEVEL_BANNER_SECONDS
    player_name = ""
    name_entry_error = ""
    result_state = ""
    ranking_open = False
    menu_overlay = ""
    running = True
    try:
        # Repite la actualización, atención de eventos y dibujo de cada fotograma.
        while running:
            delta_time = min(clock.tick(ajustes.FPS) / 1000, ajustes.MAX_DELTA_TIME)

            # Reduce el tiempo de presentación del nivel antes de jugar.
            if (
                game_state == "playing"
                and not ranking_open
                and level_banner_time > 0
            ):
                level_banner_time = max(0, level_banner_time - delta_time)

            # Procesa el cierre de ventana y las acciones del teclado y el ratón.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Finaliza el ciclo principal al cerrar la ventana.
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Esc cierra primero los paneles y, si no hay ninguno, el juego.
                    if game_state == "menu" and menu_overlay:
                        menu_overlay = ""
                    elif ranking_open:
                        ranking_open = False
                    else:
                        running = False
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    # Ajusta el clic al sistema de coordenadas interno del juego.
                    mouse_x = round(
                        event.pos[0] * ajustes.WINDOW_WIDTH / display.get_width()
                    )
                    mouse_y = round(
                        event.pos[1] * ajustes.WINDOW_HEIGHT / display.get_height()
                    )
                    mouse_position = (mouse_x, mouse_y)

                    # Convierte los clics en acciones según la pantalla activa.
                    if game_state == "menu":
                        # Cierra el panel abierto o activa un botón del menú.
                        if menu_overlay == "instructions":
                            if pygame.Rect(INSTRUCTIONS_CLOSE_RECT).collidepoint(
                                mouse_position
                            ):
                                menu_overlay = ""
                        elif menu_overlay == "ranking":
                            if not pygame.Rect(RANKING_PANEL_RECT).collidepoint(
                                mouse_position
                            ):
                                menu_overlay = ""
                        else:
                            for label, button_rect in MENU_BUTTON_RECTS.items():
                                if not pygame.Rect(button_rect).collidepoint(
                                    mouse_position
                                ):
                                    continue
                                if label == "JUGAR":
                                    (
                                        player,
                                        objects,
                                        level_bottles,
                                        total_bottles,
                                        lives,
                                        remaining,
                                        spawn_elapsed,
                                        game_state,
                                    ) = reset_game()
                                    level_index = 0
                                    level_banner_time = ajustes.LEVEL_BANNER_SECONDS
                                    player_name = ""
                                    name_entry_error = ""
                                    result_state = ""
                                    ranking_open = False
                                    menu_overlay = ""
                                elif label == "CÓMO JUGAR":
                                    menu_overlay = "instructions"
                                elif label == "RANKING":
                                    menu_overlay = "ranking"
                                elif label == "SALIR":
                                    game_state = "menu"
                                    menu_overlay = ""
                                    ranking_open = False
                                break
                    elif game_state in {"playing", "paused"} and (
                        game_state == "paused" or level_banner_time <= 0
                    ):
                        # Gestiona los controles de volver, ranking y pausa.
                        if pygame.Rect(RETURN_MENU_BUTTON_RECT).collidepoint(
                            mouse_position
                        ):
                            game_state = "menu"
                            ranking_open = False
                            menu_overlay = ""
                        elif pygame.Rect(RANKING_BUTTON_RECT).collidepoint(
                            mouse_position
                        ):
                            # Abre o cierra el ranking superpuesto a la partida.
                            ranking_open = not ranking_open
                        elif ranking_open:
                            ranking_open = False
                        elif pygame.Rect(PAUSE_BUTTON_RECT).collidepoint(mouse_position):
                            # Alterna la pausa y cancela cualquier contacto en curso.
                            game_state = (
                                "playing" if game_state == "paused" else "paused"
                            )
                            for falling_object in objects:
                                falling_object.hand_touched_open = False
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_p
                    and game_state in {"playing", "paused"}
                    and not ranking_open
                ):
                    # La tecla P alterna la pausa y desarma los contactos pendientes.
                    game_state = "playing" if game_state == "paused" else "paused"
                    for falling_object in objects:
                        falling_object.hand_touched_open = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # La tecla R reinicia desde las pantallas de resultado.
                    if game_state in {"ranking", "ranking_result"}:
                        (
                            player,
                            objects,
                            level_bottles,
                            total_bottles,
                            lives,
                            remaining,
                            spawn_elapsed,
                            game_state,
                        ) = reset_game()
                        level_index = 0
                        level_banner_time = ajustes.LEVEL_BANNER_SECONDS
                        player_name = ""
                        name_entry_error = ""
                        result_state = ""
                        ranking_open = False
                elif game_state == "enter_name" and event.type == pygame.KEYDOWN:
                    # Permite editar el nombre y guardar el puntaje al presionar Enter.
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if player_name.strip():
                            ranking = save_ranking_score(
                                ranking,
                                player_name.strip(),
                                total_bottles,
                            )
                            game_state = "ranking"
                            name_entry_error = ""
                        else:
                            name_entry_error = "Escribe tu nombre antes de continuar."
                    elif event.unicode and event.unicode.isprintable():
                        if len(player_name) < ajustes.MAX_PLAYER_NAME_LENGTH:
                            player_name += event.unicode

            # Lee la mano detectada y prepara una superficie transparente para dibujar.
            hand_state = vision.read_hand_state()
            camera_position = hand_state.position if hand_state is not None else None
            screen.fill((0, 0, 0, 0))

            if (
                game_state == "playing"
                and not ranking_open
                and level_banner_time <= 0
            ):
                # Actualiza el tiempo, la posición del jugador y la aparición de botellas.
                remaining -= delta_time
                player.follow(camera_position)
                if hand_state is not None:
                    player.radius = hand_state.radius
                spawn_elapsed += delta_time
                level = ajustes.LEVELS[level_index]
                target_bottles = level["bottles_to_collect"]
                if (
                    level_bottles < target_bottles
                    and spawn_elapsed >= ajustes.SPAWN_INTERVAL
                ):
                    objects.append(spawn_object(level["bottle_variant"]))
                    spawn_elapsed -= ajustes.SPAWN_INTERVAL

                # Comprueba contactos: la mano abierta prepara y el cierre aplasta.
                for falling_object in objects:
                    falling_object.update(delta_time)
                    if falling_object.crushed:
                        continue
                    if hand_state is None:
                        falling_object.hand_touched_open = False
                        continue

                    distance = math.hypot(
                        falling_object.x - player.x,
                        falling_object.y - player.y,
                    )
                    touch_distance = falling_object.radius + hand_state.radius
                    if hand_state.is_open:
                        if distance < touch_distance:
                            falling_object.hand_touched_open = True
                        elif distance > (
                            touch_distance + ajustes.HAND_TOUCH_RELEASE_MARGIN
                        ):
                            falling_object.hand_touched_open = False
                    elif falling_object.hand_touched_open:
                        if distance < (
                            touch_distance + ajustes.HAND_TOUCH_RELEASE_MARGIN
                        ):
                            if falling_object.crush():
                                if falling_object.bottle_variant == level["bottle_variant"]:
                                    level_bottles += 1
                                    total_bottles += 1
                                    collect_sound.play()
                                else:
                                    lives -= 1
                                    hit_sound.play()
                        else:
                            falling_object.hand_touched_open = False

                # Retira botellas fuera de pantalla y determina el resultado del nivel.
                objects = [
                    falling_object
                    for falling_object in objects
                    if falling_object.is_fully_visible
                ]

                level_complete = (
                    level_bottles >= target_bottles
                    and not any(falling_object.crushed for falling_object in objects)
                )
                if level_complete:
                    if level_index == len(ajustes.LEVELS) - 1:
                        result_state = "won"
                        game_state = (
                            "enter_name"
                            if qualifies_for_ranking(ranking, total_bottles)
                            else "ranking_result"
                        )
                    else:
                        level_index += 1
                        level_bottles = 0
                        objects = []
                        remaining = ajustes.LEVELS[level_index]["time_limit"]
                        spawn_elapsed = 0.0
                        level_banner_time = ajustes.LEVEL_BANNER_SECONDS
                elif lives <= 0 or remaining <= 0:
                    result_state = "lost"
                    game_state = (
                        "enter_name"
                        if qualifies_for_ranking(ranking, total_bottles)
                        else "ranking_result"
                    )

            # Dibuja las botellas y la barra de información cuando corresponde.
            if game_state != "menu" and (
                level_banner_time <= 0 or game_state == "paused"
            ):
                for falling_object in objects:
                    falling_object.draw(
                        screen,
                        bottle_sprites,
                        crushed_bottle_sprites,
                    )
                draw_hud(
                    screen,
                    small_font,
                    level_index,
                    level_bottles,
                    lives,
                    remaining,
                    game_state,
                    bottle_hud_sprites,
                    hud_background,
                )

            # Avisa al jugador si la cámara no detecta una mano durante la partida.
            if (
                camera_position is None
                and game_state == "playing"
                and level_banner_time <= 0
            ):
                warning_panel = pygame.Rect(
                    ajustes.WINDOW_WIDTH // 2 - 250,
                    ajustes.WINDOW_HEIGHT - 104,
                    500,
                    84,
                )
                pygame.draw.rect(
                    screen,
                    (18, 14, 25, 245),
                    warning_panel.move(0, 5),
                    border_radius=18,
                )
                pygame.draw.rect(
                    screen,
                    (50, 33, 65),
                    warning_panel,
                    border_radius=18,
                )
                pygame.draw.rect(
                    screen,
                    (192, 150, 218),
                    warning_panel,
                    width=2,
                    border_radius=18,
                )
                draw_text(
                    screen,
                    "No detecto la mano.",
                    menu_body_font,
                    ajustes.WARNING_COLOR,
                    (warning_panel.centerx, warning_panel.top + 27),
                    centered=True,
                )
                draw_text(
                    screen,
                    "Mostrá la mano frente a la cámara.",
                    menu_body_font,
                    ajustes.WARNING_COLOR,
                    (warning_panel.centerx, warning_panel.top + 57),
                    centered=True,
                )

            # Dibuja la pantalla o capa correspondiente al estado actual del juego.
            if game_state == "menu":
                draw_start_screen(
                    screen,
                    menu_title_font,
                    menu_subtitle_font,
                    menu_body_font,
                    menu_button_font,
                )
                if menu_overlay == "instructions":
                    draw_instructions_overlay(
                        screen,
                        menu_title_font,
                        menu_body_font,
                    )
                elif menu_overlay == "ranking":
                    draw_ranking_overlay(
                        screen,
                        font,
                        small_font,
                        ranking,
                        return_to_menu=True,
                    )
            elif ranking_open:
                draw_ranking_overlay(
                    screen,
                    font,
                    small_font,
                    ranking,
                    return_to_game=True,
                )
            elif game_state == "playing" and level_banner_time > 0:
                draw_level_intro(
                    screen,
                    level_index,
                    lives,
                    level_banner_time,
                    bottle_intro_sprites,
                    menu_title_font,
                    menu_subtitle_font,
                    menu_body_font,
                )
            elif game_state == "paused":
                draw_pause_overlay(screen, font, small_font)
            elif game_state == "enter_name":
                # Presenta el resultado y permite escribir el nombre para el ranking.
                panel = pygame.Rect(145, 140, 670, 360)
                pygame.draw.rect(screen, (16, 42, 30), panel.move(0, 7), border_radius=24)
                pygame.draw.rect(screen, (255, 250, 232), panel, border_radius=24)
                pygame.draw.rect(screen, (0, 116, 72), panel, width=3, border_radius=24)
                header = pygame.Rect(panel.left, panel.top, panel.width, 88)
                pygame.draw.rect(
                    screen,
                    (239, 133, 57),
                    header,
                    border_top_left_radius=22,
                    border_top_right_radius=22,
                )
                pygame.draw.rect(
                    screen,
                    (255, 207, 72),
                    (panel.left, header.bottom - 8, panel.width, 8),
                )
                headline = (
                    "¡PLANETA LIMPIO!"
                    if result_state == "won"
                    else "SE ACABÓ EL TIEMPO O LAS VIDAS"
                )
                color = (
                    (255, 255, 255)
                    if result_state == "won"
                    else (255, 246, 223)
                )
                draw_text(
                    screen,
                    headline,
                    font if result_state == "won" else small_font,
                    color,
                    (panel.centerx, panel.top + 44),
                    centered=True,
                )
                score_box = pygame.Rect(panel.left + 72, panel.top + 112, panel.width - 144, 48)
                pygame.draw.rect(screen, (255, 225, 133), score_box, border_radius=14)
                draw_text(
                    screen,
                    f"Puntaje: {total_bottles} botellas",
                    small_font,
                    (0, 76, 52),
                    score_box.center,
                    centered=True,
                )
                draw_text(
                    screen,
                    "Escribe tu nombre y presiona Enter:",
                    small_font,
                    (0, 76, 52),
                    (panel.centerx, panel.top + 190),
                    centered=True,
                )
                name_box = pygame.Rect(
                    panel.centerx - 210,
                    panel.top + 220,
                    420,
                    48,
                )
                pygame.draw.rect(screen, (255, 255, 255), name_box, border_radius=12)
                pygame.draw.rect(screen, (69, 160, 112), name_box, width=2, border_radius=12)
                name_image = small_font.render(
                    player_name or "Tu nombre",
                    True,
                    (0, 76, 52) if player_name else (120, 139, 155),
                )
                screen.blit(name_image, name_image.get_rect(center=name_box.center))
                if name_entry_error:
                    draw_text(
                        screen,
                        name_entry_error,
                        small_font,
                        (164, 64, 46),
                        (panel.centerx, panel.bottom - 22),
                        centered=True,
                    )

            elif game_state in {"ranking", "ranking_result"}:
                # Muestra el ranking al terminar una partida.
                draw_ranking_overlay(
                    screen,
                    font,
                    small_font,
                    ranking,
                    personal_score=(
                        total_bottles if game_state == "ranking_result" else None
                    ),
                )

            # Compone la imagen de cámara y la interfaz antes de presentar el fotograma.
            if vision.camera_surface is None:
                display.fill((0, 0, 0))
            else:
                display.blit(vision.camera_surface, (0, 0))
            pygame.transform.smoothscale(
                screen,
                display.get_size(),
                display_overlay,
            )
            display.blit(display_overlay, (0, 0))
            pygame.display.flip()
    finally:
        # Libera la cámara y cierra Pygame incluso si ocurre un error en el ciclo.
        vision.release()
        pygame.quit()

    return 0


# Ejecuta el juego cuando este archivo se inicia directamente.
if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        # Informa errores de inicio y devuelve un código de salida distinto de cero.
        print(error, file=sys.stderr)
        sys.exit(1)
