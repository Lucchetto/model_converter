from enum import Enum
import logging
from flask import Flask, Response, jsonify, request, send_file
import os
import uuid

from src.licensing import setup_pub_key, validate_license

from .converter import UnsupportedModelArch, convert_pth_to_onnx

class ApiErrorReason(Enum):
    UNSUPPORTED_ARCH = "UNSUPPORTED_ARCH"
    INVALID_LICENSE = 'INVALID_LICENSE'
    UNSUPPORTED_FORMAT = 'UNSUPPORTED_FORMAT'
    UNKNOWN = 'UNKNOWN'

def api_error(reason: ApiErrorReason):
    if reason == ApiErrorReason.INVALID_LICENSE:
        status_code = 401
    else:
        status_code = 400
    return jsonify({"reason": reason.value}), status_code

def create_app():
    logging.basicConfig(level=logging.NOTSET)
    app = Flask(__name__)

    # Ensure the directory exists
    os.makedirs("tmp", exist_ok=True)

    pub_key = setup_pub_key()

    @app.errorhandler(ValueError)
    def handle_convert_error(error):
        if "is unsupported by chaiNNer. Please try another" in str(error):
            reason = ApiErrorReason.UNSUPPORTED_FORMAT
        else:
            reason = ApiErrorReason.UNKNOWN

        return api_error(reason)

    @app.route("/pthToOnnx", methods=['POST'])
    def pthToOnnx():
        if pub_key is not None:
            if not validate_license(pub_key, request.form.get("responseData"), request.form.get("signature")):
                return api_error(ApiErrorReason.INVALID_LICENSE)

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
        except UnsupportedModelArch as e:
            return api_error(ApiErrorReason.UNSUPPORTED_ARCH)
        finally:
            if os.path.isfile(tmp_input_path):
                os.remove(tmp_input_path)
            if os.path.isfile(tmp_output_path):
                os.remove(tmp_output_path)
    
    return app
