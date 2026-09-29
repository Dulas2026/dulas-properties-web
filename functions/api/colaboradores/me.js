// Devuelve el usuario conectado (lo usa la zona privada para mostrar el nombre).
import { validarSesion } from '../../_lib/auth.js';

export async function onRequestGet({ request, env }) {
  const usuario = await validarSesion(request, env);
  return new Response(JSON.stringify({ usuario: usuario }), {
    status: usuario ? 200 : 401,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
  });
}
