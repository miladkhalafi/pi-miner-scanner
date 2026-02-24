#!/usr/bin/env python3
"""
Miner Scanner GUI for Raspberry Pi 3.5" TFT LCD 480x320 SPI touchscreen.
Scans LAN for ASIC miners (Whatsminer, Antminer, etc.) and displays all data.
"""

import os
import sys
import threading
from datetime import datetime

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, SUBNET
from scanner import run_scan
from gui.screens import HomeScreen, MinerListScreen, DetailScreen


def _setup_display_for_spi_tft() -> None:
    """Configure SDL for 3.5" TFT SPI framebuffer (before pygame.init)."""
    if os.environ.get("SDL_VIDEODRIVER"):
        return  # Already set (e.g. by launch script)
    if sys.platform == "linux" and os.path.exists("/dev/fb0"):
        os.putenv("SDL_VIDEODRIVER", "fbcon")
        os.putenv("SDL_FBDEV", os.environ.get("SDL_FBDEV", "/dev/fb0"))


def main() -> None:
    _setup_display_for_spi_tft()
    pygame.init()
    pygame.mouse.set_visible(True)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Miner Scanner")
    clock = pygame.time.Clock()

    miners: list[dict] = []
    scan_thread: threading.Thread | None = None

    def do_scan() -> None:
        nonlocal miners, scan_thread
        home.set_scanning(True)
        try:
            miners = run_scan(SUBNET)
        except Exception:
            miners = []
        finally:
            home.set_scanning(False)
            home.set_last_scan(datetime.now().strftime("%H:%M:%S"))
            home.set_miners(miners)
            list_screen.set_miners(miners)

    home = HomeScreen(on_scan=lambda: None)
    list_screen = MinerListScreen([], on_select=lambda d: None, on_back=lambda: None)
    detail_screen: DetailScreen | None = None

    def on_scan_click() -> None:
        nonlocal scan_thread
        if scan_thread and scan_thread.is_alive():
            return
        scan_thread = threading.Thread(target=do_scan, daemon=True)
        scan_thread.start()

    def on_select_miner(data: dict) -> None:
        nonlocal detail_screen
        detail_screen = DetailScreen(data, on_back=lambda: None)

    def on_back_from_list() -> None:
        pass

    def on_back_from_detail() -> None:
        pass

    home.on_scan = on_scan_click
    list_screen.on_select = on_select_miner
    list_screen.on_back = on_back_from_list

    current_screen: str = "home"
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if current_screen == "detail":
                    current_screen = "list"
                    detail_screen = None
                elif current_screen == "list":
                    current_screen = "home"
                else:
                    running = False
                continue

            next_screen = None
            if current_screen == "home":
                next_screen = home.handle_event(event)
            elif current_screen == "list":
                next_screen = list_screen.handle_event(event)
            elif current_screen == "detail" and detail_screen:
                next_screen = detail_screen.handle_event(event)

            if next_screen:
                current_screen = next_screen
                if current_screen == "list":
                    detail_screen = None

        screen.fill((30, 30, 40))
        if current_screen == "home":
            home.draw(screen)
        elif current_screen == "list":
            list_screen.draw(screen)
        elif current_screen == "detail" and detail_screen:
            detail_screen.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
