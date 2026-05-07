import json
import sys
from enum import Enum, auto
from pathlib import Path
import pygame
from src.computer import ComputerPlayer
from src.discovery import HostBroadcaster, HostListener
from src.grid import Grid
from src.menu import Menu
from src.network import OnlineClient, OnlineServer


class GameState(Enum):
    MENU = auto()
    MODE_SELECT = auto()
    COLOR_SELECT = auto()
    ONLINE_MENU = auto()
    ONLINE_FIND = auto()
    HELP = auto()
    HIGHSCORES = auto()
    PLAYING = auto()
    RESIGN_CONFIRM = auto()
    GAME_OVER = auto()
    HIGHSCORE_INPUT = auto()


class GameMode(Enum):
    PVE = auto()
    PVP = auto()
    ONLINE = auto()


class Othello:
    def __init__(self):
        pygame.init()
        self.settings = self.load_settings()
        self.rows = self.settings["board"]["rows"]
        self.columns = self.settings["board"]["columns"]
        self.cell_size = self.settings["board"]["cell_size"]
        self.board_offset = self.settings["board"]["offset"]
        self.ai_depth = self.settings["ai"]["depth"]

        window_width = self.settings["window"]["width"]
        window_height = self.settings["window"]["height"]

        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(self.settings["window"]["title"])

        self.clock = pygame.time.Clock()

        self.currentPlayer = 1
        self.state = GameState.MENU
        self.mode = GameMode.PVE
        self.board_rotated = False
        self.winner = None
        self.game_over_reason = None
        self.skip_highscores = False
        self.pending_record_score = 0
        self.highscore_name = ""

        self.highscore_file = Path("config/highscores.json")
        self.grid = Grid(self, self.rows, self.columns, self.settings)
        self.computerPlayer = ComputerPlayer(self.grid)
        self.menu = Menu(self.screen)

        self.game_over_font = pygame.font.SysFont('Arial', 60, True)
        self.game_over_small_font = pygame.font.SysFont('Arial', 36)
        self.hud_font = pygame.font.SysFont('Arial', 26, True)

        self.rules = [
            "1. Игроки ходят по очереди, ставя фишки на пустые клетки.",
            "2. Ход возможен только если вы зажимаете фишки соперника.",
            "3. Все зажатые фишки переворачиваются в ваш цвет.",
            "4. Если ходов нет, ход передается сопернику.",
            "5. Игра завершается, когда оба не могут ходить.",
            "6. Побеждает тот, у кого больше фишек на поле.",
        ]

        self.time = 0
        self.player1Score = 0
        self.player2Score = 0
        self.human_player = 1
        self.ai_player = -1
        self.local_player = 1

        self.highscores = self.load_highscores()
        self.place_sound, self.flip_sound = self.load_sounds()
        self.music_state = "idle"
        self.start_music_starting_game_once()

        online_cfg = self.settings.get("online", {})
        self.online_tcp_port = int(online_cfg.get("tcp_port", 50007))
        self.discovery_port = int(online_cfg.get("discovery_port", 50008))
        self.discovery_interval_ms = int(online_cfg.get("discovery_interval_ms", 700))

        self.host_listener = None
        self.hosts = []
        self.host_selected = 0
        self.net_server = None
        self.net_client = None
        self.host_broadcaster = None
        self.online_connected = False
        self.resign_button_rect = None

    def load_settings(self):
        with open("config/settings.json", "r", encoding="utf-8") as file:
            return json.load(file)

    def load_highscores(self):
        if not self.highscore_file.exists():
            self.highscore_file.write_text('{"records": []}', encoding="utf-8")
            return []
        try:
            data = json.loads(self.highscore_file.read_text(encoding="utf-8"))
            return data.get("records", [])
        except json.JSONDecodeError:
            return []

    def save_highscores(self):
        payload = {"records": self.highscores[:10]}
        self.highscore_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_sounds(self):
        try:
            pygame.mixer.init()
            sfx_volume = self.settings["audio"]["sfx_volume"]
            music_cfg = self.settings.get("music", {})
            place = self.try_load_sound(music_cfg.get("place_token"))
            flip = self.try_load_sound(music_cfg.get("flip_token"))
            if place:
                place.set_volume(sfx_volume)
            return place, flip
        except:
            return None, None

    def try_find_track_path(self, base_path_without_ext):
        if not base_path_without_ext:
            return None
        for ext in (".ogg", ".mp3", ".wav"):
            path = f"{base_path_without_ext}{ext}"
            if Path(path).exists():
                return path
        if Path(base_path_without_ext).exists():
            return base_path_without_ext
        return None

    def try_load_sound(self, base_path_without_ext):
        path = self.try_find_track_path(base_path_without_ext)
        if not path:
            return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None

    def play_music_track(self, base_path_without_ext, loop=False):
        path = self.try_find_track_path(base_path_without_ext)
        if not path:
            return False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.settings["audio"]["music_volume"])
            pygame.mixer.music.play(-1 if loop else 0)
            return True
        except pygame.error:
            return False

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except:
            pass

    def start_music_starting_game_once(self):
        if self.music_state != "idle":
            return
        music_cfg = self.settings.get("music", {})
        if self.play_music_track(music_cfg.get("starting_game_once"), loop=False):
            self.music_state = "starting_once"
        else:
            self.start_music_background()

    def start_music_background(self):
        music_cfg = self.settings.get("music", {})
        if self.play_music_track(music_cfg.get("background_music"), loop=True):
            self.music_state = "background"
        else:
            self.music_state = "idle"

    def start_music_win(self):
        music_cfg = self.settings.get("music", {})
        if self.play_music_track(music_cfg.get("win"), loop=False):
            self.music_state = "result"

    def start_music_lose(self):
        music_cfg = self.settings.get("music", {})
        if self.play_music_track(music_cfg.get("lose"), loop=False):
            self.music_state = "result"

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == GameState.MENU:
                    self.handle_menu_input(event)
                elif self.state == GameState.MODE_SELECT:
                    self.handle_mode_select_input(event)
                elif self.state == GameState.COLOR_SELECT:
                    self.handle_color_select_input(event)
                elif self.state == GameState.ONLINE_MENU:
                    self.handle_online_menu_input(event)
                elif self.state == GameState.ONLINE_FIND:
                    self.handle_online_find_input(event)
                elif self.state == GameState.HELP:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                elif self.state == GameState.HIGHSCORES:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                elif self.state == GameState.PLAYING:
                    self.handle_playing_input(event)
                elif self.state == GameState.RESIGN_CONFIRM:
                    self.handle_resign_confirm_input(event)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over_input(event)
                elif self.state == GameState.HIGHSCORE_INPUT:
                    self.handle_highscore_input(event)

            if self.music_state == "starting_once":
                if not pygame.mixer.music.get_busy():
                    self.start_music_background()

            # Отрисовка
            if self.state == GameState.MENU:
                self.menu.draw()
            elif self.state == GameState.MODE_SELECT:
                self.menu.draw_mode_select()
            elif self.state == GameState.COLOR_SELECT:
                self.menu.draw_color_select()
            elif self.state == GameState.ONLINE_MENU:
                self.menu.draw_online_menu()
            elif self.state == GameState.ONLINE_FIND:
                self.update_online_find()
                self.menu.draw_online_host_list(self.hosts, self.host_selected)
            elif self.state == GameState.HELP:
                self.menu.draw_help(self.rules)
            elif self.state == GameState.HIGHSCORES:
                self.menu.draw_highscores(self.highscores)
            elif self.state == GameState.PLAYING:
                self.update()
                self.draw()
            elif self.state == GameState.RESIGN_CONFIRM:
                self.draw_resign_confirm()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.HIGHSCORE_INPUT:
                self.menu.draw_highscore_input(self.highscore_name, self.pending_record_score)

            self.clock.tick(60)
            pygame.display.update()

    # ==================== Обработчики ввода ====================

    def handle_menu_input(self, event):
        action = self.menu.handle_input(event)
        if action == "Начать игру":
            self.state = GameState.MODE_SELECT
        elif action == "Онлайн 1v1":
            self.state = GameState.ONLINE_MENU
        elif action == "Таблица рекордов":
            self.state = GameState.HIGHSCORES
        elif action == "Справка":
            self.state = GameState.HELP
        elif action == "Выход":
            pygame.quit()
            sys.exit()

    def handle_mode_select_input(self, event):
        action = self.menu.handle_input(event, mode=True)
        if action == "PvE":
            self.mode = GameMode.PVE
            self.state = GameState.COLOR_SELECT
        elif action == "PvP":
            self.mode = GameMode.PVP
            self.start_new_game()
        elif action == "Назад":
            self.state = GameState.MENU

    def handle_color_select_input(self, event):
        action = self.menu.handle_simple_list_input(event, self.menu.color_options, "color_selected")
        if action == "Белые":
            self.human_player = 1
            self.ai_player = -1
            self.start_new_game()
        elif action == "Чёрные":
            self.human_player = -1
            self.ai_player = 1
            self.start_new_game()
        elif action == "Назад":
            self.state = GameState.MODE_SELECT

    def handle_online_menu_input(self, event):
        action = self.menu.handle_simple_list_input(event, self.menu.online_options, "online_selected")
        if action == "Назад":
            self.stop_online()
            self.state = GameState.MENU
        elif action == "Хостить":
            self.start_online_host()
            self.state = GameState.ONLINE_FIND
        elif action == "Найти игру":
            self.start_online_find()
            self.state = GameState.ONLINE_FIND

    # ... (остальные методы start_online_host, start_online_find и т.д. без изменений) ...

    def start_online_host(self):
        self.stop_online()
        self.net_server = OnlineServer(host="0.0.0.0", port=self.online_tcp_port)
        self.net_server.start()
        self.host_broadcaster = HostBroadcaster(
            name="Ищу соперника",
            tcp_port=self.online_tcp_port,
            discovery_port=self.discovery_port,
            interval_ms=self.discovery_interval_ms,
        )
        self.host_broadcaster.start()
        self.start_online_find()

    def start_online_find(self):
        if not self.host_listener:
            self.host_listener = HostListener(self.discovery_port)
            self.host_listener.start()
        self.hosts = []
        self.host_selected = 0

    def update_online_find(self):
        if self.host_listener:
            self.hosts = self.host_listener.get_hosts()
        if self.host_selected >= len(self.hosts):
            self.host_selected = max(0, len(self.hosts) - 1)

        if self.net_server:
            for ev in self.net_server.poll():
                if ev.type == "client_connected":
                    self.start_online_game_as_host()

        if self.net_client:
            for ev in self.net_client.poll():
                if ev.type == "start":
                    self.local_player = int(ev.data.get("you", 1))
                    self.mode = GameMode.ONLINE
                    self.human_player = self.local_player
                    self.online_connected = True
                    self.start_new_game()
                elif ev.type == "disconnected":
                    self.stop_online()
                    self.state = GameState.MENU

    def handle_online_find_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.stop_online()
            self.state = GameState.ONLINE_MENU
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.host_selected = max(0, self.host_selected - 1)
            elif event.key == pygame.K_DOWN:
                self.host_selected = min(max(0, len(self.hosts) - 1), self.host_selected + 1)
            elif event.key == pygame.K_RETURN:
                self.join_selected_host()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.menu.handle_input(event)
            if isinstance(action, int):
                self.host_selected = action
                self.join_selected_host()

    def join_selected_host(self):
        if not self.hosts:
            return
        host = self.hosts[self.host_selected]
        if self.net_client:
            return
        try:
            self.net_client = OnlineClient(host.ip, host.port)
            self.net_client.connect(timeout=2.0)
            self.net_client.send({"type": "hello", "name": "Player"})
        except OSError:
            self.net_client = None

    def start_online_game_as_host(self):
        import random
        self.mode = GameMode.ONLINE
        self.online_connected = True
        host_color = random.choice([1, -1])
        self.local_player = host_color
        self.human_player = self.local_player
        if self.net_server:
            self.net_server.send_to_client({"type": "start", "you": -host_color})
        self.start_new_game()

    def stop_online(self):
        if self.host_broadcaster:
            self.host_broadcaster.stop()
            self.host_broadcaster = None
        if self.host_listener:
            self.host_listener.stop()
            self.host_listener = None
        if self.net_client:
            self.net_client.close()
            self.net_client = None
        if self.net_server:
            self.net_server.stop()
            self.net_server = None
        self.online_connected = False

    def start_new_game(self):
        self.grid.newGame()
        self.currentPlayer = 1
        self.board_rotated = False
        self.winner = None
        self.game_over_reason = None
        self.skip_highscores = False
        self.highscore_name = ""
        self.time = pygame.time.get_ticks()
        self.update_scores()
        self.state = GameState.PLAYING

    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.mode == GameMode.PVE and self.currentPlayer == self.ai_player:
                return
            if self.mode == GameMode.ONLINE and self.currentPlayer != self.local_player:
                return
            self.state = GameState.RESIGN_CONFIRM
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.resign_button_rect and self.resign_button_rect.collidepoint(event.pos):
                if self.mode == GameMode.PVE and self.currentPlayer == self.ai_player:
                    return
                if self.mode == GameMode.ONLINE and self.currentPlayer != self.local_player:
                    return
                self.state = GameState.RESIGN_CONFIRM
                return

            # Обычный ход
            if self.mode == GameMode.PVE and self.currentPlayer == self.ai_player:
                return
            if self.mode == GameMode.ONLINE and self.currentPlayer != self.local_player:
                return

            col, row = self.get_clicked_cell(pygame.mouse.get_pos())
            if row is None or col is None:
                return
            valid_moves = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
            if (row, col) in valid_moves:
                self.make_move(row, col, send_network=True)

    def handle_resign_confirm_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
            self.state = GameState.PLAYING
            return
        if event.key == pygame.K_y or event.key == pygame.K_RETURN:
            self.resign_current_player()
            return

    def resign_current_player(self):
        self.skip_highscores = True
        self.game_over_reason = "resign"
        if self.currentPlayer == 1:
            self.winner = "Black"
        else:
            self.winner = "White"
        self.start_music_lose()

        if self.mode == GameMode.ONLINE:
            if self.net_client:
                self.net_client.send({"type": "resign"})
            if self.net_server:
                self.net_server.send_to_client({"type": "resign"})

        self.state = GameState.GAME_OVER

    def get_clicked_cell(self, pos):
        x, y = pos
        col = (x - self.board_offset) // self.cell_size
        row = (y - self.board_offset) // self.cell_size
        if row < 0 or col < 0 or row >= self.rows or col >= self.columns:
            return None, None
        if self.mode == GameMode.PVP and self.board_rotated:
            row = self.rows - 1 - row
            col = self.columns - 1 - col
        return col, row

    def make_move(self, row, col, send_network=False):
        player = self.currentPlayer
        self.grid.insertToken(self.grid.gridLogic, player, row, col)

        if self.place_sound:
            self.place_sound.play()

        swappable = self.grid.swappableTiles(row, col, self.grid.gridLogic, player)
        for tile in swappable:
            self.grid.animateTransitions(tile, player)
            self.grid.gridLogic[tile[0]][tile[1]] *= -1
            self.grid.tokens[tile].player = player

        if self.flip_sound:
            self.flip_sound.play()

        self.currentPlayer *= -1
        if self.mode == GameMode.PVP:
            self.board_rotated = not self.board_rotated

        if self.mode == GameMode.ONLINE and send_network:
            if self.net_client:
                self.net_client.send({"type": "move", "row": row, "col": col})
            if self.net_server:
                self.net_server.send_to_client({"type": "move", "row": row, "col": col})

        self.time = pygame.time.get_ticks()
        self.update_scores()

    def update(self):
        if self.mode == GameMode.ONLINE:
            self.update_online_messages()

        if self.mode == GameMode.PVE and self.currentPlayer == self.ai_player:
            self.make_ai_move()

        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
            if self.grid.findAvailMoves(self.grid.gridLogic, -self.currentPlayer):
                self.currentPlayer *= -1
                if self.mode == GameMode.PVP:
                    self.board_rotated = not self.board_rotated
            else:
                self.finish_game()

        self.update_scores()

    def update_online_messages(self):
        if self.net_client:
            events = self.net_client.poll()
        elif self.net_server:
            events = self.net_server.poll()
        else:
            events = []

        for ev in events:
            if ev.type == "move":
                row = int(ev.data.get("row", -1))
                col = int(ev.data.get("col", -1))
                if 0 <= row < self.rows and 0 <= col < self.columns:
                    if (row, col) in self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                        self.make_move(row, col, send_network=False)
            elif ev.type == "resign":
                self.skip_highscores = True
                self.game_over_reason = "resign"
                self.winner = "White" if self.currentPlayer == -1 else "Black"
                self.start_music_win()
                self.state = GameState.GAME_OVER
            elif ev.type == "disconnected":
                self.stop_online()
                self.state = GameState.MENU

    def make_ai_move(self):
        new_time = pygame.time.get_ticks()
        if new_time - self.time < 300:
            return
        moves = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
        if not moves:
            return
        move, _ = self.computerPlayer.computerHard(
            self.grid.gridLogic, self.ai_depth, -1000, 1000, self.ai_player
        )
        if move:
            self.make_move(move[0], move[1], send_network=False)

    def update_scores(self):
        self.player1Score = self.grid.calculatePlayerScore(1)
        self.player2Score = self.grid.calculatePlayerScore(-1)
        self.grid.player1Score = self.player1Score
        self.grid.player2Score = self.player2Score

    def finish_game(self):
        if self.player1Score > self.player2Score:
            self.winner = "White"
            winner_score = self.player1Score
        elif self.player2Score > self.player1Score:
            self.winner = "Black"
            winner_score = self.player2Score
        else:
            self.winner = "Draw"
            winner_score = 0

        self.stop_music()

        if (not self.skip_highscores) and self.winner != "Draw" and self.is_top10_score(winner_score):
            self.pending_record_score = winner_score
            self.highscore_name = ""
            self.state = GameState.HIGHSCORE_INPUT
        else:
            self.state = GameState.GAME_OVER

        if self.winner == "White":
            self.start_music_win()
        elif self.winner == "Black":
            self.start_music_lose()

    def is_top10_score(self, score):
        if len(self.highscores) < 10:
            return True
        return score > self.highscores[-1]["score"]

    def handle_highscore_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.state = GameState.GAME_OVER
            return
        if event.key == pygame.K_BACKSPACE:
            self.highscore_name = self.highscore_name[:-1]
            return
        if event.key == pygame.K_RETURN:
            if self.highscore_name.strip():
                self.highscores.append({"name": self.highscore_name.strip()[:12], "score": self.pending_record_score})
                self.highscores.sort(key=lambda item: item["score"], reverse=True)
                self.highscores = self.highscores[:10]
                self.save_highscores()
            self.state = GameState.GAME_OVER
            return
        if len(self.highscore_name) < 12 and event.unicode.isprintable():
            self.highscore_name += event.unicode

    def handle_game_over_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = GameState.MODE_SELECT
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU

    # ==================== Отрисовка ====================

    def draw(self):
        self.screen.fill((0, 0, 0))
        rotated = self.mode == GameMode.PVP and self.board_rotated
        self.grid.drawGrid(self.screen, rotated=rotated)

        if self.mode in (GameMode.PVE, GameMode.ONLINE):
            color = "Белые" if self.human_player == 1 else "Чёрные"
            text = self.hud_font.render(f"Вы играете за {color}", True, (255, 255, 255))
            self.screen.blit(text, (20, self.settings["window"]["height"] - 40))

        if self.state == GameState.PLAYING:
            self.draw_resign_button()

    def draw_resign_button(self):
        btn_width = 180
        btn_height = 50
        x = self.settings["window"]["width"] - btn_width - 30
        y = self.settings["window"]["height"] - btn_height - 30

        self.resign_button_rect = pygame.Rect(x, y, btn_width, btn_height)

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.resign_button_rect.collidepoint(mouse_pos)

        color = (180, 30, 30) if is_hovered else (140, 20, 20)
        border_color = (255, 80, 80)

        pygame.draw.rect(self.screen, color, self.resign_button_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, self.resign_button_rect, width=3, border_radius=12)

        text = self.hud_font.render("Сдаться", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.resign_button_rect.center)
        self.screen.blit(text, text_rect)

    def draw_resign_confirm(self):
        self.draw()

        overlay = pygame.Surface((self.settings["window"]["width"], self.settings["window"]["height"]), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        text = self.game_over_small_font.render(
            "Точно сдаваться? (Y/Enter - да, N/Esc - нет)",
            True, (255, 215, 0)
        )
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, 360))
        self.screen.blit(text, text_rect)

    def draw_game_over(self):
        self.draw()

        overlay = pygame.Surface((self.settings["window"]["width"], self.settings["window"]["height"]))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "Draw":
            text = self.game_over_font.render("НИЧЬЯ!", True, (255, 215, 0))
        else:
            text = self.game_over_font.render(f"{self.winner} ПОБЕДИЛ!", True, (255, 215, 0))
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 180))

        if self.game_over_reason == "resign":
            reason = self.game_over_small_font.render("Победа по сдаче", True, (230, 230, 230))
            self.screen.blit(reason, (self.screen.get_width() // 2 - reason.get_width() // 2, 240))

        score_line = self.game_over_small_font.render(
            f"White: {self.player1Score} | Black: {self.player2Score}",
            True, (255, 255, 255)
        )
        self.screen.blit(score_line, (self.screen.get_width() // 2 - score_line.get_width() // 2, 280))

        hint = self.game_over_small_font.render("Enter - выбор режима, Esc - меню", True, (220, 220, 220))
        self.screen.blit(hint, (self.screen.get_width() // 2 - hint.get_width() // 2, 380))

    # ==================== Запуск ====================
if __name__ == "__main__":
    game = Othello()
    game.run()