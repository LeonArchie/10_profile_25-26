from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

@app.route('/uuid/generate', methods=['GET'])
def generate():
    return jsonify({"uuid": str(uuid.uuid4()), "version": 4}), 200

@app.route('/uuid/batch/<int:count>', methods=['GET'])
def batch(count: int):
    uuids = []
    for i in range(count):
        uuids.append(str(uuid.uuid4()))
    return jsonify({"uuids": uuids, "count": count}), 200

@app.route('/uuid/validate', methods=['GET'])
def validate():
    try:
        input_uuid = request.args.get("uuid", None)
        uuid_obj = uuid.UUID(input_uuid)
        version = int(uuid_obj.version)

        return jsonify({"valid": version != 0, "version": version}), 200
    except:
        return jsonify({"valid": False, "version": 0}), 200

@app.route('/uuid/versions', methods=['GET'])
def versions():
    return jsonify({"versions": [1, 4]}), 200

@app.route('/uuid/convert', methods=['POST'])
def convert():
    input_dict = request.get_json()
    
    input_uuid = uuid.UUID(input_dict["uuid"])
    format = input_dict["format"]
    output_uuid = ""

    if format == "standard":
        output_uuid = str(input_uuid)
    elif format == "hex":
        output_uuid = input_uuid.hex
    elif format == "urn":
        output_uuid = input_uuid.urn
    else:
        return jsonify({"error": "wrong format"}), 400
    
    return jsonify({"original": input_dict["uuid"], "converted": output_uuid}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": True}), 200

@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "healthy"}), 200

@app.route('/readyz', methods=['GET'])
def readyz():
    return jsonify({"status": "ready"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
