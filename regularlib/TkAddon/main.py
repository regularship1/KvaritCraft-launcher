import os.path
from tkinter import Tk
import tkinter as tk
import os
from tkinter.ttk import Style
from ctypes import windll, byref, create_unicode_buffer

SRC = os.path.dirname(os.path.abspath(__file__))

FONT = "Arial Black Primer"

def SetupStyles(window: Tk):
	buf = create_unicode_buffer(os.path.join(SRC, "ArialBlackPrimer.ttf"))
	add_font = windll.gdi32.AddFontResourceExW
	add_font(byref(buf), 0x10 | 0, 0)
	styles = Style(window)
	styles.theme_use("clam")
	styles.configure("DarkCustom.TButton", font=(FONT, 30), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.TEntry", font=(FONT, 30), foreground="white", fieldbackground="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white", insertcolor="white")
	styles.configure("DarkCustom.Horizontal.TProgressbar", background="#000000", troughcolor="#232423",
					 troughbordercolor="#232423", troughborderwidth=1)
	styles.configure("DarkCustom.Horizontal.TScale", background="#000000", troughcolor="#232423",
					 troughbordercolor="#232423", troughborderwidth=1)
	styles.configure("DarkCustom.TLabel", font=(FONT, 30), foreground="white", background="#171716",
					 bordercolor="#171716", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TRadiobutton", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TCheckbutton", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TButton", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TCombobox", font=(FONT, 10), fieldbackground="#232423", foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white", arrowcolor="white", selectbackground="#232423")
	styles.configure("DarkCustom.SizeTen.TFrame", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TNotebook", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TNotebook.Tab", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TLabel", font=(FONT, 10), foreground="white", background="#171716",
					 bordercolor="#171716", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.Red.TLabel", font=(FONT, 10), foreground="red", background="#171716",
					 bordercolor="#171716", focusthickness=0, focuscolor="#white")
	styles.configure("DarkCustom.SizeTen.TEntry", font=(FONT, 10), foreground="white", fieldbackground="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white", insertcolor="white")
	styles.configure("DarkCustom.SizeTen.Placeholder.TEntry", font=(FONT, 10), foreground="#787a79", fieldbackground="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white", insertcolor="white")
	styles.configure("DarkCustom.SizeTen.Treeview", font=(FONT, 10), foreground="white", background="#232423",
					 fieldbackground="#232423", rowheight=25, bordercolor="#232423", focusthickness=0, focuscolor="#white", indent=20)
	styles.configure("DarkCustom.SizeTen.Treeview.Heading", font=(FONT, 10), foreground="white", background="#232423",
					 bordercolor="#232423", focusthickness=0, focuscolor="#white", indent=20)
	styles.map("DarkCustom.TButton", background=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.TButton", background=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.TCombobox", background=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.TFrame", background=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.TNotebook", background=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.TNotebook.Tab", background=[("active", "#121212")], cursor=[('active', 'hand2'), ('selected', 'hand2')])
	styles.map("DarkCustom.Horizontal.TScale", background=[("active", "#121212"), ("focus", "#121212")])
	styles.map("DarkCustom.SizeTen.TEntry", fieldbackground=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.Placeholder.TEntry", fieldbackground=[("active", "#121212")])
	styles.map("DarkCustom.SizeTen.TRadiobutton", background=[("active", "#121212"), ("selected", "black")])
	styles.map("DarkCustom.SizeTen.TCheckbutton", background=[("active", "#121212"), ("selected", "black")])
	styles.map("DarkCustom.SizeTen.Treeview", background=[("active", "#121212"), ("selected", "#121212")])
	styles.map("DarkCustom.SizeTen.Treeview.Heading", background=[("active", "#121212")])
	window.option_add('*TCombobox*Listbox.background', '#232423')
	window.option_add('*TCombobox*Listbox.foreground', 'white')
	window.option_add('*TCombobox*Listbox.selectBackground', '#121212')
	window.option_add('*TCombobox*Listbox.selectForeground', 'white')

def GetTreeviewRoot(tree, item_id):
	parent = tree.parent(item_id)
	if parent == "": return item_id
	while True:
		next_parent = tree.parent(parent)
		if next_parent == "": return parent
		parent = next_parent

class ToolTip:
	def __init__(self, widget, text, wait=400):
		self.widget = widget
		self.text = text
		self.wait = wait
		self.id = None
		self.tw = None
		widget.bind("<Enter>", self._enter)
		widget.bind("<Leave>", self._leave)
	def _enter(self, event=None):
		self._schedule()
	def _leave(self, event=None):
		self._unschedule()
		self._hide()
	def _schedule(self):
		self._unschedule()
		self.id = self.widget.after(self.wait, self._show)
	def _unschedule(self):
		if self.id:
			self.widget.after_cancel(self.id)
			self.id = None
	def _show(self, event=None):
		if self.tw: return
		x = self.widget.winfo_rootx() + 20
		y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
		self.tw = tk.Toplevel(self.widget)
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry(f"+{x}+{y}")
		label = tk.Label(self.tw, text=self.text, justify="left", background="#121212", relief="solid", borderwidth=1, foreground="#ffffff", font=(FONT, 10))
		label.pack(ipadx=5, ipady=2)
	def _hide(self):
		if self.tw:
			self.tw.destroy()
			self.tw = None