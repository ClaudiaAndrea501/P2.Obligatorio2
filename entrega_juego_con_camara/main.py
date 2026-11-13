import math
import json
import random
import sys

import pygame

import ajustes
from vision import Vision


RANKING_BUTTON_RECT = (914, 7, 38, 38)
PAUSE_BUTTON_RECT = (870, 7, 38, 38)


class Player:
    def __init__(self):
        self.x = ajustes.WINDOW_WIDTH / 2
        self.y = ajustes.WINDOW_HEIGHT - 95
        self.radius = ajustes.PLAYER_RADIUS

    def follow(self, target):
        if target is None:
            return
        target_x, target_y = target
        self.x += (target_x - self.x) * ajustes.PLAYER_SMOOTHING
        self.y += (target_y - self.y) * ajustes.PLAYER_SMOOTHING

class FallingObject:
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

    @property
    def bounds_size(self):
        return (48, ajustes.BOTTLE_SPRITE_SIZE[1])

    @property
    def sprite_size(self):
        if self.crushed:
            return (48, 18)
        return ajustes.BOTTLE_SPRITE_SIZE

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

    def draw(self, surface, bottle_sprites, crushed_bottle_sprites):
        center = (int(self.x), int(self.y))
        sprites = crushed_bottle_sprites if self.crushed else bottle_sprites
        sprite = sprites[self.bottle_variant]
        surface.blit(sprite, sprite.get_rect(center=center))

    def crush(self):
        if self.crushed:
            return False
        self.crushed = True
        self.crushed_time = ajustes.CRUSHED_BOTTLE_DISPLAY_SECONDS
        return True


def create_bottle_sprite(body_color, edge_color, cap_color, cap_edge_color):
    scale = 3
    width, height = ajustes.BOTTLE_SPRITE_SIZE
    sprite = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)

    def point(x, y):
        return int(x * scale), int(y * scale)

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
    pygame.draw.line(sprite, ajustes.BOTTLE_HIGHLIGHT_COLOR, point(10, 25), point(10, 43), scale)
    pygame.draw.line(sprite, ajustes.BOTTLE_HIGHLIGHT_COLOR, point(12, 21), point(14, 18), max(1, scale // 2))
    pygame.draw.line(sprite, ajustes.BOTTLE_HIGHLIGHT_COLOR, point(9, 45), point(13, 47), max(1, scale // 2))
    pygame.draw.rect(sprite, (195, 255, 240, 100), (*point(12, 30), 12 * scale, 8 * scale))

    label_font = pygame.font.Font(None, 11 * scale)
    label = label_font.render("ECO", True, ajustes.BOTTLE_LABEL_COLOR)
    sprite.blit(label, label.get_rect(center=point(18, 34)))
    return pygame.transform.smoothscale(sprite, ajustes.BOTTLE_SPRITE_SIZE).convert_alpha()


def create_crushed_bottle_sprite(bottle_sprite):
    return pygame.transform.smoothscale(bottle_sprite, (48, 18)).convert_alpha()


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


def load_ranking():
    if not ajustes.RANKING_PATH.exists():
        return []

    try:
        ranking_data = json.loads(ajustes.RANKING_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"El archivo de ranking no tiene un formato valido: {ajustes.RANKING_PATH}"
        ) from error

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


def save_ranking_score(ranking, player_name, score):
    updated_ranking = [*ranking, {"name": player_name, "score": score}]
    updated_ranking.sort(key=lambda entry: (-entry["score"], entry["name"].casefold()))
    updated_ranking = updated_ranking[:ajustes.MAX_RANKING_ENTRIES]
    ajustes.RANKING_PATH.write_text(
        json.dumps(updated_ranking, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return updated_ranking


def qualifies_for_ranking(ranking, score):
    return (
        len(ranking) < ajustes.MAX_RANKING_ENTRIES
        or score > ranking[-1]["score"]
    )


def draw_camera_background(surface, camera_surface):
    if camera_surface is None:
        surface.fill((0, 0, 0))
    else:
        surface.blit(camera_surface, (0, 0))


def draw_hud(
    surface,
    small_font,
    level_index,
    level_bottles,
    lives,
    remaining,
    game_state,
    bottle_hud_sprites,
):
    level = ajustes.LEVELS[level_index]
    hud_height = 112
    hud_color = ajustes.BOTTLE_CAP_COLOR[:3]
    pygame.draw.rect(surface, (255, 255, 255), (0, 0, ajustes.WINDOW_WIDTH, hud_height))
    pygame.draw.line(
        surface,
        hud_color,
        (0, hud_height - 1),
        (ajustes.WINDOW_WIDTH, hud_height - 1),
        2,
    )
    draw_text(
        surface,
        f"BOTELLAS  {level_bottles}/{level['bottles_to_collect']}",
        small_font,
        hud_color,
        (24, 10),
    )
    draw_text(
        surface,
        "APLASTA:",
        small_font,
        hud_color,
        (24, 43),
    )
    target_sprite = bottle_hud_sprites[level["bottle_variant"]]
    surface.blit(target_sprite, target_sprite.get_rect(topleft=(141, 41)))
    draw_text(
        surface,
        level["name"],
        small_font,
        hud_color,
        (174, 43),
    )
    draw_text(
        surface,
        f"VIDAS  {'♥ ' * lives}",
        small_font,
        hud_color,
        (24, 76),
    )
    draw_text(
        surface,
        f"NIVEL {level_index + 1}/{len(ajustes.LEVELS)}",
        small_font,
        hud_color,
        (365, 10),
    )
    draw_text(
        surface,
        f"TIEMPO  {max(0, math.ceil(remaining)):02d}",
        small_font,
        hud_color,
        (860, 10),
        right_aligned=True,
    )
    if game_state == "playing" and remaining <= ajustes.TIME_WARNING_SECONDS:
        draw_text(
            surface,
            "¡ÚLTIMOS SEGUNDOS!",
            small_font,
            hud_color,
            (ajustes.WINDOW_WIDTH - 24, 52),
            right_aligned=True,
        )
    ranking_button = pygame.Rect(RANKING_BUTTON_RECT)
    pygame.draw.rect(
        surface,
        hud_color,
        ranking_button,
        border_radius=7,
    )
    trophy_color = (255, 255, 255)
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
    pygame.draw.rect(surface, hud_color, pause_button, border_radius=7)
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


def draw_ranking_overlay(
    surface,
    font,
    small_font,
    ranking,
    personal_score=None,
    return_to_game=False,
):
    overlay_rect = pygame.Rect(
        0,
        112,
        ajustes.WINDOW_WIDTH,
        ajustes.WINDOW_HEIGHT - 112,
    )
    overlay = pygame.Surface(overlay_rect.size, pygame.SRCALPHA)
    overlay.fill((5, 9, 24, 215))
    surface.blit(overlay, overlay_rect.topleft)
    draw_text(
        surface,
        "MEJORES 5 JUGADORES",
        font,
        ajustes.BOTTLE_EDGE_COLOR[:3],
        (ajustes.WINDOW_WIDTH // 2, 150),
        centered=True,
    )
    for index, entry in enumerate(ranking):
        line = f"{index + 1:>2}.  {entry['name']:<16}  {entry['score']:>3} botellas"
        draw_text(
            surface,
            line,
            small_font,
            ajustes.WHITE,
            (ajustes.WINDOW_WIDTH // 2, 205 + index * 38),
            centered=True,
        )
    if not ranking:
        draw_text(
            surface,
            "Aun no hay puntajes guardados.",
            small_font,
            ajustes.WHITE,
            (ajustes.WINDOW_WIDTH // 2, 210),
            centered=True,
        )
    if personal_score is not None:
        draw_text(
            surface,
            f"Tu puntaje: {personal_score} botellas",
            small_font,
            ajustes.WHITE,
            (ajustes.WINDOW_WIDTH // 2, 430),
            centered=True,
        )
    prompt = (
        "Haz clic en la copa para volver"
        if return_to_game
        else "Presiona R para volver a jugar"
    )
    draw_text(
        surface,
        prompt,
        small_font,
        ajustes.WHITE,
        (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT - 36),
        centered=True,
    )


def draw_pause_overlay(surface, font, small_font):
    overlay_rect = pygame.Rect(
        0,
        112,
        ajustes.WINDOW_WIDTH,
        ajustes.WINDOW_HEIGHT - 112,
    )
    overlay = pygame.Surface(overlay_rect.size, pygame.SRCALPHA)
    overlay.fill((5, 9, 24, 165))
    surface.blit(overlay, overlay_rect.topleft)
    draw_text(
        surface,
        "JUEGO EN PAUSA",
        font,
        ajustes.WHITE,
        (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT // 2),
        centered=True,
    )
    draw_text(
        surface,
        "Pulsa el botón de pausa para continuar",
        small_font,
        ajustes.WHITE,
        (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT // 2 + 48),
        centered=True,
    )


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as error:
        pygame.quit()
        raise RuntimeError(f"No se pudo iniciar el audio: {error}") from error

    display_flags = pygame.FULLSCREEN if ajustes.FULLSCREEN else 0
    display_size = (0, 0) if ajustes.FULLSCREEN else (
        ajustes.WINDOW_WIDTH,
        ajustes.WINDOW_HEIGHT,
    )
    display = pygame.display.set_mode(display_size, display_flags)
    screen = pygame.Surface((ajustes.WINDOW_WIDTH, ajustes.WINDOW_HEIGHT))
    pygame.display.set_caption(ajustes.WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, ajustes.FONT_SIZE)
    small_font = pygame.font.Font(None, ajustes.SMALL_FONT_SIZE)
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
    crushed_bottle_sprites = {
        variant: create_crushed_bottle_sprite(sprite)
        for variant, sprite in bottle_sprites.items()
    }
    ranking = load_ranking()

    vision = Vision(ajustes.CAMERA_INDEX)
    if not vision.is_opened:
        vision.release()
        pygame.quit()
        raise RuntimeError(
            "No se pudo abrir la cámara. Conectala y revisá los permisos antes de ejecutar el juego."
        )

    player, objects, level_bottles, total_bottles, lives, remaining, spawn_elapsed, game_state = reset_game()
    level_index = 0
    level_banner_time = ajustes.LEVEL_BANNER_SECONDS
    player_name = ""
    name_entry_error = ""
    result_state = ""
    ranking_open = False
    running = True
    try:
        while running:
            delta_time = min(clock.tick(ajustes.FPS) / 1000, ajustes.MAX_DELTA_TIME)
            if game_state == "playing" and not ranking_open:
                level_banner_time = max(0, level_banner_time - delta_time)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if ranking_open:
                        ranking_open = False
                    else:
                        running = False
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and game_state in {"playing", "paused"}
                ):
                    mouse_x = round(
                        event.pos[0] * ajustes.WINDOW_WIDTH / display.get_width()
                    )
                    mouse_y = round(
                        event.pos[1] * ajustes.WINDOW_HEIGHT / display.get_height()
                    )
                    mouse_position = (mouse_x, mouse_y)
                    if pygame.Rect(RANKING_BUTTON_RECT).collidepoint(mouse_position):
                        ranking_open = not ranking_open
                    elif ranking_open:
                        ranking_open = False
                    elif pygame.Rect(PAUSE_BUTTON_RECT).collidepoint(mouse_position):
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
                    game_state = "playing" if game_state == "paused" else "paused"
                    for falling_object in objects:
                        falling_object.hand_touched_open = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
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

            hand_state = vision.read_hand_state()
            camera_position = hand_state.position if hand_state is not None else None
            draw_camera_background(screen, vision.camera_surface)

            if game_state == "playing" and not ranking_open:
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
            )

            if level_banner_time > 0 and game_state == "playing":
                level = ajustes.LEVELS[level_index]
                draw_text(
                    screen,
                    f"APLASTA SOLO: {level['name']}",
                    font,
                    level["text_color"],
                    (ajustes.WINDOW_WIDTH // 2, 176),
                    centered=True,
                )
                draw_text(
                    screen,
                    f"Consigue {level['bottles_to_collect']} botellas objetivo",
                    small_font,
                    level["text_color"],
                    (ajustes.WINDOW_WIDTH // 2, 220),
                    centered=True,
                )
                draw_text(
                    screen,
                    "Toca con la mano abierta y ciérrala para aplastar",
                    small_font,
                    level["text_color"],
                    (ajustes.WINDOW_WIDTH // 2, 258),
                    centered=True,
                )

            if camera_position is None and game_state == "playing":
                draw_text(
                    screen,
                    "No detecto la mano",
                    small_font,
                    ajustes.WARNING_COLOR,
                    (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT - 52),
                    centered=True,
                )
                draw_text(
                    screen,
                    "Muestra la mano abierta frente a la cámara",
                    small_font,
                    ajustes.WARNING_COLOR,
                    (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT - 22),
                    centered=True,
                )

            if ranking_open:
                draw_ranking_overlay(
                    screen,
                    font,
                    small_font,
                    ranking,
                    return_to_game=True,
                )
            elif game_state == "paused":
                draw_pause_overlay(screen, font, small_font)
            elif game_state == "enter_name":
                overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                overlay.fill((5, 9, 24, 210))
                screen.blit(overlay, (0, 0))
                headline = (
                    "¡PLANETA LIMPIO!"
                    if result_state == "won"
                    else "SE ACABÓ EL TIEMPO O LAS VIDAS"
                )
                color = (
                    ajustes.BOTTLE_EDGE_COLOR[:3]
                    if result_state == "won"
                    else ajustes.WARNING_COLOR
                )
                draw_text(
                    screen,
                    headline,
                    font,
                    color,
                    (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT // 2 - 35),
                    centered=True,
                )
                draw_text(
                    screen,
                    f"Puntaje: {total_bottles} botellas",
                    small_font,
                    ajustes.WHITE,
                    (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT // 2 + 4),
                    centered=True,
                )
                draw_text(
                    screen,
                    "Escribe tu nombre y presiona Enter:",
                    small_font,
                    ajustes.WHITE,
                    (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT // 2 + 48),
                    centered=True,
                )
                name_box = pygame.Rect(
                    ajustes.WINDOW_WIDTH // 2 - 190,
                    ajustes.WINDOW_HEIGHT // 2 + 72,
                    380,
                    48,
                )
                pygame.draw.rect(screen, (245, 250, 255), name_box, border_radius=8)
                name_image = small_font.render(
                    player_name or "Tu nombre",
                    True,
                    (24, 73, 113) if player_name else (120, 139, 155),
                )
                screen.blit(name_image, name_image.get_rect(center=name_box.center))
                if name_entry_error:
                    draw_text(
                        screen,
                        name_entry_error,
                        small_font,
                        ajustes.WARNING_COLOR,
                        (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT // 2 + 146),
                        centered=True,
                    )

            elif game_state in {"ranking", "ranking_result"}:
                draw_ranking_overlay(
                    screen,
                    font,
                    small_font,
                    ranking,
                    personal_score=(
                        total_bottles if game_state == "ranking_result" else None
                    ),
                )

            pygame.transform.smoothscale(screen, display.get_size(), display)
            pygame.display.flip()
    finally:
        vision.release()
        pygame.quit()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
