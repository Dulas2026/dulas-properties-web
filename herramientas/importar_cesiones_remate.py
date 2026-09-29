"""Importa el 'Fichero Cesiones de Remate' (Excel de Hipoges) a la Zona Colaboradores.

Uso:  python herramientas/importar_cesiones_remate.py "C:/ruta/Fichero Cesiones de Remate 2026.09.11.xlsx"
Guarda colaboradores/_hipoges/cesiones-remate.json (sustituye al anterior). Luego ejecuta
generar_listado_colaboradores.py y publica.

NO se copian datos internos: cartera (Portfolio), carpeta (Folder), gestor (Sales Manager),
referencia catastral, enlace del anuncio, numero/planta/puerta de la direccion, marcas New/Deleted ni estados internos de Hipoges.
Los activos 'Out Of Stock' o marcados como borrados no se publican.
"""
import sys, os, re, json
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from importar_hipogesworks import na, ALIAS, PROV, MUNI, categoria  # mismas tablas de provincias y municipios
from importar_nacional import calle as solo_calle  # nombre de la via sin numero/planta/puerta

TIPOS = {
    'apartment / flat': 'Piso', 'penthouse': 'Ático', 'terraced house': 'Adosado',
    'semi-detached house': 'Chalet Pareado', 'detached house': 'Casa', 'urban land': 'Parcela Urbana',
    'agricultural land': 'Finca Rústica', 'storage': 'Trastero', 'store': 'Local', 'garage': 'Garaje',
    'parking': 'Plaza de Garaje', 'warehouse': 'Nave', 'office': 'Oficina', 'building': 'Edificio',
}
CATEGORIA = {'Nave': 'Industrial', 'Plaza de Garaje': 'Anejo', 'Garaje': 'Anejo', 'Trastero': 'Anejo'}

ETIQUETAS = ['Cesión de remate', 'Procedente de NPL']
SITUACION_LEGAL = 'Cesión de remate (CDR) · NPL'
NOTAS = ('Operación de CESIÓN DE REMATE procedente de un préstamo hipotecario impagado (NPL). '
         'No es una compraventa directa del inmueble: se cede el derecho de remate obtenido en la subasta judicial, '
         'y la adjudicación y la posesión dependen del procedimiento. Sin visitas interiores salvo indicación. '
         'Precio orientativo sujeto a aprobación. Cualquier información adicional sobre este activo puede solicitarse a Dulas y se facilitará sin problema.')


def bonito(s):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    if s.isupper() or s.islower():
        s = ' '.join(p if re.fullmatch(r'[A-Z]{1,2}/?', p) else p.capitalize() for p in s.split(' '))
        s = re.sub(r'\b(De|Del|La|Las|Los|El|Y|En)\b', lambda m: m.group(1).lower(), s)
    return s


def municipio(town, pid):
    t = na(town)
    for v, b in MUNI.get(pid, []):
        if v == t:
            return b
    return bonito(town)


def main():
    if len(sys.argv) < 2:
        sys.exit('Indica la ruta del Excel de Cesiones de Remate')
    df = pd.read_excel(sys.argv[1])
    out, fuera, sin_prov = [], [], []
    for _, r in df.iterrows():
        pid = str(r['PropertyID']).strip()
        estado_int = str(r.get('PropertyStageStatus') or '')
        borrado = str(r.get('Deleted **') or '').strip().lower() not in ('', 'nan', 'no')
        if borrado or na(estado_int) == 'out of stock':
            fuera.append(pid); continue
        prov_id = ALIAS.get(na(r['Province']), '')
        if not prov_id:
            m = re.match(r'(.+),\s*(\w+)$', str(r['Province']))
            prov_id = ALIAS.get(na('%s %s' % (m.group(2), m.group(1))) if m else '', '')
        if not prov_id:
            sin_prov.append(pid)
        provincia, ccaa = (PROV[prov_id][0], PROV[prov_id][1]) if prov_id else (bonito(r['Province']), '')
        muni = municipio(r['Town'], prov_id)
        tipo = TIPOS.get(na(r['Typology']), bonito(r['Typology']))
        calle = solo_calle(r['Address'])
        precio = re.sub(r'[^\d]', '', str(r['AskingPrice']).split('.')[0])
        estado = 'En comercialización' if na(estado_int) == 'marketing' else 'Próximamente'
        out.append(dict(
            ref='CDR-' + pid, titulo='%s en %s, %s' % (tipo, calle, muni) if calle else '%s en %s' % (tipo, muni),
            direccion=calle, detalle_direccion='', tipo=tipo, categoria=CATEGORIA.get(tipo) or categoria(tipo),
            municipio=muni, provincia=provincia, comunidad=ccaa,
            precio=int(precio) if precio else None, precio_anterior=None, m2=None, hab=None,
            mapa=' '.join(x for x in [calle, muni, provincia] if x), img=None,
            situacion='CDR', estado=estado, etiquetas=list(ETIQUETAS), situacion_legal=SITUACION_LEGAL,
            notas=NOTAS, fiscalidad='', lote=False, ficha=None, origen='Cesiones de remate Hipoges'))
    dest = os.path.join(RAIZ, 'colaboradores', '_hipoges'); os.makedirs(dest, exist_ok=True)
    json.dump(out, open(os.path.join(dest, 'cesiones-remate.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('%d cesiones de remate guardadas | %d no publicadas (Out Of Stock/borradas): %s' % (len(out), len(fuera), ', '.join(fuera)))
    if sin_prov: print('Sin provincia reconocida:', ', '.join(sin_prov))


if __name__ == '__main__':
    main()
