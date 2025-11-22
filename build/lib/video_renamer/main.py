import math
import os
import re
import sys
import ffmpeg
from datetime import datetime

def resolution_label(width, height):
    resolutions = {
        4320: '8K',
        2880: '5_3K',
        2160: '4K',
        1440: '2_5K',
        1080: 'FullHD',
        720: 'HD',
        480: 'SD'
    }
    vertical = min(width, height)
    chosen_res = None
    for res in sorted(resolutions.keys(), reverse=True):
        if vertical >= res:
            chosen_res = resolutions[res]
            break
    if chosen_res is None:
        chosen_res = f'Unknown({width}x{height})'
    return chosen_res

def extraire_date_video(metadonnees):
    # D'abord dans 'format'
    creation_time = metadonnees.get('format', {}).get('tags', {}).get('creation_time', None)
    # Sinon on cherche dans chaque stream
    if not creation_time:
        for stream in metadonnees['streams']:
            creation_time = stream.get('tags', {}).get('creation_time', None)
            if creation_time:
                break
    return creation_time


def renommer_video(file_video):
    try:
        metadonnees = ffmpeg.probe(file_video)
        creation_time = extraire_date_video(metadonnees)
        if creation_time:
            # Ex : 2023-09-30T14:35:02.000000Z
            dt = datetime.strptime(creation_time[:16], "%Y-%m-%dT%H:%M")
            date_str = dt.strftime('%Y%m%d-%H%M')
        else:
            # fallback : date de maintenant
            dt = datetime.now()
            date_str = dt.strftime('%Y%m%d-%H%M')

        video_stream = next((s for s in metadonnees['streams'] if s['codec_type'] == 'video'), None)
        if video_stream:
            fps_str = video_stream.get('r_frame_rate', '0/1')
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den != 0 else 0
            fps_arrondi = math.ceil(fps / 10) * 10
            display_aspect_ratio = video_stream.get('display_aspect_ratio', 'N/A')
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
            resolution = resolution_label(width, height)

            ext = os.path.splitext(file_video)[1]
            newname = f"{date_str}-{fps_arrondi}-{display_aspect_ratio}-{resolution}{ext}"
            newpath = os.path.join(os.path.dirname(file_video), newname)

            os.rename(file_video, newpath)
            print(f"{os.path.basename(file_video)} -> {os.path.basename(newpath)}")
        else:
            print(f"{os.path.basename(file_video)}\tPas de flux vidéo.")
    except ffmpeg.Error as e:
        print(f"{os.path.basename(file_video)}\tErreur lecture metadata: {e}")

def nom_commence_par_date(filename):
    # Match JJMMYYYY en début de nom, ex : 22112025...
    return re.match(r'^\d{8}', filename) is not None

def traiter_dossier(folder):
    extensions_video = ['.mp4', '.mov', '.avi', '.mkv']
    for entry in os.scandir(folder):
        if entry.is_file() and os.path.splitext(entry.name)[1].lower() in extensions_video:
            if not nom_commence_par_date(entry.name):
                renommer_video(entry.path)
            else:
                print(f"{entry.name} : déjà renommé avec le bon format, ignoré")

def main():
    if len(sys.argv) < 2:
        print("Usage : python script.py <dossier_video>")
        sys.exit(1)
    folder_name = sys.argv[1]
    if not os.path.isdir(folder_name):
        print(f"Le chemin {folder_name} n'est pas un dossier valide.")
        sys.exit(1)
    traiter_dossier(folder_name)