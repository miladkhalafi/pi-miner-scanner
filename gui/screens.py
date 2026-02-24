"""Screens: Home, Miner List, Detail view."""

import pygame
from datetime import datetime

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MIN_TOUCH_TARGET
from gui.components import (
    Button,
    ScrollableList,
    get_font,
    BG,
    FG,
    ACCENT,
    BORDER,
    ERROR_COLOR,
)


class Screen:
    """Base screen."""

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Return next screen name or None."""
        return None

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def update(self, dt: float) -> None:
        pass


class HomeScreen(Screen):
    """Home: Scan button, last scan time, View Miners button."""

    def __init__(self, on_scan: callable):
        self.on_scan = on_scan
        self.last_scan: str | None = None
        self.scanning = False
        self.miners: list[dict] = []
        btn_w = 120
        btn_h = max(MIN_TOUCH_TARGET, 50)
        self.scan_btn = Button(
            (SCREEN_WIDTH - btn_w) // 2,
            SCREEN_HEIGHT // 2 - btn_h - 30,
            btn_w,
            btn_h,
            "Scan",
            font_size=20,
        )
        self.view_btn = Button(
            (SCREEN_WIDTH - btn_w) // 2,
            SCREEN_HEIGHT // 2 + 10,
            btn_w,
            btn_h,
            "View Miners",
            font_size=16,
        )
        self.font = get_font(14)
        self.title_font = get_font(18)

    def set_last_scan(self, when: str | None) -> None:
        self.last_scan = when

    def set_scanning(self, scanning: bool) -> None:
        self.scanning = scanning

    def set_miners(self, miners: list[dict]) -> None:
        self.miners = miners

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if self.scan_btn.handle_event(event):
            if not self.scanning:
                self.on_scan()
            return None
        if self.miners and self.view_btn.handle_event(event):
            return "list"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG)
        title = self.title_font.render("Miner Scanner", True, FG)
        surface.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 20))
        if self.scanning:
            self.scan_btn.text = "Scanning..."
            self.scan_btn.draw(surface)
            self.scan_btn.text = "Scan"
        else:
            self.scan_btn.draw(surface)
        if self.miners:
            self.view_btn.text = f"View ({len(self.miners)})"
            self.view_btn.draw(surface)
        if self.last_scan:
            txt = self.font.render(f"Last scan: {self.last_scan}", True, FG)
            surface.blit(txt, ((SCREEN_WIDTH - txt.get_width()) // 2, SCREEN_HEIGHT // 2 + 70))


class MinerListScreen(Screen):
    """Scrollable list of miners; tap row for detail."""

    def __init__(self, miners: list[dict], on_select: callable, on_back: callable):
        self.miners = miners
        self.on_select = on_select
        self.on_back = on_back
        self.list = ScrollableList(0, 40, SCREEN_WIDTH, SCREEN_HEIGHT - 90, item_height=36)
        self.list.set_items(miners)
        self.back_btn = Button(10, 5, 80, max(MIN_TOUCH_TARGET, 30), "Back", font_size=14)
        self.font = get_font(14)

    def set_miners(self, miners: list[dict]) -> None:
        self.miners = miners
        self.list.set_items(miners)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.contains(event.pos):
                self.on_back()
                return "home"
            kind, idx = self.list.hit_test(event.pos)
            if kind == "up":
                self.list.scroll_up()
            elif kind == "down":
                self.list.scroll_down()
            elif kind == "item" and idx is not None:
                self.on_select(self.miners[idx])
                return "detail"
        if event.type == pygame.MOUSEMOTION:
            self.back_btn.hover = self.back_btn.contains(event.pos)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG)
        self.back_btn.draw(surface)
        header = self.font.render(f"Miners ({len(self.miners)})", True, FG)
        surface.blit(header, (100, 12))
        self.list.draw(surface)


class DetailScreen(Screen):
    """All miner data: IP, hostname, model, hashrate, temp, fans, workers, etc."""

    def __init__(self, data: dict, on_back: callable):
        self.data = data
        self.on_back = on_back
        self.back_btn = Button(10, 5, 80, max(MIN_TOUCH_TARGET, 30), "Back", font_size=14)
        self.scroll = 0
        self.line_height = 16
        self.font = get_font(12)
        self.content_height = 0
        self.up_rect = pygame.Rect(SCREEN_WIDTH - 52, 45, 44, 44)
        self.down_rect = pygame.Rect(SCREEN_WIDTH - 52, SCREEN_HEIGHT - 90, 44, 44)

    def _build_lines(self) -> list[str]:
        lines = []
        d = self.data
        lines.append(f"IP: {d.get('ip', '')}")
        lines.append(f"Hostname: {d.get('hostname', '')}")
        lines.append(f"Model: {d.get('model', '')} ({d.get('make', '')})")
        lines.append(f"Firmware: {d.get('firmware', '')}")
        lines.append(f"Hashrate: {d.get('hashrate', '')}")
        lines.append(f"Expected: {d.get('expected_hashrate', '')}")
        lines.append(f"Wattage: {d.get('wattage', '')}W")
        lines.append(f"Efficiency: {d.get('efficiency', '')} J/TH")
        lines.append(f"Temp avg: {d.get('temperature_avg', '')}C")
        lines.append(f"Env temp: {d.get('env_temp', '')}C")
        lines.append(f"Uptime: {d.get('uptime', '')}s")
        lines.append(f"Mining: {d.get('is_mining', '')}")
        lines.append(f"Fault light: {d.get('fault_light', '')}")
        workers = d.get("workers", []) or []
        for i, (url, user) in enumerate(workers):
            lines.append(f"Pool {i+1}: {user or '(no worker)'}")
            if url:
                lines.append(f"  URL: {url[:50]}...")
        hashboards = d.get("hashboards", []) or []
        if hashboards:
            for i, hb in enumerate(hashboards[:4]):
                hr = hb.get("hashrate", "?")
                temp = hb.get("temp", "?")
                lines.append(f"Board {i+1}: {hr} {temp}C")
        fans = d.get("fans", []) or []
        if fans:
            speeds = [str(f.get("speed", "?")) for f in fans]
            lines.append(f"Fans: {', '.join(speeds)}")
        errors = d.get("errors", []) or []
        if errors:
            lines.append("Errors:")
            for e in errors[:5]:
                lines.append(f"  {str(e)[:60]}")
        return lines

    def _max_scroll(self) -> int:
        lines = self._build_lines()
        total_h = len(lines) * self.line_height
        visible = SCREEN_HEIGHT - 50
        return max(0, total_h - visible)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.contains(event.pos):
                self.on_back()
                return "list"
            if self.up_rect.collidepoint(event.pos) and self.scroll > 0:
                self.scroll = max(0, self.scroll - 40)
            if self.down_rect.collidepoint(event.pos) and self.scroll < self._max_scroll():
                self.scroll = min(self._max_scroll(), self.scroll + 40)
        if event.type == pygame.MOUSEMOTION:
            self.back_btn.hover = self.back_btn.contains(event.pos)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG)
        self.back_btn.draw(surface)
        lines = self._build_lines()
        y = 45 - self.scroll
        for line in lines:
            if y + self.line_height > 40 and y < SCREEN_HEIGHT:
                color = ERROR_COLOR if "Error" in line else FG
                txt = self.font.render(line[:60], True, color)
                surface.blit(txt, (10, y))
            y += self.line_height
        self.content_height = y + self.scroll
        # Scroll arrows
        up_color = ACCENT if self.scroll > 0 else BORDER
        down_color = ACCENT if self.scroll < self._max_scroll() else BORDER
        pygame.draw.polygon(surface, up_color, [
            (self.up_rect.centerx, self.up_rect.y + 8),
            (self.up_rect.left + 12, self.up_rect.bottom - 8),
            (self.up_rect.right - 12, self.up_rect.bottom - 8),
        ])
        pygame.draw.polygon(surface, down_color, [
            (self.down_rect.centerx, self.down_rect.bottom - 8),
            (self.down_rect.left + 12, self.down_rect.y + 8),
            (self.down_rect.right - 12, self.down_rect.y + 8),
        ])
