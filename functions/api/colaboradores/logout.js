// Cierra la sesión del colaborador.
import { cookieBorrar } from '../../_lib/auth.js';

export function onRequest({ request }) {
  const origin = new URL(request.url).origin;
  return new Response(null, {
    status: 303,
    headers: { Location: origin + '/acceso-colaboradores?salida=1', 'Set-Cookie': cookieBorrar(), 'Cache-Control': 'no-store' }
  });
}
