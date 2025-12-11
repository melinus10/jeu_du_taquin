#!/usr/bin/env python3
import os
import random
import heapq
import threading
import tkinter as tk
from tkinter import PhotoImage, Canvas, Button, Label, messagebox, ttk
from tkinter.font import Font
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Variable globale pour l'image source
image_source_path = "shuffle/image1.png"

def load_image_and_create_tiles(size):
    """
    Découpe une image source en tuiles dynamiques et ajoute les numéros sur chaque tuile.
    Retourne une liste `photos` où photos[0] == None (tuile vide) et photos[1..n] sont ImageTk.PhotoImage.
    Si l'image source est manquante ou qu'il y a une erreur, on génère des tuiles numérotées simples.
    """
    try:
        # Compatibilité pour le paramètre de resampling entre versions de Pillow
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            # Pillow < 9 compat
            resample_filter = Image.LANCZOS

        # Charger l'image source
        if not os.path.exists(image_source_path):
            raise FileNotFoundError(f"Image source introuvable: {image_source_path}")

        image_source = Image.open(image_source_path)

        # Redimensionner l'image pour correspondre aux dimensions du puzzle
        total_size = size * 150  # 150 pixels par tuile
        image_source = image_source.resize((total_size, total_size), resample=resample_filter)

        # Calculer la taille de chaque tuile
        tile_width = total_size // size
        tile_height = total_size // size

        photos = []

        # Essayer de charger une police spécifique ; adapter la taille selon tile
        font_size = max(12, tile_width // 3)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        tile_number = 1
        for i in range(size):
            for j in range(size):
                left = j * tile_width
                upper = i * tile_height
                right = left + tile_width
                lower = upper + tile_height

                tile = image_source.crop((left, upper, right, lower))

                if not (i == size - 1 and j == size - 1):
                    draw = ImageDraw.Draw(tile)
                    text = str(tile_number)

                    # Calculer la bbox du texte pour le centrer (compatibilité)
                    try:
                        text_bbox = draw.textbbox((0,0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                    except AttributeError:
                        text_width, text_height = draw.textsize(text, font=font)

                    text_x = (tile_width - text_width) // 2
                    text_y = (tile_height - text_height) // 2

                    draw.text((text_x, text_y), text, fill="white", font=font)
                    photos.append(ImageTk.PhotoImage(tile))
                    tile_number += 1
                else:
                    # tuile vide : insérer None en début pour que photos[index] corresponde au numéro
                    photos.insert(0, None)

        return photos

    except Exception as e:
        print("Erreur lors du découpage des images ou de l'ajout des chiffres :", e)
        # fallback : créer des tuiles colorées numérotées (au cas où l'image est manquante)
        photos = [None]  # index 0 = tuile vide
        tile_width = tile_height = 150
        font_size = max(12, tile_width // 3)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        for n in range(1, size*size):
            img = Image.new("RGB", (tile_width, tile_height), color=(50 + (n*30)%200, 80 + (n*20)%150, 120 + (n*10)%120))
            draw = ImageDraw.Draw(img)
            try:
                text_bbox = draw.textbbox((0,0), str(n), font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except AttributeError:
                text_width, text_height = draw.textsize(str(n), font=font)
            text_x = (tile_width - text_width) // 2
            text_y = (tile_height - text_height) // 2
            draw.text((text_x, text_y), str(n), fill="white", font=font)
            photos.append(ImageTk.PhotoImage(img))
        return photos

# Configuration des couleurs et du style
COLORS = {
    'primary': '#117a65',    # Bleu principal
    'secondary': '#45b39d',  # Bleu foncé pour hover
    'background': '#f3f4f6', # Fond gris clair
    'text': '#1f2937',       # Texte foncé
    'white': '#ffffff'       # Blanc
}

class StyledButton(Button):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            bg=COLORS['primary'],
            fg=COLORS['white'],
            font=('Helvetica', 12),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground=COLORS['secondary'],
            activeforeground=COLORS['white'],
            bd=2,  # Ajout d'une bordure
            highlightthickness=2,  # Épaisseur de la bordure
            highlightbackground=COLORS['text'],  # Couleur de bordure
            **kwargs
        )
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, e):
        self['background'] = COLORS['secondary']

    def _on_leave(self, e):
        self['background'] = COLORS['primary']

def afficher_selection_taille():
    for widget in fenetre.winfo_children():
        widget.destroy()

    create_title_label(fenetre, "Taille du Puzzle").pack()

    frame = tk.Frame(fenetre, bg=COLORS['background'], pady=20)
    frame.pack(expand=True)

    Label(
        frame,
        text="Choisissez la taille du puzzle",
        font=('Helvetica', 16),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack(pady=20)

    StyledButton(frame, text="3x3", command=lambda: start_game(3)).pack(pady=10)
    StyledButton(frame, text="4x4", command=lambda: start_game(4)).pack(pady=10)
    StyledButton(frame, text="Image aléatoire", command=choisir_image_aleatoire).pack(pady=10)

    # Bouton Retour
    StyledButton(frame, text="Retour", command=afficher_selection_mode).pack(pady=10)

def choisir_image_aleatoire():
    """
    Sélectionne une image aléatoire dans le dossier 'shuffle' pour le puzzle.
    """
    global image_source_path
    # Liste des fichiers dans le dossier 'shuffle'
    image_folder = "/home/fatima/projet_annuel2/projet_annuel/shuffle"
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)  # Crée le dossier s'il n'existe pas
    images = [f for f in os.listdir(image_folder) if f.endswith(".png")]
    if images:
        image_source_path = os.path.join(image_folder, random.choice(images))

def animate_tile(canvas, tile, start_x, start_y, end_x, end_y, steps=10, delay=20):
    """
    Anime le déplacement d'une tuile dans le canvas.
    """
    delta_x = (end_x - start_x) / steps
    delta_y = (end_y - start_y) / steps

    def step_animation(step=0):
        if step <= steps:
            try:
                canvas.move(tile, delta_x, delta_y)
            except Exception:
                pass
            canvas.after(delay, step_animation, step + 1)

    step_animation()

# États finaux du puzzle
goal_state_3x3 = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
goal_state_4x4 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]

# Variables globales
mode_de_jeu = None
fenetre_joueur1 = None
fenetre_joueur2 = None
puzzle_canvas_j1 = None
puzzle_canvas_j2 = None
photos = []
board_j1 = None
board_j2 = None
current_player = 1
shuffle_button = None
shuffle_button_j1 = None
shuffle_button_j2 = None

def setup_window(window, title):
    window.title(title)
    window.configure(bg=COLORS['background'])
    window_width = 800
    window_height = 600
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f'{window_width}x{window_height}+{x}+{y}')

def create_title_label(parent, text):
    return Label(
        parent,
        text=text,
        font=('Helvetica', 24, 'bold'),
        bg=COLORS['background'],
        fg=COLORS['text'],
        pady=20
    )

def afficher_page_accueil():
    for widget in fenetre.winfo_children():
        widget.destroy()

    create_title_label(fenetre, "Bienvenue dans le Jeu du Taquin").pack()

    frame = tk.Frame(fenetre, bg=COLORS['background'], pady=20)
    frame.pack(expand=True)

    StyledButton(frame, text="Jouer", command=afficher_selection_mode).pack(pady=10)
    StyledButton(frame, text="Quitter", command=fenetre.quit).pack(pady=10)

def afficher_selection_mode():
    for widget in fenetre.winfo_children():
        widget.destroy()

    create_title_label(fenetre, "Jeu du Taquin").pack()

    frame = tk.Frame(fenetre, bg=COLORS['background'], pady=20)
    frame.pack(expand=True)

    Label(
        frame,
        text="Choisissez le mode de jeu",
        font=('Helvetica', 16),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack(pady=20)

    StyledButton(frame, text="Solo", command=lambda: choisir_mode("solo")).pack(pady=10)
    StyledButton(frame, text="IA", command=lambda: choisir_mode("ia")).pack(pady=10)
    StyledButton(frame, text="Multijoueur", command=lambda: choisir_mode("multijoueur")).pack(pady=10)

def choisir_mode(mode):
    global mode_de_jeu
    mode_de_jeu = mode
    afficher_selection_taille()

def afficher_selection_taille():
    for widget in fenetre.winfo_children():
        widget.destroy()

    create_title_label(fenetre, "Taille du Puzzle").pack()

    frame = tk.Frame(fenetre, bg=COLORS['background'], pady=20)
    frame.pack(expand=True)

    Label(
        frame,
        text="Choisissez la taille du puzzle",
        font=('Helvetica', 16),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack(pady=20)

    StyledButton(frame, text="3x3", command=lambda: start_game(3)).pack(pady=10)
    StyledButton(frame, text="4x4", command=lambda: start_game(4)).pack(pady=10)

    # Bouton Retour
    StyledButton(frame, text="Retour", command=afficher_selection_mode).pack(pady=10)

def start_game(size):
    global board_j1, board_j2, goal_state, photos, puzzle_canvas, shuffle_button, random_image_button
    if size == 3:
        board_j1 = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        board_j2 = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        goal_state = goal_state_3x3
    else:
        board_j1 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
        board_j2 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
        goal_state = goal_state_4x4

    photos = load_image_and_create_tiles(size)
    for widget in fenetre.winfo_children():
        widget.destroy()

    if mode_de_jeu == "multijoueur":
        start_multiplayer_game(size)
    else:
        game_frame = tk.Frame(fenetre, bg=COLORS['background'])
        game_frame.pack(expand=True)

        puzzle_canvas = Canvas(
            game_frame,
            width=size*150,
            height=size*150,
            bg=COLORS['white'],
            highlightthickness=2,
            highlightbackground=COLORS['primary']
        )
        puzzle_canvas.pack(pady=20)

        button_frame = tk.Frame(game_frame, bg=COLORS['background'])
        button_frame.pack(pady=20)

        if mode_de_jeu == "solo":
            puzzle_canvas.bind("<Button-1>", lambda e: disable_shuffle_button_and_move(e, board_j1, puzzle_canvas, shuffle_button))

        shuffle_button = StyledButton(button_frame, text="Mélanger", command=shuffle_puzzle)
        shuffle_button.pack(side='left', padx=10)

        # Bouton pour choisir une image aléatoire
        random_image_button = StyledButton(button_frame, text="Image Aléatoire", command=lambda: changer_image_et_recharger_puzzle(size))
        random_image_button.pack(side='left', padx=10)

        if mode_de_jeu == "ia":
           StyledButton(button_frame, text="Résolution IA (Manhattan)",
             command=lambda: handle_ia_button(shuffle_button, "manhattan")).pack(side='left', padx=10)
           StyledButton(button_frame, text="Résolution IA (Hamming)",
             command=lambda: handle_ia_button(shuffle_button, "hamming")).pack(side='left', padx=10)
        StyledButton(button_frame, text="Quitter", command=lambda: quitter_partie()).pack(side='left', padx=10)

        update_display()

def handle_ia_button(shuffle_button_ref, heuristic):
    """
    Gère le clic sur un bouton IA et affiche des informations sur l'heuristique choisie.
    Lance la résolution dans un thread pour ne pas bloquer l'UI.
    """
    if heuristic == "manhattan":
        if fenetre.winfo_exists():
            messagebox.showinfo("Heuristique Manhattan",
                                "L'heuristique Manhattan calcule la somme des distances absolues entre chaque tuile et sa position cible.")
    elif heuristic == "hamming":
        if fenetre.winfo_exists():
            messagebox.showinfo("Heuristique Hamming",
                                "L'heuristique Hamming compte le nombre de tuiles mal placées par rapport à leur position cible.")

    # Désactiver le bouton pendant la résolution
    try:
        shuffle_button_ref['state'] = 'disabled'
    except Exception:
        pass

    # Lancer la résolution dans un thread
    t = threading.Thread(target=solve_puzzle_and_disable_shuffle, args=(shuffle_button_ref, heuristic), daemon=True)
    t.start()

def changer_image_et_recharger_puzzle(size):
    """
    Change l'image utilisée pour le puzzle en sélectionnant une image aléatoire
    depuis le dossier 'shuffle', puis recharge le puzzle avec la nouvelle image.
    """
    global image_source_path, photos
    image_folder = "shuffle"
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)  # Crée le dossier s'il n'existe pas
    images = [f for f in os.listdir(image_folder) if f.endswith(".png")]
    if images:
        image_source_path = os.path.join(image_folder, random.choice(images))
        photos = load_image_and_create_tiles(size)  # Recharge les tuiles avec la nouvelle image
        update_display()

def start_multiplayer_game(size):
    global puzzle_canvas_j1, puzzle_canvas_j2, shuffle_button_j1, shuffle_button_j2, current_player

    for widget in fenetre.winfo_children():
        widget.destroy()

    create_title_label(fenetre, "Mode Multijoueur").pack()

    game_frame = tk.Frame(fenetre, bg=COLORS['background'])
    game_frame.pack(expand=True, pady=20)

    # Frame Joueur 1
    frame_j1 = tk.Frame(game_frame, bg=COLORS['background'])
    frame_j1.pack(side='left', padx=40)

    Label(
        frame_j1,
        text="Joueur 1",
        font=('Helvetica', 16, 'bold'),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack()

    puzzle_canvas_j1 = Canvas(
        frame_j1,
        width=size*150,
        height=size*150,
        bg=COLORS['white'],
        highlightthickness=2,
        highlightbackground=COLORS['primary']
    )
    puzzle_canvas_j1.pack(pady=10)

    shuffle_button_j1 = StyledButton(frame_j1, text="Mélanger", command=shuffle_puzzle_j1)
    shuffle_button_j1.pack(pady=5)
    StyledButton(frame_j1, text="Quitter", command=lambda: quitter_partie(1)).pack(pady=5)

    # Frame Joueur 2
    frame_j2 = tk.Frame(game_frame, bg=COLORS['background'])
    frame_j2.pack(side='right', padx=40)

    Label(
        frame_j2,
        text="Joueur 2",
        font=('Helvetica', 16, 'bold'),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack()

    puzzle_canvas_j2 = Canvas(
        frame_j2,
        width=size*150,
        height=size*150,
        bg=COLORS['white'],
        highlightthickness=2,
        highlightbackground=COLORS['primary']
    )
    puzzle_canvas_j2.pack(pady=10)

    shuffle_button_j2 = StyledButton(frame_j2, text="Mélanger", command=shuffle_puzzle_j2)
    shuffle_button_j2.pack(pady=5)
    StyledButton(frame_j2, text="Quitter", command=lambda: quitter_partie(2)).pack(pady=5)

    # Désactiver le plateau du joueur 2 et les boutons au départ
    disable_canvas(puzzle_canvas_j2)
    enable_canvas(puzzle_canvas_j1)

    # Lier les clics sur chaque puzzle
    puzzle_canvas_j1.bind("<Button-1>", move_tile_j1)
    puzzle_canvas_j2.bind("<Button-1>", move_tile_j2)

    update_display_j1()
    update_display_j2()

def move_tile_j1(event):
    global board_j1, current_player, shuffle_button_j1
    if current_player == 1:  # Vérifie que c'est bien le tour du joueur 1
        size = len(board_j1)
        x, y = event.x // 150, event.y // 150
        blank_x, blank_y = find_blank(board_j1)
        if abs(blank_x - y) + abs(blank_y - x) == 1:
            board_j1[blank_x][blank_y], board_j1[y][x] = board_j1[y][x], board_j1[blank_x][blank_y]
            update_display_j1()
            shuffle_button_j1['state'] = 'disabled'

            # Vérifie si le joueur 1 a gagné
            if board_j1 == goal_state:
                show_congratulations_multiplayer(1)
            else:
                # Passe au joueur 2
                current_player = 2
                disable_canvas(puzzle_canvas_j1)
                enable_canvas(puzzle_canvas_j2)

def move_tile_j2(event):
    global board_j2, current_player, shuffle_button_j2
    if current_player == 2:  # Vérifie que c'est bien le tour du joueur 2
        size = len(board_j2)
        x, y = event.x // 150, event.y // 150
        blank_x, blank_y = find_blank(board_j2)
        if abs(blank_x - y) + abs(blank_y - x) == 1:
            board_j2[blank_x][blank_y], board_j2[y][x] = board_j2[y][x], board_j2[blank_x][blank_y]
            update_display_j2()
            shuffle_button_j2['state'] = 'disabled'

            # Vérifie si le joueur 2 a gagné
            if board_j2 == goal_state:
                show_congratulations_multiplayer(2)
            else:
                # Passe au joueur 1
                current_player = 1
                disable_canvas(puzzle_canvas_j2)
                enable_canvas(puzzle_canvas_j1)

def show_congratulations_multiplayer(winning_player):
    """
    Affiche l'image complète et un message de félicitations pour le joueur gagnant.
    """
    try:
        # Charger l'image source
        image_source = Image.open(image_source_path)

        # Redimensionner l'image source à la taille du canvas
        size = len(board_j1)
        total_size = size * 150
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS
        image_source = image_source.resize((total_size, total_size), resample=resample_filter)

        # Convertir l'image pour tkinter
        image_complete = ImageTk.PhotoImage(image_source)

        # Afficher l'image complète dans le canvas correspondant
        if winning_player == 1:
            puzzle_canvas_j1.delete("all")
            puzzle_canvas_j1.create_image(0, 0, anchor=tk.NW, image=image_complete)
            puzzle_canvas_j1.image = image_complete
        elif winning_player == 2:
            puzzle_canvas_j2.delete("all")
            puzzle_canvas_j2.create_image(0, 0, anchor=tk.NW, image=image_complete)
            puzzle_canvas_j2.image = image_complete

        # Afficher un message de félicitations
        if fenetre.winfo_exists():
            messagebox.showinfo("Félicitations", f"Bravo ! Joueur {winning_player} a complété le puzzle !")
        afficher_page_accueil()

    except Exception as e:
        print("Erreur lors de l'affichage de l'image complète :", e)

def disable_canvas(canvas):
    """
    Désactive un canvas pour empêcher les clics.
    """
    canvas.unbind("<Button-1>")  # Supprime l'événement lié au clic

def enable_canvas(canvas):
    """
    Active un canvas pour autoriser les clics.
    """
    if canvas == puzzle_canvas_j1:
        canvas.bind("<Button-1>", move_tile_j1)
    elif canvas == puzzle_canvas_j2:
        canvas.bind("<Button-1>", move_tile_j2)

def disable_shuffle_button_and_move(event, board, puzzle_canvas, shuffle_button_ref):
    """
    Fonction générique appelée pour détecter un déplacement dans le puzzle.
    Désactive le bouton "Mélanger" après le premier déplacement.
    """
    size = len(board)
    x, y = event.x // 150, event.y // 150
    blank_x, blank_y = find_blank(board)
    if abs(blank_x - y) + abs(blank_y - x) == 1:
        # Obtenir la position de départ et d'arrivée
        start_x, start_y = blank_y * 150, blank_x * 150
        end_x, end_y = y * 150, x * 150

        # Déplacer la tuile dans le tableau
        board[blank_x][blank_y], board[y][x] = board[y][x], board[blank_x][blank_y]

        # Animer le déplacement si possible
        try:
            tile = puzzle_canvas.create_image(start_x, start_y, anchor=tk.NW, image=photos[board[y][x]])
            animate_tile(puzzle_canvas, tile, start_x, start_y, end_x, end_y)
        except Exception:
            pass

        # Supprimer l'ancienne position après l'animation
        puzzle_canvas.delete("all")
        for i in range(size):
            for j in range(size):
                value = board[i][j]
                if value != 0:
                    try:
                        puzzle_canvas.create_image(j * 150, i * 150, anchor=tk.NW, image=photos[value])
                    except Exception:
                        puzzle_canvas.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))

        try:
            if shuffle_button_ref['state'] == 'normal':
                shuffle_button_ref['state'] = 'disabled'
        except Exception:
            pass

        if board == goal_state:
            show_congratulations()

def shuffle_puzzle():
    global board_j1
    for _ in range(100):
        neighbors = generate_neighbors(board_j1)
        board_j1 = random.choice(neighbors)
    update_display()

def shuffle_puzzle_j1():
    global board_j1
    for _ in range(100):
        neighbors = generate_neighbors(board_j1)
        board_j1 = random.choice(neighbors)
    update_display_j1()

def shuffle_puzzle_j2():
    global board_j2
    for _ in range(100):
        neighbors = generate_neighbors(board_j2)
        board_j2 = random.choice(neighbors)
    update_display_j2()

def solve_puzzle_and_disable_shuffle(shuffle_button_ref, heuristic="manhattan"):
    """
    Résout le puzzle en utilisant l'algorithme A* dans un thread et lance l'exécution
    de la solution sur l'UI via fenetre.after.
    """
    global board_j1

    # Capture l'état initial (copie profonde)
    initial = [row[:] for row in board_j1]

    solution = a_star(initial, goal_state, heuristic=heuristic)

    # Si l'UI a été fermée pendant la recherche, on s'arrête proprement
    if not fenetre.winfo_exists():
        return

    if solution:
        # Exécuter la solution via fenetre.after pour rester dans le thread Tkinter
        fenetre.after(0, lambda: execute_solution(solution))
    else:
        # Réactiver le bouton si on n'a pas trouvé de solution ou si c'était impossible
        try:
            if fenetre.winfo_exists():
                messagebox.showinfo("Résolution", "Aucune solution trouvée ou limite d'exploration atteinte.")
        except Exception:
            pass
        try:
            shuffle_button_ref['state'] = 'normal'
        except Exception:
            pass

def find_blank(state):
    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j] == 0:
                return i, j
    return None

def manhattan_distance(state):
    distance = 0
    n = len(state)
    for i in range(n):
        for j in range(n):
            value = state[i][j]
            if value != 0:
                goal_i, goal_j = divmod(value - 1, n)
                distance += abs(goal_i - i) + abs(goal_j - j)
    return distance

def hamming_distance(state):
    distance = 0
    for i in range(len(state)):
        for j in range(len(state[i])):
            value = state[i][j]
            if value != 0 and value != goal_state[i][j]:
                distance += 1
    return distance

def generate_neighbors(state):
    """
    Retourne la liste d'états voisins en déplaçant la tuile vide.
    """
    neighbors = []
    x, y = find_blank(state)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in moves:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < len(state) and 0 <= new_y < len(state[0]):
            new_state = [row[:] for row in state]
            new_state[x][y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[x][y]
            neighbors.append(new_state)

    return neighbors

class Node:
    def __init__(self, state, parent=None, g=0, heuristic="manhattan"):
        self.state = state
        self.parent = parent
        self.g = g

        # Choisissez l'heuristique à utiliser
        if heuristic == "hamming":
            self.h = hamming_distance(state)
        else:  # Par défaut, utilisez Manhattan
            self.h = manhattan_distance(state)

        self.f = g + self.h

    def __lt__(self, other):
        return self.f < other.f

def a_star(initial_state, goal_state_param, heuristic="manhattan"):
    """
    Algorithme A* robuste avec closed_set et g_scores.
    Retourne la liste d'états de la solution (inclusive) ou None si échec / limite atteinte.
    """
    max_explored = 300000  # limite pour éviter explosion mémoire (ajuster si nécessaire)
    n = len(initial_state)

    def state_to_tuple(s):
        return tuple(tuple(row) for row in s)

    start_tuple = state_to_tuple(initial_state)
    goal_tuple = state_to_tuple(goal_state_param)

    open_heap = []
    start_node = Node(initial_state, parent=None, g=0, heuristic=heuristic)
    heapq.heappush(open_heap, (start_node.f, 0, start_node))  # tie-breaker by counter
    counter = 1

    g_scores = {start_tuple: 0}
    closed_set = set()
    explored = 0

    while open_heap:
        _, _, current_node = heapq.heappop(open_heap)
        current_tuple = state_to_tuple(current_node.state)

        # Si c'est le but, reconstituer la solution
        if current_tuple == goal_tuple:
            path = []
            node = current_node
            while node:
                path.append(node.state)
                node = node.parent
            path.reverse()
            return path

        if current_tuple in closed_set:
            continue

        closed_set.add(current_tuple)
        explored += 1
        if explored > max_explored:
            print("A*: limite d'exploration atteinte.")
            return None

        # Générer voisins
        for neighbor in generate_neighbors(current_node.state):
            neighbor_tuple = state_to_tuple(neighbor)
            tentative_g = current_node.g + 1

            # Si on a déjà un meilleur coût pour ce voisin, ignorer
            if neighbor_tuple in g_scores and tentative_g >= g_scores[neighbor_tuple]:
                continue

            g_scores[neighbor_tuple] = tentative_g
            child = Node(neighbor, parent=current_node, g=tentative_g, heuristic=heuristic)
            heapq.heappush(open_heap, (child.f, counter, child))
            counter += 1

    return None  # aucun chemin trouvé

def show_congratulations():
    """
    Affiche l'image complète lorsque le puzzle est résolu.
    """
    try:
        # Charger l'image source
        image_source = Image.open(image_source_path)

        # Redimensionner l'image source à la taille du canvas
        size = len(board_j1)
        total_size = size * 150
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS
        image_source = image_source.resize((total_size, total_size), resample=resample_filter)

        # Convertir l'image pour tkinter
        image_complete = ImageTk.PhotoImage(image_source)

        # Afficher l'image complète dans le canvas
        puzzle_canvas.delete("all")  # Nettoyer le canvas
        puzzle_canvas.create_image(0, 0, anchor=tk.NW, image=image_complete)
        puzzle_canvas.image = image_complete  # Conserver une référence à l'image

        # Afficher le message de félicitations
        if fenetre.winfo_exists():
            messagebox.showinfo("Félicitations", "Bravo ! Vous avez complété le puzzle !")

    except Exception as e:
        print("Erreur lors de l'affichage de l'image complète :", e)

def update_display():
    size = len(board_j1)
    puzzle_canvas.delete("all")
    if not photos:
        # fallback textuel si pas d'images chargées
        for i in range(size):
            for j in range(size):
                value = board_j1[i][j]
                if value != 0:
                    puzzle_canvas.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))
        return

    for i in range(size):
        for j in range(size):
            value = board_j1[i][j]
            if value != 0:
                if value < len(photos):
                    try:
                        puzzle_canvas.create_image(j*150, i*150, anchor=tk.NW, image=photos[value])
                    except Exception:
                        puzzle_canvas.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))

def update_display_j1():
    size = len(board_j1)
    puzzle_canvas_j1.delete("all")
    if not photos:
        for i in range(size):
            for j in range(size):
                value = board_j1[i][j]
                if value != 0:
                    puzzle_canvas_j1.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))
        return

    for i in range(size):
        for j in range(size):
            value = board_j1[i][j]
            if value != 0:
                if value < len(photos):
                    try:
                        puzzle_canvas_j1.create_image(j*150, i*150, anchor=tk.NW, image=photos[value])
                    except Exception:
                        puzzle_canvas_j1.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))

def update_display_j2():
    size = len(board_j2)
    puzzle_canvas_j2.delete("all")
    if not photos:
        for i in range(size):
            for j in range(size):
                value = board_j2[i][j]
                if value != 0:
                    puzzle_canvas_j2.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))
        return

    for i in range(size):
        for j in range(size):
            value = board_j2[i][j]
            if value != 0:
                if value < len(photos):
                    try:
                        puzzle_canvas_j2.create_image(j*150, i*150, anchor=tk.NW, image=photos[value])
                    except Exception:
                        puzzle_canvas_j2.create_text(j*150+75, i*150+75, text=str(value), font=('Helvetica', 24))

def execute_solution(solution, i=1):
    """
    Exécute la solution (appelée depuis le thread UI via fenetre.after).
    """
    global board_j1
    if not fenetre.winfo_exists():
        return

    if i < len(solution):
        board_j1 = solution[i]
        update_display()
        fenetre.after(300, execute_solution, solution, i+1)
    else:
        show_congratulations()

def quitter_partie(joueur=None):
    """
    Fonction générique appelée lorsqu'un joueur ou l'utilisateur clique sur "Quitter".
    """
    if joueur is not None:
        gagnant = "Joueur 2" if joueur == 1 else "Joueur 1"
        reponse = messagebox.askyesno("Confirmation", f"Joueur {joueur}, êtes-vous sûr de vouloir quitter ?")
        if reponse:
            messagebox.showinfo("Partie terminée", f"{gagnant} remporte la partie !")
            afficher_page_accueil()
    else:
        reponse = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir quitter ?")
        if reponse:
            afficher_page_accueil()

# Lancement de l'application
fenetre = tk.Tk()
setup_window(fenetre, "Jeu du Taquin")
style = ttk.Style()
style.configure('TFrame', background=COLORS['background'])
afficher_page_accueil()
fenetre.mainloop()
