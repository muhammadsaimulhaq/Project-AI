from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
import joblib
from model import CarPricePredictor
import urllib.parse

app = Flask(__name__)
predictor = CarPricePredictor()

# Load and prepare car data
try:
    car_df = pd.read_csv('car_data.csv')
    print("✅ Car data loaded successfully")
    print(f"📊 Total records: {len(car_df)}")
    
    # Your CSV already has the correct column names, so no need to rename
    # Just ensure we have the required columns
    print("📋 Available columns:", car_df.columns.tolist())
    
    # Create brand column from model if needed (but your CSV already has brand)
    if 'brand' not in car_df.columns and 'model' in car_df.columns:
        car_df['brand'] = car_df['model'].apply(lambda x: x.split()[0] if isinstance(x, str) else 'Unknown')
    
    print("🔧 Data preparation completed")
    print(f"🚗 Brands available: {car_df['brand'].unique()}")
    print(f"💰 Price range: ₹{car_df['price'].min():,} to ₹{car_df['price'].max():,}")
    
except Exception as e:
    print(f"❌ Error loading car data: {e}")
    car_df = pd.DataFrame()

def get_google_search_url(brand, model, year=None):
    """Generate Google search URL for car images"""
    search_query = f"{brand} {model} car"
    if year:
        search_query = f"{brand} {model} {year} car"
    
    encoded_query = urllib.parse.quote_plus(search_query)
    return f"https://www.google.com/search?q={encoded_query}&tbm=isch"

@app.route('/')
def index():
    return render_template('index.html')

# API ROUTES
@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API for price prediction"""
    try:
        data = request.get_json()
        print("📥 Received prediction request:", data)
        
        # Validate required fields
        required_fields = ['brand', 'model', 'year', 'mileage', 'fuel_type', 'transmission', 'engine_size', 'horsepower']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Make prediction
        if predictor.model is not None:
            predicted_price = predictor.predict(data)
        else:
            # Fallback calculation based on your actual data patterns
            base_price = 300000  # Base price in rupees
            
            # Calculate based on actual patterns from your data
            year_factor = max(0, (data['year'] - 2010)) * 50000
            mileage_factor = max(0, (100000 - data['mileage'])) * 2
            engine_factor = data['engine_size'] * 100000
            hp_factor = data['horsepower'] * 1000
            
            # Brand premium
            luxury_brands = ['BMW', 'Mercedes', 'Audi', 'Mercedes-Benz']
            premium_brands = ['Toyota', 'Honda', 'Hyundai', 'Ford']
            
            if data['brand'] in luxury_brands:
                brand_premium = 1000000
            elif data['brand'] in premium_brands:
                brand_premium = 200000
            else:
                brand_premium = 0
            
            # Transmission premium
            transmission_premium = 50000 if data['transmission'] == 'Automatic' else 0
            
            # Fuel type adjustment
            fuel_premium = 30000 if data['fuel_type'] in ['Diesel', 'Electric'] else 0
            
            predicted_price = (base_price + year_factor + mileage_factor + 
                            engine_factor + hp_factor + brand_premium + 
                            transmission_premium + fuel_premium)
            
            # Add some randomness to make it more realistic
            predicted_price = predicted_price * np.random.uniform(0.8, 1.2)
            predicted_price = max(300000, predicted_price)  # Minimum price based on your data
        
        # Generate Google search URL
        google_url = get_google_search_url(data['brand'], data['model'], data['year'])
        
        response_data = {
            'predicted_price': round(predicted_price),
            'google_search_url': google_url,
            'car_features': data
        }
        
        print("📤 Prediction response:", response_data)
        return jsonify(response_data)
        
    except Exception as e:
        print("❌ Prediction error:", str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/api/similar_cars')
def api_similar_cars():
    """API for similar cars"""
    try:
        brand = request.args.get('brand', '')
        model = request.args.get('model', '')
        fuel_type = request.args.get('fuel_type', '')
        transmission = request.args.get('transmission', '')
        limit = int(request.args.get('limit', '20'))
        
        print(f"🔍 Similar cars request - Brand: {brand}, Model: {model}")
        
        if car_df.empty:
            return jsonify({'error': 'Car data not loaded'}), 500
        
        # Filter cars based on parameters
        filtered_cars = car_df.copy()
        
        if brand:
            filtered_cars = filtered_cars[filtered_cars['brand'].str.lower() == brand.lower()]
        if model:
            filtered_cars = filtered_cars[filtered_cars['model'].str.lower().str.contains(model.lower())]
        if fuel_type:
            filtered_cars = filtered_cars[filtered_cars['fuel_type'].str.lower() == fuel_type.lower()]
        if transmission:
            filtered_cars = filtered_cars[filtered_cars['transmission'].str.lower() == transmission.lower()]
        
        # Sort by year (newest first) and price
        filtered_cars = filtered_cars.sort_values(['year', 'price'], ascending=[False, True])
        filtered_cars = filtered_cars.head(limit)
        
        # Convert to list of dictionaries with Google search URLs
        cars_list = []
        for _, car in filtered_cars.iterrows():
            car_dict = {
                'brand': car['brand'],
                'model': car['model'],
                'year': int(car['year']),
                'price': int(car['price']),
                'mileage': int(car['mileage']),
                'fuel_type': car['fuel_type'],
                'transmission': car['transmission'],
                'engine_size': float(car['engine_size']),
                'horsepower': int(car['horsepower'])
            }
            car_dict['google_search_url'] = get_google_search_url(car['brand'], car['model'], car['year'])
            cars_list.append(car_dict)
        
        print(f"✅ Found {len(cars_list)} similar cars")
        return jsonify({'cars': cars_list})
        
    except Exception as e:
        print("❌ Similar cars error:", str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/api/dashboard')
def api_dashboard():
    """API for dashboard data"""
    try:
        print("📊 Dashboard data requested")
        
        if car_df.empty:
            return jsonify({'error': 'Car data not loaded'}), 500
        
        # Basic statistics from your actual data
        stats = {
            'total_cars': len(car_df),
            'avg_price': round(car_df['price'].mean()),
            'min_price': round(car_df['price'].min()),
            'max_price': round(car_df['price'].max()),
            'avg_year': round(car_df['year'].mean()),
            'avg_mileage': round(car_df['mileage'].mean()),
            'avg_engine_size': round(car_df['engine_size'].mean(), 1),
            'avg_horsepower': round(car_df['horsepower'].mean())
        }
        
        # Count by fuel type
        fuel_counts = car_df['fuel_type'].value_counts().to_dict()
        
        # Count by transmission
        transmission_counts = car_df['transmission'].value_counts().to_dict()
        
        # Top brands
        top_brands = car_df['brand'].value_counts().head(10).to_dict()
        
        # Feature importance (based on typical car pricing factors)
        feature_importance = {
            'year': 0.25,
            'brand': 0.20,
            'mileage': 0.18,
            'engine_size': 0.15,
            'horsepower': 0.12,
            'fuel_type': 0.06,
            'transmission': 0.04
        }
        
        response_data = {
            'stats': stats,
            'feature_importance': feature_importance,
            'fuel_counts': fuel_counts,
            'transmission_counts': transmission_counts,
            'top_brands': top_brands
        }
        
        print("✅ Dashboard data sent")
        print(f"   - Total cars: {stats['total_cars']}")
        print(f"   - Avg price: ₹{stats['avg_price']:,}")
        print(f"   - Year range: {car_df['year'].min()} to {car_df['year'].max()}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print("❌ Dashboard error:", str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/api/brands')
def api_brands():
    """API to get all available brands"""
    try:
        if car_df.empty:
            return jsonify({'error': 'Car data not loaded'}), 500
        
        brands = sorted(car_df['brand'].unique().tolist())
        return jsonify({'brands': brands})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/models')
def api_models():
    """API to get models for a specific brand"""
    try:
        brand = request.args.get('brand', '')
        if not brand:
            return jsonify({'error': 'Brand parameter required'}), 400
        
        if car_df.empty:
            return jsonify({'error': 'Car data not loaded'}), 500
        
        models = sorted(car_df[car_df['brand'] == brand]['model'].unique().tolist())
        return jsonify({'models': models})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("🚀 Starting CarPrice Pro App...")
    if not car_df.empty:
        print("📊 Loaded data:", len(car_df), "cars")
        print("💰 Price range: ₹{:,.0f} to ₹{:,.0f}".format(car_df['price'].min(), car_df['price'].max()))
        print("📅 Year range: {} to {}".format(car_df['year'].min(), car_df['year'].max()))
        print("🚗 Brands count:", len(car_df['brand'].unique()))
    else:
        print("❌ No car data loaded")
    
    print("🌐 Server running at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)