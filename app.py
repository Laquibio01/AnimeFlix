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

def get_anime_episodes(anime_id, source, anime_title=None):
    """
    Obtiene los episodios de un anime usando diferentes fuentes
    
    Args:
        anime_id (str): ID del anime en la fuente correspondiente
        source (str): Fuente de datos ('jikan', 'anilist', 'kitsu')
        anime_title (str): Título del anime para búsquedas alternativas
        
    Returns:
        list: Lista de episodios con sus detalles
    """
    episodes = []
    
    try:
        if source == "jikan":
            # Usar Jikan para obtener episodios
            url = f"https://api.jikan.moe/v4/anime/{anime_id}/episodes"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for ep in data.get("data", []):
                    episodes.append({
                        "number": ep.get("mal_id", ep.get("episode", 0)),
                        "title": ep.get("title", f"Episodio {ep.get('episode', '')}"),
                        "video_url": "",  # Jikan no proporciona enlaces directos
                        "thumbnail": ep.get("images", {}).get("jpg", {}).get("image_url", "")
                    })
        
        elif source == "anilist":
            # Usar AniList + consumidor de streaming
            query = """
            query ($id: Int) {
                Media(id: $id) {
                    id
                    title {
                        romaji
                        english
                    }
                    episodes
                }
            }
            """
            variables = {"id": int(anime_id)}
            response = requests.post(
                "https://graphql.anilist.co",
                json={"query": query, "variables": variables}
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {}).get("Media", {})
                total_eps = data.get("episodes", 12)
                title = data.get("title", {}).get("romaji", "") or anime_title
                
                # Buscar en Gogoanime (ejemplo)
                if title:
                    search_url = f"https://gogoanime3.co/search.html?keyword={title}"
                    # Aquí implementarías el scraping para obtener los enlaces
                    # Esto es solo un ejemplo conceptual
                    for i in range(1, total_eps + 1):
                        episodes.append({
                            "number": i,
                            "title": f"Episodio {i}",
                            "video_url": f"https://gogoanime3.co/{title.lower().replace(' ', '-')}-episode-{i}",
                            "thumbnail": f"https://via.placeholder.com/300x169?text={title}+Ep{i}"
                        })
        
        elif source == "kitsu":
            # Usar Kitsu + consumidor de streaming
            url = f"https://kitsu.io/api/edge/anime/{anime_id}/episodes"
            headers = {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json"
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                for ep in data.get("data", []):
                    attributes = ep.get("attributes", {})
                    episodes.append({
                        "number": attributes.get("number", 0),
                        "title": attributes.get("canonicalTitle", ""),
                        "video_url": "",  # Kitsu no proporciona enlaces directos
                        "thumbnail": attributes.get("thumbnail", {}).get("original", "")
                    })
    
    except Exception as e:
        print(f"Error al obtener episodios: {e}")
    
    # Si no se encontraron episodios, devolver algunos de ejemplo
    if not episodes:
        for i in range(1, 13):
            episodes.append({
                "number": i,
                "title": f"Episodio {i}",
                "video_url": f"https://example.com/videos/{source}_{anime_id}_ep{i}.mp4",
                "thumbnail": f"https://via.placeholder.com/300x169?text=Episodio+{i}"
            })
    
    return episodes

@app.route("/watch/<source>/<anime_id>")
def watch(source, anime_id):
    episodes = get_anime_episodes(anime_id, source)
    return render_template("watch.html", episodes=episodes)


# Verifica si el script se ejecuta directamente (no importado como módulo)
if __name__ == "__main__":
    # Inicia la aplicación Flask en modo debug:
    # - debug=True: Recarga automática al detectar cambios y muestra errores detallados
    # - Solo para desarrollo (no usar en producción)
    app.run(debug=True)