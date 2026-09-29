// Protege TODO lo que hay dentro de /colaboradores/ (página y listado de activos).
// Si no hay sesión válida, se redirige a la pantalla de acceso.
import { validarSesion } from '../_lib/auth.js';

export async function onRequest(context) {
  const { request, env, next } = context;
  const usuario = await validarSesion(request, env);
  if (!usuario) {
    const url = new URL(request.url);
    const destino = '/acceso-colaboradores?next=' + encodeURIComponent(url.pathname);
    return Response.redirect(url.origin + destino, 302);
  }
  const resp = await next();
  const r = new Response(resp.body, resp);
  r.headers.set('Cache-Control', 'private, no-store');
  r.headers.set('X-Robots-Tag', 'noindex, nofollow');
  return r;
}
