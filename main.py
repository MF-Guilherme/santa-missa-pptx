import requests, os

api_key_vagalume = os.getenv("KEY_VAGALUME")
api_key_musixmatch = os.getenv("KEY_MUSIXMATCH")

def get_playlist():
    with open('musicas.csv', "r") as file:
        playlist = []
        for music in file:
            music = music.strip("\n")
            music_name, artist_name = music.split(", ")
            playlist.append((music_name, artist_name))
        return playlist

def find_lyrics(playlist):
    for music in playlist:
        url = f"https://api.vagalume.com.br/search.php?art={music[1]}&mus={music[0]}&apikey={api_key_vagalume}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'mus' in data:
                music_id = data['mus'][0]['id']
                letra = data['mus'][0]['text']
                with open("lista_com_id.txt", "r") as lista_id:
                    content = lista_id.read()
                if music_id not in content:
                    with open("lista_com_id.txt", "a") as id_list:
                        id_list.write(f"{music[0]}, {music[1]}, {music_id}\n")
            else:
                print("Letra não encontrada.")
        else:
            print("Erro ao fazer requisição.")

playlist = get_playlist()
find_lyrics(playlist)

