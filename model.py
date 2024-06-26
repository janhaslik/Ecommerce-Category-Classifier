import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from tqdm import tqdm
import numpy as np
import pandas as pd

class Classifier:
    def __init__(self, data=None, model_name='model', epochs=3, batch_size=32, learning_rate=2e-5):
        self.data = data
        self.model_name = model_name
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
        self.model = None
        self.optimizer = None
        self.train_loader = None
        self.val_loader = None
        self.label_encoder = LabelEncoder()

    def load_data(self):
        tokenized_dataset = self.tokenize(self.data)

        input_ids = tokenized_dataset['input_ids']
        attention_mask = tokenized_dataset['attention_mask']
        labels = self.label_encoder.fit_transform(self.data['category'])

        train_inputs, val_inputs, train_masks, val_masks, train_labels, val_labels = (
            train_test_split(input_ids, attention_mask, labels, test_size=0.2, random_state=42))

        self.train_inputs = torch.tensor(train_inputs, device=self.device)
        self.train_masks = torch.tensor(train_masks, device=self.device)
        self.train_labels = torch.tensor(train_labels, dtype=torch.long, device=self.device)
        self.val_inputs = torch.tensor(val_inputs, device=self.device)
        self.val_masks = torch.tensor(val_masks, device=self.device)
        self.val_labels = torch.tensor(val_labels, dtype=torch.long, device=self.device)

        self.train_dataset = TensorDataset(self.train_inputs, self.train_masks, self.train_labels)
        self.val_dataset = TensorDataset(self.val_inputs, self.val_masks, self.val_labels)

        self.train_loader = DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)
        self.val_loader = DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=False)

        self.model = AutoModelForSequenceClassification.from_pretrained('bert-base-cased', num_labels=len(self.label_encoder.classes_))
        self.model.to(self.device)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.learning_rate)

    def clean_text(self, text):
        text = text.lower()  # Example: convert to lowercase
        return text

    def tokenize(self, text_data):
        texts = text_data['text'].tolist()
        tokenized = self.tokenizer(texts, truncation=True, padding=True, max_length=128)
        return tokenized

    def train(self):
        for epoch in range(self.epochs):
            # Training
            self.model.train()
            train_loss = 0.0

            for batch in tqdm(self.train_loader, desc=f'Epoch {epoch + 1}/{self.epochs}'):
                batch = tuple(t.to(self.device) for t in batch)
                inputs, masks, labels = batch

                self.optimizer.zero_grad()
                outputs = self.model(inputs, attention_mask=masks, labels=labels)
                loss = outputs.loss
                train_loss += loss.item()

                loss.backward()
                self.optimizer.step()

            avg_train_loss = train_loss / len(self.train_loader)
            print(f'Train Loss: {avg_train_loss:.4f}')

            # Validation
            self.model.eval()
            val_loss = 0.0
            val_preds = []
            val_true = []

            with torch.no_grad():
                for batch in tqdm(self.val_loader, desc=f'Validation'):
                    batch = tuple(t.to(self.device) for t in batch)
                    inputs, masks, labels = batch

                    outputs = self.model(inputs, attention_mask=masks, labels=labels)
                    logits = outputs.logits
                    loss = outputs.loss
                    val_loss += loss.item()

                    preds = torch.argmax(logits, dim=1)
                    val_preds.extend(preds.cpu().detach().numpy())
                    val_true.extend(labels.cpu().detach().numpy())

            avg_val_loss = val_loss / len(self.val_loader)
            val_accuracy = accuracy_score(val_true, val_preds)

            print(f'Validation Loss: {avg_val_loss:.4f}')
            print(f'Validation Accuracy {val_accuracy:.4f}')

    def save_model(self):
        torch.save(self.model.state_dict(), f"{self.model_name}.pt")

    def load_model(self):
        self.model = AutoModelForSequenceClassification.from_pretrained('bert-base-cased', num_labels=len(self.label_encoder.classes_))
        self.model.load_state_dict(torch.load(f"{self.model_name}.pt"))
        self.model.to(self.device)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.learning_rate)

    def fine_tune(self, feedback_data):
        tokenized_dataset = self.tokenize(feedback_data)

        input_ids = tokenized_dataset['input_ids']
        attention_mask = tokenized_dataset['attention_mask']
        labels = self.label_encoder.transform(feedback_data['category'])

        inputs = torch.tensor(input_ids, device=self.device)
        masks = torch.tensor(attention_mask, device=self.device)
        labels = torch.tensor(labels, dtype=torch.long, device=self.device)

        dataset = TensorDataset(inputs, masks, labels)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model.train()
        for epoch in range(1):  # Fine-tune for 1 epoch with feedback data
            feedback_loss = 0.0

            for batch in tqdm(loader, desc='Fine-tuning with feedback'):
                batch = tuple(t.to(self.device) for t in batch)
                inputs, masks, labels = batch

                self.optimizer.zero_grad()
                outputs = self.model(inputs, attention_mask=masks, labels=labels)
                loss = outputs.loss
                feedback_loss += loss.item()

                loss.backward()
                self.optimizer.step()

            avg_feedback_loss = feedback_loss / len(loader)
            print(f'Feedback Training Loss: {avg_feedback_loss:.4f}')

        torch.save(self.model.state_dict(), f"{self.model_name}.pt")
