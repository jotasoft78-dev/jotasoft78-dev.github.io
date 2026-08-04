import os
import html
import re

# Configuración de carpetas
PLATAFORMAS = ["windows", "android"]
HTML_OUTPUT = "index.html"

# Definir iconos para las plataformas
ICONOS = {
    "windows": "🖥️",
    "android": "📱"
}

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

def buscar_aplicaciones():
    apps = { "windows": [], "android": [] }
    
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
                
                archivo_app = "#"
                for archivo in os.listdir(ruta_app):
                    if archivo.lower().endswith((".exe", ".apk", ".zip", ".msi", ".rar", ".reg")):
                        archivo_url_encoded = archivo.replace(" ", "%20")
                        archivo_app = f"{plataforma}/{nombre_app}/{archivo_url_encoded}"
                        break
                
                captura = f"{plataforma}/{nombre_app}/captura.jpg"
                if not os.path.exists(os.path.join(os.getcwd(), captura)):
                    captura = ""
                
                apps[plataforma].append({
                    "nombre": nombre_app,
                    "descripcion": descripcion_html,
                    "archivo": archivo_app,
                    "captura": captura
                })
                
    return apps

def generar_html(apps):
    estilo_css = """
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
        body.adblock-detected .main-container,
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
        }
    """

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
        }

        // Función para detectar AdBlock
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
    
</head>
<body>

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

    <header>
        <h1>JotaSoft78</h1>
        <div class="header-banner">
            <!--PUBLICIDAD-->
		        <iframe
            title="Publicidad"
            src="https://tiny-paste.com/ad-banner.html"
            width="728"
            height="90"
            style="border:0; overflow:hidden;"
            scrolling="no"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation">
        </iframe>
        </div>
        <p>Repositorio oficial de aplicaciones para Windows y Android.</p>
    </header>

    <main class="main-container">
"""

    for plataforma in PLATAFORMAS:
        if apps[plataforma]:
            html_content += f"""
        <section class="platform-section">
            <div class="platform-header">
                <span class="platform-icon">{ICONOS.get(plataforma, '')}</span>
                <h2>{plataforma.upper()}</h2>
            </div>
            
            <div class="apps-grid">
"""
            for app in apps[plataforma]:
                img_tag = f'<img src="{html.escape(app["captura"])}" alt="Captura de {html.escape(app["nombre"])}" loading="lazy" onclick="abrirModal(this.src)">'
                img_wrapper_class = "card-image-container"
                if not app["captura"]:
                    img_tag = ""
                    img_wrapper_class += " no-image"

                texto_boton = f"Descargar {app['nombre']} ({plataforma.capitalize()})"

                html_content += f"""
                <article class="app-card">
                    <div class="{img_wrapper_class}">
                        {img_tag}
                    </div>
                    <div class="card-body">
                        <div>
                            <h3 class="card-title">{html.escape(app["nombre"])}</h3>
                            <div class="card-description">{app["descripcion"]}</div>
                        </div>
                        <a href="{html.escape(app["archivo"])}" class="download-btn" download>
                            {html.escape(texto_boton)}
                        </a>
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
    print(f"¡Archivo {HTML_OUTPUT} generado con éxito, con el sistema anti-adblock integrado!")

if __name__ == "__main__":
    app_data = buscar_aplicaciones()
    generar_html(app_data)