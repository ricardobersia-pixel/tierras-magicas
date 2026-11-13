"""Genera los 4 reels de verano a partir de fotos reales.

Uso: FOTOS=/ruta/a/fotos python3 build.py
Requiere ffmpeg, Node con Playwright y las fuentes Inter y Noto Color Emoji.
"""
import json, subprocess, os

R = '/home/user/tierras-magicas'
S = os.path.dirname(os.path.abspath(__file__))
F = os.environ.get('FOTOS', os.path.join(S, '..', 'drive')) + '/'
OUT = os.environ.get('SALIDA', R + '/entrega/reels-verano')
os.makedirs(OUT, exist_ok=True)
os.makedirs(S + '/ov', exist_ok=True)
os.makedirs(S + '/clips', exist_ok=True)

# Encuadres: (foto, centro x, centro y, alto del recorte) en fracciones de la foto.
# El ancho sale de la proporción 9:16. Ningún encuadre muestra caras.
CROPS = {
    'CAB':  ('cabana.jpg', 0.42, 0.5, 1.0),
    'CABm': ('cabana.jpg', 0.78, 0.5, 1.0),
    'CABh': ('cabana.jpg', 0.22, 0.5, 1.0),
    'DECK': ('deck-reposeras.jpg', 0.42, 0.5, 1.0),
    'TP':   ('tina-pareja.jpg', 0.19, 0.585, 0.569),
    'TM':   ('tina-montana.jpg', 0.90, 0.437, 0.474),
    'TI':   ('tina-inflable.jpg', 0.336, 0.5, 1.0),
    'TD':   ('tina-deck.jpg', 0.22, 0.5, 1.0),
    'FS':   ('fogon-sol.jpg', 0.50, 0.5, 1.0),
    'FM':   ('fogon-montana.jpg', 0.44, 0.5, 1.0),
    'SAU':  ('sauna.jpg', 0.53, 0.5, 1.0),
    'L1':   ('lago.jpg', 0.30, 0.5, 1.0),
    'L2':   ('lago.jpg', 0.58, 0.5, 1.0),
    'L3':   ('lago.jpg', 0.86, 0.5, 1.0),
    'AE':   ('aerea-vertical.jpg', 'vpan'),
    'AE2':  ('aerea-vertical.jpg', 0.70, 0.53, 0.45),
}

T1 = 1.2  # duración estándar de cada toma, en segundos
REELS = [
    {'id': 'reel1-pareja', 'text': ['Necesito un secuestro de 3 días', 'en una cabañita así con vos ❤️'],
     'shots': [('CAB', T1), ('DECK', T1), ('L1', T1), ('TM', T1), ('FS', T1), ('TI', T1), ('TP', 2.0), ('L2', 3.4)]},
    {'id': 'reel2-grupo', 'text': ['Necesito 3 días acá con mis amigos', 'y que nadie diga "¿y si volvemos?" 🔥'],
     'shots': [('AE', T1), ('FM', T1), ('CABm', T1), ('TD', T1), ('SAU', T1), ('FS', T1), ('DECK', 2.0), ('L3', 3.4)]},
    {'id': 'reel3-incluye', 'text': ['3 días de verano en Moquehue', 'y nada de esto se paga aparte 👀'],
     'shots': [('TP', 1.5, 'tina caliente'), ('SAU', 1.5, 'sauna'), ('L2', 1.5, 'el lago, a 50 m'),
               ('AE', 1.5, 'isla flotante'), ('AE2', 1.5, 'kayaks y stand up'), ('DECK', 3.5, 'y esta vista')]},
    {'id': 'reel4-carnaval', 'text': ['Yo en Carnaval, mientras vos seguís', '"viendo qué hacemos" 🙃'],
     'shots': [('DECK', T1), ('L3', T1), ('TI', T1), ('CABh', T1), ('AE', T1), ('TM', T1), ('TP', 2.0), ('L2', 3.4)]},
]

GRADE = 'eq=saturation=1.08:contrast=1.04,unsharp=5:5:0.5'


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])


# 1. Textos de cada toma como PNG transparente
spec = [{'id': r['id'], 'text': r['text'],
         'shots': [{'label': s[2] if len(s) > 2 else None, 'handle': i == len(r['shots']) - 1}
                   for i, s in enumerate(r['shots'])]} for r in REELS]
json.dump(spec, open(S + '/spec.json', 'w'), ensure_ascii=False)
npm_root = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
subprocess.run(['node', S + '/overlays.js', S + '/spec.json', S + '/ov'], check=True,
               env={**os.environ, 'NODE_PATH': npm_root})

# 2. Cada toma: recorte 9:16 con paneo lento + texto; después se unen con cortes secos
for r in REELS:
    parts = []
    for i, s in enumerate(r['shots']):
        key, dur = s[0], s[1]
        crop = CROPS[key]
        img = crop[0]
        frames = round(dur * 30)
        d = 1 if i % 2 == 0 else -1  # alterna la dirección del movimiento
        if crop[1] == 'vpan':
            # foto vertical a pantalla completa, paneo de arriba hacia el centro
            vf = f"[0:v]scale=1080:-2:flags=lanczos,crop=1080:1920:0:'(ih-oh)*0.45*t/{dur}',{GRADE},setsar=1[b]"
        else:
            _, cx, cy, h = crop
            cw = f"ih*{h}*9/16*1.12"  # 12% más ancho para el paneo
            ch = f"ih*{h}"
            vf = (f"[0:v]crop='{cw}':'{ch}':'max(0,min(iw-{cw},iw*{cx}-{cw}/2))':'max(0,min(ih-{ch},ih*{cy}-{ch}/2))',"
                  f"scale=1210:1920:flags=lanczos,"
                  f"crop=1080:1920:'(iw-ow)*({0 if d > 0 else 1}+{d}*t/{dur})':0,{GRADE},setsar=1[b]")
        ov = f"{S}/ov/{r['id']}_{i}.png"
        out = f"{S}/clips/{r['id']}_{i}.mp4"
        run(['ffmpeg', '-y', '-loop', '1', '-framerate', '30', '-t', str(dur), '-i', F + img, '-i', ov,
             '-filter_complex', vf + ';[b][1:v]overlay=0:0,format=yuv420p[v]', '-map', '[v]',
             '-frames:v', str(frames), '-r', '30', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', out])
        parts.append(out)
    lst = f"{S}/clips/{r['id']}.txt"
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    dst = f"{OUT}/{r['id']}.mp4"
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
         '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
         '-c:v', 'libx264', '-crf', '19', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
         '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', dst])
    print('OK', dst)
