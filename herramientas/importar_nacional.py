"""Importa el Excel 'NACIONAL' (hojas NPL, CDR y REO) a la Zona Colaboradores.

Uso:  python herramientas/importar_nacional.py "C:/ruta/NACIONAL.xlsx"
Guarda colaboradores/_hipoges/nacional-npl.json, nacional-cdr.json y nacional-reo.json
(sustituye los anteriores). Luego ejecuta generar_listado_colaboradores.py y publica.

DATOS QUE NUNCA SE COPIAN: nombre del deudor/titular, cartera y cliente, IDs de Pipedrive/LinkedIn,
Connection/Contract ID, finca y registro, referencia catastral, deuda, OB, cargas, responsabilidad
hipotecaria, juzgado, n.º de autos, fechas del procedimiento, estado de negociación con el deudor
y cualquier dato de vulnerabilidad. La dirección se publica SOLO con el nombre de la calle
(sin número, planta ni puerta), porque en NPL y REO suele ser la vivienda del deudor u ocupante.
"""
import sys, os, re, json
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from importar_hipogesworks import na, ALIAS, PROV, MUNI, categoria

TIPOS = {
    'flat': 'Piso', 'piso': 'Piso', 'residencial': 'Vivienda', 'house': 'Casa', 'town house': 'Casa de Pueblo',
    'casa de pueblo': 'Casa de Pueblo', 'detached house': 'Casa', 'unifamiliar independiente': 'Casa',
    'terraced house': 'Adosado', 'adosado': 'Adosado', 'semidetached house': 'Chalet Pareado', 'pareado': 'Chalet Pareado',
    'parking': 'Plaza de Garaje', 'garaje': 'Garaje', 'storage': 'Trastero', 'trastero': 'Trastero',
    'retail': 'Local', 'local comercial': 'Local', 'office': 'Oficina', 'oficinas': 'Oficina',
    'warehouse': 'Nave', 'nave industrial': 'Nave', 'land': 'Suelo', 'terreno urbano - urbanizable': 'Suelo Urbanizable',
    'terreno urbano - solar': 'Solar', 'rustic land': 'Finca Rústica', 'terreno rustico': 'Finca Rústica',
    'other': 'Otro', 'otros': 'Otro',
}
CATEGORIA = {'Nave': 'Industrial', 'Plaza de Garaje': 'Anejo', 'Garaje': 'Anejo', 'Trastero': 'Anejo',
             'Suelo': 'Terreno', 'Suelo Urbanizable': 'Terreno', 'Solar': 'Terreno', 'Vivienda': 'Residencial'}

NOTA = {
    'NPL': ('VENTA DE CRÉDITO (NPL). Se adquiere el préstamo hipotecario impagado, no el inmueble: '
            'el comprador se subroga como acreedor y la propiedad solo se obtiene por acuerdo con el deudor '
            'o tras la ejecución hipotecaria. Sin visitas. Precio orientativo sujeto a aprobación. Cualquier información adicional sobre este activo puede solicitarse a Dulas y se facilitará sin problema.'),
    'CDR': ('CESIÓN DE REMATE (CDR) procedente de NPL. No es una compraventa directa: se cede el derecho '
            'de remate obtenido en la subasta judicial y la adjudicación y la posesión dependen del juzgado. '
            'Sin visitas. Precio orientativo sujeto a aprobación. Cualquier información adicional sobre este activo puede solicitarse a Dulas y se facilitará sin problema.'),
    'REO': ('INMUEBLE ADJUDICADO (REO) PENDIENTE DE POSESIÓN. La propiedad ya es del fondo pero el inmueble '
            'está ocupado; la entrega depende del procedimiento de desahucio o toma de posesión. Sin visitas. '
            'Precio orientativo sujeto a aprobación.'
            ' Cualquier información adicional sobre este activo puede solicitarse a Dulas y se facilitará sin problema.'),
}


def txt(v):
    return '' if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() in ('nan', '0', '-') else str(v).strip()


def bonito(s):
    s = re.sub(r'\s+', ' ', txt(s))
    if s.isupper() or s.islower():
        s = ' '.join(p.capitalize() for p in s.split(' '))
        s = re.sub(r'(?<=\s)(De|Del|La|Las|Los|El|Y|En|I)\b', lambda m: m.group(1).lower(), s)
    return s


def calle(s):
    """Solo el nombre de la via: sin numero, planta, puerta ni textos detras."""
    s = re.split(r'\d|,|\(|\bS/N\b|\bN[ºo°]|(?<=\s)(?:[AÁ]tico|Bajo|Baj|Planta|Plt|Esc|Izq|Izda|Dcha)\b', txt(s), flags=re.I)[0]
    s = re.sub(r'\b(No Consta|OD)\b', '', s, flags=re.I)
    s = bonito(s.strip(' .-/'))
    return '' if len(s) < 3 or na(s) in ('calle', 'avenida', 'avda', 'plaza', 'camino', 'cj g', 'no consta') else s


def provincia(p):
    pid = ALIAS.get(na(txt(p)), '')
    if not pid:
        m = re.match(r'(.+),\s*(\w+)$', txt(p))
        pid = ALIAS.get(na('%s %s' % (m.group(2), m.group(1))), '') if m else ''
    return pid


def municipio(town, pid):
    t = na(txt(town))
    for v, b in MUNI.get(pid, []):
        if v == t:
            return b
    return bonito(town)


def precio(v):
    n = re.sub(r'[^\d]', '', txt(v).split('.')[0])
    return int(n) if n and int(n) >= 500 else None


def ficha(ref, sit, tipo_raw, city, prov, direccion, p, etiquetas, legal, estado='En comercialización', m2=None):
    pid = provincia(prov)
    pn, cc = (PROV[pid][0], PROV[pid][1]) if pid else (bonito(prov), '')
    mu = municipio(city, pid)
    tipo = TIPOS.get(na(txt(tipo_raw)), bonito(tipo_raw) or 'Inmueble')
    via = calle(direccion)
    return dict(ref=ref, titulo=('%s en %s, %s' % (tipo, via, mu)) if via else '%s en %s' % (tipo, mu),
                direccion=via, detalle_direccion='', tipo=tipo, categoria=CATEGORIA.get(tipo) or categoria(tipo),
                municipio=mu, provincia=pn, comunidad=cc, precio=p, precio_anterior=None,
                m2=m2, hab=None, mapa=' '.join(x for x in [via, mu, pn] if x), img=None,
                situacion=sit, estado=estado, etiquetas=etiquetas, situacion_legal=legal, notas=NOTA[sit if sit in NOTA else 'REO'],
                fiscalidad='', lote=False, ficha=None, origen='Hipoges NACIONAL')


def npl(df):
    out = {}
    for _, r in df.iterrows():
        aid = txt(r.get('Asset ID'))
        if not aid or txt(r.get('CATEGORIA')) != 'NPL':
            continue
        fase = txt(r.get('Estado Judicial Mapeo'))
        d = ficha('NPL-' + aid, 'NPL', r.get('Subtype of Collateral') or r.get('Type of Collateral'), r.get('Asset City'),
                  r.get('Asset Province'), r.get('Asset Address'), precio(r.get('PRECIO ORIENTATIVO')),
                  ['Venta de crédito NPL'] + (['Fase judicial: ' + fase] if fase else []),
                  'NPL · ' + (fase or 'Fase judicial sin informar'))
        prev = out.get(d['ref'])
        if not prev or (d['precio'] or 0) > (prev['precio'] or 0):
            out[d['ref']] = d
    return list(out.values())


def cdr(df):
    out = {}
    for _, r in df.iterrows():
        aid = txt(r.get('ASSET_ID'))
        if not aid:
            continue
        paral = txt(r.get('MOTIVO_PARALIZACION'))
        if paral:  # archivado / regularizado: ya no esta disponible
            continue
        out['CDR-' + aid] = ficha('CDR-' + aid, 'CDR', r.get('ASSET_SUBTYPE') or r.get('ASSET_TYPE'), r.get('LOCALIDAD'),
                                  r.get('PROVINCIA'), r.get('DIRECCIÓN'), precio(r.get('Precio CdR')),
                                  ['Cesión de remate', 'Procedente de NPL', 'Pendiente de fijar la cesión'],
                                  'Cesión de remate (CDR) · NPL · Fase: ' + (txt(r.get('DESCRIPCION_SUBFASE')) or 'Adjudicación'))
    return list(out.values())


OCUPACION = {'si.okupado': 'Ocupado sin título', 'si.deudor': 'Ocupado por el antiguo propietario',
             'si.3o con titulo': 'Ocupado por tercero con título'}


def reo(df):
    out = {}
    for _, r in df.iterrows():
        aid = txt(r.get('Asset Id'))
        if not aid:
            continue
        oc = na(txt(r.get('Estado ocupación')))
        subestado = na(txt(r.get('Subestado demanda')))
        suspendido = 'suspendido' in subestado or 'vulnerab' in oc
        ocupacion = OCUPACION.get(oc, 'Ocupado' if oc.startswith('si') else '')
        grado = txt(r.get('GRADO AVANCE JUDICIAL DESAHUCIO'))
        et = ['REO · Pendiente de posesión'] + ([ocupacion] if ocupacion else []) + (['Lanzamiento suspendido'] if suspendido else [])
        legal = 'REO ocupado · Desahucio: ' + (grado.capitalize() if grado else 'sin informar') + (' · SUSPENDIDO' if suspendido else '')
        m2 = re.sub(r'[^\d.]', '', txt(r.get('m2')))
        out['REO-' + aid] = ficha('REO-' + aid, 'Ocupado' if ocupacion else 'REO', r.get('Subtipo activo') or r.get('Tipo activo'),
                                  r.get('Localidad'), r.get('Provincia'), r.get('Direccion'), precio(r.get('Precio orientativo')),
                                  et, legal, estado='Suspendido' if suspendido else 'En comercialización',
                                  m2=int(float(m2)) if m2 and float(m2) > 0 else None)
    return list(out.values())


def main():
    if len(sys.argv) < 2:
        sys.exit('Indica la ruta del Excel NACIONAL')
    x = pd.ExcelFile(sys.argv[1])
    dest = os.path.join(RAIZ, 'colaboradores', '_hipoges'); os.makedirs(dest, exist_ok=True)
    for hoja, fn in (('NPL', npl), ('CDR', cdr), ('REO', reo)):
        if hoja not in x.sheet_names:
            print('Hoja %s no encontrada' % hoja); continue
        filas = fn(x.parse(hoja))
        json.dump(filas, open(os.path.join(dest, 'nacional-%s.json' % hoja.lower()), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        sin = sum(1 for d in filas if not d['comunidad'])
        print('%-4s %5d activos%s' % (hoja, len(filas), (' (%d sin provincia reconocida)' % sin) if sin else ''))


if __name__ == '__main__':
    main()
