#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МИРА (MIRA) — AI-Ассистент v13.3 "NEBULA"
🧠 AI: Qwen 3 (latest) на Ollama
🔄 Управление процессами (закрытие приложений)
🔧 Интеллектуальная обработка ошибок (приложения не найдены)
📋 Установка Qwen 3: ollama pull qwen3
© CayPlay 2026. Все права защищены.
"""

import os, sys, json, logging, subprocess, threading, time, urllib.request, urllib.parse, webbrowser
import shutil, psutil, platform, re, winreg, math
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

import pyttsx3
import speech_recognition as sr
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QStatusBar,
    QSystemTrayIcon, QMenu, QDialog, QPlainTextEdit, QScrollArea,
    QStackedWidget, QMessageBox, QToolButton, QSizePolicy, QGraphicsDropShadowEffect
)

from PyQt6.QtGui import (
    QAction, QFont, QIcon, QColor, QPainter, QPixmap, QClipboard,
    QLinearGradient, QBrush, QPalette, QFontDatabase, QGradient, QMouseEvent
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QUrl, QSize, QObject,
    QPropertyAnimation, QEasingCurve, QRect, QPoint, QSequentialAnimationGroup
)
from PyQt6.QtGui import QDesktopServices

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("mira.log", encoding="utf-8")])
logger = logging.getLogger("MIRA")

def handle_exception(etype, value, tb):
    import traceback
    logger.error("".join(traceback.format_exception(etype, value, tb)))
sys.excepthook = handle_exception

# === КОНФИГУРАЦИЯ ===
CONFIG_PATH = Path("mira_config.json")

DEFAULT_CONFIG = {
    "ai": {
        "base_url": "http://localhost:11434",
        "model": "qwen3",
        "max_tokens": 4096,
        "temperature": 0.4
    },
    "commands": [
        {"trigger": "выключи компьютер", "action": "shutdown /s /t 30", "type": "system"},
        {"trigger": "перезагрузи компьютер", "action": "shutdown /r /t 30", "type": "system"},
        {"trigger": "заблокируй компьютер", "action": "rundll32.exe user32.dll,LockWorkStation", "type": "system"}
    ],
    "scripts": {},
    "aliases": {
        "калькулятор": "calc.exe", "блокнот": "notepad.exe", "проводник": "explorer.exe",
        "диспетчер задач": "taskmgr.exe", "реестр": "regedit.exe", "командная строка": "cmd.exe",
        "терминал": "wt.exe", "пауэршелл": "powershell.exe", "браузер": "msedge.exe",
        "хром": "chrome.exe", "firefox": "firefox.exe", "опера": "opera.exe", "яндекс браузер": "browser.exe",
        "стим": "steam.exe", "обс": "obs64.exe", "обс студио": "obs64.exe", "obs": "obs64.exe",
        "дискорд": "discord.exe", "телеграм": "Telegram.exe", "вк": "VK.exe",
        "vs code": "code.exe", "визуал студио": "devenv.exe", "pycharm": "pycharm64.exe",
        "геометри дэш": "GeometryDash.exe", "geometry dash": "GeometryDash.exe",
        "майнкрафт": "minecraft.exe", "minecraft": "minecraft.exe", "mc": "minecraft.exe"
    },
    "search_engines": {
        "google": "https://www.google.com/search?q=",
        "yandex": "https://yandex.ru/search/?text=",
        "duckduckgo": "https://duckduckgo.com/?q="
    },
    "default_search": "yandex",
    "unrestricted": {
        "enabled": True,
        "search_paths": [
            "C:\\Program Files\\", "C:\\Program Files (x86)\\",
            "C:\\Users\\{}\\AppData\\Local\\Programs\\",
            "C:\\Users\\{}\\AppData\\Roaming\\",
            os.environ.get("PATH", "")
        ],
        "game_launchers": [
            "C:\\Program Files\\Epic Games\\",
            "C:\\Program Files (x86)\\GOG Galaxy\\",
            "C:\\Program Files\\Origin Games\\",
            "C:\\Program Files (x86)\\Ubisoft\\",
            "C:\\Program Files\\Battle.net\\",
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\",
        ]
    },
    "voice": {"language": "ru-RU", "speed": 160},
    "contacts": {"telegram": "@CayPlay78", "vk": "https://m.vk.com/cayplay"}
}

def load_config() -> Dict:
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        
        # Автоисправление: заменяем старые названия моделей на qwen3
        old_models = ["qwen3:3.5b", "qwen2.5:1.5b", "qwen2.5:3.5b"]
        if cfg.get("ai", {}).get("model") in old_models:
            cfg["ai"]["model"] = "qwen3"
            cfg["ai"]["max_tokens"] = 4096
            logger.info("Модель обновлена на qwen3")
        
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
            elif isinstance(v, dict) and isinstance(cfg[k], dict):
                for sk, sv in v.items():
                    if sk not in cfg[k]:
                        cfg[k][sk] = sv
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return cfg
    except Exception as e:
        logger.error(f"Config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

# === ТЕМА И ДИЗАЙН ===

class Theme:
    """Премиальная тёмная тема с фиолетовыми акцентами"""
    BG_DEEP = "#06060f"
    BG_MAIN = "#0c0c1d"
    BG_SURFACE = "#12122a"
    BG_ELEVATED = "#1a1a35"
    BG_GLASS = "rgba(18, 18, 42, 0.75)"
    
    ACCENT = "#8b5cf6"
    ACCENT_LIGHT = "#a78bfa"
    ACCENT_DARK = "#7c3aed"
    ACCENT_GLOW = "rgba(139, 92, 246, 0.25)"
    
    GRADIENT_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8b5cf6, stop:0.5 #a78bfa, stop:1 #7c3aed)"
    GRADIENT_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9b6cf6, stop:0.5 #b78bfa, stop:1 #8c4aed)"
    GRADIENT_PRESSED = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7b4ce6, stop:0.5 #978bfa, stop:1 #6c2add)"
    
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    TEXT_ACCENT = "#c4b5fd"
    
    SUCCESS = "#10b981"
    ERROR = "#ef4444"
    WARNING = "#f59e0b"
    INFO = "#3b82f6"
    
    BORDER = "rgba(139, 92, 246, 0.15)"
    BORDER_FOCUS = "rgba(139, 92, 246, 0.4)"
    BORDER_HOVER = "rgba(139, 92, 246, 0.3)"

class StyledButton(QPushButton):
    """Современная кнопка с градиентом, тенями и анимацией"""
    def __init__(self, text="", parent=None, accent=False, icon_text=""):
        super().__init__(f"{icon_text} {text}".strip(), parent)
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self._setup_shadow()
        self._apply_style()
        
    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(139, 92, 246, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def _apply_style(self):
        if self.accent:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.GRADIENT_PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 14px;
                    padding: 14px 28px;
                    font-weight: 700;
                    letter-spacing: 0.3px;
                }}
                QPushButton:hover {{
                    background: {Theme.GRADIENT_HOVER};
                }}
                QPushButton:pressed {{
                    background: {Theme.GRADIENT_PRESSED};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.BG_ELEVATED};
                    color: {Theme.TEXT_PRIMARY};
                    border: 1.5px solid {Theme.BORDER};
                    border-radius: 14px;
                    padding: 14px 24px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {Theme.BG_SURFACE};
                    border-color: {Theme.BORDER_HOVER};
                }}
                QPushButton:pressed {{
                    background: {Theme.BG_MAIN};
                    border-color: {Theme.BORDER_FOCUS};
                }}
            """)

class GlassCard(QFrame):
    """Карточка с эффектом матового стекла"""
    def __init__(self, parent=None, padding=24):
        super().__init__(parent)
        self.setObjectName("glassCard")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        self.setStyleSheet(f"""
            #glassCard {{
                background: {Theme.BG_GLASS};
                border: 1.5px solid {Theme.BORDER};
                border-radius: 20px;
                padding: {padding}px;
            }}
            #glassCard:hover {{
                border-color: {Theme.BORDER_HOVER};
                background: rgba(25, 25, 50, 0.8);
            }}
        """)

class AnimatedVoiceButton(QPushButton):
    """Кнопка голосового ввода с пульсирующей анимацией"""
    def __init__(self, parent=None):
        super().__init__("🎤", parent)
        self.setFixedSize(52, 52)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.listening = False
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._pulse)
        self._pulse_scale = 1.0
        self._pulse_dir = 0.04
        self._base_size = 52
        self.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.BG_ELEVATED};
                border: 2px solid {Theme.BORDER};
                border-radius: 26px;
                font-size: 22px;
            }}
            QPushButton:hover {{
                border-color: {Theme.BORDER_HOVER};
                background: {Theme.BG_SURFACE};
            }}
        """)
        
    def set_listening(self, active: bool):
        self.listening = active
        if active:
            self._anim_timer.start(80)
        else:
            self._anim_timer.stop()
            self.setFixedSize(self._base_size, self._base_size)
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.BG_ELEVATED};
                    border: 2px solid {Theme.BORDER};
                    border-radius: 26px;
                    font-size: 22px;
                }}
            """)
            
    def _pulse(self):
        self._pulse_scale += self._pulse_dir
        if self._pulse_scale > 1.12 or self._pulse_scale < 1.0:
            self._pulse_dir *= -1
        size = int(self._base_size * self._pulse_scale)
        self.setFixedSize(size, size)
        alpha = int(180 + (self._pulse_scale - 1) * 300)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(139, 92, 246, {alpha/255:.2f}), 
                    stop:1 rgba(167, 139, 250, {alpha/255:.2f}));
                border: 2px solid {Theme.ACCENT_LIGHT};
                border-radius: {size//2}px;
                font-size: 22px;
            }}
        """)

class StatusWave(QFrame):
    """Анимированная волна загрузки"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)
        self.active = False
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        
    def set_active(self, active: bool):
        self.active = active
        if active:
            self.timer.start(40)
        else:
            self.timer.stop()
            self.update()
            
    def _animate(self):
        self.offset = (self.offset + 3) % 300
        self.update()
        
    def paintEvent(self, event):
        if not self.active:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        gradient = QLinearGradient(self.offset - 300, 0, self.offset + 300, 0)
        gradient.setColorAt(0, QColor(139, 92, 246, 0))
        gradient.setColorAt(0.3, QColor(167, 139, 250, 100))
        gradient.setColorAt(0.5, QColor(196, 181, 253, 255))
        gradient.setColorAt(0.7, QColor(167, 139, 250, 100))
        gradient.setColorAt(1, QColor(139, 92, 246, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, 3, 1.5, 1.5)

# === БЭКЕНД ===

class ProcessManager:
    """Управление процессами Windows (закрытие приложений)"""
    
    APP_MAP = {
        "блокнот": "notepad.exe",
        "калькулятор": "CalculatorApp.exe",
        "проводник": "explorer.exe",
        "диспетчер задач": "Taskmgr.exe",
        "браузер": ["msedge.exe", "chrome.exe", "firefox.exe", "opera.exe"],
        "хром": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "стим": "steam.exe",
        "дискорд": "discord.exe",
        "телеграм": "Telegram.exe",
        "obs": "obs64.exe",
        "обс": "obs64.exe",
        "майнкрафт": ["javaw.exe", "minecraft.exe"],
    }
    
    @staticmethod
    def find_process(name: str) -> Optional[psutil.Process]:
        """Находит процесс по имени приложения"""
        name = name.lower().strip()
        
        targets = ProcessManager.APP_MAP.get(name, name)
        if isinstance(targets, str):
            targets = [targets]
        elif not isinstance(targets, list):
            targets = [name]
            
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                proc_exe = (proc.info['exe'] or "").lower()
                
                for target in targets:
                    target_lower = target.lower()
                    if proc_name == target_lower:
                        return proc
                    if target_lower in proc_exe:
                        return proc
                    if target_lower.replace('.exe', '') in proc_name.replace('.exe', ''):
                        return proc
                    if len(target_lower) > 4 and target_lower.replace('.exe', '') in proc_name:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    @staticmethod
    def close_app(name: str) -> Tuple[bool, str]:
        """Закрывает приложение по названию"""
        proc = ProcessManager.find_process(name)
        if proc:
            try:
                app_name = proc.name()
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    proc.kill()
                return True, f"✅ Закрыто: {app_name}"
            except Exception as e:
                return False, f"❌ Ошибка при закрытии: {e}"
        return False, f"❌ Приложение «{name}» не запущено"
    
    @staticmethod
    def get_running_apps() -> List[str]:
        """Возвращает список запущенных приложений с GUI"""
        apps = set()
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                exe = proc.info['exe']
                if exe and "windows" not in exe.lower() and "system32" not in exe.lower():
                    name = proc.info['name'].replace('.exe', '')
                    if name and len(name) > 1:
                        apps.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sorted(list(apps))[:20]

class OmniResolver:
    def __init__(self, config: Dict):
        self.aliases = {k.lower(): v for k, v in config.get("aliases", DEFAULT_CONFIG["aliases"]).items()}
        self.paths = config.get("unrestricted", {}).get("search_paths", [])
        self.game_paths = config.get("unrestricted", {}).get("game_launchers", [])
        self.user = os.getlogin() if hasattr(os, "getlogin") else "User"
        self.steam_path = self._find_steam()
        self._steam_games_cache = {}
        self._scan_steam_games()
        
    def _find_steam(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                return winreg.QueryValueEx(k, "SteamPath")[0]
        except: pass
        for p in ["C:\\Program Files (x86)\\Steam", "D:\\Games\\Steam"]:
            if os.path.exists(os.path.join(p, "steam.exe")): return p
        return None
    
    def _scan_steam_games(self):
        if not self.steam_path: return
        vdf_path = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        libraries = [os.path.join(self.steam_path, "steamapps", "common")]
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f.read().split("\n"):
                        if '"path"' in line:
                            match = re.search(r'"path"\s*"([^"]+)"', line)
                            if match:
                                lib_path = match.group(1).replace("\\\\", "\\")
                                common = os.path.join(lib_path, "steamapps", "common")
                                if os.path.isdir(common): libraries.append(common)
            except: pass
        for lib in libraries:
            if not os.path.isdir(lib): continue
            for folder in os.listdir(lib):
                folder_path = os.path.join(lib, folder)
                if not os.path.isdir(folder_path): continue
                for root, _, files in os.walk(folder_path):
                    if root.replace(folder_path, '').count(os.sep) > 1: break
                    for f in files:
                        if f.lower().endswith('.exe') and not f.lower().startswith(('unins', 'setup', 'install')):
                            exe_path = os.path.join(root, f)
                            self._steam_games_cache[folder.lower()] = exe_path
                            self._steam_games_cache[f.lower().replace('.exe','')] = exe_path
    
    def _search_registry_apps(self, name: str):
        name = name.lower()
        for key_path in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0].lower()
                                    if name in display_name or display_name in name:
                                        for val_name in ["InstallLocation", "UninstallString", "DisplayIcon"]:
                                            try:
                                                val = winreg.QueryValueEx(subkey, val_name)[0]
                                                if val and isinstance(val, str):
                                                    exe = val.replace('"','').split(',')[0].strip()
                                                    if exe.lower().endswith('.exe') and os.path.exists(exe): return exe
                                                    elif os.path.isdir(exe):
                                                        for root, _, files in os.walk(exe):
                                                            if root.replace(exe, '').count(os.sep) > 1: break
                                                            for f in files:
                                                                if name.replace(' ','') in f.lower().replace(' ','') and f.lower().endswith('.exe'):
                                                                    return os.path.join(root, f)
                                            except: pass
                                except: pass
                        except: pass
            except: pass
        return None
    
    def _search_start_menu(self, name: str):
        name = name.lower()
        start_paths = [
            os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs")
        ]
        for start_path in start_paths:
            if not os.path.isdir(start_path): continue
            for root, _, files in os.walk(start_path):
                for f in files:
                    if f.lower().endswith('.lnk') or f.lower().endswith('.exe'):
                        if name in f.lower().replace('.lnk','').replace('.exe',''):
                            shortcut = os.path.join(root, f)
                            if shortcut.lower().endswith('.lnk'):
                                try:
                                    import pythoncom
                                    from win32com.shell import shell
                                    pythoncom.CoInitialize()
                                    shortcut_obj = shell.CreateShellLink(shortcut)
                                    target = shortcut_obj.GetPath(shell.SLGP_UNCPRIORITY)[0]
                                    if target and os.path.exists(target): return target
                                except: pass
                            elif os.path.exists(shortcut): return shortcut
        return None
    
    def resolve(self, raw_cmd: str) -> Optional[str]:
        cmd = raw_cmd.lower().strip(".,!?;:- \"'")
        for verb in ["открой", "запусти", "включи", "покажи", "открыть", "запустить", "включить", "найди", "запусти игру"]:
            if cmd.startswith(verb):
                cmd = cmd.replace(verb, "").strip()
                break
        
        if cmd in self.aliases:
            exe = self.aliases[cmd]
            if shutil.which(exe): return shutil.which(exe)
            return exe
        for alias, exe in self.aliases.items():
            if alias in cmd or cmd in alias:
                if shutil.which(exe): return shutil.which(exe)
                return exe
        
        for game_name, exe_path in self._steam_games_cache.items():
            if game_name in cmd or cmd in game_name:
                if os.path.exists(exe_path): return exe_path
        
        if shutil.which(cmd): return shutil.which(cmd)
        if shutil.which(cmd + ".exe"): return shutil.which(cmd + ".exe")
        
        reg_result = self._search_registry_apps(cmd)
        if reg_result: return reg_result
        
        start_result = self._search_start_menu(cmd)
        if start_result: return start_result
        
        for base in self.game_paths + [p.format(self.user) for p in self.paths]:
            if not base or not os.path.isdir(base): continue
            for root, dirs, files in os.walk(base):
                if root.replace(base, '').count(os.sep) > 2: dirs[:] = []
                for f in files:
                    f_lower = f.lower()
                    if f_lower.endswith(('.exe','.bat','.cmd','.lnk')):
                        f_name = f_lower.replace('.exe','').replace('.bat','').replace('.cmd','').replace('.lnk','')
                        if cmd == f_name or cmd == f_lower:
                            return os.path.join(root, f)
        return cmd
    
    def _get_friendly_name(self, command: str) -> str:
        """Возвращает понятное название приложения для сообщений"""
        cmd = command.lower().strip(".,!?;:- \"'")
        for verb in ["открой", "запусти", "включи", "покажи", "открыть", "запустить", "включить", "найди"]:
            if cmd.startswith(verb):
                cmd = cmd.replace(verb, "").strip()
                break
        return cmd.capitalize()

class SystemExecutor:
    def __init__(self, config: Dict):
        self.resolver = OmniResolver(config)
        self.search_engines = config.get("search_engines", DEFAULT_CONFIG["search_engines"])
        self.default_search = config.get("default_search", "yandex")
        
    def search_web(self, query: str, engine: str = None) -> str:
        engine = engine or self.default_search
        url = self.search_engines.get(engine, self.search_engines["yandex"]) + urllib.parse.quote(query)
        try:
            webbrowser.open(url)
            return f"✅ Поиск в {engine.capitalize()}: {query}"
        except Exception as e:
            return f"❌ Ошибка поиска: {e}"
    
    def execute(self, command: str, ctype: str = "auto") -> str:
        try:
            if command.startswith("SEARCH:"):
                query = command.replace("SEARCH:", "").strip()
                return self.search_web(query)
            if command.startswith("CLOSE:"):
                app_name = command.replace("CLOSE:", "").strip()
                success, msg = ProcessManager.close_app(app_name)
                return msg
            if command.startswith("steam://"):
                os.startfile(command)
                return f"✅ Steam: {command}"
            if ctype == "auto":
                if command.lower().startswith(("shutdown","restart","lock","rundll32")): ctype = "system"
                elif command.lower().startswith("powershell"): ctype = "powershell"
                elif Path(command).exists(): ctype = "file"
                else: ctype = "app"
            if ctype == "powershell":
                res = subprocess.run(["powershell","-Command",command], capture_output=True, text=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
                return res.stdout.strip() or res.stderr.strip() or "✅ Выполнено"
            elif ctype == "file":
                os.startfile(command) if platform.system()=="Windows" else None
                return f"✅ Открыто: {command}"
            else:
                # Проверяем существование приложения ПЕРЕД запуском
                resolved = self.resolver.resolve(command)
                logger.info(f"Resolve '{command}' -> '{resolved}'")
                
                # Проверяем, что это реальный путь к файлу
                if resolved and Path(resolved).exists():
                    try:
                        subprocess.Popen(resolved, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        app_name = Path(resolved).stem
                        return f"✅ Запущено: {app_name}"
                    except Exception as e:
                        return f"❌ Не удалось запустить: {e}"
                
                # Проверяем, есть ли такая команда в PATH
                elif resolved and shutil.which(resolved):
                    try:
                        subprocess.Popen(resolved, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        return f"✅ Запущено: {resolved}"
                    except Exception as e:
                        return f"❌ Не удалось запустить: {e}"
                
                # Пробуем запустить как есть (может быть системной командой)
                elif command.lower() in ["cmd", "cmd.exe", "powershell", "powershell.exe"] or \
                     shutil.which(command.split()[0] if ' ' in command else command):
                    try:
                        subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        return f"✅ Запущено: {command}"
                    except Exception as e:
                        return f"❌ Не удалось запустить: {e}"
                
                # Приложение не найдено — информативное сообщение
                else:
                    search_name = command.lower().strip(".,!?;:- \"'")
                    for verb in ["открой", "запусти", "включи", "покажи", "открыть", "запустить", "включить", "найди"]:
                        if search_name.startswith(verb):
                            search_name = search_name.replace(verb, "").strip()
                            break
                    
                    friendly_name = self.resolver._get_friendly_name(command)
                    
                    # Проверяем алиасы для подсказки
                    if search_name in self.resolver.aliases:
                        exe_path = self.resolver.aliases[search_name]
                        return f"❌ Не могу найти приложение «{friendly_name}»\n💡 Ожидаемый файл: {exe_path}\nПроверьте, установлено ли приложение"
                    
                    # Проверяем, может это игра из Steam
                    if self.resolver.steam_path:
                        for game_name in self.resolver._steam_games_cache:
                            if search_name in game_name or game_name in search_name:
                                return f"❌ Игра «{friendly_name}» найдена в Steam, но исполняемый файл не обнаружен\n💡 Попробуйте запустить через Steam"
                    
                    return f"❌ Не могу найти приложение «{friendly_name}»\n💡 Проверьте название или установите программу"
                    
        except Exception as e:
            return f"❌ Ошибка: {e}"

class VoiceManager:
    def __init__(self, config: Dict):
        vc = config.get("voice", DEFAULT_CONFIG["voice"])
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 300
        self.mic = None
        self.engine = None
        try:
            self.mic = sr.Microphone()
            with self.mic as s: self.rec.adjust_for_ambient_noise(s, duration=0.5)
        except: pass
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("language", vc["language"])
            self.engine.setProperty("rate", vc.get("speed", 160))
        except: pass
    def listen_once(self, timeout=5, limit=10):
        if not self.mic: return None
        try:
            with self.mic as source:
                self.rec.adjust_for_ambient_noise(source, duration=0.3)
                return self.rec.listen(source, timeout=timeout, phrase_time_limit=limit)
        except: return None
    def recognize(self, audio):
        try: return self.rec.recognize_google(audio, language="ru-RU").strip()
        except: return None
    def speak(self, text: str):
        if not self.engine: return
        threading.Thread(target=lambda: (self.engine.say(text), self.engine.runAndWait()), daemon=True).start()

class AIManager:
    def __init__(self, config: Dict):
        ai_cfg = config.get("ai", DEFAULT_CONFIG["ai"])
        self.base_url = ai_cfg["base_url"]
        self.model = ai_cfg["model"]  # "qwen3"
        self.ai_history = [{"role":"system","content":"Ты МИРА, ИИ-ассистент на базе Qwen 3. Отвечай кратко, умно и по делу. Помогай с любыми вопросами."}]
        self.ai_available = False
        self.available_models = []
        self._detect_qwen_model()
        
    def _detect_qwen_model(self):
        """Автоматически находит доступную модель Qwen"""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as r:
                data = json.loads(r.read())
                models = [m["name"] for m in data.get("models", [])]
                self.available_models = models
                
                # ПРИОРИТЕТ: ищем точное совпадение "qwen3:latest" или "qwen3"
                qwen_exact = [m for m in models if m == "qwen3:latest" or m == "qwen3"]
                if qwen_exact:
                    self.model = qwen_exact[0]
                    self.ai_available = True
                    logger.info(f"Найдена Qwen 3 (latest): {self.model}")
                    return
                
                # Ищем любую Qwen 3 (с тегами размера)
                qwen3_models = [m for m in models if "qwen3" in m.lower()]
                if qwen3_models:
                    self.model = qwen3_models[0]
                    self.ai_available = True
                    logger.info(f"Найдена Qwen 3: {self.model}")
                    return
                
                # Ищем Qwen 2.5 как запасной вариант
                qwen25_models = [m for m in models if "qwen2.5" in m.lower()]
                if qwen25_models:
                    self.model = qwen25_models[0]
                    self.ai_available = True
                    logger.info(f"Qwen 3 не найдена, использую Qwen 2.5: {self.model}")
                    return
                
                # Ищем любую Qwen
                qwen_any = [m for m in models if "qwen" in m.lower()]
                if qwen_any:
                    self.model = qwen_any[0]
                    self.ai_available = True
                    logger.info(f"Использую: {self.model}")
                    return
                
                # Ищем другие популярные модели
                for m in models:
                    if any(name in m.lower() for name in ["llama3", "mistral", "phi"]):
                        self.model = m
                        self.ai_available = True
                        logger.info(f"Qwen не найдена, использую: {self.model}")
                        return
                
                # Ничего не найдено
                logger.warning("Не найдено подходящих моделей")
                self.model = "qwen3"
                
        except Exception as e:
            logger.error(f"Ошибка подключения к Ollama: {e}")
            self.model = "qwen3"
    
    def ask(self, prompt: str) -> str:
        if not self.ai_available:
            return ("⚠️ Qwen 3 не найдена в Ollama\n\n"
                   "📥 Установите модель:\n"
                   "• ollama pull qwen3\n\n"
                   "📋 Проверьте список моделей:\n"
                   "• ollama list")
        
        self.ai_history.append({"role":"user","content":prompt})
        if len(self.ai_history) > 10: 
            self.ai_history = [self.ai_history[0]] + self.ai_history[-8:]
        
        try:
            payload = json.dumps({
                "model": self.model,
                "messages": self.ai_history,
                "stream": False
            }).encode()
            
            req = urllib.request.Request(
                f"{self.base_url}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=60) as r:
                ans = json.loads(r.read())["message"]["content"]
                self.ai_history.append({"role":"assistant","content":ans})
                return ans.strip()
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                return f"❌ Модель '{self.model}' не установлена\n📥 Выполните: ollama pull {self.model}"
            return f"🌐 Ошибка AI: {error_msg}"
    
    def clear(self): 
        self.ai_history = [self.ai_history[0]]

# === ПОТОКИ ===
class AIWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, ai: AIManager, prompt: str):
        super().__init__()
        self.ai = ai
        self.prompt = prompt
    def run(self): self.result.emit(self.ai.ask(self.prompt))

class CmdWorker(QThread):
    result = pyqtSignal(str)
    def __init__(self, executor: SystemExecutor, command: str, ctype: str):
        super().__init__()
        self.executor = executor
        self.command = command
        self.ctype = ctype
    def run(self): self.result.emit(self.executor.execute(self.command, self.ctype))

class ScriptWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str)
    def __init__(self, executor: SystemExecutor, name: str, commands: List[str]):
        super().__init__()
        self.executor = executor
        self.name = name
        self.commands = commands
    def run(self):
        for i, cmd in enumerate(self.commands):
            cmd = cmd.strip()
            if not cmd: continue
            self.progress.emit(i+1, len(self.commands), cmd)
            self.executor.execute(cmd, "auto")
            time.sleep(1.2)
        self.finished.emit(self.name)

# === ИНТЕРФЕЙС ===

class Sidebar(QFrame):
    nav_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(88)
        self.setStyleSheet(f"""
            #sidebar {{
                background: {Theme.BG_DEEP};
                border-right: 1.5px solid {Theme.BORDER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 32, 12, 32)
        layout.setSpacing(16)
        
        # Логотип
        logo_container = QFrame()
        logo_container.setFixedSize(64, 64)
        logo_container.setStyleSheet(f"""
            background: {Theme.GRADIENT_PRIMARY};
            border-radius: 20px;
        """)
        logo_lay = QVBoxLayout(logo_container)
        logo_lay.setContentsMargins(0, 0, 0, 0)
        logo = QLabel("✦")
        logo.setFont(QFont("Segoe UI Emoji", 28))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: white; background: transparent;")
        logo_lay.addWidget(logo)
        layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(8)
        
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {Theme.BORDER};")
        layout.addWidget(sep)
        
        layout.addSpacing(8)
        
        self.nav_btns = {}
        nav_items = [
            ("chat", "💬", "Чат с ИИ"),
            ("scripts", "⚡", "Сценарии"),
            ("processes", "📋", "Процессы"),
            ("contacts", "👤", "Контакты"),
            ("settings", "⚙", "Настройки"),
            ("about", "ℹ", "О Мире")
        ]
        
        for nav_id, icon, tooltip in nav_items:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(tooltip)
            btn.setProperty("nav_id", nav_id)
            btn.setFixedSize(56, 56)
            btn.setFont(QFont("Segoe UI Emoji", 20))
            btn.setCheckable(True)
            btn.clicked.connect(self._on_nav)
            btn.setStyleSheet(f"""
                QToolButton {{
                    background: transparent;
                    color: {Theme.TEXT_MUTED};
                    border: none;
                    border-radius: 16px;
                    font-size: 22px;
                }}
                QToolButton:hover {{
                    background: rgba(139, 92, 246, 0.12);
                    color: {Theme.TEXT_PRIMARY};
                }}
                QToolButton:checked {{
                    background: {Theme.GRADIENT_PRIMARY};
                    color: white;
                }}
            """)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            self.nav_btns[nav_id] = btn
            
        self.nav_btns["chat"].setChecked(True)
        layout.addStretch()
        
        self.status_dot = QLabel("●")
        self.status_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_dot.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 14px;")
        self.status_dot.setToolTip("Qwen 3 онлайн")
        layout.addWidget(self.status_dot)
        
    def _on_nav(self):
        btn = self.sender()
        nav_id = btn.property("nav_id")
        for b in self.nav_btns.values(): b.setChecked(False)
        btn.setChecked(True)
        self.nav_changed.emit(nav_id)

class ChatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"background: {Theme.BG_DEEP}; border-bottom: 1.5px solid {Theme.BORDER};")
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(24, 0, 24, 0)
        title = QLabel("💬 Чат с МИРОЙ")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; background: transparent;")
        header_lay.addWidget(title)
        header_lay.addStretch()
        clear_btn = QPushButton("Очистить")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Theme.TEXT_SECONDARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {Theme.BG_SURFACE};
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        clear_btn.clicked.connect(lambda: self.chat.clear())
        header_lay.addWidget(clear_btn)
        layout.addWidget(header)
        
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setObjectName("chatArea")
        self.chat.setStyleSheet(f"""
            #chatArea {{
                background: {Theme.BG_MAIN};
                border: none;
                color: {Theme.TEXT_PRIMARY};
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                padding: 24px;
                line-height: 1.7;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.BORDER_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        layout.addWidget(self.chat, 1)
        
        self.status_wave = StatusWave()
        layout.addWidget(self.status_wave)
        
        input_frame = QFrame()
        input_frame.setStyleSheet(f"background: {Theme.BG_DEEP}; border-top: 1.5px solid {Theme.BORDER};")
        input_lay = QHBoxLayout(input_frame)
        input_lay.setContentsMargins(24, 16, 24, 16)
        input_lay.setSpacing(12)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Напишите сообщение или команду...")
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {Theme.BG_SURFACE};
                border: 2px solid {Theme.BORDER};
                border-radius: 16px;
                padding: 16px 24px;
                color: {Theme.TEXT_PRIMARY};
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border-color: {Theme.BORDER_FOCUS};
                background: {Theme.BG_ELEVATED};
            }}
        """)
        input_lay.addWidget(self.input, 1)
        
        self.send_btn = StyledButton("", accent=True, icon_text="➤")
        self.send_btn.setFixedSize(52, 52)
        input_lay.addWidget(self.send_btn)
        
        self.voice_btn = AnimatedVoiceButton()
        input_lay.addWidget(self.voice_btn)
        
        layout.addWidget(input_frame)

class ProcessPanel(QFrame):
    """Панель управления процессами"""
    close_signal = pyqtSignal(str)
    refresh_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("processPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        header = QHBoxLayout()
        title = QLabel("📋 Управление процессами")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()
        refresh_btn = StyledButton("Обновить", icon_text="🔄")
        refresh_btn.clicked.connect(lambda: self.refresh_signal.emit())
        header.addWidget(refresh_btn)
        layout.addLayout(header)
        
        hint = QLabel("Здесь показаны запущенные приложения. Нажмите ✕ чтобы закрыть.")
        hint.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(hint)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER};
                border-radius: 4px;
            }}
        """)
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        self.process_layout = QVBoxLayout(self.content)
        self.process_layout.setSpacing(8)
        self.process_layout.addStretch()
        layout.addWidget(self.scroll, 1)
        
        quick_frame = QFrame()
        quick_frame.setStyleSheet(f"background: {Theme.BG_DEEP}; border-radius: 16px; padding: 20px;")
        quick_lay = QHBoxLayout(quick_frame)
        quick_lay.setSpacing(12)
        
        self.quick_input = QLineEdit()
        self.quick_input.setPlaceholderText("Название приложения для закрытия...")
        self.quick_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Theme.BG_SURFACE};
                border: 2px solid {Theme.BORDER};
                border-radius: 12px;
                padding: 14px 20px;
                color: {Theme.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {Theme.BORDER_FOCUS};
            }}
        """)
        quick_lay.addWidget(self.quick_input, 1)
        
        close_btn = StyledButton("Закрыть", accent=True, icon_text="✕")
        close_btn.clicked.connect(lambda: self.close_signal.emit(self.quick_input.text()))
        quick_lay.addWidget(close_btn)
        
        layout.addWidget(quick_frame)
    
    def update_processes(self):
        while self.process_layout.count() > 1:
            item = self.process_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        apps = ProcessManager.get_running_apps()
        if not apps:
            empty = QLabel("Нет запущенных приложений")
            empty.setStyleSheet(f"color: {Theme.TEXT_MUTED}; padding: 40px; font-size: 15px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.process_layout.insertWidget(0, empty)
            return
        
        for app_name in apps:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {Theme.BG_GLASS};
                    border: 1.5px solid {Theme.BORDER};
                    border-radius: 14px;
                    padding: 12px 20px;
                }}
                QFrame:hover {{
                    border-color: {Theme.BORDER_HOVER};
                    background: rgba(25, 25, 50, 0.8);
                }}
            """)
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(0, 0, 0, 0)
            
            icon = QLabel("●")
            icon.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 12px; background: transparent;")
            card_lay.addWidget(icon)
            
            name_label = QLabel(app_name.capitalize())
            name_label.setFont(QFont("Segoe UI", 13))
            name_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; background: transparent;")
            card_lay.addWidget(name_label, 1)
            
            close_btn = QPushButton("✕")
            close_btn.setFixedSize(36, 36)
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Theme.TEXT_MUTED};
                    border: 1px solid {Theme.BORDER};
                    border-radius: 10px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background: rgba(239, 68, 68, 0.15);
                    color: {Theme.ERROR};
                    border-color: {Theme.ERROR};
                }}
            """)
            close_btn.clicked.connect(lambda checked, n=app_name: self.close_signal.emit(n))
            card_lay.addWidget(close_btn)
            
            self.process_layout.insertWidget(self.process_layout.count() - 1, card)

class ScriptPanel(QFrame):
    run_signal = pyqtSignal(str)
    create_signal = pyqtSignal()
    
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        header = QHBoxLayout()
        title = QLabel("⚡ Сценарии")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()
        add_btn = StyledButton("Создать", accent=True, icon_text="+")
        add_btn.clicked.connect(lambda: self.create_signal.emit())
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}")
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        self.content_lay = QVBoxLayout(self.content)
        self.content_lay.setSpacing(16)
        layout.addWidget(self.scroll, 1)
        self.refresh_scripts()
        
    def refresh_scripts(self):
        while self.content_lay.count():
            w = self.content_lay.takeAt(0).widget()
            if w: w.deleteLater()
        scripts = self.cfg.get("scripts", {})
        if not scripts:
            empty = QLabel("Нет сценариев. Создайте первый!")
            empty.setStyleSheet(f"color: {Theme.TEXT_MUTED}; padding: 60px; font-size: 16px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_lay.addWidget(empty)
            return
        for name, cmds in scripts.items():
            card = GlassCard(padding=20)
            card_lay = QVBoxLayout(card)
            header = QHBoxLayout()
            h = QLabel(f"📋 {name}")
            h.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            h.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; background: transparent;")
            header.addWidget(h)
            header.addStretch()
            run_btn = StyledButton("Запустить", accent=True, icon_text="▶")
            run_btn.clicked.connect(lambda checked, n=name: self.run_signal.emit(n))
            header.addWidget(run_btn)
            del_btn = StyledButton("", icon_text="✕")
            del_btn.setFixedWidth(48)
            del_btn.clicked.connect(lambda checked, n=name: self._delete_script(n))
            header.addWidget(del_btn)
            card_lay.addLayout(header)
            steps = QLabel(f"📌 {len(cmds)} шагов")
            steps.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 13px; background: transparent;")
            card_lay.addWidget(steps)
            self.content_lay.addWidget(card)
            
    def _delete_script(self, name: str):
        if name in self.cfg.get("scripts", {}):
            del self.cfg["scripts"][name]
            save_config(self.cfg)
            self.refresh_scripts()

class ContactsPanel(QFrame):
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 80, 80, 80)
        layout.setSpacing(40)
        
        title = QLabel("👤 Контакты разработчика")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(title)
        
        for icon, label, value, url in [
            ("✈️", "Telegram", config.get("contacts", {}).get("telegram", "@CayPlay78"), "https://t.me/CayPlay78"),
            ("🔵", "ВКонтакте", config.get("contacts", {}).get("vk", "https://m.vk.com/cayplay"), config.get("contacts", {}).get("vk", "https://m.vk.com/cayplay"))
        ]:
            card = GlassCard(padding=28)
            card_lay = QHBoxLayout(card)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 36))
            icon_label.setStyleSheet("background: transparent;")
            card_lay.addWidget(icon_label)
            
            info_lay = QVBoxLayout()
            name_label = QLabel(label)
            name_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            name_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; background: transparent;")
            value_label = QLabel(value)
            value_label.setFont(QFont("Consolas", 15))
            value_label.setStyleSheet(f"color: {Theme.ACCENT_LIGHT}; background: transparent;")
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            info_lay.addWidget(name_label)
            info_lay.addWidget(value_label)
            card_lay.addLayout(info_lay)
            card_lay.addStretch()
            
            copy_btn = StyledButton("Копировать", icon_text="📋")
            copy_btn.clicked.connect(lambda checked, v=value: self._copy(v))
            card_lay.addWidget(copy_btn)
            
            open_btn = StyledButton("Открыть", accent=True, icon_text="↗")
            open_btn.clicked.connect(lambda checked, u=url: QDesktopServices.openUrl(QUrl(u)))
            card_lay.addWidget(open_btn)
            
            layout.addWidget(card)
        layout.addStretch()
        
    def _copy(self, text: str):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Скопировано", f"✅ {text}\nскопирован в буфер обмена")

class SettingsPanel(QFrame):
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(28)
        
        title = QLabel("⚙ Настройки системы")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(title)
        
        self.labels = {}
        for key, icon, label in [
            ("ai", "🧠", "Искусственный интеллект (Qwen 3)"),
            ("voice", "🎤", "Голосовой ввод"),
            ("steam", "🎮", "Steam интеграция")
        ]:
            card = GlassCard(padding=24)
            card_lay = QVBoxLayout(card)
            t = QLabel(f"{icon} {label}")
            t.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            t.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; background: transparent;")
            card_lay.addWidget(t)
            lbl = QLabel("Проверка...")
            lbl.setFont(QFont("Consolas", 14))
            lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; background: transparent;")
            card_lay.addWidget(lbl)
            self.labels[key] = lbl
            layout.addWidget(card)
        layout.addStretch()
        
    def update_ui(self, ai_ok: bool, voice_ok: bool, steam_path: Optional[str]):
        self.labels["ai"].setText(f"{'✅' if ai_ok else '❌'} Ollama: {self.cfg['ai']['model']} (Qwen 3)")
        self.labels["ai"].setStyleSheet(f"color: {'#10b981' if ai_ok else '#ef4444'}; font-size: 15px; background: transparent;")
        self.labels["voice"].setText(f"{'✅' if voice_ok else '❌'} Микрофон {'готов' if voice_ok else 'не найден'}")
        self.labels["voice"].setStyleSheet(f"color: {'#10b981' if voice_ok else '#ef4444'}; font-size: 15px; background: transparent;")
        self.labels["steam"].setText(f"{'✅' if steam_path else '❌'} Steam: {steam_path or 'Не найден'}")
        self.labels["steam"].setStyleSheet(f"color: {'#10b981' if steam_path else '#ef4444'}; font-size: 15px; background: transparent;")

class AboutPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = GlassCard(padding=48)
        card.setFixedWidth(580)
        card_lay = QVBoxLayout(card)
        card_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.setSpacing(20)

        logo = QLabel("✦")
        logo.setFont(QFont("Segoe UI Emoji", 56))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {Theme.ACCENT}; background: transparent;")
        card_lay.addWidget(logo)

        title = QLabel("MIRA")
        title.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(title)

        version = QLabel("v13.3 \"Nebula\"")
        version.setFont(QFont("Consolas", 14))
        version.setStyleSheet(f"color: {Theme.ACCENT_LIGHT}; background: transparent;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(version)

        model_info = QLabel("🧠 Модель: Qwen 3 (latest)")
        model_info.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        model_info.setStyleSheet(f"color: {Theme.SUCCESS}; background: transparent;")
        model_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(model_info)

        desc = QLabel("Локальный ИИ-ассистент на базе Qwen 3\nГолос, текст, сценарии, поиск и управление ПК")
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; background: transparent;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        card_lay.addWidget(desc)

        features = QLabel("✨ Возможности:\n• Чат с ИИ • Голосовое управление • Сценарии автоматизации\n• Управление процессами • Поиск в интернете • Запуск любых приложений")
        features.setFont(QFont("Segoe UI", 12))
        features.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; background: transparent; line-height: 1.8;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(features)

        copyright_lbl = QLabel("© CayPlay 2026. Все права защищены.")
        copyright_lbl.setFont(QFont("Segoe UI", 11))
        copyright_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; background: transparent;")
        copyright_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(copyright_lbl)

        btns_lay = QHBoxLayout()
        btns_lay.setSpacing(16)
        btns_lay.addStretch()
        gh_btn = StyledButton("GitHub", icon_text="🐙")
        gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/CayPlayProjects")))
        tg_btn = StyledButton("Telegram", accent=True, icon_text="✈️")
        tg_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/CayPlay78")))
        btns_lay.addWidget(gh_btn)
        btns_lay.addWidget(tg_btn)
        btns_lay.addStretch()
        card_lay.addLayout(btns_lay)

        layout.addWidget(card, 0, Qt.AlignmentFlag.AlignCenter)

# === ГЛАВНОЕ ОКНО ===

class MIRAWindow(QMainWindow):
    voice_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.executor = SystemExecutor(self.cfg)
        self.ai = AIManager(self.cfg)
        self.voice = VoiceManager(self.cfg)
        
        self.voice_signal.connect(self._on_voice)
        self.active_threads = []
        self._drag_pos = None  # Для перетаскивания окна
        
        self._setup_ui()
        self._apply_global_style()
        self._init_tray()
        
        self.showFullScreen()
        QTimer.singleShot(400, self._boot)

    def _setup_ui(self):
        self.setWindowTitle("MIRA — AI Ассистент")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # === ЗАГОЛОВОК ОКНА (РАБОЧИЕ КНОПКИ + ПЕРЕТАСКИВАНИЕ) ===
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet(f"background: {Theme.BG_DEEP}; border-bottom: 1.5px solid {Theme.BORDER};")
        
        # Добавляем поддержку перетаскивания
        self.title_bar.mousePressEvent = self._title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self._title_bar_mouse_move
        self.title_bar.mouseDoubleClickEvent = self._title_bar_double_click
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(20, 0, 8, 0)
        
        self.title_label = QLabel("✦ MIRA")
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {Theme.ACCENT_LIGHT}; background: transparent;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        # Кнопка "Свернуть" (─)
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setFixedSize(40, 32)
        self.minimize_btn.setToolTip("Свернуть")
        self.minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Theme.TEXT_MUTED};
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.08);
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_btn)
        
        # Кнопка "Развернуть/Восстановить" (□/❐)
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(40, 32)
        self.maximize_btn.setToolTip("Развернуть")
        self.maximize_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Theme.TEXT_MUTED};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.08);
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        title_layout.addWidget(self.maximize_btn)
        
        # Кнопка "Закрыть" (✕)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 32)
        self.close_btn.setToolTip("Закрыть")
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Theme.TEXT_MUTED};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        root_layout.addWidget(self.title_bar)
        
        # === ОСТАЛЬНОЙ КОНТЕНТ ===
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self._switch_page)
        content_layout.addWidget(self.sidebar)
        
        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet(f"background: {Theme.BG_MAIN};")
        
        self.chat_panel = ChatPanel()
        self.chat_panel.send_btn.clicked.connect(self._process)
        self.chat_panel.input.returnPressed.connect(self._process)
        self.chat_panel.voice_btn.clicked.connect(self._toggle_voice)
        self.stacked.addWidget(self.chat_panel)
        
        self.script_panel = ScriptPanel(self.cfg)
        self.script_panel.run_signal.connect(self._run_script)
        self.script_panel.create_signal.connect(self._create_script_dialog)
        self.stacked.addWidget(self.script_panel)
        
        self.process_panel = ProcessPanel()
        self.process_panel.close_signal.connect(self._close_process)
        self.process_panel.refresh_signal.connect(lambda: self.process_panel.update_processes())
        self.stacked.addWidget(self.process_panel)
        
        self.contacts_panel = ContactsPanel(self.cfg)
        self.stacked.addWidget(self.contacts_panel)
        
        self.settings_panel = SettingsPanel(self.cfg)
        self.stacked.addWidget(self.settings_panel)
        
        self.about_panel = AboutPanel()
        self.stacked.addWidget(self.about_panel)
        
        content_layout.addWidget(self.stacked, 1)
        root_layout.addWidget(content_widget, 1)

    # Методы для перетаскивания окна
    def _title_bar_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def _title_bar_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def _title_bar_double_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {Theme.BG_MAIN};
            }}
            QToolTip {{
                background: {Theme.BG_ELEVATED};
                color: {Theme.TEXT_PRIMARY};
                border: 1.5px solid {Theme.BORDER};
                border-radius: 10px;
                padding: 8px 14px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
        """)

    def _init_tray(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, 32, 32)
        gradient.setColorAt(0, QColor(139, 92, 246))
        gradient.setColorAt(1, QColor(167, 139, 250))
        p.setBrush(QBrush(gradient))
        p.drawRoundedRect(2, 2, 28, 28, 8, 8)
        p.setPen(Qt.GlobalColor.white)
        p.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        p.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M")
        p.end()
        
        self.tray = QSystemTrayIcon(QIcon(pixmap), self)
        self.tray.setToolTip("MIRA — AI Ассистент (Qwen 3)")
        
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background: {Theme.BG_ELEVATED};
                color: {Theme.TEXT_PRIMARY};
                border: 1.5px solid {Theme.BORDER};
                border-radius: 12px;
                padding: 8px;
            }}
            QMenu::item {{
                padding: 10px 28px;
                border-radius: 8px;
                margin: 2px 4px;
            }}
            QMenu::item:selected {{
                background: {Theme.ACCENT_GLOW};
            }}
        """)
        menu.addAction("🔍 Открыть MIRA", self._restore_window)
        menu.addSeparator()
        menu.addAction("📋 Процессы", lambda: (self._restore_window(), self._switch_page("processes")))
        menu.addAction("ℹ️ О программе", lambda: (self._restore_window(), self._switch_page("about")))
        menu.addAction("❌ Выход", self._full_exit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self._restore_window() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()

    def _restore_window(self):
        if self.isMinimized(): self.showNormal()
        elif not self.isVisible(): self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()

    def _full_exit(self):
        self.tray.hide()
        for thread in self.active_threads:
            if thread.isRunning(): thread.terminate()
        sys.exit(0)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
            self.maximize_btn.setToolTip("Развернуть")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")
            self.maximize_btn.setToolTip("Восстановить")

    def _switch_page(self, page: str):
        pages = {
            "chat": (self.chat_panel, "💬 Чат с МИРОЙ"),
            "scripts": (self.script_panel, "⚡ Сценарии"),
            "processes": (self.process_panel, "📋 Процессы"),
            "contacts": (self.contacts_panel, "👤 Контакты"),
            "settings": (self.settings_panel, "⚙ Настройки"),
            "about": (self.about_panel, "ℹ О Мире")
        }
        widget, title = pages.get(page, (self.chat_panel, "💬 Чат с МИРОЙ"))
        self.stacked.setCurrentWidget(widget)
        self.title_label.setText(f"✦ MIRA — {title}")
        
        if page == "processes":
            self.process_panel.update_processes()

    def _boot(self):
        if self.ai.ai_available:
            ai_status = f"✅ Qwen 3 подключён ({self.ai.model})"
        else:
            ai_status = "❌ Qwen 3 не подключён"
        
        self._add_bubble("ai", f"✨ Привет! Я МИРА.\n"
                               f"{ai_status}\n\n"
                               f"Я могу:\n"
                               f"• Отвечать на вопросы\n"
                               f"• Запускать и закрывать приложения\n"
                               f"• Выполнять сценарии\n"
                               f"• Искать в интернете\n"
                               f"• Работать с голосом\n\n"
                               f"Попробуй: «открой блокнот» или «закрой хром»")
        
        self.settings_panel.update_ui(
            self.ai.ai_available,
            self.voice.mic is not None,
            self.executor.resolver.steam_path
        )
        if self.ai.ai_available:
            self.sidebar.status_dot.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 14px;")
            self.sidebar.status_dot.setToolTip(f"Qwen 3 онлайн ({self.ai.model})")
        else:
            self.sidebar.status_dot.setStyleSheet(f"color: {Theme.ERROR}; font-size: 14px;")
            self.sidebar.status_dot.setToolTip("AI оффлайн")

    def _cleanup_thread(self, thread):
        if thread in self.active_threads:
            self.active_threads.remove(thread)
        thread.deleteLater()

    def _start_worker(self, worker):
        worker.finished.connect(lambda: self._cleanup_thread(worker))
        self.active_threads.append(worker)
        worker.start()

    def _resolve_command(self, text: str) -> Tuple[Optional[str], bool, Optional[str]]:
        clean = text.lower().strip(".,!?;:- \"'")
        
        close_patterns = [
            r'закрой\s+(.+)', r'выключи\s+(.+)', r'останови\s+(.+)',
            r'заверши\s+(.+)', r'убей\s+(.+)', r'close\s+(.+)'
        ]
        for pattern in close_patterns:
            match = re.match(pattern, clean)
            if match:
                app_name = match.group(1).strip()
                return f"CLOSE:{app_name}", False, True
        
        search_patterns = [
            r'найди в интернете\s+(.+)', r'погугли\s+(.+)', r'яндекси\s+(.+)',
            r'поиск в (яндекс|google|гугл)\s+(.+)'
        ]
        for pattern in search_patterns:
            match = re.match(pattern, clean)
            if match:
                query = match.group(1).strip()
                engine = "yandex"
                if "гугл" in clean or "google" in clean: engine = "google"
                elif "duck" in clean: engine = "duckduckgo"
                return f"SEARCH:{query}", True, False
        
        cmd = clean
        for verb in ["открой", "запусти", "включи", "покажи", "открыть", "запустить", "включить"]:
            if cmd.startswith(verb):
                cmd = cmd.replace(verb, "").strip()
                break
        
        if cmd in self.executor.resolver.aliases:
            return self.executor.resolver.aliases[cmd], False, False
        
        for alias, exe in self.executor.resolver.aliases.items():
            if alias in cmd or cmd in alias:
                return exe, False, False
        
        question_words = ["привет", "здравствуй", "как дела", "что ты умеешь", "кто ты",
                         "помоги", "спасибо", "пока", "до свидания", "расскажи", "объясни",
                         "почему", "как", "что", "где", "когда", "зачем"]
        if any(qw in cmd for qw in question_words):
            return None, False, False
        
        resolved = self.executor.resolver.resolve(cmd)
        if resolved and (shutil.which(resolved) or Path(resolved).exists() or resolved.startswith("steam://")):
            return resolved, False, False
        
        return None, False, False

    def _add_bubble(self, role: str, text: str):
        colors = {
            "user": "#818cf8", "ai": "#a78bfa", "sys": "#fbbf24",
            "success": "#10b981", "error": "#ef4444"
        }
        bg_map = {
            "user": "rgba(129, 140, 248, 0.1)", "ai": "rgba(167, 139, 250, 0.08)",
            "sys": "rgba(251, 191, 36, 0.08)", "success": "rgba(16, 185, 129, 0.1)",
            "error": "rgba(239, 68, 68, 0.1)"
        }
        bg = bg_map.get(role, "rgba(167, 139, 250, 0.08)")
        color = colors.get(role, "#a78bfa")
        
        html = f"""
        <div style='margin:12px 0;'>
            <div style='background:{bg}; padding:16px 20px; border-radius:18px; border: 1.5px solid rgba(139, 92, 246, 0.12);'>
                <span style='color:{color}; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:1.5px;'>{role}</span><br>
                <span style='color:#f1f5f9; font-size:15px; line-height:1.6;'>{text.replace('<','&lt;').replace('>','&gt;').replace(chr(10),'<br>')}</span>
            </div>
        </div>
        """
        self.chat_panel.chat.append(html)
        self.chat_panel.chat.verticalScrollBar().setValue(
            self.chat_panel.chat.verticalScrollBar().maximum()
        )

    def _process(self):
        txt = self.chat_panel.input.text().strip()
        if not txt: return
        self.chat_panel.input.clear()
        self._add_bubble("user", txt)
        QTimer.singleShot(10, lambda: self._route(txt))

    def _route(self, text: str):
        try:
            clean = text.lower().strip(".,!?;:- \"'")
            
            if re.match(r'создай\s+сценарий\s*[:\-]?\s*(.+)', clean):
                name = re.match(r'создай\s+сценарий\s*[:\-]?\s*(.+)', clean).group(1).strip("\"' ")
                QTimer.singleShot(10, lambda: self._create_script_dialog(name))
                return
            
            if re.match(r'запусти\s+сценарий\s*[:\-]?\s*(.+)', clean):
                nm = re.match(r'запусти\s+сценарий\s*[:\-]?\s*(.+)', clean).group(1).strip("\"' ")
                QTimer.singleShot(10, lambda: self._run_script(nm))
                return
            
            for cmd in self.cfg.get("commands", []):
                trig = cmd.get("trigger", "")
                if trig and trig in clean:
                    self._execute_cmd(cmd["action"], cmd.get("type", "app"))
                    return
            
            resolved, is_search, is_close = self._resolve_command(clean)
            
            if resolved:
                self.chat_panel.status_wave.set_active(True)
                if is_search:
                    self._add_bubble("sys", f"🔍 Поиск: {resolved.replace('SEARCH:','')}")
                elif is_close:
                    self._add_bubble("sys", f"🔒 Закрываю: {resolved.replace('CLOSE:','')}")
                else:
                    self._add_bubble("sys", f"🚀 Запуск: {resolved}")
                
                worker = CmdWorker(self.executor, resolved, "auto")
                worker.result.connect(self._on_cmd_result)
                self._start_worker(worker)
            else:
                self.chat_panel.status_wave.set_active(True)
                self._add_bubble("ai", "🤔 Думаю...")
                worker = AIWorker(self.ai, text)
                worker.result.connect(self._on_ai_result)
                self._start_worker(worker)
                
        except Exception as e:
            self._add_bubble("error", f"❌ Ошибка: {e}")

    def _on_cmd_result(self, result: str):
        self.chat_panel.status_wave.set_active(False)
        role = "success" if "✅" in result else "error"
        self._add_bubble(role, result)
        
        if "закрыт" in result.lower() or "закрыто" in result.lower():
            if hasattr(self, 'process_panel'):
                self.process_panel.update_processes()

    def _on_ai_result(self, result: str):
        self.chat_panel.status_wave.set_active(False)
        self._add_bubble("ai", result)

    def _execute_cmd(self, cmd: str, ctype: str):
        self.chat_panel.status_wave.set_active(True)
        worker = CmdWorker(self.executor, cmd, ctype)
        worker.result.connect(self._on_cmd_result)
        self._start_worker(worker)

    def _close_process(self, app_name: str):
        if not app_name.strip():
            return
        self._add_bubble("sys", f"🔒 Закрываю: {app_name}")
        self.chat_panel.status_wave.set_active(True)
        worker = CmdWorker(self.executor, f"CLOSE:{app_name}", "auto")
        worker.result.connect(self._on_cmd_result)
        self._start_worker(worker)
        self.process_panel.quick_input.clear()

    def _run_script(self, name: str):
        scripts = self.cfg.get("scripts", {})
        if name not in scripts:
            self._add_bubble("error", f"❌ Сценарий '{name}' не найден")
            return
        cmds = scripts[name]
        self._add_bubble("ai", f"⚡ Запускаю '{name}' ({len(cmds)} шагов)...")
        worker = ScriptWorker(self.executor, name, cmds)
        worker.progress.connect(lambda i, t, c: self._add_bubble("sys", f"⏳ {i}/{t}: {c}"))
        worker.finished.connect(lambda n: self._add_bubble("success", f"✅ Сценарий '{n}' выполнен"))
        self._start_worker(worker)

    def _create_script_dialog(self, pre_name: str = ""):
        dlg = QDialog(self)
        dlg.setWindowTitle("✨ Новый сценарий")
        dlg.resize(540, 460)
        dlg.setStyleSheet(f"""
            QDialog {{
                background: {Theme.BG_MAIN};
                color: {Theme.TEXT_PRIMARY};
                border: 1.5px solid {Theme.BORDER};
                border-radius: 20px;
            }}
            QLabel {{
                color: {Theme.ACCENT_LIGHT};
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            }}
            QLineEdit, QPlainTextEdit {{
                background: {Theme.BG_SURFACE};
                border: 2px solid {Theme.BORDER};
                border-radius: 12px;
                padding: 12px;
                color: {Theme.TEXT_PRIMARY};
                font-family: Consolas;
                font-size: 14px;
            }}
            QLineEdit:focus, QPlainTextEdit:focus {{
                border-color: {Theme.BORDER_FOCUS};
                background: {Theme.BG_ELEVATED};
            }}
        """)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        
        layout.addWidget(QLabel("📝 Название сценария:"))
        name_input = QLineEdit(pre_name)
        name_input.setPlaceholderText("Например: Запуск стрима")
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("📋 Команды (по одной на строку):"))
        cmd_input = QPlainTextEdit()
        cmd_input.setPlaceholderText("obs64.exe\nnotepad.exe\nsteam://run/730")
        layout.addWidget(cmd_input)
        
        btns = QHBoxLayout()
        save = StyledButton("Сохранить", accent=True, icon_text="💾")
        save.clicked.connect(dlg.accept)
        cancel = StyledButton("Отмена")
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        
        if dlg.exec() == 1:
            nm = name_input.text().strip()
            cmds = [l.strip() for l in cmd_input.toPlainText().split('\n') if l.strip()]
            if not nm: return
            self.cfg.setdefault("scripts", {})[nm] = cmds
            save_config(self.cfg)
            self._add_bubble("success", f"✅ Сценарий '{nm}' сохранён ({len(cmds)} шагов)")
            self.script_panel.refresh_scripts()

    def _on_voice(self, txt: str):
        if not txt:
            self.chat_panel.voice_btn.set_listening(False)
            return
        self._add_bubble("user", f"🎤 {txt}")
        QTimer.singleShot(10, lambda: self._route(txt))
        self.chat_panel.voice_btn.set_listening(False)

    def _toggle_voice(self):
        if not self.voice.mic:
            self._add_bubble("error", "❌ Микрофон не найден")
            return
        self.chat_panel.voice_btn.set_listening(True)
        self._add_bubble("sys", "🎤 Слушаю вас...")
        
        def listen():
            try:
                with self.voice.mic as source:
                    self.voice.rec.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.voice.rec.listen(source, timeout=6, phrase_time_limit=10)
                    txt = self.voice.recognize(audio)
                    if txt: self.voice_signal.emit(txt)
                    else: self.voice_signal.emit("")
            except:
                self.voice_signal.emit("")
        threading.Thread(target=listen, daemon=True).start()

    def closeEvent(self, event):
        self.hide()
        self.tray.showMessage(
            "MIRA",
            "Ассистент свёрнут в трей. Дважды кликните для открытия.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
        event.ignore()

# === ЗАПУСК ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(12, 12, 29))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(241, 245, 249))
    app.setPalette(palette)
    
    win = MIRAWindow()
    win.show()
    sys.exit(app.exec())
