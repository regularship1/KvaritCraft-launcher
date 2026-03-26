import json
import os
import subprocess
from pathlib import Path
import sys
import tkinter
import tomllib
from threading import Thread
from tkinter.ttk import Frame, Button, Scale, Label, Checkbutton, Notebook
import minecraft_launcher_lib
import tomli_w

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SRC)
import cv2
import hashlib
import uuid
from PIL import Image, ImageTk
from tkinter.messagebox import showerror
from tkinter import Label as tkLabel, Tk, Text, IntVar, BooleanVar
from regularlib import TkAddon
VERSION = "1.0-alpha 5"

def offline_uuid(name):
    data = ("OfflinePlayer:" + name).encode("utf-8")
    md5_hash = hashlib.md5(data).digest()
    b = bytearray(md5_hash)
    b[6] = (b[6] & 0x0F) | 0x30
    b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b))

laucherootFP = Path(os.getenv("APPDATA")) / "regularship1" / "kvaritcraft6"
cfgFP = laucherootFP / "config.toml"

if not laucherootFP.exists(): laucherootFP.mkdir(parents=True)

if not cfgFP.exists(): cfgFP.write_text(tomli_w.dumps(dict(instancedir=r"D:\Temp\kvaritcraft", instancemem=4, instancequickplay=True, instancefullscreen=True, launchvanila=True, playernick="regularship1")), encoding="utf-8")
config = tomllib.load(cfgFP.open("rb"))

instanceFP = Path(config["instancedir"])

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

def mainloop():
    global mainscreen, settings, console, mccon, constd
    bgphoto = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\bglogo.png"))
    normalbgphoto = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\bg.png"))
    playbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\play.png"))
    settingsbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\settings.png"))
    backbtnicon = tkinter.PhotoImage(file=os.path.join(SRC, "assets\\back.png"))
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
    #console
    consoles = Notebook(console, style="DarkCustom.SizeTen.TNotebook")
    globalconframe = Frame(consoles, style="DarkCustom.SizeTen.TFrame")
    globalcon = Text(globalconframe, bg="#232423", fg="white", insertbackground="white", state="disabled")
    globalcon.pack(expand=True, fill="both")
    class constd:
        def __init__(self, con): self.con = con
        def write(self, text):
            self.con.config(state="normal")
            self.con.insert("end", text)
            self.con.config(state="disabled")
            if self.con.yview()[1] >= 0.999: self.con.see("end")
        def flush(self): pass
    sys.stdout = constd(globalcon)
    sys.stderr = constd(globalcon)
    consoles.add(globalconframe, text="Лаунчер")
    mcconframe = Frame(consoles, style="DarkCustom.SizeTen.TFrame")
    mccon = Text(mcconframe, bg="#232423", fg="white", insertbackground="white", state="disabled")
    mccon.pack(expand=True, fill="both")
    consoles.add(mcconframe, text="Майнкрафт")
    consoles.place(x=0, y=0, relwidth=1, relheight=1)
    contomain = Button(console, image=backbtnicon, style="DarkCustom.SizeTen.TButton", command=lambda: liftFrameDown(mainscreen), cursor="hand2")
    contomain.image = backbtnicon
    contomain.place(x=0, y=630)
    console.place(x=0, y=0, relwidth=1, relheight=1)
    print("Привет! Я Мита!")
    #mainscreen
    bg = tkLabel(mainscreen, image=bgphoto, bg="white")
    bg.image = bgphoto
    bg.place(x=0, y=0, relwidth=1, relheight=1)
    play = Button(mainscreen, style="DarkCustom.SizeTen.TButton", image=playbtnicon, cursor="hand2", command=launchinstance)
    play.image = playbtnicon
    play.place(x=200, y=300)
    gosettings = Button(mainscreen, image=settingsbtnicon, style="DarkCustom.SizeTen.TButton", command=lambda: liftFrameDown(settings), cursor="hand2")
    gosettings.image = settingsbtnicon
    gosettings.place(x=200, y=400)
    goconsole = Button(mainscreen, text="Консоль", style="DarkCustom.SizeTen.TButton", command=lambda: liftFrameDown(console), cursor="hand2")
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
    settingsChangeClientPath = Button(settingsframe, style="DarkCustom.SizeTen.TButton", text="Сменить", cursor="hand2")
    settingsChangeClientPath.place(x=700, y=90)
    settingsShowClientPath = Button(settingsframe, style="DarkCustom.SizeTen.TButton", text="Показать", cursor="hand2")
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

def installinstance():
    minecraft_launcher_lib.install.install_minecraft_version(
        "1.20.1",
        config["instancedir"]
    )

def MCconThread(**kwargs):
    proc = subprocess.Popen(**kwargs)
    mcstd = constd(mccon)
    for line in proc.stdout:
        print(line, file=mcstd, end="")

def launchinstance():
    print("launching kvaritcraft")
    cmd = minecraft_launcher_lib.command.get_minecraft_command(
        "1.20.1" if config["launchvanila"] else "1.20.1-forge-47.4.10",
        config["instancedir"],
        {
            "username": config["playernick"],
            "uuid": str(offline_uuid(config["playernick"])),
            "token": "",
            "jvmArguments": ["-Xmx4G", "-Xms2G"],
        }
    )
    if config["instancequickplay"]: cmd += ["--quickPlayMultiplayer", "kvaritcraft.mclan.ru"]
    Thread(target=MCconThread, kwargs={
        "args": cmd,
        "cwd": config["instancedir"],
        "stdout":subprocess.PIPE,
        "stderr":subprocess.STDOUT,
        "text": True,
    }).start()

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

vidplayer.bind("<Button-1>", skipsplash)
#Window.after(0, vidnext)
Window.after(0, mainloop)
Window.mainloop()