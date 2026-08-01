"""
Generate animated terminal-style SVG banner — matches arifhaxn architecture exactly.

Architecture:
  1. Intro layer: ~60 groups fade in over ~2s, then `<set opacity="0" begin="3.2s"/>`
  2. Loop layer: ~94 drift bands, each with translate+opacity keyframes over 13.9s
     Phase: portrait(2.7s) → transition(1.3s) → logo1(2.7s) → transition(1.3s) → logo2(2.7s) → transition(1.3s)
  3. All dots are individual 1×1 pixels using path "M{x} {y}h1v1h-1z"
  4. Portrait grid: 300×340, scaled via transform to fit 400×492 panel
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import os, math, random

# ──── Config ────
PHOTO_PATH   = "168572456.jpg"
OUT_DIR      = "."
GRID_W, GRID_H = 300, 340

# Panel geometry
PANEL_X, PANEL_Y = 36, 84
PANEL_W, PANEL_H = 400, 492
TRANSLATE_X, TRANSLATE_Y = 50, 86
SCALE_X = PANEL_W / GRID_W    # ~1.333
SCALE_Y = PANEL_H / GRID_H    # ~1.447

CANVAS_W, CANVAS_H = 1180, 610

# Animation
INTRO_DUR   = 3.2       # seconds until loop starts
CYCLE_DUR   = 13.9      # total loop duration
NUM_INTRO_GROUPS = 60
NUM_DRIFT_BANDS  = 94

# keyTimes for 2-logo loop (7 values)
KEY_TIMES = "0.000;0.200;0.300;0.500;0.600;0.800;1.000"

# Portrait loop opacity (visible during portrait, hidden during logo 1 & 2)
PORTRAIT_OPACITY = "1;1;0;0;0;0;1"

# Traveller opacity (hidden during portrait, visible during logo 1 & 2)
TRAVELLER_OPACITY = "0;0;1;1;1;1;0"

NUM_TRAVELLERS = 900

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


def load_and_prepare(path, grid_w, grid_h, for_dark=False):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    target_ratio = grid_w / grid_h
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        img = img.crop((0, 0, w, min(new_h, h)))

    img = img.resize((grid_w, grid_h), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float64)

    if for_dark:
        # Invert: light bg -> dark (few dots), dark subject -> light (many dots)
        arr = 255.0 - arr
        arr = np.clip(arr * 1.4, 0, 255)
    return arr


def floyd_steinberg_dither(arr):
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


def get_dot_list(bitmap):
    """Return list of (x, y) for all active dots."""
    dots = []
    h, w = bitmap.shape
    for y in range(h):
        for x in range(w):
            if bitmap[y, x]:
                dots.append((x, y))
    return dots


def dots_to_path(dots):
    """Convert list of (x,y) to SVG path string — individual 1x1 rects."""
    return "".join(f"M{x} {y}h1v1h-1z" for x, y in dots)


def make_logo_bitmap(text, grid_w, grid_h, font_size=200):
    """Create a dithered bitmap from text."""
    img = Image.new("L", (grid_w, grid_h), 0)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (grid_w - tw) // 2 - bbox[0]
    y = (grid_h - th) // 2 - bbox[1]
    draw.text((x, y), text, fill=255, font=font)
    return floyd_steinberg_dither(np.array(img, dtype=np.float64))


def make_vercel_bitmap(grid_w, grid_h):
    """Create Vercel triangle bitmap."""
    img = Image.new("L", (grid_w, grid_h), 0)
    draw = ImageDraw.Draw(img)
    cx, cy = grid_w // 2, grid_h // 2
    size = min(grid_w, grid_h) // 3
    draw.polygon([(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)], fill=255)
    return floyd_steinberg_dither(np.array(img, dtype=np.float64))


def compute_centroid(dots):
    if not dots:
        return (150, 170)
    xs = [d[0] for d in dots]
    ys = [d[1] for d in dots]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def scatter_into_groups(dots, n_groups, seed=42):
    """Scatter dots into groups ensuring spatial evenness."""
    random.seed(seed)
    indices = list(range(len(dots)))
    random.shuffle(indices)
    groups = [[] for _ in range(n_groups)]
    for i, idx in enumerate(indices):
        groups[i % n_groups].append(dots[idx])
    return groups


def compute_drift_offsets(dots_group, target_centroid):
    """Compute the translate offset to move this group's centroid toward the target."""
    if not dots_group:
        return (0, 0)
    cx, cy = compute_centroid(dots_group)
    # Move ~42% toward the target
    dx = int((target_centroid[0] - cx) * 0.42)
    dy = int((target_centroid[1] - cy) * 0.42)
    return (dx, dy)


def match_dots_nearest(src_positions, dst_positions, n_travellers):
    random.seed(42)
    # Sample traveler indices from source
    src_indices = random.sample(range(len(src_positions)), min(n_travellers, len(src_positions)))
    src_pts = np.array([src_positions[i] for i in src_indices], dtype=np.float64)
    dst_pts = np.array(dst_positions, dtype=np.float64)
    
    matched = []
    used_dst = set()
    for i, sp in enumerate(src_pts):
        dists = np.sqrt(np.sum((dst_pts - sp) ** 2, axis=1))
        order = np.argsort(dists)
        for j in order:
            if j not in used_dst:
                used_dst.add(j)
                matched.append((src_indices[i], sp, dst_pts[j]))
                break
        else:
            j = order[0]
            matched.append((src_indices[i], sp, dst_pts[j]))
    return matched


def svg_info_row(y, label, value, accent, text_color, leader, begin):
    dots_count = max(10, 78 - len(label) - len(value) - 2)
    dots = "." * dots_count
    return f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/><text x="470" y="{y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{accent}">{label} </tspan><tspan fill="{leader}">{dots}</tspan><tspan fill="{text_color}" font-weight="600"> {value}</tspan></text></g>'


def generate_svg(portrait_bitmap, is_dark=True):
    if is_dark:
        bg="#0A101F"; dot_color="#A78BFA"; accent="#22D3EE"; violet="#A78BFA"
        emerald="#10B981"; text_c="#F8FAFC"; muted="#94A3B8"; dim="#475569"
        pill_bg="#4C1D95"; pill_text="#E9D5FF"
        panel_stroke="rgba(34,211,238,0.35)"; line_color="rgba(255,255,255,0.10)"
        title_bar="#0B1222"; title_text="#94A3B8"
        leader="rgba(148,163,184,0.35)"; border_opacity="0.55"
        glow_panel='<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>'
    else:
        bg="#F8FAFC"; dot_color="#334155"; accent="#0891B2"; violet="#7C3AED"
        emerald="#059669"; text_c="#0F172A"; muted="#475569"; dim="#94A3B8"
        pill_bg="#7C3AED"; pill_text="#FFFFFF"
        panel_stroke="rgba(8,145,178,0.30)"; line_color="rgba(0,0,0,0.08)"
        title_bar="#F1F5F9"; title_text="#475569"
        leader="rgba(100,116,139,0.25)"; border_opacity="0.35"
        glow_panel='<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#0891B2" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>'

    portrait_dots = get_dot_list(portrait_bitmap)

    # Generate logo bitmaps
    vercel_bm = make_vercel_bitmap(GRID_W, GRID_H)
    code_bm = make_logo_bitmap("</>", GRID_W, GRID_H, font_size=200)
    logo1_dots = get_dot_list(vercel_bm)
    logo2_dots = get_dot_list(code_bm)
    logo1_centroid = compute_centroid(logo1_dots)

    # Match travellers to Vercel and Code logos
    random.seed(42)
    n_trav = min(NUM_TRAVELLERS, len(portrait_dots))
    traveller_indices = random.sample(range(len(portrait_dots)), n_trav)
    traveller_portrait_pts = [portrait_dots[i] for i in traveller_indices]
    
    logo1_pts = np.array(logo1_dots, dtype=np.float64)
    logo2_pts = np.array(logo2_dots, dtype=np.float64)
    
    travellers_mapped = []
    for pt in traveller_portrait_pts:
        sp = np.array(pt, dtype=np.float64)
        # Nearest in logo1 (Vercel)
        d1 = np.sqrt(np.sum((logo1_pts - sp) ** 2, axis=1))
        nearest_l1 = logo1_dots[np.argmin(d1)]
        # Nearest in logo2 (Code)
        d2 = np.sqrt(np.sum((logo2_pts - sp) ** 2, axis=1))
        nearest_l2 = logo2_dots[np.argmin(d2)]
        travellers_mapped.append((pt, nearest_l1, nearest_l2))

    # Intro groups (scattered for shimmer effect)
    intro_groups = scatter_into_groups(portrait_dots, NUM_INTRO_GROUPS, seed=42)

    # Drift bands for loop layer (same dots, different grouping for drift)
    drift_bands = scatter_into_groups(portrait_dots, NUM_DRIFT_BANDS, seed=99)

    total = len(portrait_dots)
    print(f"  {'Dark' if is_dark else 'Light'}: {total} portrait dots, {len(logo1_dots)} vercel dots, {len(logo2_dots)} code dots, {n_trav} travellers")

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
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<rect id="{trav_id}" width="2.4" height="1.7" fill="{dot_color}"/>
</defs>''')

    # === Background + chrome ===
    p.append(f'''<rect x="2" y="2" width="1176" height="606" rx="18" fill="{bg}"/>
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
<rect x="36" y="84" width="400" height="492" rx="10" fill="{bg}" stroke="{panel_stroke}"/>''')

    # === INTRO LAYER — fades in then disappears at 3.2s ===
    p.append(f'<g transform="translate({TRANSLATE_X},{TRANSLATE_Y}) scale({SCALE_X:.4f},{SCALE_Y:.4f})" fill="{dot_color}" shape-rendering="crispEdges">')
    p.append(f'<set attributeName="opacity" to="0" begin="{INTRO_DUR}s"/>')

    for i, group in enumerate(intro_groups):
        begin = 0.20 + (i / NUM_INTRO_GROUPS) * 2.0
        path_d = dots_to_path(group)
        p.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{path_d}"/></g>')

    p.append('</g>')

    # === LOOP LAYER — appears at 3.2s, drift bands animate ===
    p.append(f'<g transform="translate({TRANSLATE_X},{TRANSLATE_Y}) scale({SCALE_X:.4f},{SCALE_Y:.4f})" fill="{dot_color}" shape-rendering="crispEdges" opacity="0">')
    p.append(f'<set attributeName="opacity" to="1" begin="{INTRO_DUR}s"/>')

    for i, band in enumerate(drift_bands):
        if not band:
            continue
        dx, dy = compute_drift_offsets(band, logo1_centroid)
        translate_values = f"0 0;0 0;{-dx} {-dy};{-dx} {-dy};{-dx} {-dy};{-dx} {-dy};0 0"
        path_d = dots_to_path(band)
        p.append(f'<g opacity="1"><animate attributeName="opacity" values="{PORTRAIT_OPACITY}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="{translate_values}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite"/><path d="{path_d}"/></g>')

    p.append('</g>')

    # === TRAVELLER LAYER — morphs between photo ↔ Vercel ↔ Code ===
    p.append(f'<g transform="translate({TRANSLATE_X},{TRANSLATE_Y}) scale({SCALE_X:.4f},{SCALE_Y:.4f})">')
    for pt, l1, l2 in travellers_mapped:
        px, py = pt
        l1x, l1y = l1
        l2x, l2y = l2
        translate_values = f"{px} {py};{px} {py};{l1x} {l1y};{l1x} {l1y};{l2x} {l2y};{l2x} {l2y};{px} {py}"
        p.append(f'<use href="#{trav_id}" opacity="0"><animate attributeName="opacity" values="{TRAVELLER_OPACITY}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="{translate_values}" keyTimes="{KEY_TIMES}" dur="{CYCLE_DUR}s" begin="{INTRO_DUR}s" repeatCount="indefinite"/></use>')
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
    print("=== Generating SVG banners (arifhaxn architecture) ===\n")

    print("[1/4] Processing dark mode...")
    arr_dark = load_and_prepare(PHOTO_PATH, GRID_W, GRID_H, for_dark=True)
    bm_dark = floyd_steinberg_dither(arr_dark)

    print("[2/4] Processing light mode...")
    arr_light = load_and_prepare(PHOTO_PATH, GRID_W, GRID_H, for_dark=False)
    bm_light = floyd_steinberg_dither(arr_light)

    print("[3/4] Generating dark.svg...")
    dark_svg = generate_svg(bm_dark, is_dark=True)
    with open(os.path.join(OUT_DIR, "dark.svg"), "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"  Wrote dark.svg ({len(dark_svg):,} bytes)")

    print("[4/4] Generating light.svg...")
    light_svg = generate_svg(bm_light, is_dark=False)
    with open(os.path.join(OUT_DIR, "light.svg"), "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"  Wrote light.svg ({len(light_svg):,} bytes)")

    print("\nDone! Animation: portrait shimmer -> drift toward logo -> loop")


if __name__ == "__main__":
    main()
