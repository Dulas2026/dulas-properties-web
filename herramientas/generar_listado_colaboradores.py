"""Genera colaboradores/activos.json (listado privado de la Zona Colaboradores)
a partir de las fichas publicadas (activo-*.html) y del CV_DATA de Baleares.
Uso:  python herramientas/generar_listado_colaboradores.py
Si existe colaboradores/datos_internos.json (precio colaborador, comision, situacion,
fotos... sacados de HipogesWorks) se fusiona por referencia."""
import re, json, glob, html, os, unicodedata
from urllib.parse import unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

def t(x): return html.unescape(re.sub(r'<[^>]+>', '', x or '')).strip()
def sin_acentos(s): return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

def categoria(tipo):
    s = sin_acentos(tipo)
    if re.search(r'hotel', s): return 'Hotel'
    if re.search(r'oficina', s): return 'Oficina'
    if re.search(r'nave|industrial', s) and not re.search(r'piso|casa|vivienda', s): return 'Industrial'
    if re.search(r'suelo|solar|finca|parcela|terreno|rustic', s): return 'Terreno'
    if re.search(r'piso|casa|chalet|adosad|duplex|atico|apartamento|estudio|loft|vivienda|residencial|pareado|bungalow', s): return 'Residencial'
    if re.search(r'local|comercial', s): return 'Comercial'
    if re.search(r'garaje|trastero|plaza|parking|anejo', s): return 'Anejo'
    return 'Otro'

PROV = {'Santa  C. de Tenerife': 'Santa Cruz de Tenerife', 'Alicante': 'Alicante/Alacant', 'Valencia': 'Valencia/València',
        'Castellón': 'Castellón/Castelló', 'Islas Baleares': 'Illes Balears'}
CV = ('Comunitat Valenciana', 'Alicante/Alacant', 'Valencia/València', 'Castellón/Castelló')

out = {}
for f in sorted(glob.glob('activo-*.html')):
    s = open(f, encoding='utf-8').read()
    info = {k.strip(): t(v) for k, v in re.findall(r'class="prop-info-key">(.*?)</.*?class="prop-info-val">(.*?)</', s, re.S)}
    g = lambda c: (lambda m: t(m.group(1)) if m else '')(re.search(r'class="%s"[^>]*>(.*?)</' % c, s, re.S))
    bc = re.search(r'class="prop-breadcrumb".*?</div>', s, re.S)
    links = re.findall(r'<a [^>]*>(.*?)</a>', bc.group(0)) if bc else []
    ccaa = t(links[2]) if len(links) >= 3 else ''
    pn = re.sub(r'[^\d]', '', g('prop-price'))
    m2 = None
    for v, l in re.findall(r'class="prop-spec-val"[^>]*>(.*?)</.*?class="prop-spec-label"[^>]*>(.*?)</', s, re.S):
        if '²' in t(l) or 'superficie' in t(l).lower(): m2 = re.sub(r'[^\d]', '', t(v)) or None
    mq = re.search(r'google\.com/maps\?q=([^&"]+)', s)
    cuerpo = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    sit = 'CDR' if re.search(r'\bCDR\b|Cesi[oó]n de remate', cuerpo) else ('NPL' if re.search(r'\bNPL\b', cuerpo) else ('Ocupado' if re.search(r'ocupad[oa]', cuerpo, re.I) else ''))
    out[f] = dict(ref=info.get('Referencia') or g('prop-price-sub').replace('REF:', '').strip(), titulo=g('prop-title'),
                  tipo=info.get('Tipo', ''), municipio=info.get('Municipio', ''), provincia=info.get('Provincia', ''),
                  comunidad=ccaa, precio=int(pn) if pn else None, hab=info.get('Habitaciones') or None,
                  m2=int(m2) if m2 else None, ficha=f, mapa=unquote(mq.group(1)) if mq else '', situacion=sit, img=None)

for f in ['activos-baleares.html', 'activos-baleares-2.html']:
    s = open(f, encoding='utf-8').read()
    for d in json.loads(re.search(r'const CV_DATA\s*=\s*(\[.*?\]);', s, re.S).group(1)):
        fi = d.get('ficha') or d['ref']
        img = d.get('img') if d.get('img') and not str(d.get('img')).startswith('http') else None
        sit = d.get('clasif') or ('Ocupado' if d.get('badge') == 'Ocupado' else '')
        if fi in out:
            out[fi]['img'] = out[fi]['img'] or img
            out[fi]['situacion'] = out[fi]['situacion'] or sit
            continue
        out[fi] = dict(ref=d['ref'], titulo=d.get('titulo', ''), tipo=d.get('tipo', ''), municipio=d.get('municipio', ''),
                       provincia=d.get('isla', ''), comunidad='Illes Balears', precio=d.get('price'), hab=d.get('hab'),
                       m2=d.get('m2'), ficha=d.get('ficha'), mapa=(d.get('calle', '') + ' ' + d.get('municipio', '')).strip(),
                       situacion=sit, img=img)

# Fichas propias con nombre (alcudia, conforama...): usar la referencia real que aparece en la ficha
REFS_FICHAS = json.load(open('herramientas/referencias_fichas.json', encoding='utf-8')) if os.path.exists('herramientas/referencias_fichas.json') else {}
for d in out.values():
    reales = REFS_FICHAS.get(str(d['ref']).lower())
    if reales:
        d['alias'] = [d['ref']] + reales[1:]
        d['ref'] = reales[0]

# Quitar duplicados por referencia (el mismo activo puede estar en una ficha y en el CV_DATA)
por_ref = {}
for k, d in list(out.items()):
    r = str(d['ref']).upper()
    if r in por_ref:
        a = out[por_ref[r]]
        for campo in ('img', 'situacion', 'ficha', 'm2', 'hab', 'precio', 'mapa', 'alias'):
            if not a.get(campo) and d.get(campo): a[campo] = d[campo]
        del out[k]
    else:
        por_ref[r] = k

# Activos importados de HipogesWorks (paginas guardadas) -> tienen prioridad sobre los datos de la web publica
hip = {}
for f in glob.glob('colaboradores/_hipoges/*.json'):
    for d in json.load(open(f, encoding='utf-8')):
        hip[str(d['ref']).upper()] = d
if hip:
    existentes = {str(d['ref']).upper(): k for k, d in out.items()}
    for r, d in hip.items():
        if r in existentes:
            viejo = out[existentes[r]]
            d = dict(d); d['ficha'] = viejo.get('ficha') or d.get('ficha'); d['alias'] = viejo.get('alias') or d.get('alias')
            out[existentes[r]] = d
        else:
            out['hw:' + r] = dict(d)

internos = {}
if os.path.exists('colaboradores/datos_internos.json'):
    internos = {str(x['ref']).upper(): x for x in json.load(open('colaboradores/datos_internos.json', encoding='utf-8'))}

L = []
for d in out.values():
    d['provincia'] = PROV.get(d['provincia'], d['provincia'])
    if d['provincia'] in CV: d['comunidad'] = 'Comunitat Valenciana'
    if isinstance(d['precio'], str):
        n = re.sub(r'[^\d]', '', d['precio']); d['precio'] = int(n) if n else None
    if d['hab'] in ('N/D', '', '0'): d['hab'] = None
    if d['m2'] == 0: d['m2'] = None
    d['categoria'] = d.get('categoria') or categoria(d['tipo'])
    d['lote'] = d.get('lote') or bool(re.match(r'^\d+\s', d['tipo']) or 'lote' in d['tipo'].lower())
    for campo, defecto in (('estado', 'En comercialización'), ('precio_colaborador', None), ('comision', None), ('situacion_legal', ''), ('notas', ''), ('situacion', ''), ('img', None), ('mapa', '')):
        d.setdefault(campo, defecto)
    extra = internos.get(str(d['ref']).upper())
    if extra: d.update({k: v for k, v in extra.items() if v not in (None, '')})
    L.append(d)

# Un fichero por comunidad autonoma + un indice (la zona privada carga solo la comunidad elegida)
import shutil
def slug(x): return re.sub(r'[^a-z0-9]+', '-', sin_acentos(x)).strip('-') or 'sin-comunidad'
os.makedirs('colaboradores/datos', exist_ok=True)
for viejo in glob.glob('colaboradores/datos/*.json'): os.remove(viejo)
if os.path.exists('colaboradores/activos.json'): os.remove('colaboradores/activos.json')
grupos = {}
for d in L: grupos.setdefault(d['comunidad'] or 'Sin comunidad', []).append(d)
indice = []
for ccaa, filas in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
    sl = slug(ccaa)
    json.dump(filas, open('colaboradores/datos/%s.json' % sl, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    cats, sits, provs = {}, {}, {}
    for d in filas:
        cats[d['categoria']] = cats.get(d['categoria'], 0) + 1
        k = d['situacion'] or '_'; sits[k] = sits.get(k, 0) + 1
        if d['provincia']: provs[d['provincia']] = provs.get(d['provincia'], 0) + 1
    precios = [d['precio'] for d in filas if d['precio'] and d['precio'] >= 1000]
    indice.append(dict(comunidad=ccaa, slug=sl, total=len(filas), categorias=cats, situaciones=sits,
                       provincias=sorted(provs, key=lambda k: -provs[k]),
                       poblaciones=sorted({d['municipio'] for d in filas if d['municipio']}),
                       precio_min=min(precios) if precios else None, precio_medio=round(sum(precios) / len(precios)) if precios else None))
json.dump(indice, open('colaboradores/datos/indice.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
# Indice de referencias para el buscador global de la Zona Colaboradores
refs = [[d['ref'], slug(d['comunidad'] or 'Sin comunidad'), d.get('titulo') or d.get('tipo') or '', d.get('municipio') or '', d.get('alias') or []] for d in L]
json.dump(refs, open('colaboradores/datos/referencias.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
print(len(L), 'activos'); print(Counter(d['categoria'] for d in L)); print(Counter(d['situacion'] or '-' for d in L))
print('de HipogesWorks', len(hip), '|', 'con foto', sum(1 for d in L if d['img']), '| con mapa', sum(1 for d in L if d['mapa']), '| con datos internos', sum(1 for d in L if str(d['ref']).upper() in internos))
