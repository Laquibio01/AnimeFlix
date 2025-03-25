from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

ANILIST_API = "https://graphql.anilist.co"
KITSU_API = "https://kitsu.io/api/edge/anime"
GOGOANIME_API = "https://api.consumet.org/anime/gogoanime"

def get_anilist_data(title):
    query = """
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        title {
          romaji
          english
        }
        description
        coverImage {
          large
        }
      }
    }
    """
    variables = {"search": title}
    response = requests.post(ANILIST_API, json={"query": query, "variables": variables})
    return response.json().get("data", {}).get("Media", {})

def get_kitsu_data(title):
    response = requests.get(f"{KITSU_API}?filter[text]={title}")
    return response.json().get("data", [])[0] if response.status_code == 200 else {}

def get_gogoanime_data(title):
    response = requests.get(f"{GOGOANIME_API}/{title}")
    return response.json() if response.status_code == 200 else {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/anime", methods=["GET"])
def get_anime():
    title = request.args.get("title")
    if not title:
        return jsonify({"error": "Debes proporcionar un título de anime."}), 400

    anilist_data = get_anilist_data(title)
    kitsu_data = get_kitsu_data(title)
    gogoanime_data = get_gogoanime_data(title)

    result = {
        "title": anilist_data.get("title", {}).get("romaji", "Desconocido"),
        "description": anilist_data.get("description", "Descripción no disponible"),
        "image": anilist_data.get("coverImage", {}).get("large", ""),
        "sources": {
            "AniList": anilist_data,
            "Kitsu": kitsu_data,
            "GogoAnime": gogoanime_data,
        }
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
