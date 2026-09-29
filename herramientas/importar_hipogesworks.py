"""Convierte paginas guardadas de HipogesWorks (Ctrl+S del listado 'Solicitar asignacion')
en datos para la Zona Colaboradores.

Uso:  python herramientas/importar_hipogesworks.py "C:/ruta/HIPOGES SUSPENDIDOS"
Lee todos los .html/.htm de esa carpeta (y subcarpetas), extrae cada activo y guarda
colaboradores/_hipoges/<comunidad>.json. Luego ejecuta generar_listado_colaboradores.py.

Direccion: la Zona Colaboradores es privada (usuario y contrasena), asi que por defecto se guarda
la direccion completa tal y como aparece en HipogesWorks (numero, escalera, planta, puerta).
Para ocultarla, poner DIRECCION_COMPLETA = False.
"""
DIRECCION_COMPLETA = True
import sys, os, re, json, glob, csv, unicodedata
from bs4 import BeautifulSoup

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def na(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s or '') if unicodedata.category(c) != 'Mn').lower().strip()

# Provincias INE -> (nombre publicado, comunidad, alias)
PROV = {
 '01': ('Álava', 'País Vasco', ['alava', 'araba/alava', 'araba']), '02': ('Albacete', 'Castilla-La Mancha', []),
 '03': ('Alicante/Alacant', 'Comunitat Valenciana', ['alicante', 'alacant']), '04': ('Almería', 'Andalucía', []),
 '05': ('Ávila', 'Castilla y León', []), '06': ('Badajoz', 'Extremadura', []), '07': ('Illes Balears', 'Illes Balears', ['baleares', 'islas baleares', 'balears (illes)', 'illes balears', 'mallorca', 'menorca', 'ibiza', 'eivissa', 'formentera']),
 '08': ('Barcelona', 'Cataluña', []), '09': ('Burgos', 'Castilla y León', []), '10': ('Cáceres', 'Extremadura', []),
 '11': ('Cádiz', 'Andalucía', []), '12': ('Castellón/Castelló', 'Comunitat Valenciana', ['castellon', 'castello']),
 '13': ('Ciudad Real', 'Castilla-La Mancha', []), '14': ('Córdoba', 'Andalucía', []), '15': ('A Coruña', 'Galicia', ['coruna (a)', 'la coruna', 'coruna']),
 '16': ('Cuenca', 'Castilla-La Mancha', []), '17': ('Girona', 'Cataluña', ['gerona']), '18': ('Granada', 'Andalucía', []),
 '19': ('Guadalajara', 'Castilla-La Mancha', []), '20': ('Guipúzcoa', 'País Vasco', ['gipuzkoa', 'guipuzcoa']), '21': ('Huelva', 'Andalucía', []),
 '22': ('Huesca', 'Aragón', []), '23': ('Jaén', 'Andalucía', []), '24': ('León', 'Castilla y León', []), '25': ('Lleida', 'Cataluña', ['lerida']),
 '26': ('La Rioja', 'La Rioja', ['rioja (la)', 'rioja']), '27': ('Lugo', 'Galicia', []), '28': ('Madrid', 'Comunidad de Madrid', []),
 '29': ('Málaga', 'Andalucía', []), '30': ('Murcia', 'Región de Murcia', []), '31': ('Navarra', 'Navarra', ['nafarroa']),
 '32': ('Ourense', 'Galicia', ['orense']), '33': ('Asturias', 'Asturias', []), '34': ('Palencia', 'Castilla y León', []),
 '35': ('Las Palmas', 'Canarias', ['palmas (las)', 'palmas']), '36': ('Pontevedra', 'Galicia', []), '37': ('Salamanca', 'Castilla y León', []),
 '38': ('Santa Cruz de Tenerife', 'Canarias', ['s.c. tenerife', 'santa c. de tenerife', 'tenerife']), '39': ('Cantabria', 'Cantabria', []),
 '40': ('Segovia', 'Castilla y León', []), '41': ('Sevilla', 'Andalucía', []), '42': ('Soria', 'Castilla y León', []),
 '43': ('Tarragona', 'Cataluña', []), '44': ('Teruel', 'Aragón', []), '45': ('Toledo', 'Castilla-La Mancha', []),
 '46': ('Valencia/València', 'Comunitat Valenciana', ['valencia', 'valencia/valencia']), '47': ('Valladolid', 'Castilla y León', []),
 '48': ('Vizcaya', 'País Vasco', ['bizkaia']), '49': ('Zamora', 'Castilla y León', []), '50': ('Zaragoza', 'Aragón', []),
 '51': ('Ceuta', 'Ceuta', []), '52': ('Melilla', 'Melilla', []),
}
ALIAS = {}
for pid, (nom, cc, al) in PROV.items():
    for a in [nom] + al + nom.split('/'):
        ALIAS[na(a)] = pid

def variantes(nombre):
    """'Palmas de Gran Canaria, Las' -> ['palmas de gran canaria, las','palmas de gran canaria (las)','las palmas de gran canaria']"""
    v = {na(nombre)}
    for parte in nombre.split('/'):
        v.add(na(parte))
        m = re.match(r'(.+),\s*(\w+)$', parte.strip())
        if m:
            v.add(na('%s (%s)' % (m.group(1), m.group(2))))
            v.add(na('%s %s' % (m.group(2), m.group(1))))
    return v

MUNI = {}   # provincia_id -> [(variante normalizada, nombre bonito)]
with open(os.path.join(RAIZ, 'herramientas', 'municipios_ine.csv'), encoding='utf-8') as f:
    for r in csv.DictReader(f):
        nombre = r['nombre']
        m = re.match(r'(.+),\s*(\w+)$', nombre.split('/')[0].strip())
        bonito = ('%s %s' % (m.group(2), m.group(1))) if m else nombre.split('/')[0].strip()
        for v in variantes(nombre):
            MUNI.setdefault(r['provincia_id'].zfill(2), []).append((v, bonito))
for k in MUNI: MUNI[k].sort(key=lambda x: -len(x[0]))

def categoria(tipo):
    s = na(tipo)
    if 'hotel' in s: return 'Hotel'
    if 'oficina' in s: return 'Oficina'
    if re.search(r'nave|industrial', s): return 'Industrial'
    if re.search(r'suelo|solar|finca|parcela|terreno|rustic', s): return 'Terreno'
    if re.search(r'piso|casa|chalet|adosad|duplex|atico|apartamento|estudio|loft|vivienda|residencial|pareado|bungalow|unifamiliar', s): return 'Residencial'
    if re.search(r'local|comercial', s): return 'Comercial'
    if re.search(r'garaje|trastero|plaza|parking|anejo', s): return 'Anejo'
    return 'Otro'

def limpiar_calle(c):
    c = re.split(r'\s+N[ºo°]\.?\s*|\s+(?:Esc|Pl|Pt|Planta|Puerta|Bloque|Portal)\b[:.]?', c, maxsplit=1, flags=re.I)[0]
    c = re.sub(r'\s+\d+[A-Za-z]?\s*$', '', c)
    return c.strip(' ,.-')

def separar(resto, pid):
    """resto = 'Calle Ftco Pedro Rivero Nº 13 Palmas de Gran Canaria (Las)' -> (calle, municipio)"""
    nr = na(resto)
    for v, bonito in MUNI.get(pid, []):
        if nr.endswith(' ' + v) or nr == v:
            corte = len(resto) - len(v)
            original = resto[corte:].strip()
            m = re.match(r'(.+?)\s*\((\w+)\)$', original)
            if m: original = '%s %s' % (m.group(2), m.group(1))
            return resto[:corte].strip(), original
    m = re.search(r'N[ºo°]\s*\S+\s+(.+)$', resto)
    if m: return resto[:m.start()].strip(), m.group(1).strip()
    return resto, ''

def parsear(html):
    soup = BeautifulSoup(html, 'html.parser')
    vistos, out = set(), []
    for tr in soup.find_all('tr'):
        td = tr.find('td', attrs={'goto-action': re.compile(r'/Details/\d+')})
        if not td: continue
        hw_id = re.search(r'/Details/(\d+)', td['goto-action']).group(1)
        if hw_id in vistos: continue
        vistos.add(hw_id)
        txt = re.sub(r'\s+', ' ', tr.get_text(' ')).strip()
        tit_el = tr.find(class_='font-blue')
        titulo = re.sub(r'\s+', ' ', tit_el.get_text(' ')).strip() if tit_el else ''
        spec_el = tr.find(class_='alert-info')
        spec = re.sub(r'\s+', ' ', spec_el.get_text(' ')).strip() if spec_el else ''
        img = tr.find('img'); img = img.get('src') if img else ''
        ref = (re.search(r'REF:\s*([A-Z0-9-]+)', txt) or [None, ''])[1]
        precios = [int(p.replace('.', '')) for p in re.findall(r'([\d.]{3,})\s*€', txt)]
        badges = [re.sub(r'\s+', ' ', b.get_text(' ')).strip() for b in tr.select('.badge, .label, span[class*="bg-"]')]
        badges = [b for b in badges if b and b not in ('Venta', 'Alquiler')]
        m = re.match(r'(?:Venta|Alquiler) de (.+?) en (.+?)\s*\(([^()]+)\)\s*$', titulo)
        tipo, resto, prov_txt = (m.group(1), m.group(2), m.group(3)) if m else ('', titulo, '')
        pid = ALIAS.get(na(prov_txt), '')
        calle, municipio = separar(resto, pid) if pid else (resto, '')
        m2 = re.search(r'([\d.]+)\s*m\s*2|([\d.]+)\s*m²', spec)
        hab = re.search(r'(\d+)\s*hab', spec)
        low = na(txt)
        sit = 'Ocupado' if re.search(r'okupa|ocupad', low) else ('CDR' if re.search(r'cesion de remate|\bcdr\b', low) else ('NPL' if re.search(r'\bnpl\b', low) else ''))
        estado = next((b for b in badges if na(b) in ('suspendido', 'en comercializacion', 'reservado', 'preventa', 'oferta', 'oferta en negociacion', 'contrato privado', 'donacion')), 'Suspendido')
        fisc = (re.search(r'Fiscalidad en la venta:\s*([A-Z ]+?)(?=\s+REF|$)', txt) or [None, ''])[1].strip()
        calle_l = limpiar_calle(calle)
        planta = (re.search(r'Planta:\s*([^|]+)', spec) or [None, ''])[1].strip()
        puerta = (re.search(r'Puerta:?\s*([^|]+)', spec) or [None, ''])[1].strip()
        esc = (re.search(r'Esc(?:alera)?:?\s*([^|]+)', spec) or [None, ''])[1].strip()
        direccion = calle.strip() if DIRECCION_COMPLETA else calle_l
        extra_dir = ', '.join(x for x in [('Esc. ' + esc) if esc else '', ('Planta ' + planta) if planta else '', ('Puerta ' + puerta) if puerta else ''] if x) if DIRECCION_COMPLETA else ''
        pnombre, ccaa = (PROV[pid][0], PROV[pid][1]) if pid else (prov_txt, '')
        out.append(dict(
            ref=ref, hw_id=hw_id, titulo=('%s en %s, %s' % (tipo, calle_l, municipio)).strip(', ') if tipo else titulo,
            direccion=direccion, detalle_direccion=extra_dir,
            tipo=tipo, categoria=categoria(tipo), municipio=municipio, provincia=pnombre, comunidad=ccaa,
            precio=precios[0] if precios else None, precio_anterior=precios[1] if len(precios) > 1 else None,
            m2=int(float(((m2.group(1) or m2.group(2)) if m2 else '0').replace('.', '')) or 0) or None,
            hab=hab.group(1) if hab else None, mapa=' '.join(x for x in [direccion if DIRECCION_COMPLETA else calle_l, municipio, pnombre] if x),
            img=img if img.startswith('http') else None, situacion=sit, estado=estado,
            etiquetas=[b for b in badges if na(b) != na(estado)], fiscalidad=fisc, lote=bool(re.match(r'^\d+\s', tipo) or 'lote' in na(tipo)),
            ficha=None, origen='HipogesWorks'))
    return out

def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, '..', 'HIPOGES SUSPENDIDOS')
    ficheros = sorted(glob.glob(os.path.join(carpeta, '**', '*.htm*'), recursive=True))
    if not ficheros: sys.exit('No hay paginas .html en ' + carpeta)
    todos, sin_prov = {}, 0
    for f in ficheros:
        filas = parsear(open(f, encoding='utf-8', errors='ignore').read())
        print('%-60s %3d activos' % (os.path.relpath(f, carpeta)[:60], len(filas)))
        for d in filas:
            if not d['ref']: continue
            if not d['comunidad']: sin_prov += 1
            todos[d['ref'].upper()] = d
    dest = os.path.join(RAIZ, 'colaboradores', '_hipoges'); os.makedirs(dest, exist_ok=True)
    por = {}
    for d in todos.values(): por.setdefault(d['comunidad'] or 'Sin comunidad', []).append(d)
    for cc, filas in por.items():
        nombre = re.sub(r'[^a-z0-9]+', '-', na(cc)).strip('-')
        previo = os.path.join(dest, nombre + '.json')
        existentes = {x['ref'].upper(): x for x in json.load(open(previo, encoding='utf-8'))} if os.path.exists(previo) else {}
        existentes.update({x['ref'].upper(): x for x in filas})
        json.dump(list(existentes.values()), open(previo, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('-> %-25s %5d nuevos/actualizados, %5d en total' % (cc, len(filas), len(existentes)))
    print('Activos unicos: %d | sin provincia reconocida: %d' % (len(todos), sin_prov))

if __name__ == '__main__':
    main()
