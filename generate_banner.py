"""
Generate animated terminal-style SVG banner — 100% Logo-based (GitHub -> Code -> Vercel morphing loop).
Clean, crisp static logos + fluid particle stream morph transitions using cubic-bezier easing (.4 0 .2 1).
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, math, random

# ──── Config ────
OUT_DIR = "."
GRID_W, GRID_H = 300, 340

# Panel geometry
PANEL_X, PANEL_Y = 36, 84
PANEL_W, PANEL_H = 400, 492
TRANSLATE_X, TRANSLATE_Y = 50, 86
SCALE_X = 1.2400
SCALE_Y = 1.4471

CANVAS_W, CANVAS_H = 1180, 610

# Animation timing
INTRO_DUR   = 3.2       # seconds until loop starts
CYCLE_DUR   = 13.9      # total loop duration
NUM_INTRO_GROUPS = 60
NUM_DRIFT_BANDS  = 94
NUM_TRAVELLERS   = 1500

# 9 Keytimes for 3-logo loop cycle:
# 0.000-0.194: GitHub Hold
# 0.194-0.288: Transition to Code
# 0.288-0.432: Code Hold
# 0.432-0.525: Transition to Vercel
# 0.525-0.669: Vercel Hold
# 0.669-0.763: Transition to GitHub
# 0.763-1.000: GitHub Hold
KEY_TIMES = "0.000;0.194;0.288;0.432;0.525;0.669;0.763;0.906;1.000"
KEY_SPLINES = ".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"

# Opacity keyframes for each full logo layer (crisp during hold, smooth crossfade)
GITHUB_OPACITY = "1;1;0;0;0;0;1;1;1"
CODE_OPACITY   = "0;0;1;1;0;0;0;0;0"
VERCEL_OPACITY = "0;0;0;0;1;1;0;0;0"

# Traveller particles are ONLY visible during the transition phases (flow stream), hidden during static logo hold
TRAVELLER_OPACITY = "0;0;1;0;1;0;1;0;0"

INFO = {
    "email":     "biswalsubhamrony@gmail.com",
    "subject":   "Subham Biswal",
    "role":      "Developer . Builder . Explorer",
    "origin":    "Odisha, India",
    "education": "B.Tech CSE - GITA Autonomous",
    "status":    "Building + Learning + Shipping",
    "toolchain": "VS Code, Git, PyCharm, IntelliJ, Figma",
    "core_lang": "JavaScript, Python, Java, C",
    "frontend":  "React, Next.js, Tailwind",
    "backend":   "Node.js, Express, Flask, Django",
    "database":  "MySQL, MongoDB, Firebase, AWS",
    "ai_ml":     "TensorFlow, LLM Integration",
    "mail":      "biswalsubhamrony@gmail.com",
    "portfolio": "biswalsubham.vercel.app",
    "linkedin":  "subham-biswal",
    "github":    "@subhambiswalrony",
    "instagram": "@subhambiswal_rony",
}


def floyd_steinberg_dither(arr):
    """1-bit Floyd-Steinberg dithering."""
    h, w = arr.shape
    img = arr.copy()
    result = np.zeros((h, w), dtype=bool)
    for y in range(h):
        x_range = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
        for x in x_range:
            old = img[y, x]
            new = 255.0 if old > 127 else 0.0
            result[y, x] = new > 0
            err = old - new
            if y % 2 == 0:
                if x + 1 < w:       img[y, x+1]     += err * 7/16
                if y + 1 < h:
                    if x - 1 >= 0:   img[y+1, x-1]   += err * 3/16
                    img[y+1, x]     += err * 5/16
                    if x + 1 < w:    img[y+1, x+1]   += err * 1/16
            else:
                if x - 1 >= 0:       img[y, x-1]     += err * 7/16
                if y + 1 < h:
                    if x + 1 < w:    img[y+1, x+1]   += err * 3/16
                    img[y+1, x]     += err * 5/16
                    if x - 1 >= 0:   img[y+1, x-1]   += err * 1/16
    return result


def load_github_logo():
    """Load 25231.png alpha channel into 300x340 canvas and dither."""
    canvas = Image.new("L", (GRID_W, GRID_H), 0)
    img = Image.open("25231.png").convert("RGBA")
    img.thumbnail((220, 220), Image.LANCZOS)
    w, h = img.size
    offset = ((GRID_W - w) // 2, (GRID_H - h) // 2)
    alpha = img.split()[3]
    canvas.paste(alpha, offset)
    arr = np.array(canvas, dtype=np.float64)
    bm = floyd_steinberg_dither(arr)
    return [(x, y) for y in range(GRID_H) for x in range(GRID_W) if bm[y, x]]


def load_code_logo():
    """Render </> code symbol centered in 300x340 canvas and dither."""
    canvas = Image.new("L", (GRID_W, GRID_H), 0)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 160)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "</>", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((GRID_W - w) // 2 - bbox[0], (GRID_H - h) // 2 - bbox[1]), "</>", fill=255, font=font)
    arr = np.array(canvas, dtype=np.float64)
    bm = floyd_steinberg_dither(arr)
    return [(x, y) for y in range(GRID_H) for x in range(GRID_W) if bm[y, x]]


def load_vercel_logo():
    """Render exact Vercel triangle (path M37.5274 0L75.0548 65H0L37.5274 0Z) centered in 300x340 and dither."""
    canvas = Image.new("L", (GRID_W, GRID_H), 0)
    draw = ImageDraw.Draw(canvas)
    # Centered bold Vercel triangle: top=(150, 75), bottom-right=(255, 255), bottom-left=(45, 255)
    polygon = [(150, 75), (255, 255), (45, 255)]
    draw.polygon(polygon, fill=255)
    arr = np.array(canvas, dtype=np.float64)
    bm = floyd_steinberg_dither(arr)
    return [(x, y) for y in range(GRID_H) for x in range(GRID_W) if bm[y, x]]


def dots_to_path(dots):
    """Convert list of (x,y) to SVG path string — individual 1x1 rects."""
    return "".join(f"M{x} {y}h1v1h-1z" for x, y in dots)


def scatter_into_groups(dots, n_groups, seed=42):
    random.seed(seed)
    indices = list(range(len(dots)))
    random.shuffle(indices)
    groups = [[] for _ in range(n_groups)]
    for i, idx in enumerate(indices):
        groups[i % n_groups].append(dots[idx])
    return groups


def svg_info_row(y, label, value, accent, text_color, leader, begin):
    dots_count = max(10, 78 - len(label) - len(value) - 2)
    dots = "." * dots_count
    return f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/><text x="470" y="{y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{accent}">{label} </tspan><tspan fill="{leader}">{dots}</tspan><tspan fill="{text_color}" font-weight="600"> {value}</tspan></text></g>'


def generate_svg(is_dark=True):
    if is_dark:
        outer_bg="#070B16"; bg="url(#panelGrad)"; inner_bg="#0A101F"; dot_color="#A78BFA"; accent="#22D3EE"; violet="#7C3AED"
        emerald="#10B981"; text_c="#F8FAFC"; muted="#94A3B8"; dim="#475569"
        pill_bg="#4C1D95"; pill_text="#E9D5FF"
        panel_stroke="rgba(34,211,238,0.35)"; line_color="rgba(255,255,255,0.10)"
        title_bar="#0B1222"; title_text="#94A3B8"
        leader="rgba(148,163,184,0.35)"; border_opacity="0.55"
        glow_panel='<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>'
        panel_grad_def='<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A101F"/><stop offset="1" stop-color="#0C1426"/></linearGradient>'
    else:
        outer_bg="#F8FAFC"; bg="#F8FAFC"; inner_bg="#F8FAFC"; dot_color="#334155"; accent="#0891B2"; violet="#7C3AED"
        emerald="#059669"; text_c="#0F172A"; muted="#475569"; dim="#94A3B8"
        pill_bg="#7C3AED"; pill_text="#FFFFFF"
        panel_stroke="rgba(8,145,178,0.30)"; line_color="rgba(0,0,0,0.08)"
        title_bar="#F1F5F9"; title_text="#475569"
        leader="rgba(100,116,139,0.25)"; border_opacity="0.35"
        glow_panel='<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#0891B2" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>'
        panel_grad_def=''

    # Load 3 distinct logos in exact sequence: GitHub -> Code -> Vercel
    github_dots = load_github_logo()
    code_dots   = load_code_logo()
    vercel_dots = load_vercel_logo()

    # Match travellers across GitHub -> Code -> Vercel -> GitHub
    random.seed(42)
    n_trav = min(NUM_TRAVELLERS, len(github_dots))
    traveller_indices = random.sample(range(len(github_dots)), n_trav)
    trav_github = [github_dots[i] for i in traveller_indices]

    code_pts   = np.array(code_dots, dtype=np.float64)
    vercel_pts = np.array(vercel_dots, dtype=np.float64)

    travellers_mapped = []
    for pt in trav_github:
        sp = np.array(pt, dtype=np.float64)
        # Nearest in Code
        d1 = np.sqrt(np.sum((code_pts - sp) ** 2, axis=1))
        near_c = code_dots[np.argmin(d1)]
        # Nearest in Vercel
        d2 = np.sqrt(np.sum((vercel_pts - sp) ** 2, axis=1))
        near_v = vercel_dots[np.argmin(d2)]
        travellers_mapped.append((pt, near_c, near_v))

    # Intro groups for GitHub logo shimmer (0 - 3.2s)
    intro_groups = scatter_into_groups(github_dots, NUM_INTRO_GROUPS, seed=42)

    # Full logo paths for crisp rendering during each phase
    github_path_d = dots_to_path(github_dots)
    code_path_d   = dots_to_path(code_dots)
    vercel_path_d = dots_to_path(vercel_dots)

    print(f"  {'Dark' if is_dark else 'Light'}: GitHub ({len(github_dots)} dots), Code ({len(code_dots)} dots), Vercel ({len(vercel_dots)} dots), {n_trav} travellers")

    trav_id = "tvdark" if is_dark else "tvlight"
    p = []

    # === SVG header + defs ===
    p.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Subham Biswal -- profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{violet}"><animate attributeName="stop-color" values="{violet};{accent};{emerald};{violet}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="{accent}"><animate attributeName="stop-color" values="{accent};{emerald};{violet};{accent}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="{emerald}"><animate attributeName="stop-color" values="{emerald};{violet};{accent};{emerald}" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#60A5FA"/>
  <stop offset="0.45" stop-color="{violet}"/>
  <stop offset="1" stop-color="{accent}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 -120; 0 120; 0 -120" dur="9s" repeatCount="indefinite"/>
</linearGradient>
{panel_grad_def}
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<rect id="{trav_id}" width="2.4" height="1.7" fill="{dot_color}"/>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{outer_bg}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="{bg}"/>
<rect x="2" y="2" width="1176" height="46" fill="{title_bar}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{line_color}"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{title_text}">{INFO["email"]} - % ./profile.sh --live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="{dim}">VISUAL.MAP</text>
{glow_panel}
<rect x="36" y="84" width="400" height="492" rx="10" fill="{inner_bg}" stroke="{panel_stroke}"/>''')

    # === INTRO LAYER — GitHub logo fades in then disappears at 3.2s ===
    p.append(f'<g transform="translate({TRANSLATE_X},{TRANSLATE_Y}) scale({SCALE_X:.4f},{SCALE_Y:.4f})" fill="{dot_color}" shape-rendering="crispEdges">')
    p.append(f'<set attributeName="opacity" to="0" begin="{INTRO_DUR}s"/>')

    for i, group in enumerate(intro_groups):
        begin = 0.20 + (i / NUM_INTRO_GROUPS) * 2.0
        path_d = dots_to_path(group)
        p.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{path_d}"/></g>')

    p.append('</g>')

    # === FULL LOGO LAYERS (Clean static logos during hold phases, smooth crossfade during transitions) ===
    p.append(f'<g transform="translate({TRANSLATE_X},{TRANSLATE_Y}) scale({SCALE_X:.4f},{SCALE_Y:.4f})" fill="{dot_color}" shape-rendering="crispEdges" opacity="0">')
    p.append(f'<set attributeName="opacity" to="1" begin="{INTRO_DUR}s"/>')

    # 1. Full GitHub Logo Layer (Phase 1: 0.000 - 0.194)
    p.append(f'<g opacity="1"><animate attributeName="opacity" values="{GITHUB_OPACITY}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{KEY_SPLINES}"/><path d="{github_path_d}"/></g>')

    # 2. Full Code Logo Layer (Phase 2: 0.288 - 0.432)
    p.append(f'<g opacity="0"><animate attributeName="opacity" values="{CODE_OPACITY}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{KEY_SPLINES}"/><path d="{code_path_d}"/></g>')

    # 3. Full Vercel Triangle Logo Layer (Phase 3: 0.525 - 0.669)
    p.append(f'<g opacity="0"><animate attributeName="opacity" values="{VERCEL_OPACITY}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{KEY_SPLINES}"/><path d="{vercel_path_d}"/></g>')

    p.append('</g>')

    # === TRAVELLER LAYER — Morphs particles ONLY during transition phases, hidden during logo hold ===
    p.append(f'<g transform="translate({TRANSLATE_X},{TRANSLATE_Y}) scale({SCALE_X:.4f},{SCALE_Y:.4f})">')
    for pt, c, v in travellers_mapped:
        gx, gy = pt
        cx, cy = c
        vx, vy = v
        translate_values = f"{gx} {gy};{gx} {gy};{cx} {cy};{cx} {cy};{vx} {vy};{vx} {vy};{gx} {gy};{gx} {gy};{gx} {gy}"
        p.append(f'<use href="#{trav_id}" opacity="0"><animate attributeName="opacity" values="{TRAVELLER_OPACITY}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{KEY_SPLINES}"/><animateTransform attributeName="transform" type="translate" values="{translate_values}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite" calcMode="spline" keySplines="{KEY_SPLINES}"/></use>')
    p.append('</g>')

    # === Corner brackets ===
    p.append(f'''<path d="M 50 84 L 36 84 L 36 98" fill="none" stroke="{accent}" stroke-width="2" opacity="0.8"/>
<path d="M 422 84 L 436 84 L 436 98" fill="none" stroke="{accent}" stroke-width="2" opacity="0.8"/>
<path d="M 50 576 L 36 576 L 36 562" fill="none" stroke="{accent}" stroke-width="2" opacity="0.8"/>
<path d="M 422 576 L 436 576 L 436 562" fill="none" stroke="{accent}" stroke-width="2" opacity="0.8"/>''')

    # === Right panel: SYSTEM.INFO ===
    p.append(f'''<text x="470" y="106" font-size="13" letter-spacing="2" fill="{accent}" filter="url(#txtGlow)">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="{line_color}"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="#F87171" font-weight="700"><tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>''')

    # Email pill
    p.append(f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>
<rect x="470" y="122" width="258" height="20" rx="4" fill="{pill_bg}"/>
<text x="479" y="136" font-size="14" font-weight="700" fill="{pill_text}">{INFO["email"]}</text>
<line x1="738" y1="130" x2="1125" y2="130" stroke="{line_color}"/>
</g>''')

    # Info rows
    y_pos = 162; begin = 0.90
    for label, value in [("Subject", INFO["subject"]), ("Role", INFO["role"]),
                          ("Origin", INFO["origin"]), ("Education", INFO["education"]),
                          ("Status", INFO["status"]), ("ToolChain", INFO["toolchain"])]:
        p.append(svg_info_row(y_pos, label, value, accent, text_c, leader, begin))
        y_pos += 23; begin += 0.12

    p.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{muted}">- Skills </tspan><tspan fill="{leader}">----------------------------------------------------------------------</tspan></text></g>')
    y_pos += 23; begin += 0.12

    for label, value in [("Core.Lang", INFO["core_lang"]), ("Core.Frontend", INFO["frontend"]),
                          ("Core.Backend", INFO["backend"]), ("Core.Database", INFO["database"]),
                          ("Core.AI_ML", INFO["ai_ml"])]:
        p.append(svg_info_row(y_pos, label, value, accent, text_c, leader, begin))
        y_pos += 23; begin += 0.12

    p.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{muted}">- Contact </tspan><tspan fill="{leader}">---------------------------------------------------------------------</tspan></text></g>')
    y_pos += 23; begin += 0.12

    for label, value in [("Grid.Mail", INFO["mail"]), ("Grid.Portfolio", INFO["portfolio"]),
                          ("Grid.LinkedIn", INFO["linkedin"]), ("Grid.GitHub", INFO["github"]),
                          ("Grid.Instagram", INFO["instagram"])]:
        p.append(svg_info_row(y_pos, label, value, accent, text_c, leader, begin))
        y_pos += 23; begin += 0.12

    p.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin:.2f}s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" fill="{muted}">&#9656; More about me &amp; projects below &#8595; <tspan fill="{accent}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text></g>')

    # Close clip + border
    p.append(f'''</g>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="{border_opacity}" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>''')

    return "\n".join(p)


def main():
    print("=== Generating SVG banners (Clean static logos + fluid particle transitions) ===\n")

    print("[1/2] Generating dark.svg...")
    dark_svg = generate_svg(is_dark=True)
    with open(os.path.join(OUT_DIR, "dark.svg"), "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"  Wrote dark.svg ({len(dark_svg):,} bytes)")

    print("[2/2] Generating light.svg...")
    light_svg = generate_svg(is_dark=False)
    with open(os.path.join(OUT_DIR, "light.svg"), "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"  Wrote light.svg ({len(light_svg):,} bytes)")

    print("\nDone! Animation: GitHub logo -> Code logo -> Vercel triangle logo -> GitHub logo")


if __name__ == "__main__":
    main()
