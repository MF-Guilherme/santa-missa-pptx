import requests, os

api_key_vagalume = os.getenv("KEY_VAGALUME")
api_key_musixmatch = os.getenv("KEY_MUSIXMATCH")


def buscar_letra(nome_musica, nome_artista):
    url = f"https://api.vagalume.com.br/search.php?art={nome_artista}&mus={nome_musica}&apikey={api_key_vagalume}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'mus' in data:
            id_musica = data['art']['id']
            letra = data['mus'][0]['text']
            print(id_musica)
            return letra
        else:
            return "Letra não encontrada."
    else:
        return "Erro ao fazer requisição."


print(buscar_letra('eu quero ser de Deus', 'Celina Borges'))



