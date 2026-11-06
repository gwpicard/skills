#!/usr/bin/env python3
"""Measure brand colours: WCAG 2 contrast and CIEDE2000 colour difference.

Usage:
  python3 colour_check.py checks.json          # table of all checks, exit code 1 if any fail
  python3 colour_check.py --pair "#222222" "#FAFAF7"   # one pair: contrast and ΔE00

checks.json:
{
  "contrast": [
    {"name": "body text on page", "fg": "#222222", "bg": "#FAFAF7", "min": 4.5},
    {"name": "accent on dark",    "fg": "#D0603A", "bg": "#181818", "min": 3}
  ],
  "distinct": [
    {"name": "card vs panel", "a": "#C9D3DC", "b": "#C6D0DA", "min": 3}
  ]
}

Thresholds: WCAG text 4.5 (large text 3), non-text graphics 3. A ΔE00 below about 2-3
reads as the same colour to most people at a glance. Colour maths: sRGB (D65) -> XYZ ->
CIELAB, CIEDE2000; no dependencies.
"""
import json, math, sys

WHITE = (0.95047, 1.0, 1.08883)


def hex2rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def xyz(h):
    r, g, b = map(lin, hex2rgb(h))
    return (0.4124564 * r + 0.3575761 * g + 0.1804375 * b,
            0.2126729 * r + 0.7151522 * g + 0.0721750 * b,
            0.0193339 * r + 0.1191920 * g + 0.9503041 * b)


def lab(h):
    x, y, z = xyz(h)

    def f(t):
        return t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29
    fx, fy, fz = f(x / WHITE[0]), f(y / WHITE[1]), f(z / WHITE[2])
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def contrast(a, b):
    la, lb = xyz(a)[1], xyz(b)[1]
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def de2000(h1, h2):
    L1, a1, b1 = lab(h1)
    L2, a2, b2 = lab(h2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dh = 0
    else:
        dh = h2p - h1p
        if dh > 180:
            dh -= 360
        elif dh < -180:
            dh += 360
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lb, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hb = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hb = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hb = (h1p + h2p + 360) / 2
    else:
        hb = (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hb - 30)) + 0.24 * math.cos(math.radians(2 * hb))
         + 0.32 * math.cos(math.radians(3 * hb + 6)) - 0.20 * math.cos(math.radians(4 * hb - 63)))
    dth = 30 * math.exp(-((hb - 275) / 25) ** 2)
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lb - 50) ** 2 / math.sqrt(20 + (Lb - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dth)) * Rc
    return math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


def main(argv):
    if len(argv) == 4 and argv[1] == '--pair':
        a, b = argv[2], argv[3]
        print(f'{a} vs {b}: contrast {contrast(a, b):.2f}:1, ΔE00 {de2000(a, b):.1f}')
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    spec = json.load(open(argv[1]))
    failed = 0
    print('| Check | Colours | Measured | Minimum | Result |\n|---|---|---|---|---|')
    for c in spec.get('contrast', []):
        v = contrast(c['fg'], c['bg'])
        ok = v >= c.get('min', 4.5)
        failed += not ok
        print(f"| {c['name']} | {c['fg']} on {c['bg']} | {v:.2f}:1 | {c.get('min', 4.5)}:1 | {'PASS' if ok else 'FAIL'} |")
    for c in spec.get('distinct', []):
        v = de2000(c['a'], c['b'])
        ok = v >= c.get('min', 3)
        failed += not ok
        print(f"| {c['name']} | {c['a']} vs {c['b']} | ΔE00 {v:.1f} | {c.get('min', 3)} | {'PASS' if ok else 'FAIL'} |")
    print(f'\n{failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
