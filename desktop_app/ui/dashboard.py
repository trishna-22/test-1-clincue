"""Dashboard view: header + procedure card grid, ported from index.html."""

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import data
import progress_store

CARD_IMAGE_SIZE = (280, 150)


def _badge_info(theme, checked_count, percent):
    if checked_count == 0:
        return "Not Started", theme["text_muted"], theme["bg_surface_hover"]
    if percent == 100:
        return "Completed", "#ffffff", theme["success"]
    return "In Progress", "#ffffff", theme["accent"]


def _button_label(checked_count, percent):
    if checked_count == 0:
        return "Start Revision"
    if percent == 100:
        return "Revise Again"
    return "Resume Revision"


def build_dashboard(container, app):
    theme = app.theme
    image_refs = []

    root_frame = tk.Frame(container, bg=theme["bg_main"])

    # ---- Header ----
    header = tk.Frame(root_frame, bg=theme["bg_surface"])
    header.pack(fill="x")
    header_inner = tk.Frame(header, bg=theme["bg_surface"])
    header_inner.pack(fill="x", padx=24, pady=14)

    brand = tk.Frame(header_inner, bg=theme["bg_surface"])
    brand.pack(side="left")
    icon = tk.Label(brand, text="C", bg=theme["accent"], fg="#ffffff",
                     font=("Outfit", 14, "bold"), width=2, height=1)
    icon.pack(side="left", padx=(0, 8))
    tk.Label(brand, text=data.APP_NAME, bg=theme["bg_surface"], fg=theme["text_main"],
              font=("Outfit", 15, "bold")).pack(side="left")

    theme_label = "Switch to Light Mode" if app.theme_name == "dark" else "Switch to Dark Mode"
    theme_btn = tk.Button(header_inner, text=theme_label, command=app.toggle_theme,
                           bg=theme["bg_surface_hover"], fg=theme["text_main"],
                           relief="flat", font=("Inter", 9), padx=10, pady=4,
                           cursor="hand2")
    theme_btn.pack(side="right")

    # ---- Scrollable body ----
    canvas = tk.Canvas(root_frame, bg=theme["bg_main"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(root_frame, orient="vertical", command=canvas.yview)
    body = tk.Frame(canvas, bg=theme["bg_main"])

    body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=body, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    content = tk.Frame(body, bg=theme["bg_main"])
    content.pack(fill="both", expand=True, padx=32, pady=24)

    # ---- Hero ----
    tk.Label(content, text="Clinical Procedure Revision", bg=theme["bg_main"],
              fg=theme["text_main"], font=("Outfit", 24, "bold")).pack(anchor="w")
    tk.Label(content,
              text="A structured revision guide for nursing students, covering core clinical\n"
                   "procedures with narrated instruction, pictorial checklists, and video reference.",
              bg=theme["bg_main"], fg=theme["text_muted"], font=("Inter", 11),
              justify="left").pack(anchor="w", pady=(6, 24))

    # ---- Procedure grid ----
    grid = tk.Frame(content, bg=theme["bg_main"])
    grid.pack(fill="both", expand=True)
    grid.grid_columnconfigure(0, weight=1)
    grid.grid_columnconfigure(1, weight=1)

    for i, proc in enumerate(data.PROCEDURES):
        card = _build_card(grid, app, theme, proc, image_refs)
        card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=12, pady=12)

    root_frame.image_refs = image_refs

    def cleanup():
        canvas.unbind_all("<MouseWheel>")

    return root_frame, cleanup


def _build_card(parent, app, theme, proc, image_refs):
    info = progress_store.get_procedure_progress(proc["slug"], proc["total_steps"])
    checked_count = len(info["checked_steps"])
    percent = info["percent"]

    card = tk.Frame(parent, bg=theme["bg_surface"], highlightbackground=theme["border"],
                     highlightthickness=1)

    try:
        img = Image.open(proc["image"])
        img.thumbnail(CARD_IMAGE_SIZE)
        photo = ImageTk.PhotoImage(img)
        image_refs.append(photo)
        tk.Label(card, image=photo, bg=theme["bg_surface"]).pack(fill="x")
    except (OSError, FileNotFoundError):
        tk.Label(card, text="[image unavailable]", bg=theme["bg_surface"],
                  fg=theme["text_muted"], height=6).pack(fill="x")

    body = tk.Frame(card, bg=theme["bg_surface"])
    body.pack(fill="both", expand=True, padx=16, pady=16)

    title_row = tk.Frame(body, bg=theme["bg_surface"])
    title_row.pack(fill="x")
    tk.Label(title_row, text=proc["title"], bg=theme["bg_surface"], fg=theme["text_main"],
              font=("Outfit", 14, "bold"), anchor="w", justify="left",
              wraplength=300).pack(side="left", fill="x", expand=True)

    badge_text, badge_fg, badge_bg = _badge_info(theme, checked_count, percent)
    tk.Label(title_row, text=badge_text, bg=badge_bg, fg=badge_fg, font=("Inter", 8, "bold"),
              padx=8, pady=2).pack(side="right")
    tk.Label(body, text=proc["subtitle"], bg=theme["bg_surface"], fg=theme["text_muted"],
              font=("Inter", 9), anchor="w", justify="left", wraplength=380).pack(
        fill="x", pady=(4, 10))

    progress_row = tk.Frame(body, bg=theme["bg_surface"])
    progress_row.pack(fill="x")
    tk.Label(progress_row, text="Progress", bg=theme["bg_surface"], fg=theme["text_muted"],
              font=("Inter", 8)).pack(side="left")
    tk.Label(progress_row, text=f"{percent}%", bg=theme["bg_surface"], fg=theme["accent"],
              font=("Inter", 8, "bold")).pack(side="right")

    bar_bg = tk.Frame(body, bg=theme["border"], height=6)
    bar_bg.pack(fill="x", pady=(4, 12))
    bar_bg.pack_propagate(False)
    if percent > 0:
        bar_fill = tk.Frame(bar_bg, bg=theme["accent"])
        bar_fill.place(relx=0, rely=0, relwidth=percent / 100, relheight=1)

    meta_row = tk.Frame(body, bg=theme["bg_surface"])
    meta_row.pack(fill="x", pady=(0, 12))
    tk.Label(meta_row, text=f"{proc['total_steps']} Steps",
              bg=theme["bg_surface"], fg=theme["text_muted"], font=("Inter", 9)).pack(side="left")
    tk.Label(meta_row, text="•", bg=theme["bg_surface"], fg=theme["text_muted"],
              font=("Inter", 9)).pack(side="left", padx=8)
    tk.Label(meta_row, text=proc["meta"], bg=theme["bg_surface"],
              fg=theme["text_muted"], font=("Inter", 9)).pack(side="left")

    tk.Button(body, text=_button_label(checked_count, percent),
              command=lambda: app.show_procedure(proc["slug"]), bg=theme["accent"],
              fg="#ffffff", relief="flat", font=("Inter", 10, "bold"), pady=8,
              cursor="hand2").pack(fill="x")

    return card
