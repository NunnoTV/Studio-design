import os
import base64
from dotenv import load_dotenv
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/estilizar", methods=["POST"])
def estilizar_imagem():

    if "image" not in request.files:
        return jsonify({"error": "Campo 'image' é obrigatório (arquivo)."}), 400

    image_file = request.files["image"]
    prompt = request.form.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Campo 'prompt' é obrigatório (texto)."}), 400

    try:
        # 🔥 CONVERSÃO ESSENCIAL
        # O SDK NÃO ACEITA FileStorage direto!
        # Formato correto: tuple (nome, stream ou bytes)
        uploaded_image = ("input.png", image_file.stream)

        result = client.images.edit(
            model="gpt-image-1",
            image=uploaded_image,   # AGORA SIM!
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