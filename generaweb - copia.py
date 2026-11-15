#pip install paramiko
import os
import html
import re
import json
import unicodedata

# Configuración de carpetas
PLATAFORMAS = ["windows", "android"]
HTML_OUTPUT = "index.html"
SITEMAP_OUTPUT = "map.xml"
BASE_URL = "https://jotasoft78-dev.github.io"  # sin barra final
GA_MEASUREMENT_ID = "G-RWH4FNTL6S"

# ---------------------------------------------------------------------------
# Configuración de subida del sitemap al VPS por SFTP (sobrescribe el archivo)
# RELLENA estas 4 líneas con tus datos reales de acceso SSH al VPS:
# ---------------------------------------------------------------------------
SFTP_HOST = "195.20.235.22"          # ej: "123.45.67.89" o "tiny-paste.com"
SFTP_PORT = 22                                   # el mismo puerto que usas para SSH, no lo toques
SFTP_USUARIO = "root"             # ej: "root"
SFTP_CONTRASENA = "Caceres100"       # tu contraseña SSH normal
SFTP_CLAVE_PRIVADA = None                        # no la necesitas, déjalo así
SFTP_RUTA_REMOTA = "/var/www/vhosts/tiny-paste.com/httpdocs/map.xml"  # ej: "/var/www/tiny-paste.com/map.xml"

# Definir iconos para las plataformas
ICONOS = {
    "windows": "🖥️",
    "android": "📱"
}

def subir_sitemap_por_sftp(ruta_local, host, puerto, usuario, contrasena=None,
                            clave_privada=None, ruta_remota=None):
    """Sube el sitemap al VPS por SFTP, sobrescribiendo el archivo que haya
    en 'ruta_remota'. Requiere la librería 'paramiko' (pip install paramiko).
    Si algo falla (credenciales, conexión, ruta remota inexistente...), avisa
    por consola pero NUNCA interrumpe la generación local de los archivos."""
    datos_sin_rellenar = {
        None, "", "PON_AQUI_TU_IP_O_DOMINIO", "PON_AQUI_TU_USUARIO",
        "PON_AQUI_TU_CONTRASENA", "PON_AQUI_LA_RUTA_REAL/map.xml"
    }
    if host in datos_sin_rellenar or usuario in datos_sin_rellenar \
            or contrasena in datos_sin_rellenar or ruta_remota in datos_sin_rellenar:
        print("⚠️  Faltan datos de conexión SFTP por rellenar (host/usuario/contraseña/ruta); se omite la subida del sitemap.")
        return False

    try:
        import paramiko
    except ImportError:
        print("⚠️  Falta la librería 'paramiko'. Instálala con: pip install paramiko")
        return False

    transport = None
    try:
        transport = paramiko.Transport((host, puerto))
        if clave_privada:
            clave = paramiko.RSAKey.from_private_key_file(clave_privada)
            transport.connect(username=usuario, pkey=clave)
        else:
            transport.connect(username=usuario, password=contrasena)

        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(ruta_local, ruta_remota)
        sftp.close()
        print(f"✅ {ruta_local} subido y sobrescrito en {host}:{ruta_remota}")
        return True

    except Exception as e:
        print(f"⚠️  Error al subir el sitemap por SFTP a {host}: {e}")
        return False

    finally:
        if transport is not None:
            transport.close()

def obtener_tag_analytics():
    """Devuelve el snippet de Google tag (gtag.js) para Google Analytics.
    Se usa igual en TODAS las páginas del sitio (índice y páginas individuales)."""
    return f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA_MEASUREMENT_ID}');
</script>"""

def obtener_html_adblock():
    """Devuelve el popup de aviso de AdBlock. Se inserta igual en TODAS
    las páginas del sitio (índice y páginas individuales)."""
    return """
    <!-- Popup de adblock -->
    <div id="adblock-overlay">
        <div id="adblock-popup">
            <div class="adblock-header">
                <h2>AdBlocker Detected</h2>
            </div>
            <div class="adblock-content">
                <div class="adblock-icon">⚠️</div>
                <div class="adblock-message">
                    <p>We have detected that you are using an adblocker. Our service is funded through advertisements.</p>
                    <p>Please disable your adblocker to access JotaSoft78.</p>
                </div>
                <button class="adblock-button" id="reload-button">I've disabled AdBlocker</button>

                <div class="adblock-instructions">
                    <h3>How to disable adblocker:</h3>
                    <p>1. Click on the adblocker icon in your browser</p>
                    <p>2. Select "Pause on this site" or similar option</p>
                    <p>3. Refresh the page to continue</p>
                </div>
            </div>
        </div>
    </div>
"""

def obtener_script_adblock():
    """Devuelve el script de detección de AdBlock y el listener del botón
    de recarga. Se inserta igual en TODAS las páginas del sitio."""
    return """
        function detectAdBlock() {
          return new Promise((resolve) => {
            fetch('https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js', {
              method: 'HEAD',
              mode: 'no-cors',
              cache: 'no-store'
            }).catch(() => {
              resolve(true);
            });

            setTimeout(() => {
              const ad = document.createElement('div');
              ad.innerHTML = '&nbsp;';
              ad.className = 'ad-container adsbox advertisement ad-banner ad-unit';
              ad.style.position = 'absolute';
              ad.style.left = '-9999px';
              ad.style.top = '-9999px';
              ad.style.height = '1px';
              ad.style.width = '1px';
              document.body.appendChild(ad);

              setTimeout(() => {
                const isBlocked = ad.offsetHeight === 0 ||
                                  ad.offsetWidth === 0 ||
                                  getComputedStyle(ad).display === 'none' ||
                                  getComputedStyle(ad).visibility === 'hidden' ||
                                  ad.offsetParent === null;

                document.body.removeChild(ad);
                resolve(isBlocked);
              }, 100);
            }, 100);
          });
        }

        document.addEventListener('DOMContentLoaded', function() {
          detectAdBlock().then((isBlocked) => {
            if (isBlocked) {
              document.body.classList.add('adblock-detected');

              document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
              });
            }
          });

          var reloadBtn = document.getElementById('reload-button');
          if (reloadBtn) {
            reloadBtn.addEventListener('click', function() {
              location.reload(true);
            });
          }
        });
"""

def limpiar_conflictos_git(texto):
    """Elimina los marcadores de conflicto de Git si estuvieran presentes por error en los txt."""
    texto = re.sub(r'<<<<<<< HEAD.*?\n', '', texto)
    texto = re.sub(r'\|\|\|\|\|\|\|.*?(\r?\n)', '', texto, flags=re.DOTALL)
    texto = re.sub(r'=======\s*', '', texto)
    texto = re.sub(r'>>>>>>>\s*[a-zA-Z0-9_.-]+.*?\n', '', texto)
    return texto

def procesar_bbcode(texto):
    """Convierte etiquetas [spoiler]texto[/spoiler] en un acordeón HTML interactivo."""
    texto = limpiar_conflictos_git(texto)
    
    def replacer(match):
        contenido_spoiler = match.group(1)
        contenido_escapado = html.escape(contenido_spoiler).replace('\n', '<br>')
        return f'''
            <div class="spoiler-container">
                <button type="button" class="spoiler-btn" onclick="toggleSpoiler(this)">Ver contenido oculto (.reg)</button>
                <div class="spoiler-content">{contenido_escapado}</div>
            </div>
        '''
    
    patron = re.compile(r'\[spoiler\](.*?)\[/spoiler\]', re.DOTALL | re.IGNORECASE)
    
    partes = []
    ultimo_indice = 0
    
    for match in patron.finditer(texto):
        texto_normal = texto[ultimo_indice:match.start()]
        partes.append(html.escape(texto_normal).replace('\n', '<br>'))
        partes.append(replacer(match))
        ultimo_indice = match.end()
        
    texto_normal = texto[ultimo_indice:]
    partes.append(html.escape(texto_normal).replace('\n', '<br>'))
    
    return "".join(partes)

def aplicar_negritas_seo(html_texto, palabras_clave):
    """Resalta con <strong> la primera aparición de cada palabra clave SEO
    (nombre de la app, plataforma, 'gratis'...) fuera de los bloques de
    spoiler, para reforzar el indexado de Google sin saturar el texto de
    negritas ni tocar el contenido técnico oculto (.reg, etc.)."""
    partes = re.split(r'(<div class="spoiler-content">.*?</div>)', html_texto, flags=re.DOTALL)

    for palabra in palabras_clave:
        palabra = (palabra or "").strip()
        if not palabra:
            continue
        patron = re.compile(re.escape(palabra), re.IGNORECASE)
        for i, parte in enumerate(partes):
            if parte.startswith('<div class="spoiler-content">'):
                continue
            nueva_parte, encontrada = patron.subn(
                lambda m: f"<strong>{m.group(0)}</strong>", parte, count=1
            )
            if encontrada:
                partes[i] = nueva_parte
                break  # esta palabra clave ya ha sido resaltada una vez

    return "".join(partes)

def generar_slug(nombre, slugs_usados):
    """Genera un identificador único basado en el nombre de la app (sin acentos, en minúsculas y con guiones)."""
    slug = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    slug = slug.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    if not slug:
        slug = 'app'

    slug_base = slug
    contador = 2
    while slug in slugs_usados:
        slug = f"{slug_base}-{contador}"
        contador += 1

    slugs_usados.add(slug)
    return slug

def buscar_aplicaciones():
    apps = { "windows": [], "android": [] }
    slugs_usados = set()
    
    for plataforma in PLATAFORMAS:
        ruta_plat = os.path.join(os.getcwd(), plataforma)
        if not os.path.exists(ruta_plat):
            continue
            
        for nombre_app in os.listdir(ruta_plat):
            ruta_app = os.path.join(ruta_plat, nombre_app)
            
            if os.path.isdir(ruta_app):
                descripcion_raw = "Sin descripción disponible."
                ruta_txt = os.path.join(ruta_app, "descripcion.txt")
                if os.path.exists(ruta_txt):
                    with open(ruta_txt, "r", encoding="utf-8") as f:
                        descripcion_raw = f.read().strip()
                
                descripcion_html = procesar_bbcode(descripcion_raw)
                descripcion_html = aplicar_negritas_seo(
                    descripcion_html,
                    [nombre_app, plataforma.capitalize(), "gratis", "gratuito"]
                )
                
                archivo_app = "#"
                for archivo in os.listdir(ruta_app):
                    if archivo.lower().endswith((".exe", ".apk", ".zip", ".msi", ".rar", ".reg")):
                        archivo_url_encoded = archivo.replace(" ", "%20")
                        archivo_app = f"{plataforma}/{nombre_app}/{archivo_url_encoded}"
                        break
                
                captura = f"{plataforma}/{nombre_app}/captura.jpg"
                if not os.path.exists(os.path.join(os.getcwd(), captura)):
                    captura = ""
                
                slug = generar_slug(nombre_app, slugs_usados)

                apps[plataforma].append({
                    "nombre": nombre_app,
                    "descripcion": descripcion_html,
                    "descripcion_raw": descripcion_raw,
                    "archivo": archivo_app,
                    "captura": captura,
                    "slug": slug
                })
                
    return apps

def obtener_estilo_css():
    return """
        :root {
            --bg-color: #0b0f19;
            --card-bg: #131b2e;
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --body-font: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        * { box-sizing: border-box; }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: var(--body-font);
            margin: 0;
            padding: 0;
            line-height: 1.6;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header {
            padding: 5rem 2rem 3rem 2rem;
            text-align: center;
            background: radial-gradient(circle at 50% 0%, #1e293b 0%, var(--bg-color) 70%);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header h1 {
            font-size: 3rem;
            font-weight: 800;
            margin: 0 0 1.5rem 0;
            color: #ffffff;
            letter-spacing: -0.5px;
        }

        .header-banner {
            margin: 0 auto 1.5rem auto;
            max-width: 100%;
            overflow-x: auto;
        }

        header p {
            font-size: 1.15rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
        }

        /* Estilos del Menú de Navegación y Buscador Desplegable Global */
        .nav-controls {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(11, 15, 25, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            justify-content: space-between;
            max-width: 1100px;
            margin: 0 auto;
            width: 100%;
        }

        .nav-buttons {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }

        .nav-btn {
            background-color: #1e293b;
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: background-color 0.2s, border-color 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .nav-btn:hover {
            background-color: #334155;
            border-color: rgba(37, 99, 235, 0.4);
        }

        .search-container {
            position: relative;
            flex-grow: 1;
            max-width: 350px;
        }

        .search-input {
            width: 100%;
            background-color: #131b2e;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.5rem 1rem 0.5rem 2.5rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }

        .search-input:focus {
            border-color: var(--accent);
        }

        .search-icon {
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        /* Recuadro desplegable de resultados del buscador */
        .search-results-dropdown {
            position: absolute;
            top: calc(100% + 5px);
            left: 0;
            right: 0;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            z-index: 200;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }

        .search-result-item {
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-decoration: none;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-color);
            transition: background-color 0.2s;
        }

        .search-result-item:last-child {
            border-bottom: none;
        }

        .search-result-item:hover {
            background-color: #1e293b;
        }

        .search-result-name {
            font-weight: 600;
            font-size: 0.9rem;
        }

        .search-result-plat {
            font-size: 0.75rem;
            color: var(--text-secondary);
            background: rgba(255, 255, 255, 0.05);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }

        .search-no-results {
            padding: 1rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .main-container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 3rem 2rem;
            width: 100%;
        }

        .platform-section {
            margin-bottom: 4rem;
        }

        .platform-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            margin-bottom: 2.5rem;
        }

        .platform-header h2 {
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-primary);
            letter-spacing: 0.5px;
        }
        
        .platform-icon {
            font-size: 2rem;
        }

        .platform-count-badge {
            background-color: rgba(37, 99, 235, 0.15);
            color: #93c5fd;
            border: 1px solid rgba(37, 99, 235, 0.4);
            font-size: 0.9rem;
            font-weight: 700;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            letter-spacing: normal;
        }

        .nav-btn-count {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 999px;
            padding: 0.1rem 0.5rem;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .apps-grid {
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
            max-width: 950px;
            margin: 0 auto;
        }

        .app-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: row;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            transition: border-color 0.2s ease, transform 0.2s ease;
            scroll-margin-top: 100px;
        }

        .app-card:hover {
            border-color: rgba(37, 99, 235, 0.4);
            transform: translateY(-2px);
        }

        .card-image-container {
            width: 320px;
            min-width: 320px;
            background-color: #05070b;
            border-right: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            padding: 1.5rem;
        }

        .card-image-container img {
            width: 100%;
            height: auto;
            max-height: 400px;
            object-fit: contain;
            border-radius: 6px;
            cursor: pointer;
            transition: opacity 0.2s;
        }

        .card-image-container img:hover {
            opacity: 0.85;
        }
        
        .card-image-container.no-image::before {
            content: '📸';
            font-size: 3rem;
            opacity: 0.3;
        }

        .card-body {
            padding: 2.5rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
            word-break: break-word;
            overflow-wrap: break-word;
        }

        .card-title {
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            color: #ffffff;
        }

        .card-title-link {
            color: inherit;
            text-decoration: none;
        }

        .card-title-link:hover {
            text-decoration: underline;
        }

        .card-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 2rem;
            line-height: 1.6;
        }

        .spoiler-container {
            margin: 1.25rem 0;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background-color: rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .spoiler-btn {
            background-color: #1e293b;
            color: var(--text-primary);
            border: none;
            width: 100%;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background-color 0.2s;
        }

        .spoiler-btn::after {
            content: '▼';
            font-size: 0.75rem;
            transition: transform 0.2s;
        }

        .spoiler-btn.active::after {
            transform: rotate(180deg);
        }

        .spoiler-btn:hover {
            background-color: #334155;
        }

        .spoiler-content {
            display: none;
            padding: 1rem;
            background-color: #080c14;
            font-family: monospace;
            font-size: 0.85rem;
            color: #cbd5e1;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 250px;
            overflow-y: auto;
            border-top: 1px solid var(--border-color);
        }

        .card-actions {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .download-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: var(--accent);
            color: white;
            text-align: center;
            padding: 0.85rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: background-color 0.2s ease;
            align-self: flex-start;
        }

        .download-btn:hover {
            background-color: var(--accent-hover);
        }

        .share-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background-color: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            padding: 0.85rem 1.25rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: inherit;
            cursor: pointer;
            transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        }

        .share-btn:hover {
            background-color: #1e293b;
            border-color: rgba(37, 99, 235, 0.4);
            color: var(--text-primary);
        }

        .share-btn.copied {
            background-color: rgba(34, 197, 94, 0.15);
            border-color: rgba(34, 197, 94, 0.5);
            color: #86efac;
        }

        /* Estilos de la Ventana Modal */
        .image-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(5px);
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }

        .modal-content {
            max-width: 90%;
            max-height: 90vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            animation: modalScale 0.2s ease-in-out;
        }

        @keyframes modalScale {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        /* Estilos para el popup de adblock */
        #adblock-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(10px);
        }

        #adblock-popup {
            background: #1a1a1a;
            width: 90%;
            max-width: 600px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
            border: 2px solid #ff6600;
            text-align: center;
            color: white;
        }

        .adblock-header {
            background: #ff6600;
            color: white;
            padding: 20px;
            font-size: 24px;
            font-weight: bold;
        }

        .adblock-content {
            padding: 30px;
        }

        .adblock-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            color: #ff6600;
        }

        .adblock-message {
            margin-bottom: 25px;
            line-height: 1.6;
            font-size: 16px;
        }

        .adblock-button {
            background: #ff6600;
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 50px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s;
            font-weight: bold;
        }

        .adblock-button:hover {
            background: #e65c00;
            transform: translateY(-2px);
        }

        .adblock-instructions {
            margin-top: 20px;
            padding: 15px;
            background: #2a2a2a;
            border-radius: 8px;
            text-align: left;
            font-size: 14px;
        }

        .adblock-instructions h3 {
            margin-top: 0;
            color: #ff6600;
        }

        /* Ocultar contenido cuando se detecta adblock */
        body.adblock-detected header,
        body.adblock-detected .nav-controls,
        body.adblock-detected .main-container,
        body.adblock-detected .app-page-wrap,
        body.adblock-detected footer {
            display: none !important;
        }

        /* Mostrar el popup cuando se detecta adblock */
        body.adblock-detected #adblock-overlay {
            display: flex !important;
        }

        footer {
            text-align: center;
            padding: 3rem 2rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            margin-top: auto;
            font-size: 0.85rem;
        }

        @media (max-width: 768px) {
            .app-card {
                flex-direction: column;
            }
            .card-image-container {
                width: 100%;
                min-width: 100%;
                height: 260px;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            .card-body {
                padding: 1.5rem;
            }
            header h1 { font-size: 2.25rem; }
            .download-btn { width: 100%; }
            .nav-controls {
                flex-direction: column;
                align-items: stretch;
            }
            .search-container {
                max-width: 100%;
            }
        }
    """

def generar_html(apps):
    estilo_css = obtener_estilo_css()

    script_js = """
        function toggleSpoiler(btn) {
            btn.classList.toggle('active');
            var content = btn.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        }

        function abrirModal(imgSrc) {
            var modal = document.getElementById('imageModal');
            var modalImg = document.getElementById('modalImage');
            modal.style.display = "flex";
            modalImg.src = imgSrc;
        }

        function cerrarModal() {
            var modal = document.getElementById('imageModal');
            modal.style.display = "none";
        }

        window.onclick = function(event) {
            var modal = document.getElementById('imageModal');
            if (event.target === modal) {
                cerrarModal();
            }
            // Cerrar el desplegable de búsqueda si se hace clic fuera
            if (!event.target.closest('.search-container')) {
                var dropdown = document.getElementById('searchResultsDropdown');
                if (dropdown) dropdown.style.display = 'none';
            }
        }

        // Script para el buscador desplegable buscando en todo el contenido (nombre y descripción)
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('searchInput');
            const dropdown = document.getElementById('searchResultsDropdown');

            if (searchInput && dropdown) {
                const appCards = document.querySelectorAll('.app-card');
                const appsData = [];

                appCards.forEach(card => {
                    const originalName = card.querySelector('.card-title').textContent;
                    const descText = card.querySelector('.card-description').textContent;
                    const searchableText = (originalName + ' ' + descText).toLowerCase();
                    const platform = card.getAttribute('data-platform');
                    const cardId = card.id;
                    const pagePath = card.getAttribute('data-page');
                    
                    appsData.push({ 
                        searchableText: searchableText, 
                        originalName: originalName, 
                        platform: platform, 
                        cardId: cardId,
                        pagePath: pagePath
                    });
                });

                searchInput.addEventListener('input', function(e) {
                    const term = e.target.value.toLowerCase().trim();
                    dropdown.innerHTML = '';

                    if (term === '') {
                        dropdown.style.display = 'none';
                        return;
                    }

                    const filtered = appsData.filter(app => app.searchableText.includes(term));

                    if (filtered.length > 0) {
                        filtered.forEach(app => {
                            const item = document.createElement('a');
                            item.href = app.pagePath;
                            item.className = 'search-result-item';
                            item.innerHTML = `
                                <span class="search-result-name">${app.originalName}</span>
                                <span class="search-result-plat">${app.platform.toUpperCase()}</span>
                            `;
                            item.addEventListener('click', function() {
                                dropdown.style.display = 'none';
                                searchInput.value = '';
                            });
                            dropdown.appendChild(item);
                        });
                        dropdown.style.display = 'block';
                    } else {
                        const noRes = document.createElement('div');
                        noRes.className = 'search-no-results';
                        noRes.textContent = 'No se encontraron aplicaciones';
                        dropdown.appendChild(noRes);
                        dropdown.style.display = 'block';
                    }
                });

                searchInput.addEventListener('focus', function() {
                    if (searchInput.value.trim() !== '') {
                        dropdown.style.display = 'block';
                    }
                });
            }
        });

        // Función para compartir una app: usa el selector nativo del móvil (Web Share API)
        // y, si no está disponible (la mayoría de navegadores de escritorio), copia el enlace directo.
        function compartirApp(nombreApp, rutaPagina, botonEl) {
          const url = window.location.origin + '/' + rutaPagina;
          const datosCompartir = {
            title: 'JotaSoft78 - ' + nombreApp,
            text: 'Descarga ' + nombreApp + ' en JotaSoft78',
            url: url
          };

          if (navigator.share) {
            navigator.share(datosCompartir).catch(() => {});
            return;
          }

          const mostrarCopiado = () => {
            const textoOriginal = botonEl.innerHTML;
            botonEl.classList.add('copied');
            botonEl.innerHTML = '✅ <span class="share-btn-label">¡Enlace copiado!</span>';
            setTimeout(() => {
              botonEl.classList.remove('copied');
              botonEl.innerHTML = textoOriginal;
            }, 2000);
          };

          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(mostrarCopiado).catch(() => {
              window.prompt('Copia este enlace:', url);
            });
          } else {
            window.prompt('Copia este enlace:', url);
          }
        }
    """ + obtener_script_adblock()

    total_apps_global = sum(len(apps[plataforma]) for plataforma in PLATAFORMAS)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Metaetiquetas SEO y Open Graph -->
    <title>JotaSoft78 | Repositorio Oficial de Software</title>
    <meta name="description" content="Repositorio oficial de aplicaciones para Windows y Android desarrolladas por JotaSoft78. Descarga herramientas y utilidades optimizadas.">
    <meta name="keywords" content="JotaSoft78, software, aplicaciones, windows, android, descargas, utilidades">
    <meta name="author" content="JotaSoft78">
    
    <meta property="og:title" content="JotaSoft78 | Repositorio de Software">
    <meta property="og:description" content="Descarga utilidades y aplicaciones para Windows y Android de forma rápida y segura.">
    <meta property="og:type" content="website">
    
    <style>{estilo_css}</style>
    {obtener_tag_analytics()}
</head>
<body>

    {obtener_html_adblock()}
    <header>
        <h1>JotaSoft78</h1>
        <div class="header-banner">
            <!--PUBLICIDAD-->
		        <iframe
            title="Publicidad"
            src="iframe.html"
            width="728"
            height="90"
            style="border:0; overflow:hidden;"
            scrolling="no"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation">
        </iframe>
        </div>
        <p>Repositorio oficial de aplicaciones para Windows y Android. Actualmente con <strong>{total_apps_global}</strong> {"aplicación disponible" if total_apps_global == 1 else "aplicaciones disponibles"}.</p>
    </header>

    <!-- Barra de navegación fija con botones de sección y buscador desplegable global -->
    <nav class="nav-controls">
        <div class="nav-buttons">
"""

    for plataforma in PLATAFORMAS:
        if apps[plataforma]:
            total_plataforma = len(apps[plataforma])
            html_content += f"""            <a href="#{plataforma}" class="nav-btn"><span>{ICONOS.get(plataforma, '')}</span> {plataforma.capitalize()} <span class="nav-btn-count">{total_plataforma}</span></a>\n"""

    html_content += f"""        </div>
        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-input" placeholder="Buscar aplicaciones en todo el contenido..." autocomplete="off">
            <div id="searchResultsDropdown" class="search-results-dropdown"></div>
        </div>
    </nav>

    <main class="main-container">
"""

    app_counter = 0
    for plataforma in PLATAFORMAS:
        if apps[plataforma]:
            total_plataforma = len(apps[plataforma])
            texto_contador = "aplicación" if total_plataforma == 1 else "aplicaciones"
            html_content += f"""
        <section id="{plataforma}" class="platform-section">
            <div class="platform-header">
                <span class="platform-icon">{ICONOS.get(plataforma, '')}</span>
                <h2>Aplicaciones para {plataforma.capitalize()}</h2>
                <span class="platform-count-badge">{total_plataforma} {texto_contador}</span>
            </div>
            
            <div class="apps-grid">
"""
            for app in apps[plataforma]:
                app_counter += 1
                card_id = app["slug"]
                ruta_pagina_app = f"{plataforma}/{card_id}.html"
                
                img_tag = f'<img src="{html.escape(app["captura"])}" alt="Captura de {html.escape(app["nombre"])}" loading="lazy" onclick="abrirModal(this.src)">'
                img_wrapper_class = "card-image-container"
                if not app["captura"]:
                    img_tag = ""
                    img_wrapper_class += " no-image"

                texto_boton = f"Descargar {app['nombre']} ({plataforma.capitalize()})"
                
                # Evento de analíticas integrado para el contador de descargas
                onclick_analytics = f"gtag('event', 'download', {{'app_name': '{app['nombre']}', 'platform': '{plataforma}'}});"

                html_content += f"""
                <article class="app-card" id="{card_id}" data-platform="{plataforma}" data-page="{html.escape(ruta_pagina_app)}">
                    <div class="{img_wrapper_class}">
                        {img_tag}
                    </div>
                    <div class="card-body">
                        <div>
                            <h3 class="card-title"><a href="{html.escape(ruta_pagina_app)}" class="card-title-link">{html.escape(app["nombre"])}</a></h3>
                            <div class="card-description">{app["descripcion"]}</div>
                        </div>
                        <div class="card-actions">
                            <a href="{html.escape(app["archivo"])}" class="download-btn" download onclick="{onclick_analytics}">
                                {html.escape(texto_boton)}
                            </a>
                            <button type="button" class="share-btn" title="Compartir esta aplicación" onclick="compartirApp('{html.escape(app['nombre'], quote=True)}', '{html.escape(ruta_pagina_app, quote=True)}', this)">
                                🔗 <span class="share-btn-label">Compartir</span>
                            </button>
                        </div>
                    </div>
                </article>
"""
            html_content += "            </div>\n        </section>\n"

    html_content += f"""
    </main>

    <!-- Ventana Modal para las imágenes -->
    <div id="imageModal" class="image-modal" onclick="cerrarModal()">
        <img class="modal-content" id="modalImage">
    </div>

    <footer>
        <p>&copy; 2026 JotaSoft78 - Todos los derechos reservados.</p>
    </footer>

    <script>{script_js}</script>
</body>
</html>
"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"¡Archivo {HTML_OUTPUT} generado con éxito con buscador desplegable que analiza todo el texto y botones de sección rápidos!")

def generar_meta_descripcion(texto_raw, nombre_app, plataforma):
    """Genera una meta description limpia (sin BBCode/spoilers) y truncada a ~155 caracteres."""
    texto = re.sub(r'\[spoiler\].*?\[/spoiler\]', '', texto_raw, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r'\[/?[a-zA-Z0-9]+(?:=[^\]]*)?\]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    if not texto or texto == "Sin descripción disponible.":
        texto = f"Descarga {nombre_app} gratis para {plataforma.capitalize()}."
    if len(texto) > 155:
        texto = texto[:152].rsplit(" ", 1)[0] + "..."
    return texto

def generar_pagina_individual(app, plataforma):
    """Genera una página HTML real y autocontenida para una app, con SEO on-page:
    title único, meta description, canonical, Open Graph, Twitter Card y datos
    estructurados JSON-LD (SoftwareApplication)."""
    nombre = app["nombre"]
    slug = app["slug"]
    url_pagina = f"{BASE_URL}/{plataforma}/{slug}.html"
    meta_desc = generar_meta_descripcion(app["descripcion_raw"], nombre, plataforma)
    titulo_pagina = f"{nombre} para {plataforma.capitalize()} | Descarga gratis en JotaSoft78"

    imagen_tag = ""
    imagen_og = ""
    if app["captura"]:
        ruta_imagen_absoluta = f"{BASE_URL}/{app['captura']}"
        imagen_og = f'<meta property="og:image" content="{html.escape(ruta_imagen_absoluta)}">\n    <meta name="twitter:image" content="{html.escape(ruta_imagen_absoluta)}">'
        imagen_tag = f'<img src="../{html.escape(app["captura"])}" alt="Captura de pantalla de {html.escape(nombre)} en {plataforma.capitalize()}" loading="lazy" style="max-width:100%;border-radius:12px;">'

    texto_boton = f"Descargar {nombre} ({plataforma.capitalize()})"
    ruta_archivo = f"../{app['archivo']}" if not app["archivo"].startswith(("http://", "https://", "#")) else app["archivo"]

    json_ld = f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": {json.dumps(nombre)},
      "operatingSystem": {json.dumps(plataforma.capitalize())},
      "applicationCategory": "UtilitiesApplication",
      "description": {json.dumps(meta_desc)},
      "url": {json.dumps(url_pagina)},
      "offers": {{
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "EUR"
      }}
    }}
    </script>"""

    pagina = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(titulo_pagina)}</title>
    <meta name="description" content="{html.escape(meta_desc)}">
    <link rel="canonical" href="{html.escape(url_pagina)}">

    <meta property="og:type" content="website">
    <meta property="og:title" content="{html.escape(titulo_pagina)}">
    <meta property="og:description" content="{html.escape(meta_desc)}">
    <meta property="og:url" content="{html.escape(url_pagina)}">
    <meta property="og:site_name" content="JotaSoft78">
    {imagen_og}

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(titulo_pagina)}">
    <meta name="twitter:description" content="{html.escape(meta_desc)}">
    {json_ld}
    {obtener_tag_analytics()}

    <style>{obtener_estilo_css()}
        .app-page-wrap {{ max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }}
        .breadcrumb {{ margin-bottom: 1.5rem; font-size: 0.9rem; }}
        .breadcrumb a {{ color: var(--text-secondary); }}
        .app-page-wrap h1 {{ font-size: 2rem; margin-bottom: 1rem; color: #fff; }}
        .app-page-wrap h2 {{ font-size: 1.4rem; font-weight: 700; margin: 2.25rem 0 1rem 0; color: #fff; letter-spacing: 0.3px; }}
        .app-page-wrap .app-lead {{ font-size: 1.05rem; color: var(--text-secondary); margin: 0 0 1.5rem 0; }}
    </style>
</head>
<body>
    {obtener_html_adblock()}
    <div class="app-page-wrap">
        <nav class="breadcrumb" aria-label="Miga de pan">
            <a href="../index.html">Inicio</a> &rsaquo; {html.escape(nombre)}
        </nav>
        <article>
            <h1>{html.escape(nombre)} para {html.escape(plataforma.capitalize())}</h1>
            <p class="app-lead">Descarga <strong>{html.escape(nombre)}</strong> gratis para <strong>{html.escape(plataforma.capitalize())}</strong>: la última versión disponible en JotaSoft78, lista para instalar en pocos pasos.</p>

            <h2>Descripción de {html.escape(nombre)}</h2>
            {imagen_tag}
            <div class="card-description">{app["descripcion"]}</div>

            <h2>Descargar {html.escape(nombre)} gratis para {html.escape(plataforma.capitalize())}</h2>
            <p>
                <a href="{html.escape(ruta_archivo)}" class="download-btn" download>
                    {html.escape(texto_boton)}
                </a>
            </p>
        </article>
    </div>

    <script>{obtener_script_adblock()}</script>
</body>
</html>
"""
    return pagina

def generar_paginas_individuales(apps):
    rutas_generadas = []
    for plataforma in PLATAFORMAS:
        os.makedirs(plataforma, exist_ok=True)
        for app in apps[plataforma]:
            pagina = generar_pagina_individual(app, plataforma)
            ruta = os.path.join(plataforma, f"{app['slug']}.html")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(pagina)
            rutas_generadas.append(f"{plataforma}/{app['slug']}.html")
    print(f"¡{len(rutas_generadas)} páginas individuales generadas en 'windows/' y 'android/'!")
    return rutas_generadas

def generar_sitemap(rutas_apps=None):
    """Genera un sitemap.xml válido: la URL raíz + una URL real por cada página
    individual de app (sin '#', ya que cada una es un archivo .html propio)."""
    rutas_apps = rutas_apps or []
    urls = [f"{BASE_URL}/"] + [f"{BASE_URL}/{ruta}" for ruta in rutas_apps]
    entradas = "\n".join(f"  <url>\n    <loc>{html.escape(u)}</loc>\n  </url>" for u in urls)
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entradas}
</urlset>
"""
    with open(SITEMAP_OUTPUT, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print(f"¡Archivo {SITEMAP_OUTPUT} generado con éxito ({len(urls)} URLs, sin '#')!")

    subir_sitemap_por_sftp(
        SITEMAP_OUTPUT,
        SFTP_HOST, SFTP_PORT, SFTP_USUARIO,
        contrasena=SFTP_CONTRASENA,
        clave_privada=SFTP_CLAVE_PRIVADA,
        ruta_remota=SFTP_RUTA_REMOTA
    )

if __name__ == "__main__":
    app_data = buscar_aplicaciones()
    generar_html(app_data)
    rutas_apps = generar_paginas_individuales(app_data)
    generar_sitemap(rutas_apps)