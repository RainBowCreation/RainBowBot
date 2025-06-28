import joblib
from flask import Flask, request, jsonify
import os

# --- Constants ---
MODEL_FILE = 'assets/bot_intent_model.joblib'

# --- Initialize Flask App and Predictor ---
app = Flask(__name__)
predictor = None

# --- Load the Model ---
def load_model():
    """Load the pipeline from disk."""
    global predictor
    if os.path.exists(MODEL_FILE):
        print(f"Loading model from {MODEL_FILE}...")
        predictor = joblib.load(MODEL_FILE)
        print("Model loaded successfully.")
    else:
        print(f"FATAL: Model file not found at {MODEL_FILE}")
        print("Please make sure the model is trained and the file is in the same directory.")
        predictor = None

# --- API Endpoint ---
@app.route('/predict', methods=['POST'])
def predict_intent():
    """
    Receives a text message and returns the predicted intent.
    Expects a JSON payload like: {"text": "your message here"}
    """
    if predictor is None:
        return jsonify({'error': 'Model not loaded'}), 500

    # Get JSON data from the request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input. JSON with a "text" key is required.'}), 400

    text_to_predict = data['text']

    # Make prediction using the loaded pipeline
    try:
        prediction = predictor.predict([text_to_predict])
        # The prediction is a numpy array, so we get the first element
        intent = int(prediction[0])
        print(f"Received: '{text_to_predict}' -> Predicted: {intent}")
        return jsonify({'intent': intent})
    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return jsonify({'error': 'Failed to make a prediction.'}), 500

# --- Main Execution ---
if __name__ == '__main__':
    # Load the model once when the server starts
    load_model()
    # Run the Flask app
    # Host '0.0.0.0' makes it accessible from other devices on your network, including Node-RED
    app.run(host='0.0.0.0', port=5000, debug=True)