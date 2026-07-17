"""ClinCue procedure data, ported from index.html and procedures/*.html."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")

APP_NAME = "ClinCue"


def _media(kind, slug, ext):
    return os.path.join(MEDIA_DIR, kind, f"{slug}.{ext}")


PROCEDURES = [
    {
        "slug": "urinary-catheterisation",
        "title": "Urinary Catheterisation",
        "subtitle": "Revision of sterile insertion protocols, patient preparation, "
                     "insertion guidelines, and catheter securement.",
        "meta": "Audio + Pictorial",
        "steps": [
            "Preparation & Consent",
            "Sterile Field Setup",
            "Patient Preparation",
            "Insertion of Catheter",
            "Inflation & Securing",
            "Connection & Clean",
        ],
        "step_descriptions": [
            "Gather necessary catheter kit, verify patient name, explain procedure details, "
            "perform hand hygiene.",
            "Create a sterile workspace by opening the catheter tray kit using aseptic "
            "technique, don sterile surgical gloves, and place sterile drapes.",
            "Cleanse periurethral area using antiseptic solution (front-to-back sweeps for "
            "females, circular sweeps for males).",
            "Apply sterile lubricant, gently insert catheter through the urethra until urine "
            "flow is visible in tubing, then advance an extra 1-2 inches.",
            "Inflate retention balloon using 10cc sterile water, gently pull catheter until "
            "seated, and secure connection to patient's thigh.",
            "Connect drainage tube to bag, clean genital area of prep residue, dispose of "
            "waste materials, wash hands, and document output.",
        ],
    },
    {
        "slug": "cardiopulmonary-resuscitation",
        "title": "Cardiopulmonary Resuscitation",
        "subtitle": "Review emergency cardiac life support steps, 30:2 compression-to-"
                     "ventilation ratio, and AED safety operating procedures.",
        "meta": "Audio + Video",
        "steps": [
            "Scene Safety & Responsiveness",
            "Activate Emergency Response",
            "High-Quality Chest Compressions",
            "Rescue Breaths",
            "AED Operation",
        ],
        "step_descriptions": [
            "Confirm scene safety, tap patient's shoulder and shout 'Are you okay?', and check "
            "breathing and pulse (max 10 seconds).",
            "Call for help, send someone to retrieve an AED, and contact emergency services "
            "immediately.",
            "Place heel of one hand on lower half of sternum, compress at depth of 2-2.4 "
            "inches, and speed of 100-120 compressions per minute.",
            "Perform head-tilt, chin-lift to open airway, and deliver 2 rescue breaths (1 "
            "second each) after every 30 compressions.",
            "Turn on the AED, apply pads to bare chest, follow vocal prompts, clear the "
            "patient during rhythm analysis, and deliver shock if advised.",
        ],
    },
    {
        "slug": "intravenous-cannulation",
        "title": "Intravenous Cannulation",
        "subtitle": "Revision of venipuncture site selection, sterile skin preparation, "
                     "proper insertion angle, flashback checks, and securing.",
        "meta": "Audio + Pictorial",
        "steps": [
            "Gather Equipment & Select Site",
            "Aseptic Prep",
            "Venipuncture",
            "Advance Cannula",
            "Secure & Flush",
        ],
        "step_descriptions": [
            "Explain procedure, apply tourniquet, and identify a suitable vein (e.g., "
            "cephalic or median cubital vein).",
            "Clean the injection site with 2% chlorhexidine in 70% isopropyl alcohol for 30 "
            "seconds using friction, and allow it to dry completely.",
            "Anchor the vein, insert the cannula bevel up at a 15-30 degree angle, and "
            "observe for blood flashback in the chamber.",
            "Lower the angle slightly, advance the needle 1-2mm further, then slide the "
            "plastic cannula off the needle into the vein.",
            "Release the tourniquet, apply pressure above the cannula tip, withdraw the "
            "needle safely, attach the saline flush to test patency, and secure with a "
            "transparent dressing.",
        ],
    },
    {
        "slug": "sterile-wound-dressing",
        "title": "Sterile Wound Dressing",
        "subtitle": "Step-by-step revision of wound assessment, removing old dressings, "
                     "establishing an aseptic field, and cleansing rules.",
        "meta": "Audio + Pictorial",
        "steps": [
            "Assess & Prepare",
            "Remove Old Dressing",
            "Establish Sterile Field",
            "Cleanse Wound",
            "Apply Dressing",
        ],
        "step_descriptions": [
            "Explain the procedure, perform hand hygiene, position the patient comfortably, "
            "and prepare a clean waste container.",
            "Don clean non-sterile gloves, gently peel the old dressing off in the direction "
            "of hair growth, assess the wound drainage, and dispose of the dressing.",
            "Wash hands, open the sterile wound dressing pack using aseptic technique to "
            "create a sterile field, and arrange instruments and saline.",
            "Don sterile gloves, wet gauze with sterile normal saline, and wipe the wound "
            "gently from the least contaminated (center) to the most contaminated (outer "
            "edges) using one swipe per gauze pad.",
            "Pat the surrounding skin dry with sterile dry gauze, apply the primary dressing "
            "layer, cover with the secondary protective dressing, secure with medical tape, "
            "and wash hands.",
        ],
    },
]

for _proc in PROCEDURES:
    _proc["total_steps"] = len(_proc["steps"])
    _proc["image"] = _media("images", _proc["slug"], "jpg")
    _proc["audio"] = _media("audio", _proc["slug"], "mp3")
    _proc["video"] = _media("video", _proc["slug"], "mp4")


def get_procedure(slug):
    for proc in PROCEDURES:
        if proc["slug"] == slug:
            return proc
    raise KeyError(f"Unknown procedure slug: {slug}")
