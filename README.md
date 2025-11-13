# Proyecto de Gestión de Ventas y Comisiones

Esta es una aplicación web desarrollada en Flask que sirve como un dashboard para la visualización y gestión de datos de ventas, comisiones, y objetivos para empresas de ventas.

## Características Principales

- **Dashboard Interactivo:** Visualización de métricas de ventas y rendimiento a través de gráficos.
- **Gestión de Datos:** Carga de datos de ventas, pagos y objetivos a través de archivos Excel.
- **Cálculo de Comisiones:** Lógica para calcular comisiones basada en objetivos y resultados de ventas.
- **Autenticación de Usuarios:** Sistema de login y registro de usuarios con JSON Web Tokens (JWT) para proteger las rutas.
- **API REST:** Endpoints para consultar datos de empleados, supervisores, ventas, y más.
- **Visualización de Rankings:** Muestra los empleados con mejores rendimientos en ventas.

## Estructura del Proyecto

- `app.py`: Archivo principal de la aplicación Flask. Contiene las rutas, la lógica de negocio y la configuración.
- `cn.py`: Módulo para la conexión a la base de datos SQLite y funciones para la consulta de datos.
- `chart_utils.py`: Utilidades para generar los datos necesarios para los gráficos del dashboard.
- `gestiondata.py`: Módulo para el procesamiento y la carga de datos desde archivos Excel.
- `templates/`: Contiene las plantillas HTML que renderiza la aplicación.
- `static/`: Almacena los archivos estáticos como CSS, JavaScript, e imágenes.
- `requirements.txt`: Lista de las dependencias de Python necesarias para el proyecto.

## Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd MyPage
    ```

2.  **Crear un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar las dependencias:**
    Asegúrate de tener `pip` instalado. Ejecuta el siguiente comando para instalar las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos:**
    La aplicación utiliza una base de datos SQLite. Asegúrate de que la ruta en el archivo `cn.py` (`DB_PATH`) sea correcta.


5.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```

    La aplicación estará disponible en `http://127.0.0.1:5000`.