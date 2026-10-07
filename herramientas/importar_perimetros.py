"""Importa los perímetros de Hipoges (Excel) a la Zona Colaboradores.

Uso:  python herramientas/importar_perimetros.py "C:/ruta/carpeta_con_los_excel"
Detecta cada fichero por su nombre y guarda colaboradores/_hipoges/perimetro-<nombre>.json
(el Perímetro VI sustituye a nacional-*.json y las Cesiones de Remate a cesiones-remate.json).
Luego ejecuta generar_listado_colaboradores.py y publica.

SOLO SE PUBLICA: referencia del activo, dirección (calle, población y provincia, sin número,
planta ni puerta), tipo de inmueble, precio si lo hay y el tipo de operación (NPL / CDR / REO / ocupado).
NUNCA: deudor, cartera, cliente, gestor, carpeta, préstamos, deuda, OB, cargas, tasaciones, catastro,
finca/registro, juzgado, autos, fases judiciales, abogados, procuradores, información de ocupantes,
enlaces de portales ni coordenadas.
"""
import sys, os, re, json, glob
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from importar_hipogesworks import na, PROV, MUNI
from importar_nacional import ficha, txt, provincia, TIPOS

INFO = ' Cualquier información adicional sobre este activo puede solicitarse a Dulas y se facilitará sin problema.'
NOTA = {
    'NPL': 'VENTA DE CRÉDITO (NPL). Se adquiere el préstamo hipotecario impagado, no el inmueble. Sin visitas. Precio orientativo sujeto a aprobación.' + INFO,
    'CDR': 'CESIÓN DE REMATE (CDR) procedente de NPL. Se cede el derecho de remate de la subasta judicial; la adjudicación y la posesión dependen del juzgado. Sin visitas. Precio orientativo sujeto a aprobación.' + INFO,
    'REO': 'INMUEBLE ADJUDICADO (REO). Consultar estado de posesión y posibilidad de visita. Precio orientativo sujeto a aprobación.' + INFO,
    'Ocupado': 'INMUEBLE ADJUDICADO (REO) OCUPADO. La entrega depende del procedimiento de posesión. Sin visitas. Precio orientativo sujeto a aprobación.' + INFO,
    'VUELO': 'REO EN VUELO: adjudicación en curso a favor del fondo. Sin visitas. Precio orientativo sujeto a aprobación.' + INFO,
}
ETIQ = {'NPL': ['Venta de crédito NPL'], 'CDR': ['Cesión de remate', 'Procedente de NPL'], 'REO': ['REO'], 'Ocupado': ['REO ocupado'],
        'VUELO': ['REO en vuelo', 'Adjudicación en curso']}

TIPOS2 = dict(TIPOS)
TIPOS2.update({'vivienda': 'Piso', 'vivenda unif.': 'Casa', 'casa': 'Casa', 'parcela': 'Solar', 'nave': 'Nave', 'local': 'Local',
               'apartment / flat': 'Piso', 'terraced house': 'Adosado', 'detached house': 'Casa', 'semi-detached house': 'Chalet Pareado',
               'urban land': 'Solar', 'agricultural land': 'Finca Rústica', 'store': 'Local', 'garage': 'Garaje', 'warehouse': 'Nave',
               'vivienda_bloque_piso': 'Piso', 'apartamento': 'Piso', 'local_comercial': 'Local', 'parcela_vivienda': 'Solar',
               'nave_industrial': 'Nave', 'vivienda_aislada': 'Casa', 'otro': 'Otro', 'edificio': 'Edificio', 'wip': 'Obra en curso',
               'plaza garaje': 'Plaza de Garaje', 'adosado': 'Adosado', 'suelo urbano': 'Solar', 'oficina': 'Oficina', 'trastero': 'Trastero',
               'detached_house': 'Casa', 'terraced_house': 'Adosado', 'duplex': 'Dúplex', 'residential': 'Vivienda', 'annex': 'Anejo',
               'retail': 'Local', 'buildable land': 'Solar', 'industrial': 'Nave', 'land': 'Suelo', 'non-residential': 'Otro',
               'commercial': 'Local', 'hotel': 'Hotel', 'flat': 'Piso', 'house': 'Casa',
               'parking space': 'Plaza de Garaje', 'apartment': 'Piso', 'ready-to-build urban plot': 'Solar',
               'high street retail': 'Local', 'non-irrigated agricultural land': 'Finca Rústica', 'non-consolidated urban plot': 'Suelo',
               'storage space': 'Trastero', 'finca_rustica': 'Finca Rústica', 'irrigated agricultural land': 'Finca Rústica',
               'urbanizable plot (urb. & repar. plan approved)': 'Suelo Urbanizable', 'urbanizable plot (non-sectorized)': 'Suelo Urbanizable',
               'vivienda_pareada': 'Chalet Pareado', 'plaza_garaje': 'Plaza de Garaje', 'logistics warehouse': 'Nave',
               'multiuse warehouse': 'Nave', 'stand alone / retail park unit': 'Local', 'building': 'Edificio',
               'garage/store': 'Garaje', 'apartment /store': 'Piso', 'suelo rustico': 'Finca Rústica'})
import importar_nacional
importar_nacional.TIPOS.update(TIPOS2)


def num(v):
    n = re.sub(r'[^\d]', '', txt(v).split('.')[0]) if not isinstance(v, (int, float)) or pd.isna(v) else str(int(v))
    return int(n) if n and int(n) >= 500 else None


def prov_de(ciudad, prov):
    p = re.sub(r'\s+', ' ', txt(prov).split(';')[0]).strip()
    if provincia(p): return p
    c = na(txt(ciudad).split(',')[0].split(';')[0])
    for pid, lst in MUNI.items():
        if any(v == c for v, _ in lst): return PROV[pid][0]
    return p


def reg(ref, sit, tipo, ciudad, prov, direccion, precio=None, estado='En comercialización', origen=''):
    prov = prov_de(ciudad, prov)
    if not txt(tipo): tipo = 'Inmueble'
    d = ficha(ref, 'CDR' if sit == 'CDR' else ('NPL' if sit == 'NPL' else ('Ocupado' if sit == 'Ocupado' else 'REO')),
              tipo, ciudad, prov, direccion, precio, list(ETIQ[sit]), '', estado=estado)
    d['notas'] = NOTA[sit]; d['situacion_legal'] = ''; d['origen'] = origen
    return d


def limpiar_dir(s):
    """Quita '(CP Municipio ...)' y textos tras la coma del final de las direcciones completas."""
    s = re.split(r'\(\s*\d{5}|,\s*\d{5}', txt(s))[0]
    return s


def leer(f, sheet=0, header=0):
    return pd.read_excel(f, sheet_name=sheet, header=header)


def npl_anticipa(f):
    d = leer(f); out = {}
    for _, r in d.iterrows():
        rid = txt(r.get('ID Prinex'))
        if not rid or txt(r.get('PL NPL')) != 'NPL': continue
        out[rid] = reg(rid, 'NPL', r.get('Tipo Inmueble'), r.get('Municipio'), r.get('Provincia'), limpiar_dir(r.get('Dirección Completa Inmueble')), origen='NPL Anticipa')
    return out


def cdr_anticipa(f):
    d = leer(f); out = {}
    for _, r in d.iterrows():
        rid = txt(r.get('ID Prinex'))
        if not rid.startswith(('VI-', 'CA-')): continue
        out[rid] = reg(rid, 'CDR', 'Vivienda', r.get('Municipio'), r.get('Provincia'), limpiar_dir(r.get('Dirección')), origen='CDR Anticipa')
    return out


def cesiones(f):
    d = leer(f); out = {}
    for _, r in d.iterrows():
        pid = txt(r.get('PropertyID'))
        if not pid: continue
        out['CDR-' + pid] = reg('CDR-' + pid, 'CDR', r.get('Typology'), r.get('Town'), r.get('Province'), r.get('Address'), num(r.get('AskingPrice')), origen='Cesiones de remate')
    return out


def lezama_reo(f):
    d = leer(f, header=1); out = {}
    for _, r in d.iterrows():
        pid = txt(r.get('ID Property')); t = na(txt(r.get('Type')))
        if not pid: continue
        oc = na(txt(r.get('Información ocupantes')))
        sit = 'CDR' if 'cesion' in t else ('Ocupado' if 'ocupad' in t or ('ocupad' in oc and 'vacio' not in oc) else 'REO')
        ref = ('CDR-' if sit == 'CDR' else 'REO-') + pid
        est = 'Próximamente' if na(txt(r.get('Stage Status'))) == 'securing' else 'En comercialización'
        out[ref] = reg(ref, sit, r.get('Tipologia'), r.get('Localidad'), r.get('Provincia'), r.get('PropertyAddress'), num(r.get('Precio Publicacion')), est, 'Lezama REO')
    return out


def lezama_vuelo(f):
    d = leer(f, header=1); out = {}
    for _, r in d.iterrows():
        pid = txt(r.get('ID Property'))
        if not pid: continue
        out['REO-' + pid] = reg('REO-' + pid, 'VUELO', r.get('Tipologia'), r.get('Localidad'), r.get('Provincia'), r.get('PropertyAddress'), num(r.get('Precio previo CDR')), 'Próximamente', 'Lezama REO en vuelo')
    return out


def colat(f):
    d = leer(f, header=2); out = {}; n = {}
    for _, r in d.iterrows():
        cod = txt(r.get('Deudor'))
        if not cod: continue
        n[cod] = n.get(cod, 0) + 1
        ref = '%s-%02d' % (cod, n[cod])
        out[ref] = reg(ref, 'NPL', r.get('Tipología'), r.get('Ciudad') or r.get('Provincia'), r.get('Provincia'), r.get('Dirección del inmueble'), origen='Perímetro Colat')
    return out


def aurora(f):
    d = leer(f); out = {}
    for _, r in d.iterrows():
        ref = txt(r.get('reference_code'))
        if not ref or na(txt(r.get('legalphase'))) == 'terminado': continue
        out[ref] = reg(ref, 'NPL', r.get('property_type'), r.get('city'), r.get('province'), re.sub(r'\s+\S+\s*\(.*$', '', txt(r.get('ADRESS'))), origen='Cartera Aurora')
    return out


def camino(f):
    d = leer(f, header=1); out = {}
    for _, r in d.iterrows():
        cid = txt(r.get('Colateral ID ')); st = txt(r.get('Status'))
        if not cid or st == 'Closed' or txt(r.get('Status3')) == 'Vendido': continue
        oc = na(txt(r.get('Ocupational Status')))
        sit = 'NPL' if st == 'Active' else ('Ocupado' if 'ocupada' in oc else 'REO')
        ref = '%s-%s' % (txt(r.get('Portfolio')).upper()[:3], cid)
        out[ref] = reg(ref, sit, txt(r.get('Subtipo de Activo')) or txt(r.get('Tipo De Activo')), r.get('Localidad'), r.get('Provincia'),
                       txt(r.get('Dirección completa')).split(',')[0], origen='Perímetro Camino-Segovia')
    return out


def qasar(f):
    d = leer(f, 'DT Credit Sale', header=2); out = {}
    for _, r in d.iterrows():
        aid = txt(r.get('Asset ID'))
        if not aid or txt(r.get('Status Listed (Publicacion)')) != 'Publicado': continue
        out['QSR-' + aid] = reg('QSR-' + aid, 'NPL', r.get('Main Use'), r.get('Town'), r.get('Province'), r.get('Address'), origen='NPL Qasar')
    return out


def campana_q4(f):
    d = leer(f, header=2); out = {}
    EST = {'suspendido': 'Suspendido', 'on_sale': 'En comercialización', 'offer_received': 'Oferta recibida', 'pre_marketing': 'Próximamente'}
    for _, r in d.iterrows():
        ref = txt(r.get('Property IDH'))
        if not ref: continue
        sit = 'Ocupado' if 'ocupado' in na(txt(r.get('Libre /Ocupado'))) else 'REO'
        calle = ' '.join(x for x in [txt(r.get('Street Type')).capitalize(), txt(r.get('Address'))] if x)
        out[ref] = reg(ref, sit, r.get('Property SubType'), r.get('Town'), r.get('Province'), calle, None,  # precio a consultar (decision Dulas)
                       EST.get(txt(r.get('Marketing Status')), 'En comercialización'), 'Campaña Q4')
    return out


FICHEROS = [  # (patron del nombre, funcion, fichero de salida)
    ('npl anticipa', npl_anticipa, 'perimetro-npl-anticipa'), ('cdr anticipa', cdr_anticipa, 'perimetro-cdr-anticipa'),
    ('cesiones de remate', cesiones, 'cesiones-remate'), ('reo y aat', lezama_reo, 'perimetro-lezama-reo'),
    ('reo en vuelo', lezama_vuelo, 'perimetro-lezama-vuelo'), ('perimetro colat', colat, 'perimetro-colat'),
    ('aurora', aurora, 'perimetro-aurora'), ('camino-segovia', camino, 'perimetro-camino-segovia'),
    ('npl qasar', qasar, 'perimetro-qasar'), ('datacampanaq4', campana_q4, 'perimetro-campana-q4'),
]


def main():
    carpeta = sys.argv[1]
    dest = os.path.join(RAIZ, 'colaboradores', '_hipoges'); os.makedirs(dest, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(carpeta, '*.xlsx'))):
        nombre = na(os.path.basename(f)).replace('í', 'i')
        if 'perimetro vi' in nombre:   # perímetro nacional (hojas reos / cdr / npl)
            x = pd.ExcelFile(f)
            for hoja, fn in (('npl', importar_nacional.npl), ('cdr', importar_nacional.cdr), ('reos', importar_nacional.reo)):
                filas = fn(x.parse(hoja))
                for d in filas:
                    sit = {'NPL': 'NPL', 'CDR': 'CDR', 'Ocupado': 'Ocupado'}.get(d['situacion'], 'REO')
                    d['etiquetas'] = list(ETIQ[sit]) + (['Lanzamiento suspendido'] if d.get('estado') == 'Suspendido' else [])
                    d['situacion_legal'] = ''; d['notas'] = NOTA[sit]
                sal = 'nacional-' + {'reos': 'reo'}.get(hoja, hoja)
                json.dump(filas, open(os.path.join(dest, sal + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
                print('%-48s %-6s %5d activos' % (os.path.basename(f)[:48], hoja, len(filas)))
            continue
        for pat, fn, sal in FICHEROS:
            if pat in nombre:
                filas = [d for d in fn(f).values() if d['comunidad']]
                json.dump(filas, open(os.path.join(dest, sal + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
                sin = sum(1 for d in filas if not d['comunidad'])
                print('%-48s %5d activos%s' % (os.path.basename(f)[:48], len(filas), ('  (%d sin provincia)' % sin) if sin else ''))
                break
        else:
            print('NO RECONOCIDO:', os.path.basename(f))


if __name__ == '__main__':
    main()
