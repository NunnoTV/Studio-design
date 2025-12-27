import os
import base64
import uuid

import requests
from dotenv import load_dotenv

from flask import Flask, request, jsonify, url_for, send_from_directory
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route('/temp_image/<filename>')
def serve_temp_image(filename):
    # Rota para servir imagens salvas no diretório temporário (necessário para Vercel/Serverless)
    import tempfile
    return send_from_directory(tempfile.gettempdir(), filename)

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
        
        print(f"DEBUG RESPONSE: {result}") # Log para debug no terminal

        # Verifica se veio URL ou B64 (alguns proxies podem mandar b64 sem pedir)
        image_data_out = None
        
        if hasattr(result.data[0], 'url') and result.data[0].url:
            # Baixar a imagem gerada da URL remota
            response_img = requests.get(result.data[0].url)
            if response_img.status_code == 200:
                image_data_out = response_img.content
        elif hasattr(result.data[0], 'b64_json') and result.data[0].b64_json:
             image_data_out = base64.b64decode(result.data[0].b64_json)
        
        if not image_data_out:
             return jsonify({"error": "A API não retornou URL nem Base64 da imagem.", "debug": str(result)}), 500

        # Gerar nome único para o arquivo
        filename = f"generated_{uuid.uuid4().hex}.png"
        
        # Usar diretório temporário do sistema (compatível com Vercel/Read-only FS)
        import tempfile
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        # Salvar a imagem
        with open(filepath, "wb") as f:
            f.write(image_data_out)

        # Gerar URL temporária local apontando para a nova rota
        image_url = url_for('serve_temp_image', filename=filename, _external=True)

        return jsonify({"url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)