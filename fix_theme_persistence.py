"""
Script para corregir la persistencia del tema
Usar un enfoque que funcione antes de que el body esté listo
"""
import os

templates_dir = r"c:\Users\Usuario\Documents\HeroApp #2\MyPage\templates"

html_files = [
    'Home.html',
    'dashboard.html',
    'Comisiones.html',
    'posiciones.html',
    'procesos.html',
    'Mantenimientos.html',
    'Audios.html'
]

# Nuevo script que funciona correctamente
new_theme_script = """    <!-- Theme initialization - prevents flash -->
    <script>
    (function(){
        var t=localStorage.getItem('darkMode');
        if(t==='true'){
            // Usar un intervalo muy corto para aplicar apenas el body esté disponible
            var applyTheme=function(){
                if(document.body){
                    document.body.classList.add('dark');
                }else{
                    setTimeout(applyTheme,1);
                }
            };
            applyTheme();
        }
    })();
    </script>
"""

def fix_theme_script(filepath):
    """Reemplaza el script de tema con uno que funcione"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar el script de tema actual
    import re
    
    # Patrón para encontrar el script de tema actual
    pattern = r'    <!-- Theme initialization - prevents flash -->\s*<script>\(function\(\)\{var t=localStorage\.getItem\(\'darkMode\'\);if\(t===\'true\'\)\{document\.body\.classList\.add\(\'dark\'\);\}\}\)\(\);</script>'
    
    if re.search(pattern, content):
        content = re.sub(pattern, new_theme_script.strip(), content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Procesar archivos
print("Corrigiendo persistencia de tema...\n")
count = 0
for filename in html_files:
    filepath = os.path.join(templates_dir, filename)
    if os.path.exists(filepath):
        if fix_theme_script(filepath):
            print(f"✓ {filename}")
            count += 1
        else:
            print(f"○ {filename} - Sin cambios")

print(f"\n✅ {count} archivos corregidos")
