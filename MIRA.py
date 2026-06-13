#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIRA (MIRA) v13.0 "AURORA"
AI Assistant with OpenRouter Cloud + Ollama Local
New Aurora design system, stable UI, no animation bugs.
(c) CayPlay 2026
"""

# === 1. IMPORTS ===
import os, sys, json, logging, subprocess, threading, time
import urllib.request, urllib.parse, urllib.error, webbrowser
import shutil, psutil, platform, re, winreg, math, difflib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

import pyttsx3
import speech_recognition as sr
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame,
    QSystemTrayIcon, QMenu, QDialog, QPlainTextEdit, QScrollArea,
    QStackedWidget, QMessageBox, QToolButton, QProgressBar,
    QListWidget, QListWidgetItem, QComboBox
)
from PyQt6.QtGui import (
    QAction, QFont, QIcon, QColor, QPainter, QPixmap, QClipboard,
    QRadialGradient, QPen, QBrush, QDesktopServices
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QUrl, QSize,
    QPropertyAnimation, QEasingCurve, QAbstractAnimation, pyqtProperty
)

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mira.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("MIRA")


def _excepthook(etype, value, tb):
    import traceback
    logger.error("".join(traceback.format_exception(etype, value, tb)))


sys.excepthook = _excepthook

# === 2. CONFIG ===
CONFIG_PATH = Path("mira_config.json")

DEFAULT_CONFIG = {
    "openrouter": {
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-2.0-flash-001",
        "max_tokens": 2048,
        "temperature": 0.7
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "qwen3:1.7b"
    },
    "ai_provider": "openrouter",
    "commands": [
        {"trigger": "выключи компьютер", "action": "shutdown /s /t 30", "type": "system"},
        {"trigger": "перезагрузи компьютер", "action": "shutdown /r /t 30", "type": "system"},
        {"trigger": "заблокируй компьютер", "action": "rundll32.exe user32.dll,LockWorkStation", "type": "system"},
        {"trigger": "спящий режим", "action": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0", "type": "system"},
        {"trigger": "отмени выключение", "action": "shutdown /a", "type": "system"},
        {"trigger": "очисти корзину", "action": "powershell -Command Clear-RecycleBin -Force", "type": "system"},
        {"trigger": "диспетчер задач", "action": "taskmgr.exe", "type": "app"},
        {"trigger": "настройки системы", "action": "ms-settings:", "type": "app"},
        {"trigger": "панель управления", "action": "control.exe", "type": "app"},
    ],
    "scripts": {},
    "aliases": {
        # === Apps (Cyrillic) ===
        "калькулятор": "calc.exe", "блокнот": "notepad.exe",
        "проводник": "explorer.exe", "диспетчер задач": "taskmgr.exe",
        "реестр": "regedit.exe", "командная строка": "cmd.exe",
        "терминал": "wt.exe", "powershell": "powershell.exe",
        "браузер": "msedge.exe", "хром": "chrome.exe",
        "стим": "steam.exe", "обс": "obs64.exe",
        "дискорд": "discord.exe", "телеграм": "Telegram.exe",
        "вк": "VK.exe", "вконтакте": "https://vk.com",
        "визуал студио": "devenv.exe", "пайчарм": "pycharm64.exe",
        "геометри дэш": "GeometryDash.exe",
        "майнкрафт": "minecraft.exe",
        "ютуб": "https://youtube.com", "гитхаб": "https://github.com",
        "почта": "https://mail.google.com", "яндекс": "https://yandex.ru",
        "гугл": "https://google.com",
        # === Apps (Latin - same names) ===
        "steam": "steam.exe", "calc": "calc.exe", "calculator": "calc.exe",
        "notepad": "notepad.exe", "explorer": "explorer.exe",
        "task manager": "taskmgr.exe", "taskmgr": "taskmgr.exe",
        "regedit": "regedit.exe", "registry": "regedit.exe",
        "cmd": "cmd.exe", "command prompt": "cmd.exe",
        "terminal": "wt.exe", "wt": "wt.exe",
        "powershell": "powershell.exe",
        "browser": "msedge.exe", "edge": "msedge.exe",
        "chrome": "chrome.exe", "google chrome": "chrome.exe",
        "firefox": "firefox.exe", "opera": "opera.exe",
        "obs": "obs64.exe", "obs studio": "obs64.exe",
        "discord": "discord.exe", "telegram": "Telegram.exe",
        "vk": "VK.exe", "vscode": "code.exe", "vs code": "code.exe",
        "visual studio": "devenv.exe",
        "pycharm": "pycharm64.exe", "intellij": "idea64.exe",
        "minecraft": "minecraft.exe", "mc": "minecraft.exe",
        "geometry dash": "GeometryDash.exe", "gd": "GeometryDash.exe",
        "epic": "EpicGamesLauncher.exe", "epic games": "EpicGamesLauncher.exe",
        "gog": "GOGGalaxy.exe", "origin": "Origin.exe",
        "ubisoft": "UbisoftConnect.exe", "battle.net": "Agent.exe",
        "spotify": "Spotify.exe", "photoshop": "Photoshop.exe",
        "word": "WINWORD.EXE", "excel": "EXCEL.EXE",
        "powerpoint": "POWERPNT.EXE", "outlook": "OUTLOOK.EXE",
        # === URLs ===
        "youtube": "https://youtube.com", "github": "https://github.com",
        "google": "https://google.com", "yandex": "https://yandex.ru",
        "mail": "https://mail.google.com", "gmail": "https://mail.google.com",
        "drive": "https://drive.google.com", "docs": "https://docs.google.com",
        "maps": "https://maps.google.com", "translate": "https://translate.google.com",
        "reddit": "https://reddit.com", "twitter": "https://twitter.com",
        "x": "https://x.com", "tiktok": "https://tiktok.com",
        "twitch": "https://twitch.tv", "discord web": "https://discord.com/app",
        "spotify web": "https://open.spotify.com",
    },
    "search_engines": {
        "google": "https://www.google.com/search?q=",
        "yandex": "https://yandex.ru/search/?text=",
        "duckduckgo": "https://duckduckgo.com/?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
    },
    "default_search": "yandex",
    "unrestricted": {
        "search_paths": [
            "C:\\Program Files\\", "C:\\Program Files (x86)\\",
            "C:\\Users\\{}\\AppData\\Local\\Programs\\",
            "C:\\Users\\{}\\AppData\\Roaming\\",
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
    "contacts": {"telegram": "@CayPlay78", "vk": "https://m.vk.com/cayplay"},
    "notes": [],
}


def load_config() -> Dict:
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # Merge new defaults
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
            elif isinstance(v, dict) and isinstance(cfg[k], dict):
                for sk, sv in v.items():
                    if sk not in cfg[k]:
                        cfg[k][sk] = sv
        # Force update aliases with latest version
        cfg["aliases"] = DEFAULT_CONFIG["aliases"]
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return cfg
    except Exception as e:
        logger.error(f"Config: {e}")
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Save config: {e}")

# === 3. THEME ===


class Theme:
    ACCENT = "#6366f1"
    ACCENT_LIGHT = "#818cf8"
    ACCENT_DARK = "#4f46e5"
    BG = "#0a0a18"
    SURFACE = "#12122a"
    CARD = "#1a1a35"
    CARD_HOVER = "#22224a"
    INPUT = "#14142c"
    BORDER = "#2a2a50"
    BORDER_FOCUS = "#6366f1"
    TEXT = "#e8e8f0"
    TEXT_DIM = "#9494b8"
    TEXT_MUTED = "#5a5a7a"
    SUCCESS = "#22c55e"
    ERROR = "#ef4444"
    WARNING = "#f59e0b"
    INFO = "#3b82f6"

# === 4. UI COMPONENTS ===


class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self.setStyleSheet(f"""
            QFrame#glassCard {{
                background: {Theme.CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: 14px;
            }}
        """)

    def setHoverMode(self, enabled=True):
        if enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        if self.cursor().shape() == Qt.CursorShape.PointingHandCursor:
            self.setStyleSheet(f"""
                QFrame#glassCard {{
                    background: {Theme.CARD_HOVER};
                    border: 1px solid {Theme.ACCENT}50;
                    border-radius: 14px;
                }}
            """)

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame#glassCard {{
                background: {Theme.CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: 14px;
            }}
        """)


class GlowButton(QPushButton):
    def __init__(self, text="", parent=None, accent=False):
        super().__init__(text, parent)
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        base = "QPushButton{border:none;border-radius:10px;padding:10px 18px;font-family:'Segoe UI';font-size:13px;font-weight:500;}"
        if self.accent:
            self.setStyleSheet(base + f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {Theme.ACCENT_DARK},stop:1 {Theme.ACCENT});color:white;}}QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {Theme.ACCENT},stop:1 {Theme.ACCENT_LIGHT});}}QPushButton:pressed{{background:{Theme.ACCENT_DARK};padding-top:11px;padding-bottom:9px;}}")
        else:
            self.setStyleSheet(base + f"QPushButton{{background:{Theme.CARD_HOVER};color:{Theme.TEXT};}}QPushButton:hover{{background:#2a2a4e;}}QPushButton:pressed{{background:{Theme.CARD};}}")


class FluentInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {Theme.INPUT};
                border: 2px solid {Theme.BORDER};
                border-radius: 12px;
                padding: 12px 16px;
                color: {Theme.TEXT};
                font-family: 'Segoe UI';
                font-size: 15px;
                selection-background-color: {Theme.ACCENT};
            }}
            QLineEdit:focus {{ border-color: {Theme.BORDER_FOCUS}; background: {Theme.CARD}; }}
        """)


class PulseIndicator(QWidget):
    def __init__(self, size=14, color=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(size * 3, size)
        self._phase = 0
        self._color = QColor(color or Theme.SUCCESS)
        self._active = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(80)

    def set_active(self, active):
        self._active = active
        self.update()

    def _tick(self):
        if self._active:
            self._phase = (self._phase + 0.25) % (2 * math.pi)
            self.update()

    def paintEvent(self, event):
        if not self._active:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        for i in range(3):
            x = w // 2 - 21 + i * 14
            amp = math.sin(self._phase + i) * 0.5 + 0.5
            r = int(amp * 6) + 3
            c = QColor(self._color)
            c.setAlpha(int(150 + amp * 100))
            painter.setBrush(c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x, h // 2 - r // 2, r, r)

# === 5. NLP ===


SYNONYMS = {
    "open": ["открой", "запусти", "включи", "покажи", "открыть", "запустить", "включить"],
    "search": ["найди", "поищи", "погугли", "яндекси", "загугли"],
    "greet": ["привет", "здравствуй", "добрый день", "хай", "хей"],
    "bye": ["пока", "до свидания", "прощай"],
    "thanks": ["спасибо", "благодарю"],
}

STOP_WORDS = {
    "пожалуйста", "будь", "добр", "мне", "тебе", "очень", "просто",
    "сейчас", "только", "именно", "же", "то", "ли", "а", "и", "но",
}

INTENT_PATTERNS = {
    "search_web": [
        r"(найди|поищи|погугли|яндекси|загугли)\s+(.+)",
        r"что\s+такое\s+(.+)",
        r"кто\s+такой\s+(.+)",
    ],
    "create_script": [r"создай\s+сценарий\s*[:\-]?\s*(.+)"],
    "run_script": [r"запусти\s+сценарий\s*[:\-]?\s*(.+)"],
    "list_scripts": [r"(покажи|список)\s+сценари"],
    "calc": [r"сколько\s+будет\s+(.+)", r"посчитай\s+(.+)", r"вычисли\s+(.+)"],
    "time_query": [r"(сколько\s+времени|который\s+час|время)"],
    "date_query": [r"(какое\s+сегодня|дата|число)"],
    "note_save": [r"(запомни|запиши|сохрани\s+заметку)\s+(.+)"],
    "note_list": [r"(покажи\s+заметки|список\s+заметок|мои\s+заметки)"],
}


class IntentClassifier:
    def __init__(self, config):
        self.commands = config.get("commands", [])
        self.aliases = {k.lower(): v for k, v in config.get("aliases", {}).items()}
        # Build reverse alias map: exe_name -> alias_key for fast lookup
        self._exe_to_alias = {}
        for k, v in self.aliases.items():
            exe = v.lower().replace(".exe", "").replace(".bat", "").replace(".cmd", "")
            self._exe_to_alias[exe] = k

    def _normalize(self, text):
        return " ".join(w for w in text.lower().strip(".,!?;:- \"'").split() if w not in STOP_WORDS)

    def _fuzzy(self, target, candidates, threshold=0.7):
        best, best_r = None, 0.0
        target_l = target.lower()
        for c in candidates:
            c_l = c.lower()
            # Exact match
            if target_l == c_l:
                return c
            # Substring match
            if target_l in c_l or c_l in target_l:
                ratio = 0.9
                if ratio > best_r:
                    best, best_r = c, ratio
                continue
            r = difflib.SequenceMatcher(None, target_l, c_l).ratio()
            if r > best_r and r >= threshold:
                best, best_r = c, r
        return best

    def _extract_target(self, text):
        """Extract app name from text after removing verbs and prepositions."""
        # Remove verbs
        for verb in SYNONYMS["open"] + SYNONYMS["search"]:
            text = re.sub(rf"\b{verb}\b", "", text, flags=re.IGNORECASE)
        # Remove prepositions
        text = re.sub(r"\b(в|на|из|по|для|с|к|о|у)\b", "", text, flags=re.IGNORECASE)
        # Remove browser/internet filler phrases
        text = re.sub(r"\b(в\s+браузере|в\s+интернете|онлайн|в\s+гугле|в\s+яндексе|в\s+поиске)\b", "", text, flags=re.IGNORECASE)
        return " ".join(text.split()).strip()

    def classify(self, text):
        original = text.lower().strip()
        clean = self._normalize(text)

        # 1. Patterns (scripts, calc, time, etc.)
        for intent, patterns in INTENT_PATTERNS.items():
            for pat in patterns:
                m = re.search(pat, original)
                if m:
                    return intent, {"match": m.group(1).strip() if m.groups() else "", "full": original}

        # 2. System commands
        for cmd in self.commands:
            if cmd.get("trigger", "") and cmd["trigger"] in original:
                return "system_cmd", {"action": cmd["action"], "type": cmd.get("type", "app"), "trigger": cmd["trigger"]}

        # 3. Search
        for verb in SYNONYMS["search"]:
            if original.startswith(verb + " ") or f" {verb} " in original:
                q = self._extract_target(original)
                if q:
                    eng = "google" if ("гугл" in original or "google" in original) else "yandex"
                    return "search_web", {"query": q, "engine": eng}

        # 4. URL
        url_m = re.search(r"(https?://\S+)", original)
        if url_m:
            return "open_url", {"url": url_m.group(1)}

        # 5. Open app - check all verbs (start of sentence OR anywhere)
        for verb in SYNONYMS["open"]:
            # Check if verb is present
            if verb in original:
                target = self._extract_target(original)
                if target:
                    # Direct alias match (exact, case-insensitive)
                    if target in self.aliases:
                        return "open_app", {"target": self.aliases[target], "display": target}
                    # Try with .exe
                    if target + ".exe" in [v.lower() for v in self.aliases.values()]:
                        for k, v in self.aliases.items():
                            if v.lower() == target + ".exe":
                                return "open_app", {"target": v, "display": k}
                    # Fuzzy match
                    m = self._fuzzy(target, list(self.aliases.keys()))
                    if m:
                        return "open_app", {"target": self.aliases[m], "display": m}
                    # If no match, try the target directly
                    return "open_app", {"target": target, "display": target}

        # 6. Also check if any alias key appears directly in text (without verb)
        for alias, exe in self.aliases.items():
            if alias in original and len(alias) >= 3:
                return "open_app", {"target": exe, "display": alias}

        # 7. Time/Date
        if any(w in original for w in ["время", "час", "который час"]):
            return "time_query", {}
        if any(w in original for w in ["дата", "число", "день", "какое сегодня"]):
            return "date_query", {}

        # 8. Notes
        for verb in ["запомни", "запиши"]:
            if original.startswith(verb + " "):
                return "note_save", {"text": original.replace(verb, "", 1).strip()}

        # 9. Calculator
        if re.search(r"\d+\s*[+\-*/]\s*\d+", original) or "посчитай" in original or "сколько будет" in original:
            expr = re.findall(r"[\d+\-*/().\s]+", original)
            return "calc", {"expr": expr[0].strip() if expr else ""}

        # 10. Chat phrases
        if any(w in original for w in SYNONYMS["greet"]):
            return "chat", {"response": "Привет! Чем могу помочь?"}
        if any(w in original for w in SYNONYMS["bye"]):
            return "chat", {"response": "До свидания! Возвращайтесь."}
        if any(w in original for w in SYNONYMS["thanks"]):
            return "chat", {"response": "Пожалуйста! Рада помочь."}
        if "как дела" in original:
            return "chat", {"response": "Отлично! Готова помочь."}
        if "что ты умеешь" in original:
            return "chat", {"response": "Я умею:\n- Запускать приложения и игры\n- Искать в интернете\n- Отвечать на вопросы (AI)\n- Сценарии и заметки\n- Калькулятор и многое другое"}

        # 11. Default: AI chat
        return "chat", {"prompt": text}

# === 6. BACKEND ===


class OmniResolver:
    def __init__(self, config):
        self.aliases = {k.lower(): v for k, v in config.get("aliases", DEFAULT_CONFIG["aliases"]).items()}
        self.paths = config.get("unrestricted", {}).get("search_paths", [])
        self.game_paths = config.get("unrestricted", {}).get("game_launchers", [])
        self.user = os.getlogin() if hasattr(os, "getlogin") else "User"
        self.steam_path = self._find_steam()
        self._steam_cache = {}
        self._steam_ready = False
        self._reg_cache = {}
        self._reg_ready = False
        self._lnk_cache = {}
        self._lnk_ready = False
        self._cache = {}
        threading.Thread(target=self._bg_init, daemon=True).start()

    def _bg_init(self):
        try:
            self._scan_steam()
            self._steam_ready = True
        except Exception as e:
            logger.error(f"Steam: {e}")
        try:
            self._scan_registry()
            self._reg_ready = True
        except Exception as e:
            logger.error(f"Registry: {e}")
        try:
            self._scan_start_menu()
            self._lnk_ready = True
        except Exception as e:
            logger.error(f"StartMenu: {e}")
        logger.info(f"Resolver ready: {len(self._steam_cache)} steam, {len(self._reg_cache)} reg, {len(self._lnk_cache)} lnk")

    def _fuzzy(self, target, candidates, threshold=0.7):
        best, best_r = None, 0.0
        for c in candidates:
            r = difflib.SequenceMatcher(None, target.lower(), c.lower()).ratio()
            if r > best_r and r >= threshold:
                best, best_r = c, r
        return best

    def _resolve_exe(self, exe_name):
        """Resolve exe name to full path. Returns full path or original name."""
        # Already a full path
        if os.path.isabs(exe_name) and os.path.exists(exe_name):
            return exe_name
        # Try shutil.which (searches PATH)
        found = shutil.which(exe_name)
        if found:
            return found
        # Try with .exe extension
        if not exe_name.lower().endswith(".exe"):
            found = shutil.which(exe_name + ".exe")
            if found:
                return found
        # Check steam cache
        if self._steam_ready:
            for k, v in self._steam_cache.items():
                if k == exe_name.lower() or k == exe_name.lower().replace(".exe", ""):
                    if os.path.exists(v):
                        return v
        # Fallback: check Steam path directly if cache not ready yet
        elif self.steam_path:
            exe_lower = exe_name.lower().replace(".exe", "")
            if exe_lower in ("steam", "стим"):
                steam_exe = os.path.join(self.steam_path, "steam.exe")
                if os.path.exists(steam_exe):
                    return steam_exe
        # Check registry cache
        if self._reg_ready:
            for k, v in self._reg_cache.items():
                if exe_name.lower().replace(".exe", "") in k:
                    if os.path.exists(v):
                        return v
        # Return as-is (will try subprocess.Popen later)
        return exe_name

    def _find_steam(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                return winreg.QueryValueEx(k, "SteamPath")[0]
        except Exception:
            pass
        for p in ["C:\\Program Files (x86)\\Steam", "D:\\Games\\Steam"]:
            if os.path.exists(os.path.join(p, "steam.exe")):
                return p
        return None

    def _scan_steam(self):
        if not self.steam_path:
            return
        # First, find steam.exe itself
        steam_exe = os.path.join(self.steam_path, "steam.exe")
        if os.path.exists(steam_exe):
            self._steam_cache["steam"] = steam_exe
            self._steam_cache["steam.exe"] = steam_exe
            self._steam_cache["стим"] = steam_exe
        # Also check steamservice.exe for other scenarios
        vdf = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        libs = [os.path.join(self.steam_path, "steamapps", "common")]
        if os.path.exists(vdf):
            try:
                with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if '"path"' in line:
                            m = re.search(r'"path"\s*"([^"]+)"', line)
                            if m:
                                p = m.group(1).replace("\\\\", "\\")
                                c = os.path.join(p, "steamapps", "common")
                                if os.path.isdir(c):
                                    libs.append(c)
            except Exception:
                pass
        # Skip list - helper executables that shouldn't be launched
        skip_exe = {"uninstall", "setup", "install", "redist", "unins",
                     "steamwebhelper", "steamservice", "crashhandler",
                     "streaming_client", "gameoverlayrenderer"}
        for lib in libs:
            if not os.path.isdir(lib):
                continue
            try:
                for folder in os.listdir(lib):
                    fp = os.path.join(lib, folder)
                    if not os.path.isdir(fp):
                        continue
                    # Find the main game exe
                    best_exe = None
                    for e in os.listdir(fp):
                        el = e.lower()
                        if not el.endswith(".exe"):
                            continue
                        name = el.replace(".exe", "")
                        if any(name.startswith(s) for s in skip_exe):
                            continue
                        # Prefer the exe that matches the folder name
                        if name == folder.lower():
                            best_exe = os.path.join(fp, e)
                            break
                        if not best_exe:
                            best_exe = os.path.join(fp, e)
                    if best_exe:
                        self._steam_cache[folder.lower()] = best_exe
                        exe_name = os.path.basename(best_exe).lower().replace(".exe", "")
                        if exe_name not in skip_exe:
                            self._steam_cache[exe_name] = best_exe
            except Exception:
                pass

    def _scan_registry(self):
        for kp in [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, kp) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sk = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sk) as sub:
                                try:
                                    name = winreg.QueryValueEx(sub, "DisplayName")[0].lower()
                                    if name in self._reg_cache:
                                        continue
                                    for vn in ["InstallLocation", "DisplayIcon"]:
                                        try:
                                            val = winreg.QueryValueEx(sub, vn)[0]
                                            if val and isinstance(val, str):
                                                exe = val.replace('"', '').split(",")[0].strip()
                                                if exe.lower().endswith(".exe") and os.path.exists(exe):
                                                    self._reg_cache[name] = exe
                                                    break
                                                elif os.path.isdir(exe):
                                                    try:
                                                        for e in os.listdir(exe)[:30]:
                                                            if e.lower().endswith(".exe"):
                                                                self._reg_cache[name] = os.path.join(exe, e)
                                                                break
                                                    except Exception:
                                                        pass
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                        except Exception:
                            pass
            except Exception:
                pass

    def _scan_start_menu(self):
        for sp in [
            os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs"),
        ]:
            if not os.path.isdir(sp):
                continue
            try:
                for entry in os.listdir(sp):
                    full = os.path.join(sp, entry)
                    if entry.lower().endswith(".lnk"):
                        self._lnk_cache[entry.lower().replace(".lnk", "")] = full
                    elif os.path.isdir(full):
                        try:
                            for sub in os.listdir(full):
                                if sub.lower().endswith(".lnk"):
                                    k = (entry + " " + sub).lower().replace(".lnk", "")
                                    self._lnk_cache[k] = os.path.join(full, sub)
                        except Exception:
                            pass
            except Exception:
                pass

    def _resolve_lnk(self, path):
        try:
            import pythoncom
            from win32com.shell import shell
            pythoncom.CoInitialize()
            return shell.CreateShellLink(path).GetPath(0)[0]
        except Exception:
            return None

    def resolve(self, raw_cmd):
        if not raw_cmd:
            return None
        cmd = raw_cmd.lower().strip(".,!?;:- \"'")
        if not cmd:
            return None
        if cmd in self._cache:
            return self._cache[cmd]
        # 1. Aliases (direct match)
        if cmd in self.aliases:
            r = self._resolve_exe(self.aliases[cmd])
            self._cache[cmd] = r
            return r
        words = set(re.findall(r"\w+", cmd))
        for alias, exe in self.aliases.items():
            if alias in words or alias == cmd:
                r = self._resolve_exe(exe)
                self._cache[cmd] = r
                return r
        clean = re.sub(r"\b(найди|открой|запусти|включи|покажи|поищи)\b", "", cmd).strip()
        if 0 < len(clean.split()) <= 3:
            m = self._fuzzy(clean, list(self.aliases.keys()))
            if m:
                r = self._resolve_exe(self.aliases[m])
                self._cache[cmd] = r
                return r
        # 2. Steam
        if self._steam_ready:
            for gn, ep in self._steam_cache.items():
                if gn in cmd or cmd in gn:
                    if os.path.exists(ep):
                        self._cache[cmd] = ep
                        return ep
        # 3. Direct
        if shutil.which(cmd):
            r = shutil.which(cmd)
            self._cache[cmd] = r
            return r
        if shutil.which(cmd + ".exe"):
            r = shutil.which(cmd + ".exe")
            self._cache[cmd] = r
            return r
        # 4. Registry
        if self._reg_ready:
            if cmd in self._reg_cache and os.path.exists(self._reg_cache[cmd]):
                self._cache[cmd] = self._reg_cache[cmd]
                return self._reg_cache[cmd]
            m = self._fuzzy(cmd, list(self._reg_cache.keys()), 0.7)
            if m and os.path.exists(self._reg_cache[m]):
                self._cache[cmd] = self._reg_cache[m]
                return self._reg_cache[m]
        # 5. Start Menu
        if self._lnk_ready:
            if cmd in self._lnk_cache:
                t = self._resolve_lnk(self._lnk_cache[cmd])
                if t:
                    self._cache[cmd] = t
                    return t
            m = self._fuzzy(cmd, list(self._lnk_cache.keys()), 0.7)
            if m:
                t = self._resolve_lnk(self._lnk_cache[m])
                if t:
                    self._cache[cmd] = t
                    return t
        return cmd


class SystemExecutor:
    def __init__(self, config):
        self.resolver = OmniResolver(config)
        self.search_engines = config.get("search_engines", DEFAULT_CONFIG["search_engines"])
        self.default_search = config.get("default_search", "yandex")

    def search_web(self, query, engine=None):
        engine = engine or self.default_search
        url = self.search_engines.get(engine, self.search_engines["yandex"]) + urllib.parse.quote(query)
        try:
            webbrowser.open(url)
            return f"В {engine.capitalize()}: {query}"
        except Exception as e:
            return f"Ошибка поиска: {e}"

    def open_url(self, url):
        if not url.startswith("http"):
            url = "https://" + url
        try:
            webbrowser.open(url)
            return f"Открываю: {url}"
        except Exception as e:
            return f"Ошибка: {e}"

    def execute(self, command, ctype="auto"):
        try:
            if command.startswith("SEARCH:"):
                return self.search_web(command.replace("SEARCH:", "").strip())
            if command.startswith("URL:"):
                return self.open_url(command.replace("URL:", "").strip())
            if command.startswith("steam://"):
                os.startfile(command)
                return f"Steam: {command}"
            if ctype == "auto":
                cl = command.lower()
                if cl.startswith(("shutdown", "restart", "lock", "rundll32", "powershell")):
                    ctype = "system"
                elif Path(command).exists() or command.startswith("ms-"):
                    ctype = "file"
                else:
                    ctype = "app"
            if ctype == "system":
                r = subprocess.run(command, shell=True, capture_output=True, text=True,
                                   timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
                return r.stdout.strip() or r.stderr.strip() or "Готово"
            elif ctype == "file":
                if platform.system() == "Windows":
                    os.startfile(command)
                return f"Открыто: {Path(command).name}"
            else:
                # "app" type - try to launch
                resolved = self.resolver.resolve(command)
                # If resolved is a local file that exists - launch it
                if resolved and os.path.isabs(resolved) and os.path.exists(resolved):
                    subprocess.Popen(f'"{resolved}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return f"Запущено: {Path(resolved).name}"
                # If resolved is a URL (http/https) - open in browser
                if resolved and resolved.startswith(("http://", "https://")):
                    return self.open_url(resolved)
                # If resolved looks like a .exe/.bat/.cmd - try to launch directly
                if resolved and resolved.lower().endswith((".exe", ".bat", ".cmd")):
                    try:
                        subprocess.Popen(f'"{resolved}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        return f"Запущено: {resolved}"
                    except Exception:
                        pass
                return f"Не найдено: {command}"
        except Exception as e:
            return f"Ошибка: {e}"


class AIManager:
    def __init__(self, config):
        self.or_cfg = config.get("openrouter", DEFAULT_CONFIG["openrouter"])
        self.oll_cfg = config.get("ollama", DEFAULT_CONFIG["ollama"])
        self.provider = config.get("ai_provider", "openrouter")
        self.api_key = self.or_cfg.get("api_key", "")
        self.or_model = self.or_cfg.get("model", "google/gemini-2.0-flash-001")
        self.oll_model = self.oll_cfg.get("model", "qwen3:1.7b")
        self.oll_url = self.oll_cfg.get("base_url", "http://localhost:11434")
        self.max_tokens = self.or_cfg.get("max_tokens", 2048)
        self.temperature = self.or_cfg.get("temperature", 0.7)
        self.history = [{"role": "system", "content": "Ты МИРА - дружелюбный ИИ-ассистент. Отвечай кратко, по-делу, на русском. Используй эмодзи умеренно."}]
        self.or_available = bool(self.api_key)
        self.oll_available = False
        self._checked_ollama = False
        self._lock = threading.Lock()

    def check_ollama_async(self):
        def _check():
            if self._checked_ollama:
                return
            self._checked_ollama = True
            try:
                req = urllib.request.Request(f"{self.oll_url}/api/tags")
                with urllib.request.urlopen(req, timeout=2) as r:
                    self.oll_available = r.status == 200
            except Exception:
                self.oll_available = False
        threading.Thread(target=_check, daemon=True).start()

    def ask(self, prompt):
        self.history.append({"role": "user", "content": prompt})
        if len(self.history) > 11:
            self.history = [self.history[0]] + self.history[-9:]
        if self.provider == "openrouter" and self.or_available:
            return self._ask_openrouter()
        elif self.provider == "ollama" and self.oll_available:
            return self._ask_ollama()
        elif self.or_available:
            return self._ask_openrouter()
        elif self.oll_available:
            return self._ask_ollama()
        else:
            self.check_ollama_async()
            return "AI недоступна. Настройте OpenRouter API в настройках или запустите Ollama."

    def _ask_openrouter(self):
        try:
            payload = json.dumps({
                "model": self.or_model,
                "messages": self.history,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }).encode()
            req = urllib.request.Request(
                self.or_cfg["base_url"],
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Title": "MIRA Assistant",
                }
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
                ans = data["choices"][0]["message"]["content"]
                self.history.append({"role": "assistant", "content": ans})
                return ans.strip()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return "Неверный API-ключ OpenRouter. Проверьте ключ в настройках."
            elif e.code == 429:
                return "Превышен лимит запросов OpenRouter. Подождите немного."
            elif e.code >= 500:
                return f"Ошибка сервера OpenRouter ({e.code}). Попробуйте позже."
            return f"Ошибка OpenRouter ({e.code}): {e.reason}"
        except Exception as e:
            return f"Ошибка подключения к OpenRouter: {e}"

    def _ask_ollama(self):
        try:
            payload = json.dumps({
                "model": self.oll_model,
                "messages": self.history,
                "stream": False,
            }).encode()
            req = urllib.request.Request(
                f"{self.oll_url}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                ans = json.loads(r.read())["message"]["content"]
                self.history.append({"role": "assistant", "content": ans})
                return ans.strip()
        except Exception as e:
            return f"Ollama Error: {e}"

    def clear(self):
        self.history = [self.history[0]]

    @property
    def available(self):
        if self.provider == "openrouter":
            return self.or_available
        return self.oll_available

    def set_provider(self, provider):
        self.provider = provider

    def set_api_key(self, key):
        self.api_key = key
        self.or_available = bool(key)

    def set_or_model(self, model):
        self.or_model = model

    def set_oll_model(self, model):
        self.oll_model = model


class VoiceManager:
    def __init__(self, config):
        vc = config.get("voice", DEFAULT_CONFIG["voice"])
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 300
        self.rec.dynamic_energy_threshold = True
        self.mic = None
        self.engine = None
        self._lock = threading.Lock()
        try:
            self.mic = sr.Microphone()
            with self.mic as s:
                self.rec.adjust_for_ambient_noise(s, duration=0.5)
        except Exception:
            pass
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", vc.get("speed", 160))
            for voice in self.engine.getProperty("voices"):
                if "ru" in voice.id.lower():
                    self.engine.setProperty("voice", voice.id)
                    break
        except Exception:
            pass

    def recognize(self, audio):
        try:
            return self.rec.recognize_google(audio, language="ru-RU").strip()
        except Exception:
            return None

    def speak(self, text):
        if not self.engine or not text:
            return
        def _t():
            with self._lock:
                try:
                    self.engine.say(text[:200])
                    self.engine.runAndWait()
                except Exception:
                    pass
        threading.Thread(target=_t, daemon=True).start()

# === 7. THREADS ===


class AIWorker(QThread):
    result = pyqtSignal(str)

    def __init__(self, ai, prompt):
        super().__init__()
        self.ai = ai
        self.prompt = prompt

    def run(self):
        self.result.emit(self.ai.ask(self.prompt))


class CmdWorker(QThread):
    result = pyqtSignal(str)

    def __init__(self, executor, command, ctype):
        super().__init__()
        self.executor = executor
        self.command = command
        self.ctype = ctype

    def run(self):
        self.result.emit(self.executor.execute(self.command, self.ctype))


class ScriptWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str)

    def __init__(self, executor, name, commands):
        super().__init__()
        self.executor = executor
        self.name = name
        self.commands = commands
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        for i, cmd in enumerate(self.commands):
            if self._stop:
                break
            cmd = cmd.strip()
            if not cmd:
                continue
            self.progress.emit(i + 1, len(self.commands), cmd)
            self.executor.execute(cmd, "auto")
            time.sleep(1.2)
        self.finished.emit(self.name)

# === 8. SIDEBAR ===


class Sidebar(QFrame):
    nav_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self.setStyleSheet(f"""
            #sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.SURFACE}, stop:1 {Theme.BG});
                border-right: 1px solid {Theme.BORDER};
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 24, 16, 24)
        lay.setSpacing(4)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(48)
        logo_lay = QHBoxLayout(logo_frame)
        logo_lay.setContentsMargins(8, 0, 0, 0)
        logo_lay.setSpacing(12)

        # Logo icon
        logo_icon = QLabel("M")
        logo_icon.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        logo_icon.setFixedSize(36, 36)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Theme.ACCENT}, stop:1 {Theme.ACCENT_LIGHT});
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        logo_lay.addWidget(logo_icon)

        logo_text = QLabel("MIRA")
        logo_text.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_text.setStyleSheet(f"color: {Theme.TEXT}; letter-spacing: 3px; background: transparent;")
        logo_lay.addWidget(logo_text)
        logo_lay.addStretch()
        lay.addWidget(logo_frame)
        lay.addSpacing(24)

        # Section label
        section = QLabel("NAVIGATION")
        section.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 10px; font-weight: 600; letter-spacing: 2px; padding-left: 12px; background: transparent;")
        lay.addWidget(section)
        lay.addSpacing(8)

        # Nav buttons
        self.nav_btns = {}
        items = [
            ("chat", "\U0001F4AC", "Chat"),
            ("scripts", "\U0001F3AC", "Scripts"),
            ("notes", "\U0001F4DD", "Notes"),
            ("system", "\U0001F4CA", "System Monitor"),
            ("contacts", "\U0001F4CC", "Contacts"),
            ("settings", "\u2699\uFE0F", "Settings"),
            ("about", "\u2139\uFE0F", "About"),
        ]
        for nid, icon, label in items:
            btn = QToolButton()
            btn.setText(f"  {icon}  {label}")
            btn.setProperty("nav_id", nid)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QToolButton {{
                    background: transparent;
                    color: {Theme.TEXT_DIM};
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-family: 'Segoe UI';
                    text-align: left;
                    padding-left: 12px;
                }}
                QToolButton:hover {{
                    background: {Theme.CARD_HOVER};
                    color: {Theme.TEXT};
                }}
                QToolButton:checked {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {Theme.ACCENT_DARK}, stop:1 {Theme.ACCENT});
                    color: white;
                    font-weight: 600;
                }}
            """)
            btn.setCheckable(True)
            btn.clicked.connect(self._on_nav)
            lay.addWidget(btn)
            self.nav_btns[nid] = btn

        self.nav_btns["chat"].setChecked(True)
        lay.addStretch()

        # Status
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: {Theme.CARD};
                border-radius: 10px;
                padding: 8px 12px;
            }}
        """)
        status_lay = QHBoxLayout(status_frame)
        status_lay.setContentsMargins(8, 8, 8, 8)
        status_lay.setSpacing(8)
        self.dot = PulseIndicator(color=Theme.SUCCESS)
        self.dot.set_active(True)
        status_lay.addWidget(self.dot)
        status_text = QLabel("Online")
        status_text.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 12px; font-weight: 500; background: transparent;")
        status_lay.addWidget(status_text)
        status_lay.addStretch()
        lay.addWidget(status_frame)

    def _on_nav(self):
        btn = self.sender()
        nid = btn.property("nav_id")
        old = None
        for k, b in self.nav_btns.items():
            if b.isChecked() and k != nid:
                b.setChecked(False)
                old = k
            elif k == nid:
                b.setChecked(True)
        direction = "left"
        order = ["chat", "scripts", "notes", "system", "contacts", "settings", "about"]
        if old and nid in order and old in order:
            direction = "left" if order.index(nid) > order.index(old) else "right"
        self.nav_changed.emit(nid, direction)

    def select(self, nid):
        if nid in self.nav_btns:
            self.nav_btns[nid].click()

# === 9. TITLE BAR ===


class TitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.setFixedHeight(44)
        self._drag = None
        self.setStyleSheet(f"""
            QFrame {{
                background: {Theme.SURFACE};
                border-bottom: 1px solid {Theme.BORDER};
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(260, 0, 12, 0)
        lay.setSpacing(16)

        self.page_icon = QLabel("\U0001F4AC")
        self.page_icon.setFont(QFont("Segoe UI Emoji", 14))
        self.page_icon.setStyleSheet("background: transparent;")
        lay.addWidget(self.page_icon)

        self.page_lbl = QLabel("Chat")
        self.page_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.page_lbl.setStyleSheet(f"color: {Theme.TEXT}; background: transparent;")
        lay.addWidget(self.page_lbl)

        lay.addStretch()

        # Window buttons
        for txt, func, color in [
            ("\u2014", self._parent.showMinimized, Theme.TEXT_DIM),
            ("\u25A1", self._parent._toggle_maximize, Theme.TEXT_DIM),
            ("\u2715", self._parent.close, Theme.ERROR)
        ]:
            b = QPushButton(txt)
            b.setFixedSize(36, 30)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {color};
                    border: none;
                    font-size: 13px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background: {Theme.CARD_HOVER};
                }}
            """)
            b.clicked.connect(func)
            lay.addWidget(b)

    def set_page(self, text):
        self.page_lbl.setText(text)
        icons = {
            "Chat": "\U0001F4AC", "Scripts": "\U0001F3AC", "Notes": "\U0001F4DD",
            "System": "\U0001F4CA", "Contacts": "\U0001F4CC", "Settings": "\u2699\uFE0F", "About": "\u2139\uFE0F"
        }
        self.page_icon.setText(icons.get(text, "\U0001F4AC"))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._parent.isMaximized():
            self._drag = event.globalPosition().toPoint() - self._parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag and event.buttons() & Qt.MouseButton.LeftButton and not self._parent.isMaximized():
            self._parent.move(event.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, event):
        self._drag = None

    def mouseDoubleClickEvent(self, event):
        self._parent._toggle_maximize()

# === 10. CHAT PANEL ===


class ChatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {Theme.TEXT};
                font-family: 'Segoe UI';
                font-size: 14px;
                padding: 24px 32px;
                line-height: 1.6;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.CARD_HOVER};
                border-radius: 5px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.ACCENT}60;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        lay.addWidget(self.chat, 1)

        # Status indicator
        ind_row = QHBoxLayout()
        ind_row.setContentsMargins(32, 6, 32, 6)
        self.indicator = PulseIndicator(color=Theme.ACCENT_LIGHT)
        ind_row.addWidget(self.indicator)
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 12px; background: transparent;")
        ind_row.addWidget(self.status_lbl)
        ind_row.addStretch()
        wrap = QWidget()
        wrap.setLayout(ind_row)
        lay.addWidget(wrap)

        # Input area
        inp_frame = QFrame()
        inp_frame.setStyleSheet(f"""
            QFrame {{
                background: {Theme.SURFACE};
                border-top: 1px solid {Theme.BORDER};
                padding: 16px 28px;
            }}
        """)
        inp_lay = QHBoxLayout(inp_frame)
        inp_lay.setContentsMargins(0, 0, 0, 0)
        inp_lay.setSpacing(12)

        self.inp = FluentInput("Type a command or question...")
        inp_lay.addWidget(self.inp, 1)

        self.voice_btn = GlowButton("\U0001F3A4")
        self.voice_btn.setFixedWidth(48)
        inp_lay.addWidget(self.voice_btn)

        self.send_btn = GlowButton("\u27A4", accent=True)
        self.send_btn.setFixedWidth(48)
        inp_lay.addWidget(self.send_btn)

        lay.addWidget(inp_frame)

    def set_status(self, text, active=True):
        self.indicator.set_active(active)
        self.status_lbl.setText(text)

# === 11. SCRIPT PANEL ===


class ScriptPanel(QFrame):
    run_signal = pyqtSignal(str)
    create_signal = pyqtSignal()
    edit_signal = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.cfg = config
        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 28, 36, 28)
        lay.setSpacing(16)
        title = QLabel("Scripts")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        lay.addWidget(title)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea{{background:transparent;border:none;}}QScrollBar:vertical{{background:transparent;width:8px;}}QScrollBar::handle:vertical{{background:{Theme.CARD_HOVER};border-radius:4px;min-height:30px;}}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}")
        self.content = QWidget()
        self.content.setStyleSheet("background:transparent;")
        self.scroll.setWidget(self.content)
        self.cl = QVBoxLayout(self.content)
        self.cl.setContentsMargins(0, 0, 0, 0)
        self.cl.setSpacing(10)
        self.cl.addStretch()
        lay.addWidget(self.scroll, 1)
        add_btn = GlowButton("+ New Script", accent=True)
        add_btn.clicked.connect(self.create_signal.emit)
        lay.addWidget(add_btn)
        self.refresh()

    def refresh(self):
        while self.cl.count():
            item = self.cl.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        scripts = self.cfg.get("scripts", {})
        if not scripts:
            e = QLabel("No scripts yet. Create your first one!")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e.setStyleSheet(f"color:{Theme.TEXT_MUTED};padding:50px;font-size:14px;background:transparent;")
            self.cl.addWidget(e)
        else:
            for name, cmds in scripts.items():
                self.cl.addWidget(self._card(name, cmds))
        self.cl.addStretch()

    def _card(self, name, cmds):
        card = GlassCard()
        card.setHoverMode(True)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(8)
        header = QHBoxLayout()
        h = QLabel(name)
        h.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        h.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        header.addWidget(h)
        header.addStretch()
        run = GlowButton("Play", accent=True)
        run.setFixedWidth(60)
        run.clicked.connect(lambda: self.run_signal.emit(name))
        header.addWidget(run)
        edit = GlowButton("Edit")
        edit.setFixedWidth(50)
        edit.clicked.connect(lambda: self.edit_signal.emit(name))
        header.addWidget(edit)
        delete = GlowButton("Del")
        delete.setFixedWidth(46)
        delete.setStyleSheet(f"QPushButton{{background:{Theme.CARD_HOVER};color:{Theme.ERROR};border:none;border-radius:8px;padding:8px;font-family:'Segoe UI';}}QPushButton:hover{{background:rgba(239,68,68,0.2);}}")
        delete.clicked.connect(lambda: self._delete(name))
        header.addWidget(delete)
        cl.addLayout(header)
        meta = QLabel(f"{len(cmds)} steps ~{len(cmds)*1.2:.0f}s")
        meta.setStyleSheet(f"color:{Theme.TEXT_MUTED};font-size:12px;background:transparent;")
        cl.addWidget(meta)
        return card

    def _delete(self, name):
        if name in self.cfg.get("scripts", {}):
            del self.cfg["scripts"][name]
            save_config(self.cfg)
            self.refresh()

# === 12. NOTES PANEL ===


class NotesPanel(QFrame):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.cfg = config
        self._suspend = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 28, 36, 28)
        lay.setSpacing(16)
        header = QHBoxLayout()
        title = QLabel("Notes")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        header.addWidget(title)
        header.addStretch()
        add_btn = GlowButton("+ New", accent=True)
        add_btn.clicked.connect(self._new)
        header.addWidget(add_btn)
        lay.addLayout(header)
        content = QHBoxLayout()
        content.setSpacing(14)
        self.list_w = QListWidget()
        self.list_w.setStyleSheet(f"QListWidget{{background:{Theme.SURFACE};border:1px solid {Theme.BORDER};border-radius:12px;padding:6px;color:{Theme.TEXT};font-family:'Segoe UI';font-size:13px;}}QListWidget::item{{padding:10px 12px;border-radius:8px;margin:2px 0;}}QListWidget::item:hover{{background:{Theme.CARD_HOVER};}}QListWidget::item:selected{{background:{Theme.ACCENT};color:white;}}")
        self.list_w.currentItemChanged.connect(self._on_select)
        self.list_w.setMaximumWidth(260)
        content.addWidget(self.list_w, 1)
        right = QVBoxLayout()
        right.setSpacing(8)
        self.date_lbl = QLabel("")
        self.date_lbl.setStyleSheet(f"color:{Theme.TEXT_MUTED};font-size:12px;background:transparent;")
        right.addWidget(self.date_lbl)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Title...")
        self.title_edit.setStyleSheet(f"QLineEdit{{background:{Theme.CARD};border:1px solid {Theme.BORDER};border-radius:10px;padding:10px 14px;color:white;font-family:'Segoe UI';font-size:16px;font-weight:bold;}}QLineEdit:focus{{border-color:{Theme.ACCENT};}}")
        self.title_edit.textChanged.connect(self._auto_save)
        right.addWidget(self.title_edit)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Note text...")
        self.text_edit.setStyleSheet(f"QPlainTextEdit{{background:{Theme.CARD};border:1px solid {Theme.BORDER};border-radius:10px;padding:12px 14px;color:{Theme.TEXT};font-family:'Segoe UI';font-size:14px;}}QPlainTextEdit:focus{{border-color:{Theme.ACCENT};}}")
        self.text_edit.textChanged.connect(self._auto_save)
        right.addWidget(self.text_edit, 1)
        del_btn = GlowButton("Delete")
        del_btn.setStyleSheet(f"QPushButton{{background:{Theme.CARD_HOVER};color:{Theme.ERROR};border:none;border-radius:8px;padding:8px 14px;}}QPushButton:hover{{background:rgba(239,68,68,0.2);}}")
        del_btn.clicked.connect(self._delete)
        right.addWidget(del_btn)
        content.addLayout(right, 3)
        lay.addLayout(content, 1)
        self.refresh()

    def refresh(self):
        self.list_w.clear()
        for i, n in enumerate(self.cfg.get("notes", [])):
            t = n.get("title", "Untitled") or "Untitled"
            d = n.get("date", "")
            item = QListWidgetItem(f"{t}\n{d}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.list_w.addItem(item)

    def _new(self):
        notes = self.cfg.setdefault("notes", [])
        notes.insert(0, {"title": "New Note", "text": "", "date": datetime.now().strftime("%d.%m.%Y %H:%M")})
        save_config(self.cfg)
        self.refresh()
        self.list_w.setCurrentRow(0)

    def _on_select(self, current, _prev):
        if not current:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        notes = self.cfg.get("notes", [])
        if 0 <= idx < len(notes):
            self._suspend = True
            self.title_edit.setText(notes[idx].get("title", ""))
            self.text_edit.setPlainText(notes[idx].get("text", ""))
            self.date_lbl.setText(notes[idx].get("date", ""))
            self._suspend = False

    def _auto_save(self):
        if self._suspend:
            return
        current = self.list_w.currentItem()
        if not current:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        notes = self.cfg.get("notes", [])
        if 0 <= idx < len(notes):
            notes[idx]["title"] = self.title_edit.text() or "Untitled"
            notes[idx]["text"] = self.text_edit.toPlainText()
            notes[idx]["date"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            save_config(self.cfg)
            current.setText(f"{notes[idx]['title']}\n{notes[idx]['date']}")

    def _delete(self):
        current = self.list_w.currentItem()
        if not current:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        notes = self.cfg.get("notes", [])
        if 0 <= idx < len(notes):
            notes.pop(idx)
            save_config(self.cfg)
            self.refresh()
            self.title_edit.clear()
            self.text_edit.clear()

# === 13. SYSTEM MONITOR ===


class SystemMonitorPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 28, 36, 28)
        lay.setSpacing(16)
        title = QLabel("System Monitor")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        lay.addWidget(title)
        grid = QGridLayout()
        grid.setSpacing(14)
        self.cpu_card, self.cpu_val, self.cpu_bar = self._metric("CPU")
        grid.addWidget(self.cpu_card, 0, 0)
        self.ram_card, self.ram_val, self.ram_bar = self._metric("RAM")
        grid.addWidget(self.ram_card, 0, 1)
        self.disk_card, self.disk_val, self.disk_bar = self._metric("Disk")
        grid.addWidget(self.disk_card, 0, 2)
        info_card = GlassCard()
        il = QVBoxLayout(info_card)
        il.setContentsMargins(20, 16, 20, 16)
        il.setSpacing(8)
        it = QLabel("System Info")
        it.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        it.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        il.addWidget(it)
        self.info_lbl = QLabel()
        self.info_lbl.setStyleSheet(f"color:{Theme.TEXT_DIM};font-family:Consolas;font-size:11px;background:transparent;")
        self.info_lbl.setWordWrap(True)
        il.addWidget(self.info_lbl)
        grid.addWidget(info_card, 1, 0, 1, 3)
        lay.addLayout(grid)
        lay.addStretch()
        self._last_info = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(1500)
        self._update()

    def _metric(self, name):
        card = GlassCard()
        card.setMinimumHeight(120)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(6)
        t = QLabel(name)
        t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{Theme.TEXT_DIM};background:transparent;")
        cl.addWidget(t)
        v = QLabel("0%")
        v.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        v.setStyleSheet(f"color:{Theme.ACCENT_LIGHT};background:transparent;")
        cl.addWidget(v)
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(5)
        bar.setStyleSheet(f"QProgressBar{{background:{Theme.CARD_HOVER};border:none;border-radius:2px;}}QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {Theme.ACCENT},stop:1 {Theme.ACCENT_LIGHT});border-radius:2px;}}")
        cl.addWidget(bar)
        return card, v, bar

    def _update(self):
        try:
            cpu = psutil.cpu_percent(interval=0)
            self.cpu_val.setText(f"{cpu:.0f}%")
            self.cpu_bar.setValue(int(cpu))
            ram = psutil.virtual_memory()
            self.ram_val.setText(f"{ram.percent:.0f}%")
            self.ram_bar.setValue(int(ram.percent))
            disk = psutil.disk_usage("/")
            self.disk_val.setText(f"{disk.percent:.0f}%")
            self.disk_bar.setValue(int(disk.percent))
            now = time.time()
            if now - self._last_info > 30:
                self._last_info = now
                info = f"OS: {platform.system()} {platform.release()}\n"
                info += f"CPU: {platform.processor()[:50]}\n"
                info += f"RAM: {ram.total / (1024**3):.1f} GB ({ram.available / (1024**3):.1f} free)\n"
                info += f"Cores: {psutil.cpu_count(logical=False)} phys / {psutil.cpu_count(logical=True)} logical"
                self.info_lbl.setText(info)
        except Exception:
            pass

# === 14. CONTACTS ===


class ContactsPanel(QFrame):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        contacts = config.get("contacts", {})
        lay = QVBoxLayout(self)
        lay.setContentsMargins(50, 36, 50, 36)
        lay.setSpacing(16)
        title = QLabel("Contacts")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        lay.addWidget(title)
        for icon, name, val, url in [
            ("\u2708\uFE0F", "Telegram", contacts.get("telegram", "@CayPlay78"), f"https://t.me/{contacts.get('telegram', '@CayPlay78').lstrip('@')}"),
            ("\U0001F535", "VKontakte", contacts.get("vk", "https://m.vk.com/cayplay"), contacts.get("vk", "https://m.vk.com/cayplay")),
        ]:
            card = GlassCard()
            card.setFixedHeight(80)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(22, 16, 22, 16)
            ic = QLabel(icon)
            ic.setFont(QFont("Segoe UI Emoji", 26))
            ic.setStyleSheet("background:transparent;")
            cl.addWidget(ic)
            info = QVBoxLayout()
            info.setSpacing(2)
            lbl = QLabel(name)
            lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
            info.addWidget(lbl)
            vl = QLabel(val)
            vl.setFont(QFont("Consolas", 12))
            vl.setStyleSheet(f"color:{Theme.ACCENT_LIGHT};background:transparent;")
            info.addWidget(vl)
            cl.addLayout(info)
            cl.addStretch()
            copy = GlowButton("Copy")
            copy.setFixedWidth(60)
            copy.clicked.connect(lambda v=val: self._copy(v))
            cl.addWidget(copy)
            open_ = GlowButton("Open", accent=True)
            open_.setFixedWidth(60)
            open_.clicked.connect(lambda u=url: QDesktopServices.openUrl(QUrl(u)))
            cl.addWidget(open_)
            lay.addWidget(card)
        lay.addStretch()

    def _copy(self, text):
        QApplication.clipboard().setText(text)

# === 15. SETTINGS ===


class SettingsPanel(QFrame):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.cfg = config
        self._parent = parent
        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 28, 36, 28)
        lay.setSpacing(16)
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        lay.addWidget(title)
        # AI Provider section
        ai_card = GlassCard()
        al = QVBoxLayout(ai_card)
        al.setContentsMargins(20, 16, 20, 16)
        al.setSpacing(10)
        al.addWidget(self._section_label("AI Provider"))
        # Provider toggle
        prov_row = QHBoxLayout()
        prov_row.setSpacing(10)
        self.or_btn = GlowButton("OpenRouter (Cloud)", accent=True)
        self.or_btn.clicked.connect(lambda: self._set_provider("openrouter"))
        prov_row.addWidget(self.or_btn)
        self.oll_btn = GlowButton("Ollama (Local)")
        self.oll_btn.clicked.connect(lambda: self._set_provider("ollama"))
        prov_row.addWidget(self.oll_btn)
        prov_row.addStretch()
        al.addLayout(prov_row)
        # OpenRouter section
        or_frame = QFrame()
        or_frame.setStyleSheet(f"QFrame{{background:{Theme.CARD};border-radius:10px;padding:12px;}}")
        or_lay = QVBoxLayout(or_frame)
        or_lay.setSpacing(8)
        or_lay.addWidget(self._label("OpenRouter API Key"))
        key_row = QHBoxLayout()
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("sk-or-...")
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setText(config.get("openrouter", {}).get("api_key", ""))
        self.api_input.setStyleSheet(f"QLineEdit{{background:{Theme.INPUT};border:1px solid {Theme.BORDER};border-radius:8px;padding:8px 12px;color:white;font-family:Consolas;font-size:12px;}}QLineEdit:focus{{border-color:{Theme.ACCENT};}}")
        self.api_input.textChanged.connect(self._on_key_change)
        key_row.addWidget(self.api_input, 1)
        show_btn = QPushButton("Show")
        show_btn.setFixedWidth(55)
        show_btn.setStyleSheet(f"QPushButton{{background:{Theme.CARD_HOVER};color:{Theme.TEXT_DIM};border:none;border-radius:6px;font-size:11px;}}QPushButton:hover{{color:white;}}")
        show_btn.clicked.connect(self._toggle_key)
        key_row.addWidget(show_btn)
        or_lay.addLayout(key_row)
        or_lay.addWidget(self._label("Model"))
        self.or_model_combo = QComboBox()
        self.or_model_combo.addItems([
            "google/gemini-2.0-flash-001",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.3-70b-instruct",
            "deepseek/deepseek-chat-v3-0324",
            "qwen/qwen3-30b-a3b",
        ])
        self.or_model_combo.setCurrentText(config.get("openrouter", {}).get("model", "google/gemini-2.0-flash-001"))
        self.or_model_combo.setStyleSheet(f"QComboBox{{background:{Theme.INPUT};border:1px solid {Theme.BORDER};border-radius:8px;padding:8px 12px;color:white;font-family:Consolas;font-size:12px;min-width:200px;}}QComboBox::drop-down{{border:none;}}QComboBox QAbstractItemView{{background:{Theme.SURFACE};color:white;selection-background-color:{Theme.ACCENT};border:1px solid {Theme.BORDER};}}")
        self.or_model_combo.currentTextChanged.connect(self._on_or_model)
        or_lay.addWidget(self.or_model_combo)
        al.addWidget(or_frame)
        # Ollama section
        oll_frame = QFrame()
        oll_frame.setStyleSheet(f"QFrame{{background:{Theme.CARD};border-radius:10px;padding:12px;}}")
        oll_lay = QVBoxLayout(oll_frame)
        oll_lay.setSpacing(8)
        oll_lay.addWidget(self._label("Ollama Model"))
        self.oll_combo = QComboBox()
        self.oll_combo.addItems(["qwen3:0.6b", "qwen3:1.7b", "qwen3:4b", "qwen3:8b", "qwen2.5:1.5b", "qwen2.5:3b", "llama3.2:3b"])
        self.oll_combo.setCurrentText(config.get("ollama", {}).get("model", "qwen3:1.7b"))
        self.oll_combo.setStyleSheet(self.or_model_combo.styleSheet())
        self.oll_combo.currentTextChanged.connect(self._on_oll_model)
        oll_lay.addWidget(self.oll_combo)
        dl = GlowButton("Download Model")
        dl.clicked.connect(self._download)
        oll_lay.addWidget(dl)
        al.addWidget(oll_frame)
        # Status
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color:{Theme.TEXT_DIM};font-family:Consolas;font-size:11px;background:transparent;")
        al.addWidget(self.status_lbl)
        lay.addWidget(ai_card)
        # Actions
        act_card = GlassCard()
        act_lay = QVBoxLayout(act_card)
        act_lay.setContentsMargins(20, 16, 20, 16)
        act_lay.setSpacing(8)
        act_lay.addWidget(self._section_label("Actions"))
        refresh = GlowButton("Refresh Status")
        refresh.clicked.connect(self._refresh)
        act_lay.addWidget(refresh)
        clear = GlowButton("Clear AI History")
        clear.clicked.connect(self._clear_ai)
        act_lay.addWidget(clear)
        lay.addWidget(act_card)
        lay.addStretch()
        self._update_provider_ui()

    def _section_label(self, text):
        l = QLabel(text)
        l.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        l.setStyleSheet(f"color:{Theme.TEXT};background:transparent;")
        return l

    def _label(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"color:{Theme.TEXT_DIM};font-size:12px;background:transparent;")
        return l

    def _set_provider(self, p):
        self.cfg["ai_provider"] = p
        save_config(self.cfg)
        if hasattr(self._parent, "_ai"):
            self._parent._ai.set_provider(p)
        self._update_provider_ui()

    def _update_provider_ui(self):
        p = self.cfg.get("ai_provider", "openrouter")
        self.or_btn.setStyleSheet(f"QPushButton{{background:{Theme.ACCENT if p=='openrouter' else Theme.CARD_HOVER};color:{'white' if p=='openrouter' else Theme.TEXT};border:none;border-radius:10px;padding:10px 18px;font-family:'Segoe UI';font-size:13px;}}")
        self.oll_btn.setStyleSheet(f"QPushButton{{background:{Theme.ACCENT if p=='ollama' else Theme.CARD_HOVER};color:{'white' if p=='ollama' else Theme.TEXT};border:none;border-radius:10px;padding:10px 18px;font-family:'Segoe UI';font-size:13px;}}")
        self._update_status()

    def _on_key_change(self, key):
        self.cfg.setdefault("openrouter", {})["api_key"] = key
        save_config(self.cfg)
        if hasattr(self._parent, "_ai"):
            self._parent._ai.set_api_key(key)
        self._update_status()

    def _on_or_model(self, model):
        self.cfg.setdefault("openrouter", {})["model"] = model
        save_config(self.cfg)
        if hasattr(self._parent, "_ai"):
            self._parent._ai.set_or_model(model)

    def _on_oll_model(self, model):
        self.cfg.setdefault("ollama", {})["model"] = model
        save_config(self.cfg)
        if hasattr(self._parent, "_ai"):
            self._parent._ai.set_oll_model(model)

    def _toggle_key(self):
        mode = self.api_input.echoMode()
        self.api_input.setEchoMode(QLineEdit.EchoMode.Normal if mode == QLineEdit.EchoMode.Password else QLineEdit.EchoMode.Password)

    def _update_status(self):
        p = self.cfg.get("ai_provider", "openrouter")
        if p == "openrouter":
            ok = bool(self.api_input.text().strip())
            self.status_lbl.setText(f"{'OK - Cloud AI ready' if ok else 'No API key provided'}")
            self.status_lbl.setStyleSheet(f"color:{Theme.SUCCESS if ok else Theme.WARNING};font-family:Consolas;font-size:11px;background:transparent;")
        else:
            ok = hasattr(self._parent, "_ai") and self._parent._ai.oll_available if hasattr(self._parent, "_ai") else False
            self.status_lbl.setText(f"{'OK - Ollama online' if ok else 'Checking Ollama...'}")
            self.status_lbl.setStyleSheet(f"color:{Theme.SUCCESS if ok else Theme.WARNING};font-family:Consolas;font-size:11px;background:transparent;")

    def _refresh(self):
        if hasattr(self._parent, "_ai"):
            self._parent._ai.check_ollama_async()
        QTimer.singleShot(1500, self._update_status)

    def _clear_ai(self):
        if hasattr(self._parent, "_ai"):
            self._parent._ai.clear()

    def _download(self):
        model = self.oll_combo.currentText()
        def _run():
            try:
                flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                p = subprocess.Popen(["ollama", "pull", model], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
                p.communicate(timeout=600)
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()

# === 16. ABOUT ===


class AboutPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card = GlassCard()
        card.setMaximumWidth(560)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(44, 36, 44, 36)
        cl.setSpacing(12)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QLabel("M")
        logo.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        logo.setStyleSheet(f"color:{Theme.ACCENT};background:transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(logo)
        v = QLabel("Version 13.0 AURORA")
        v.setFont(QFont("Consolas", 12))
        v.setStyleSheet(f"color:{Theme.ACCENT_LIGHT};background:transparent;")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(v)
        d = QLabel("AI Assistant for your PC.\nVoice, text, scripts, search, system monitor.")
        d.setFont(QFont("Segoe UI", 13))
        d.setStyleSheet(f"color:{Theme.TEXT_DIM};background:transparent;")
        d.setAlignment(Qt.AlignmentFlag.AlignCenter)
        d.setWordWrap(True)
        cl.addWidget(d)
        cl.addSpacing(8)
        c = QLabel("(c) CayPlay 2026")
        c.setFont(QFont("Segoe UI", 11))
        c.setStyleSheet(f"color:{Theme.TEXT_MUTED};background:transparent;")
        c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(c)
        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addStretch()
        gh = GlowButton("GitHub")
        gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com")))
        btns.addWidget(gh)
        tg = GlowButton("Telegram", accent=True)
        tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/CayPlay78")))
        btns.addWidget(tg)
        btns.addStretch()
        cl.addLayout(btns)
        wrap = QHBoxLayout()
        wrap.addStretch()
        wrap.addWidget(card)
        wrap.addStretch()
        lay.addLayout(wrap)

# === 17. TOAST ===


class Toast(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame{{background:{Theme.ACCENT};border-radius:12px;padding:12px 20px;color:white;font-family:'Segoe UI';font-size:13px;}}")
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, text, duration=2500):
        for ch in self.findChildren(QLabel):
            ch.deleteLater()
        lay = self.layout() or QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(text)
        lbl.setStyleSheet("color:white;background:transparent;")
        lbl.setWordWrap(True)
        lay.addWidget(lbl)
        self.adjustSize()
        if self.parent():
            pw = self.parent().width()
            self.move((pw - self.width()) // 2, self.parent().height() - self.height() - 50)
        self.show()
        self.raise_()
        self._timer.start(duration)

# === 18. MAIN WINDOW ===


class MIRAWindow(QMainWindow):
    voice_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self._executor = SystemExecutor(self.cfg)
        self._ai = AIManager(self.cfg)
        self._voice = VoiceManager(self.cfg)
        self._classifier = IntentClassifier(self.cfg)
        self.voice_signal.connect(self._on_voice)
        self.active_threads = []
        self._script_worker = None
        self._setup_ui()
        self._setup_hotkeys()
        self._init_tray()
        QTimer.singleShot(100, self._boot)

    def _setup_ui(self):
        self.setWindowTitle("MIRA - AI Assistant")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background:{Theme.BG};")
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.title_bar = TitleBar(self)
        root.addWidget(self.title_bar)
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self._switch_page)
        content.addWidget(self.sidebar)
        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet(f"background:{Theme.BG};")
        self.chat_panel = ChatPanel()
        self.chat_panel.send_btn.clicked.connect(self._process)
        self.chat_panel.inp.returnPressed.connect(self._process)
        self.chat_panel.voice_btn.clicked.connect(self._toggle_voice)
        self.stacked.addWidget(self.chat_panel)
        self.script_panel = ScriptPanel(self.cfg)
        self.script_panel.run_signal.connect(self._run_script)
        self.script_panel.create_signal.connect(lambda: self._create_script_dialog())
        self.script_panel.edit_signal.connect(self._edit_script)
        self.stacked.addWidget(self.script_panel)
        self.notes_panel = NotesPanel(self.cfg)
        self.stacked.addWidget(self.notes_panel)
        self.system_panel = SystemMonitorPanel()
        self.stacked.addWidget(self.system_panel)
        self.contacts_panel = ContactsPanel(self.cfg)
        self.stacked.addWidget(self.contacts_panel)
        self.settings_panel = SettingsPanel(self.cfg, self)
        self.stacked.addWidget(self.settings_panel)
        self.about_panel = AboutPanel()
        self.stacked.addWidget(self.about_panel)
        content.addWidget(self.stacked, 1)
        cw = QWidget()
        cw.setLayout(content)
        root.addWidget(cw, 1)
        self._toast = Toast(self)

    def _setup_hotkeys(self):
        from PyQt6.QtGui import QShortcut, QKeySequence
        def _ghk():
            try:
                import keyboard
                hk = self.cfg.get("hotkey", "ctrl+shift+m")
                keyboard.add_hotkey(hk, self._restore_window)
            except Exception:
                pass
        threading.Thread(target=_ghk, daemon=True).start()
        for i, page in enumerate(["chat", "scripts", "notes", "system", "contacts", "settings", "about"], 1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, lambda p=page: self.sidebar.select(p))
        QShortcut(QKeySequence("Ctrl+Q"), self, self._full_exit)
        QShortcut(QKeySequence("Ctrl+L"), self, self._clear_chat)
        QShortcut(QKeySequence("Ctrl+Space"), self, self._toggle_voice)
        QShortcut(QKeySequence("F11"), self, self._toggle_maximize)

    def _init_tray(self):
        px = QPixmap(64, 64)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        g = QRadialGradient(32, 32, 32)
        g.setColorAt(0, QColor(99, 102, 241))
        g.setColorAt(1, QColor(79, 70, 229))
        p.setBrush(QBrush(g))
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.drawRoundedRect(2, 2, 60, 60, 14, 14)
        p.setPen(Qt.GlobalColor.white)
        p.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "M")
        p.end()
        self.tray = QSystemTrayIcon(QIcon(px), self)
        self.tray.setToolTip("MIRA v13.0")
        m = QMenu()
        m.setStyleSheet(f"QMenu{{background:{Theme.SURFACE};color:{Theme.TEXT};border:1px solid {Theme.BORDER};border-radius:8px;padding:6px;}}QMenu::item{{padding:8px 24px;border-radius:6px;}}QMenu::item:selected{{background:{Theme.ACCENT};color:white;}}QMenu::separator{{height:1px;background:{Theme.BORDER};margin:4px 8px;}}")
        a1 = QAction("Open MIRA", self)
        a1.triggered.connect(self._restore_window)
        m.addAction(a1)
        m.addSeparator()
        a3 = QAction("Exit", self)
        a3.triggered.connect(self._full_exit)
        m.addAction(a3)
        self.tray.setContextMenu(m)
        self.tray.activated.connect(lambda r: self._restore_window() if r == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def _restore_window(self):
        if self.isMinimized():
            self.showNormal()
        if not self.isVisible():
            self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()

    def _full_exit(self):
        self.tray.hide()
        for t in self.active_threads:
            try:
                if t.isRunning():
                    t.terminate()
            except Exception:
                pass
        QApplication.quit()
        sys.exit(0)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _switch_page(self, page, direction="left"):
        titles = {"chat": "Chat", "scripts": "Scripts", "notes": "Notes", "system": "System", "contacts": "Contacts", "settings": "Settings", "about": "About"}
        widgets = {"chat": self.chat_panel, "scripts": self.script_panel, "notes": self.notes_panel, "system": self.system_panel, "contacts": self.contacts_panel, "settings": self.settings_panel, "about": self.about_panel}
        self.stacked.setCurrentWidget(widgets.get(page, self.chat_panel))
        self.title_bar.set_page(titles.get(page, "MIRA"))

    def _boot(self):
        welcome = """Добро пожаловать в MIRA v13.0 AURORA

Я ваш ИИ-ассистент. Вот что я умею:

  Чат и ИИ
    - Задайте любой вопрос (облачный ИИ через OpenRouter)
    - "Привет", "Как дела?", "Что ты умеешь?"

  Приложения и игры
    - "Открой браузер", "Запусти Steam"
    - "Открой калькулятор", "Открой VS Code"

  Поиск
    - "Найди рецепт пасты"
    - "Что такое Python?", "Кто такой Илон Маск?"

  Система
    - "Выключи компьютер", "Открой диспетчер задач"
    - "Сколько будет 25*4?" (калькулятор)

  Сценарии
    - "Создай сценарий - Утренний распорядок"
    - "Запусти сценарий - Утренний распорядок"

  Заметки
    - "Запомни купить молоко"
    - "Покажи заметки"

  Голос
    - Нажмите кнопку микрофона или Ctrl+Space

  Горячие клавиши
    - Ctrl+1-7: Переключение страниц
    - F11: Полный экран
    - Ctrl+Q: Выход"""
        self._add_bubble("ai", welcome)
        self._ai.check_ollama_async()
        QTimer.singleShot(300, lambda: self.settings_panel._update_status())

    def _clear_chat(self):
        self.chat_panel.chat.clear()
        self._add_bubble("ai", "Chat cleared.")

    def _cleanup_thread(self, t):
        if t in self.active_threads:
            self.active_threads.remove(t)
        t.deleteLater()

    def _start_worker(self, w):
        w.finished.connect(lambda: self._cleanup_thread(w))
        self.active_threads.append(w)
        w.start()

    def _add_bubble(self, role, text):
        colors = {"user": Theme.INFO, "ai": Theme.SUCCESS, "sys": Theme.WARNING, "success": Theme.SUCCESS, "error": Theme.ERROR}
        align = "right" if role == "user" else "left"
        bg_map = {
            "user": "rgba(99, 102, 241, 0.12)",
            "ai": "rgba(34, 197, 94, 0.08)",
            "sys": "rgba(245, 158, 11, 0.08)",
            "success": "rgba(34, 197, 94, 0.12)",
            "error": "rgba(239, 68, 68, 0.12)"
        }
        bg = bg_map.get(role, bg_map["ai"])
        c = colors.get(role, Theme.SUCCESS)
        safe = text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        ts = datetime.now().strftime("%H:%M")

        if role == "user":
            html = f"""
            <div style="text-align:right; margin:12px 0;">
                <div style="background:linear-gradient(135deg, {Theme.ACCENT}18, {Theme.ACCENT}08);
                            padding:14px 18px; border-radius:16px 16px 4px 16px;
                            display:inline-block; max-width:75%;
                            border:1px solid {Theme.ACCENT}30;
                            box-shadow:0 2px 8px rgba(99,102,241,0.1);">
                    <div style="color:{Theme.TEXT}; font-size:14px; line-height:1.5;">{safe}</div>
                    <div style="color:{Theme.TEXT_MUTED}; font-size:10px; margin-top:6px;">{ts}</div>
                </div>
            </div>
            """
        else:
            html = f"""
            <div style="text-align:left; margin:12px 0;">
                <div style="background:{bg};
                            padding:14px 18px; border-radius:16px 16px 16px 4px;
                            display:inline-block; max-width:75%;
                            border:1px solid {c}25;
                            box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <div style="font-size:10px; color:{c}; font-weight:600; letter-spacing:1px; margin-bottom:6px;">{role.upper()}</div>
                    <div style="color:{Theme.TEXT}; font-size:14px; line-height:1.5;">{safe}</div>
                    <div style="color:{Theme.TEXT_MUTED}; font-size:10px; margin-top:6px;">{ts}</div>
                </div>
            </div>
            """

        self.chat_panel.chat.append(html)
        sb = self.chat_panel.chat.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _process(self):
        txt = self.chat_panel.inp.text().strip()
        if not txt:
            return
        self.chat_panel.inp.clear()
        self._add_bubble("user", txt)
        QTimer.singleShot(10, lambda: self._route(txt))

    def _route(self, text):
        try:
            intent, data = self._classifier.classify(text)
            if intent == "system_cmd":
                self._add_bubble("sys", f"Running: {data['trigger']}")
                self._execute_cmd(data["action"], data["type"])
            elif intent == "search_web":
                q = data.get('query') or data.get('match', '')
                # Clean filler phrases from search query
                q = re.sub(r"\b(в\s+браузере|в\s+интернете|онлайн|в\s+гугле|в\s+яндексе|в\s+поиске)\b", "", q, flags=re.IGNORECASE)
                q = " ".join(q.split()).strip()
                self._add_bubble("sys", f"Searching: {q}")
                self._execute_cmd(f"SEARCH:{q}", "search")
            elif intent == "open_url":
                self._add_bubble("sys", f"Opening: {data['url']}")
                self._execute_cmd(f"URL:{data['url']}", "url")
            elif intent == "open_app":
                self._add_bubble("sys", f"Launching: {data.get('display', data['target'])}")
                self._execute_cmd(data["target"], "auto")
            elif intent == "create_script":
                self._create_script_dialog(data.get("match", ""))
            elif intent == "run_script":
                self._run_script(data.get("match", ""))
            elif intent == "list_scripts":
                scripts = self.cfg.get("scripts", {})
                msg = "Scripts:\n" + "\n".join(f"- {n} ({len(c)} steps)" for n, c in scripts.items()) if scripts else "No scripts yet."
                self._add_bubble("ai", msg)
            elif intent == "time_query":
                self._add_bubble("ai", f"Time: {datetime.now().strftime('%H:%M:%S')}")
            elif intent == "date_query":
                months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                n = datetime.now()
                self._add_bubble("ai", f"Date: {n.day} {months[n.month]} {n.year}")
            elif intent == "calc":
                try:
                    safe = re.sub(r"[^0-9+\-*/().,\s]", "", data.get("expr", "")).replace(",", ".")
                    result = eval(safe, {"__builtins__": {}}, {})
                    self._add_bubble("success", f"{data.get('expr', '')} = {result}")
                except Exception:
                    self._add_bubble("error", f"Cannot calculate: {data.get('expr', '')}")
            elif intent == "note_save":
                notes = self.cfg.setdefault("notes", [])
                notes.insert(0, {"title": data["text"][:40], "text": data["text"], "date": datetime.now().strftime("%d.%m.%Y %H:%M")})
                save_config(self.cfg)
                self.notes_panel.refresh()
                self._add_bubble("success", f"Note saved: {data['text']}")
            elif intent == "note_list":
                self.sidebar.select("notes")
            elif intent == "chat":
                if "response" in data:
                    self._add_bubble("ai", data["response"])
                else:
                    self._add_bubble("ai", "Thinking...")
                    w = AIWorker(self._ai, data.get("prompt", text))
                    w.result.connect(self._on_ai_result)
                    self._start_worker(w)
        except Exception as e:
            self._add_bubble("error", f"Error: {e}")

    def _on_cmd_result(self, result):
        self.chat_panel.set_status("", False)
        role = "success" if any(w in result for w in ["Запущено", "Открыто", "Steam", "В ", "Готово", "Открываю"]) else ("error" if "Ошибка" in result or "Не найдено" in result else "sys")
        self._add_bubble(role, result)

    def _on_ai_result(self, result):
        self.chat_panel.set_status("", False)
        self._add_bubble("ai", result)

    def _execute_cmd(self, cmd, ctype):
        self.chat_panel.set_status("Working...", True)
        w = CmdWorker(self._executor, cmd, ctype)
        w.result.connect(self._on_cmd_result)
        self._start_worker(w)

    def _run_script(self, name):
        scripts = self.cfg.get("scripts", {})
        if name not in scripts:
            self._add_bubble("error", f"Script '{name}' not found")
            return
        cmds = scripts[name]
        self._add_bubble("ai", f"Running '{name}' ({len(cmds)} steps)...")
        self._script_worker = ScriptWorker(self._executor, name, cmds)
        self._script_worker.progress.connect(lambda i, t, c: self._add_bubble("sys", f"Step {i}/{t}: {c}"))
        self._script_worker.finished.connect(lambda n: self._add_bubble("success", f"Script '{n}' complete!"))
        self._start_worker(self._script_worker)

    def _create_script_dialog(self, pre_name=""):
        self._edit_script(None, pre_name)

    def _edit_script(self, name=None, pre_name=""):
        dlg = QDialog(self)
        dlg.setWindowTitle("Script Editor")
        dlg.resize(580, 440)
        dlg.setStyleSheet(f"QDialog{{background:{Theme.SURFACE};color:{Theme.TEXT};}}QLabel{{color:{Theme.ACCENT_LIGHT};font-weight:bold;font-family:'Segoe UI';}}QLineEdit,QPlainTextEdit{{background:{Theme.CARD};border:1px solid {Theme.BORDER};border-radius:8px;padding:10px;color:white;font-family:Consolas;}}QLineEdit:focus,QPlainTextEdit:focus{{border-color:{Theme.ACCENT};}}")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)
        lay.addWidget(QLabel("Name:"))
        name_in = QLineEdit(pre_name)
        if name and name in self.cfg.get("scripts", {}):
            name_in.setText(name)
        lay.addWidget(name_in)
        lay.addWidget(QLabel("Commands (one per line):"))
        cmd_in = QPlainTextEdit()
        if name and name in self.cfg.get("scripts", {}):
            cmd_in.setPlainText("\n".join(self.cfg["scripts"][name]))
        lay.addWidget(cmd_in)
        btns = QHBoxLayout()
        btns.addStretch()
        cancel = GlowButton("Cancel")
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(cancel)
        save = GlowButton("Save", accent=True)
        save.clicked.connect(dlg.accept)
        btns.addWidget(save)
        lay.addLayout(btns)
        if dlg.exec():
            nm = name_in.text().strip()
            cmds = [l.strip() for l in cmd_in.toPlainText().split("\n") if l.strip()]
            if not nm:
                return
            if name and name in self.cfg.get("scripts", {}):
                del self.cfg["scripts"][name]
            self.cfg.setdefault("scripts", {})[nm] = cmds
            save_config(self.cfg)
            self.script_panel.refresh()

    def _on_voice(self, txt):
        if not txt:
            self.chat_panel.set_status("", False)
            return
        self._add_bubble("user", f"{txt}")
        QTimer.singleShot(10, lambda: self._route(txt))
        self.chat_panel.set_status("", False)

    def _toggle_voice(self):
        if not self._voice.mic:
            self._add_bubble("error", "Microphone not found")
            return
        self.chat_panel.set_status("Listening...", True)
        def listen():
            try:
                with self._voice.mic as source:
                    self._voice.rec.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self._voice.rec.listen(source, timeout=6, phrase_time_limit=10)
                    txt = self._voice.recognize(audio)
                    self.voice_signal.emit(txt or "")
            except Exception:
                self.voice_signal.emit("")
        threading.Thread(target=listen, daemon=True).start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_toast") and self._toast.isVisible():
            self._toast.move((self.width() - self._toast.width()) // 2, self.height() - self._toast.height() - 50)

    def closeEvent(self, event):
        self.hide()
        self.tray.showMessage("MIRA", "Minimized to tray.", QSystemTrayIcon.MessageIcon.Information, 2000)
        event.ignore()

# === 19. MAIN ===


def main():
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("MIRA")
    app.setApplicationVersion("13.0")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(Theme.BG))
    palette.setColor(palette.ColorRole.WindowText, QColor(Theme.TEXT))
    palette.setColor(palette.ColorRole.Base, QColor(Theme.CARD))
    palette.setColor(palette.ColorRole.Text, QColor(Theme.TEXT))
    palette.setColor(palette.ColorRole.Button, QColor(Theme.CARD_HOVER))
    palette.setColor(palette.ColorRole.ButtonText, QColor(Theme.TEXT))
    palette.setColor(palette.ColorRole.Highlight, QColor(Theme.ACCENT))
    palette.setColor(palette.ColorRole.HighlightedText, QColor("white"))
    app.setPalette(palette)
    win = MIRAWindow()
    win.resize(1400, 900)
    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
