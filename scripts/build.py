#!/usr/bin/env python3
"""Genera el prototipo navegable (app/ e index.html) a partir de las pantallas de design/.

Uso:  python3 scripts/build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / 'design'
APP = ROOT / 'app'

GROUPS = [
    ('nav', 'Navegación principal', 'Inicio, mis viajes, avisos y perfil del pasajero y del conductor.',
     lambda s: s == 'Main' or s.startswith('hub_')),
    ('p01', 'P-01 · Registro y verificación', 'Crear la cuenta, verificar al pasajero y habilitar al conductor.',
     lambda s: s.startswith('reg_') and not s.startswith('reg_A') and s not in DRIVER_PROFILE),
    ('perfil', 'Perfil del conductor', 'Vehículo, documentos, medio de cobro y preferencias.',
     lambda s: s in DRIVER_PROFILE),
    ('p03', 'P-03 · Búsqueda, reserva y pago', 'Del buscador al código de abordaje, con tarjeta, billetera o efectivo.',
     lambda s: s.startswith('res_')),
    ('p12', 'P-12 · Acompañantes', 'Enlace de un solo uso para verificar a quien viaja con el titular.',
     lambda s: s.startswith('reg_A')),
    ('p04c', 'P-04 · Ejecución · conductor', 'Abrir el viaje, verificación facial, abordaje y llegada.',
     lambda s: s.startswith('eje_') and not s.startswith('eje_P')),
    ('p04p', 'P-04 · Ejecución · pasajero', 'Código de abordaje, viaje en curso, SOS y confirmación de llegada.',
     lambda s: s.startswith('eje_P')),
    ('p02', 'P-02 · Publicación de viaje', 'Ruta, puntos, salida, condiciones, precio por tramo y publicación.',
     lambda s: s.startswith('pub_')),
    ('p07', 'P-07 · Wallet del conductor', 'Saldo, movimientos, recargas, retiros y límites por deuda.',
     lambda s: s.startswith('wal_')),
]
DRIVER_PROFILE = {'reg_08-vehiculo', 'reg_09-documentos', 'reg_09b-documento-vencido', 'reg_10-cobros', 'reg_11-preferencias'}

SHELL_CSS = '''
html, body.shell { margin: 0; min-height: 100%; background: #ECEAF3; }
body.shell { font-family: 'IBM Plex Sans', system-ui, sans-serif; color: #251D44; }
.shell-bar { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 12px; justify-content: space-between;
  padding: 10px 16px; background: #251D44; color: #FFFFFF; font-size: 13px; }
.shell-bar a { color: #D1F383; font-weight: 600; text-decoration: none; }
.shell-bar span { opacity: .8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.shell-stage { display: flex; justify-content: center; padding: 24px 16px 48px; }
#dc-root { flex: none; background: #FFFFFF; border-radius: 28px; overflow: hidden; box-shadow: 0 18px 50px rgba(37,29,68,.22); }
@media (max-width: 480px) {
  .shell-stage { padding: 0; }
  #dc-root { border-radius: 0; box-shadow: none; }
}
'''


def screen_page(stem: str, src: str, title: str) -> str:
    helmet = re.search(r'<helmet>(.*?)</helmet>', src, re.S)
    helmet = helmet.group(1) if helmet else ''
    body = src.split('<x-dc>', 1)[1].split('</x-dc>', 1)[0]
    body = re.sub(r'<helmet>.*?</helmet>', '', body, flags=re.S).strip()
    logic = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', src, re.S).group(1)
    size = re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}', src)
    w, h = (size.group(1), size.group(2)) if size else ('390', '844')
    tpl_json = json.dumps(body, ensure_ascii=False).replace('</', '<\\/')
    logic_safe = logic.replace('</script', '<\\/script')
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · RUTA</title>
{helmet.strip()}
<style>{SHELL_CSS}</style>
<script src="runtime.js"></script>
</head>
<body class="shell">
<div class="shell-bar"><a href="../index.html">← Todas las pantallas</a><span>{html.escape(title)}</span><a href="Main.html">Reiniciar demo</a></div>
<div class="shell-stage"><div id="dc-root" style="width: {w}px; min-height: {h}px;"></div></div>
<script type="application/json" id="dc-template">{tpl_json}</script>
<script type="text/x-dc" id="dc-logic">{logic_safe}</script>
</body>
</html>
'''


def index_page(groups) -> str:
    sections = []
    for gid, gtitle, gdesc, items in groups:
        cards = ''.join(
            f'<a class="card" href="app/{stem}.html"><span class="t">{html.escape(t)}</span><span class="f">{stem}</span></a>'
            for stem, t in items)
        sections.append(f'<section id="{gid}"><h2>{html.escape(gtitle)}</h2><p>{html.escape(gdesc)}</p><div class="grid">{cards}</div></section>')
    total = sum(len(i) for *_, i in groups)
    short = {'nav': 'Navegación', 'p01': 'P-01 Registro', 'perfil': 'Perfil conductor', 'p03': 'P-03 Reserva', 'p12': 'P-12 Acompañantes',
             'p04c': 'P-04 Conductor', 'p04p': 'P-04 Pasajero', 'p02': 'P-02 Publicación', 'p07': 'P-07 Wallet'}
    nav = ''.join(f'<a href="#{gid}">{html.escape(short.get(gid, gt))}</a>' for gid, gt, _, _ in groups)
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RUTA · Prototipo integral</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&amp;display=swap" rel="stylesheet">
<style>
:root {{ --ink: #251D44; --ink2: #5B5670; --line: #E4E1EE; --lime: #D1F383; --lav: #EEEBFD; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #FFFFFF; color: var(--ink); font-family: 'IBM Plex Sans', system-ui, sans-serif; }}
header {{ background: var(--ink); color: #FFFFFF; padding: 40px 16px 32px; }}
.wrap {{ max-width: 1080px; margin: 0 auto; }}
h1 {{ margin: 0 0 8px; font-size: 34px; line-height: 1.15; }}
header p {{ margin: 0 0 20px; color: rgba(255,255,255,.78); max-width: 640px; line-height: 1.5; }}
.cta {{ display: inline-flex; align-items: center; height: 48px; padding: 0 20px; border-radius: 12px; background: var(--lime);
  color: var(--ink); font-weight: 700; text-decoration: none; }}
nav {{ position: sticky; top: 0; z-index: 5; background: #FFFFFF; border-bottom: 1px solid var(--line); }}
nav .wrap {{ display: flex; gap: 6px; overflow-x: auto; padding: 10px 16px; }}
nav a {{ flex: none; padding: 6px 12px; border-radius: 16px; background: var(--lav); color: var(--ink); font-size: 13px; font-weight: 600; text-decoration: none; }}
main {{ padding: 8px 16px 64px; }}
section {{ padding-top: 28px; }}
h2 {{ margin: 0 0 4px; font-size: 20px; }}
section > p {{ margin: 0 0 14px; color: var(--ink2); font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }}
.card {{ display: flex; flex-direction: column; gap: 4px; padding: 12px 14px; border: 1.5px solid var(--line); border-radius: 12px;
  color: var(--ink); text-decoration: none; }}
.card:hover {{ border-color: var(--ink); background: #F3FBE1; }}
.card .t {{ font-weight: 600; font-size: 14px; }}
.card .f {{ font-size: 12px; color: var(--ink2); font-family: ui-monospace, monospace; }}
footer {{ padding: 24px 16px 40px; color: var(--ink2); font-size: 13px; border-top: 1px solid var(--line); }}
</style>
</head>
<body>
<header><div class="wrap">
<h1>RUTA · Prototipo integral</h1>
<p>Prototipo navegable de la app de viajes compartidos entre ciudades (corredor Lima ↔ Ica). {total} pantallas que unen registro, reserva, publicación, ejecución del viaje y wallet.</p>
<a class="cta" href="app/Main.html">Iniciar la demo</a>
</div></header>
<nav><div class="wrap">{nav}</div></nav>
<main><div class="wrap">{''.join(sections)}</div></main>
<footer><div class="wrap">Generado desde <code>design/</code> con <code>scripts/build.py</code>.</div></footer>
</body>
</html>
'''


def main():
    canvas = json.loads((DESIGN / 'canvas.json').read_text(encoding='utf-8'))
    boards = canvas['boards']
    order = [o[:-8] for o in canvas['order'] if o.endswith('.dc.html')]
    stems = [p.name[:-8] for p in sorted(DESIGN.glob('*.dc.html'))]
    stems = sorted(stems, key=lambda s: order.index(s) if s in order else 10 ** 6)

    APP.mkdir(exist_ok=True)
    for old in APP.glob('*.html'):
        old.unlink()
    for s in stems:
        src = (DESIGN / f'{s}.dc.html').read_text(encoding='utf-8')
        title = boards.get(f'{s}.dc.html', {}).get('title', s)
        (APP / f'{s}.html').write_text(screen_page(s, src, title), encoding='utf-8')

    groups, used = [], set()
    for gid, gtitle, gdesc, match in GROUPS:
        items = [(s, boards.get(f'{s}.dc.html', {}).get('title', s)) for s in stems if s not in used and match(s)]
        used.update(s for s, _ in items)
        groups.append((gid, gtitle, gdesc, items))
    rest = [s for s in stems if s not in used]
    assert not rest, rest
    (ROOT / 'index.html').write_text(index_page(groups), encoding='utf-8')

    # enlaces rotos
    names = set(stems)
    bad = [(s, t) for s in stems for t in re.findall(r'href="([^"#:]+)\.dc\.html"', (DESIGN / f'{s}.dc.html').read_text(encoding='utf-8')) if t not in names]
    if bad:
        raise SystemExit(f'Enlaces rotos: {bad}')
    print(f'{len(stems)} pantallas generadas en app/ e índice en index.html')


if __name__ == '__main__':
    main()
