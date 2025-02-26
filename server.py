from flask import Flask, request, jsonify
import scraper

app = Flask(__name__)

def validate(data):
    if not data.get("url") and not data.get("day") and not data.get("month") and data.get("name"):
        return False
    return True

@app.route("/", methods=['POST'])
def run():
    try:
        data = request.get_json()  # Retrieve JSON data from request
        if not validate(data):
            return jsonify({"error": "Invalid data"}), 400

        auction_data = scraper.builder(data)
        return jsonify(auction_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ping", methods=['GET'])
def ping():
    return jsonify("pong")

if __name__ == '__main__':
    app.run(debug=True)