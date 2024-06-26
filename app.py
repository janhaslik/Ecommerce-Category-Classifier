import os

import torch
import pandas as pd
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.preprocessing import LabelEncoder
from flask import Flask, request, jsonify, send_from_directory
import db
import model_pipeline as mp

app = Flask("Ecommerce-Category-Classifier")

# Load the pretrained BERT model and tokenizer
model_path = 'model.pt'  # Replace with your saved model path
tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')

# Load the number of labels
data_pandas = pd.read_csv('ecommerceDataset.csv', names=['category', 'text'], header=None)
label_encoder = LabelEncoder()
label_encoder.fit(data_pandas['category'].unique())
num_labels = len(label_encoder.classes_)

# Load the model with the correct number of labels
model = AutoModelForSequenceClassification.from_pretrained('bert-base-cased', num_labels=num_labels)
model.load_state_dict(torch.load(model_path))
model.eval()

# Debug: Print the number of labels and classes
print(f"Number of labels: {num_labels}")
print(f"Classes: {label_encoder.classes_}")


def clean_text(text):
    text = text.lower()  # Example: convert to lowercase
    return text


# Function to classify input text
def classify_text(input_text):
    # Tokenize input text
    inputs = tokenizer(input_text, return_tensors='pt', truncation=True, padding=True, max_length=128)

    # Inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = F.softmax(logits, dim=1).cpu().numpy()[0]
        predictions = torch.argmax(logits, dim=1).cpu().numpy()

    # Decode predictions
    predicted_label = label_encoder.inverse_transform(predictions)[0]
    class_probabilities = {label_encoder.inverse_transform([i])[0]: prob for i, prob in enumerate(probabilities)}

    return predicted_label, class_probabilities


# ESSENTIAL
@app.route("/api/classify", methods=['POST'])
def classify():
    # Extract request
    text = clean_text(request.json['text'])

    # Classify text
    predicted_category, categories_probabilities = classify_text(text)

    # Insert Request in DB
    predictionid = db.insert_classification_request(input_text=text, predicted_category=predicted_category)

    if predictionid < 0:
        return jsonify({"message": "Error"}), 500

    # Construct result
    result = [{'category': category, 'probability': f'{probability:.2}'}
              for category, probability in categories_probabilities.items()]

    return jsonify({"predictionid": predictionid, 'categories_probabilities': result}), 200


@app.route("/api/feedback/<int:predictionid>", methods=['PATCH'])
def feedback(predictionid):
    try:
        category = request.json['category']
        result = db.insert_feedback(predictionid=predictionid, category=category)
        if result == 200:
            return "OK", 200
        else:
            return "Internal Server Error", 500
    except Exception as e:
        print(f"Error handling feedback request: {e}")
        return "Internal Server Error", 500


# ADDITIONAL NICE TO HAVE FEATURES

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route("/api/feedback", methods=['GET'])
def feedback_get():
    try:
        feedback_data = db.get_feedback()
        result = [{'input_text': f_input_text,
                   'predicted_category': f_c_predicted_category,
                   'feedback_category': f_c_feedback_category}
                  for f_input_text, f_c_predicted_category, f_c_feedback_category in feedback_data]
        if feedback_data == 500:
            return "Internal Server Error", 500
        return jsonify({'feedback': result}), 200
    except Exception as e:
        print(f"Error handling feedback request: {e}")
        return "Internal Server Error", 500


@app.route("/api/finetune", methods=['POST'])
def finetune():
    try:
        mp.finetune_model()
        return "OK", 200
    except Exception as e:
        print(f"Error handling finetune request: {e}")
        return "Internal Server Error", 500


if __name__ == "__main__":
    app.run(port=5000)