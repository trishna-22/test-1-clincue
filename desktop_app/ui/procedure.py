"""Procedure detail view: header/progress + Audio / Pictorial / Combined tabs.

Ported from procedures/*.html + js/procedure-init.js.
"""

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import data
import progress_store
from video_player import VideoPlayer

HERO_IMAGE_SIZE = (640, 300)
VIDEO_SIZE = (480, 270)


def build_procedure(container, app, slug):
    theme = app.theme
    proc = data.get_procedure(slug)
    narrator = app.narrator
    audio_player = app.audio_player
    image_refs = []

    # Mutable state shared across the tabs/closures below.
    state = {
        "is_audio_playing": False,
        "is_combined_playing": False,
        "combined_slide": 0,
        "pending_after_id": None,
        "step_cards": {},  # idx -> {"card": frame, "check": label}
    }

    root_frame = tk.Frame(container, bg=theme["bg_main"])

    # ---------------------------------------------------------------- header
    header_wrap = tk.Frame(root_frame, bg=theme["bg_main"])
    header_wrap.pack(fill="x", padx=32, pady=(20, 10))

    back_btn = tk.Button(header_wrap, text="← Back to Dashboard",
                          command=lambda: app.show_dashboard(), bg=theme["bg_main"],
                          fg=theme["accent"], relief="flat", font=("Inter", 10, "bold"),
                          cursor="hand2", bd=0)
    back_btn.pack(anchor="w")

    title_row = tk.Frame(header_wrap, bg=theme["bg_main"])
    title_row.pack(fill="x", pady=(10, 0))

    title_block = tk.Frame(title_row, bg=theme["bg_main"])
    title_block.pack(side="left", fill="x", expand=True)
    tk.Label(title_block, text=proc["title"], bg=theme["bg_main"], fg=theme["text_main"],
              font=("Outfit", 22, "bold"), anchor="w").pack(fill="x")
    tk.Label(title_block, text=proc["subtitle"], bg=theme["bg_main"], fg=theme["text_muted"],
              font=("Inter", 10), anchor="w", justify="left", wraplength=600).pack(
        fill="x", pady=(4, 0))

    progress_box = tk.Frame(title_row, bg=theme["bg_surface"])
    progress_box.pack(side="right", padx=(20, 0))
    progress_inner = tk.Frame(progress_box, bg=theme["bg_surface"])
    progress_inner.pack(padx=20, pady=12)
    progress_label_row = tk.Frame(progress_inner, bg=theme["bg_surface"])
    progress_label_row.pack(fill="x")
    tk.Label(progress_label_row, text="Revision Progress", bg=theme["bg_surface"],
              fg=theme["text_main"], font=("Inter", 9)).pack(side="left")
    pct_label = tk.Label(progress_label_row, text="0%", bg=theme["bg_surface"],
                          fg=theme["accent"], font=("Inter", 9, "bold"))
    pct_label.pack(side="left", padx=(12, 0))
    bar_bg = tk.Frame(progress_inner, bg=theme["border"], height=8, width=180)
    bar_bg.pack(pady=(8, 0))
    bar_bg.pack_propagate(False)
    bar_fill = tk.Frame(bar_bg, bg=theme["accent"])

    def refresh_header_progress():
        info = progress_store.get_procedure_progress(slug, proc["total_steps"])
        pct_label.configure(text=f"{info['percent']}%")
        bar_fill.place(relx=0, rely=0, relwidth=info["percent"] / 100, relheight=1)
        return info

    refresh_header_progress()

    # ---------------------------------------------------------------- tabs
    notebook = ttk.Notebook(root_frame)
    notebook.pack(fill="both", expand=True, padx=32, pady=(10, 20))

    audio_tab = tk.Frame(notebook, bg=theme["bg_main"])
    pictorial_tab = tk.Frame(notebook, bg=theme["bg_main"])
    combined_tab = tk.Frame(notebook, bg=theme["bg_main"])
    notebook.add(audio_tab, text="\U0001F3A7 Audio Revision")
    notebook.add(pictorial_tab, text="\U0001F5BC️ Pictorial Guide")
    notebook.add(combined_tab, text="\U0001F39B️ Combined Media")

    full_narration = [
        f"Step {i + 1}. {title}. {desc}."
        for i, (title, desc) in enumerate(zip(proc["steps"], proc["step_descriptions"]))
    ]

    def highlight_step_card(idx):
        for i, refs in state["step_cards"].items():
            refs["card"].configure(highlightbackground=theme["border"], highlightthickness=1)
        if idx is not None and idx >= 0 and idx in state["step_cards"]:
            state["step_cards"][idx]["card"].configure(
                highlightbackground=theme["accent"], highlightthickness=2)

    def clear_step_highlight():
        highlight_step_card(None)

    # ============================================================= AUDIO TAB
    deck = tk.Frame(audio_tab, bg=theme["bg_surface"])
    deck.pack(fill="x", pady=20, padx=10)
    tk.Label(deck, text=proc["title"], bg=theme["bg_surface"], fg=theme["text_main"],
              font=("Outfit", 16, "bold")).pack(pady=(20, 4))
    tk.Label(deck, text="Narrated Revision • Ambient Backing Track", bg=theme["bg_surface"],
              fg=theme["text_muted"], font=("Inter", 9)).pack()

    deck_progress_row = tk.Frame(deck, bg=theme["bg_surface"])
    deck_progress_row.pack(fill="x", padx=40, pady=(20, 4))
    audio_step_label = tk.Label(deck_progress_row, text="0:00", bg=theme["bg_surface"],
                                 fg=theme["text_muted"], font=("Inter", 9))
    audio_step_label.pack(side="left")
    audio_bar_bg = tk.Frame(deck_progress_row, bg=theme["border"], height=6)
    audio_bar_bg.pack(side="left", fill="x", expand=True, padx=10)
    audio_bar_bg.pack_propagate(False)
    audio_bar_fill = tk.Frame(audio_bar_bg, bg=theme["accent"])
    tk.Label(deck_progress_row, text="Step-by-Step", bg=theme["bg_surface"],
              fg=theme["text_muted"], font=("Inter", 9)).pack(side="left")

    audio_play_btn = tk.Button(deck, text="▶️", bg=theme["accent"], fg="#ffffff",
                                relief="flat", font=("Segoe UI Emoji", 14), width=4,
                                cursor="hand2")
    audio_play_btn.pack(pady=16)

    volume_row = tk.Frame(deck, bg=theme["bg_surface"])
    volume_row.pack(pady=(0, 20))
    tk.Label(volume_row, text="\U0001F3B5 Ambient Volume:", bg=theme["bg_surface"],
              fg=theme["text_muted"], font=("Inter", 9)).pack(side="left")
    volume_scale = ttk.Scale(volume_row, from_=0, to=0.5, orient="horizontal", length=120)
    volume_scale.set(0.15)
    volume_scale.pack(side="left", padx=8)

    def on_volume_change(_evt=None):
        audio_player.set_volume(float(volume_scale.get()))

    volume_scale.configure(command=on_volume_change)

    def update_audio_deck_ui(is_playing):
        state["is_audio_playing"] = is_playing
        audio_play_btn.configure(text="⏸️" if is_playing else "▶️")

    def on_audio_step_change(idx):
        highlight_step_card(idx)
        if idx is not None and idx >= 0:
            pct = round(((idx + 1) / len(proc["steps"])) * 100)
            audio_bar_fill.place(relx=0, rely=0, relwidth=pct / 100, relheight=1)
            audio_step_label.configure(text=f"Step {idx + 1}")
        else:
            audio_bar_fill.place(relx=0, rely=0, relwidth=0, relheight=1)
            audio_step_label.configure(text="0:00")

    def on_audio_state_change(is_playing):
        update_audio_deck_ui(is_playing)
        if not is_playing:
            audio_player.pause()

    def play_audio_narration():
        narrator.set_steps(full_narration)
        narrator.on_step_change = on_audio_step_change
        narrator.on_state_change = on_audio_state_change
        audio_player.load(proc["audio"])
        audio_player.set_volume(float(volume_scale.get()))
        audio_player.play()
        narrator.play()

    def stop_audio_narration():
        narrator.stop()
        audio_player.pause()
        clear_step_highlight()

    def toggle_audio():
        if state["is_audio_playing"]:
            stop_audio_narration()
        else:
            play_audio_narration()

    audio_play_btn.configure(command=toggle_audio)

    # ========================================================== PICTORIAL TAB
    pictorial_canvas = tk.Canvas(pictorial_tab, bg=theme["bg_main"], highlightthickness=0)
    pictorial_scroll = ttk.Scrollbar(pictorial_tab, orient="vertical",
                                      command=pictorial_canvas.yview)
    pictorial_body = tk.Frame(pictorial_canvas, bg=theme["bg_main"])
    pictorial_body.bind(
        "<Configure>",
        lambda e: pictorial_canvas.configure(scrollregion=pictorial_canvas.bbox("all")))
    pictorial_window = pictorial_canvas.create_window((0, 0), window=pictorial_body, anchor="nw")
    pictorial_canvas.bind(
        "<Configure>", lambda e: pictorial_canvas.itemconfigure(pictorial_window, width=e.width))
    pictorial_canvas.configure(yscrollcommand=pictorial_scroll.set)
    pictorial_canvas.pack(side="left", fill="both", expand=True)
    pictorial_scroll.pack(side="right", fill="y")

    def _on_pictorial_wheel(event):
        pictorial_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    pictorial_canvas.bind_all("<MouseWheel>", _on_pictorial_wheel)

    try:
        hero_img = Image.open(proc["image"])
        hero_img.thumbnail(HERO_IMAGE_SIZE)
        hero_photo = ImageTk.PhotoImage(hero_img)
        image_refs.append(hero_photo)
        tk.Label(pictorial_body, image=hero_photo, bg=theme["bg_main"]).pack(pady=(20, 16))
    except (OSError, FileNotFoundError):
        pass

    tk.Label(pictorial_body, text="Revision Checklist", bg=theme["bg_main"],
              fg=theme["text_main"], font=("Outfit", 15, "bold")).pack(anchor="w", padx=20)

    checklist_frame = tk.Frame(pictorial_body, bg=theme["bg_main"])
    checklist_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    def make_toggle_step(idx):
        def _toggle():
            info = progress_store.toggle_step(slug, idx, proc["total_steps"])
            refs = state["step_cards"][idx]
            checked = idx in info["checked_steps"]
            _apply_check_style(refs, checked)
            refresh_header_progress()
        return _toggle

    def _apply_check_style(refs, checked):
        if checked:
            refs["check"].configure(bg=theme["accent"], fg="#ffffff")
            refs["card"].configure(bg=theme["bg_surface_hover"])
        else:
            refs["check"].configure(bg=theme["bg_input"], fg=theme["text_muted"])
            refs["card"].configure(bg=theme["bg_surface"])

    initial_info = progress_store.get_procedure_progress(slug, proc["total_steps"])

    def make_read_step(idx):
        def _read():
            narrator.stop()
            title = proc["steps"][idx]
            desc = proc["step_descriptions"][idx]
            narrator.set_steps([f"{title}. {desc}"])
            narrator.speak_step(0)
        return _read

    for idx, (title, desc) in enumerate(zip(proc["steps"], proc["step_descriptions"])):
        card = tk.Frame(checklist_frame, bg=theme["bg_surface"], highlightbackground=theme["border"],
                         highlightthickness=1)
        card.pack(fill="x", pady=6)

        top_row = tk.Frame(card, bg=theme["bg_surface"])
        top_row.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(top_row, text=str(idx + 1), bg=theme["accent"], fg="#ffffff",
                  font=("Inter", 9, "bold"), width=2).pack(side="left")
        tk.Label(top_row, text=title, bg=theme["bg_surface"], fg=theme["text_main"],
                  font=("Outfit", 12, "bold")).pack(side="left", padx=(10, 0))

        check_label = tk.Label(top_row, text="✓", bg=theme["bg_input"],
                                fg=theme["text_muted"], font=("Inter", 10, "bold"), width=2)
        check_label.pack(side="right")
        check_label.bind("<Button-1>", lambda e, i=idx: make_toggle_step(i)())
        check_label.configure(cursor="hand2")

        tk.Label(card, text=desc, bg=theme["bg_surface"], fg=theme["text_muted"],
                  font=("Inter", 9), anchor="w", justify="left", wraplength=700).pack(
            fill="x", padx=14)

        read_btn = tk.Button(card, text="\U0001F50A Read Step", command=make_read_step(idx),
                              bg=theme["bg_input"], fg=theme["text_main"], relief="flat",
                              font=("Inter", 8), cursor="hand2")
        read_btn.pack(anchor="w", padx=14, pady=(6, 12))

        state["step_cards"][idx] = {"card": card, "check": check_label}
        _apply_check_style(state["step_cards"][idx], idx in initial_info["checked_steps"])

    # =========================================================== COMBINED TAB
    combined_split = tk.Frame(combined_tab, bg=theme["bg_main"])
    combined_split.pack(fill="both", expand=True, padx=10, pady=20)

    video_col = tk.Frame(combined_split, bg=theme["bg_main"])
    video_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
    video_label = tk.Label(video_col, bg="#000000", width=VIDEO_SIZE[0], height=VIDEO_SIZE[1])
    video_label.pack()
    video_player = VideoPlayer(app.root, video_label, default_size=VIDEO_SIZE)
    video_player.load(proc["video"])

    video_btn = tk.Button(video_col, text="▶️ Play Video",
                           bg=theme["bg_surface_hover"], fg=theme["text_main"], relief="flat",
                           font=("Inter", 9), cursor="hand2")

    def toggle_video():
        video_player.toggle()
        video_btn.configure(
            text="⏸️ Pause Video" if video_player.is_playing else "▶️ Play Video")

    video_btn.configure(command=toggle_video)
    video_btn.pack(pady=10)

    show_col = tk.Frame(combined_split, bg=theme["bg_surface"])
    show_col.pack(side="left", fill="both", expand=True)
    show_header = tk.Frame(show_col, bg=theme["bg_surface"])
    show_header.pack(fill="x", padx=16, pady=(16, 4))
    tk.Label(show_header, text="Audio-Slideshow Revision", bg=theme["bg_surface"],
              fg=theme["text_main"], font=("Inter", 10, "bold")).pack(side="left")
    slide_tracker_label = tk.Label(show_header, text=f"Step 1 of {len(proc['steps'])}",
                                    bg=theme["bg_surface"], fg=theme["text_muted"],
                                    font=("Inter", 9))
    slide_tracker_label.pack(side="right")

    slide_num_label = tk.Label(show_col, text="01", bg=theme["bg_surface"], fg=theme["accent"],
                                font=("Outfit", 28, "bold"))
    slide_num_label.pack(pady=(20, 6))
    slide_title_label = tk.Label(show_col, text="", bg=theme["bg_surface"], fg=theme["accent"],
                                  font=("Outfit", 14, "bold"), wraplength=340, justify="center")
    slide_title_label.pack(padx=16)
    slide_desc_label = tk.Label(show_col, text="", bg=theme["bg_surface"], fg=theme["text_main"],
                                 font=("Inter", 9), wraplength=340, justify="center")
    slide_desc_label.pack(padx=16, pady=(8, 20))

    nav_row = tk.Frame(show_col, bg=theme["bg_surface"])
    nav_row.pack(fill="x", padx=16)
    prev_btn = tk.Button(nav_row, text="◀ Previous", bg=theme["bg_input"],
                          fg=theme["text_main"], relief="flat", font=("Inter", 9), cursor="hand2")
    prev_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
    next_btn = tk.Button(nav_row, text="Next ▶", bg=theme["bg_input"],
                          fg=theme["text_main"], relief="flat", font=("Inter", 9), cursor="hand2")
    next_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

    combined_play_btn = tk.Button(show_col, text="▶️ Start Auto Guide",
                                   bg=theme["accent"], fg="#ffffff", relief="flat",
                                   font=("Inter", 10, "bold"), cursor="hand2")
    combined_play_btn.pack(fill="x", padx=16, pady=16)

    def display_slide(idx):
        state["combined_slide"] = idx
        slide_num_label.configure(text=f"0{idx + 1}")
        slide_title_label.configure(text=proc["steps"][idx])
        slide_desc_label.configure(text=proc["step_descriptions"][idx])
        slide_tracker_label.configure(text=f"Step {idx + 1} of {len(proc['steps'])}")
        highlight_step_card(idx)

    def update_combined_ui(is_playing):
        combined_play_btn.configure(
            text="⏸️ Pause Auto Guide" if is_playing else "▶️ Start Auto Guide")

    def stop_combined_narration():
        state["is_combined_playing"] = False
        update_combined_ui(False)
        narrator.stop()
        if state["pending_after_id"] is not None:
            app.root.after_cancel(state["pending_after_id"])
            state["pending_after_id"] = None
        clear_step_highlight()

    def speak_current_slide():
        idx = state["combined_slide"]
        text = f"Step {idx + 1}. {proc['steps'][idx]}. {proc['step_descriptions'][idx]}."
        narrator.stop()
        narrator.set_steps([text])

        def on_state(is_playing):
            if not is_playing and state["is_combined_playing"]:
                state["pending_after_id"] = app.root.after(1200, advance_slide)

        narrator.on_state_change = on_state
        narrator.play()

    def advance_slide():
        state["pending_after_id"] = None
        if not state["is_combined_playing"]:
            return
        idx = state["combined_slide"]
        if idx < len(proc["steps"]) - 1:
            display_slide(idx + 1)
            speak_current_slide()
        else:
            stop_combined_narration()

    def play_combined_narration():
        state["is_combined_playing"] = True
        update_combined_ui(True)
        display_slide(state["combined_slide"])
        speak_current_slide()

    def toggle_combined():
        if state["is_combined_playing"]:
            stop_combined_narration()
        else:
            play_combined_narration()

    combined_play_btn.configure(command=toggle_combined)

    def go_prev():
        was_playing = state["is_combined_playing"]
        stop_combined_narration()
        if state["combined_slide"] > 0:
            display_slide(state["combined_slide"] - 1)
            if was_playing:
                play_combined_narration()

    def go_next():
        was_playing = state["is_combined_playing"]
        stop_combined_narration()
        if state["combined_slide"] < len(proc["steps"]) - 1:
            display_slide(state["combined_slide"] + 1)
            if was_playing:
                play_combined_narration()

    prev_btn.configure(command=go_prev)
    next_btn.configure(command=go_next)

    display_slide(0)

    # ---------------------------------------------------------- tab switching
    def stop_everything(_evt=None):
        stop_audio_narration()
        stop_combined_narration()
        video_player.pause()
        video_btn.configure(text="▶️ Play Video")

    notebook.bind("<<NotebookTabChanged>>", stop_everything)

    root_frame.image_refs = image_refs

    def cleanup():
        pictorial_canvas.unbind_all("<MouseWheel>")
        stop_everything()
        video_player.stop()
        if state["pending_after_id"] is not None:
            app.root.after_cancel(state["pending_after_id"])
            state["pending_after_id"] = None

    return root_frame, cleanup
