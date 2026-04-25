#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МИРА (MIRA) — AI-Ассистент v11.0 "ULTIMATE STABLE"
✅ Исправлены все ошибки: Layout, Threads, CSS, DPI, Импорты.
✨ Дизайн: Fluent Dark, FullHD, 100% отзывчивый UI.
🧠 Функции: Omni-Resolver, Поиск в интернете, Сценарии, Голос, Локальный AI.
© CayPlay 2026. Все права защищены.
"""

# === 1. ИМПОРТЫ ===
import os, sys, json, logging, subprocess, threading, time, urllib.request, urllib.parse, webbrowser
import shutil, psutil, platform, re, winreg, math
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

import pyttsx3
import speech_recognition as sr
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QStatusBar,
    QSystemTrayIcon, QMenu, QDialog, QPlainTextEdit, QScrollArea,
    QStackedWidget, QMessageBox, QToolButton, QSizePolicy
)
# ✅ ИСПРАВЛЕНО: QAction перемещен в QtGui для PyQt6
from PyQt6.QtGui import (
    QAction, QFont, QIcon, QColor, QPainter, QPixmap, QClipboard
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QUrl, QSize, QObject
)
from PyQt6.QtGui import QDesktopServices

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("mira.log", encoding="utf-8")])
logger = logging.getLogger("MIRA")

def handle_exception(etype, value, tb):
    import traceback
    logger.error("".join(traceback.format_exception(etype, value, tb)))
sys.excepthook = handle_exception

# === 2. КОНФИГУРАЦИЯ ===
CONFIG_PATH = Path("mira_config.json")

DEFAULT_CONFIG = {
    "ai": {"base_url": "http://localhost:11434", "model": "qwen2.5:1.5b", "max_tokens": 2048, "temperature": 0.3},
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
        with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f: cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg: cfg[k] = v
            elif isinstance(v, dict) and isinstance(cfg[k], dict):
                for sk, sv in v.items():
                    if sk not in cfg[k]: cfg[k][sk] = sv
        with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=4, ensure_ascii=False)
        return cfg
    except Exception as e:
        logger.error(f"Config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=4, ensure_ascii=False)

# === 3. UI КОМПОНЕНТЫ (Fluent Style) ===

class FluentButton(QPushButton):
    def __init__(self, text="", parent=None, icon=None, accent=False):
        super().__init__(text, parent)
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_style()
        
    def _setup_style(self):
        # ✅ ИСПРАВЛЕНО: Удален transition
        base = "QPushButton { border: none; border-radius: 8px; padding: 10px 18px; font-family: 'Segoe UI', sans-serif; font-size: 14px; }"
        if self.accent:
            self.setStyleSheet(base + """
                QPushButton { background: #605cd8; color: white; }
                QPushButton:hover { background: #7470e8; }
                QPushButton:pressed { background: #504cb8; }
            """)
        else:
            self.setStyleSheet(base + """
                QPushButton { background: #2d2d3a; color: #e0e0e0; }
                QPushButton:hover { background: #3d3d4a; }
                QPushButton:pressed { background: #252530; }
            """)

class FluentInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                background: #1e1e2a;
                border: 2px solid #3a3a4a;
                border-radius: 10px;
                padding: 12px 16px;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
            }
            QLineEdit:focus {
                border-color: #605cd8;
                background: #252535;
            }
        """)

class FluentCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fluentCard")
        self.setStyleSheet("""
            #fluentCard {
                background: #1e1e2a;
                border: 1px solid #3a3a4a;
                border-radius: 12px;
            }
        """)

class StatusIndicator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self.setObjectName("statusIndicator")
        self.setStyleSheet("#statusIndicator { background: transparent; }")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(150)
        self.phase = 0
        self.active = False
        
    def set_active(self, active: bool):
        self.active = active
        if not active: self.update()
        
    def _animate(self):
        if self.active:
            self.phase += 0.3
            self.update()
            
    def paintEvent(self, event):
        if not self.active: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        for i in range(3):
            x = w//2 - 15 + i * 15
            amp = math.sin(self.phase + i) * 0.5 + 0.5
            r = int(amp * 4) + 2
            painter.setBrush(QColor(96, 92, 216, int(180 + amp * 75)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x), h//2 - r//2, r, r)

# === 4. БЭКЕНД (Omni-Resolver & AI) ===

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
                    content = f.read()
                    for line in content.split("\n"):
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
                resolved = self.resolver.resolve(command)
                logger.info(f"🔍 Resolve '{command}' -> '{resolved}'")
                if resolved and Path(resolved).exists():
                    subprocess.Popen(resolved, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return f"✅ Запущено: {Path(resolved).name if Path(resolved).exists() else command}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

class AIManager:
    def __init__(self, config: Dict):
        ai_cfg = config.get("ai", DEFAULT_CONFIG["ai"])
        self.base_url = ai_cfg["base_url"]
        self.model = ai_cfg["model"]
        self.ai_history = [{"role":"system","content":"Ты МИРА, ИИ-ассистент. Отвечай кратко, по делу."}]
        self.ai_available = False
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as r:
                self.ai_available = r.status == 200
        except: pass
        
    def ask(self, prompt: str) -> str:
        if not self.ai_available:
            return "⚠️ Ollama оффлайн. Запусти `ollama pull qwen2.5:1.5b`"
        self.ai_history.append({"role":"user","content":prompt})
        if len(self.ai_history) > 10: self.ai_history = [self.ai_history[0]] + self.ai_history[-8:]
        try:
            payload = json.dumps({"model":self.model,"messages":self.ai_history,"stream":False}).encode()
            req = urllib.request.Request(f"{self.base_url}/api/chat", data=payload, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                ans = json.loads(r.read())["message"]["content"]
                self.ai_history.append({"role":"assistant","content":ans})
                return ans.strip()
        except Exception as e:
            return f"🌐 AI Error: {e}"
    def clear(self): self.ai_history = [self.ai_history[0]]

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

# === 5. ПОТОКИ (Асинхронность) ===

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

# === 6. ИНТЕРФЕЙС (Страницы) ===

class Sidebar(QFrame):
    nav_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(72)
        self.setStyleSheet("""
            #sidebar {
                background: #16161e;
                border-right: 1px solid #2a2a3a;
            }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 24, 0, 24)
        lay.setSpacing(8)
        
        logo = QLabel("🌟")
        logo.setFont(QFont("Segoe UI Emoji", 24))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedHeight(40)
        lay.addWidget(logo)
        lay.addSpacing(16)
        
        self.nav_btns = {}
        # ✅ ДОБАВЛЕНО: "about" в навигацию
        nav_items = [
            ("chat", "💬", "Чат"), 
            ("scripts", "🎬", "Сценарии"), 
            ("contacts", "📇", "Контакты"), 
            ("settings", "⚙️", "Настройки"),
            ("about", "ℹ️", "О программе")
        ]
        for nav_id, icon, tooltip in nav_items:
            btn = QToolButton()
            btn.setIcon(QIcon())
            btn.setText(icon)
            btn.setToolTip(tooltip)
            btn.setProperty("nav_id", nav_id)
            btn.setFixedHeight(48)
            btn.setFixedWidth(56)
            btn.setStyleSheet("""
                QToolButton { background: transparent; color: #a0a0b0; border: none; border-radius: 10px; font-size: 20px; }
                QToolButton:hover { background: #2a2a3a; color: #ffffff; }
                QToolButton:checked { background: #605cd8; color: #ffffff; }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(self._on_nav)
            lay.addWidget(btn)
            lay.addSpacing(4)
            self.nav_btns[nav_id] = btn
            
        self.nav_btns["chat"].setChecked(True)
        lay.addStretch()
        
        status = QLabel("●")
        status.setStyleSheet("color: #22c55e; font-size: 10px;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(status)
        
    def _on_nav(self):
        btn = self.sender()
        nav_id = btn.property("nav_id")
        for b in self.nav_btns.values(): b.setChecked(False)
        btn.setChecked(True)
        self.nav_changed.emit(nav_id)

class ChatPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setObjectName("chatArea")
        self.chat.setStyleSheet("""
            #chatArea { background: transparent; border: none; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 15px; padding: 20px; }
        """)
        lay.addWidget(self.chat, 1)
        
        self.status_indicator = StatusIndicator()
        lay.addWidget(self.status_indicator)
        
        inp_frame = QFrame()
        inp_frame.setObjectName("inputFrame")
        inp_frame.setStyleSheet("#inputFrame { background: #16161e; border-top: 1px solid #2a2a3a; padding: 16px 24px; }")
        inp_lay = QHBoxLayout(inp_frame)
        inp_lay.setContentsMargins(0, 0, 0, 0)
        inp_lay.setSpacing(12)
        
        self.inp = FluentInput("Напишите команду или вопрос...")
        inp_lay.addWidget(self.inp, 1)
        
        self.send_btn = FluentButton("➤", accent=True)
        self.send_btn.setFixedWidth(50)
        inp_lay.addWidget(self.send_btn)
        
        self.voice_btn = FluentButton("🎤")
        self.voice_btn.setFixedWidth(50)
        inp_lay.addWidget(self.voice_btn)
        
        lay.addWidget(inp_frame)

class ScriptPanel(QFrame):
    run_signal = pyqtSignal(str)
    create_signal = pyqtSignal()
    
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(20)
        
        title = QLabel("🎬 Сценарии")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        lay.addWidget(title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        self.content_lay = QVBoxLayout(self.content)
        self.content_lay.setSpacing(12)
        lay.addWidget(self.scroll, 1)
        
        add_btn = FluentButton("+ Создать сценарий", accent=True)
        add_btn.clicked.connect(lambda: self.create_signal.emit())
        lay.addWidget(add_btn)
        self.refresh_scripts()
        
    def refresh_scripts(self):
        while self.content_lay.count():
            w = self.content_lay.takeAt(0).widget()
            if w: w.deleteLater()
        scripts = self.cfg.get("scripts", {})
        if not scripts:
            empty = QLabel("Нет сценариев. Создайте первый!")
            empty.setStyleSheet("color: #808090; padding: 40px; text-align: center;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_lay.addWidget(empty)
            return
        for name, cmds in scripts.items():
            card = FluentCard()
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(20, 16, 20, 16)
            header = QHBoxLayout()
            h = QLabel(f"📋 {name}")
            h.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            h.setStyleSheet("color: #ffffff;")
            header.addWidget(h)
            header.addStretch()
            run_btn = FluentButton("▶", accent=True)
            run_btn.setFixedWidth(80)
            run_btn.clicked.connect(lambda checked, n=name: self.run_signal.emit(n))
            header.addWidget(run_btn)
            del_btn = FluentButton("✕")
            del_btn.setFixedWidth(40)
            del_btn.setStyleSheet("QPushButton { background: #3a2a3a; color: #ff6b6b; } QPushButton:hover { background: #4a3a4a; }")
            del_btn.clicked.connect(lambda checked, n=name: self._delete_script(n))
            header.addWidget(del_btn)
            card_lay.addLayout(header)
            steps = QLabel(f"{len(cmds)} шагов")
            steps.setStyleSheet("color: #808090; font-size: 13px;")
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
        lay = QVBoxLayout(self)
        lay.setContentsMargins(60, 60, 60, 60)
        lay.setSpacing(32)
        
        title = QLabel("📇 Контакты")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        lay.addWidget(title)
        
        tg_card = FluentCard()
        tg_lay = QHBoxLayout(tg_card)
        tg_lay.setContentsMargins(24, 20, 24, 20)
        tg_icon = QLabel("✈️")
        tg_icon.setFont(QFont("Segoe UI Emoji", 28))
        tg_lay.addWidget(tg_icon)
        tg_info = QVBoxLayout()
        tg_label = QLabel("Telegram")
        tg_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        tg_label.setStyleSheet("color: #ffffff;")
        tg_value = QLabel(config.get("contacts", {}).get("telegram", "@CayPlay78"))
        tg_value.setFont(QFont("Consolas", 14))
        tg_value.setStyleSheet("color: #605cd8;")
        tg_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        tg_info.addWidget(tg_label)
        tg_info.addWidget(tg_value)
        tg_lay.addLayout(tg_info)
        tg_lay.addStretch()
        tg_copy = FluentButton("📋 Копировать")
        tg_copy.clicked.connect(lambda: self._copy(config.get("contacts", {}).get("telegram", "@CayPlay78")))
        tg_lay.addWidget(tg_copy)
        tg_open = FluentButton("↗ Открыть", accent=True)
        tg_open.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/CayPlay78")))
        tg_lay.addWidget(tg_open)
        lay.addWidget(tg_card)
        
        vk_card = FluentCard()
        vk_lay = QHBoxLayout(vk_card)
        vk_lay.setContentsMargins(24, 20, 24, 20)
        vk_icon = QLabel("🔵")
        vk_icon.setFont(QFont("Segoe UI Emoji", 28))
        vk_lay.addWidget(vk_icon)
        vk_info = QVBoxLayout()
        vk_label = QLabel("ВКонтакте")
        vk_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        vk_label.setStyleSheet("color: #ffffff;")
        vk_value = QLabel(config.get("contacts", {}).get("vk", "https://m.vk.com/cayplay"))
        vk_value.setFont(QFont("Consolas", 13))
        vk_value.setStyleSheet("color: #605cd8;")
        vk_value.setWordWrap(True)
        vk_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        vk_info.addWidget(vk_label)
        vk_info.addWidget(vk_value)
        vk_lay.addLayout(vk_info)
        vk_lay.addStretch()
        vk_copy = FluentButton("📋 Копировать")
        vk_copy.clicked.connect(lambda: self._copy(config.get("contacts", {}).get("vk", "https://m.vk.com/cayplay")))
        vk_lay.addWidget(vk_copy)
        vk_open = FluentButton("↗ Открыть", accent=True)
        vk_open.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(config.get("contacts", {}).get("vk", "https://m.vk.com/cayplay"))))
        vk_lay.addWidget(vk_open)
        lay.addWidget(vk_card)
        lay.addStretch()
        
    def _copy(self, text: str):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Скопировано", f"✅ {text}\nскопирован в буфер обмена")

class SettingsPanel(QFrame):
    def __init__(self, config: Dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(24)
        
        title = QLabel("⚙️ Настройки")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        lay.addWidget(title)
        
        self.labels = {}
        for k in ["ai", "voice", "steam"]:
            card = FluentCard()
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(24, 20, 24, 20)
            t = QLabel(k.upper())
            t.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            t.setStyleSheet("color: #ffffff;")
            c_lay.addWidget(t)
            lbl = QLabel("Загрузка...")
            lbl.setObjectName("statusLabel")
            lbl.setStyleSheet("#statusLabel { color: #e0e0e0; font-family: Consolas; font-size: 14px; }")
            c_lay.addWidget(lbl)
            self.labels[k] = lbl
            lay.addWidget(card)
        lay.addStretch()
        
    def update_ui(self, ai_ok: bool, voice_ok: bool, steam_path: Optional[str]):
        self.labels["ai"].setText(f"{'✅' if ai_ok else '❌'} Ollama: {self.cfg['ai']['model']}")
        self.labels["ai"].setStyleSheet(f"color: {'#34d399' if ai_ok else '#f87171'}; font-family: Consolas; font-size: 14px;")
        self.labels["voice"].setText(f"{'✅' if voice_ok else '❌'} Микрофон")
        self.labels["voice"].setStyleSheet(f"color: {'#34d399' if voice_ok else '#f87171'}; font-family: Consolas; font-size: 14px;")
        self.labels["steam"].setText(f"{'✅' if steam_path else '❌'} Steam: {steam_path or 'Не найден'}")
        self.labels["steam"].setStyleSheet(f"color: {'#34d399' if steam_path else '#f87171'}; font-family: Consolas; font-size: 14px;")

# === 7. О ПРОГРАММЕ (About Panel) ===
class AboutPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = FluentCard()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(50, 50, 50, 50)
        card_lay.setSpacing(16)
        card_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel("🌟")
        logo.setFont(QFont("Segoe UI Emoji", 48))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(logo)

        title = QLabel("MIRA")
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(title)

        version = QLabel("Версия 11.0 | Ultimate Stable")
        version.setFont(QFont("Consolas", 13))
        version.setStyleSheet("color: #605cd8;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(version)

        desc = QLabel("Локальный ИИ-ассистент для полного контроля над вашим ПК.\nГолос, текст, сценарии, поиск в интернете и запуск любых приложений.")
        desc.setFont(QFont("Segoe UI", 14))
        desc.setStyleSheet("color: #a0a0b0;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        card_lay.addWidget(desc)

        card_lay.addSpacing(12)

        copyright = QLabel("© CayPlay 2026. Все права защищены.")
        copyright.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        copyright.setStyleSheet("color: #6b7280;")
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(copyright)

        btns_lay = QHBoxLayout()
        btns_lay.addStretch()
        btns_lay.setSpacing(12)
        
        gh_btn = FluentButton("🐙 GitHub")
        gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com")))
        tg_btn = FluentButton("✈️ Telegram", accent=True)
        tg_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/CayPlay78")))
        
        btns_lay.addWidget(gh_btn)
        btns_lay.addWidget(tg_btn)
        btns_lay.addStretch()
        card_lay.addLayout(btns_lay)

        lay.addWidget(card, 0, Qt.AlignmentFlag.AlignCenter)

# === 8. ГЛАВНОЕ ОКНО ===

class MIRAWindow(QMainWindow):
    voice_signal = pyqtSignal(str)
    nav_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.executor = SystemExecutor(self.cfg)
        self.ai = AIManager(self.cfg)
        self.voice = VoiceManager(self.cfg)
        
        self.voice_signal.connect(self._on_voice)
        self.active_threads = []
        
        self._setup_ui()
        self._apply_styles()
        self._init_tray()
        
        self.showFullScreen()
        QTimer.singleShot(200, self._boot)

    def _setup_ui(self):
        self.setWindowTitle("MIRA")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # ✅ ЕДИНЫЙ корневой лейаут для всего окна
        central = QWidget()
        self.setCentralWidget(central)
        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)
        
        # 1. Title Bar
        self.title_bar = QFrame()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(32)
        title_lay = QHBoxLayout(self.title_bar)
        title_lay.setContentsMargins(16, 0, 16, 0)
        self.title_label = QLabel("💬 Чат")
        self.title_label.setObjectName("titleLabel")
        title_lay.addWidget(self.title_label)
        title_lay.addStretch()
        for txt, func in [("─", self.showMinimized), ("□", self._toggle_maximize), ("✕", self.close)]:
            b = QPushButton(txt)
            b.setObjectName("titleBtn")
            b.clicked.connect(func)
            b.setFixedWidth(36)
            title_lay.addWidget(b)
        root_lay.addWidget(self.title_bar)
        
        # 2. Контент (Sidebar + Pages)
        content_widget = QWidget()
        content_lay = QHBoxLayout(content_widget)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)
        
        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self._switch_page)
        content_lay.addWidget(self.sidebar)
        
        self.stacked = QStackedWidget()
        self.stacked.setObjectName("mainStack")
        
        self.chat_panel = ChatPanel()
        self.chat_panel.send_btn.clicked.connect(self._process)
        self.chat_panel.inp.returnPressed.connect(self._process)
        self.chat_panel.voice_btn.clicked.connect(self._toggle_voice)
        self.stacked.addWidget(self.chat_panel)
        
        self.script_panel = ScriptPanel(self.cfg)
        self.script_panel.run_signal.connect(self._run_script)
        self.script_panel.create_signal.connect(self._create_script_dialog)
        self.stacked.addWidget(self.script_panel)
        
        self.contacts_panel = ContactsPanel(self.cfg)
        self.stacked.addWidget(self.contacts_panel)
        
        self.settings_panel = SettingsPanel(self.cfg)
        self.stacked.addWidget(self.settings_panel)
        
        # ✅ ДОБАВЛЕНО: Панель "О программе"
        self.about_panel = AboutPanel()
        self.stacked.addWidget(self.about_panel)
        
        content_lay.addWidget(self.stacked, 1)
        root_lay.addWidget(content_widget, 1)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #0f0f1a; }
            #titleBar { background: #16161e; border-bottom: 1px solid #2a2a3a; }
            #titleLabel { color: #a0a0b0; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            #titleBtn { background: transparent; color: #6b7280; border: none; font-family: 'Segoe UI', sans-serif; font-size: 14px; border-radius: 4px; }
            #titleBtn:hover { background: #2a2a3a; color: #ffffff; }
            #mainStack { background: #0f0f1a; }
        """)

    def _init_tray(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(pixmap)
        p.setBrush(QColor(96, 92, 216))
        p.drawRoundedRect(0, 0, 32, 32, 8, 8)
        p.setPen(Qt.GlobalColor.white)
        p.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        p.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M")
        p.end()
        self.tray = QSystemTrayIcon(QIcon(pixmap), self)
        self.tray.setToolTip("MIRA — AI Ассистент")
        
        m = QMenu()
        
        # ✅ Кнопка ОТКРЫТЬ
        action_open = QAction("🔍 Открыть", self)
        action_open.triggered.connect(self._restore_window)
        m.addAction(action_open)
        
        m.addSeparator()
        
        # ✅ ДОБАВЛЕНО: Пункт "О программе" в трее
        action_about = QAction("ℹ️ О программе", self)
        action_about.triggered.connect(lambda: (self._restore_window(), self._switch_page("about")))
        m.addAction(action_about)
        
        # ✅ Кнопка ВЫХОД
        action_exit = QAction("❌ Выход", self)
        action_exit.triggered.connect(self._full_exit)
        m.addAction(action_exit)
        
        self.tray.setContextMenu(m)
        self.tray.activated.connect(lambda reason: self._restore_window() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()

    def _restore_window(self):
        """Восстанавливает и поднимает окно на передний план"""
        if self.isMinimized():
            self.showNormal()
        elif not self.isVisible():
            self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()

    def _full_exit(self):
        """Полное закрытие приложения"""
        self.tray.hide()
        for thread in self.active_threads:
            if thread.isRunning():
                thread.terminate()
        sys.exit(0)

    def _toggle_maximize(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    def _switch_page(self, page: str):
        titles = {
            "chat": "💬 Чат", 
            "scripts": "🎬 Сценарии", 
            "contacts": "📇 Контакты", 
            "settings": "⚙️ Настройки", 
            "about": "ℹ️ О программе"  # ✅ ДОБАВЛЕНО
        }
        page_widget = {
            "chat": self.chat_panel, 
            "scripts": self.script_panel, 
            "contacts": self.contacts_panel, 
            "settings": self.settings_panel,
            "about": self.about_panel  # ✅ ДОБАВЛЕНО
        }.get(page, self.chat_panel)
        self.stacked.setCurrentWidget(page_widget)

    def _boot(self):
        self._add_bubble("ai", "Система активна. Голос, текст, сценарии, поиск в интернете, запуск любых игр.")
        self.settings_panel.update_ui(self.ai.ai_available, self.voice.mic is not None, self.executor.resolver.steam_path)

    def _cleanup_thread(self, thread):
        if thread in self.active_threads:
            self.active_threads.remove(thread)
        thread.deleteLater()

    def _start_worker(self, worker):
        worker.finished.connect(lambda: self._cleanup_thread(worker))
        self.active_threads.append(worker)
        worker.start()

    def _resolve_command(self, text: str) -> tuple[Optional[str], bool]:
        clean = text.lower().strip(".,!?;:- \"'")
        search_patterns = [
            r'найди в интернете\s+(.+)', r'погугли\s+(.+)', r'яндекси\s+(.+)', r'поиск в (яндекс|google|гугл)\s+(.+)'
        ]
        for pattern in search_patterns:
            match = re.match(pattern, clean)
            if match:
                query = match.group(1).strip()
                engine = "yandex"
                if "гугл" in clean or "google" in clean: engine = "google"
                elif "duck" in clean: engine = "duckduckgo"
                return f"SEARCH:{query}", True
        
        cmd = clean
        for verb in ["открой", "запусти", "включи", "покажи", "открыть", "запустить", "включить"]:
            if cmd.startswith(verb):
                cmd = cmd.replace(verb, "").strip()
                break
        
        if cmd in self.executor.resolver.aliases: return self.executor.resolver.aliases[cmd], False
        for alias, exe in self.executor.resolver.aliases.items():
            if alias in cmd or cmd in alias: return exe, False
        
        question_words = ["привет", "здравствуй", "как дела", "что ты умеешь", "кто ты", "помоги", "спасибо", "пока", "до свидания", "расскажи", "объясни", "почему", "как", "что", "где", "когда", "зачем"]
        if any(qw in cmd for qw in question_words): return None, False
        
        resolved = self.executor.resolver.resolve(cmd)
        if resolved and (shutil.which(resolved) or Path(resolved).exists() or resolved.startswith("steam://")):
            return resolved, False
        return None, False

    def _add_bubble(self, role: str, text: str):
        colors = {"user": "#60a5fa", "ai": "#34d399", "sys": "#fbbf24", "success": "#34d399", "error": "#f87171"}
        align = "right" if role == "user" else "left"
        bg_map = {"user": "rgba(96,165,250,0.15)", "ai": "rgba(52,211,153,0.12)", "sys": "rgba(251,191,36,0.12)", "success": "rgba(52,211,153,0.15)", "error": "rgba(248,113,113,0.15)"}
        bg = bg_map.get(role, "rgba(52,211,153,0.12)")
        c = colors.get(role, "#34d399")
        html = f"""
        <div style='text-align:{align}; margin:12px 0;'>
            <span style='background:{bg}; padding:14px 18px; border-radius:14px; display:inline-block; max-width:75%; box-shadow: 0 2px 8px rgba(0,0,0,0.2);'>
                <b style='color:{c}; font-weight:600;'>{role.upper()}</b><br>
                {text.replace('<','&lt;').replace('>','&gt;').replace(chr(10),'<br>')}
            </span>
        </div>
        """
        self.chat_panel.chat.append(html)
        self.chat_panel.chat.verticalScrollBar().setValue(self.chat_panel.chat.verticalScrollBar().maximum())

    def _process(self):
        txt = self.chat_panel.inp.text().strip()
        if not txt: return
        self.chat_panel.inp.clear()
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
            if "покажи сценарии" in clean:
                scripts = self.cfg.get("scripts", {})
                msg = "📋 Сценарии:\n" + "\n".join(f"• {n} ({len(c)} шагов)" for n,c in scripts.items()) if scripts else "📋 Нет сценариев"
                self._add_bubble("ai", msg)
                return
                
            for cmd in self.cfg.get("commands", []):
                trig = cmd.get("trigger", "")
                if trig and trig in clean:
                    self._execute_cmd(cmd["action"], cmd.get("type", "app"))
                    return
                    
            resolved, is_search = self._resolve_command(clean)
            
            if is_search and resolved:
                self.chat_panel.status_indicator.set_active(True)
                self._add_bubble("sys", f"🔍 Поиск: {resolved.replace('SEARCH:','')}")
                worker = CmdWorker(self.executor, resolved, "search")
                worker.result.connect(self._on_cmd_result)
                self._start_worker(worker)
                
            elif resolved:
                self.chat_panel.status_indicator.set_active(True)
                self._add_bubble("sys", f"🔍 Ищу: {resolved}")
                worker = CmdWorker(self.executor, resolved, "auto")
                worker.result.connect(self._on_cmd_result)
                self._start_worker(worker)
                
            else:
                self.chat_panel.status_indicator.set_active(True)
                self._add_bubble("ai", "🤖 Думаю...")
                worker = AIWorker(self.ai, text)
                worker.result.connect(self._on_ai_result)
                self._start_worker(worker)
                
        except Exception as e:
            self._add_bubble("error", f"❌ {e}")

    def _on_cmd_result(self, result: str):
        self.chat_panel.status_indicator.set_active(False)
        self._add_bubble("success" if "✅" in result else "error", result)
        self.voice.speak("Готово")

    def _on_ai_result(self, result: str):
        self.chat_panel.status_indicator.set_active(False)
        self._add_bubble("ai", result)
        self.voice.speak("Ответ получен")

    def _execute_cmd(self, cmd: str, ctype: str):
        self.chat_panel.status_indicator.set_active(True)
        worker = CmdWorker(self.executor, cmd, ctype)
        worker.result.connect(self._on_cmd_result)
        self._start_worker(worker)

    def _run_script(self, name: str):
        scripts = self.cfg.get("scripts", {})
        if name not in scripts:
            self._add_bubble("error", f"❌ '{name}' не найден")
            return
        cmds = scripts[name]
        self._add_bubble("ai", f"🎬 Запуск '{name}' ({len(cmds)} шагов)...")
        
        worker = ScriptWorker(self.executor, name, cmds)
        worker.progress.connect(lambda i, t, c: self._add_bubble("sys", f"⏳ {i}/{t}: {c}"))
        worker.finished.connect(lambda n: (self._add_bubble("success", f"✅ '{n}' завершён"), self.voice.speak("Сценарий выполнен")))
        self._start_worker(worker)

    def _create_script_dialog(self, pre_name: str = ""):
        dlg = QDialog(self)
        dlg.setWindowTitle("🎬 Новый сценарий")
        dlg.resize(520, 420)
        dlg.setStyleSheet("""
            QDialog { background: #16161e; color: #e0e0e0; }
            QLabel { font-weight: bold; color: #605cd8; font-family: 'Segoe UI'; }
            QLineEdit, QPlainTextEdit { background: #1e1e2a; border: 1px solid #3a3a4a; border-radius: 8px; padding: 10px; color: #fff; font-family: Consolas; }
            QPushButton { background: #605cd8; color: #fff; border: none; border-radius: 8px; padding: 12px 24px; font-family: 'Segoe UI'; font-weight: bold; }
            QPushButton:hover { background: #7470e8; }
        """)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        
        lay.addWidget(QLabel("📝 Название:"))
        name_in = QLineEdit(pre_name)
        lay.addWidget(name_in)
        
        lay.addWidget(QLabel("📋 Команды (каждая с новой строки):"))
        cmd_in = QPlainTextEdit()
        cmd_in.setPlaceholderText("obs64.exe\nnotepad.exe\nsteam://run/730")
        lay.addWidget(cmd_in)
        
        btns = QHBoxLayout()
        save = FluentButton("💾 Сохранить", accent=True)
        save.clicked.connect(dlg.accept)
        cancel = FluentButton("❌ Отмена")
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        lay.addLayout(btns)
        
        if dlg.exec() == 1:
            nm = name_in.text().strip()
            cmds = [l.strip() for l in cmd_in.toPlainText().split('\n') if l.strip()]
            if not nm: return
            self.cfg.setdefault("scripts", {})[nm] = cmds
            save_config(self.cfg)
            self._add_bubble("success", f"✅ '{nm}' сохранён ({len(cmds)} шагов)")
            if hasattr(self, 'script_panel'):
                self.script_panel.refresh_scripts()

    def _on_voice(self, txt: str):
        if not txt:
            self.chat_panel.status_indicator.set_active(False)
            return
        self._add_bubble("user", f"🎤 {txt}")
        QTimer.singleShot(10, lambda: self._route(txt))
        self.chat_panel.status_indicator.set_active(False)

    def _toggle_voice(self):
        if not self.voice.mic:
            self._add_bubble("error", "❌ Микрофон не найден")
            return
        self.chat_panel.status_indicator.set_active(True)
        self._add_bubble("sys", "🎤 Слушаю...")
        
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
            "Ассистент свернут в трей. Нажмите дважды для открытия.", 
            QSystemTrayIcon.MessageIcon.Information, 
            2000
        )
        event.ignore()

# === 8. ЗАПУСК ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    win = MIRAWindow()
    win.show()
    sys.exit(app.exec())
