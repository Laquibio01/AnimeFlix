# """
# Anime Information Fetcher - Flask Web Application

# Aplicación web que consulta información de anime desde múltiples APIs (Jikan, AniList, Kitsu)
# y muestra los resultados en una página HTML.

# Dependencias:
# - Flask: Framework web para rutas y renderizado de templates.
# - requests: Para hacer solicitudes HTTP a las APIs.
# """

from flask import Flask, render_template, request
import requests

app = Flask(__name__)


def get_anime_info_jikan(anime_name):
    # """
    # Obtiene información de anime desde la API de Jikan (MyAnimeList).

    # Args:
    #     anime_name (str): Nombre del anime a buscar.

    # Returns:
    #     list[dict] | None: Lista de resultados de anime en formato JSON si la solicitud es exitosa,
    #                        None en caso de error o si no hay resultados.
    # """
    jikan_url = f"https://api.jikan.moe/v4/anime?q={anime_name}&sfw"
    response = requests.get(jikan_url)
    
    if response.status_code == 200:
        return response.json()["data"]
    return None


def get_anime_info_anilist(anime_name):
    # """
    # Obtiene información detallada de anime desde la API GraphQL de AniList.

    # Args:
    #     anime_name (str): Nombre del anime a buscar.

    # Returns:
    #     dict | None: Diccionario con datos del anime (títulos, descripción, imagen, estudios) 
    #                 si la solicitud es exitosa, None en caso de error.
    # """
    query = """
    query ($name: String) {
      Media(search: $name) {
        title {
          romaji
          english
        }
        description
        coverImage {
          large
        }
        studios {
          nodes {
            name
          }
        }
      }
    }
    """
    url = "https://graphql.anilist.co"
    variables = {"name": anime_name}
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        return response.json()["data"]["Media"]
    return None


def get_anime_info_kitsu(anime_name):
    # """
    # Obtiene información de anime desde la API de Kitsu.

    # Args:
    #     anime_name (str): Nombre del anime a buscar.

    # Returns:
    #     dict | None: Primer resultado de anime en formato JSON si la solicitud es exitosa,
    #                  None en caso de error o si no hay resultados.
    # """
    kitsu_url = f"https://kitsu.io/api/edge/anime?filter[text]={anime_name}"
    headers = {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json"
    }
    response = requests.get(kitsu_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]  # Devuelve el primer resultado
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    # """
    # Ruta principal de la aplicación Flask.

    # Métodos:
    #     GET: Muestra el formulario de búsqueda vacío.
    #     POST: Procesa el formulario y muestra resultados de las APIs.

    # Returns:
    #     str: HTML renderizado con el template 'index.html' y los datos de anime.
    # """
    anime_data_jikan = None
    anime_data_anilist = None
    anime_data_kitsu = None

    if request.method == "POST":
        anime_name = request.form.get("anime_name")
        
        # Obtener datos de las APIs
        anime_data_jikan = get_anime_info_jikan(anime_name)
        anime_data_anilist = get_anime_info_anilist(anime_name)
        anime_data_kitsu = get_anime_info_kitsu(anime_name)

    return render_template(
        "index.html", 
        anime_data_jikan=anime_data_jikan, 
        anime_data_anilist=anime_data_anilist,
        anime_data_kitsu=anime_data_kitsu
    )


if __name__ == "__main__":
    # Ejecuta la aplicación en modo debug (solo para desarrollo)
    app.run(debug=True)