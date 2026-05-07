import pygame


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont('Arial', 60, True)
        self.font = pygame.font.SysFont('Arial', 38)
        self.small_font = pygame.font.SysFont('Arial', 28)
        self.options = ["Начать игру", "Онлайн 1v1", "Таблица рекордов", "Справка", "Выход"]
        self.mode_options = ["PvE", "PvP", "Назад"]
        self.color_options = ["Белые", "Чёрные", "Назад"]
        self.online_options = ["Хостить", "Найти игру", "Назад"]
        self.selected = 0
        self.mode_selected = 0
        self.color_selected = 0
        self.online_selected = 0
        self.last_rects = []

    def draw(self, title="РЕВЕРСИ"):
        self.screen.fill((0, 50, 0))
        title_surface = self.font_big.render(title, True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 100))
        self.last_rects = []
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected else (255, 215, 0)
            text = self.font.render(option, True, color)
            x = self.screen.get_width() // 2 - text.get_width() // 2
            y = 250 + i * 70
            self.screen.blit(text, (x, y))
            self.last_rects.append((pygame.Rect(x - 10, y - 6, text.get_width() + 20, text.get_height() + 12), option))

        pygame.display.update()

    def draw_mode_select(self):
        self.screen.fill((0, 40, 40))
        title_surface = self.font_big.render("РЕЖИМ ИГРЫ", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 130))

        self.last_rects = []
        for i, option in enumerate(self.mode_options):
            color = (255, 255, 255) if i != self.mode_selected else (255, 215, 0)
            text = self.font.render(option, True, color)
            x = self.screen.get_width() // 2 - text.get_width() // 2
            y = 280 + i * 70
            self.screen.blit(text, (x, y))
            self.last_rects.append((pygame.Rect(x - 10, y - 6, text.get_width() + 20, text.get_height() + 12), option))

        pygame.display.update()

    def draw_color_select(self):
        self.screen.fill((40, 30, 0))
        title_surface = self.font_big.render("ВЫБОР ЦВЕТА", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 130))
        self.last_rects = []
        for i, option in enumerate(self.color_options):
            color = (255, 255, 255) if i != self.color_selected else (255, 215, 0)
            text = self.font.render(option, True, color)
            x = self.screen.get_width() // 2 - text.get_width() // 2
            y = 280 + i * 70
            self.screen.blit(text, (x, y))
            self.last_rects.append((pygame.Rect(x - 10, y - 6, text.get_width() + 20, text.get_height() + 12), option))

        pygame.display.update()

    def draw_online_menu(self):
        self.screen.fill((20, 20, 45))
        title_surface = self.font_big.render("ОНЛАЙН 1v1", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 130))

        self.last_rects = []
        for i, option in enumerate(self.online_options):
            color = (255, 255, 255) if i != self.online_selected else (255, 215, 0)
            text = self.font.render(option, True, color)
            x = self.screen.get_width() // 2 - text.get_width() // 2
            y = 280 + i * 70
            self.screen.blit(text, (x, y))
            self.last_rects.append((pygame.Rect(x - 10, y - 6, text.get_width() + 20, text.get_height() + 12), option))

        hint = self.small_font.render("Enter/клик - выбрать", True, (180, 220, 180))
        self.screen.blit(hint, (80, self.screen.get_height() - 70))
        pygame.display.update()

    def draw_online_host_list(self, hosts, selected_index):
        self.screen.fill((15, 30, 35))
        title_surface = self.font_big.render("ДОСТУПНЫЕ ИГРОКИ", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 60))

        self.last_rects = []
        base_y = 170
        if not hosts:
            empty = self.small_font.render("Никого не найдено... (ищем)", True, (255, 255, 255))
            self.screen.blit(empty, (self.screen.get_width() // 2 - empty.get_width() // 2, base_y))
        else:
            for i, h in enumerate(hosts[:10]):
                row = f"{h.name}  ({h.ip}:{h.port})"
                color = (255, 255, 255) if i != selected_index else (255, 215, 0)
                text = self.small_font.render(row, True, color)
                x = 120
                y = base_y + i * 42
                self.screen.blit(text, (x, y))
                self.last_rects.append((pygame.Rect(x - 10, y - 6, text.get_width() + 20, text.get_height() + 12), i))

        hint = self.small_font.render("Enter/клик - подключиться, Esc - назад", True, (180, 220, 180))
        self.screen.blit(hint, (80, self.screen.get_height() - 70))
        pygame.display.update()

    def draw_help(self, rules):
        self.screen.fill((20, 20, 30))
        title_surface = self.font_big.render("СПРАВКА", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 50))

        for idx, line in enumerate(rules):
            rendered = self.small_font.render(line, True, (235, 235, 235))
            self.screen.blit(rendered, (80, 170 + idx * 42))

        hint = self.small_font.render("ESC - назад в меню", True, (180, 220, 180))
        self.screen.blit(hint, (80, self.screen.get_height() - 70))
        pygame.display.update()

    def draw_highscores(self, highscores):
        self.screen.fill((20, 35, 20))
        title_surface = self.font_big.render("ТАБЛИЦА РЕКОРДОВ", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 50))

        if not highscores:
            empty = self.small_font.render("Пока нет записей", True, (255, 255, 255))
            self.screen.blit(empty, (self.screen.get_width() // 2 - empty.get_width() // 2, 220))
        else:
            for idx, item in enumerate(highscores[:10], start=1):
                row = f"{idx:2}. {item['name']:<12}  {item['score']:>2}"
                color = (255, 255, 255) if idx > 3 else (255, 223, 120)
                rendered = self.small_font.render(row, True, color)
                self.screen.blit(rendered, (self.screen.get_width() // 2 - 160, 170 + idx * 42))

        hint = self.small_font.render("ESC - назад в меню", True, (180, 220, 180))
        self.screen.blit(hint, (80, self.screen.get_height() - 70))
        pygame.display.update()

    def draw_highscore_input(self, current_name, score):
        self.screen.fill((35, 20, 20))
        title_surface = self.font_big.render("НОВЫЙ РЕКОРД!", True, (255, 215, 0))
        self.screen.blit(title_surface, (self.screen.get_width() // 2 - title_surface.get_width() // 2, 80))

        prompt = self.small_font.render(f"Введите имя (score: {score}) и нажмите Enter:", True, (255, 255, 255))
        self.screen.blit(prompt, (self.screen.get_width() // 2 - prompt.get_width() // 2, 230))

        input_surface = self.font.render(current_name or "_", True, (255, 255, 0))
        self.screen.blit(input_surface, (self.screen.get_width() // 2 - input_surface.get_width() // 2, 300))

        hint = self.small_font.render("Backspace - удалить, ESC - отмена", True, (180, 220, 180))
        self.screen.blit(hint, (self.screen.get_width() // 2 - hint.get_width() // 2, 370))
        pygame.display.update()

    def handle_input(self, event, mode=False):
        options = self.mode_options if mode else self.options
        selected_attr = "mode_selected" if mode else "selected"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                setattr(self, selected_attr, (getattr(self, selected_attr) - 1) % len(options))
            elif event.key == pygame.K_DOWN:
                setattr(self, selected_attr, (getattr(self, selected_attr) + 1) % len(options))
            elif event.key == pygame.K_RETURN:
                return options[getattr(self, selected_attr)]
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            for rect, value in self.last_rects:
                if rect.collidepoint(mx, my):
                    return value
        return None

    def handle_simple_list_input(self, event, options, selected_attr):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                setattr(self, selected_attr, (getattr(self, selected_attr) - 1) % len(options))
            elif event.key == pygame.K_DOWN:
                setattr(self, selected_attr, (getattr(self, selected_attr) + 1) % len(options))
            elif event.key == pygame.K_RETURN:
                return options[getattr(self, selected_attr)]
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            for rect, value in self.last_rects:
                if rect.collidepoint(mx, my):
                    if isinstance(value, int):
                        setattr(self, selected_attr, value)
                        return options[value]
                    return value
        return None