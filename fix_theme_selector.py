"""
Script para corregir el selector de tema en templates
Cambiar de document.documentElement a document.body
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

def fix_theme_selector(filepath):
    """Corrige el selector del tema"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cambiar document.documentElement a document.body en el script de tema
    old_script = "document.documentElement.classList.add('dark')"
    new_script = "document.body.classList.add('dark')"
    
    if old_script in content:
        content = content.replace(old_script, new_script)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Procesar archivos
print("Corrigiendo selector de tema...\n")
count = 0
for filename in html_files:
    filepath = os.path.join(templates_dir, filename)
    if os.path.exists(filepath):
        if fix_theme_selector(filepath):
            print(f"✓ {filename}")
            count += 1
        else:
            print(f"○ {filename} - Sin cambios")

print(f"\n✅ {count} archivos corregidos")
