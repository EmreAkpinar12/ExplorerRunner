import pgzrun
import random

WIDTH = 1000
HEIGHT = 600
BACKGROUND = "backgroundcolordesert"
music_track = "backgroundmusic"


class Player:
    def __init__(self):
        self.actor = Actor("player_1", (100, HEIGHT - 80))
        self.actor.vy = 0
        self.images = ["player_1", "player_2", "player_3"]
        self.frame = 0
        self.ground = HEIGHT - 80

    def update(self):
        self.actor.vy += 0.4  # Yerçekimi
        self.actor.y += self.actor.vy
        if self.actor.y > self.ground:
            self.actor.y = self.ground
            self.actor.vy = 0
        self.frame = (self.frame + 1) % len(self.images)
        self.actor.image = self.images[self.frame]

    def jump(self):
        if self.actor.y == self.ground:
            self.actor.vy = -15  # Zıplama kuvveti
            if sound_on:
                sounds.jump.play()

    def draw(self):
        self.actor.draw()


def create_enemy():
    enemy_type = random.choice(["enemy_ground", "enemy_air"])
    if enemy_type == "enemy_ground":
        enemy = Actor("enemy_ground_1", (WIDTH, HEIGHT - 80))
        enemy.images = ["enemy_ground_1", "enemy_ground_2", "enemy_ground_3"]
    else:
        enemy = Actor("enemy_air_1", (WIDTH, random.randint(50, HEIGHT - 300)))
        enemy.images = ["enemy_air_1", "enemy_air_2", "enemy_air_3"]
    enemy.frame = 0
    return enemy


class Ammo:
    def __init__(self):
        self.actor = Actor("ammo")
        self.falling = random.choice([True, False])
        if self.falling:
            self.actor.pos = (
                random.randint(WIDTH // 2, WIDTH),
                random.randint(50, 200),
            )
        else:
            self.actor.pos = (WIDTH, HEIGHT - 80)
        self.lifetime = 300

    def update(self):
        if self.falling:
            self.actor.y += 3
            self.actor.x -= 5
            if self.actor.y >= HEIGHT - 80:
                self.actor.y = HEIGHT - 80
                self.falling = False
        else:
            self.actor.x -= speed
        self.lifetime -= 1

    def draw(self):
        self.actor.draw()


def create_bullet():
    bullet = Actor("bullet", (player.actor.x + 40, player.actor.y))
    if sound_on:
        sounds.shoot.play()
    return bullet


game_active = False
paused = False
main_menu = True
score = 0
speed = 5
speed_increment = 0.2
sound_on = True
ammo_count = 3


def start_game():
    global game_active, main_menu, paused, score, speed, ammo_count, enemies, bullets, ammo_boxes
    game_active = True
    main_menu = False
    paused = False
    score = 0
    speed = 5
    ammo_count = 3
    enemies.clear()
    bullets.clear()
    ammo_boxes.clear()
    enemies.extend([create_enemy(), create_enemy()])
    ammo_boxes.append(Ammo())


player = Player()
enemies = []
bullets = []
ammo_boxes = []

music.play(music_track)
music.set_volume(0.5)


def draw():
    screen.clear()
    screen.blit(BACKGROUND, (0, 0))
    if main_menu:
        draw_buttons(
            "Runner Quest", ["Start Game", f"Sound: {'ON' if sound_on else 'OFF'}"]
        )
    elif game_active and not paused:
        screen.draw.text(f"Score: {score}", (10, 10), color="white", fontsize=30)
        screen.draw.text(
            f"Ammo: {ammo_count}", (WIDTH - 120, 10), color="white", fontsize=30
        )
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        for ammo in ammo_boxes:
            ammo.draw()
    elif paused:
        draw_buttons(
            "Game Paused",
            ["Resume", "Main Menu", f"Sound: {'ON' if sound_on else 'OFF'}"],
        )


def draw_buttons(title, options):
    screen.draw.text(
        title, center=(WIDTH // 2, HEIGHT // 4), fontsize=50, color="yellow"
    )
    for i, option in enumerate(options):
        screen.draw.filled_rect(
            Rect((WIDTH // 2 - 100, HEIGHT // 2 + i * 60), (200, 50)), "gray"
        )
        screen.draw.text(
            option,
            center=(WIDTH // 2, HEIGHT // 2 + i * 60 + 25),
            fontsize=30,
            color="white",
        )


def update():
    global score, speed, ammo_count, game_active, main_menu
    if game_active and not paused:
        player.update()
        for enemy in enemies:
            enemy.x -= speed
            enemy.frame = (enemy.frame + 1) % len(enemy.images)
            enemy.image = enemy.images[enemy.frame]
            if player.actor.colliderect(enemy):
                game_active = False
                main_menu = True
            if enemy.x < -50:
                enemies.remove(enemy)
                enemies.append(create_enemy())
                score += 1
        for bullet in bullets:
            bullet.x += 10
            for enemy in enemies:
                if bullet.colliderect(enemy):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    enemies.append(create_enemy())
                    score += 1
                    break
            if bullet.x > WIDTH:
                bullets.remove(bullet)
        for ammo in ammo_boxes:
            ammo.update()
            if ammo.lifetime <= 0:
                ammo_boxes.remove(ammo)
                ammo_boxes.append(Ammo())
            if player.actor.colliderect(ammo.actor):
                ammo_boxes.remove(ammo)
                ammo_count += 1
                ammo_boxes.append(Ammo())


def on_mouse_down(pos):
    global paused, sound_on, main_menu
    if main_menu:
        if Rect((WIDTH // 2 - 100, HEIGHT // 2), (200, 50)).collidepoint(pos):
            start_game()
        elif Rect((WIDTH // 2 - 100, HEIGHT // 2 + 60), (200, 50)).collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.play(music_track)
            else:
                music.stop()
    elif paused:
        if Rect((WIDTH // 2 - 100, HEIGHT // 2), (200, 50)).collidepoint(pos):
            paused = False
        elif Rect((WIDTH // 2 - 100, HEIGHT // 2 + 60), (200, 50)).collidepoint(pos):
            main_menu = True
            game_active = False
        elif Rect((WIDTH // 2 - 100, HEIGHT // 2 + 120), (200, 50)).collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.play(music_track)
            else:
                music.stop()


def on_key_down(key):
    global paused, ammo_count
    if key == keys.SPACE:
        player.jump()
    elif key == keys.ESCAPE:
        paused = not paused
    elif key == keys.F and ammo_count > 0:
        bullets.append(create_bullet())
        ammo_count -= 1


pgzrun.go()
