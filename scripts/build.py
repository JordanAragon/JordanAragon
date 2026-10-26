#!/usr/bin/env python3
"""Genera las imágenes del perfil de GitHub (assets/*.svg) en versión clara y oscura.

Uso: python3 scripts/build.py
Requiere: pip install fonttools brotli
Opcional: GITHUB_TOKEN para la tarjeta de actividad (contribuciones y lenguajes).
"""
import base64, io, json, math, os, sys, urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).parent))
import datos as D

RAIZ = Path(__file__).resolve().parent.parent
REC = RAIZ / "scripts" / "recursos"
SALIDA = RAIZ / "assets"
METRICAS = json.loads((REC / "metricas.json").read_text())
ICONOS = json.loads((REC / "iconos.json").read_text())
USUARIO = "JordanAragon"
W = 1200  # ancho base de todas las piezas

TEMAS = {
    "oscuro": dict(bg="#0E1013", sup="#14171C", borde="#262A31", texto="#EDEDEA", suave="#9A9DA4", tenue="#5C6069",
                   punto="#ECECE8", acento="#3FB950", rejilla="#1B1F25", fondo_ico="#1C2027"),
    "claro": dict(bg="#FBFBF9", sup="#FFFFFF", borde="#E3E1DB", texto="#141414", suave="#5F5E59", tenue="#A6A49D",
                  punto="#141414", acento="#1A7F37", rejilla="#EEEDE8", fondo_ico="#F3F2EE"),
}

FUENTES = {
    "I": REC / "inter-latin-var.woff2",
    "M4": REC / "jetbrains-mono-latin-400.woff2",
    "M5": REC / "jetbrains-mono-latin-500.woff2",
}


# ---------- texto ----------
def ancho(texto, fam="I", peso=400, tam=16, ls=0.0):
    tabla = METRICAS[f"inter{peso}"] if fam == "I" else METRICAS[f"mono{peso}"]
    return sum(tabla.get(c, 0.6) for c in texto) * tam + ls * max(0, len(texto) - 1)


def partir(texto, max_w, fam="I", peso=400, tam=16):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if actual and ancho(prueba, fam, peso, tam) > max_w:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


class Lienzo:
    """Acumula el SVG y los caracteres usados por cada fuente para recortarlas."""

    def __init__(self, ancho_, alto, tema, titulo):
        self.w, self.h, self.t, self.titulo = ancho_, alto, TEMAS[tema], titulo
        self.partes, self.css, self.usados = [], [], {"I": set(), "M4": set(), "M5": set()}

    def add(self, s):
        self.partes.append(s)

    def texto(self, x, y, s, fam="I", peso=400, tam=16, color=None, ls=0, ancla="start", clase="", estilo="", extra=""):
        clave = "I" if fam == "I" else ("M5" if peso >= 500 else "M4")
        self.usados[clave].update(s)
        familia = "I" if fam == "I" else "M"
        p = self.t
        attrs = f'x="{x:.1f}" y="{y:.1f}" font-family="{familia}" font-weight="{peso}" font-size="{tam}" fill="{color or p["texto"]}"'
        if ls:
            attrs += f' letter-spacing="{ls}"'
        if ancla != "start":
            attrs += f' text-anchor="{ancla}"'
        if clase:
            attrs += f' class="{clase}"'
        if estilo:
            attrs += f' style="{estilo}"'
        self.add(f"<text {attrs}{extra}>{escape(s)}</text>")

    def fuentes_css(self):
        reglas = []
        for clave, usados in self.usados.items():
            if not usados:
                continue
            texto = "".join(sorted(usados | {" "}))
            fuente = TTFont(FUENTES[clave])
            opciones = subset.Options()
            opciones.flavor = "woff2"
            opciones.layout_features = ["kern", "liga", "calt", "tnum"]
            opciones.name_IDs = []
            sub = subset.Subsetter(opciones)
            sub.populate(text=texto)
            sub.subset(fuente)
            buf = io.BytesIO()
            fuente.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            familia = "I" if clave == "I" else "M"
            peso = "100 900" if clave == "I" else ("500" if clave == "M5" else "400")
            reglas.append(f"@font-face{{font-family:{familia};src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:{peso}}}")
        return "".join(reglas)

    def svg(self):
        css = self.fuentes_css() + ANIMACIONES + "".join(self.css)
        cuerpo = "".join(self.partes)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'role="img" aria-label="{escape(self.titulo)}"><title>{escape(self.titulo)}</title><style>{css}</style>{cuerpo}</svg>')


ANIMACIONES = (
    ".f{opacity:0;animation:f .9s cubic-bezier(.2,.7,.2,1) forwards}"
    "@keyframes f{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}"
    ".p{opacity:0;transform-box:fill-box;transform-origin:center;animation:p .5s cubic-bezier(.3,1.5,.5,1) forwards}"
    "@keyframes p{from{opacity:0;transform:scale(0)}to{opacity:1;transform:scale(1)}}"
    ".t{animation-name:t;animation-fill-mode:forwards}"
    "@keyframes t{99%{opacity:1}to{transform:translateX(var(--w));opacity:0}}"
    ".b{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}"
    ".o{transform-box:fill-box;transform-origin:center;animation:o 2.2s ease-out infinite}"
    "@keyframes o{0%{transform:scale(1);opacity:.55}100%{transform:scale(3.2);opacity:0}}"
    ".l{stroke-dasharray:var(--d);stroke-dashoffset:var(--d);animation:l 1.4s cubic-bezier(.6,0,.2,1) forwards}"
    "@keyframes l{to{stroke-dashoffset:0}}"
    "@media (prefers-reduced-motion:reduce){.f,.p{animation:none;opacity:1}.t{display:none}.b,.o{animation:none}.l{animation:none;stroke-dashoffset:0}}"
)


def marco(c, r=20):
    p = c.t
    c.add(f'<rect x="0.5" y="0.5" width="{c.w-1}" height="{c.h-1}" rx="{r}" fill="{p["bg"]}" stroke="{p["borde"]}"/>')


def rejilla_puntos(c, x, y, w, h, paso=24):
    p = c.t
    c.add(f'<defs><pattern id="g" width="{paso}" height="{paso}" patternUnits="userSpaceOnUse">'
          f'<circle cx="1" cy="1" r="1" fill="{p["rejilla"]}"/></pattern></defs>'
          f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g)"/>')


def escribir(c, x, y, s, demora, color, fondo, tam=15, peso=400, vel=0.045):
    """Texto mono que aparece letra por letra: una cortina del color del fondo se corre con steps()."""
    c.texto(x, y, s, fam="M", peso=peso, tam=tam, color=color)
    w = ancho(s, "M", peso, tam) + 4
    n = max(1, len(s))
    c.add(f'<rect class="t" x="{x-1:.1f}" y="{y-tam:.1f}" width="{w+12:.1f}" height="{tam*1.45:.1f}" fill="{fondo}" '
          f'style="--w:{w+12:.1f}px;animation-duration:{n*vel:.2f}s;animation-timing-function:steps({n});animation-delay:{demora:.2f}s"/>')
    return demora + n * vel


def encabezado(c, x, y, numero, etiqueta, titulo, demora=0.0):  # noqa: E302
    p = c.t
    c.texto(x, y, f"{numero} — {etiqueta.upper()}", fam="M", peso=500, tam=13, color=p["suave"], ls=1.5, clase="f",
            estilo=f"animation-delay:{demora:.2f}s")
    c.texto(x, y + 44, titulo, peso=700, tam=34, ls=-1, clase="f", estilo=f"animation-delay:{demora+.1:.2f}s")


# ---------- piezas ----------
def hero(tema):
    c = Lienzo(W, 480, tema, f"{D.NOMBRE} — {D.TITULO}: {D.TITULO_2}")
    p = c.t
    marco(c, 24)
    rejilla_puntos(c, 1, 1, W - 2, 478)
    x = 64
    t = escribir(c, x, 92, f"{D.PROMPT} whoami", 0.2, p["suave"], p["bg"], tam=15)
    c.texto(x, 196, D.NOMBRE, peso=800, tam=88, ls=-3.5, clase="f", estilo=f"animation-delay:{t+.05:.2f}s")
    c.texto(x, 244, D.TITULO, peso=600, tam=24, ls=-0.4, clase="f", estilo=f"animation-delay:{t+.2:.2f}s")
    c.texto(x, 276, D.TITULO_2, peso=400, tam=24, ls=-0.4, color=p["suave"], clase="f", estilo=f"animation-delay:{t+.28:.2f}s")
    for i, linea in enumerate(partir(D.TITULAR, 520, "I", 400, 18)):
        c.texto(x, 324 + i * 28, linea, tam=18, color=p["suave"], clase="f", estilo=f"animation-delay:{t+.4+i*.06:.2f}s")
    # estado
    yb = 412
    c.add(f'<g class="f" style="animation-delay:{t+.6:.2f}s">'
          f'<circle cx="{x+6}" cy="{yb-5}" r="5" fill="{p["acento"]}" class="o"/><circle cx="{x+6}" cy="{yb-5}" r="5" fill="{p["acento"]}"/></g>')
    c.texto(x + 22, yb, D.ESTADO, peso=500, tam=15, clase="f", estilo=f"animation-delay:{t+.6:.2f}s")
    c.texto(x + 22 + ancho(D.ESTADO, "I", 500, 15) + 12, yb, D.UBICACION, fam="M", tam=14, color=p["suave"], clase="f",
            estilo=f"animation-delay:{t+.66:.2f}s")
    c.texto(x, 442, f"→ {D.SITIO}", fam="M", peso=500, tam=14, color=p["texto"], clase="f", estilo=f"animation-delay:{t+.72:.2f}s")
    # foto: panel derecho que se funde con el fondo de la tarjeta
    foto = base64.b64encode((REC / "foto-hero.webp").read_bytes()).decode()
    fx, fw, fh = W - 440, 440, 480
    c.add(f'<defs><clipPath id="marco"><rect x="1" y="1" width="{W-2}" height="{fh-2}" rx="23"/></clipPath>'
          f'<linearGradient id="fh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
          f'<stop offset=".42" stop-color="#fff" stop-opacity="1"/></linearGradient>'
          f'<linearGradient id="fv" x1="0" y1="0" x2="0" y2="1"><stop offset=".72" stop-color="#fff" stop-opacity="1"/>'
          f'<stop offset="1" stop-color="#fff" stop-opacity=".35"/></linearGradient>'
          f'<mask id="mf"><rect x="{fx}" y="0" width="{fw}" height="{fh}" fill="url(#fh)"/></mask>'
          f'<mask id="mv"><rect x="{fx}" y="0" width="{fw}" height="{fh}" fill="url(#fv)"/></mask></defs>'
          f'<g clip-path="url(#marco)"><g mask="url(#mf)"><g mask="url(#mv)"><g class="foto">'
          f'<image href="data:image/webp;base64,{foto}" x="{fx}" y="0" width="{fw}" height="{fh}" preserveAspectRatio="xMidYMid slice"/>'
          f'</g></g></g></g>')
    c.css.append(".foto{opacity:0;transform-box:fill-box;transform-origin:60% 40%;animation:fo 1.6s cubic-bezier(.2,.7,.2,1) .1s forwards}"
                 "@keyframes fo{from{opacity:0;transform:scale(1.06)}to{opacity:1;transform:scale(1)}}"
                 "@media (prefers-reduced-motion:reduce){.foto{animation:none;opacity:1}}")
    return c


def terminal(tema):
    p = TEMAS[tema]
    tam, lh, x = 15, 28, 48
    filas = []
    for tipo, s in D.TERMINAL:
        if tipo == "out":
            filas += [("out", l) for l in partir(s, W - 2 * x - 40, "M", 400, tam)]
        else:
            filas.append((tipo, s))
    yy = 92
    for tipo, _ in filas:
        if tipo == "cmd" and yy > 92:
            yy += 12
        yy += lh
    c = Lienzo(W, int(yy - lh + 36), tema, "Terminal: sobre mí y en qué estoy ahora")
    marco(c, 18)
    c.add(f'<rect x="1" y="1" width="{W-2}" height="46" rx="17" fill="{p["sup"]}"/>'
          f'<rect x="1" y="30" width="{W-2}" height="17" fill="{p["sup"]}"/>'
          f'<line x1="1" y1="47" x2="{W-1}" y2="47" stroke="{p["borde"]}"/>')
    for k in range(3):
        c.add(f'<circle cx="{28+k*20}" cy="24" r="6" fill="{p["borde"]}"/>')
    c.texto(W / 2, 29, "jordan@aragon — zsh", fam="M", tam=13, color=p["suave"], ancla="middle")
    y, t = 92, 0.3
    for tipo, s in filas:
        if tipo == "cmd":
            if y > 92:
                y += 12
            c.texto(x, y, "❯", fam="M", peso=500, tam=tam, color=p["acento"], clase="f", estilo=f"animation-delay:{t:.2f}s")
            ultimo = s == D.TERMINAL[-1][1]
            t = escribir(c, x + 22, y, s, t + 0.05, p["texto"], p["bg"], tam=tam, peso=500, vel=0.05)
            if ultimo:
                cx = x + 22 + ancho(s, "M", 500, tam) + 6
                c.add(f'<rect class="f" x="{cx:.1f}" y="{y-tam+2}" width="9" height="{tam+2}" fill="{p["texto"]}" '
                      f'style="animation-delay:{t:.2f}s"><animate attributeName="opacity" values="1;0;1" dur="1.1s" begin="{t+.3:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
            t += 0.25
        elif tipo == "item":
            c.texto(x + 22, y, "→", fam="M", tam=tam, color=p["tenue"], clase="f", estilo=f"animation-delay:{t:.2f}s")
            c.texto(x + 46, y, s, fam="M", tam=tam, color=p["suave"], clase="f", estilo=f"animation-delay:{t:.2f}s")
            t += 0.12
        else:
            c.texto(x + 22, y, s, fam="M", tam=tam, color=p["suave"], clase="f", estilo=f"animation-delay:{t:.2f}s")
            t += 0.08
        y += lh
    return c


ICONOS_SERVICIO = {
    "web": '<rect x="2.5" y="4" width="19" height="16" rx="2.5"/><path d="M2.5 8.5h19"/><circle cx="6" cy="6.3" r=".6"/><circle cx="8.3" cy="6.3" r=".6"/><path d="M8 13l-2 2 2 2M16 13l2 2-2 2M13 12l-2 6"/>',
    "ia": '<path d="M12 3l1.8 4.6L18.5 9.5l-4.7 1.9L12 16l-1.8-4.6L5.5 9.5l4.7-1.9z"/><path d="M18.5 15.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
    "auto": '<circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M7.5 6h9M6.3 8.2l4.4 7.6M17.7 8.2l-4.4 7.6"/>',
    "infra": '<rect x="3" y="3.5" width="18" height="6" rx="1.5"/><rect x="3" y="14.5" width="18" height="6" rx="1.5"/><path d="M7 6.5h.01M7 17.5h.01M11 6.5h6M11 17.5h6M12 9.5v5"/>',
}


def servicios(tema):
    c = Lienzo(W, 400, tema, "Lo que hago: producto web, IA y agentes, automatización e infraestructura")
    p = c.t
    encabezado(c, 0, 26, "01", "Lo que hago", "Producto web, IA aplicada e infraestructura.")
    gap, top = 16, 112
    cw = (W - 3 * gap) / 4
    ch = 268
    for k, (ico, titulo, desc, items) in enumerate(D.SERVICIOS):
        x = k * (cw + gap)
        d = 0.25 + k * 0.12
        c.add(f'<g class="f" style="animation-delay:{d:.2f}s">'
              f'<rect x="{x+.5:.1f}" y="{top+.5}" width="{cw-1:.1f}" height="{ch-1}" rx="16" fill="{p["sup"]}" stroke="{p["borde"]}"/>'
              f'<rect x="{x+24:.1f}" y="{top+24}" width="44" height="44" rx="11" fill="{p["fondo_ico"]}"/>'
              f'<g transform="translate({x+34:.1f} {top+34})" fill="none" stroke="{p["texto"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONOS_SERVICIO[ico]}</g></g>')
        c.texto(x + cw - 24, top + 52, f"0{k+1}", fam="M", tam=13, color=p["tenue"], ancla="end", clase="f", estilo=f"animation-delay:{d:.2f}s")
        c.texto(x + 24, top + 112, titulo, peso=600, tam=21, ls=-0.4, clase="f", estilo=f"animation-delay:{d+.05:.2f}s")
        for i, l in enumerate(partir(desc, cw - 48, "I", 400, 15)):
            c.texto(x + 24, top + 142 + i * 22, l, tam=15, color=p["suave"], clase="f", estilo=f"animation-delay:{d+.1:.2f}s")
        c.add(f'<line x1="{x+24:.1f}" y1="{top+ch-58}" x2="{x+cw-24:.1f}" y2="{top+ch-58}" stroke="{p["borde"]}" class="f" style="animation-delay:{d+.1:.2f}s"/>')
        for i, l in enumerate(partir(items, cw - 48, "M", 400, 12)):
            c.texto(x + 24, top + ch - 32 + i * 18, l, fam="M", tam=12, color=p["tenue"], clase="f", estilo=f"animation-delay:{d+.15:.2f}s")
    c.h = top + ch + 2
    return c


def luminancia(hexa):
    r, g, b = (int(hexa[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def stack(tema):
    c = Lienzo(W, 800, tema, "Stack: " + "; ".join(f"{g}: " + ", ".join(n for n, _ in items) for g, items in D.STACK))
    p = c.t
    encabezado(c, 0, 26, "02", "Stack", "Con lo que construyo.")
    y = 112
    col = 210
    alto_chip, gap = 38, 10
    idx = 0
    for grupo, items in D.STACK:
        x = col
        filas_y = y
        c.texto(0, y + 24, grupo, peso=600, tam=16, clase="f", estilo=f"animation-delay:{.2 + idx*0.015:.2f}s")
        c.texto(0, y + 44, f"{len(items):02d} herramientas", fam="M", tam=12, color=p["tenue"], clase="f",
                estilo=f"animation-delay:{.2 + idx*0.015:.2f}s")
        for nombre, slug in items:
            wt = ancho(nombre, "I", 500, 14.5)
            wc = 14 + 18 + 9 + wt + 16
            if x + wc > W:
                x = col
                filas_y += alto_chip + gap
            d = 0.25 + idx * 0.022
            g = [f'<g class="f" style="animation-delay:{d:.2f}s">',
                 f'<rect x="{x+.5:.1f}" y="{filas_y+.5:.1f}" width="{wc-1:.1f}" height="{alto_chip-1}" rx="{(alto_chip-1)/2:.1f}" fill="{p["sup"]}" stroke="{p["borde"]}"/>']
            ix, iy = x + 14, filas_y + (alto_chip - 18) / 2
            if slug and slug in ICONOS:
                color = "#" + ICONOS[slug]["hex"]
                lum = luminancia(ICONOS[slug]["hex"])
                if (tema == "oscuro" and lum < 0.09) or (tema == "claro" and lum > 0.75):
                    color = p["texto"]
                g.append(f'<g transform="translate({ix:.1f} {iy:.1f}) scale(.75)"><path d="{ICONOS[slug]["path"]}" fill="{color}"/></g>')
            else:
                g.append(f'<rect x="{ix:.1f}" y="{iy:.1f}" width="18" height="18" rx="5" fill="{p["fondo_ico"]}" stroke="{p["borde"]}"/>')
                letra = nombre[0].upper()
                c.usados["M5"].add(letra)
                g.append(f'<text x="{ix+9:.1f}" y="{iy+13:.1f}" font-family="M" font-weight="500" font-size="11" text-anchor="middle" fill="{p["suave"]}">{escape(letra)}</text>')
            c.usados["I"].update(nombre)
            g.append(f'<text x="{ix+18+9:.1f}" y="{filas_y+alto_chip/2+5:.1f}" font-family="I" font-weight="500" font-size="14.5" fill="{p["texto"]}">{escape(nombre)}</text></g>')
            c.add("".join(g))
            x += wc + gap
            idx += 1
        y = filas_y + alto_chip + 30
        c.add(f'<line x1="0" y1="{y-15}" x2="{W}" y2="{y-15}" stroke="{p["borde"]}" stroke-dasharray="2 6" class="f" style="animation-delay:.2s"/>')
    c.h = int(y - 12)
    return c


# matriz 5x7 para la letra de cada proyecto
LETRAS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
}


def proyecto(tema, k, datos):
    archivo, titulo, estado, tipo, desc, pila, url_v, _, letra = datos
    c = Lienzo(600, 320, tema, f"{titulo} — {estado}. {desc} Stack: {pila}. {url_v}")
    p = c.t
    c.add(f'<rect x="8.5" y="8.5" width="583" height="303" rx="18" fill="{p["sup"]}" stroke="{p["borde"]}"/>')
    x = 36
    d = 0.1
    c.texto(x, 60, f"{k+1:02d}", fam="M", tam=13, color=p["tenue"], clase="f", estilo=f"animation-delay:{d:.2f}s")
    # estado
    color_estado = p["acento"] if tipo == "vivo" else p["suave"]
    we = ancho(estado, "M", 500, 12) + 30
    c.add(f'<g class="f" style="animation-delay:{d:.2f}s"><rect x="{x+34:.1f}" y="43" width="{we:.1f}" height="24" rx="12" fill="{p["fondo_ico"]}" stroke="{p["borde"]}"/>'
          f'<circle cx="{x+47:.1f}" cy="55" r="3.5" fill="{color_estado}"/></g>')
    c.texto(x + 57, 59.5, estado, fam="M", peso=500, tam=12, color=p["suave"], clase="f", estilo=f"animation-delay:{d:.2f}s")
    # matriz de puntos con la letra
    filas = LETRAS[letra]
    paso, mx, my = 11, 600 - 36 - 5 * 11, 34
    pts = []
    for j, fila in enumerate(filas):
        for i, ch in enumerate(fila):
            on = ch == "1"
            pts.append(f'<circle class="p" style="animation-delay:{.2 + (i+j)*0.04:.2f}s" cx="{mx+i*paso+5:.1f}" cy="{my+j*paso+5:.1f}" r="{3.6 if on else 1.4}" fill="{p["texto"] if on else p["borde"]}"/>')
    c.add("".join(pts))
    c.texto(x, 146, titulo, peso=700, tam=34, ls=-1.2, clase="f", estilo=f"animation-delay:{d+.08:.2f}s")
    for i, l in enumerate(partir(desc, 600 - 2 * x - 10, "I", 400, 15.5)):
        c.texto(x, 182 + i * 23, l, tam=15.5, color=p["suave"], clase="f", estilo=f"animation-delay:{d+.14:.2f}s")
    c.add(f'<line x1="{x}" y1="258" x2="{600-x}" y2="258" stroke="{p["borde"]}" class="f" style="animation-delay:{d+.2:.2f}s"/>')
    libre = 600 - 2 * x - ancho(f"{url_v} ↗", "M", 500, 12.5) - 28
    piezas = pila.split(" · ")
    while len(piezas) > 1 and ancho(" · ".join(piezas), "M", 400, 12) > libre:
        piezas.pop()
    c.texto(x, 286, " · ".join(piezas), fam="M", tam=12, color=p["tenue"], clase="f", estilo=f"animation-delay:{d+.22:.2f}s")
    c.texto(600 - x, 286, f"{url_v} ↗", fam="M", peso=500, tam=12.5, color=p["texto"], ancla="end", clase="f",
            estilo=f"animation-delay:{d+.24:.2f}s")
    return c


def titulo_seccion(tema, numero, etiqueta, titulo, alto=96, x=8):
    c = Lienzo(W, alto, tema, f"{etiqueta}: {titulo}")
    encabezado(c, x, 26, numero, etiqueta, titulo)
    return c


def trayectoria(tema):
    c = Lienzo(W, 470, tema, "Trayectoria: experiencia y formación")
    p = c.t
    encabezado(c, 0, 26, "04", "Trayectoria", "De arreglar equipos a construir sistemas.")
    top = 112
    colw = (W - 24) / 2

    def columna(x0, titulo, items, d0):
        c.add(f'<rect x="{x0+.5:.1f}" y="{top+.5}" width="{colw-1:.1f}" height="{c.h-top-2}" rx="16" fill="{p["sup"]}" stroke="{p["borde"]}" class="f" style="animation-delay:{d0:.2f}s"/>')
        c.texto(x0 + 28, top + 40, titulo.upper(), fam="M", peso=500, tam=12, color=p["suave"], ls=1.5, clase="f", estilo=f"animation-delay:{d0:.2f}s")
        y = top + 82
        linea_x = x0 + 34
        alto_total = 0
        bloques = []
        for it in items:
            bloques.append((y, it))
            y += it["alto"]
        largo = bloques[-1][0] - bloques[0][0]
        c.add(f'<line class="l" x1="{linea_x}" y1="{bloques[0][0]-5}" x2="{linea_x}" y2="{bloques[-1][0]-5}" stroke="{p["borde"]}" stroke-width="2" style="--d:{largo:.0f};animation-delay:{d0+.2:.2f}s"/>')
        for n, (yy, it) in enumerate(bloques):
            dd = d0 + 0.25 + n * 0.18
            c.add(f'<circle class="p" style="animation-delay:{dd:.2f}s" cx="{linea_x}" cy="{yy-5}" r="6" fill="{p["sup"]}" stroke="{p["acento"] if n == 0 and it.get("actual") else p["texto"]}" stroke-width="2"/>')
            tx = linea_x + 26
            c.texto(tx, yy, it["titulo"], peso=600, tam=18, ls=-0.3, clase="f", estilo=f"animation-delay:{dd:.2f}s")
            c.texto(x0 + colw - 28, yy, it["fecha"], fam="M", tam=12, color=p["tenue"], ancla="end", clase="f", estilo=f"animation-delay:{dd:.2f}s")
            c.texto(tx, yy + 24, it["sub"], tam=14.5, color=p["texto"], clase="f", estilo=f"animation-delay:{dd+.04:.2f}s")
            for i, l in enumerate(it["lineas"]):
                c.texto(tx, yy + 48 + i * 21, l, tam=14, color=p["suave"], clase="f", estilo=f"animation-delay:{dd+.08:.2f}s")

    ancho_txt = colw - 28 - 60 - 30
    exp = []
    for org, fecha, rol, desc in D.EXPERIENCIA:
        lineas = partir(desc, ancho_txt, "I", 400, 14)
        exp.append(dict(titulo=org, fecha=fecha, sub=rol, lineas=lineas, alto=70 + len(lineas) * 21 + 22, actual="hoy" in fecha))
    form = []
    for prog, inst, fecha in D.FORMACION:
        lineas_t = partir(prog, ancho_txt - 90, "I", 600, 18)
        form.append(dict(titulo=lineas_t[0], fecha=fecha, sub=" ".join(lineas_t[1:]) or inst, lineas=[inst] if len(lineas_t) > 1 else [],
                         alto=92 if len(lineas_t) > 1 else 74, actual="curso" in fecha))
    alto_col = max(sum(i["alto"] for i in exp), sum(i["alto"] for i in form)) + 82 + 10
    c.h = int(top + alto_col)
    columna(0, "Experiencia", exp, 0.2)
    columna(colw + 24, "Formación", form, 0.35)
    return c


def _rest(ruta):
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req = urllib.request.Request(f"https://api.github.com/{ruta}", headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        return json.load(urllib.request.urlopen(req, timeout=30))
    import subprocess
    return json.loads(subprocess.run(["gh", "api", ruta], capture_output=True, text=True, check=True).stdout)


def _colores_lenguajes():
    f = REC / "colores-lenguajes.json"
    return json.loads(f.read_text()) if f.exists() else {}


def datos_github():
    if os.environ.get("REPOS"):  # para correr fuera de Actions con acceso limitado a ciertos repos
        repos = [_rest(f"repos/{USUARIO}/{n}") for n in os.environ["REPOS"].split(",")]
    else:
        repos = _rest(f"users/{USUARIO}/repos?per_page=100&type=owner")
    repos = [r for r in repos if not r["fork"] and not r.get("private")]
    colores = _colores_lenguajes()
    langs = {}
    for r in repos:
        for nombre, tam in _rest(f"repos/{USUARIO}/{r['name']}/languages").items():
            langs.setdefault(nombre, [0, colores.get(nombre, "#8B8D93")])
            langs[nombre][0] += tam
    gh = dict(repos=len(repos), langs=sorted(langs.items(), key=lambda x: -x[1][0])[:8], total=None, dias=[])
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            q = '{ user(login: "%s") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }' % USUARIO
            req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                         headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
            cal = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            gh["total"] = cal["totalContributions"]
            gh["dias"] = [d for w in cal["weeks"] for d in w["contributionDays"]]
        except Exception as e:
            print("aviso: sin calendario de contribuciones:", e)
    return gh


def actividad(tema, gh):
    c = Lienzo(W, 400, tema, "Actividad en GitHub: contribuciones del último año y lenguajes de los repos públicos")
    p = c.t
    encabezado(c, 0, 26, "05", "Actividad", "Lo que se mueve en GitHub.")
    top = 112
    if not gh:
        c.texto(0, top + 30, "Se actualiza cada día con GitHub Actions.", tam=15, color=p["suave"])
        c.h = top + 50
        return c
    # cifras
    racha, maxr = 0, 0
    for d in gh["dias"]:
        racha = racha + 1 if d["contributionCount"] > 0 else 0
        maxr = max(maxr, racha)
    activos = sum(1 for d in gh["dias"] if d["contributionCount"] > 0)
    cifras = []
    if gh["total"] is not None:
        cifras += [(f'{gh["total"]:,}'.replace(",", "."), "contribuciones en el último año"),
                   (str(activos), "días con actividad"), (str(maxr), "días de racha más larga")]
    cifras.append((str(gh["repos"]), "repositorios públicos"))
    cifras.append((str(len(gh["langs"])), "lenguajes en uso"))
    cifras = cifras[:4]
    cw = (W - (len(cifras) - 1) * 16) / len(cifras)
    for k, (num, etq) in enumerate(cifras):
        x = k * (cw + 16)
        d = .2 + k * .1
        c.add(f'<rect class="f" style="animation-delay:{d:.2f}s" x="{x+.5:.1f}" y="{top+.5}" width="{cw-1:.1f}" height="119" rx="16" fill="{p["sup"]}" stroke="{p["borde"]}"/>')
        c.texto(x + 24, top + 66, num, peso=700, tam=44, ls=-1.5, clase="f", estilo=f"animation-delay:{d+.05:.2f}s")
        c.texto(x + 24, top + 96, etq, tam=14, color=p["suave"], clase="f", estilo=f"animation-delay:{d+.1:.2f}s")
    # mapa de las últimas 26 semanas
    y2 = top + 148
    c.add(f'<rect class="f" style="animation-delay:.5s" x=".5" y="{y2+.5}" width="{W-1}" height="190" rx="16" fill="{p["sup"]}" stroke="{p["borde"]}"/>')
    c.texto(24, y2 + 34, "LENGUAJES · REPOS PÚBLICOS", fam="M", peso=500, tam=12, color=p["suave"], ls=1.5, clase="f", estilo="animation-delay:.5s")
    total = sum(v[0] for _, v in gh["langs"]) or 1
    bx, bw, by = 24, W - 48, y2 + 56
    xx = bx
    c.add(f'<clipPath id="barra"><rect x="{bx}" y="{by}" width="{bw}" height="14" rx="7"/></clipPath><g clip-path="url(#barra)">')
    for n, (nombre, (tam_b, color)) in enumerate(gh["langs"]):
        w = bw * tam_b / total
        c.add(f'<rect class="f" style="animation-delay:{.6+n*.06:.2f}s" x="{xx:.1f}" y="{by}" width="{w+.5:.1f}" height="14" fill="{color}"/>')
        xx += w
    c.add("</g>")
    lx, ly = bx, by + 52
    for n, (nombre, (tam_b, color)) in enumerate(gh["langs"]):
        etq = f"{nombre} {tam_b/total*100:.1f}%"
        we = ancho(etq, "I", 500, 14) + 40
        if lx + we > W - 24:
            lx, ly = bx, ly + 30
        c.add(f'<circle class="p" style="animation-delay:{.7+n*.05:.2f}s" cx="{lx+6}" cy="{ly-5}" r="5" fill="{color}"/>')
        c.texto(lx + 18, ly, nombre, peso=500, tam=14, clase="f", estilo=f"animation-delay:{.7+n*.05:.2f}s")
        c.texto(lx + 18 + ancho(nombre, "I", 500, 14) + 6, ly, f"{tam_b/total*100:.1f}%", fam="M", tam=12, color=p["tenue"], clase="f", estilo=f"animation-delay:{.7+n*.05:.2f}s")
        lx += we
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    c.texto(W - 24, y2 + 34, f"actualizado {hoy}", fam="M", tam=12, color=p["tenue"], ancla="end", clase="f", estilo="animation-delay:.5s")
    c.h = int(max(ly + 30, y2 + 120) + 2)
    c.partes = [s.replace(f'height="190" rx="16"', f'height="{c.h-y2-2:.0f}" rx="16"') for s in c.partes]
    return c


def contacto(tema, k, etiqueta, valor):
    w = 300
    c = Lienzo(w, 96, tema, f"{etiqueta}: {valor}")
    p = c.t
    d = .1 + k * .08
    c.add(f'<rect class="f" style="animation-delay:{d:.2f}s" x="8.5" y="8.5" width="{w-17}" height="79" rx="16" fill="{p["sup"]}" stroke="{p["borde"]}"/>')
    c.texto(30, 44, etiqueta, peso=600, tam=17, clase="f", estilo=f"animation-delay:{d+.05:.2f}s")
    while ancho(valor, "M", 400, 12.5) > w - 60:
        valor = valor[:-2] + "…"
    c.texto(30, 68, valor, fam="M", tam=12.5, color=p["suave"], clase="f", estilo=f"animation-delay:{d+.1:.2f}s")
    c.texto(w - 30, 44, "↗", fam="M", peso=500, tam=17, color=p["suave"], ancla="end", clase="f", estilo=f"animation-delay:{d+.15:.2f}s")
    return c


def cierre(tema):
    c = Lienzo(W, 112, tema, D.CIERRE)
    p = c.t
    c.add(f'<line x1="8" y1="1" x2="{W-8}" y2="1" stroke="{p["borde"]}"/>')
    linea = f"{D.PROMPT} echo \"{D.CIERRE}\""
    c.texto(8, 56, D.PROMPT, fam="M", tam=14, color=p["tenue"])
    c.texto(8 + ancho(D.PROMPT + " ", "M", 400, 14), 56, f"echo \"{D.CIERRE}\"", fam="M", tam=14, color=p["suave"])
    c.add(f'<rect x="{8 + ancho(linea, "M", 400, 14) + 6:.1f}" y="43" width="8" height="16" fill="{p["texto"]}" class="b"/>')
    c.texto(8, 90, "Jordan Aragon · Cali, Colombia · jordanco.club", fam="M", tam=12, color=p["tenue"])
    return c


def guardar(nombre, lienzo_fn):
    for tema in TEMAS:
        c = lienzo_fn(tema)
        (SALIDA / f"{nombre}-{tema}.svg").write_text(c.svg())


def main():
    SALIDA.mkdir(exist_ok=True)
    guardar("hero", hero)
    guardar("terminal", terminal)
    guardar("servicios", servicios)
    guardar("stack", stack)
    guardar("proyectos", lambda t: titulo_seccion(t, "03", "Proyectos", "Lo que está en producción."))
    for k, pr in enumerate(D.PROYECTOS):
        guardar(f"proyecto-{pr[0]}", lambda t, k=k, pr=pr: proyecto(t, k, pr))
    guardar("trayectoria", trayectoria)
    gh = None
    try:
        gh = datos_github()
    except Exception as e:  # sin red o sin permisos: la tarjeta queda con el último dato
        print("aviso: no se pudo leer GitHub:", e)
    if gh or not (SALIDA / "actividad-oscuro.svg").exists():  # sin datos nuevos se conserva la última tarjeta
        guardar("actividad", lambda t: actividad(t, gh))
    guardar("contacto", lambda t: titulo_seccion(t, "06", "Contacto", "Hablemos.", 96))
    for k, (clave, etq, val, _) in enumerate(D.CONTACTO):
        guardar(f"contacto-{clave}", lambda t, k=k, etq=etq, val=val: contacto(t, k, etq, val))
    guardar("cierre", cierre)
    total = sum(f.stat().st_size for f in SALIDA.glob("*.svg"))
    print(f"{len(list(SALIDA.glob('*.svg')))} archivos, {total/1024:.0f} KB")


if __name__ == "__main__":
    main()
