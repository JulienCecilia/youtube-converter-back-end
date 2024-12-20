# # app.py
# from flask import Flask, request, jsonify, send_file
# import os
# import yt_dlp
# from flask_cors import CORS


# app = Flask(__name__)
# CORS(app)  # Active CORS pour toutes les routes et tous les domaines


# @app.route('/convert', methods=['POST'])
# def convert_video():
#     try:
#         # Récupérer l'URL depuis la requête
#         data = request.json
#         youtube_url = data['url']
        
#         # Créer un chemin temporaire pour stocker le fichier
#         # download_path = "downloads"
#         # os.makedirs(download_path, exist_ok=True)
        
#         # Chemin vers le dossier Téléchargements
#         # DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
#         DOWNLOAD_FOLDER = "/tmp"

#         os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Crée le dossier s'il n'existe pas
        
#         # Télécharger et convertir en MP3
#         ydl_opts = {
#             'format': 'bestaudio/best',
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }],
#             'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
#         }
        
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(youtube_url, download=True)
#             file_path = f"{DOWNLOAD_FOLDER}/{info['title']}.mp3"
        
#         # Retourner le fichier MP3
#         return send_file(file_path, as_attachment=True)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# # if __name__ == "__main__":
# #     app.run(debug=True)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)



# app.py
from flask import Flask, request, jsonify, send_file
import os
import yt_dlp
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Active CORS pour permettre les requêtes cross-origin

# Chemin temporaire pour les téléchargements (utilisé sur Heroku ou localement)
DOWNLOAD_FOLDER = "/tmp"

# Crée le dossier temporaire s'il n'existe pas déjà
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)


@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert_video():
    if request.method == 'OPTIONS':
        # Réponse pour les requêtes préliminaires CORS
        response = app.response_class()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200

    # Logique existante pour la conversion
    try:
        logging.debug(f"Requête reçue : {request.json}")
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL manquante dans la requête."}), 400
        
        youtube_url = data['url']

        # Options de téléchargement et conversion avec yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Modèle de fichier de sortie
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            file_title = info.get('title', 'audio')
            file_path = f"{DOWNLOAD_FOLDER}/{file_title}.mp3"

        if not os.path.exists(file_path):
            return jsonify({"error": "Le fichier MP3 n'a pas pu être généré."}), 500

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Une erreur est survenue : {str(e)}"}), 500


if __name__ == "__main__":
    # Récupérer le port défini par Heroku ou utiliser 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
