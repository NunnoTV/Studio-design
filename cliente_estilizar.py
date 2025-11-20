import requests

# URL da sua API Flask
API_URL = "http://localhost:5000/estilizar"   # coloque a URL do seu servidor em produção aqui

def estilizar_imagem(caminho_imagem, prompt, caminho_saida="resultado.png"):
    """
    Envia uma imagem + prompt para a API e salva a imagem estilizada no disco.
    """

    # Prepara o envio multipart/form-data
    files = {
        "image": open(caminho_imagem, "rb")  # arquivo da imagem
    }

    data = {
        "prompt": prompt
    }

    # Faz a requisição POST
    response = requests.post(API_URL, files=files, data=data)

    # Verifica erro
    if response.status_code != 200:
        print("Erro ao estilizar imagem:", response.text)
        return

    # Salva a imagem retornada
    with open(caminho_saida, "wb") as f:
        f.write(response.content)

    print(f"Imagem estilizada salva em: {caminho_saida}")


if __name__ == "__main__":
    # Exemplo de uso
    prompt = (
        "Transforme essa pessoa em uma caricatura estilo chibi / cute cartoon, "
        "cabeça grande, corpo pequeno, olhos grandes brilhantes e cores pastéis."
    )

    estilizar_imagem(
        caminho_imagem="minha_foto.jpg",
        prompt=prompt,
        caminho_saida="minha_foto_chibi.png"
    )
