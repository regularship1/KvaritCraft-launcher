import os
import shutil
import subprocess
import time
import traceback
from pathlib import Path
import sys
import tomllib
from threading import Thread
from tkinter.filedialog import askdirectory
from zipfile import ZipFile
import minecraft_launcher_lib
import psutil
import requests
import tomli_w
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
from customtkinter import CTkProgressBar, CTkSlider, CTkLabel, BooleanVar, CTkCheckBox, CTk, CTkButton, CTkFrame, CTkTabview, CTkTextbox, IntVar, CTkToplevel
from regularlib.misc import copyDirWithProgress, deleteDirWithProgress, normalizeN, mcOfflineUUID

if getattr(sys, "_MEIPASS", False):
    os.chdir(sys._MEIPASS)
SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SRC)
VERSION = "2.0"
ctk.set_default_color_theme(r"assets\themes\maintheme.json")
Window = CTk()
Window.geometry(f"1280x720+{Window.winfo_screenwidth()//2-640}+{Window.winfo_screenheight()//2-360}")
Window.title(f"KvaritCraft launcher v.{VERSION}")
Window.iconbitmap(True, os.path.join(SRC, r"assets\images\icon.ico"))
Window.resizable(False, False)

def liftFrameDown(frame, y=-750):
    if y < 0:
        frame.place(x=0, y=y)
        Window.after(10, liftFrameDown, frame, y + 30)
    else: frame.place(x=0, y=0)
    if y == -750: frame.lift()

def checkupdates():
    liftFrameDown(mcProgressframe)
    progresstext.configure(True, text="Проверка обновлений")
    progressdesc.configure(True, text="Получение метаданных")
    while True:
        try:
            with requests.get("https://raw.githubusercontent.com/regularship1/KvaritCraft-launcher/refs/heads/main/updates.toml", stream=True) as r:
                r.raise_for_status()
                _max = int(r.headers.get("Content-Length"))
                progressbar.set(0)
                with open(str(temp / "updates.toml"), "wb") as f:
                    for chunk in r.iter_content(chunk_size=1048576):
                        if chunk:
                            f.write(chunk)
                            progressbar.set(progressbar.get() + normalizeN(len(chunk), 0, _max))
                            Window.update_idletasks()
        except BaseException:
            liftFrameDown(console)
            traceback.print_exc()
            continue
        break
    updates = tomllib.load((temp / "updates.toml").open("rb"))
    if os.path.basename(sys.executable) not in ("pythonw.exe", "python.exe") and VERSION != updates["launcher_version"]:
        progresstext.configure(True, text="Обновление лаунчера")
        progressdesc.configure(True, text="Скачивание установщика")
        while True:
            try:
                with requests.get(f"https://github.com/regularship1/KvaritCraft-launcher/releases/download/Latest/Kvaritcraft.exe", stream=True) as r:
                    r.raise_for_status()
                    _max = int(r.headers.get("Content-Length"))
                    progressbar.set(0)
                    with open(temp / "KvaritcraftSetup.exe", "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar.set(progressbar.get() + normalizeN(len(chunk), 0, _max))
                                Window.update_idletasks()
            except BaseException:
                liftFrameDown(console)
                traceback.print_exc()
                continue
            break
        try: subprocess.Popen(str(temp / "KvaritcraftSetup.exe"), creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        except BaseException:
            liftFrameDown(console)
            traceback.print_exc()
        try:
            Window.destroy()
            sys.exit()
        except BaseException: pass
    version = tomllib.loads((instanceFP / "version.txt").read_text()) if (instanceFP / "version.txt").exists() else {"mc_version": "", "mc_core_version": ""}
    if version["mc_core_version"] != updates["mc_core_version"] and (instanceFP / "version.txt").exists():
        progresstext.configure(True, text="Обновление игры")
        progressdesc.configure(True, text="Скачивание zip-архива")
        while True:
            try:
                with requests.get("https://drive.usercontent.google.com/download?confirm=t&id=1MZV4I8FYikmPB4KN4Tc6fwIrFpGIkdIo&export=download", stream=True) as r:
                    r.raise_for_status()
                    _max = int(r.headers.get("Content-Length"))
                    progressbar.set(0)
                    with open(str(temp / "minecraft.zip"), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar.set(progressbar.get() + normalizeN(len(chunk), 0, _max))
                                Window.update_idletasks()
            except BaseException:
                liftFrameDown(console)
                traceback.print_exc()
                continue
            break
        time.sleep(1)
        progressdesc.configure(True, text="Отчистка папки")
        try: shutil.rmtree(str(instanceFP))
        except PermissionError: pass
        except BaseException:
            liftFrameDown(console)
            traceback.print_exc()
        with ZipFile(str(temp / "minecraft.zip"), "r") as z:
            files = z.namelist()
            _max = len(files)
            progressbar.set(0)
            for i, filename in enumerate(files):
                progressdesc.configure(True, text=f"Распаковка {filename}")
                z.extract(filename, config["instancedir"])
                progressbar.set(normalizeN(i, 0, _max))
                Window.update_idletasks()
        version["mc_version"] = ""
    if version["mc_version"] != updates["mc_version"] and (instanceFP / "version.txt").exists():
        progresstext.configure(True, text="Обновление модов")
        progressdesc.configure(True, text="Скачивание zip-архива")
        while True:
            try:
                with requests.get("https://drive.usercontent.google.com/download?confirm=t&id=1yx7EeZOsS_764YDznrGRQiO3uPqNhV8q&export=download", stream=True) as r:
                    r.raise_for_status()
                    _max = int(r.headers.get("Content-Length"))
                    progressbar.set(0)
                    with open(str(temp / "mods.zip"), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar.set(progressbar.get() + len(chunk))
                                Window.update_idletasks()
            except BaseException:
                liftFrameDown(console)
                traceback.print_exc()
                continue
            break
        progressdesc.configure(True, text="Отчистка папки")
        try:
            if (instanceFP / "mods").exists(): shutil.rmtree(str(instanceFP / "mods"))
        except BaseException:
            liftFrameDown(console)
            traceback.print_exc()
        with ZipFile(str(temp / "mods.zip"), "r") as z:
            files = z.namelist()
            _max = len(files)
            progressbar.set(0)
            for i, filename in enumerate(files):
                if filename.startswith("config/") and (instanceFP / "config").exists(): progressdesc["text"] = progressdesc.configure(True, text=f"Пропускаю распаковку {filename}")
                else:
                    progressdesc.configure(True, text=f"Распаковка {filename}")
                    z.extract(filename, config["instancedir"])
                progressbar.set(normalizeN(i, 0, _max))
                Window.update_idletasks()
    liftFrameDown(mainscreen)

laucherootFP = Path(os.getenv("APPDATA")) / "regularship1" / "kvaritcraft"
cfgFP = laucherootFP / "config.toml"

class InputDialog(ctk.CTkToplevel):
    def __init__(self, master, title, placeholder):
        super().__init__(master)
        self.title(title)
        self.geometry("300x150")
        self.result = None
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.pack(padx=20, pady=20, fill="x")
        btn = ctk.CTkButton(self, text="OK", command=self.ok)
        btn.pack(pady=10)
    def ok(self):
        self.result = self.entry.get()
        self.destroy()
def askSTR(master, title, placeholder) -> str:
    dialog = InputDialog(Window, title, placeholder)
    master.wait_window(dialog)
    return dialog.result
if not laucherootFP.exists(): laucherootFP.mkdir(parents=True)

if not cfgFP.exists():
    nick = ""
    while nick == "": nick = askSTR(Window, "Ваш внутриигровой ник", "Введите ваш внутриигровой ник")
    config = dict(instancedir=str(laucherootFP / "minecraft"), instancemem=5, instancequickplay=True, playernick=nick)
    tomli_w.dump(config, cfgFP.open("wb"))
config = tomllib.load(cfgFP.open("rb"))
def changeNick():
    nick = ""
    while nick == "": nick = askSTR(Window, "Ваш внутриигровой ник", "Введите ваш внутриигровой ник")
    config["playernick"] = nick
    currentNickLbl.configure(True, text="Текущий ник: " + config["playernick"])
    tomli_w.dump(config, cfgFP.open("wb"))

instanceFP = Path(config["instancedir"])
temp = Path(os.getenv("LOCALAPPDATA")) / "Temp"

def liftFrameUp(frame, y=720):
    if y > 0:
        frame.place(x=0, y=y)
        Window.after(10, liftFrameUp, frame, y - 30)
    else: frame.place(x=0, y=720)
    if y == 720: frame.lift()

def changeInstanceDir():
    newdir = askdirectory(title="Выберите папку", initialdir=config["instancedir"])
    msg = CTkMessagebox(title="Вопрос", message="Переносить содержимое прошлой папки?", icon="question", option_1="Нет", option_2="Да")
    response = msg.get()
    if response == "Да":
        liftFrameDown(mcProgressframe)
        progresstext.configure(True, text="Перенос майнкрафта")
        progressdesc.configure(True, text="Копирование в новое место")
        Window.update()
        def callback(progress, total):
            progressbar.set(normalizeN(progress, 0, total))
            Window.update()
        copyDirWithProgress(config["instancedir"], newdir, callback)
        progressdesc.configure(True, text="Удаление старой папки")
        deleteDirWithProgress(config["instancedir"], callback)
        liftFrameDown(settings)
    config["instancedir"] = newdir
    tomli_w.dump(config, cfgFP.open("wb"))

def installinstance():
    if not (instanceFP / "version.txt").exists():
        progresstext.configure(True, text="Установка майнкрафта")
        progressdesc.configure(True, text="Скачивание zip-архива")
        while True:
            try:
                with requests.get("https://drive.usercontent.google.com/download?confirm=t&id=1MZV4I8FYikmPB4KN4Tc6fwIrFpGIkdIo&export=download", stream=True) as r:
                    r.raise_for_status()
                    _max = int(r.headers.get("Content-Length"))
                    progressbar.set(0)
                    Window.update_idletasks()
                    with open(str(temp / "minecraft.zip"), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar.set(progressbar.get() + normalizeN(len(chunk), 0, _max))
                                Window.update_idletasks()
            except BaseException:
                liftFrameDown(console)
                traceback.print_exc()
                continue
            break
        progresstext.configure(True, text="Установка майнкрафта")
        with ZipFile(str(temp / "minecraft.zip"), "r") as z:
            files = z.namelist()
            _max = len(files)
            progressbar.set(0)
            Window.update_idletasks()
            for i, filename in enumerate(files):
                z.extract(filename, config["instancedir"])
                progressbar.set(normalizeN(i, 0, _max))
                progressdesc.configure(True, text=f"Распаковка {filename}")
                Window.update_idletasks()
    if not os.path.exists(str(instanceFP / "mods")) or not os.listdir(str(instanceFP / "mods")):
        progresstext.configure(True, text="Установка модов")
        progressdesc.configure(True, text="Скачивание zip-архива")
        while True:
            try:
                with requests.get("https://drive.usercontent.google.com/download?confirm=t&id=1yx7EeZOsS_764YDznrGRQiO3uPqNhV8q&export=download", stream=True) as r:
                    r.raise_for_status()
                    _max = int(r.headers.get("Content-Length"))
                    progressbar.set(0)
                    with open(str(temp / "mods.zip"), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar.set(progressbar.get() + normalizeN(len(chunk), 0, _max))
                                Window.update_idletasks()
            except BaseException:
                liftFrameDown(console)
                traceback.print_exc()
                continue
            break
        progresstext.configure(True, text="Установка игры")
        with ZipFile(str(temp / "mods.zip"), "r") as z:
            files = z.namelist()
            _max = len(files)
            progressbar.set(0)
            for i, filename in enumerate(files):
                z.extract(filename, config["instancedir"])
                progressbar.set(normalizeN(i, 0, _max))
                progressdesc.configure(True, text=f"Распаковка {filename}")
                Window.update_idletasks()
def launchinstance():
    print("Запуск сборки")
    liftFrameDown(mcProgressframe)
    installinstance()
    mainscreen.lift()
    liftFrameDown(console)
    version = tomllib.loads((instanceFP / "version.txt").read_text())
    cmd = minecraft_launcher_lib.command.get_minecraft_command(
        version["mc_core_version"],
        config["instancedir"],
        {
            "username": config["playernick"],
            "uuid": str(mcOfflineUUID(config["playernick"], "KvaritcraftPlayer")),
            "token": "",
            "jvmArguments": [f"-Xmx{config["instancemem"]}G", "-Xms3G"],
        }
    )
    if config["instancequickplay"]: cmd += ["--quickPlayMultiplayer", "kvaritcraft.mclan.ru"]
    proc = subprocess.Popen(**{"args": cmd, "cwd": config["instancedir"], "stdout":subprocess.PIPE, "stderr":subprocess.STDOUT, "bufsize":1, "text": True, "errors":"replace", "creationflags":subprocess.CREATE_NO_WINDOW,})
    mcstd = constd(mccon)
    Window.update_idletasks()
    for line in proc.stdout: print(line, file=mcstd, end="")
bgImg = ctk.CTkImage(light_image=Image.open(os.path.join(SRC, r"assets\images\bg.png")), size=(1280, 720))
logoImg = ctk.CTkImage(light_image=Image.open(os.path.join(SRC, r"assets\images\logo.png")), size=(700, 100))
telegramImg = ctk.CTkImage(light_image=Image.open(os.path.join(SRC, r"assets\images\telegram.png")))
githubImg = ctk.CTkImage(light_image=Image.open(os.path.join(SRC, r"assets\images\github.png")))
consoleImg = ctk.CTkImage(light_image=Image.open(os.path.join(SRC, r"assets\images\console.png")))
tabs = CTkFrame(Window)
tabs.place(x=0, y=0, relwidth=1, relheight=1)
console = CTkFrame(tabs)
mainscreen = CTkFrame(tabs)
settings = CTkFrame(tabs)
mcProgressframe = CTkFrame(tabs)
#console
consoles = CTkTabview(console)
consoles.add("Лаунчер")
consoles.add("Майнкрафт")
globalconframe = CTkFrame(consoles.tab("Лаунчер"))
globalcon = CTkTextbox(globalconframe, state="disabled", wrap="none")
globalcon.pack(expand=True, fill="both")
class constd:
    def __init__(self, con): self.con = con
    def write(self, text):
        autoscroll = self.con.yview()[1] >= 0.999
        self.con.configure(state="normal")
        self.con.insert("end", text)
        self.con.configure(state="disabled")
        if autoscroll: self.con.see("end")
    def flush(self): pass
sys.stdout = constd(globalcon)
sys.stderr = constd(globalcon)
mcconframe = CTkFrame(consoles.tab("Майнкрафт"))
mccon = CTkTextbox(mcconframe, state="disabled", wrap="none")
mccon.pack(expand=True, fill="both")
consoles.place(x=0, y=0, relwidth=1, relheight=1)
conback = CTkButton(console, text="Назад", command=lambda: liftFrameDown(tabs.winfo_children()[-2]), cursor="hand2")
conback.place(x=0, y=0)
console.place(x=0, y=0, relwidth=1, relheight=1)
print("Привет! Я Мита!")
#mainscreen
bg = CTkLabel(mainscreen, image=bgImg, text="")
bg.image = bgImg
bg.place(x=0, y=0, relwidth=1, relheight=1)
play = CTkButton(mainscreen, text="Играть", cursor="hand2", command=lambda: Thread(target=launchinstance, daemon=True).start())
play.place(x=10, y=600)
gosettings = CTkButton(mainscreen, text="Настройки", cursor="hand2", command=lambda: liftFrameDown(settings))
gosettings.place(x=10, y=650)
logo = CTkLabel(mainscreen, image=logoImg, text="")
logo.place(x=300, y=150)
globalconframe.pack(fill="both", expand=True)
mcconframe.pack(fill="both", expand=True)
mainscreen.place(x=0, y=0, relwidth=1, relheight=1)
mainscreen.lift()
#settings
def saveSettings(*_):
    config["instancemem"] = settingsRAMVar.get()
    config["instancequickplay"] = settingsAutoJoinVar.get()
    tomli_w.dump(config, cfgFP.open("wb"))
bg = CTkLabel(settings, image=bgImg, text="")
bg.image = bgImg
bg.place(x=0, y=0, relwidth=1, relheight=1)
settingsframe = CTkFrame(settings, width=1200, height=660)
settingsframe.place(x=40, y=40)
changeNickBtn = CTkButton(settingsframe, text="Сменить ник", cursor="hand2", command=changeNick)
changeNickBtn.place(x=10, y=90)
currentNickLbl = CTkLabel(settingsframe, text="Текущий ник: " + config["playernick"])
currentNickLbl.place(x=10, y=130)
settingsRAMVar = IntVar(value=config["instancemem"])
goconsole = CTkButton(settingsframe, text="Консоль", image=consoleImg, cursor="hand2", command=lambda: liftFrameDown(console))
goconsole.image = consoleImg
goconsole.place(x=10, y=50)
def cngRAMLbl(_):
    settingsRAMLabel.configure(True, text=f"{settingsRAMVar.get()} ГБ")
    saveSettings()
settingsRAM = CTkSlider(settingsframe, from_=3, to=psutil.virtual_memory().total / 1024**3, variable=settingsRAMVar, command=cngRAMLbl, cursor="hand2", width=300, height=20)
settingsRAM.place(x=700, y=30)
settingsRAMLabel = CTkLabel(settingsframe, text=f"{settingsRAMVar.get()} ГБ")
settingsRAMLabel.place(x=1010, y=26)
settingsRAMTitle = CTkLabel(settingsframe, text="Оперативная память")
settingsRAMTitle.place(x=300, y=30)
settingsChangeClientPath = CTkButton(settingsframe, text="Сменить", cursor="hand2", command=changeInstanceDir)
settingsChangeClientPath.place(x=700, y=90)
settingsShowClientPath = CTkButton(settingsframe, text="Показать", cursor="hand2", command=lambda: os.startfile(config["instancedir"]))
settingsShowClientPath.place(x=850, y=90)
settingsChangeClientPathLbl = CTkLabel(settingsframe, text="Место установки")
settingsChangeClientPathLbl.place(x=300, y=95)
settingsAutoJoinVar = BooleanVar(value=config["instancequickplay"])
settingsAutoJoinVar.trace_add("write", saveSettings)
settingsAutoJoin = CTkCheckBox(settingsframe, text="Подключатся на сервер сразу", variable=settingsAutoJoinVar, cursor="hand2")
settingsAutoJoin.place(x=700, y=125)
gomainscreen = CTkButton(settingsframe, text="Назад", command=lambda: liftFrameDown(mainscreen), cursor="hand2")
gomainscreen.place(x=10, y=10)
settings.place(x=0, y=0, relwidth=1, relheight=1)
#progress
bg = CTkLabel(mcProgressframe, image=bgImg)
bg.image = bgImg
bg.place(x=0, y=0)
logo = CTkLabel(mcProgressframe, image=logoImg, text="")
logo.place(x=325, y=150)
progresstext = CTkLabel(mcProgressframe)
progresstext.place(relx=0.5, y=270, anchor="n")
progressdesc = CTkLabel(mcProgressframe)
progressdesc.place(relx=0.5, y=300, anchor="n")
progressbar = CTkProgressBar(mcProgressframe, width=1200, height=40)
progressbar.place(relx=0.5, y=330, anchor="n")
goconsole = CTkButton(mcProgressframe, text="Консоль", image=consoleImg, cursor="hand2", command=lambda: liftFrameDown(console))
goconsole.image = consoleImg
goconsole.place(x=0, y=0)
mcProgressframe.place(x=0, y=0, relwidth=1, relheight=1)
Thread(target=checkupdates, daemon=True).start()
try: Window.mainloop()
except BaseException: pass