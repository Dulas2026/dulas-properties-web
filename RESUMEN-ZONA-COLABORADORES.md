# Resumen para continuar: Zona Colaboradores de dulasproperties.com (29/09/2026)

## Dónde está todo
- **Carpeta de trabajo (la buena):** `C:\Users\PC\Desktop\EMPRESA\WEB DULAS ACTUAL` (copia de GitHub `Dulas2026/dulas-properties-web`).
- **NO usar** `WEB DEFINITIVO` ni su `deploy.bat`: está desactualizada desde agosto y publicaría una web antigua.
- **Hosting:** Cloudflare Pages, proyecto `dulas-properties` (no Netlify).
- **Publicar:** `powershell -ExecutionPolicy Bypass -File "C:\Users\PC\Desktop\EMPRESA\WEB DULAS ACTUAL\publicar-web.ps1"` (inicia sesión en Cloudflare si hace falta, publica, sube a GitHub y comprueba que la zona privada está protegida).

## Qué está hecho
- Botón **Colaboradores** en el menú de todas las páginas (inyectado desde `menu.js`, estilos `.colab-link` en `styles.css`).
- Acceso con usuario y contraseña gestionado en el servidor (Cloudflare Pages Functions):
  - `functions/colaboradores/_middleware.js` protege todo `/colaboradores/`.
  - `functions/api/colaboradores/login.js`, `logout.js`, `me.js`, lógica en `functions/_lib/auth.js`.
  - Pantalla de acceso: `acceso-colaboradores.html`. Sesión de 12 h.
  - Secretos en Cloudflare: `COLABORADORES` (lista `usuario:contraseña`) y `SESSION_SECRET`.
- **Comerciales dados de alta:** asier, peretomas, raulolamora, jaimevich, jaimesojo (usuarios en minúsculas).
  - Gestión: `WEB DEFINITIVO\gestionar-comerciales.ps1` (añadir, quitar o cambiar contraseña; guarda la lista cifrada en el PC, sube a Cloudflare, publica y prueba que cada uno entra).
- **Catálogo privado** `colaboradores/index.html`:
  - Pantalla de entrada con tarjetas por comunidad autónoma y buscador de comunidad, provincia o población.
  - Dentro de cada comunidad: pestañas por situación (NPL, CDR, Ocupado…), botones por tipo, provincia y tramo de precio, panel de búsqueda estilo HipogesWorks, orden, 15/30/45 por página, ficha con mapa, exportar a Excel (CSV).
  - REF destacada y copiable con un clic; dirección completa (portal, planta, puerta) solo en la zona privada.
  - Enlaces por comunidad: `/colaboradores/#illes-balears`, `#andalucia`…
- **Datos:** un archivo por comunidad en `colaboradores/datos/*.json` más `indice.json` (4.084 activos sacados de las fichas públicas). Nunca se suben a GitHub (el repositorio es público); se publican protegidos.
- **Herramientas** (`herramientas/`):
  - `generar_listado_colaboradores.py`: regenera `colaboradores/datos/` a partir de las fichas públicas y de lo importado de HipogesWorks (lo de HipogesWorks tiene prioridad; sin duplicados por REF).
  - `importar_hipogesworks.py "C:\ruta\HIPOGES SUSPENDIDOS"`: lee páginas guardadas con Ctrl+S del listado de HipogesWorks y guarda `colaboradores/_hipoges/<comunidad>.json`. Después hay que ejecutar `generar_listado_colaboradores.py` y publicar.
  - `municipios_ine.csv`: municipios del INE para separar calle y población.

## Pendiente
- **Subir todos los activos SUSPENDIDOS de HipogesWorks** (35.709 en total, cualquier tipo), comunidad por comunidad, empezando por **Illes Balears**.
  - Filtro en HipogesWorks: Inmuebles → Solicitar asignación → Estado inmueble = Suspendido + Comunidad autónoma; 45 por página.
  - En esta conversación, la extracción automática desde la sesión de Chrome fue **bloqueada por el sistema de seguridad** de la app. Vías disponibles: páginas guardadas por el usuario (Ctrl+S, "Página web, solo HTML", en `EMPRESA\HIPOGES SUSPENDIDOS\<Comunidad>\p01.html…`) o un Excel/API solicitado a Hipoges.
- Revisar el "Protocolo de Actuación de Brokers 2026" de HipogesWorks sobre compartir datos con colaboradores externos.
- Error menor en la web pública: 173 fichas `activo-alre-*` de la Comunitat Valenciana tienen "Illes Balears" en la ruta de navegación superior.
