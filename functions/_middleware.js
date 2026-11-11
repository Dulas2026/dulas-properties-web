// Oculta de la web publica todos los activos de la peninsula (se mantienen Baleares y Canarias).
// Para volver a publicarlos basta con borrar este archivo.
const ISLAS = ['baleares'];
const esIsla = (r) => ISLAS.some((i) => r.startsWith(i));

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const p = url.pathname.toLowerCase();

  const listado = p.match(/^\/activos-([a-z-]+?)(-\d+)?(\.html)?\/?$/);
  if (listado && !esIsla(listado[1])) {
    return Response.redirect(url.origin + '/activos', 302);
  }

  if (/^\/activo-[a-z0-9-]+(\.html)?\/?$/.test(p)) {
    const res = await context.next();
    if (res.status !== 200) return res;
    const html = await res.clone().text();
    const m = html.match(/href="\/?activos-([a-z-]+)/);
    if (m && esIsla(m[1])) return res;
    return Response.redirect(url.origin + '/activos', 302);
  }

  return context.next();
}
