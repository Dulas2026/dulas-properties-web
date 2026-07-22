# Estado del proyecto: activos por comunidad autónoma (Dulas Properties)

Última actualización: sesión del 9 de julio de 2026 (tramo 20 - 5 activos de "ocupados-singulares" añadidos a Baleares).

## BUG: botón "Buscar activos" y mapa de `activos.html` rotos por residuo de Cloudflare Rocket Loader (11 julio 2026) — RESUELTO
- El usuario avisó de que el botón "Buscar activos →" de la portada no hacía nada.
- Causa real: el `<script>` que define `heroSearch()` en `index.html` tenía el atributo
  `type="5292fc3926c2be843bfc9ca8-text/javascript"` en vez de un tipo válido. Ese hash es un residuo de
  Cloudflare Rocket Loader (que reescribe scripts para diferirlos y los reconstruye en el navegador); al
  quedar guardado tal cual en el HTML estático, el navegador nunca lo reconocía como JavaScript ejecutable,
  así que ni el carrusel del hero rotaba ni `heroSearch()` llegaba a existir.
- Se encontró el mismo problema en `activos.html`, con dos scripts afectados: la carga de `d3.v7.min.js` y
  el bloque que define `CCAA_COLORS` y dibuja el mapa. Es decir, el mapa interactivo de esa página llevaba
  tiempo sin funcionar realmente.
- Arreglado quitando el hash de `type="...-text/javascript"` y dejándolo en `type="text/javascript"` en
  ambos archivos. Verificado con una barrida completa del sitio: no queda ningún otro script con este
  patrón corrupto.
- Pendiente de confirmar tras el próximo deploy que el botón de búsqueda y el mapa de `activos.html`
  funcionan en vivo.

## TRAMO 20 (9 julio 2026): Fichero ocupados-singulares.xlsx — 5 activos añadidos a Baleares

El usuario subió `Fichero ocupados-singulares.xlsx` (6.631 filas, cartera nacional, 48 columnas,
mucho más sensible que el anterior: número de portal/planta/puerta, Referencia Catastral, IDUFIR,
fase de desahucio/lanzamiento, tipo de ocupante (squatter/debtor/ilegal_tenant), Cash for Keys,
precio a brokers y nombre del gestor comercial).

- Filtrado a Baleares + `Marketing Status = suspendido` (criterio "como siempre"): 9 filas.
- **4 duplicados detectados y excluidos**: CIRE-03464 (San Vicente de Paul, Palma, 219.000 — ya
  publicado como "sanvicente"), JARE-1469 (Pizarro, Cala Ratjada, 245.000 — ya "calaratjada"),
  MORE-2879 (Joan Rosselló, Palma, 795.000 — ya "joanrosello"), PERE-003257 (Baladre, Palma,
  224.400 — ya "rafal"). Detectados cruzando municipio + calle + precio a brokers contra los 19
  listados propios ya publicados.
- **5 activos nuevos**: CIRE-03255 (Llucmajor), CIRE-04960 (Felanitx), LIRE-02964 (Capdepera),
  PERE-005234 (Palma de Mallorca), RETI-02008 (Manacor). Clasificados NPL/CDR según fase de
  procedimiento (`Fase Procedimiento` vacía = NPL; `lanzamiento`/`sentencia`/`esperando_fecha_lanzamiento`
  = CDR, ya en fase de ejecución). Resultado: 2 NPL / 3 CDR.
- Por petición explícita del usuario, **no se publica precio** en estos 5 activos (el único precio
  disponible en el fichero era "Price to brokers", un dato interno de comisión, no el precio de
  venta) — las tarjetas muestran "Consultar precio" y CTA de "Solicitar información". Tampoco se
  publica el tipo de ocupante, fase de desahucio, cash for keys, IDUFIR, catastral, portfolio,
  gestor comercial ni equipo comercial — ninguno de esos 43 campos restantes del fichero se usó.
  Solo se usó: municipio, calle (sin número), tipo de inmueble, m², fase legal (para NPL/CDR) y
  la referencia pública del inmueble (mismo esquema de REF que ya se usa en el resto del sitio).
- Añadidos al mismo `CV_DATA` de `activos-baleares.html` (114 → **119 activos**). Actualizado
  `index.html` (114 → 119, total cartera 1774 → 1779).
- **Incidencia técnica**: al editar `activos-baleares.html` escribiendo directamente en la carpeta
  montada (sin pasar por un archivo temporal primero), el archivo se truncó a mitad de palabra
  (mismo bug ya documentado). Se detectó de inmediato con `Read`, se restauró desde la copia previa
  y se repitió el cambio escribiendo primero a un archivo temporal y copiando después — verificado
  completo con `Read`. **Lección reforzada**: nunca escribir directamente sobre un archivo ya
  publicado en la carpeta montada; siempre escribir a un archivo nuevo/temporal primero y copiar
  después, verificando con `Read` (no con `bash tail`/`wc`).
- Auditoría final (regex): 0 fugas de Esc/Pl/Pt/Nº/catastral/IDUFIR/tipo de ocupante/gestor/precio
  a broker/nombre de portfolio en el archivo publicado.
- **Pendiente de confirmar por el usuario**: ejecutar `deploy.bat`.

## TRAMO 19 (9 julio 2026): NPLBALEARES.xlsx depurado y publicado en activos-baleares.html

El usuario subió `NPLBALEARES.xlsx` (15.160 filas, cartera nacional) pidiendo preparar los activos
de Baleares para la web quitando cualquier información problemática.

- Filtrado a `provinc == 'Islas Baleares'`: 146 filas brutas.
- **Depuración de direcciones**: solo se conserva el nombre de calle; se quitó número de portal,
  Esc:/Pl:/Pt:, "Nº X", referencia catastral y el importe del préstamo (`loan_gbv`) del dataset
  publicado.
- **Nombres de cartera/portfolio**: por petición explícita del usuario, nunca se publica el nombre
  de una cartera. Se detectaron 5 carteras agrupadas bajo un mismo préstamo (mismo `loan_gbv`
  repetido en varias filas): Gremi Fusters (13 garajes/oficina, Palma), Las Planas de Siller (19
  suelos, Pollença), Coma de Ses Bolengues (8 suelos, Son Servera, con una variante que además
  llevaba el prefijo "CALLE" pegado — detectado y corregido), Judith (4 plazas de garaje, Palma) y
  Ficus (3 tramos de préstamo del mismo piso, Sant Llorenç des Cardassar). Todas se redujeron a 1
  activo representativo sin mostrar el nombre de la agrupación (solo municipio + tipo).
- **Deduplicación general**: cualquier dirección duplicada (mismo texto o mismo `loan_gbv` con señal
  de dirección poco fiable) se redujo a 1 fila representativa. 146 filas → **95 activos finales**.
- **Clasificación NPL/CDR** (decidido con el usuario): fase legal anterior a la convocatoria de
  subasta (`admision_demanda`, `requerimiento_pago`, `preparacion_doc`, `vista`, etc.) = **NPL**
  (crédito en mora); desde `subasta_convocatoria` en adelante = **CDR** (cesión de remate). Resultado:
  68 NPL / 27 CDR.
- **Revisión previa**: se generó `REVISAR-baleares-npl-cdr.html` (borrador no enlazado, con el mismo
  estilo de tarjetas del sitio) + un Excel con las 95 filas para que el usuario revisara antes de
  publicar. Aprobado por el usuario.
- **Publicación**: `activos-baleares.html` se reconstruyó al patrón CV_DATA estándar (como Sevilla),
  preservando los 19 listados propios de Dulas (fotos reales, "Ver ficha", badges
  Disponible/Ocupado) y añadiendo los 95 activos NPL/CDR con franja de color ya definida en
  `styles.css` (`.badge-npl`, `.badge-cdr`) — pedido explícito del usuario de que la franja NPL/CDR
  quede "muy muy clara". Filtros por isla (Mallorca/Menorca/Ibiza), tipo y estado. Nuevo total de la
  página: **114 activos** (antes 19).
- Actualizado `index.html`: tarjeta de región Illes Balears (19 → 114) y contador total de activos
  en cartera (1679 → 1774).
- Auditoría final (regex sobre el `CV_DATA` publicado): 0 fugas de Esc/Pl/Pt/Nº/número de portal,
  0 referencias a los 5 nombres de cartera detectados.
- **Pendiente de confirmar por el usuario**: ejecutar `deploy.bat`. También queda `REVISAR-baleares-npl-cdr.html`
  en la carpeta (borrador ya aprobado, sin enlazar) — se puede borrar si el usuario lo confirma.

## TRAMO 18 (9 julio 2026): Imágenes de mapa rotas en casi toda la web — diagnóstico y fix completo

## TRAMO 18 (9 julio 2026): Imágenes de mapa rotas en casi toda la web — diagnóstico y fix completo

El usuario reportó que, salvo Baleares, ninguna página mostraba imagen en las tarjetas de activos.

**Causa raíz**: el parámetro `text=` (geocodificación por texto) de la API de Yandex Static Maps
dejó de funcionar — cualquier petición devuelve HTTP 400 `"Unable to evaluate area of interest"`.
Este parámetro era el que se usaba como fallback en la mayoría de páginas para generar el mapa
a partir de la dirección, así que se rompió de golpe en todo el sitio.

**Fix aplicado, página por página** (17 páginas revisadas):
- **Cataluña y Murcia**: ya corregidas en el tramo anterior con coordenadas reales (Photon/OSM →
  Yandex `ll=`/`pt=`). Sin cambios adicionales.
- **Castilla y León**: 12 imágenes con `text=` roto → geocodificadas con Photon y convertidas a
  Yandex `ll=`.
- **Castilla-La Mancha** (225 tarjetas), **Asturias** (36), **Cantabria** (32), **La Rioja** (90),
  **Canarias** (223, conserva su rama de foto Street View cuando hay `panoid`): todas usaban
  `text=` roto → migradas al **embed oficial de Google Maps** (`google.com/maps?q=...&output=embed`
  en un `<iframe>`), que no requiere API key ni geocodificación previa y no depende de Yandex.
- **Navarra** y **Galicia**: la mayoría de tarjetas ya usaban coordenadas correctas; se encontraron
  y corrigieron 1 y 2 imágenes sueltas respectivamente que aún tenían `text=` roto (mismo fix de
  iframe de Google Maps).
- **Aragón, Comunitat Valenciana, Madrid, País Vasco, Sevilla**: ya tenían implementado el mismo
  embed de Google Maps desde una sesión anterior — no necesitaron cambios, solo pendientes de
  desplegar.
- **Extremadura y Baleares** (fotos Street View): no se vieron afectadas, sin cambios.

**Bug colateral encontrado y corregido**: al escribir archivos grandes por script, el archivo se
truncaba a mitad de palabra en el footer (bug recurrente ya documentado). Se detectó y corrigió en
Castilla y León, Castilla-La Mancha, Navarra y Galicia — todas terminaban cortadas antes de
`</html>`. Verificado con la herramienta de lectura (no con `tail`/`wc` de bash, que en este entorno
a veces da lecturas obsoletas).

**Auditoría de privacidad**: 0 fugas de número de portal/escalera/planta/puerta en las 8 páginas
tocadas en este tramo.

- **Pendiente de confirmar por el usuario**: ejecutar `deploy.bat` y verificar en vivo que los
  mapas cargan en todas las páginas.

## TRAMO 17 (9 julio 2026): Murcia ampliada (tarea pendiente #2)

Se reanudó la tarea pausada de ampliar `activos-murcia.html` más allá de las páginas iniciales.

- Filtro HipogesWorks: Estado inmueble = Suspendido + Comunidad autónoma = Murcia → 1.971 activos
  encontrados en total.
- La página 6 (siguiente inmediata a las ya extraídas) resultó ser 100% duplicada de refs ya
  presentes en el archivo — confirma que la extracción original ya cubría varias páginas no
  contiguas por diversidad, no solo las páginas 1-5. El "bug de paginación" de sesiones anteriores
  parece haber sido más bien la naturaleza extremadamente repetitiva del catálogo (grandes
  promociones nuevas con decenas de unidades idénticas: "Novopalmar" en El Palmar, urbanización
  Corvera Golf & Country Club) que un fallo técnico real.
- Estrategia aplicada: saltos a páginas dispersas (6, 20, 35, 50, 70, 100, 115, 130) tomando 1-2
  registros representativos por cada portfolio masivo repetido, priorizando diversidad de
  municipios sobre volumen.
- Resultado: **51 activos nuevos** (0 duplicados con los 225 existentes), total ahora
  **276 activos** en 35 municipios distintos (antes solo unos pocos municipios repetidos).
  Nuevos municipios incorporados: Lorca, San Pedro del Pinatar, Mazarrón, Molina de Segura,
  Totana, Campos del Río, Cartagena, Águilas, Alguazas, San Javier, Cieza, Santomera, Archena,
  Calasparra, Torre-Pacheco, Cehegín, Jumilla, Mula, La Unión, entre otros.
- Todas las direcciones nuevas limpiadas de número de portal antes de incorporarlas al `CV_DATA`
  (norma interna de privacidad). Auditoría final sobre los 276 registros: 0 fugas.
- El contador de activos es dinámico (`CV_DATA.length`), no requirió tocar texto estático en la
  página de Murcia. Sí se actualizó en `index.html`: tarjeta de región (225 → 276) y contador
  total de la cartera (1628 → 1679).
- **Pendiente de confirmar por el usuario**: ejecutar `deploy.bat`.
- Sigue pendiente Tarea #11 (ampliar Canarias más allá de 223/1.338 activos) como siguiente paso.

## TRAMO 16 (9 julio 2026): Cataluña re-extraída completa desde HipogesWorks

`activos-cataluna.html` estaba roto: 177/180 activos sin calle/municipio/provincia (campos vacíos)
y sin coordenadas — no era arreglable con parches de imagen, había que re-extraer desde cero.

- Sesión en HipogesWorks caducada al empezar; se pidió al usuario iniciar sesión manualmente
  (nunca se introduce la contraseña). Confirmado por el usuario.
- Filtro aplicado: Estado inmueble = Suspendido + Comunidad autónoma = Cataluña → 4.618 activos
  encontrados. Se extrajeron 9 páginas (135 registros en bruto) siguiendo la regla de
  "diversidad antes que volumen": 1 registro representativo por portfolio duplicado, priorizando
  cobertura de las 4 provincias catalanas y de varios tipos de inmueble.
- Resultado: **114 activos únicos** con calle, municipio y provincia reales, repartidos así:
  Barcelona 65 · Girona 18 · Tarragona 16 · Lleida 9.
- Todas las direcciones limpiadas de número de portal / Esc / Pl / Pt antes de publicar (norma
  interna de privacidad). Auditoría final: 0 fugas.
- Imagen de mapa: Yandex Static Maps con consulta de texto (calle + municipio + provincia) en
  las 114 tarjetas — 0 imágenes de Google Maps (que sabemos que está roto en todo el sitio).
- **Hallazgo colateral importante**: el archivo `activos-cataluna.html` original (y probablemente
  otros generados con el mismo patrón de tarjetas estáticas, como Galicia) terminaba truncado
  literalmente a mitad del footer, sin `</div></footer></body></html>`. El navegador lo renderiza
  bien porque cierra las etiquetas automáticamente, así que no se notaba visualmente, pero es un
  archivo corrupto de fondo. El nuevo `activos-cataluna.html` se generó completo y verificado
  byte a byte (termina correctamente en `</html>`). **Recomendación para la próxima sesión**:
  revisar si Galicia, Extremadura, Baleares, Castilla-La Mancha y Castilla y León tienen el mismo
  problema de cierre incompleto, aunque no afecte a la visualización.
- Actualizado en `index.html`: contador de la tarjeta de región (180 → 114), provincias mostradas,
  y el contador total de activos en cartera (1694 → 1628).
- `activos.html` ya tenía enlazada Cataluña de una sesión anterior (mapa clicable) — no requirió
  cambios.
- **Pendiente de confirmar por el usuario**: ejecutar `deploy.bat` para publicar este cambio.
- **Siguiente en la cola** (según instrucción del usuario "solucionamos cataluña y después seguimos
  con las demás"): Tarea #2 (ampliar Murcia, páginas 6-45) y Tarea #11 (ampliar Canarias más allá
  de 223/1.338 activos).

## TRAMO 15 (9 julio 2026): auditoría completa comunidad por comunidad

## TRAMO 15 (9 julio 2026): auditoría completa comunidad por comunidad

Verificación pedida por el usuario antes de seguir publicando: privacidad + imagen de mapa + carga
en producción, una por una, en las 17 páginas.

- **Privacidad (local, todas las páginas)**: 0 fugas encontradas (direcciones exactas, Esc/Pl/Pt,
  número de portal). Solo se corrigió 1 activo suelto en Navarra (SBRE-0120666) que aún tenía el
  placeholder roto `via.placeholder.com` en vez de un mapa Yandex.
- **Carga e imagen en producción, comprobado con navegador real**: Comunitat Valenciana (81/81,
  ya estable tras el 3er arreglo), Navarra (15/15), Illes Balears (19/19), Castilla-La Mancha
  (225/225), Aragón (39/39), Asturias (36/36), Cantabria (32/32), La Rioja (90/90), Madrid (15/15),
  Murcia (225/225), Canarias (223/223), País Vasco (120/120), Andalucía/Sevilla (306/306),
  Castilla y León (12/12), Extremadura (30/30), Galicia (45/45) → **16 de 17 comunidades: perfectas.**
- **Cataluña sigue rota** (ya detectado en el tramo 13, confirmado de nuevo): sus 177 activos no
  tienen ni calle, ni municipio, ni provincia (título y ubicación vacíos), y la imagen sigue
  apuntando a Google Maps sin clave. No es arreglable con un parche — necesita re-extraerse desde
  HipogesWorks de cero, igual que Aragón/Asturias/etc. Sigue pendiente de decisión con el usuario.

**Pendiente: nuevo `deploy.bat`** para publicar el arreglo de Navarra.

## TRAMO 14 (8 julio 2026): activos-comunitat-valenciana.html se corta solo, tercera vez

Tras el redeploy del tramo 13, se verificó de nuevo en producción: Galicia y Navarra funcionaban
perfectamente (imágenes Yandex, activos visibles), pero **Comunitat Valenciana volvía a mostrar 0
activos** — el mismo síntoma de las veces anteriores (script cortado antes de cerrar `</script>`).

Esto ya es la tercera vez en la misma sesión que este archivo en concreto pierde el final del
script después de corregirlo y publicarlo. Las otras 15 páginas con la misma estructura nunca han
tenido este problema. No tenemos visibilidad de qué lo causa exactamente (podría ser algo en el
proceso de guardado/sincronización de ese archivo en el ordenador del usuario, un editor abierto
con autoguardado, o algo del propio `deploy.bat`/wrangler específico de ese archivo). Se ha vuelto
a completar el script de la misma manera. **Recomendación pendiente de trasladar al usuario**: si
vuelve a pasar, comprobar si tiene `activos-comunitat-valenciana.html` abierto en algún editor de
texto/código en su ordenador que pueda estar sobrescribiéndolo con una versión antigua.

**Pendiente: nuevo `deploy.bat`.**

## TRAMO 13 (8 julio 2026): imágenes en blanco por API de Google sin clave

El usuario mandó una captura de `activos-galicia.html` en producción: las tarjetas cargaban pero
el mapa salía en blanco. Causa: esas imágenes usaban
`https://maps.googleapis.com/maps/api/staticmap` (Google Static Maps), que **requiere una clave de
API de pago** — sin ella, Google no devuelve ninguna imagen. Es un servicio distinto del que usa el
resto del sitio (Yandex Static Maps, que no requiere clave).

Se encontró el mismo problema en 4 archivos más, todos con coordenadas reales embebidas en la URL
rota (fácil de convertir):
- **Galicia**: 43/45 activos — corregido (convertido a Yandex con las mismas coordenadas).
- **Extremadura**: 30/30 activos — corregido.
- **Navarra**: archivo nuevo (`activos-navarra.html`, 15 activos) — corregido, auditado (0 fugas de
  privacidad) y **enlazado por primera vez** en index.html y activos.html (antes no existía ningún
  archivo para esta comunidad). Nuevo total: **1.694 activos, 17 regiones activas** (España
  completa, ya no queda ninguna comunidad autónoma sin publicar).
- **Comunitat Valenciana**: 1 uso (la rama con lat/lon del renderCard) — corregido de nuevo a
  Yandex.

### Pendiente sin resolver: Cataluña
`activos-cataluna.html` (177 activos) usa el mismo Google Maps roto, pero a diferencia de las
anteriores **no tiene coordenadas guardadas** (`center=%20`, un valor vacío) — y tampoco tiene
calle, municipio ni provincia rellenos en ninguno de sus 177 registros (`card-title` y
`card-location` están vacíos, solo se conservan precio y REF). No es solo un problema de imagen:
esta página no tiene ninguna información de ubicación utilizable. No se puede arreglar con un
cambio de URL — haría falta **volver a extraer Cataluña desde HipogesWorks** igual que se hizo con
La Rioja/Aragón/Asturias/Cantabria. Pendiente de decidir con el usuario si se aborda ahora o más
adelante.

**Pendiente: nuevo `deploy.bat`** para publicar estas correcciones.

## TRAMO 12 (8 julio 2026): activos-comunitat-valenciana.html no mostraba ningún activo

Al verificar en producción los cambios del tramo 11, se detectó que la página de Comunitat
Valenciana cargaba (título correcto) pero **mostraba 0 activos** — el contador y la rejilla
aparecían vacíos. Diagnóstico con la consola del navegador: el `<script>` de la página nunca se
cerraba (faltaba `</script></body></html>`), cortado literalmente a mitad de la función
`applyFilters`. Al no cerrarse el script, el navegador no podía ejecutar ni siquiera la primera
línea (`const CV_DATA = [...]`), así que la página entera quedaba en blanco de datos.

Parece un defecto que ya existía en el archivo desde antes de esta sesión (no relacionado con el
cambio de imágenes del tramo 11) y que nadie había detectado porque el título y la cabecera de la
página cargan igual aunque el script falle. Se comprobó el resto de páginas con el mismo patrón
(Aragón, Asturias, Cantabria, La Rioja, Canarias, Madrid, Murcia, País Vasco, Sevilla): todas
cierran correctamente su script, solo Comunitat Valenciana estaba afectada.

**Corrección**: se completó el final del script (cierre de `applyFilters`, llamada a
`populateTipoOptions()`/`renderAll()`, los tres `addEventListener`, y las etiquetas de cierre
`</script></body></html>`) copiando la misma estructura que usan el resto de páginas de este
mismo pipeline. Verificado localmente que el archivo ahora es completo.

**Pendiente: nuevo `deploy.bat`** para publicar esta corrección (y las del tramo 11 si aún no se
habían subido del todo).

## TRAMO 11 (8 julio 2026): ~830 activos sin imagen de mapa — corregido

El usuario pidió comprobar que todos los activos tienen imagen de localización de la calle (sin
número exacto). Al revisar el código de cada página se encontró que la mayoría de las comunidades
nunca llegaron a tener imagen real: la función que genera cada tarjeta dependía de un campo
`panoid` (Street View) o `lat/lon` que casi nunca se rellenó durante la extracción, y en su
ausencia mostraba un cuadro gris "Imagen de calle no disponible" en el 100% de los casos.

### Diagnóstico (antes de la corrección)
- **0% de imagen real** (830 activos): Aragón (39), Asturias (36), Cantabria (32), La Rioja (90),
  Canarias (223), Madrid (15), Murcia (225), País Vasco (120).
- **Parcial**: Comunitat Valenciana (33/81 con imagen), Sevilla/Andalucía (291/306 con imagen),
  Galicia (43/45, 2 activos con placeholder roto).
- **100% ya correcto**: Castilla-La Mancha, Castilla y León, Cataluña, Extremadura (225+12+180+30),
  y Baleares (19/19, combinando fotos reales y Street View).

### Corrección aplicada
En las 8 comunidades al 0% y en el "else" de Valencia/Sevilla, se sustituyó el aviso "no
disponible" por un mapa Yandex generado a partir de **calle (sin número) + municipio + provincia**
— la misma técnica que ya funcionaba bien en Castilla-La Mancha/Cataluña/Castilla y León/
Extremadura. Se mantiene el Street View real (`panoid`) para los pocos activos que sí lo tienen.
En Galicia se sustituyeron los 2 activos con enlace placeholder roto (`via.placeholder.com`) por el
mismo tipo de mapa. Verificado tras el cambio: 0 referencias a "Imagen de calle no disponible" o a
placeholders rotos en ningún archivo.

Como el mapa se genera a partir del campo "calle" ya depurado (sin Esc/Pl/Pt/número de portal), no
se introduce ninguna dirección exacta nueva — sigue mostrando solo la zona de la calle, igual que
las comunidades que ya funcionaban bien.

**Pendiente: nuevo `deploy.bat`** para que las imágenes se vean en producción.

## TRAMO 10 (8 julio 2026): chequeo general — privacidad, enlaces y carga en producción

El usuario pidió comprobar que todas las comunidades funcionan, abren sin problemas y solo muestran
la calle (nunca el número exacto). Resultado:

### Fugas de privacidad encontradas y corregidas
- **activos-castilla-lamancha.html**: 6 registros con número de portal/Esc/Pl/Pt/código postal
  visibles ("Avenida Libertad 61/70 Bonete", "Rª Ronda de San Isidoro 2 1 Sótano 1 00001/00002
  Tarancón", "Calle Mayor 12 1 Fontanar", y el código de parcela "2.11.1" de un suelo industrial).
  Corregido en card-title, WhatsApp y el `src` del mapa Yandex (que también incluía la dirección
  completa en texto).
- **activos-galicia.html**: 1 registro ("Paraje LG A Insua, 109") con número de casa tras coma.
- **activos-baleares.html**: 7 registros con número de portal (Gran Via Asima 6, Calle Aragó 211,
  Camino dels Reis 164, Avenida Joan Miró 287, Travesía de Sant Jordi 29, Calle Jaume Juan 11,
  Calle Son Oliva 3). Esta comunidad tiene además **7 fichas individuales** (asima.html,
  conforama.html, garaje.html, joanmiro.html, menorca.html, solarsantamaria.html, sonoliva.html)
  enlazadas desde "Ver ficha" que repetían el mismo número exacto en título, meta descripción,
  breadcrumb, H1, dirección y enlaces de WhatsApp — todas corregidas.
- Verificado 0 fugas en el resto (Castilla y León, Cataluña, Aragón, Asturias, Cantabria, La Rioja,
  Comunitat Valenciana, Canarias, Madrid, Murcia, Sevilla, País Vasco, Extremadura).

### Página fantasma encontrada
- **activos-extremadura.html** ya existía en la carpeta (30 activos, Badajoz y Cáceres, 0 fugas)
  y ya estaba en el mapa (`activos.html`), pero **nunca se enlazó en index.html**. Enlazada ahora
  (dropdown, tarjeta de región, stats). Nuevo total: **1.679 activos, 16 regiones activas**.

### Enlace roto corregido
- El mapa (`activos.html`) tenía preconfigurada la entrada "Navarra" apuntando a
  `activos-navarra.html`, un archivo que **nunca se creó**. Al hacer clic en Navarra, esto habría
  producido el mismo fallo que el de País Vasco (redirección/fallo silencioso). Se quitó la entrada
  del mapa: ahora Navarra muestra correctamente "Próximamente" hasta que se publique esa comunidad.

### Comprobación de carga en producción (www.dulasproperties.com)
Probadas las 16 páginas con navegador real. **14 cargan correctamente** con su propio contenido:
Aragón, Asturias, La Rioja, Castilla-La Mancha, Castilla y León, Cataluña, Galicia, Baleares,
Canarias, Madrid, Murcia, País Vasco, Andalucía/Sevilla y Comunitat Valenciana.

**2 todavía no están en producción** (caen de vuelta a la home, mismo síntoma que el bug original,
pero es simplemente que no se han desplegado aún): **Cantabria** (creada en el tramo 8, después
del último despliegue) y **Extremadura** (recién enlazada en este tramo). Los cambios de este
tramo (privacidad de Castilla-La Mancha/Galicia/Baleares, enlace de Extremadura, quitar Navarra del
mapa) tampoco están aún en producción.

**Pendiente: el usuario debe ejecutar `deploy.bat` de nuevo** para publicar todo lo anterior.

## TRAMO 9 (8 julio 2026): activos-valencia-NUEVO.html — descartado, no publicar

- El usuario encontró `activos-valencia-NUEVO.html` (6 KB, 111 "activos") accesible en la rama
  preview `main.dulas-properties.pages.dev` y preguntó si se podía publicar.
- Investigación: es un **borrador antiguo sin depurar**, anterior al pipeline de limpieza de esta
  sesión. Comparado registro a registro contra `activos-comunitat-valenciana.html` (el que está
  publicado, 82 activos):
  - Los ~76 registros que sí pertenecen a Alicante/Castellón/Valencia **ya están todos** en
    `activos-comunitat-valenciana.html`, en varios casos ya corregidos (direcciones con
    Esc:/Pl:/Pt: y número de portal fueron limpiadas al pasar al archivo publicado).
  - Los ~29 registros restantes pertenecen a **otras comunidades** (Illes Balears ~17, Barcelona,
    Tarragona x2, Murcia, Jaén, Málaga, Madrid x2) etiquetados incorrectamente como Comunitat
    Valenciana — mezcla de datos de un scrape antiguo sin filtrar.
  - Contiene **fugas de privacidad activas**: al menos 6 registros con dirección exacta
    (número de portal + Esc/Pl/Pt), incluida una fuga grave con "Nº 5" completo (REF LIRE-08712,
    que ni siquiera se incluyó en el archivo publicado, correctamente).
- **Conclusión: no se publica.** No aporta activos nuevos y violaría la regla de "solo calle, nunca
  número exacto". Es un residuo de una versión anterior, ya superada por el archivo en producción.
- **Resuelto**: el usuario confirmó, se eliminó `activos-valencia-NUEVO.html` de la carpeta.

## TRAMO 8 (8 julio 2026): Cantabria publicado

### Cantabria — PUBLICADA (32 activos)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = Cantabria → **837 activos** encontrados.
- 3 páginas recorridas (de 56 totales), priorizando diversidad (21 municipios: Santander,
  Torrelavega, Reinosa, Camargo, Reocín, Piélagos, Cartes, Ampuero, Cabezón de la Sal y más)
  frente a los portfolios repetitivos de Reocín (Villapresente) y Torrelavega (Calle Santander).
- **Incidencia de UI repetida esta vez**: al cambiar de comunidad autónoma sin recargar la página,
  el campo de texto a veces conserva el valor anterior y concatena el nuevo (p. ej. quedó
  "AsturiasCantabria"). Fix aplicado: usar Ctrl+A dentro del campo antes de escribir el nuevo
  valor, en vez de asumir que un solo click/triple-click limpia el contenido previo.
- 0 fugas de privacidad. Filtro de página por Municipio.
- Enlazada en activos.html (ya tenía la entrada `cantabria` preconfigurada) y en index.html.
- Nuevo total: **1.649 activos, 15 regiones activas**.

## TRAMO 7 (8 julio 2026): Asturias publicado

### Asturias — PUBLICADA (36 activos)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = Asturias → **668 activos** encontrados.
- Solo 3 páginas recorridas (de 45 totales): dominado por el portfolio repetitivo "8 Pisos en BOLADO"
  en Grado (varias copias casi idénticas) — se tomó 1 registro representativo y se priorizó
  diversidad (11 municipios: Oviedo, Gijón, Avilés, Siero, Langreo, Carreño, Mieres, Grado,
  Llanera, San Martín del Rey Aurelio, Corvera de Asturias).
- **Nota de UI en esta sesión**: el formulario de filtros de HipogesWorks re-scrollea/reflowa según
  el contenido de resultados (fotos vs "Foto no disponible"), lo que desplaza las coordenadas de
  los campos entre una captura y otra. Pasó dos veces que el texto tecleado cayó en el campo
  equivocado (Portfolio en vez de Comunidad autónoma). Lección: tras cada scroll, tomar screenshot
  y confirmar visualmente la posición exacta del campo antes de teclear, no asumir coordenadas fijas.
- 0 fugas de privacidad. Filtro de página por Municipio.
- Enlazada en activos.html (ya tenía la entrada `asturias` preconfigurada) y en index.html.
- Nuevo total: **1.617 activos, 14 regiones activas**.

## TRAMO 6 (8 julio 2026): Aragón publicado

### Aragón — PUBLICADA (39 activos)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = Aragón → **702 activos** encontrados.
- Solo se recorrieron 5 páginas (de 47 totales): a partir de la página 2-3 el catálogo se llena de
  dos portfolios masivos muy repetitivos — "96 Pisos + Local + 79 Trasteros + 135 Garajes" en
  Muela (La), Zaragoza (311 activos subordinados) y "43 Suelos Urbanos Residenciales" en Zuera,
  Zaragoza (43 activos subordinados) — se tomó 1 registro representativo de cada portfolio y se
  priorizó diversidad (16 municipios, las 3 provincias: Zaragoza/Huesca/Teruel) sobre volumen.
- 0 fugas de privacidad. Filtro de página por Provincia (Zaragoza/Huesca/Teruel).
- Enlazada en activos.html (ya tenía la entrada `aragon` preconfigurada) y en index.html.
- Nuevo total: **1.581 activos, 13 regiones activas**.
- Pendiente si se quiere ampliar: quedan ~42 páginas más (mayormente los dos portfolios repetidos).

## TRAMO 5 (8 julio 2026): Bug de despliegue resuelto + privacidad en Castilla-La Mancha + La Rioja publicada

### Bug de despliegue a producción — RESUELTO
El dominio real (www.dulasproperties.com) llevaba varias sesiones sin reflejar ningún cambio,
mientras que `main.dulas-properties.pages.dev` sí se veía actualizado. Causa encontrada: el
proyecto Cloudflare Pages "dulas-properties" tiene como **rama de producción "production"**, no
"main". `deploy.bat` publicaba con `wrangler pages deploy . --project-name=dulas-properties` sin
especificar rama, así que Cloudflare lo trataba como una implementación de vista previa de la
rama "main" y nunca llegaba a producción (ni por tanto al dominio real). Se corrigió `deploy.bat`
añadiendo `--branch=production`. Lección para el futuro: cualquier script de despliegue de este
proyecto DEBE incluir `--branch=production` explícitamente.

### Privacidad — Castilla-La Mancha (fuga encontrada y corregida)
Se descubrió que `activos-castilla-lamancha.html` (225 activos, no generada en esta sesión) tenía
3 registros con dirección exacta expuesta (número de portal, escalera, planta, puerta):
ALRE-01680, ALRE-05696, ALRE-00012. Corregido dejando solo el nombre de calle, tanto en el título
de la tarjeta como en el enlace de WhatsApp y en la URL del mapa estático.

### Descubrimiento: 4 páginas "fantasma" ya existían pero no estaban enlazadas
Al buscar "otra comunidad sin activos" se encontró que `activos-castilla-lamancha.html` (225),
`activos-castilla-leon.html` (12), `activos-cataluna.html` (180) y `activos-galicia.html` (45) YA
EXISTÍAN en la carpeta (de una sesión/proceso anterior no documentado) y ya estaban correctamente
enlazadas en el mapa de `activos.html`, pero **nunca se habían añadido a index.html** (ni
desplegable ni tarjetas de región ni stats). Se auditaron las 4 por privacidad: Galicia tenía 1
fuga (VARE-00000414, número de portal expuesto) — corregida. Las otras 3 estaban limpias. Se
enlazaron las 4 en index.html. Nuevo total: **1.542 activos, 12 regiones activas**.
Lección: antes de dar por "vacía" una comunidad, comprobar si ya existe el archivo
`activos-<slug>.html` en la carpeta, porque puede haber quedado sin enlazar de un tramo anterior.

### La Rioja — PUBLICADA (90 activos)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = La Rioja → **371 activos** encontrados.
- Paginación sin bugs en las 6 páginas recorridas (90 activos brutos, 90 únicos tras dedupe por REF).
- Se extrajeron 6 páginas (de 25 totales) porque a partir de la página 3 el catálogo se llena de
  portfolios de parcelas ("Suelos Urbanos Residenciales") muy repetitivos en Calahorra/Alberite/
  Villamediana de Iregua — se priorizó diversidad geográfica (21 municipios) sobre volumen bruto.
- 0 fugas de privacidad verificadas programáticamente.
- Filtro de página por Municipio (no hay varias provincias, La Rioja es uniprovincial).
- Enlazada en activos.html (ya tenía la entrada `la-rioja` preconfigurada) y en index.html
  (hero-dropdown + tarjeta de región + stats: 1080 activos totales, 8 regiones activas).
- Pendiente si se quiere ampliar: quedan ~19 páginas más (mayormente parcelas repetidas de Calahorra).

## TRAMO 3 (8 julio 2026): País Vasco publicado

### País Vasco — PUBLICADA (120 activos)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = País Vasco → **234 activos** encontrados.
- El bug de paginación (pérdida del filtro, no contenido repetido esta vez) reapareció al saltar de la
  página 7 a la 8: el filtro se resetéo solo y la página 8 devolvió resultados de TODA España sin
  filtrar (55.452 activos). **Solución que funcionó**: volver a `/Estates/ListCommercial`, reaplicar
  los dos filtros (Comunidad autónoma + Estado) y navegar de nuevo a la página 8 — el filtro se
  recuperó correctamente y se pudo seguir extrayendo. Anotar este método para futuras ampliaciones:
  si el filtro se pierde a mitad de la paginación, no hace falta reiniciar sesión, basta con
  reaplicar el formulario de búsqueda desde cero antes de continuar en la página donde se cortó.
- Se extrajeron 8 páginas (120 activos únicos) antes de parar deliberadamente: a partir de la página 6
  aproximadamente el listado se llena de un mismo edificio en Vitoria-Gasteiz (Calle Hondarribia Nº 3,
  un portfolio de "36 Pisos + 5 Locales + 33 Garajes") repetido decenas de veces con distintas REF pero
  la misma dirección — se decidió no seguir extrayendo más páginas de puro relleno duplicado y cerrar
  el tramo en 120 activos con buena diversidad (Bilbao, Vitoria-Gasteiz, Donostia-San Sebastián,
  Barakaldo, Erandio, Basauri, Getxo, Leioa, Irun, etc.).
- Publicado `activos-pais-vasco.html` (patrón CV_DATA estándar, filtro por Provincia: Vizcaya,
  Guipúzcoa, Álava). Direcciones limpiadas, verificado 0 fugas de privacidad.
- El mapa de `activos.html` ya tenía preconfigurado el enlace `pais-vasco → activos-pais-vasco.html`.
  Se añadió la tarjeta y la opción del buscador rápido en `index.html`, y se actualizaron las cifras
  totales (990 activos, 7 regiones activas).
- Pendiente: ampliar más allá de 120/234 si se quiere completar el resto (quedan ~114 activos, en su
  mayoría parte del mismo portfolio duplicado de Vitoria-Gasteiz).

## TRAMO 2 (8 julio 2026): Canarias publicada + correcciones de enlaces rotos

## TRAMO 2 (8 julio 2026, continuación): Canarias publicada + correcciones de enlaces rotos

### Canarias — PUBLICADA (223 activos)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = Canarias → **1.338 activos** encontrados.
- **IMPORTANTE — el bug de paginación NO se reprodujo esta vez**: se navegó por URL directa
  `/Estates/ListCommercial/page_N_15` desde la página 1 hasta la 15 (225 activos en bruto, 223 únicos
  tras deduplicar) sin ningún caso de contenido repetido/atascado. Cada página devolvió REFs nuevas y
  correctas. No está claro si el bug de Murcia/Madrid era temporal (rate-limiting que ya se disipó) o
  si depende de la comunidad/carga del servidor en ese momento — **vale la pena reintentar la ampliación
  de Murcia (páginas 6-45) y Madrid (más allá de página 1) con este mismo método de navegación directa
  por URL antes de asumir que el bug sigue activo.**
- Se publicó `activos-canarias.html` (patrón CV_DATA estándar, sin fotos Street View, filtro por
  Provincia ya que Canarias solo tiene 2: Las Palmas y Santa Cruz de Tenerife). Direcciones limpiadas
  (sin Nº/Esc/Pl/Pt), sin badge de planta.
- Municipios reconocidos vía lista manual (~40 municipios canarios, incluyendo formas con artículo
  como "Palmas de Gran Canaria (Las)", "Rosario (El)", "Realejos (Los)", etc.) — si se amplía la
  extracción y aparecen municipios no listados, el parser los dejará sin `municipio` (revisar
  `/tmp/parse_canarias.py` si se recupera la sesión de bash).
- Pendiente: ampliar más allá de los 223/1.338 (faltan ~1.115 activos, páginas 16 en adelante).
- El mapa de `activos.html` ya tenía preconfigurado el enlace `canarias → activos-canarias.html`
  (estaba esperando este archivo). Se añadió también la tarjeta de Canarias y la opción en el buscador
  rápido de `index.html`.

### Corrección: enlaces rotos en la portada (`index.html`)
- El usuario reportó que al hacer clic en "Comunitat Valenciana" volvía a la página de inicio. Causa:
  `index.html` tiene su PROPIO buscador rápido y su propia sección "Regiones donde operamos"
  (independientes del mapa de `activos.html`, que ya se había corregido en el tramo anterior) — estos
  seguían apuntando al archivo antiguo `ocupados/comunitat-valenciana.html` (no existe → recarga la home).
- Corregido en 2 sitios de `index.html`: el `<select id="hero-region">` del buscador rápido y la tarjeta
  de "Regiones donde operamos". Ambos ahora apuntan a `activos-comunitat-valenciana.html`.
- De paso se actualizaron cifras desactualizadas en `index.html`: Murcia ya no dice "próximamente"
  (225 activos), se añadieron las tarjetas de Madrid (15) y Canarias (223), y el total pasó de 552 a
  870 activos en 6 regiones activas.
- **Lección para el futuro**: cualquier comunidad nueva debe enlazarse en DOS sitios, no solo uno:
  1) el mapa interactivo de `activos.html` (objeto JS de regiones), y
  2) el buscador rápido + sección "Regiones donde operamos" de `index.html` (home).

### Corrección: violación de privacidad encontrada en Madrid ya publicado
- Al verificar el sitio en vivo con Claude in Chrome (JS real), `activos-madrid.html` mostraba una
  versión ANTIGUA/distinta a la documentada en el tramo 1: 17 activos en HTML estático (no CV_DATA),
  sin nombre de calle visible y con el badge "🏢 Planta Es:1 Pl:00 Pt:B" (escalera/planta/puerta
  exactos) — violación directa de la regla de privacidad.
- Se reconstruyó `activos-madrid.html` desde los datos ya limpiados guardados en la sesión de bash
  (`/tmp/madrid_cv_data.json`, 15 activos reales, sin Nº/Esc/Pl/Pt), con el patrón CV_DATA estándar.
  Verificado programáticamente: 0 coincidencias de patrones de dirección exacta en el archivo final.
- **Causa probable**: desincronización entre lo que se construyó en una sesión anterior y lo que
  finalmente se escribió/desplegó — no se pudo determinar la causa exacta. Recomendación: tras
  reconstruir cualquier página, verificar SIEMPRE con Claude in Chrome (JS real) sobre el sitio en
  vivo, no solo confiar en que el archivo local es correcto.

### Corrección: segunda violación de privacidad encontrada en Comunitat Valenciana ya publicada
- Auditoría final de todas las páginas (script Python buscando Nº/Esc:/Pl:/Pt:/coma-número en el
  CV_DATA de cada archivo) encontró 6 registros en `activos-comunitat-valenciana.html` con dirección
  exacta completa filtrada desde el tramo anterior (no se había detectado porque el chequeo de esa
  sesión no cubría el patrón "Esc:1 Pl:0 Pt:26" pegado sin espacios al nombre de la calle):
  ALRE-05125, ALRE-03772, ALRE-07144, EXRE-01295 (con Esc:/Pl:/Pt: + número de parcela + municipio
  pegado al final), ALRE-05209 (número de calle suelto sin "Nº"), DIRE-002633 (número de parcela).
  Todos corregidos, verificado 0 fugas restantes en las 5 páginas del sitio (Murcia, Madrid, Comunitat
  Valenciana, Canarias, Sevilla).
- **Lección para el futuro**: el chequeo de fugas de privacidad debe buscar el patrón `Esc:`/`Pl:`/`Pt:`
  en CUALQUIER posición de la cadena `calle` (no solo al principio), y también números sueltos al
  final sin prefijo "Nº". Usar como referencia el regex:
  `r'\bN[ºo°]\.?\s*\d|Esc\s*:|Pl\s*:|Pt\s*:|,\s*\d'` sobre el campo `calle` de cada registro del
  `CV_DATA`, para todas las páginas, antes de dar por cerrada cualquier publicación.
- Nota de calidad de datos (no es problema de privacidad): en `activos-comunitat-valenciana.html` el
  campo `municipio` está vacío en los 81 registros (el nombre del municipio quedó a veces embebido al
  final de `calle`, ej. "Calle Luna Pilar de la Horadada"). No afecta a privacidad ni a lo mostrado
  (la tarjeta solo muestra provincia), pero limita el filtro de búsqueda por municipio. Pendiente de
  mejorar si se retoma esta página.

### Deploy
- Se creó `deploy.bat` en la carpeta del proyecto (doble clic → ejecuta `wrangler pages deploy .
  --project-name=dulas-properties`) para que el usuario no tenga que escribir el comando en PowerShell
  cada vez.

## Objetivo
Publicar en dulasproperties.com la cartera de activos "Suspendido" de Hipoges, comunidad a comunidad,
siguiendo el patrón ya en producción de `activos-sevilla.html` (Andalucía, 306 activos reales).

## Patrón de página ya validado (usar siempre este, NO páginas individuales por activo)
- Un único HTML por comunidad (ej. `activos-murcia.html`).
- Array JS `CV_DATA` con objetos: `{ref, tipo, calle, municipio, provincia, price, m2, hab, planta, panoid}`.
- Tarjetas renderizadas por JS con filtros (tipo, búsqueda, etc.), igual que en `activos-sevilla.html`.
- Imagen de cada tarjeta = Street View real vía:
  `https://streetviewpixels-pa.googleapis.com/v1/thumbnail?cb_client=maps_sv.tactile&w=600&h=400&pitch=0&panoid=${panoid}&yaw=0`
  (no requiere API key). Si no hay panoid, se muestra placeholder "Imagen de calle no disponible".
- Ver función `svUrl()` y el bloque `<script>` en `activos-sevilla.html` como plantilla exacta a copiar.
- Pendiente para cuando se generen los CV_DATA reales: conseguir el `panoid` de Google Street View para
  cada calle+municipio (no hay script guardado de cómo se hizo para Sevilla; hay que resolverlo de nuevo,
  posiblemente vía geocoding + Street View metadata, o repitiendo el método usado en su momento).

## Comunidades ya completadas (en producción)
- **Andalucía** → `activos-sevilla.html` (306 activos, CV_DATA completo).
- **Illes Balears** → `activos-baleares.html` + páginas individuales antiguas (alcudia.html, asima.html, etc.) — patrón antiguo, no replicar.

## Comunidad de Madrid — publicada parcialmente (8 julio 2026)
- Filtros: Estado inmueble = Suspendido + Comunidad autónoma = Comunidad de Madrid → **2.471 activos**.
- El bug de paginación se reprodujo de inmediato (clic a página 2 no avanza, igual que en Murcia) —
  no es un problema de la sesión de Murcia, es del sitio en general.
- Se publicó `activos-madrid.html` con los **15 activos de la página 1** únicamente. Direcciones
  limpiadas (sin Nº/Esc/Pl/Pt, sin badge de planta), mismo patrón que Murcia y Sevilla.
- Lista de municipios de Madrid usada en el parser: no es la lista completa de los 179 municipios
  de la comunidad, solo ~90 de los más conocidos (los 7 que aparecen en estos 15 activos están
  cubiertos). Si se amplía la extracción, revisar que el municipio se detecte bien para pueblos
  pequeños no incluidos en la lista.
- Pendiente: ampliar más allá de la página 1 cuando se resuelva o se sortee el bug de paginación
  (ver sección de paginación de Murcia — aplica igual aquí).

## Comunidades ya completadas (en producción) — actualización
- **Región de Murcia** → `activos-murcia.html` **PUBLICADO** (8 julio 2026) con **225 activos reales**
  (de un total de 2.024 en Hipoges con filtro Suspendido). CV_DATA generado a partir de
  `murcia_raw_p01.txt` a `murcia_raw_p05.txt` con un parser Python (municipio/calle separados por
  lista de los 45 municipios de la Región de Murcia). Sin fotos Street View todavía (placeholder
  "Imagen de calle no disponible" en todas las tarjetas — pendiente conseguir panoids, ver sección
  de imágenes más abajo). Filtro por "Municipio" en vez de "Provincia" (Murcia es uniprovincial).

## Comunidades en curso
### Región de Murcia — ampliación pendiente (1.799 activos restantes)
- Filtros en HipogesWorks confirmados: **Estado inmueble = Suspendido** + **Comunidad autónoma = Murcia**
  → **2.024 activos** en 45 páginas de 45 resultados.
- Progreso de extracción: **5 de 45 páginas guardadas = 225 activos** (~11%), ya publicados en
  `activos-murcia.html`. Faltan las páginas 6-45 (1.799 activos) para completar la cartera.
- Archivos guardados en esta carpeta: `murcia_raw_p01.txt` a `murcia_raw_p05.txt`
  (texto ya limpiado: título/dirección, m²/hab/planta, precio (+ % descuento si "Rebajado"), REF, estado, si falta foto).
- **BUG CONFIRMADO DE NUEVO (8 julio 2026):** el listado de HipogesWorks quedó "enganchado" en el
  contenido de la página 5 — ni clics automáticos, ni navegación directa a `/page_6_45`, ni cerrar y
  reabrir sesión lo desbloquean. El usuario probó clic manual en otra pestaña/ventana y esa sí avanzó,
  confirmando que el problema es específico de automatización (ver sección de paginación más abajo).
  Pendiente: retomar con el usuario haciendo los clics él mismo en la pestaña que Claude controla, o
  preguntar a Hipoges por una exportación masiva.

## AVISO DE PRIVACIDAD RESUELTO (8 julio 2026)
El usuario avisó de urgencia: **no se puede publicar la dirección exacta (número, escalera, piso,
puerta), solo el nombre de la calle.** Se corrigió:
- `activos-murcia.html`: los 225 registros se limpiaron para quitar "Nº X", "Esc:/Pl:/Pt:" y
  duplicados de municipio de la propia dirección. Se quitó también el badge "🏢 Planta X" de las
  tarjetas.
- `activos-sevilla.html` (ya publicada): se encontró y corrigió 1 registro con dirección exacta
  completa (ACRE-000668, "Avenida Alcalde Cantos Ropero, 51, Esc 1, Piso 0 pta 40" → solo
  "Avenida Alcalde Cantos Ropero") y 1 con número de parcela de urbanización. Se quitó también el
  badge de planta de las tarjetas de Sevilla.
- `activos-baleares.html`: revisada, ya estaba limpia (sin números de calle ni planta).
- Páginas antiguas individuales de Baleares (alcudia.html, asima.html, etc.): revisión rápida sin
  encontrar direcciones exactas, pero no se auditaron a fondo (formato distinto, no generado por
  CV_DATA).
- **Pendiente de revisar con el mismo criterio cuando se generen**: cualquier comunidad futura
  (Madrid, etc.) debe pasar por esta misma limpieza de "Nº/Esc/Pl/Pt" antes de publicarse.
- Riesgo residual: los archivos `murcia_raw_p01.txt` a `p05.txt` en esta misma carpeta SÍ contienen
  las direcciones exactas completas (son datos de trabajo, no la web publicada). Si esta carpeta se
  sube tal cual a un hosting público, esos .txt quedarían accesibles por URL directa aunque no estén
  enlazados. Recomendación: no subir los `*_raw_*.txt` al servidor de producción, o moverlos fuera
  de la carpeta que se despliega.

## Pendiente: fotos de Street View para Murcia
- Los 225 activos ya publicados no tienen `panoid` (se muestra el placeholder "Imagen de calle no
  disponible" en toda la página). Para Sevilla (306 activos) sí existen panoids reales de Google
  Street View en el CV_DATA, pero no hay guardado ningún script de cómo se consiguieron.
- Intentado en esta sesión: geocodificar direcciones vía Nominatim (OpenStreetMap, gratis) desde el
  sandbox de Claude — **bloqueado**, el sandbox no tiene salida de red a nominatim.openstreetmap.org
  ni a maps.googleapis.com. Habría que resolverlo vía el navegador (Claude in Chrome) dirección por
  dirección, que es lento para 225+ activos, o encontrar el método/script que se usó para Sevilla.

### Comunitat Valenciana — RESUELTO Y PUBLICADO (8 julio 2026)
- El archivo desplegado `activos-valencia-NUEVO.html` (visible en producción en
  https://main.dulas-properties.pages.dev/activos-valencia-NUEVO) SÍ tenía datos reales (111 activos), a
  diferencia de lo que se pensaba antes ("0 refs encontradas" era un diagnóstico erróneo de una sesión previa,
  probablemente porque el archivo local en el mount de bash estaba obsoleto/desincronizado — ver aviso técnico
  más abajo).
- Problema real encontrado: de esos 111 activos, **29 eran de otras comunidades** mezclados por error
  (Illes Balears, Madrid, Málaga, Barcelona, Huelva, Tarragona, Región de Murcia, Jaén) — probablemente por
  concatenar por accidente datos de otras sesiones/comunidades al construir el archivo.
- Se filtró a los **82 activos reales** de las 3 provincias de la Comunitat Valenciana (Alicante/Alacant,
  Valencia/València, Castellón/Castelló), se limpiaron las direcciones (Nº/Esc/Pl/Pt) y se publicó como
  `activos-comunitat-valenciana.html` (nuevo archivo, patrón CV_DATA + filtros, sin fotos por ahora).
- Se corrigió el mapa de `activos.html`: la comunidad "Comunitat Valenciana" apuntaba a
  `ocupados/comunitat-valenciana.html` (una categoría distinta, "ocupados", no la cartera de venta) — ahora
  apunta a `activos-comunitat-valenciana.html`.
- Los archivos antiguos `activos-valencia-NUEVO.html` y `valencia.html` se quedan huérfanos (ya no enlazados
  desde el mapa) pero siguen en la carpeta — no se pueden borrar sin permiso explícito del usuario.

## AVISO TÉCNICO: el mount de bash puede quedarse desincronizado con archivos preexistentes
- Durante esta sesión, `wc -l`/`grep` vía `mcp__workspace__bash` mostraban `activos-valencia-NUEVO.html` como
  un archivo pequeño y vacío (125 líneas, 0 activos reales) mientras que las herramientas `Read`/`Edit`/`Grep`
  (que operan directo sobre el host) mostraban correctamente el archivo real de 2.419 líneas y 111 activos.
- Conclusión: para archivos que ya existían ANTES de que arrancara la sesión de bash, no fiarse de `bash` para
  leer contenido — usar `Read` o `Grep` (las herramientas de archivo), que reflejan el estado real y actual.
  `bash` sigue siendo fiable para archivos creados o modificados dentro de la propia sesión de bash.

## Cómo acceder a HipogesWorks
- URL: https://www.hipogesworks.com/Estates/ListCommercial
- Sesión: usuario "Dulas Property - Baleares", login manual del usuario (Claude no introduce contraseñas).
- Menú: Inmuebles → Solicitar asignación → panel de búsqueda izquierdo.
- Filtros usados: "Estado inmueble" (checkbox "Suspendido") + "Comunidad autónoma" (autocompletar, escribir
  el nombre y seleccionar la sugerencia).
- El selector de resultados por página tiene máximo 45 (dropdown junto a la paginación); no hay opción de
  100+ ni de exportar a Excel/CSV.

## PROBLEMA CRÍTICO: paginación no fiable con automatización
- Los enlaces de paginación son `<a href="/Estates/ListCommercial/page_N_45">` reales (no JS puro), pero:
  - Navegar directamente por URL a `page_2_45` o `page_3_45` a veces devuelve el contenido de la página 1
    (bug o caché del lado servidor, no es problema de caché de navegador — probado con `?nocache=1`).
  - Hacer clic en los números de página o en "Siguiente" a veces NO dispara ninguna petición al servidor
    (confirmado revisando el log de red: la petición GET simplemente no se produce).
  - Patrón observado: tras una racha de éxitos, empiezan a fallar muchos intentos seguidos (se detectaron
    6 fallos consecutivos justo después de una racha de 2 éxitos) — **parece protección anti-bot/rate-limiting**
    de HipogesWorks, no aleatoriedad pura.
- **Decisión tomada:** parar la extracción automática para no arriesgar que la cuenta de Dulas Property quede
  marcada o bloqueada por Hipoges. Dejar reposar la cuenta antes de retomar.
- **Método que SÍ funciona cuando el sitio responde:** hacer clic (no navegar por URL) en el enlace numerado
  de la página deseada usando el DOM real (`find` + `click` sobre el elemento), luego verificar con una
  comprobación JS barata (primeras 3 REF de la página) antes de gastar una llamada completa de extracción:
  ```js
  Array.from(document.body.innerText.matchAll(/REF:\s*([A-Z0-9-]+)/g)).map(m=>m[1]).slice(0,3).join(',');
  ```
  Si las REF coinciden con una página ya guardada, reintentar el clic; si son nuevas, extraer con
  `get_page_text` completo (sin truncar, a diferencia de `javascript_tool` que trunca ~1500 caracteres).

## Opciones para retomar (recomendación por orden)
1. **Preguntar a Hipoges/el gestor de cuenta** si existe una exportación masiva (Excel/CSV/API) del catálogo
   filtrado — evitaría todo el problema de paginación. No hay botón visible en la UI, pero puede existir vía
   soporte o un endpoint no documentado.
2. **Navegación manual asistida**: el usuario hace clic real en "Siguiente" (sin el problema anti-bot al ser
   un clic humano) y Claude captura el texto de cada página en cuanto se lo indique.
3. **Reintentos automáticos espaciados**: retomar los clics automáticos pero con pausas largas entre páginas
   (varios minutos) en vez de ráfagas, para no disparar el rate-limiting.

## Archivos de datos crudos guardados (Murcia)
- `murcia_raw_p01.txt` — 45 activos (PERE-000780 ... DIRE-000987)
- `murcia_raw_p02.txt` — 45 activos (BORE-0091 ... PERE-000779)
- `murcia_raw_p03.txt` — 45 activos (DIRE-000637 ... PERE-000243)
- `murcia_raw_p04.txt` — 45 activos (PERE-000256 ... PERE-002602)
- `murcia_raw_p05.txt` — 45 activos (BRRE-00106 ... RETI-04531)

Cada archivo tiene el formato: título con dirección, especificaciones (m²/hab/planta/escalera/puerta),
precio de venta (con % y precio original si estaba "Rebajado"), REF, estado (Suspendido + Okupado/Problemas
de registro/WIP si aplica), y aviso de "[Foto no disponible]" cuando corresponde. Este formato es la base
para construir el array `CV_DATA` de `activos-murcia.html`, pero todavía falta:
1. Completar las 40 páginas restantes (faltan 1.799 activos).
2. Conseguir el `panoid` de Street View por dirección para cada activo.
3. Generar el HTML final siguiendo el patrón de `activos-sevilla.html`.

## Añadidas referencias HipogesWorks a las fichas individuales de Baleares (11 julio 2026)
- Se añadió una fila "Referencia" a la ficha (prop-info-card) de 13 de las 21 páginas individuales de
  Baleares, buscando cada dirección en HipogesWorks (sección "Asignados", `/Estates/ListAssigned`, 52
  activos asignados a Dulas):
  - alcudia.html → JARE-0099
  - joanrosello.html → MORE-2879
  - calaratjada.html → JARE-1469
  - sonoliva.html → JARE-1913
  - joanmiro.html → VARE-00000884
  - calvia.html → ACRE-005339
  - conforama.html → EXRE-00423
  - menorca.html → GIRE-399101
  - solarsantamaria.html → SBRE-0176689
  - santamaria.html → SBRE-0186923
  - manacor.html → CIRE-00458
  - calabosch.html → CIRE-01182
  - inca.html → ACRE-000654 (coincide en m², tipo y estado "ocupada"; el nombre de zona varía ligeramente
    entre la web "Son Amonda" y Hipoges "Son Estaras" — mismo Inca, alta confianza pero no 100% verificado)
- **rafal.html** (Calle Baladre 29, Palma): Jaime confirmó que aplican las 2 referencias candidatas → se
  escribió "PERE-003257 / PERE-005234" en la fila Referencia.
- **Pendientes de confirmar con Jaime** (ambigüedad entre varias unidades del mismo edificio, o sin datos
  suficientes para diferenciar):
  - garaje.html (Camino Reis, Palma): ¿SBRE-0172527 o SBRE-0172590?
  - manacorlocal.html (Marqués de la Sínia, Manacor): posible RETI-02008 (113 m² vs 105 m² de la web,
    nombre de calle no coincide exactamente — "Sinia Dels Frares" en Hipoges) o GIRE-395102 (candidato
    alternativo detectado en la lista de 23 refs "en negociación" que pasó Jaime, correspondiente a un
    "Local + Garaje en Calle Econom P. Gelabert", Manacor) — sin resolver.
- **No encontradas en HipogesWorks** (ni en Asignados ni en Vendidos): asima.html, sanvicente.html,
  llucmajor.html. Podrían ser activos ya vendidos hace tiempo, o de origen distinto a Hipoges. Pista sin
  confirmar: el array `soldRefs` de las páginas de región contiene el valor centinela `"asima"` (no es un
  formato de referencia Hipoges real), lo que sugiere que `asima.html` podría estar ya marcado como vendido
  mediante este mecanismo — no verificado.
- **bisbellompart.html**: confirmado por Jaime que es un inmueble de propietario particular, no de
  Hipoges — no lleva referencia.

## Franja amarilla "OFERTA EN NEGOCIACIÓN" en fichas individuales (11 julio 2026)
- Jaime pasó una lista de 23 referencias de activos actualmente "en negociación" (Valencia, Baleares,
  Marbella) y pidió una franja grande amarilla con el texto "OFERTA EN NEGOCIACIÓN". Al revisar el código
  se confirmó que esa lista de 23 refs es EXACTAMENTE el array `offerRefs` que ya existía (desde antes de
  esta sesión) en las 11 páginas de región (`activos-sevilla.html`, etc.), junto con la clase CSS
  `.badge-offer-banner` (franja amarilla ancho completo, ya implementada ahí) — es decir, en las páginas de
  región (tarjetas CV_DATA) el aviso ya se muestra correctamente.
- Las 21 fichas individuales de Baleares (fuera del patrón CV_DATA) NO comprobaban `offerRefs` en absoluto;
  algunas (alcudia.html, calabosch.html) solo tenían un badge pequeño flotante (`.badge-offer`, esquina fija),
  no una franja grande.
- Se añadió una nueva clase `.offer-banner` (franja amarilla, ancho completo, en el flujo normal justo
  después de `<body>`) y se aplicó a las fichas cuya referencia confirmada está en `offerRefs`:
  - alcudia.html (JARE-0099) — se sustituyó el badge pequeño flotante por la franja grande.
  - calabosch.html (CIRE-01182) — ídem.
  - joanrosello.html (MORE-2879), manacor.html (CIRE-00458), inca.html (ACRE-000654) — no tenían ningún
    aviso antes; se añadió la franja nueva.
- No se tocó rafal.html (sus refs PERE-003257/PERE-005234 no están en `offerRefs`) ni manacorlocal.html
  (referencia aún sin resolver, ver arriba).
- Pendiente de decidir con Jaime: si `soldRefs`/`offerRefs` deberían compartirse en un solo sitio (hoy están
  duplicados de forma idéntica en las 11 páginas de región) y si `manacorlocal.html` debe llevar la franja
  una vez se resuelva su referencia real.
- **Pendiente de deploy**: ninguno de estos cambios (ni los 14 de referencias, ni la franja amarilla) se ha
  subido aún a producción — falta ejecutar `deploy.bat`.

## Google Analytics 4 instalado en todo el sitio (11 julio 2026) — RESUELTO
- Propiedad GA4 creada desde cero (no existía, contrariamente a lo que se creía): "Dulas Properties",
  zona horaria España, moneda EUR, sector Inmobiliario. Measurement ID: `G-NBB3L9N4PW`.
- Snippet gtag.js insertado justo después de `<head>` en las 46 páginas reales del sitio (todas las
  `activos-*.html`, páginas legales, páginas de vivienda individuales de Baleares, `ocupados/comunitat-valenciana.html`, etc.). Verificado en producción: `dataLayer` activo y `gtag` definida en `dulasproperties.com`.
- No se ha añadido banner de consentimiento de cookies (solo la página informativa `cookies.html`). Si se
  quiere cumplir estrictamente con la guía de la AEPD sobre cookies no esenciales, lo recomendable sería
  añadir un banner que bloquee la carga de Analytics hasta que el usuario acepte. Queda pendiente si se
  decide abordarlo.

## Mejoras en `vender.html` para atraer vendedores (11 julio 2026) — RESUELTO
- Añadida barra de estadísticas (reutilizando `.stats-bar`/`.stat-item` ya definidos en `styles.css`) con
  datos reales ya usados en el resto del sitio: 500+ activos gestionados, honorarios solo a éxito, 24h de
  respuesta, partner homologado Hipoges.
- Nueva sección "Situaciones que sabemos resolver" (4 tarjetas): vivienda ocupada, hipoteca/cargas
  pendientes, herencia/proindiviso, cesión de remate — mensaje alineado con el posicionamiento real de la
  empresa (ya presente en `nosotros.html`/`servicios.html`), no inventado.
- Formulario de valoración (`#valoracion`): añadidos selects "Motivo de venta" y "¿Para cuándo?", y checkbox
  RGPD obligatorio con enlace a `privacidad.html` (antes no existía ningún consentimiento en el formulario).
  Sigue enviando a Formspree (`https://formspree.io/f/xjglnppd`), ahora con 2 campos adicionales.
- Nueva sección "¿Por qué confiar en nosotros?" con credenciales reales (Partner Hipoges, experiencia en
  activos complejos, honorarios a éxito) en vez de testimonios de clientes inventados — se decidió no
  fabricar citas/testimonios falsos atribuidos a clientes reales.
- Nueva sección FAQ (5 preguntas) sobre vender vivienda ocupada, con deuda, en herencia, plazos y
  honorarios, con disclaimer de que no sustituye asesoramiento legal/fiscal.
- Creado `cookies.html` (no existía; el footer de varias páginas —`vender.html`, `servicios.html`,
  `nosotros.html`, `privacidad.html`— ya enlazaba a él) modelado sobre `privacidad.html`: mismo responsable
  (Dulas Servicios Integrales, S.L., CIF B42783282), cookies técnicas (Cloudflare) y analíticas (Google
  Analytics). Esto arregla el enlace roto en las 4 páginas a la vez.

## BUG CRÍTICO encontrado y corregido: `index.html` truncado en producción (11 julio 2026) — RESUELTO
- Al preparar el banner de cookies se detectó que `index.html` en producción (y por tanto ya publicado en
  `dulasproperties.com`) terminaba de forma abrupta a mitad del footer: el segundo icono social (`aria-lab`)
  quedaba cortado en seco y pegado directamente al script de Cloudflare Turnstile, sin `</body>` ni `</html>`.
  Faltaban por completo: el icono de LinkedIn, el de Facebook, el bloque `footer-links` (Aviso legal,
  Privacidad, Cookies, email), el enlace flotante de WhatsApp y el cierre de etiquetas.
- Origen: no ocurrió en esta sesión (se comprobó que el archivo ya tenía exactamente este mismo contenido
  truncado, mismo tamaño, antes de instalar Analytics) — es anterior, de una sesión previa. Los navegadores
  no mostraban error visible porque el parser HTML autocompleta las etiquetas que faltan, pero el script de
  verificación de Cloudflare (Turnstile) quedaba roto (código JS inválido) al servirse así.
- Se reconstruyó el tramo que faltaba usando el mismo bloque de iconos sociales/footer que ya existe en
  `servicios.html` (idéntico HTML/CSS) y se verificó carácter a carácter antes de subirlo.
- Se aprovechó para revisar los 63 HTML del sitio: solo `activos-baleares.html` tenía otra anomalía menor ya
  documentada (falta `</html>` al final, pero sí tiene `</body>` — no afecta a la visualización) — se
  corrigió también de paso.
- **Acción requerida: hay que desplegar cuanto antes** porque el bug estaba en producción.

## Banner de consentimiento de cookies (Google Consent Mode) (11 julio 2026) — RESUELTO
- Sustituida la carga incondicional de gtag.js (en las 47 páginas: las 46 anteriores + `cookies.html`) por
  una versión con Google Consent Mode: por defecto `analytics_storage: denied`; solo se carga el script real
  de Analytics si `localStorage.dp_cookie_consent === 'accepted'`.
- Añadido un banner fijo al pie ("Aceptar" / "Rechazar") en las 47 páginas. Al aceptar, se actualiza el
  consentimiento y se inyecta gtag.js en ese momento; al rechazar, o si no se responde, Analytics no se
  carga. La elección se recuerda en `localStorage` (no hay enlace para cambiarla después; si se quiere,
  se puede añadir un pequeño enlace "gestionar cookies" en el footer más adelante).

## Recuperación de las 94 direcciones sin calle (11 julio 2026) — RESUELTO

Tras el mantenimiento inicial, el usuario pidió corregir todos los errores detectados salvo las imágenes
de Baleares (autorizadas explícitamente, hechas por el propio usuario, partner de la empresa — no tocar).
Se resolvió primero el problema de mapas Yandex con ubicación exacta (213 activos en 5 comunidades).
Quedaban pendientes 94 activos publicados sin nombre de calle (solo mostraban municipio en el mapa).

El usuario se logueó manualmente en HipogesWorks (`https://www.hipogesworks.com/Estates/ListCommercial`)
y Claude buscó cada una de las 94 REF una por una (búsqueda por "Referencia inmueble"), extrayendo el
título original y limpiándolo según la norma de privacidad del proyecto (sin número de portal, planta,
escalera, puerta, código postal, ni referencia catastral — solo calle + municipio + provincia).

Resultado: 85 de las 94 tenían una calle real recuperable y se escribió en el campo `"calle"` del array
`CV_DATA` correspondiente (antes era `null`). 2 activos rurales (REAR-01155 en Domeño y RETI-05262 en
Mazarrón) solo tenían código de parcela sin nombre de calle real, así que se usó el término genérico
"Diseminados" (habitual en fincas rústicas, no revela ubicación exacta). Los 7 restantes (FRRE-20154,
AURE-20866, LIRE-01273, MORE-2293, RETI-02528, RETI-03704, PERE-004709) son suelo urbano/rústico o
locales cuyo único dato de origen es un código de parcela o procedimiento administrativo (p. ej. "Proc.
Simplificado", "Pl Número") — no existe una calle real que mostrar, así que se dejaron sin `calle` (el
mapa sigue mostrando municipio + provincia, igual que antes, pero ya no es un error de datos sino la
ausencia real de una dirección postal para esos activos).

Archivos modificados (todos con el patrón `CV_DATA`, siguiendo el flujo seguro de archivo temporal +
verificación con `Read` antes de sobrescribir):
- `activos-sevilla.html` (Andalucía) — 42 direcciones escritas, 1 sin calle real (FRRE-20154)
- `activos-comunitat-valenciana.html` — 16 escritas, 5 sin calle real
- `activos-murcia.html` — 19 escritas (18 reales + "Diseminados"), 1 sin calle real (PERE-004709)
- `activos-madrid.html` — 5 escritas
- `activos-canarias.html` — 2 escritas
- `activos-pais-vasco.html` — 1 escrita
- `activos-aragon.html` — 1 escrita
- `activos-cantabria.html` — 1 escrita

El listado completo de las 94 REF con su dirección recuperada (o vacío si no aplica) queda guardado en
`direcciones_recuperadas.csv` en la carpeta de trabajo de Claude, por si hace falta auditarlo de nuevo.

Pendiente: el usuario debe ejecutar `deploy.bat` para publicar estos cambios, y después queda por abordar
el segundo punto pendiente — el filtro "Tipo de activo" de la portada, que no filtra nada actualmente.

## Filtro "Tipo de activo" de la portada — RESUELTO (11 julio 2026)

El desplegable `#hero-tipo` de `index.html` tenía opciones de clasificación legal (REO, NPL, Cesión de
remate, Activo ocupado) que no correspondían a ningún campo real de los datos: no existe ningún campo de
"ocupado", y el filtro `#cv-tipo` que ya existe en cada página de región filtra por **tipo de inmueble**
(`item.tipo`: "Piso", "Casa Adosada", "Local comercial", etc.), no por estado legal. El usuario eligió
cambiar la portada para que ofrezca tipo de inmueble en vez de estado legal.

Cambios:
1. `index.html` — opciones de `#hero-tipo` cambiadas a: Piso, Casa, Chalet, Local, Garaje, Suelo, Finca
   Rústica. `heroSearch()` ahora añade `?tipo=<valor>` a la URL de destino (o a `activos.html` si no se
   elige región).
2. En los 11 archivos con patrón `CV_DATA` (sevilla=Andalucía, comunitat-valenciana, murcia, madrid,
   canarias, pais-vasco, aragon, la-rioja, asturias, cantabria, baleares):
   - Al cargar la página, si hay `?tipo=` en la URL, se añade como opción seleccionada en `#cv-tipo`.
   - El filtro de tipo pasó de comparación exacta (`===`) a comparación flexible
     (`.toLowerCase().includes(...)`), porque el campo `tipo` en los datos es inconsistente entre
     archivos (mayúsculas/minúsculas, combinaciones como "Casa Adosada", "36 Pisos + 5 Locales + 33
     Garajes", etc.). Esto también mejora el filtro manual que ya usaban los visitantes en cada página.
   - `activos-baleares.html` tiene una estructura de filtrado distinta (filtra el array `CV_DATA`
     directamente, no atributos `data-tipo` en el DOM) — se aplicó el mismo criterio adaptado a su código.

Nota: las 6 páginas con patrón HTML estático (Castilla-La Mancha, Castilla y León, Cataluña, Extremadura,
Galicia, Navarra) no tienen `CV_DATA` ni filtro de tipo — si un visitante elige una de esas regiones junto
con un tipo de activo, el parámetro `tipo` de la URL simplemente se ignora sin error (no hay forma de
aplicar el filtro ahí sin construir el patrón CV_DATA para esas páginas, que es un trabajo aparte).

También se detectó (no corregido, no relacionado con este cambio) que `activos-baleares.html` termina
de forma abrupta sin la etiqueta de cierre `</html>` — ya estaba así en el archivo original antes de esta
sesión. Los navegadores lo toleran sin problema, pero queda anotado por si se quiere revisar en el futuro.
