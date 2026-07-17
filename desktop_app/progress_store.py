"""Step-completion progress persistence, ported from js/shared.js (localStorage -> JSON file)."""

import json
import os

PROGRESS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinicue_progress.json")


def load_progress():
    if os.path.exists(PROGRESS_PATH):
        try:
            with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_progress(progress):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f)


def get_procedure_progress(slug, total_steps):
    progress = load_progress()
    checked_steps = progress.get(slug, [])
    percent = round((len(checked_steps) / total_steps) * 100) if total_steps > 0 else 0
    return {
        "checked_steps": checked_steps,
        "percent": percent,
        "completed": percent == 100,
    }


def toggle_step(slug, step_index, total_steps):
    progress = load_progress()
    steps = progress.setdefault(slug, [])
    if step_index in steps:
        steps.remove(step_index)
    else:
        steps.append(step_index)
    save_progress(progress)
    return get_procedure_progress(slug, total_steps)
