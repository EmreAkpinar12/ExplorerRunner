import pgzrun
import random

WIDTH = 1000
HEIGHT = 600
BACKGROUND = "backgroundcolordesert"
music_track = "backgroundmusic"

player = Actor("player_1", (100, HEIGHT - 80))
player.vy = 0
player.images = ["player_1", "player_2", "player_3"]
player.frame = 0

ground = HEIGHT - 80

def create_enemy():
    enemy_type = random.choice(["enemy_ground", "enemy_air"])
    y_pos = ground if enemy_type == "enemy_ground" else random.randint(50, HEIGHT - 300)
    return Actor(enemy_type, (WIDTH, y_pos))

def create_bullet():
    return Actor("bullet", (player.x + 40, player.y))

def create_ammo():
    """Mermi kutularını rastgele yerde oluşturur (yerde veya yukarıdan düşerek)."""
    ammo = Actor("ammo")

    if random.choice([True, False]):  # %50 ihtimalle yukarıdan gelsin
        ammo.pos = (random.randint(WIDTH // 2, WIDTH), random.randint(50, 200))
        ammo.falling = True  # Yukarıdan düşen mermi
    else:
        ammo.pos = (WIDTH, ground)
        ammo.falling = False  # Yerde sürünen mermi

    return ammo

enemies = [create_enemy(), create_enemy()]
bullets = []
ammo_boxes = [create_ammo()]

game_active = False
paused = False
score = 0
speed = 5
speed_increment = 0.2
sound_on = True
ammo_count = 3

# Mermilerin kaybolma süresi (frame cinsinden)
ammo_lifetimes = {ammo: 300 for ammo in ammo_boxes}

music.play(music_track)
music.set_volume(0.5)

def draw():
    screen.clear()
    screen.blit(BACKGROUND, (0, 0))
    if game_active and not paused:
        screen.draw.text(f"Score: {score}", (10, 10), color="white", fontsize=30)
        screen.draw.text(f"Ammo: {ammo_count}", (WIDTH - 120, 10), color="white", fontsize=30)
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        for ammo in ammo_boxes:
            ammo.draw()
    elif paused:
        screen.draw.text("Game Paused", center=(WIDTH//2, HEIGHT//4), fontsize=50, color="yellow")
        screen.draw.text("Press ESC to Resume", center=(WIDTH//2, HEIGHT//2), fontsize=30, color="white")
        screen.draw.text(f"Sound: {'ON' if sound_on else 'OFF'} (Press S to Toggle)", center=(WIDTH//2, HEIGHT//1.5), fontsize=30, color="white")
    else:
        screen.draw.text("Runner Quest", center=(WIDTH//2, HEIGHT//4), fontsize=50, color="cyan")
        screen.draw.text("Press SPACE to Start", center=(WIDTH//2, HEIGHT//2), fontsize=30, color="white")
        screen.draw.text(f"Sound: {'ON' if sound_on else 'OFF'} (Press S to Toggle)", center=(WIDTH//2, HEIGHT//1.5), fontsize=30, color="white")

def update():
    global game_active, score, speed, ammo_count
    if game_active and not paused:
        player.vy += 0.4  # Yerçekimi
        player.y += player.vy
        if player.y > ground:
            player.y = ground
            player.vy = 0

        player.frame = (player.frame + 1) % len(player.images)
        player.image = player.images[player.frame]

        for enemy in enemies:
            enemy.x -= speed
            if enemy.x < -50:
                enemies.remove(enemy)
                enemies.append(create_enemy())
                score += 1
                if score % 5 == 0:
                    speed += speed_increment

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

        # **Mermi Kutularını Oyuncuya Doğru Hareket Ettirme**
        for ammo in ammo_boxes:
            if ammo.falling:  # Eğer yukarıdan düşüyorsa
                ammo.y += 3  # Düşme hızı
                ammo.x -= 5 # Aynı anda sola hareket etsin
                if ammo.y >= ground:  # Yere düştüğünde normal hareket etsin
                    ammo.y = ground
                    ammo.falling = False
            else:
                ammo.x -= speed  # Yerdeyse oyuncuya doğru hareket eder

            # **Mermiyi belirli sürede toplamazsa kaybolsun**
            ammo_lifetimes[ammo] -= 1
            if ammo_lifetimes[ammo] <= 0:
                ammo_boxes.remove(ammo)
                del ammo_lifetimes[ammo]
                ammo_boxes.append(create_ammo())
                ammo_lifetimes[ammo_boxes[-1]] = 300

            # **Oyuncu mermiyi toplarsa**
            if player.colliderect(ammo):
                ammo_boxes.remove(ammo)
                del ammo_lifetimes[ammo]
                ammo_count += 1
                ammo_boxes.append(create_ammo())
                ammo_lifetimes[ammo_boxes[-1]] = 300

        for enemy in enemies:
            if player.colliderect(enemy):
                reset_game()

def reset_game():
    global game_active, score, speed, ammo_count, enemies, bullets, ammo_boxes, ammo_lifetimes
    game_active = False
    score = 0
    speed = 5
    ammo_count = 3
    enemies = [create_enemy(), create_enemy()]
    bullets = []
    ammo_boxes = [create_ammo()]
    ammo_lifetimes = {ammo_boxes[0]: 300}

def on_key_down(key):
    global game_active, paused, sound_on, ammo_count
    if key == keys.SPACE:
        if not game_active:
            game_active = True
        elif player.y == ground:
            player.vy = -15  # Zıplama kuvveti
    elif key == keys.S:
        sound_on = not sound_on
        if sound_on:
            music.play(music_track)
        else:
            music.stop()
    elif key == keys.ESCAPE:
        if game_active:
            paused = not paused
    elif key == keys.F and ammo_count > 0:
        bullets.append(create_bullet())
        ammo_count -= 1

pgzrun.go()
