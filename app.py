from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Función para obtener información de anime de Jikan API
def get_anime_info_jikan(anime_name):
    jikan_url = f"https://api.jikan.moe/v4/anime?q={anime_name}&sfw"
    response = requests.get(jikan_url)
    if response.status_code == 200:
        return response.json()["data"]
    return None

# Función para obtener información de anime de AniList API
def get_anime_info_anilist(anime_name):
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

# Función para obtener información de anime de Kitsu API
def get_anime_info_kitsu(anime_name):
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

# Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
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
    app.run(debug=True)