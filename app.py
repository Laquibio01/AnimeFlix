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

# Función para obtener un GIF de Giphy API
def get_giphy_gif(anime_name):
    giphy_url = f"https://api.giphy.com/v1/gifs/search?api_key=YOUR_GIPHY_API_KEY&q={anime_name}&limit=1"
    response = requests.get(giphy_url)
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["images"]["original"]["url"]
    return None

# Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    anime_data_jikan = None
    anime_data_anilist = None
    giphy_url = None

    if request.method == "POST":
        anime_name = request.form.get("anime_name")
        
        # Obtener datos de las APIs
        anime_data_jikan = get_anime_info_jikan(anime_name)
        anime_data_anilist = get_anime_info_anilist(anime_name)
        giphy_url = get_giphy_gif(anime_name)

    return render_template("index.html", anime_data_jikan=anime_data_jikan, anime_data_anilist=anime_data_anilist, giphy_url=giphy_url)


if __name__ == "__main__":
    app.run(debug=True)
