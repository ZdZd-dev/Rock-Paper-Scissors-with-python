import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
from PIL import Image, ImageTk
from PIL import ImageEnhance
import pygame
import random
import sys
import os

# --- Helper for PyInstaller ---
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- Audio setup ---
pygame.mixer.init()
pygame.mixer.music.load(resource_path("audio/menusong.mp3"))
pygame.mixer.music.play(loops=-1)

start_sfx = pygame.mixer.Sound(resource_path("audio/mg.wav"))
btn_sfx = pygame.mixer.Sound(resource_path("audio/click.mp3"))
count_sfx = pygame.mixer.Sound(resource_path("audio/countdown.mp3"))
fight_sfx = pygame.mixer.Sound(resource_path("audio/click.mp3"))
win_sfx = pygame.mixer.Sound(resource_path("audio/win.mp3"))
lose_sfx = pygame.mixer.Sound(resource_path("audio/lose.mp3"))
draw_sfx = pygame.mixer.Sound(resource_path("audio/draw.mp3"))
winsound_sfx = pygame.mixer.Sound(resource_path("audio/winsound.mp3"))
losesound_sfx = pygame.mixer.Sound(resource_path("audio/losesound.mp3"))
pause_sfx = pygame.mixer.Sound(resource_path("audio/pause.mp3"))

choice_sfx = {
    "rock": pygame.mixer.Sound(resource_path("audio/rock.wav")),
    "paper": pygame.mixer.Sound(resource_path("audio/paper.wav")),
    "scissors": pygame.mixer.Sound(resource_path("audio/scissors.wav"))
}

# --- Tk setup ---
window = tk.Tk()
window.geometry("800x600")
window.resizable(False, False)
window.title("Rock Paper Scissors")

try:
    window.iconbitmap(resource_path("favicon.ico"))
except Exception as e:
    print("Icon load failed:", e)

main_menu = tk.Frame(window)
game_page = tk.Frame(window)
win_screen = tk.Frame(window, bg="black")
lose_screen = tk.Frame(window, bg="black")
for frame in (main_menu, game_page, win_screen, lose_screen):
    frame.place(x=0, y=0, relwidth=1, relheight=1)

# --- Pause system variables ---
is_paused = False
pause_overlay = None
pause_text_id = None
pause_menu_btn = None

# --- Menu background ---
bg_image = Image.open(resource_path("imgs/menu.png"))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(main_menu, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


player_lowhp_overlay = None
player_lowhp_pulsing = False



overlay = tk.Frame(main_menu, bg="black")
overlay.place(x=0, y=0, relwidth=1, relheight=1)

# --- Win / Lose Screens ---
def setup_end_screen(frame, text, bg_color):
    label = tk.Label(frame, text=text, font=("Pixel game", 40), fg="white", bg=bg_color)
    label.place(relx=0.5, rely=0.4, anchor="center")

    btn = tk.Button(frame, text="MAIN MENU", font=("Pixel game", 28),
                    bg="#136bae", fg="#FFE5A1", width=12, relief="raised",
                    command=lambda: return_to_menu())
    btn.place(relx=0.5, rely=0.6, anchor="center")

    def on_enter(e):
        btn.config(bg="#1e79c6")
    def on_leave(e):
        btn.config(bg="#136bae")
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

setup_end_screen(win_screen, "YOU WIN!", "#1a7431")
setup_end_screen(lose_screen, "YOU LOSE!", "#8c1c13")

# --- Start button ---
startBtn = tk.Button(main_menu, text="START", font=("Pixel game", 30),
                     width=14, bg="#136bae", fg="#FFE5A1", relief="raised")
startBtn.place(x=-300, y=500)

def on_start_enter(e):
    startBtn.config(bg="#1e79c6")
def on_start_leave(e):
    startBtn.config(bg="#136bae")
startBtn.bind("<Enter>", on_start_enter)
startBtn.bind("<Leave>", on_start_leave)

def go_to_game():
    global player_hp, npc_hp
    player_hp = 3
    npc_hp = 3
    btn_sfx.play()
    pygame.mixer.music.fadeout(1000)
    game_page.tkraise()
    window.after(800, start_game_music)
startBtn.config(command=go_to_game)

def start_game_music():
    try:
        pygame.mixer.music.load(resource_path("audio/gamesong.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(loops=-1)
    except Exception:
        pass

def slide_animation(x=-300):
    if x >= 260:
        startBtn.place(x=260, y=500)
        return
    startBtn.place(x=x, y=500)
    window.after(10, slide_animation, x + 10)

# --- Fade in w/ "Made by Luka" ---
def fade_step(alpha):
    if alpha <= 0:
        overlay.destroy()
        if hasattr(main_menu, "made_by_label"):
            main_menu.made_by_label.destroy()
        slide_animation()
        start_sfx.play()
        return
    hex_color = f'#{alpha:02x}{alpha:02x}{alpha:02x}'
    overlay.config(bg=hex_color)
    if not hasattr(main_menu, "made_by_label"):
        main_menu.made_by_label = tk.Label(main_menu, text="Made by Luka",
                                           font=("Pixel game", 24), fg="white", bg="#000000")
        main_menu.made_by_label.place(relx=0.5, rely=0.5, anchor="center")
    window.after(30, fade_step, alpha - 5)
fade_step(255)

# --- Game state ---
wins, losses, draws = 0, 0, 0
choices = ["rock", "paper", "scissors"]
game_active = False
game_over_active = False

# --- Pause state ---
game_paused = False
pause_overlay = None
pause_btn = None
pause_photo = None

# --- Health System ---
player_hp = 3
npc_hp = 3
hp_img_size = (160, 48)
hp_images = {
    1: ImageTk.PhotoImage(Image.open(resource_path("imgs/1hp.png")).resize(hp_img_size)),
    2: ImageTk.PhotoImage(Image.open(resource_path("imgs/2hp.png")).resize(hp_img_size)),
    3: ImageTk.PhotoImage(Image.open(resource_path("imgs/3hp.png")).resize(hp_img_size))
}
player_hp_display = None
npc_hp_display = None

# --- Game canvas ---
game_bg_image = Image.open(resource_path("imgs/gamebg.png")).resize((800, 600))
game_bg_photo = ImageTk.PhotoImage(game_bg_image)
canvas = tk.Canvas(game_page, width=800, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas_bg = canvas.create_image(400, 300, image=game_bg_photo)
score_text_id = canvas.create_text(400, 28, text="Wins: 0  Losses: 0  Draws: 0",
                                   font=("Pixel game", 16), fill="white")

# --- Pause button in corner ---
pause_btn_corner_img = Image.open(resource_path("imgs/pause.png")).resize((60, 60))
pause_btn_corner_photo = ImageTk.PhotoImage(pause_btn_corner_img)
pause_btn_corner = tk.Button(canvas, image=pause_btn_corner_photo, bd=0, highlightthickness=0,
                             relief="flat", command=lambda: toggle_pause_canvas(),
                             bg="black", activebackground="black")
pause_btn_corner.place(x=730, y=20)  # Top-right corner





















# --- Load heartbeat sound ---
heartbeat_sfx = pygame.mixer.Sound(resource_path("audio/lowhp.wav"))

# --- Update health function ---
def update_health():
    global player_hp_display, npc_hp_display, player_hp, npc_hp
    if player_hp_display:
        canvas.delete(player_hp_display)
    if npc_hp_display:
        canvas.delete(npc_hp_display)
    player_hp = max(0, min(3, player_hp))
    npc_hp = max(0, min(3, npc_hp))
    if player_hp > 0:
        player_hp_display = canvas.create_image(90, 470, image=hp_images[player_hp])
    if npc_hp > 0:
        npc_hp_display = canvas.create_image(90, 130, image=hp_images[npc_hp])
    if player_hp <= 0:
        trigger_game_over("lose")
    elif npc_hp <= 0:
        trigger_game_over("win")




update_health()






















# --- End screen triggers ---
def trigger_game_over(result):
    global game_over_active
    if game_over_active:
        return
    game_over_active = True
    pygame.mixer.music.fadeout(1000)
    if result == "win":
        winsound_sfx.play()
        win_screen.tkraise()
    else:
        losesound_sfx.play()
        lose_screen.tkraise()

def return_to_menu():
    btn_sfx.play()
    pygame.mixer.music.load(resource_path("audio/menusong.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)
    global player_hp, npc_hp, wins, losses, draws, game_over_active, is_paused, pause_menu_btn, pause_overlay, pause_text_id
    player_hp, npc_hp, wins, losses, draws = 3, 3, 0, 0, 0
    game_over_active = False
    is_paused = False

    # Cleanup pause overlay elements
    if pause_overlay:
        canvas.delete(pause_overlay)
        pause_overlay = None
    if pause_text_id:
        canvas.delete(pause_text_id)
        pause_text_id = None
    if pause_menu_btn:
        pause_menu_btn.destroy()
        pause_menu_btn = None

    update_score()
    update_health()
    main_menu.tkraise()


def update_score():
    canvas.itemconfig(score_text_id, text=f"Wins: {wins}  Losses: {losses}  Draws: {draws}")

# --- Load images ---
img_size = (120, 120)
player_imgs = {c: ImageTk.PhotoImage(Image.open(resource_path(f"imgs/{c}.png")).resize(img_size)) for c in choices}
npc_imgs = {c: ImageTk.PhotoImage(Image.open(resource_path(f"imgs/{c}.png")).resize(img_size).rotate(180)) for c in choices}
base_player_imgs = player_imgs.copy()
base_npc_imgs = npc_imgs.copy()

# --- Positions ---
center_x = 400
spacing = 190
npc_positions = {"rock": (center_x - spacing, 130), "paper": (center_x, 130), "scissors": (center_x + spacing, 130)}
player_positions = {"rock": (center_x - spacing, 470), "paper": (center_x, 470), "scissors": (center_x + spacing, 470)}
npc_labels = {c: canvas.create_image(x, y, image=npc_imgs[c]) for c, (x, y) in npc_positions.items()}
player_labels = {c: canvas.create_image(x, y, image=player_imgs[c]) for c, (x, y) in player_positions.items()}
countdown_text = canvas.create_text(center_x, 300, text="", font=("Pixel game", 50), fill="white")

# --- Hover setup ---
hover_states = {c: False for c in choices}
scaled_imgs = {}
def make_glow(img, intensity=1.4):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(intensity)
def pulse_image(choice, grow=True):
    if not hover_states.get(choice, False): return
    scale = 1.08 if grow else 1.0
    size = (int(img_size[0]*scale), int(img_size[1]*scale))
    bright_img = make_glow(Image.open(resource_path(f"imgs/{choice}.png")), 1.5)
    img = ImageTk.PhotoImage(bright_img.resize(size))
    scaled_imgs[choice] = img
    x, y = player_positions[choice]
    canvas.itemconfig(player_labels[choice], image=img)
    canvas.coords(player_labels[choice], x, y)
    window.after(250, lambda: pulse_image(choice, not grow))
def on_enter(event, choice):
    hover_states[choice] = True
    pulse_image(choice, True)
def on_leave(event, choice):
    hover_states[choice] = False
    canvas.itemconfig(player_labels[choice], image=base_player_imgs[choice])
    canvas.coords(player_labels[choice], *player_positions[choice])
    scaled_imgs.pop(choice, None)











# --- Pause toggle ---
def toggle_pause_canvas():
    global is_paused, pause_overlay, pause_text_id, pause_menu_btn
    if not is_paused:
        is_paused = True
        pygame.mixer.music.pause()
        try: pause_sfx.play()
        except: pass
        pause_overlay = canvas.create_rectangle(0, 0, 800, 600, fill="black", stipple="gray50")
        pause_text_id = canvas.create_text(400, 250, text="PAUSED", font=("Pixel game", 50), fill="white")
        pause_menu_btn = tk.Button(canvas, text="MAIN MENU", font=("Pixel game", 28),
                                   bg="#136bae", fg="#FFE5A1", width=12, relief="raised",
                                   command=return_to_menu)
        pause_menu_btn.place(relx=0.5, rely=0.6, anchor="center")
        pause_menu_btn.bind("<Enter>", lambda e: pause_menu_btn.config(bg="#1e79c6"))
        pause_menu_btn.bind("<Leave>", lambda e: pause_menu_btn.config(bg="#136bae"))
    else:
        is_paused = False
        pygame.mixer.music.unpause()
        if pause_overlay: canvas.delete(pause_overlay)
        if pause_text_id: canvas.delete(pause_text_id)
        if pause_menu_btn:
            pause_menu_btn.destroy()
            pause_menu_btn = None

# --- Game logic ---
player_streak = 0
npc_streak = 0
streak_text_id = canvas.create_text(400, 50, text="", font=("Pixel game", 14), fill="yellow")

def update_streak_text():
    canvas.itemconfig(streak_text_id, text=f"Player Streak: {player_streak}  NPC Streak: {npc_streak}")

update_streak_text()

# --- Hit animation / screen shake ---
def shake_screen(duration=100, intensity=5):
    def step(elapsed=0):
        if elapsed >= duration:
            canvas.place(x=0, y=0)
            return
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        canvas.place(x=offset_x, y=offset_y)
        window.after(20, lambda: step(elapsed + 20))
    step()

# --- Music adjust ---
def adjust_music_for_hp():
    if player_hp == 1:
        pygame.mixer.music.set_volume(0.5)
    else:
        pygame.mixer.music.set_volume(0.4)

# --- Flash tint ---
_STIPPLE_STEPS = ["gray75", "gray50", "gray25", "gray12"]
def flash_tint(color="green", total_time=400):
    rect = canvas.create_rectangle(0, 0, 800, 600, fill=color, outline="")
    canvas.tag_raise(rect)
    step_time = max(30, total_time // (len(_STIPPLE_STEPS) + 1))
    idx = 0
    def step():
        nonlocal idx
        if idx < len(_STIPPLE_STEPS):
            canvas.itemconfig(rect, stipple=_STIPPLE_STEPS[idx])
            idx += 1
            window.after(step_time, step)
        else:
            canvas.delete(rect)
    step()

# --- Countdown ---
def animate_countdown(callback):
    count = 3
    def tick():
        nonlocal count
        if count == 0:
            canvas.itemconfig(countdown_text, text="")
            callback()
        else:
            canvas.itemconfig(countdown_text, text=str(count))
            count_sfx.play()
            count -= 1
            window.after(1000, tick)
    tick()

# --- Move toward ---
def move_toward(center_x, npc_item, player_item, npc_y, player_y, meet_callback, player_choice, npc_choice, step=12):
    next_npc_y = npc_y + step
    next_player_y = player_y - step
    if next_npc_y >= next_player_y:
        meet_y = (npc_y + player_y) // 2
        canvas.coords(npc_item, center_x, meet_y)
        canvas.coords(player_item, center_x, meet_y)
        fight_sfx.play()
        flash_id = canvas.create_rectangle(0, 0, 800, 600, fill="white", outline="")
        canvas.tag_raise(flash_id)
        # Pass the choices here
        window.after(120, lambda: [canvas.delete(flash_id), meet_callback(player_choice, npc_choice)])
        return
    canvas.coords(npc_item, center_x, next_npc_y)
    canvas.coords(player_item, center_x, next_player_y)
    window.after(30, move_toward, center_x, npc_item, player_item, next_npc_y, next_player_y, meet_callback, player_choice, npc_choice, step)


# --- Animate return ---
def animate_return_positions(steps=12):
    current_npc_coords = {c: canvas.coords(npc_labels[c]) for c in npc_labels}
    current_player_coords = {c: canvas.coords(player_labels[c]) for c in player_labels}
    moves = []
    for c, (target_x, target_y) in npc_positions.items():
        cur = current_npc_coords.get(c, (target_x, target_y))
        dx = (target_x - cur[0]) / steps
        dy = (target_y - cur[1]) / steps
        moves.append(("npc", c, dx, dy))
    for c, (target_x, target_y) in player_positions.items():
        cur = current_player_coords.get(c, (target_x, target_y))
        dx = (target_x - cur[0]) / steps
        dy = (target_y - cur[1]) / steps
        moves.append(("player", c, dx, dy))
    def step(i=0):
        if i >= steps:
            return
        for kind, c, dx, dy in moves:
            lbl = npc_labels[c] if kind == "npc" else player_labels[c]
            x, y = canvas.coords(lbl)
            canvas.coords(lbl, x + dx, y + dy)
        window.after(25, lambda: step(i + 1))
    step(0)

def reset_positions():
    canvas.itemconfig(countdown_text, text="", fill="white")
    for c, (x, y) in npc_positions.items():
        canvas.coords(npc_labels[c], x, y)
    for c, (x, y) in player_positions.items():
        canvas.coords(player_labels[c], x, y)
        canvas.itemconfig(player_labels[c], image=base_player_imgs[c])
        canvas.itemconfig(npc_labels[c], image=base_npc_imgs[c])
    scaled_imgs.clear()
    update_health()

# --- Play function ---
def play(choice):
    global wins, losses, draws, game_active, player_hp, npc_hp, player_streak, npc_streak
    if game_active or is_paused:
        return
    game_active = True
    if choice in choice_sfx:
        choice_sfx[choice].play()
    npc_choice = random.choice(choices)

    def after_meet_original(player_choice, npc_choice):
        global wins, losses, draws, player_hp, npc_hp, player_streak, npc_streak
        if player_choice == npc_choice:
            draws += 1
            draw_sfx.play()
            tint_color = "gray"
            player_streak = 0
            npc_streak = 0
        elif (player_choice == "rock" and npc_choice == "scissors") or \
            (player_choice == "paper" and npc_choice == "rock") or \
            (player_choice == "scissors" and npc_choice == "paper"):
            wins += 1
            win_sfx.play()
            tint_color = "green"
            if player_hp < 3: player_hp += 1
            npc_hp -= 1
            player_streak += 1
            npc_streak = 0
            shake_screen()
        else:
            losses += 1
            lose_sfx.play()
            tint_color = "red"
            if npc_hp < 3: npc_hp += 1
            player_hp -= 1
            npc_streak += 1
            player_streak = 0
            shake_screen()

        update_health()
        flash_tint(color=tint_color, total_time=500)
        update_score()
        update_streak_text()
        adjust_music_for_hp()
        window.after(900, animate_return_positions)
        window.after(1400, reset_positions)
        window.after(1450, lambda: set_game_unlocked())


    def start_fight():
        npc_item = npc_labels[npc_choice]
        player_item = player_labels[choice]
        _, npc_y = canvas.coords(npc_item)
        _, player_y = canvas.coords(player_item)
        move_toward(center_x, npc_item, player_item, npc_y, player_y, after_meet_original, choice, npc_choice)


    animate_countdown(start_fight)

def set_game_unlocked():
    global game_active
    game_active = False

# --- Bind hover/clicks ---
for c in choices:
    canvas.tag_bind(player_labels[c], "<Enter>", lambda e, ch=c: on_enter(e, ch))
    canvas.tag_bind(player_labels[c], "<Leave>", lambda e, ch=c: on_leave(e, ch))
    canvas.tag_bind(player_labels[c], "<Button-1>", lambda e, ch=c: play(ch))

window.config(cursor="cross")    # crosshair






# --- LOW HP PULSE EFFECT ---
lowhp_overlay_ids = []
lowhp_scale = 1.0
lowhp_grow = True

def pulse_lowhp_effect():
    global lowhp_scale, lowhp_grow, lowhp_overlay_ids

    # remove previous overlays
    for oid in lowhp_overlay_ids:
        canvas.delete(oid)
    lowhp_overlay_ids.clear()

    if player_hp != 1:
        window.after(100, pulse_lowhp_effect)
        return

    for c in choices:
        x, y = player_positions[c]
        # pulsate alpha effect
        alpha = int(80 + (lowhp_scale-1.0)*200)  # pulsate between ~80-96 opacity
        color = f"#ff0000{alpha:02x}" if alpha <= 255 else "#ff0000ff"

        # create a rectangle behind each hand
        size = int(img_size[0]*lowhp_scale)
        oid = canvas.create_rectangle(
            x - size//2, y - size//2,
            x + size//2, y + size//2,
            fill="red", outline="", stipple="gray50"
        )
        canvas.tag_lower(oid, player_labels[c])  # put behind the hand image
        lowhp_overlay_ids.append(oid)

    # update scale for pulsate
    if lowhp_grow:
        lowhp_scale += 0.02
        if lowhp_scale >= 1.08:
            lowhp_grow = False
    else:
        lowhp_scale -= 0.02
        if lowhp_scale <= 1.0:
            lowhp_grow = True

    # loop
    window.after(100, pulse_lowhp_effect)

# --- start low HP pulse effect after all widgets are created ---
pulse_lowhp_effect()



# --- Load heartbeat sound ---
heartbeat_sfx = pygame.mixer.Sound(resource_path("audio/lowhp.wav"))

# Use a dedicated channel for looping heartbeat
heartbeat_channel = pygame.mixer.Channel(5)  # channel 5, can be any free channel

# --- Low HP overlay ---
low_hp_overlay_ids = []
low_hp_pulsing = False

def start_low_hp_effect():
    global low_hp_pulsing
    if low_hp_pulsing:
        return
    low_hp_pulsing = True
    if not heartbeat_channel.get_busy():
        heartbeat_channel.play(heartbeat_sfx, loops=-1)  # loop indefinitely
    pulse_low_hp()

def stop_low_hp_effect():
    global low_hp_pulsing
    low_hp_pulsing = False
    heartbeat_channel.stop()  # stop the heartbeat sound
    for rect_id in low_hp_overlay_ids:
        canvas.delete(rect_id)
    low_hp_overlay_ids.clear()

def pulse_low_hp(grow=True):
    if not low_hp_pulsing:
        return
    # Remove previous overlays
    for rect_id in low_hp_overlay_ids:
        canvas.delete(rect_id)
    low_hp_overlay_ids.clear()

    # Draw overlays for all 3 player hands **under the hand images**
    for c, (x, y) in player_positions.items():
        rect = canvas.create_rectangle(
            x - 60, y - 60, x + 60, y + 60,
            fill="red", stipple="gray50", outline=""
        )
        # Move it under the hand image
        canvas.tag_lower(rect, player_labels[c])
        low_hp_overlay_ids.append(rect)

    # Pulsate effect
    window.after(400, lambda: pulse_low_hp(not grow))


# --- Call inside update_health ---
def update_health():
    global player_hp_display, npc_hp_display, player_hp, npc_hp
    if player_hp_display:
        canvas.delete(player_hp_display)
    if npc_hp_display:
        canvas.delete(npc_hp_display)
    player_hp = max(0, min(3, player_hp))
    npc_hp = max(0, min(3, npc_hp))
    if player_hp > 0:
        player_hp_display = canvas.create_image(90, 470, image=hp_images[player_hp])
    if npc_hp > 0:
        npc_hp_display = canvas.create_image(90, 130, image=hp_images[npc_hp])
    if player_hp <= 0:
        trigger_game_over("lose")
    elif npc_hp <= 0:
        trigger_game_over("win")

    # Low HP effects
    if player_hp == 1:
        start_low_hp_effect()
    else:
        stop_low_hp_effect()



# --- Show menu initially ---
main_menu.tkraise()
window.mainloop()
pygame.mixer.music.stop()
