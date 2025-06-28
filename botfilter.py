import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# --- Constants ---
DATASET_FILE = 'assets/bot_training_data.csv'
MODEL_FILE = 'assets/bot_intent_model.joblib'
VECTORIZER_FILE = 'assets/bot_intent_vectorizer.joblib'

def train_model():
    """
    Loads the dataset, trains a machine learning model, evaluates it,
    and saves the trained model and vectorizer to disk.
    """
    print("--- Starting Model Training ---")

    # 1. Load Data
    if not os.path.exists(DATASET_FILE):
        print(f"Error: Dataset file not found at '{DATASET_FILE}'")
        print("Please create the CSV file with 'text,intent' columns.")
        return
        
    df = pd.read_csv(DATASET_FILE)
    print(f"Loaded {len(df)} records from {DATASET_FILE}")

    X = df['text']
    y = df['intent']

    # 2. Split Data into Training and Testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Data split into {len(X_train)} training and {len(X_test)} testing samples.")

    # 3. Create a Scikit-learn Pipeline
    # The pipeline will automatically handle vectorizing the text and then training the model.
    # CountVectorizer: Converts text into a matrix of token counts.
    # LogisticRegression: A simple, fast, and effective linear classifier.
    pipeline = Pipeline([
        ('vectorizer', CountVectorizer(stop_words='english', ngram_range=(1, 2))),
        ('classifier', LogisticRegression(random_state=42))
    ])

    # 4. Train the Model
    print("Training the model...")
    pipeline.fit(X_train, y_train)
    print("Training complete.")

    # 5. Evaluate the Model
    print("\n--- Evaluating Model Performance ---")
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # 6. Save the pipeline (model + vectorizer)
    joblib.dump(pipeline, MODEL_FILE)
    print(f"\nModel pipeline saved to '{MODEL_FILE}'")
    print("You can now use the 'predict_intent' function.")
    

class IntentPredictor:
    """
    A class to load the saved model and make predictions.
    This avoids loading the model from disk on every single prediction.
    """
    def __init__(self, model_path=MODEL_FILE):
        self.pipeline = None
        if os.path.exists(model_path):
            print(f"Loading model from {model_path}...")
            self.pipeline = joblib.load(model_path)
            print("Model loaded successfully.")
        else:
            print(f"Warning: Model file not found at {model_path}.")
            print("Please run `train_model()` first.")

    def predict(self, text: str) -> int:
        """
        Predicts the intent of a single text message.

        Args:
            text: The message content from Discord.

        Returns:
            1 if the bot should reply, 0 otherwise.
            Returns -1 if the model is not loaded.
        """
        if self.pipeline is None:
            return -1 # Indicate model not loaded

        # The input must be an iterable (like a list)
        prediction = self.pipeline.predict([text])
        return prediction[0]

# --- Main Execution ---
if __name__ == "__main__":
    
    # STEP 1: Train the model. You only need to do this once, or whenever you update your dataset.
    # Comment this out after the first run if you don't want to retrain every time.
    train_model()
    
    print("\n" + "="*50)
    print("--- Running Predictions on New Messages ---")
    print("="*50)

    # STEP 2: Use the trained model for prediction.
    # In your actual bot, you would initialize this predictor once when the bot starts.
    predictor = IntentPredictor()

    if predictor.pipeline:
        # --- Test Cases ---
        test_messages = [
            "bot can you help me?", # Expected: 1
            "I was talking about rainbowdash earlier", # Expected: 0
            "hey what's up?", # Expected: 0
            "I have a question for the bot", # Expected: 1
            "is the bot online?", # Expected: 0 (or 1 depending on training nuance)
            "Dash, play some music", # Expected: 1
            "that bot is really cool @user123" # Expected: 0
        ]

        for msg in test_messages:
            intent = predictor.predict(msg)
            decision = "REPLY" if intent == 1 else "IGNORE"
            print(f"Message: \"{msg}\" -> Predicted Intent: {intent} ({decision})")
