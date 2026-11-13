import json, subprocess, os, sys

R = '/home/user/tierras-magicas'
F = R + '/docs/welcome-book/fotos/'
S = os.path.dirname(os.path.abspath(__file__))
OUT = R + '/entrega/reels-verano'
os.makedirs(OUT, exist_ok=True)

# Encuadres: (foto, centro x en fracción del ancho, modo)
CROPS = {
    'C1': ('cabana.jpg', 0.20, 'v'), 'C2': ('cabana.jpg', 0.42, 'v'), 'C3': ('cabana.jpg', 0.76, 'v'),
    'T1': ('tina.jpg', 0.22, 'v'), 'T2': ('tina.jpg', 0.50, 'v'), 'T3': ('tina.jpg', 0.80, 'v'),
    'L1': ('lago.jpg', 0.22, 'v'), 'L2': ('lago.jpg', 0.55, 'v'), 'L3': ('lago.jpg', 0.80, 'v'),
    'A': ('lago-aereo.jpg', 0.5, 'fit'), 'A2': ('lago-aereo.jpg', 0.56, 'zoom'),
}

T1 = 1.2  # duración estándar de cada toma
REELS = [
    {'id': 'reel1-pareja', 'text': ['Necesito un secuestro de 3 días', 'en una cabañita así con vos ❤️'],
     'shots': [('C2', T1), ('T1', T1), ('C3', T1), ('L1', T1), ('A', T1), ('T2', T1), ('C1', 2.0), ('L2', 3.4)]},
    {'id': 'reel2-grupo', 'text': ['Necesito 3 días acá con mis amigos', 'y que nadie diga "¿y si volvemos?" 🔥'],
     'shots': [('A', T1), ('L3', T1), ('C3', T1), ('T1', T1), ('C2', T1), ('T3', T1), ('C1', 2.0), ('L2', 3.4)]},
    {'id': 'reel3-incluye', 'text': ['3 días de verano en Moquehue', 'y nada de esto se paga aparte 👀'],
     'shots': [('T1', 1.6, 'tina caliente'), ('L2', 1.6, 'el lago, a 50 m'), ('A', 1.6, 'isla flotante'),
               ('A2', 1.6, 'kayaks y stand up'), ('L1', 4.0, '+ sauna y esta vista')]},
    {'id': 'reel4-carnaval', 'text': ['Yo en Carnaval, mientras vos seguís', '"viendo qué hacemos" 🙃'],
     'shots': [('C3', T1), ('L3', T1), ('A', T1), ('T1', T1), ('C1', T1), ('T2', T1), ('C2', 2.0), ('L2', 3.4)]},
]

spec = []
for r in REELS:
    shots = []
    for i, s in enumerate(r['shots']):
        shots.append({'label': s[2] if len(s) > 2 else None, 'handle': i == len(r['shots']) - 1})
    spec.append({'id': r['id'], 'text': r['text'], 'shots': shots})
json.dump(spec, open(S + '/spec.json', 'w'), ensure_ascii=False)
subprocess.run(['node', S + '/overlays.js', S + '/spec.json', S + '/ov'], check=True,
               env={**os.environ, 'NODE_PATH': subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()})

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

for r in REELS:
    parts = []
    for i, s in enumerate(r['shots']):
        key, dur = s[0], s[1]
        img, cx, mode = CROPS[key]
        frames = round(dur * 30)
        d = 1 if i % 2 == 0 else -1  # alterna la dirección del movimiento
        grade = 'eq=saturation=1.08:contrast=1.04,unsharp=5:5:0.6'
        if mode == 'v':
            # franja vertical 9:16 un 12% más ancha, ampliada y con paneo horizontal lento
            base = (f"crop='ih*9/16*1.12':ih:'max(0,min(iw-ih*9/16*1.12,iw*{cx}-ih*9/16*0.56))':0,"
                    f"scale=1210:1920:flags=lanczos,"
                    f"crop=1080:1920:'(iw-ow)*({0 if d > 0 else 1}+{d}*t/{dur})':0")
            vf = f"[0:v]{base},{grade},setsar=1[b]"
        elif mode == 'fit':
            # aérea completa sobre fondo desenfocado, con zoom suave
            vf = (f"[0:v]split[a][c];[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.08[bg];"
                  f"[c]scale=1200:-2:flags=lanczos,zoompan=z='1+0.0015*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1200x527:fps=30[fg];"
                  f"[bg][fg]overlay=(W-w)/2:200,{grade},setsar=1[b]")
        else:  # zoom sobre la isla, kayaks y stand up
            vf = (f"[0:v]split[a][c];[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.08[bg];"
                  f"[c]crop=iw*0.42:ih*0.6:iw*{cx}-iw*0.21:0,scale=1080:-2:flags=lanczos,"
                  f"zoompan=z='1.05+0.002*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1080x672:fps=30[fg];"
                  f"[bg][fg]overlay=0:120,{grade},setsar=1[b]")
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
