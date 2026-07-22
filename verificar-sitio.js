// Verificacion automatica de dulasproperties.com tras un despliegue.
// Comprueba que TODAS las URLs del sitemap.xml devuelven 200 OK.
// No requiere instalar nada: usa solo modulos incluidos en Node.js.

const https = require('https');

const SITE = 'https://dulasproperties.com';
const CONCURRENCY = 15;      // peticiones simultaneas
const TIMEOUT_MS = 15000;    // por peticion
const RETRY_DELAY_MS = 5000; // espera antes de reintentar una URL fallida
const MAX_RETRIES = 1;

function fetchStatus(url, attempt = 0) {
  return new Promise((resolve) => {
    const req = https.get(url, { timeout: TIMEOUT_MS }, (res) => {
      // Descartamos el cuerpo, solo nos interesa el status
      res.resume();
      resolve({ url, status: res.statusCode });
    });
    req.on('timeout', () => {
      req.destroy();
      resolve({ url, status: 'TIMEOUT' });
    });
    req.on('error', (err) => {
      resolve({ url, status: 'ERROR:' + err.code });
    });
  }).then(async (result) => {
    if (result.status !== 200 && attempt < MAX_RETRIES) {
      await new Promise((r) => setTimeout(r, RETRY_DELAY_MS));
      return fetchStatus(url, attempt + 1);
    }
    return result;
  });
}

async function fetchText(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, { timeout: TIMEOUT_MS }, (res) => {
        if (res.statusCode !== 200) {
          reject(new Error('No se pudo descargar ' + url + ' (status ' + res.statusCode + ')'));
          return;
        }
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => resolve(data));
      })
      .on('error', reject);
  });
}

async function runBatches(items, worker, concurrency) {
  const results = [];
  let index = 0;
  async function next() {
    while (index < items.length) {
      const i = index++;
      results[i] = await worker(items[i]);
    }
  }
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, next);
  await Promise.all(workers);
  return results;
}

(async () => {
  console.log('');
  console.log('============================================');
  console.log('  Verificando dulasproperties.com...');
  console.log('============================================');
  console.log('');

  // Cloudflare tarda unos segundos en propagar el despliegue nuevo.
  console.log('Esperando 8 segundos a que se propague el despliegue...');
  await new Promise((r) => setTimeout(r, 8000));

  let xml;
  try {
    xml = await fetchText(SITE + '/sitemap.xml');
  } catch (err) {
    console.log('');
    console.log('!! No se pudo descargar sitemap.xml: ' + err.message);
    console.log('!! Esto por si solo ya es un problema grave -> revisa el despliegue.');
    process.exitCode = 1;
    return;
  }

  const urls = Array.from(xml.matchAll(/<loc>(.*?)<\/loc>/g)).map((m) => m[1]);

  if (urls.length === 0) {
    console.log('!! El sitemap.xml se descargo pero no contiene ninguna URL. Revisa el archivo.');
    process.exitCode = 1;
    return;
  }

  console.log('Comprobando ' + urls.length + ' paginas del sitemap...');
  console.log('');

  const results = await runBatches(urls, fetchStatus, CONCURRENCY);
  const failures = results.filter((r) => r.status !== 200);

  console.log('============================================');
  if (failures.length === 0) {
    console.log('  TODO CORRECTO: ' + urls.length + ' de ' + urls.length + ' paginas cargan bien (200 OK).');
  } else {
    console.log('  ATENCION: ' + failures.length + ' de ' + urls.length + ' paginas fallan.');
    console.log('');
    console.log('  Paginas con problemas:');
    failures.forEach((f) => console.log('   - ' + f.url + '  ->  ' + f.status));
    console.log('');
    console.log('  Esto normalmente significa que el despliegue subio el sitio de forma');
    console.log('  incompleta. Vuelve a ejecutar deploy.bat para intentarlo de nuevo.');
  }
  console.log('============================================');
  console.log('');

  process.exitCode = failures.length === 0 ? 0 : 1;
})();
