import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

class CarPricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = None
        
    def prepare_data(self, df):
        """Prepare and preprocess the data"""
        # Select relevant features
        features = ['brand', 'model', 'year', 'mileage', 'fuel_type', 'transmission', 'engine_size', 'horsepower']
        
        # Handle categorical variables
        categorical_cols = ['brand', 'model', 'fuel_type', 'transmission']
        
        for col in categorical_cols:
            if col in df.columns:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
        
        return df[features], df['price']
    
    def train(self, df):
        """Train the Random Forest model"""
        X, y = self.prepare_data(df)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest Regressor
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        accuracy = r2 * 100
        
        # Feature importance
        self.feature_importance = dict(zip(X.columns, self.model.feature_importances_))
        
        return mae, r2, accuracy
    
    def predict(self, car_features):
        """Predict car price for new data"""
        if self.model is None:
            raise Exception("Model not trained. Please train the model first.")
        
        # Prepare input features
        input_df = pd.DataFrame([car_features])
        
        # Encode categorical variables
        for col in ['brand', 'model', 'fuel_type', 'transmission']:
            if col in input_df.columns and col in self.label_encoders:
                try:
                    input_df[col] = self.label_encoders[col].transform([str(car_features[col])])[0]
                except ValueError:
                    # Handle unseen labels
                    input_df[col] = 0
        
        # Scale features
        input_scaled = self.scaler.transform(input_df)
        
        # Make prediction
        prediction = self.model.predict(input_scaled)[0]
        
        return max(0, prediction)  # Ensure non-negative price
    
    def save_model(self, filepath):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath):
        """Load a trained model"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_importance = model_data['feature_importance']
            return True
        return False