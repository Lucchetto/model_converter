from flask import Flask, jsonify, request, send_file
from sanic.log import logger
import os
import uuid

from .converter import convert_pth_to_onnx

app = Flask(__name__)

# Ensure the directory exists
os.makedirs("tmp", exist_ok=True)

@app.errorhandler(ValueError)
def handle_convert_error(error):
    logger.exception(error)
    if "is unsupported by chaiNNer. Please try another" in str(error):
        reason = "UNSUPPORTED_FORMAT"
    else:
        reason = "UNKNOWN"

    return jsonify({"reason": reason}), 400

@app.route("/pthToOnnx", methods=['POST'])
def pthToOnnx():
    input_file = request.files['file']
    tmp_input_dir = os.path.join("tmp", "input_models")
    os.makedirs(tmp_input_dir, exist_ok=True)
    tmp_output_dir = os.path.join("tmp", "output_models")
    os.makedirs(tmp_output_dir, exist_ok=True)
    
    request_id = str(uuid.uuid4())
    tmp_input_path = os.path.join(tmp_input_dir, request_id + ".pth")
    tmp_output_path = os.path.join(tmp_output_dir, request_id + ".onnx")

    try:
        input_file.save(tmp_input_path)
        convert_pth_to_onnx(tmp_input_path, tmp_output_path)
        
        # Return the file as a response
        return send_file(
            os.path.abspath(tmp_output_path),
            as_attachment=True,
            download_name=os.path.splitext(input_file.filename)[0] + ".onnx")
    finally:
        if os.path.isfile(tmp_input_path):
            os.remove(tmp_input_path)
        if os.path.isfile(tmp_output_path):
            os.remove(tmp_output_path)
