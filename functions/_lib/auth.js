// Utilidades de acceso para la Zona Colaboradores (Cloudflare Pages Functions).
// Los usuarios NO están en el código: se leen de la variable secreta COLABORADORES
// configurada en Cloudflare (Pages > dulas-properties > Settings > Variables and Secrets).
//   Formato: una línea (o separados por coma) por colaborador ->  usuario:contraseña
// La firma de la sesión usa la variable secreta SESSION_SECRET (texto largo aleatorio).

export const COOKIE = 'dp_colab';
const DURACION_SEG = 60 * 60 * 12; // la sesión dura 12 horas

const enc = new TextEncoder();

export function leerUsuarios(env) {
  const raw = (env.COLABORADORES || '').trim();
  const mapa = new Map();
  raw.split(/[\n,;]+/).forEach(function (linea) {
    const i = linea.indexOf(':');
    if (i < 1) return;
    const u = linea.slice(0, i).trim().toLowerCase();
    const p = linea.slice(i + 1).trim();
    if (u && p) mapa.set(u, p);
  });
  return mapa;
}

function b64url(buf) {
  let s = '';
  new Uint8Array(buf).forEach(function (b) { s += String.fromCharCode(b); });
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmac(secret, texto) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64url(await crypto.subtle.sign('HMAC', key, enc.encode(texto)));
}

// Comparación en tiempo constante (evita ataques de temporización)
export function iguales(a, b) {
  a = String(a); b = String(b);
  let dif = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    dif |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  }
  return dif === 0;
}

// La firma incluye la contraseña actual del usuario: si se le cambia o se le da de baja
// en COLABORADORES, su sesión deja de valer al instante.
export async function crearSesion(env, usuario, password) {
  const exp = Math.floor(Date.now() / 1000) + DURACION_SEG;
  const u = encodeURIComponent(usuario);
  const firma = await hmac(env.SESSION_SECRET, u + '|' + exp + '|' + password);
  return u + '.' + exp + '.' + firma;
}

export async function validarSesion(request, env) {
  if (!env.SESSION_SECRET) return null;
  const cookies = request.headers.get('Cookie') || '';
  const m = cookies.match(new RegExp('(?:^|;\\s*)' + COOKIE + '=([^;]+)'));
  if (!m) return null;
  const partes = m[1].split('.');
  if (partes.length !== 3) return null;
  const [u, exp, firma] = partes;
  if (Number(exp) < Date.now() / 1000) return null;
  const usuario = decodeURIComponent(u);
  const password = leerUsuarios(env).get(usuario);
  if (!password) return null;
  const esperada = await hmac(env.SESSION_SECRET, u + '|' + exp + '|' + password);
  return iguales(firma, esperada) ? usuario : null;
}

export function cookieSesion(valor) {
  return COOKIE + '=' + valor + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=' + DURACION_SEG;
}

export function cookieBorrar() {
  return COOKIE + '=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0';
}
