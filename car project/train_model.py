# train_model.py - Complete Training Script (Run once)
import pandas as pd
import numpy as np
from model import CarPricePredictor
import joblib
import os

def generate_sample_data(num_cars=5000):
    np.random.seed(42)  

    brands = ['Toyota', 'Honda', 'Hyundai', 'Maruti', 'BMW', 'Mercedes', 'Audi', 'Ford', 'Tata', 'Mahindra']
    models = {
        'Toyota': ['Camry', 'Corolla', 'Fortuner', 'Innova', 'Swift', 'Civic'],
        'Honda': ['Civic', 'City', 'Accord', 'Swift', 'CR-V'],
        'Hyundai': ['i20', 'Creta', 'Verna', 'Venue'],
        'Maruti': ['Swift', 'Baleno', 'Brezza', 'Dzire', 'Ertiga'],
        'BMW': ['X5', 'X1', '3 Series', '5 Series'],
        'Mercedes': ['C-Class', 'E-Class', 'S-Class', 'GLC'],
        'Audi': ['A4', 'A6', 'Q3', 'Q5'],
        'Ford': ['EcoSport', 'Figo', 'Endeavour'],
        'Tata': ['Nexon', 'Harrier', 'Tiago', 'Safari'],
        'Mahindra': ['Scorpio', 'Thar', 'XUV700', 'XUV300']
    }

    fuel_types = ['Petrol', 'Diesel', 'CNG', 'Electric']
    transmissions = ['Manual', 'Automatic']

    data = []
    for _ in range(num_cars):
        brand = np.random.choice(brands)
        model = np.random.choice(models[brand])
        year = np.random.randint(2010, 2025)
        mileage = np.random.randint(10000, 150000)
        fuel = np.random.choice(fuel_types, p=[0.5, 0.35, 0.1, 0.05])
        transmission = np.random.choice(transmissions, p=[0.45, 0.55])
        engine_size = round(np.random.uniform(1.0, 4.0), 1)
        horsepower = np.random.randint(80, 450)

        
        base_price = {
            'Toyota': 1200000, 'Honda': 1100000, 'Hyundai': 900000, 'Maruti': 600000,
            'BMW': 5500000, 'Mercedes': 6000000, 'Audi': 5200000,
            'Ford': 850000, 'Tata': 750000, 'Mahindra': 950000
        }

        price = base_price[brand]

        
        luxury_multiplier = 1.8 if brand in ['BMW', 'Mercedes', 'Audi'] else 1.0
        price *= luxury_multiplier

        
        price *= (year - 2010) / 15 + 0.6

        
        price *= np.exp(-mileage / 100000)

        if transmission == 'Automatic':
            price *= 1.25

        if fuel == 'Electric':
            price *= 1.6
        elif fuel == 'CNG':
            price *= 0.85

        
        price *= np.random.uniform(0.85, 1.15)

        price = max(300000, int(price // 1000 * 1000)) 

        data.append({
            'brand': brand,
            'model': model,
            'year': year,
            'mileage': mileage,
            'fuel_type': fuel,
            'transmission': transmission,
            'engine_size': engine_size,
            'horsepower': horsepower,
            'price': price
        })

    df = pd.DataFrame(data)
    df.to_csv('car_data.csv', index=False)
    print(f"car_data.csv  → {len(df)}")
    return df

if __name__ == "__main__":
  

    
    df = generate_sample_data(num_cars=5000)

    predictor = CarPricePredictor()

 
    mae, r2, accuracy = predictor.train(df)

    print(f"Training !")
    print(f"MAE: {mae:,.0f}ے")
    print(f"R² Score: {r2:.4f} ({accuracy:.2f}%)")

    predictor.save_model('car_price_model.joblib')
    print(" → car_price_model.joblib")

   
    test_car = {
        'brand': 'Toyota', 'model': 'Camry', 'year': 2022,
        'mileage': 35000, 'fuel_type': 'Petrol', 'transmission': 'Automatic',
        'engine_size': 2.5, 'horsepower': 203
    }
    pred_price = predictor.predict(test_car)
    print(f": 2022 Toyota Camry  = ₹{pred_price:,.0f}")

   