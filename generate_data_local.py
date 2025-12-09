#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILE: generate_data_local.py
FUNGSI: Generate sample data ke CSV files (TANPA DATABASE)
DESKRIPSI: Script untuk generate dummy data dalam bentuk CSV jika data tidak ada
"""

import os
import sys
import csv
from datetime import datetime
import random
from pathlib import Path

# =====================================================
# CONFIGURATION
# =====================================================

DATA_DIR = "data"

def ensure_data_dir():
    """Ensure data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Created '{DATA_DIR}' directory")

def write_csv(filename, headers, rows):
    """Write data to CSV file."""
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return True
    except Exception as e:
        print(f"  ✗ Error writing {filename}: {str(e)}")
        return False

def file_has_data(filename):
    """Check if CSV file has data."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            return any(row for row in reader)
    except:
        return False

def generate_regions():
    """Generate test regions CSV."""
    print("\n📌 Generating Regions...")
    
    filename = 'region.csv'
    if file_has_data(filename):
        print(f"  ✓ {filename} already exists with data")
        return True
    
    regions = [
        {'region_id': '1', 'region_name': 'Western Europe'},
        {'region_id': '2', 'region_name': 'Central and Eastern Europe'},
        {'region_id': '3', 'region_name': 'Commonwealth of Independent States'},
        {'region_id': '4', 'region_name': 'Middle East and North Africa'},
        {'region_id': '5', 'region_name': 'Sub-Saharan Africa'},
        {'region_id': '6', 'region_name': 'South Asia'},
        {'region_id': '7', 'region_name': 'Southeast Asia'},
        {'region_id': '8', 'region_name': 'East Asia'},
        {'region_id': '9', 'region_name': 'Latin America and Caribbean'},
        {'region_id': '10', 'region_name': 'North America and ANZ'},
    ]
    
    if write_csv(filename, ['region_id', 'region_name'], regions):
        print(f"  ✓ Generated {len(regions)} regions to {filename}")
        return True
    return False

def generate_countries():
    """Generate test countries CSV."""
    print("\n📌 Generating Countries...")
    
    filename = 'country.csv'
    if file_has_data(filename):
        print(f"  ✓ {filename} already exists with data")
        return True
    
    countries = [
        {'country_id': '1', 'country_name': 'Denmark', 'region_id': '1'},
        {'country_id': '2', 'country_name': 'Iceland', 'region_id': '1'},
        {'country_id': '3', 'country_name': 'Switzerland', 'region_id': '1'},
        {'country_id': '4', 'country_name': 'Netherlands', 'region_id': '1'},
        {'country_id': '5', 'country_name': 'Finland', 'region_id': '1'},
        {'country_id': '6', 'country_name': 'Sweden', 'region_id': '1'},
        {'country_id': '7', 'country_name': 'Norway', 'region_id': '1'},
        {'country_id': '8', 'country_name': 'Austria', 'region_id': '1'},
        {'country_id': '9', 'country_name': 'Germany', 'region_id': '1'},
        {'country_id': '10', 'country_name': 'France', 'region_id': '1'},
        {'country_id': '11', 'country_name': 'United Kingdom', 'region_id': '1'},
        {'country_id': '12', 'country_name': 'Belgium', 'region_id': '1'},
        {'country_id': '13', 'country_name': 'Poland', 'region_id': '2'},
        {'country_id': '14', 'country_name': 'Czechia', 'region_id': '2'},
        {'country_id': '15', 'country_name': 'Romania', 'region_id': '2'},
        {'country_id': '16', 'country_name': 'Hungary', 'region_id': '2'},
        {'country_id': '17', 'country_name': 'Slovenia', 'region_id': '2'},
        {'country_id': '18', 'country_name': 'Croatia', 'region_id': '2'},
        {'country_id': '19', 'country_name': 'Serbia', 'region_id': '2'},
        {'country_id': '20', 'country_name': 'Bulgaria', 'region_id': '2'},
        {'country_id': '21', 'country_name': 'Russia', 'region_id': '3'},
        {'country_id': '22', 'country_name': 'Kazakhstan', 'region_id': '3'},
        {'country_id': '23', 'country_name': 'Ukraine', 'region_id': '3'},
        {'country_id': '24', 'country_name': 'Belarus', 'region_id': '3'},
        {'country_id': '25', 'country_name': 'Egypt', 'region_id': '4'},
        {'country_id': '26', 'country_name': 'Saudi Arabia', 'region_id': '4'},
        {'country_id': '27', 'country_name': 'Israel', 'region_id': '4'},
        {'country_id': '28', 'country_name': 'Turkey', 'region_id': '4'},
        {'country_id': '29', 'country_name': 'Lebanon', 'region_id': '4'},
        {'country_id': '30', 'country_name': 'Iran', 'region_id': '4'},
        {'country_id': '31', 'country_name': 'South Africa', 'region_id': '5'},
        {'country_id': '32', 'country_name': 'Nigeria', 'region_id': '5'},
        {'country_id': '33', 'country_name': 'Kenya', 'region_id': '5'},
        {'country_id': '34', 'country_name': 'Ethiopia', 'region_id': '5'},
        {'country_id': '35', 'country_name': 'Ghana', 'region_id': '5'},
        {'country_id': '36', 'country_name': 'Uganda', 'region_id': '5'},
        {'country_id': '37', 'country_name': 'India', 'region_id': '6'},
        {'country_id': '38', 'country_name': 'Pakistan', 'region_id': '6'},
        {'country_id': '39', 'country_name': 'Bangladesh', 'region_id': '6'},
        {'country_id': '40', 'country_name': 'Nepal', 'region_id': '6'},
        {'country_id': '41', 'country_name': 'Sri Lanka', 'region_id': '6'},
        {'country_id': '42', 'country_name': 'Afghanistan', 'region_id': '6'},
        {'country_id': '43', 'country_name': 'Thailand', 'region_id': '7'},
        {'country_id': '44', 'country_name': 'Vietnam', 'region_id': '7'},
        {'country_id': '45', 'country_name': 'Philippines', 'region_id': '7'},
        {'country_id': '46', 'country_name': 'Indonesia', 'region_id': '7'},
        {'country_id': '47', 'country_name': 'Malaysia', 'region_id': '7'},
        {'country_id': '48', 'country_name': 'Singapore', 'region_id': '7'},
        {'country_id': '49', 'country_name': 'China', 'region_id': '8'},
        {'country_id': '50', 'country_name': 'Japan', 'region_id': '8'},
        {'country_id': '51', 'country_name': 'South Korea', 'region_id': '8'},
        {'country_id': '52', 'country_name': 'Taiwan', 'region_id': '8'},
        {'country_id': '53', 'country_name': 'Brazil', 'region_id': '9'},
        {'country_id': '54', 'country_name': 'Mexico', 'region_id': '9'},
        {'country_id': '55', 'country_name': 'Colombia', 'region_id': '9'},
        {'country_id': '56', 'country_name': 'Chile', 'region_id': '9'},
        {'country_id': '57', 'country_name': 'Argentina', 'region_id': '9'},
        {'country_id': '58', 'country_name': 'Peru', 'region_id': '9'},
        {'country_id': '59', 'country_name': 'Canada', 'region_id': '10'},
        {'country_id': '60', 'country_name': 'United States', 'region_id': '10'},
        {'country_id': '61', 'country_name': 'Australia', 'region_id': '10'},
        {'country_id': '62', 'country_name': 'New Zealand', 'region_id': '10'},
    ]
    
    if write_csv(filename, ['country_id', 'country_name', 'region_id'], countries):
        print(f"  ✓ Generated {len(countries)} countries to {filename}")
        return True
    return False

def generate_happiness_report():
    """Generate happiness report data CSV."""
    print("\n📌 Generating Happiness Report Data...")
    
    filename = 'happiness_report.csv'
    if file_has_data(filename):
        print(f"  ✓ {filename} already exists with data")
        return True
    
    happiness_data = []
    report_id = 1
    years = list(range(2015, 2025))  # 2015-2024
    
    for country_id in range(1, 63):  # 62 countries
        for year in years:
            ranking = random.randint(1, 180)
            happiness_score = round(random.uniform(2.5, 7.8), 3)
            dystopia_residual = round(random.uniform(1.0, 2.5), 3)
            
            happiness_data.append({
                'report_id': str(report_id),
                'country_id': str(country_id),
                'year': str(year),
                'ranking': str(ranking),
                'happiness_score': str(happiness_score),
                'dystopia_residual': str(dystopia_residual)
            })
            report_id += 1
    
    headers = ['report_id', 'country_id', 'year', 'ranking', 'happiness_score', 'dystopia_residual']
    if write_csv(filename, headers, happiness_data):
        print(f"  ✓ Generated {len(happiness_data)} happiness records to {filename}")
        return True
    return False

def generate_economic_indicator():
    """Generate economic indicator data CSV."""
    print("\n📌 Generating Economic Indicator Data...")
    
    filename = 'economic_indicator.csv'
    if file_has_data(filename):
        print(f"  ✓ {filename} already exists with data")
        return True
    
    # Read happiness data to match report_id
    happiness_file = os.path.join(DATA_DIR, 'happiness_report.csv')
    economic_data = []
    
    if os.path.exists(happiness_file):
        with open(happiness_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('report_id'):
                    gdp_per_capita = round(random.uniform(0.0, 1.5), 3)
                    economic_data.append({
                        'report_id': row['report_id'],
                        'gdp_per_capita': str(gdp_per_capita)
                    })
    
    headers = ['report_id', 'gdp_per_capita']
    if write_csv(filename, headers, economic_data):
        print(f"  ✓ Generated {len(economic_data)} economic records to {filename}")
        return True
    return False

def generate_social_indicator():
    """Generate social indicator data CSV."""
    print("\n📌 Generating Social Indicator Data...")
    
    filename = 'social_indicator.csv'
    if file_has_data(filename):
        print(f"  ✓ {filename} already exists with data")
        return True
    
    happiness_file = os.path.join(DATA_DIR, 'happiness_report.csv')
    social_data = []
    
    if os.path.exists(happiness_file):
        with open(happiness_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('report_id'):
                    social_support = round(random.uniform(0.0, 1.0), 3)
                    healthy_life_expectancy = round(random.uniform(0.0, 1.0), 3)
                    freedom_to_make_life_choices = round(random.uniform(0.0, 0.6), 3)
                    
                    social_data.append({
                        'report_id': row['report_id'],
                        'social_support': str(social_support),
                        'healthy_life_expectancy': str(healthy_life_expectancy),
                        'freedom_to_make_life_choices': str(freedom_to_make_life_choices)
                    })
    
    headers = ['report_id', 'social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices']
    if write_csv(filename, headers, social_data):
        print(f"  ✓ Generated {len(social_data)} social indicator records to {filename}")
        return True
    return False

def generate_perception_indicator():
    """Generate perception indicator data CSV."""
    print("\n📌 Generating Perception Indicator Data...")
    
    filename = 'perception_indicator.csv'
    if file_has_data(filename):
        print(f"  ✓ {filename} already exists with data")
        return True
    
    happiness_file = os.path.join(DATA_DIR, 'happiness_report.csv')
    perception_data = []
    
    if os.path.exists(happiness_file):
        with open(happiness_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('report_id'):
                    generosity = round(random.uniform(-0.2, 0.5), 3)
                    perceptions_of_corruption = round(random.uniform(0.0, 1.0), 3)
                    
                    perception_data.append({
                        'report_id': row['report_id'],
                        'generosity': str(generosity),
                        'perceptions_of_corruption': str(perceptions_of_corruption)
                    })
    
    headers = ['report_id', 'generosity', 'perceptions_of_corruption']
    if write_csv(filename, headers, perception_data):
        print(f"  ✓ Generated {len(perception_data)} perception indicator records to {filename}")
        return True
    return False

def main():
    """Main function to generate all CSV data."""
    print("\n" + "="*70)
    print("📊 GENERATE TEST DATA TO CSV FILES (NO DATABASE)")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        ensure_data_dir()
        generate_regions()
        generate_countries()
        generate_happiness_report()
        generate_economic_indicator()
        generate_social_indicator()
        generate_perception_indicator()
        
        print("\n" + "="*70)
        print("✅ DATA GENERATION COMPLETED")
        print(f"   Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print(f"\n📁 Data directory: {os.path.abspath(DATA_DIR)}")
        print("\n💡 Generated CSV files:")
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv'):
                filepath = os.path.join(DATA_DIR, filename)
                size = os.path.getsize(filepath)
                print(f"   ✓ {filename} ({size:,} bytes)")
        print("\n💡 Tip: Run 'python check_data_missing_local.py' to verify generated data\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
