from flask import Flask, jsonify, request, send_file
from pathlib import Path
from sanic.log import logger
import os
import uuid

from src.converter import convert_pth_to_onnx

app = Flask(__name__)

# Ensure the directory exists
os.makedirs("tmp", exist_ok=True)

@app.route("/convert", methods=['POST'])
def convert():
    try:
        input_file = request.files['file']
        tmp_input_dir = os.path.join("tmp", "input_models")
        os.makedirs(tmp_input_dir, exist_ok=True)
        tmp_output_dir = os.path.join("tmp", "output_models")
        os.makedirs(tmp_output_dir, exist_ok=True)

        tmp_input_path = os.path.join(tmp_input_dir, input_file.filename)
        tmp_output_path = os.path.join(tmp_output_dir, str(uuid.uuid4()))

        input_file.save(tmp_input_path)
        convert_pth_to_onnx(tmp_input_path, tmp_output_path)
        
        # Return the file as a response
        return send_file(
            os.path.abspath(tmp_output_path),
            as_attachment=True,
            download_name=os.path.splitext(input_file.filename) + ".onnx")
    except Exception as e:
        logger.exception(e)
        return jsonify({'error': str(e)})