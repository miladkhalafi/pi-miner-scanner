"""GUI components: buttons, list items, fonts for 3.5" TFT 480x320."""

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MIN_TOUCH_TARGET


# Colors
BG = (30, 30, 40)
FG = (220, 220, 220)
ACCENT = (70, 130, 180)
ACCENT_HOVER = (100, 160, 210)
ROW_ALT = (45, 45, 55)
BORDER = (80, 80, 90)
ERROR_COLOR = (200, 80, 80)


def get_font(size: int = 14) -> pygame.font.Font:
    """Return a font suitable for 480x320 display."""
    size = max(12, size)
    for name in ("dejavusansmono", "monospace", "courier", "liberationmono"):
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            continue
    return pygame.font.Font(None, size)


def get_bold_font(size: int = 14) -> pygame.font.Font:
    """Return a bold font."""
    try:
        return pygame.font.SysFont("monospace", max(12, size), bold=True)
    except Exception:
        return get_font(size)


class Button:
    """Touch-friendly button (min 44x44 px)."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font_size: int = 18,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = get_font(font_size)
        self.hover = False

    def draw(self, surface: pygame.Surface) -> None:
        color = ACCENT_HOVER if self.hover else ACCENT
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BORDER, self.rect, 2)
        text_surf = self.font.render(self.text, True, FG)
        tw, th = text_surf.get_size()
        tx = self.rect.x + (self.rect.w - tw) // 2
        ty = self.rect.y + (self.rect.h - th) // 2
        surface.blit(text_surf, (tx, ty))

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.contains(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(event.pos):
                return True
        return False


class MinerListItem:
    """Single row in miner list: IP | Model | TH/s."""

    def __init__(self, x: int, y: int, width: int, height: int, data: dict, index: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.data = data
        self.index = index
        self.font = get_font(12)
        self.alt_bg = index % 2 == 1

    def draw(self, surface: pygame.Surface) -> None:
        bg = ROW_ALT if self.alt_bg else BG
        pygame.draw.rect(surface, bg, self.rect)
        pygame.draw.line(surface, BORDER, (self.rect.x, self.rect.bottom), (self.rect.right, self.rect.bottom))
        ip = self.data.get("ip", "?")
        model = self.data.get("model", "?") or "?"
        hashrate = self.data.get("hashrate", "?") or "?"
        line = f"{ip} | {model} | {hashrate}"
        text_surf = self.font.render(line[:45], True, FG)
        surface.blit(text_surf, (self.rect.x + 4, self.rect.y + (self.rect.h - text_surf.get_height()) // 2))

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class ScrollableList:
    """Scrollable list with large up/down arrows for touch pen."""

    def __init__(self, x: int, y: int, width: int, height: int, item_height: int = 36):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_height = item_height
        self.items: list[dict] = []
        self.scroll_offset = 0
        self.arrow_size = max(MIN_TOUCH_TARGET, 48)
        self.up_rect = pygame.Rect(self.rect.right - self.arrow_size - 4, self.rect.y, self.arrow_size, self.arrow_size // 2)
        self.down_rect = pygame.Rect(self.rect.right - self.arrow_size - 4, self.rect.bottom - self.arrow_size // 2, self.arrow_size, self.arrow_size // 2)
        self.list_width = width - self.arrow_size - 8
        self.font = get_font(14)

    def set_items(self, items: list[dict]) -> None:
        self.items = items
        self.scroll_offset = 0

    def max_scroll(self) -> int:
        total_h = len(self.items) * self.item_height
        visible = self.rect.h
        return max(0, total_h - visible)

    def draw(self, surface: pygame.Surface) -> None:
        # Clip to list area
        list_rect = pygame.Rect(self.rect.x, self.rect.y, self.list_width, self.rect.h)
        surface.set_clip(list_rect)
        y = self.rect.y - self.scroll_offset
        for i, data in enumerate(self.items):
            item_rect = pygame.Rect(self.rect.x, y, self.list_width, self.item_height)
            if item_rect.colliderect(list_rect):
                item = MinerListItem(self.rect.x, y, self.list_width, self.item_height, data, i)
                item.draw(surface)
            y += self.item_height
        surface.set_clip(None)
        # Scroll arrows
        up_color = ACCENT if self.scroll_offset > 0 else BORDER
        down_color = ACCENT if self.scroll_offset < self.max_scroll() else BORDER
        pygame.draw.polygon(surface, up_color, [
            (self.up_rect.centerx, self.up_rect.y + 4),
            (self.up_rect.left + 8, self.up_rect.bottom - 4),
            (self.up_rect.right - 8, self.up_rect.bottom - 4),
        ])
        pygame.draw.polygon(surface, down_color, [
            (self.down_rect.centerx, self.down_rect.bottom - 4),
            (self.down_rect.left + 8, self.down_rect.y + 4),
            (self.down_rect.right - 8, self.down_rect.y + 4),
        ])

    def hit_test(self, pos: tuple[int, int]) -> tuple[str, int | None]:
        """Return ('up'|'down'|'item', index or None)."""
        if self.up_rect.collidepoint(pos) and self.scroll_offset > 0:
            return "up", None
        if self.down_rect.collidepoint(pos) and self.scroll_offset < self.max_scroll():
            return "down", None
        list_rect = pygame.Rect(self.rect.x, self.rect.y, self.list_width, self.rect.h)
        if not list_rect.collidepoint(pos):
            return "none", None
        rel_y = pos[1] - self.rect.y + self.scroll_offset
        idx = rel_y // self.item_height
        if 0 <= idx < len(self.items):
            return "item", idx
        return "none", None

    def scroll_up(self) -> None:
        self.scroll_offset = max(0, self.scroll_offset - self.item_height)

    def scroll_down(self) -> None:
        self.scroll_offset = min(self.max_scroll(), self.scroll_offset + self.item_height)
