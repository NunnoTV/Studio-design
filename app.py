import os
import base64
import requests
from dotenv import load_dotenv
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/estilizar", methods=["POST"])
def estilizar_imagem():

    # Verifica se foi enviado arquivo OU url
    image_file = request.files.get("image")
    image_url = request.form.get("image_url") or (request.json and request.json.get("image_url"))

    if not image_file and not image_url:
        return jsonify({"error": "É obrigatório enviar 'image' (arquivo) ou 'image_url' (link)."}), 400

    prompt = request.form.get("prompt") or (request.json and request.json.get("prompt"))
    
    if not prompt:
         return jsonify({"error": "Campo 'prompt' é obrigatório (texto)."}), 400
    
    prompt = prompt.strip()

    try:
        image_data = None
        
        if image_file:
             image_data = image_file.read()
        elif image_url:
            # Baixar a imagem da URL
            resp = requests.get(image_url)
            resp.raise_for_status()
            image_data = resp.content

        # 🔥 CONVERSÃO ESSENCIAL
        # O SDK NÃO ACEITA FileStorage direto!
        # Formato correto: tuple (nome, stream ou bytes)
        uploaded_image = ("input.png", image_data)

        result = client.images.edit(
            model="gpt-image-1",
            image=uploaded_image, 
            prompt=prompt,
            size="1024x1024",
            n=1
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        return send_file(
            BytesIO(image_bytes),
            mimetype="image/png",
            download_name="imagem_estilizada.png"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)