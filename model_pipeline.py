"""
INDEPENDENT SCRIPT OF THE FLASK APP, FINE TUNES THE MODEL PERIODICALLY
"""

import os

import db
import numpy as np
import pandas as pd
from model import Classifier


def combine_data():
    # Load and Clean the Dataset
    default_dataset = pd.read_csv('ecommerceDataset.csv', names=['category', 'text'], header=None)
    default_dataset = default_dataset.dropna().drop_duplicates()

    # Text Cleaning
    def clean_text(text):
        text = text.lower()  # Example: convert to lowercase
        return text

    default_dataset['text'] = default_dataset['text'].apply(clean_text)

    # Get feedback data from DB
    feedback_data = db.get_feedback_for_finetuning()
    if feedback_data == 500 or len(feedback_data) == 0:
        return default_dataset

    # Create Data Frame from feedback data
    feedback_data = np.array(feedback_data)
    feedback_data = pd.DataFrame(feedback_data, columns=['f_input_text', 'f_c_feedback_category'])

    # Merge Dataset + Feedback
    data = pd.concat([default_dataset, feedback_data[['f_c_feedback_category', 'f_input_text']].rename(columns={'f_c_feedback_category': 'category', 'f_input_text': 'text'})], axis=0, ignore_index=True)
    return data


def finetune_model():
    data = combine_data()
    model_name = "model"

    model = Classifier(data=data)

    if not os.path.exists(f"{model_name}.pt"):
        model.load_data()
        model.train()
        model.save_model()
    else:
        model.load_data()
        model.load_model()

    # Fine-tune with new feedback
    feedback_data = db.get_feedback_for_finetuning()
    if feedback_data != 500 and len(feedback_data) != 0:
        feedback_data = np.array(feedback_data)
        feedback_data = pd.DataFrame(feedback_data, columns=['f_input_text', 'f_c_feedback_category'])
        feedback_data = feedback_data.rename(columns={'f_c_feedback_category': 'category', 'f_input_text': 'text'})
        feedback_data['text'] = feedback_data['text'].apply(model.clean_text)

        model.fine_tune(feedback_data)
        db.log_finetune()
        db.delete_feedback_finetune()


def scheduler():
    finetune_model()


scheduler()