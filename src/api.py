from enum import Enum
import logging
from flask import Flask, Response, jsonify, request, send_file
import os
import uuid
import base64

from spandrel.__helpers.registry import UnsupportedModelError

from src.AppPlatform import AppPlatform
from src.LicenseData import PlayStoreLicenseData, SteamLicenseData
from src.LicenseValidator import LicenseValidator

from .converter import BlacklistedModelArchError, convert_pth_to_onnx

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

    license_validator = LicenseValidator()

    @app.route("/pthToOnnx", methods=['POST'])
    def pthToOnnx():
        app_platform = AppPlatform.from_value(request.headers.get("App-Platform"))
        
        if app_platform == AppPlatform.Android:
            response_data = request.form.get("responseData")
            signature = request.form.get("signature")            
            license_data = PlayStoreLicenseData(response_data, signature)
        elif app_platform == AppPlatform.Desktop:
            try:
                auth_ticket = base64.b64decode(request.form.get("steamAuthTicket"))
            except Exception as e:
                auth_ticket = None
            
            license_data = SteamLicenseData(auth_ticket)
        else:
            return api_error(ApiErrorReason.INVALID_LICENSE)
        
        if isinstance(license_data, SteamLicenseData):
            if license_validator.validate_steam_license(license_data) == False:
                return api_error(ApiErrorReason.INVALID_LICENSE)
        elif isinstance(license_data, PlayStoreLicenseData):
            if license_validator.validate_play_store_license(license_data) == False:
                return api_error(ApiErrorReason.INVALID_LICENSE)
        else:
            raise TypeError("Unsupported license_data type", license_data)

        input_file = request.files['file']
        tmp_input_dir = os.path.join("tmp", "input_models")
        os.makedirs(tmp_input_dir, exist_ok=True)
        tmp_output_dir = os.path.join("tmp", "output_models")
        os.makedirs(tmp_output_dir, exist_ok=True)
        
        request_id = str(uuid.uuid4())
        input_file_ext = os.path.splitext(input_file.filename)[1]
        if input_file_ext == "":
            input_file_ext = ".pth"
        tmp_input_path = os.path.join(tmp_input_dir, request_id + input_file_ext)
        tmp_output_path = os.path.join(tmp_output_dir, request_id + ".onnx")

        try:
            input_file.save(tmp_input_path)
            convert_pth_to_onnx(tmp_input_path, tmp_output_path)
            
            # Return the file as a response
            return send_file(
                os.path.abspath(tmp_output_path),
                as_attachment=True,
                download_name=os.path.splitext(input_file.filename)[0] + ".onnx")
        except (BlacklistedModelArchError, UnsupportedModelError) as e:
            return api_error(ApiErrorReason.UNSUPPORTED_ARCH)
        except ValueError as e:
            return api_error(ApiErrorReason.UNSUPPORTED_FORMAT)
        finally:
            if os.path.isfile(tmp_input_path):
                os.remove(tmp_input_path)
            if os.path.isfile(tmp_output_path):
                os.remove(tmp_output_path)
    
    return app
