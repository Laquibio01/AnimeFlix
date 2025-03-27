# Importa las clases y funciones necesarias de Flask
# - Flask: Clase principal para crear la aplicación web
# - render_template: Función para renderizar archivos HTML desde la carpeta 'templates'
# - request: Objeto que maneja los datos de solicitudes HTTP (GET/POST)
from flask import Flask, render_template, request

# Importa la librería 'requests' para hacer peticiones HTTP a APIs externas
import requests

# Crea una instancia de la aplicación Flask
# __name__ es una variable especial de Python que representa el nombre del módulo actual
app = Flask(__name__)


def get_anime_info_jikan(anime_name):
    # """
    # Consulta la API de Jikan (MyAnimeList) para obtener información de un anime.
    
    # Args:
    #     anime_name (str): Nombre del anime a buscar.
    
    # Returns:
    #     list[dict] | None: Lista de animes coincidentes en formato JSON, o None si hay error.
    # """
    # Construye la URL de la API con el nombre del anime y el parámetro 'sfw' (Safe For Work)
    jikan_url = f"https://api.jikan.moe/v4/anime?q={anime_name}&sfw"
    
    # Realiza una petición GET a la API
    response = requests.get(jikan_url)
    
    # Si la respuesta es exitosa (código 200), retorna los datos en formato JSON
    if response.status_code == 200:
        return response.json()["data"]  # Extrae el campo 'data' del JSON
    
    # Si falla, retorna None
    return None


def get_anime_info_anilist(anime_name):
    # """
    # Consulta la API de AniList (GraphQL) para obtener detalles avanzados de un anime.
    
    # Args:
    #     anime_name (str): Nombre del anime a buscar.
    
    # Returns:
    #     dict | None: Datos del anime (títulos, descripción, imagen, estudios), o None si hay error.
    # """
    # Define la consulta GraphQL para obtener datos específicos
    query = """
    query ($name: String) {
      Media(search: $name) {
        title {
          romaji   # Título en japonés (romaji)
          english  # Título en inglés
        }
        description  # Sinopsis del anime
        coverImage {
          large  # URL de la imagen de portada
        }
        studios {
          nodes {
            name  # Lista de estudios de animación
          }
        }
      }
    }
    """
    
    # URL del endpoint de AniList (GraphQL)
    url = "https://graphql.anilist.co"
    
    # Variables para la consulta GraphQL (el nombre del anime a buscar)
    variables = {"name": anime_name}
    
    # Realiza una petición POST con la consulta y variables
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    # Si la respuesta es exitosa, retorna los datos del anime
    if response.status_code == 200:
        return response.json()["data"]["Media"]  # Extrae el nodo 'Media'
    
    return None


def get_anime_info_kitsu(anime_name):
    # """
    # Consulta la API de Kitsu para obtener información básica de un anime.
    
    # Args:
    #     anime_name (str): Nombre del anime a buscar.
    
    # Returns:
    #     dict | None: Primer resultado de la búsqueda, o None si hay error.
    # """
    # Construye la URL de la API con el nombre del anime
    kitsu_url = f"https://kitsu.io/api/edge/anime?filter[text]={anime_name}"
    
    # Headers requeridos por la API de Kitsu (formato JSON API)
    headers = {
        "Accept": "application/vnd.api+json",  # Indica que se espera JSON
        "Content-Type": "application/vnd.api+json"  # Tipo de contenido
    }
    
    # Realiza una petición GET con los headers personalizados
    response = requests.get(kitsu_url, headers=headers)
    
    # Si la respuesta es exitosa y hay datos, retorna el primer anime encontrado
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]  # Retorna el primer resultado
    
    return None


# Define la ruta principal que acepta métodos GET (carga inicial) y POST (búsqueda)
@app.route("/", methods=["GET", "POST"])
def index():
    # """
    # Maneja la lógica de la página principal:
    # - GET: Muestra el formulario de búsqueda vacío.
    # - POST: Procesa el formulario y muestra resultados.
    # """
    # Inicializa variables para almacenar datos de las APIs
    anime_data_jikan = None
    anime_data_anilist = None
    anime_data_kitsu = None

    # Si la solicitud es POST (envío del formulario)
    if request.method == "POST":
        # Obtiene el nombre del anime desde el formulario HTML
        anime_name = request.form.get("anime_name")
        
        # Consulta las tres APIs en paralelo (podría optimizarse con threads)
        anime_data_jikan = get_anime_info_jikan(anime_name)
        anime_data_anilist = get_anime_info_anilist(anime_name)
        anime_data_kitsu = get_anime_info_kitsu(anime_name)

    # Renderiza el template 'index.html' con los datos obtenidos
    return render_template(
        "index.html", 
        anime_data_jikan=anime_data_jikan, 
        anime_data_anilist=anime_data_anilist,
        anime_data_kitsu=anime_data_kitsu
    )

# Verifica si el script se ejecuta directamente (no importado como módulo)
if __name__ == "__main__":
    # Inicia la aplicación Flask en modo debug:
    # - debug=True: Recarga automática al detectar cambios y muestra errores detallados
    # - Solo para desarrollo (no usar en producción)
    app.run(debug=True)