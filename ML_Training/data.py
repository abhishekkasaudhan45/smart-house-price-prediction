
import pandas as pd
import numpy as np

np.random.seed(42)

num_houses = 1000
print(f"Creating data for {num_houses} houses...")

print("\n📊 Creating house features...")

area = np.random.randint(500, 5000, num_houses)

bedrooms = np.random.randint(1, 6, num_houses)

bathrooms = np.random.randint(1, 5, num_houses)

stories = np.random.randint(1, 4, num_houses)

parking = np.random.randint(0, 4, num_houses)

has_pool = np.random.choice(['yes', 'no'], num_houses)
has_garage = np.random.choice(['yes', 'no'], num_houses)
has_ac = np.random.choice(['yes', 'no'], num_houses)

print("✅ Created all house features!")

print("\n💰 Calculating house prices...")

base_price = 100000


prices = (
    base_price +                          
    area * 100 +                         
    bedrooms * 50000 +                   
    bathrooms * 30000 +                   
    stories * 40000 +                     
    parking * 25000 +                    
    (has_pool == 'yes') * 80000 +       
    (has_garage == 'yes') * 60000 +      
    (has_ac == 'yes') * 40000 +        
    np.random.normal(0, 30000, num_houses) 
)


prices = np.maximum(prices, 150000)

print("✅ Calculated all prices!")

print("\n📋 Creating data table...")

data = pd.DataFrame({
    'area': area,
    'bedrooms': bedrooms,
    'bathrooms': bathrooms,
    'stories': stories,
    'parking': parking,
    'has_pool': has_pool,
    'has_garage': has_garage,
    'has_ac': has_ac,
    'price': prices
})

print("✅ Data table created!")

data.to_csv('house_data.csv', index=False)
print(f"\n💾 Saved to 'house_data.csv'")

print("\n" + "="*60)
print("📊 YOUR TRAINING DATA PREVIEW")
print("="*60)
print(f"\nTotal houses: {len(data)}")
print(f"\nFirst 5 houses:")
print(data.head())

print(f"\n📈 Price Statistics:")
print(f"   Cheapest house: ${data['price'].min():,.0f}")
print(f"   Most expensive: ${data['price'].max():,.0f}")
print(f"   Average price: ${data['price'].mean():,.0f}")

print("\n" + "="*60)
print("✅ SUCCESS! Your training data is ready!")
print("="*60)
print("\n💡 What you just did:")
print("   1. Created 1000 houses with different features")
print("   2. Calculated realistic prices based on those features")
print("   3. Saved everything to a CSV file")
print("\n🎯 Next: We'll use this data to train a model!")