import os
import shutil
import subprocess
from pathlib import Path
import sys
import tkinter
import tomllib
from threading import Thread
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring
from tkinter.ttk import Frame, Button, Scale, Label, Checkbutton, Notebook, Progressbar
from zipfile import ZipFile
import minecraft_launcher_lib
import requests
import tomli_w
import cv2
import hashlib
import uuid
from PIL import Image, ImageTk
from tkinter.messagebox import showerror, askyesno, showinfo
from tkinter import Label as tkLabel, Tk, IntVar, BooleanVar
SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SRC)
from regularlib import TkAddon
VERSION = "1.0.3"

def offline_uuid(name):
    data = ("OfflinePlayer:" + name).encode("utf-8")
    md5_hash = hashlib.md5(data).digest()
    b = bytearray(md5_hash)
    b[6] = (b[6] & 0x0F) | 0x30
    b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b))

def checkupdates():
    liftFrameDown(mcProgressframe)
    progresstext["text"] = "Проверка обновлений"
    progressdesc["text"] = "Downloading updates.toml"
    while True:
        try:
            with requests.get("https://raw.githubusercontent.com/regularship1/KvaritCraft-launcher/refs/heads/main/updates.toml", stream=True) as r:
                r.raise_for_status()
                progressbar["max"] = r.headers.get("Content-Length")
                with open(str(temp / "updates.toml"), "wb") as f:
                    for chunk in r.iter_content(chunk_size=1048576):
                        if chunk:
                            f.write(chunk)
                            progressbar["value"] += len(chunk)
        except BaseException as e:
            print(e)
            continue
        break
    updates = tomllib.load((temp / "updates.toml").open("rb"))
    if VERSION != updates["laucher_version"]:
        progressdesc["text"] = "Downloading Kvaritcraft.exe"
        while True:
            try:
                with requests.get(f"https://github.com/regularship1/KvaritCraft-launcher/releases/download/{updates["laucher_version"]}/Kvaritcraft.exe", stream=True) as r:
                    r.raise_for_status()
                    progressbar["max"] = r.headers.get("Content-Length")
                    with open(sys.executable, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar["value"] += len(chunk)
            except BaseException as e:
                print(e)
                continue
            break
        showinfo("Лаунчер обновился", f"Лаунчер обновился до версии {updates["laucher_version"]}. При следующем запуске вы запустите новую версию")

if os.path.basename(sys.executable) not in ("pythonw.exe", "python.exe"): checkupdates()

laucherootFP = Path(os.getenv("APPDATA")) / "regularship1" / "kvaritcraft6"
cfgFP = laucherootFP / "config.toml"

if not laucherootFP.exists(): laucherootFP.mkdir(parents=True)

if not cfgFP.exists():
    nick = ""
    while nick == "": nick = askstring("Ваш ник", "Введите ваш внутриигровой ник")
    cfgFP.write_text(tomli_w.dumps(dict(instancedir=str(laucherootFP / ".minecraft"), instancemem=8, instancequickplay=True, instancefullscreen=True, launchvanila=False, playanimation=True, playernick=nick)), encoding="utf-8")
config = tomllib.load(cfgFP.open("rb"))

instanceFP = Path(config["instancedir"])
temp = Path(os.getenv("LOCALAPPDATA")) / "Temp"

def liftFrameDown(frame, y=-750):
    if y < 0:
        frame.place(x=0, y=y)
        Window.after(10, liftFrameDown, frame, y + 30)
    else: frame.place(x=0, y=0)
    if y == -750: frame.lift()

def liftFrameUp(frame, y=720):
    if y > 0:
        frame.place(x=0, y=y)
        Window.after(10, liftFrameUp, frame, y - 30)
    else: frame.place(x=0, y=720)
    if y == 720: frame.lift()

def changeInstanceDir():
    newdir = askdirectory(title="Выберите папку", initialdir=config["instancedir"])
    move = askyesno("Переместить из старой папки?", "Переместить клиент из старой папки в новоую?(Все данные сохранятся)")
    if move: shutil.copy2(config["instancedir"], newdir)
    config["instancedir"] = newdir
    cfgFP.write_text(tomli_w.dumps(config))

def mainloop():
    global mainscreen, settings, console, mccon, constd, consoles, progressbar, mcProgressframe, progresstext, progressdesc
    bgphoto = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\bglogo.png"))
    normalbgphoto = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\bg.png"))
    playbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\play.png"))
    settingsbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\settings.png"))
    backbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\back.png"))
    conbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\console.png"))
    Window.overrideredirect(False)
    Window.attributes("-topmost", False)
    Window.iconbitmap(True, os.path.join(SRC, "assets\\icon.ico"))
    Window.resizable(False, False)
    Window.configure(background="#171716")
    Window.geometry(f"1280x720+{Window.winfo_screenwidth() // 2 - 640}+{Window.winfo_screenheight() // 2 - 360}")
    Window.title(f"KvaritCraft launcher v.{VERSION}")
    #mainFont = Font(font=(TkAddon.FONT, 10))
    tabs = Frame(style="DarkCustom.SizeTen.TFrame")
    tabs.place(x=0, y=0, relwidth=1, relheight=1)
    console = Frame(tabs, style="DarkCustom.SizeTen.TFrame")
    mainscreen = Frame(tabs, style="DarkCustom.SizeTen.TFrame")
    settings = Frame(tabs, style="DarkCustom.SizeTen.TFrame")
    mcProgressframe = Frame(tabs, style="DarkCustom.SizeTen.TFrame")
    #console
    consoles = Notebook(console, style="DarkCustom.SizeTen.TNotebook")
    globalconframe = Frame(consoles, style="DarkCustom.SizeTen.TFrame")
    globalcon = ScrolledText(globalconframe, bg="#232423", fg="white", insertbackground="white", state="disabled", wrap="word")
    #globalcon.vbar.config(bg="#171716", )
    globalcon.pack(expand=True, fill="both")
    class constd:
        def __init__(self, con): self.con = con
        def write(self, text):
            autoscroll = self.con.yview()[1] >= 0.999
            self.con.config(state="normal")
            self.con.insert("end", text)
            self.con.config(state="disabled")
            if autoscroll: self.con.see("end")
        def flush(self): pass
    sys.stdout = constd(globalcon)
    sys.stderr = constd(globalcon)
    consoles.add(globalconframe, text="Лаунчер")
    mcconframe = Frame(consoles, style="DarkCustom.SizeTen.TFrame")
    mccon = ScrolledText(mcconframe, bg="#232423", fg="white", insertbackground="white", state="disabled", wrap="word")
    mccon.pack(expand=True, fill="both")
    consoles.add(mcconframe, text="Майнкрафт")
    consoles.place(x=0, y=0, relwidth=1, relheight=1)
    conback = Button(console, image=backbtnicon, style="DarkCustom.SizeTen.TButton", command=lambda: console.lower(), cursor="hand2")
    conback.image = backbtnicon
    conback.place(x=0, y=630)
    console.place(x=0, y=0, relwidth=1, relheight=1)
    print("Привет! Я Мита!")
    #mainscreen
    bg = tkLabel(mainscreen, image=bgphoto, bg="white")
    bg.image = bgphoto
    bg.place(x=0, y=0, relwidth=1, relheight=1)
    play = Button(mainscreen, style="DarkCustom.SizeTen.TLabel", image=playbtnicon, cursor="hand2")
    play.bind("<Button-1>", lambda _: Thread(target=launchinstance, daemon=True).start())
    play.image = playbtnicon
    play.place(x=200, y=300)
    gosettings = Label(mainscreen, image=settingsbtnicon, style="DarkCustom.SizeTen.TLabel", cursor="hand2")
    gosettings.image = settingsbtnicon
    gosettings.bind("<Button-1>", lambda _: liftFrameDown(settings))
    gosettings.place(x=200, y=400)
    goconsole = Label(mainscreen, image=conbtnicon, style="DarkCustom.SizeTen.TLabel", cursor="hand2")
    goconsole.image = conbtnicon
    goconsole.bind("<Button-1>", lambda _: liftFrameDown(console))
    goconsole.place(x=200, y=500)
    mainscreen.place(x=0, y=0, relwidth=1, relheight=1)
    mainscreen.lift()
    #settings
    bg = tkLabel(settings, image=normalbgphoto, bg="white")
    bg.image = normalbgphoto
    bg.place(x=0, y=0, relwidth=1, relheight=1)
    settingsframe = Frame(settings, style="DarkCustom.SizeTen.TButton")
    settingsframe.place(x=40, y=40, width=1200, height=660)
    settingsRAMVar = IntVar(value=config["instancemem"])
    def cngRAMLbl(_):
        settingsRAMLabel["text"] = f"{settingsRAMVar.get()} ГБ"
        config["instancemem"] = settingsRAMVar.get()
        cfgFP.write_text(tomli_w.dumps(config))
    settingsRAM = Scale(settingsframe, style="DarkCustom.Horizontal.TScale", from_=1, to=16, variable=settingsRAMVar, command=cngRAMLbl, cursor="hand2")
    settingsRAMLabel = Label(settingsframe, style="DarkCustom.SizeTen.TLabel", text=f"{settingsRAMVar.get()} ГБ")
    settingsRAMLabel.place(x=650, y=30)
    settingsRAM.place(x=700, y=30, width=400, height=20)
    settingsRAMTitle = Label(settingsframe, style="DarkCustom.SizeTen.TLabel", text="Оперативная память")
    settingsRAMTitle.place(x=300, y=30)
    settingsClientFullVar = BooleanVar(value=config["instancefullscreen"])
    def UPDsettingsClientFull(*args):
        config["instancefullscreen"] = settingsClientFullVar.get()
        cfgFP.write_text(tomli_w.dumps(config))
    settingsClientFullVar.trace_add("write", UPDsettingsClientFull)
    settingsClientFull = Checkbutton(settingsframe, style="DarkCustom.SizeTen.TCheckbutton", variable=settingsClientFullVar, cursor="hand2")
    settingsClientFull.place(x=700, y=60)
    settingsClientFullabel = Label(settingsframe, style="DarkCustom.SizeTen.TLabel", text="Запускать клиент в полном экране")
    settingsClientFullabel.place(x=300, y=60)
    settingsChangeClientPath = Button(settingsframe, style="DarkCustom.SizeTen.TButton", text="Сменить", cursor="hand2", command=changeInstanceDir)
    settingsChangeClientPath.place(x=700, y=90)
    settingsShowClientPath = Button(settingsframe, style="DarkCustom.SizeTen.TButton", text="Показать", cursor="hand2", command=lambda: os.startfile(config["instancedir"]))
    settingsShowClientPath.place(x=820, y=90)
    settingsChangeClientPathLbl = Label(settingsframe, style="DarkCustom.SizeTen.TLabel", text="Место установки")
    settingsChangeClientPathLbl.place(x=300, y=95)
    settingsAutoJoinVar = BooleanVar(value=config["instancequickplay"])
    def UPDsettingsAutoJoin(*args):
        config["instancequickplay"] = settingsAutoJoinVar.get()
        cfgFP.write_text(tomli_w.dumps(config))
    settingsAutoJoinVar.trace_add("write", UPDsettingsAutoJoin)
    settingsAutoJoin = Checkbutton(settingsframe, style="DarkCustom.SizeTen.TCheckbutton", variable=settingsAutoJoinVar, cursor="hand2")
    settingsAutoJoin.place(x=700, y=125)
    settingsAutoJoinLbl = Label(settingsframe, style="DarkCustom.SizeTen.TLabel", text="Подключатся на сервер сразу")
    settingsAutoJoinLbl.place(x=300, y=125)
    settingsLaunchVanilaVar = BooleanVar(value=config["launchvanila"])
    def UPDsettingsLaunchVanila(*args):
        config["launchvanila"] = settingsLaunchVanilaVar.get()
        cfgFP.write_text(tomli_w.dumps(config))
    settingsLaunchVanilaVar.trace_add("write", UPDsettingsLaunchVanila)
    settingsLaunchVanila = Checkbutton(settingsframe, style="DarkCustom.SizeTen.TCheckbutton", variable=settingsLaunchVanilaVar, cursor="hand2")
    settingsLaunchVanila.place(x=700, y=155)
    settingsLaunchVanilaLbl = Label(settingsframe, style="DarkCustom.SizeTen.TLabel", text="Запускать Vanila 1.20.1")
    settingsLaunchVanilaLbl.place(x=300, y=155)
    gomainscreen = Button(settingsframe, image=backbtnicon, style="DarkCustom.SizeTen.TButton", command=lambda: liftFrameDown(mainscreen), cursor="hand2")
    gomainscreen.image = backbtnicon
    gomainscreen.place(x=10, y=10)
    settings.place(x=0, y=0, relwidth=1, relheight=1)
    #progress
    bg = tkLabel(mcProgressframe, image=normalbgphoto, bg="white")
    bg.image = normalbgphoto
    bg.place(x=0, y=0, relwidth=1, relheight=1)
    progresstext = Label(mcProgressframe, style="DarkCustom.SizeTen.TLabel")
    progresstext.place(relx=0.5, y=270, anchor="n")
    progressdesc = Label(mcProgressframe, style="DarkCustom.SizeTen.TLabel")
    progressdesc.place(relx=0.5, y=300, anchor="n")
    progressbar = Progressbar(mcProgressframe, style="DarkCustom.Horizontal.TProgressbar")
    progressbar.place(relx=0.5, y=330, anchor="n", width=200, height=40)
    goconsole = Label(mcProgressframe, image=conbtnicon, style="DarkCustom.SizeTen.TLabel", cursor="hand2")
    goconsole.image = conbtnicon
    goconsole.bind("<Button-1>", lambda _: liftFrameDown(console))
    goconsole.place(x=0, y=0)
    mcProgressframe.place(x=0, y=0, relwidth=1, relheight=1)

def installinstance():
    if "1.20.1" not in {v["id"] for v in minecraft_launcher_lib.utils.get_installed_versions(config["instancedir"])}:
        progresstext["text"] = "Установка майнкрафта"
        progressdesc["text"] = "Downloading minecraft.zip"
        while True:
            try:
                with requests.get("https://drive.usercontent.google.com/download?confirm=t&id=1MZV4I8FYikmPB4KN4Tc6fwIrFpGIkdIo&export=download", stream=True) as r:
                    r.raise_for_status()
                    progressbar["max"] = r.headers.get("Content-Length")
                    with open(str(temp / "minecraft.zip"), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar["value"] += len(chunk)
            except BaseException as e:
                print(e)
                continue
            break
        progresstext["text"] = "Установка майнкрафта"
        progressdesc["text"] = "Unpacking minecraft.zip"
        progressbar["mode"] = "indeterminate"
        progressbar.start()
        with ZipFile(str(temp / "minecraft.zip"), "r") as z: z.extractall(config["instancedir"])
        progressbar.stop()
        progressbar["mode"] = "determinate"
    if not os.path.exists(os.path.join(config["instancedir"], "mods")) or not os.listdir(os.path.join(config["instancedir"], "mods")):
        progresstext["text"] = "Установка модов"
        progressdesc["text"] = "Downloading mods.zip"
        while True:
            try:
                with requests.get("http://155.212.208.63:5000/static/files/mods.zip", stream=True) as r:
                    r.raise_for_status()
                    progressbar["max"] = r.headers.get("Content-Length")
                    with open(str(temp / "mods.zip"), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1048576):
                            if chunk:
                                f.write(chunk)
                                progressbar["value"] += len(chunk)
            except BaseException as e:
                print(e)
                continue
            break
        progresstext["text"] = "Установка модов"
        progressdesc["text"] = "Unpacking mods.zip"
        progressbar["mode"] = "indeterminate"
        progressbar.start()
        with ZipFile(str(temp / "mods.zip"), "r") as z: z.extractall(config["instancedir"])
        progressbar.stop()
        progressbar["mode"] = "determinate"

def launchinstance():
    print("Запуск \"Кварц 6\"")
    liftFrameDown(mcProgressframe)
    installinstance()
    mainscreen.lift()
    liftFrameDown(console)
    consoles.select(1)
    cmd = minecraft_launcher_lib.command.get_minecraft_command(
        "1.20.1" if config["launchvanila"] else "1.20.1-forge-47.4.10",
        config["instancedir"],
        {
            "username": config["playernick"],
            "uuid": str(offline_uuid(config["playernick"])),
            "token": "",
            "jvmArguments": [f"-Xmx{config["instancemem"]}G", "-Xms2G"],
        }
    )
    if config["instancequickplay"]: cmd += ["--quickPlayMultiplayer", "kvaritcraft.mclan.ru"]
    proc = subprocess.Popen(**{"args": cmd, "cwd": config["instancedir"], "stdout":subprocess.PIPE, "stderr":subprocess.STDOUT, "text": True,})
    mcstd = constd(mccon)
    for line in proc.stdout: print(line, file=mcstd, end="")

Window = Tk()
Window.focus_force()
Window.attributes("-topmost", True)
Window.geometry(f"1280x720+{Window.winfo_screenwidth()//2-640}+{Window.winfo_screenheight()//2-360}")
Window.configure(background="#171716")
TkAddon.SetupStyles(Window)
Window.resizable(False, False)
Window.overrideredirect(True)
cap = cv2.VideoCapture(os.path.join(SRC, r"assets\splash.mp4"))
ok, frame = cap.read()
if not ok: showerror("A preload exception has been occurred", "Can't load splash screen")
h, w = frame.shape[:2]
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
img = Image.fromarray(frame_rgb)
photo = ImageTk.PhotoImage(img)
vidplayer = tkLabel(Window, image=photo, bd=0, bg="black")
vidplayer.image = photo
vidplayer.pack(expand=True, fill="both")
vidskip = False

def vidnext():
    global frame, cap, frame_rgb, img, photo, code
    ok2, frame2 = cap.read()
    if not ok2 or vidskip:
        cap.release()
        vidplayer.destroy()
        Window.after(0, mainloop)
        return
    frame_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    photo = ImageTk.PhotoImage(img)
    vidplayer.image = photo
    vidplayer.config(image=photo)
    Window.after(1, vidnext)

def skipsplash(_):
    global vidskip
    vidskip = True
    config["playanimation"] = False
    cfgFP.write_text(tomli_w.dumps(config))

vidplayer.bind("<Button-1>", skipsplash)
if config["playanimation"]: Window.after(0, vidnext)
else: Window.after(0, mainloop)
Window.mainloop()
sys.exit()