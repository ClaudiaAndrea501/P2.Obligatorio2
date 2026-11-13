import math
import json
import random
import sys

import pygame

import ajustes
from vision import Vision


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
    def __init__(self, kind):
        self.kind = kind
        self.x = random.randint(ajustes.OBJECT_RADIUS, ajustes.WINDOW_WIDTH - ajustes.OBJECT_RADIUS)
        self.y = -ajustes.OBJECT_RADIUS
        self.crushed = False
        self.crushed_time = 0.0
        self.hand_touched_open = False
        self.radius = (
            ajustes.BOTTLE_COLLISION_RADIUS
            if kind == "bottle"
            else ajustes.BATTERY_COLLISION_RADIUS
        )
        self.speed = random.uniform(*ajustes.OBJECT_SPEED_RANGE)
        self.phase = random.uniform(0, math.tau)

    def update(self, delta_time):
        if self.crushed:
            self.crushed_time = max(0, self.crushed_time - delta_time)
            if self.crushed_time == 0:
                self.y = ajustes.WINDOW_HEIGHT + self.radius
            return
        self.y += self.speed * delta_time
        self.phase += delta_time * ajustes.BOTTLE_PHASE_SPEED
        if self.kind == "bottle":
            self.x += math.sin(self.phase) * ajustes.BOTTLE_SWAY * delta_time

    def draw(self, surface, bottle_sprite, battery_sprite, crushed_bottle_sprite):
        center = (int(self.x), int(self.y))
        if self.kind == "bottle":
            sprite = crushed_bottle_sprite if self.crushed else bottle_sprite
            surface.blit(sprite, sprite.get_rect(center=center))
        else:
            surface.blit(battery_sprite, battery_sprite.get_rect(center=center))

    def crush(self):
        if self.kind != "bottle" or self.crushed:
            return False
        self.crushed = True
        self.crushed_time = ajustes.CRUSHED_BOTTLE_DISPLAY_SECONDS
        return True


def create_bottle_sprite():
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
    pygame.draw.polygon(sprite, ajustes.BOTTLE_BODY_COLOR, body)
    pygame.draw.polygon(sprite, ajustes.BOTTLE_EDGE_COLOR, body, max(1, scale))
    pygame.draw.rect(sprite, ajustes.BOTTLE_BODY_COLOR, (*point(13, 8), 10 * scale, 8 * scale))
    pygame.draw.rect(
        sprite,
        ajustes.BOTTLE_EDGE_COLOR,
        (*point(13, 8), 10 * scale, 8 * scale),
        max(1, scale),
    )
    pygame.draw.rect(sprite, ajustes.BOTTLE_CAP_COLOR, (*point(11, 2), 14 * scale, 8 * scale))
    pygame.draw.rect(
        sprite,
        ajustes.BOTTLE_CAP_EDGE_COLOR,
        (*point(11, 2), 14 * scale, 8 * scale),
        max(1, scale),
    )
    for x in range(13, 25, 3):
        pygame.draw.line(
            sprite,
            ajustes.BOTTLE_CAP_EDGE_COLOR,
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


def create_battery_sprite():
    scale = 3
    width, height = ajustes.BATTERY_SPRITE_SIZE
    sprite = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    body = pygame.Rect(4 * scale, 8 * scale, 30 * scale, 42 * scale)
    pygame.draw.rect(
        sprite,
        ajustes.BATTERY_BODY_COLOR,
        body,
        border_radius=4 * scale,
    )
    pygame.draw.rect(
        sprite,
        ajustes.BATTERY_EDGE_COLOR,
        body,
        width=2 * scale,
        border_radius=4 * scale,
    )
    pygame.draw.rect(
        sprite,
        ajustes.BATTERY_TERMINAL_COLOR,
        (12 * scale, 3 * scale, 14 * scale, 6 * scale),
        border_radius=2 * scale,
    )
    pygame.draw.rect(
        sprite,
        ajustes.BATTERY_LABEL_COLOR,
        (7 * scale, 20 * scale, 24 * scale, 19 * scale),
        border_radius=2 * scale,
    )
    warning = [
        (19 * scale, 22 * scale),
        (28 * scale, 36 * scale),
        (10 * scale, 36 * scale),
    ]
    pygame.draw.polygon(sprite, ajustes.BATTERY_WARNING_COLOR, warning)
    pygame.draw.polygon(
        sprite,
        ajustes.BATTERY_EDGE_COLOR,
        warning,
        width=scale,
    )
    pygame.draw.line(
        sprite,
        ajustes.BATTERY_EDGE_COLOR,
        (19 * scale, 27 * scale),
        (19 * scale, 32 * scale),
        width=2 * scale,
    )
    pygame.draw.circle(
        sprite,
        ajustes.BATTERY_EDGE_COLOR,
        (19 * scale, 34 * scale),
        scale,
    )
    return pygame.transform.smoothscale(sprite, ajustes.BATTERY_SPRITE_SIZE)


def draw_text(surface, text, font, color, position, centered=False):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if centered:
        rect.center = position
    else:
        rect.topleft = position
    surface.blit(image, rect)
    return rect


def spawn_object():
    kind = "bottle" if random.random() < ajustes.BOTTLE_CHANCE else "battery"
    return FallingObject(kind)


def reset_game():
    return (
        Player(),
        [],
        0,
        0,
        ajustes.STARTING_LIVES,
        ajustes.GAME_DURATION,
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


def draw_camera_background(surface, camera_surface):
    if camera_surface is None:
        surface.fill((0, 0, 0))
    else:
        surface.blit(camera_surface, (0, 0))


def draw_hud(
    surface,
    font,
    small_font,
    level_index,
    level_bottles,
    lives,
    remaining,
    game_state,
):
    level = ajustes.LEVELS[level_index]
    draw_text(
        surface,
        f"BOTELLAS  {level_bottles}/{level['bottles_to_collect']}",
        small_font,
        level["text_color"],
        (24, 20),
    )
    draw_text(
        surface,
        f"VIDAS  {'♥ ' * lives}",
        small_font,
        level["text_color"],
        (24, 54),
    )
    draw_text(
        surface,
        f"NIVEL {level_index + 1}/{len(ajustes.LEVELS)}  {level['name']}",
        small_font,
        level["text_color"],
        (365, 20),
    )
    draw_text(
        surface,
        f"TIEMPO  {max(0, math.ceil(remaining)):02d}",
        small_font,
        level["text_color"],
        (ajustes.WINDOW_WIDTH - 175, 20),
    )
    if game_state == "playing" and remaining <= ajustes.TIME_WARNING_SECONDS:
        draw_text(
            surface,
            "¡ÚLTIMOS SEGUNDOS!",
            font,
            ajustes.WARNING_COLOR,
            (ajustes.WINDOW_WIDTH - 250, 54),
        )


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as error:
        pygame.quit()
        raise RuntimeError(f"No se pudo iniciar el audio: {error}") from error

    display_flags = pygame.SCALED
    if ajustes.FULLSCREEN:
        display_flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode(
        (ajustes.WINDOW_WIDTH, ajustes.WINDOW_HEIGHT),
        display_flags,
    )
    pygame.display.set_caption(ajustes.WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, ajustes.FONT_SIZE)
    small_font = pygame.font.Font(None, ajustes.SMALL_FONT_SIZE)
    collect_sound = pygame.mixer.Sound(str(ajustes.SOUND_COLLECT_PATH))
    hit_sound = pygame.mixer.Sound(str(ajustes.SOUND_HIT_PATH))
    collect_sound.set_volume(0.45)
    hit_sound.set_volume(0.55)
    bottle_sprite = create_bottle_sprite()
    crushed_bottle_sprite = create_crushed_bottle_sprite(bottle_sprite)
    battery_sprite = create_battery_sprite()
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
    running = True
    try:
        while running:
            delta_time = min(clock.tick(ajustes.FPS) / 1000, ajustes.MAX_DELTA_TIME)
            level_banner_time = max(0, level_banner_time - delta_time)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if game_state == "ranking":
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

            if game_state == "playing":
                remaining -= delta_time
                player.follow(camera_position)
                if hand_state is not None:
                    player.radius = hand_state.radius
                spawn_elapsed += delta_time
                target_bottles = ajustes.LEVELS[level_index]["bottles_to_collect"]
                if (
                    level_bottles < target_bottles
                    and spawn_elapsed >= ajustes.SPAWN_INTERVAL
                ):
                    objects.append(spawn_object())
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
                    if falling_object.kind == "bottle":
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
                                    level_bottles += 1
                                    total_bottles += 1
                                    collect_sound.play()
                            else:
                                falling_object.hand_touched_open = False
                    elif hand_state.is_open and distance < touch_distance:
                        lives -= 1
                        hit_sound.play()
                        falling_object.y = (
                            ajustes.WINDOW_HEIGHT + falling_object.radius
                        )

                objects = [
                    falling_object
                    for falling_object in objects
                    if falling_object.y < ajustes.WINDOW_HEIGHT + falling_object.radius
                ]

                level_complete = (
                    level_bottles >= target_bottles
                    and not any(falling_object.crushed for falling_object in objects)
                )
                if level_complete:
                    if level_index == len(ajustes.LEVELS) - 1:
                        result_state = "won"
                        game_state = "enter_name"
                    else:
                        level_index += 1
                        level_bottles = 0
                        objects = []
                        level_banner_time = ajustes.LEVEL_BANNER_SECONDS
                elif lives <= 0 or remaining <= 0:
                    result_state = "lost"
                    game_state = "enter_name"

            for falling_object in objects:
                falling_object.draw(
                    screen,
                    bottle_sprite,
                    battery_sprite,
                    crushed_bottle_sprite,
                )
            draw_hud(
                screen,
                font,
                small_font,
                level_index,
                level_bottles,
                lives,
                remaining,
                game_state,
            )

            if level_banner_time > 0 and game_state == "playing":
                level = ajustes.LEVELS[level_index]
                draw_text(
                    screen,
                    f"NIVEL {level_index + 1}: {level['name']}",
                    font,
                    level["text_color"],
                    (ajustes.WINDOW_WIDTH // 2, 112),
                    centered=True,
                )
                draw_text(
                    screen,
                    f"Junta {level['bottles_to_collect']} botellas para avanzar",
                    small_font,
                    level["text_color"],
                    (ajustes.WINDOW_WIDTH // 2, 151),
                    centered=True,
                )
                draw_text(
                    screen,
                    "Toca la botella con la mano abierta y cierra la mano",
                    small_font,
                    level["text_color"],
                    (ajustes.WINDOW_WIDTH // 2, 190),
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

            if game_state == "enter_name":
                overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                overlay.fill((5, 9, 24, 210))
                screen.blit(overlay, (0, 0))
                headline = (
                    "¡PLANETA LIMPIO!"
                    if result_state == "won"
                    else "SE AGOTÓ LA ENERGÍA"
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

            elif game_state == "ranking":
                overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                overlay.fill((5, 9, 24, 220))
                screen.blit(overlay, (0, 0))
                draw_text(
                    screen,
                    "RANKING",
                    font,
                    ajustes.BOTTLE_EDGE_COLOR[:3],
                    (ajustes.WINDOW_WIDTH // 2, 88),
                    centered=True,
                )
                for index, entry in enumerate(ranking):
                    line = (
                        f"{index + 1:>2}.  {entry['name']:<16}  "
                        f"{entry['score']:>3} botellas"
                    )
                    draw_text(
                        screen,
                        line,
                        small_font,
                        ajustes.WHITE,
                        (ajustes.WINDOW_WIDTH // 2, 142 + index * 34),
                        centered=True,
                    )
                if not ranking:
                    draw_text(
                        screen,
                        "Aun no hay puntajes guardados.",
                        small_font,
                        ajustes.WHITE,
                        (ajustes.WINDOW_WIDTH // 2, 200),
                        centered=True,
                    )
                draw_text(
                    screen,
                    "Presiona R para volver a jugar",
                    small_font,
                    ajustes.WHITE,
                    (ajustes.WINDOW_WIDTH // 2, ajustes.WINDOW_HEIGHT - 50),
                    centered=True,
                )

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
