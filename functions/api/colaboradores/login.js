// Recibe el formulario de acceso (usuario + contraseña) y abre la sesión.
import { leerUsuarios, iguales, crearSesion, cookieSesion } from '../../_lib/auth.js';

function volverAlLogin(origin, error, next) {
  let url = origin + '/acceso-colaboradores?error=' + error;
  if (next) url += '&next=' + encodeURIComponent(next);
  return new Response(null, { status: 303, headers: { Location: url, 'Cache-Control': 'no-store' } });
}

export async function onRequestPost({ request, env }) {
  const origin = new URL(request.url).origin;
  const form = await request.formData();
  const usuario = String(form.get('usuario') || '').trim().toLowerCase();
  const password = String(form.get('password') || '');
  let next = String(form.get('next') || '');
  if (!/^\/colaboradores(\/|$)/.test(next)) next = '/colaboradores/';

  if (!env.SESSION_SECRET || !env.COLABORADORES) return volverAlLogin(origin, 'config', '');

  const guardada = leerUsuarios(env).get(usuario);
  if (!guardada || !iguales(password, guardada)) {
    await new Promise(function (r) { setTimeout(r, 800); }); // frena intentos repetidos
    return volverAlLogin(origin, 'credenciales', next);
  }

  const valor = await crearSesion(env, usuario, guardada);
  return new Response(null, {
    status: 303,
    headers: { Location: origin + next, 'Set-Cookie': cookieSesion(valor), 'Cache-Control': 'no-store' }
  });
}

export function onRequestGet({ request }) {
  return Response.redirect(new URL(request.url).origin + '/acceso-colaboradores', 302);
}
