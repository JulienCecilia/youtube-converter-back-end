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


@app.route('/convert', methods=['POST', 'GET'])
def convert_video():
    if request.method == 'GET':
        return jsonify({"message": "Utilisez POST pour soumettre des données."})

    try:
        # Récupérer l'URL depuis la requête
        logging.debug(f"Requête reçue : {request.json}")
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL manquante dans la requête."}), 400
        
        youtube_url = data['url']

        # Options pour yt-dlp avec cookies
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Modèle de fichier de sortie
            'cookiefile': 'cookies.txt',  # Utilise le fichier cookies.txt si disponible
        }

        # Téléchargement et conversion avec yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            file_title = info.get('title', 'audio')
            file_path = f"{DOWNLOAD_FOLDER}/{file_title}.mp3"

        # Vérification si le fichier a été correctement créé
        if not os.path.exists(file_path):
            return jsonify({"error": "Le fichier MP3 n'a pas pu être généré."}), 500

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logging.error(f"Erreur lors de la conversion : {str(e)}")
        return jsonify({"error": f"Une erreur est survenue : {str(e)}"}), 500


if __name__ == "__main__":
    # Récupérer le port défini par Heroku ou utiliser 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
