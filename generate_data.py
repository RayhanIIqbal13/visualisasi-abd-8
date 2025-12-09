#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILE: generate_data.py
FUNGSI: Generate sample data untuk testing dan development
DESKRIPSI: Script untuk generate dummy data jika data di database tidak lengkap
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
import random

# Load environment variables
load_dotenv()

# =====================================================
# DATABASE CONNECTION
# =====================================================

DB_HOST = os.getenv('SUPABASE_HOST', 'aws-1-ap-south-1.pooler.supabase.com')
DB_PORT = int(os.getenv('SUPABASE_PORT', '5432'))
DB_NAME = os.getenv('SUPABASE_DB', 'postgres')
DB_USER = os.getenv('SUPABASE_USER', 'postgres.bbxemgwtzlzqhcjecjon')
DB_PASSWORD = os.getenv('SUPABASE_PASSWORD', '')

def get_connection():
    """Create database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require',
            connect_timeout=5
        )
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        sys.exit(1)

def generate_test_regions():
    """Generate test regions if table is empty."""
    print("\n📌 Generating Test Regions...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if regions exist
    cursor.execute("SELECT COUNT(*) FROM region")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Regions already exist ({count} records)")
        cursor.close()
        conn.close()
        return
    
    regions = [
        'Western Europe',
        'Central and Eastern Europe',
        'Commonwealth of Independent States',
        'Middle East and North Africa',
        'Sub-Saharan Africa',
        'South Asia',
        'Southeast Asia',
        'East Asia',
        'Latin America and Caribbean',
        'North America and ANZ'
    ]
    
    try:
        for i, region in enumerate(regions, 1):
            cursor.execute(
                "INSERT INTO region (region_id, region_name) VALUES (%s, %s)",
                (i, region)
            )
        conn.commit()
        print(f"  ✓ Generated {len(regions)} regions")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def generate_test_countries():
    """Generate test countries if table is empty."""
    print("\n📌 Generating Test Countries...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if countries exist
    cursor.execute("SELECT COUNT(*) FROM country")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Countries already exist ({count} records)")
        cursor.close()
        conn.close()
        return
    
    # Sample countries by region
    countries = [
        ('Denmark', 1), ('Iceland', 1), ('Switzerland', 1), ('Netherlands', 1),
        ('Finland', 1), ('Sweden', 1), ('Norway', 1), ('Austria', 1),
        ('Germany', 1), ('France', 1), ('United Kingdom', 1), ('Belgium', 1),
        ('Poland', 2), ('Czechia', 2), ('Romania', 2), ('Hungary', 2),
        ('Russia', 3), ('Kazakhstan', 3), ('Ukraine', 3),
        ('Egypt', 4), ('Saudi Arabia', 4), ('Israel', 4), ('Turkey', 4),
        ('South Africa', 5), ('Nigeria', 5), ('Kenya', 5), ('Ethiopia', 5),
        ('India', 6), ('Pakistan', 6), ('Bangladesh', 6), ('Nepal', 6),
        ('Thailand', 7), ('Vietnam', 7), ('Philippines', 7), ('Indonesia', 7),
        ('China', 8), ('Japan', 8), ('South Korea', 8), ('Taiwan', 8),
        ('Brazil', 9), ('Mexico', 9), ('Colombia', 9), ('Chile', 9),
        ('Canada', 10), ('United States', 10), ('Australia', 10), ('New Zealand', 10)
    ]
    
    try:
        for i, (country, region_id) in enumerate(countries, 1):
            cursor.execute(
                "INSERT INTO country (country_id, country_name, region_id) VALUES (%s, %s, %s)",
                (i, country, region_id)
            )
        conn.commit()
        print(f"  ✓ Generated {len(countries)} countries")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def generate_test_happiness_data():
    """Generate test happiness report data if table is empty."""
    print("\n📌 Generating Test Happiness Data...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if happiness data exists
    cursor.execute("SELECT COUNT(*) FROM happiness_report")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Happiness data already exists ({count} records)")
        cursor.close()
        conn.close()
        return
    
    # Get countries and years
    cursor.execute("SELECT COUNT(*) FROM country")
    num_countries = cursor.fetchone()[0]
    
    if num_countries == 0:
        print("  ✗ No countries found. Generate countries first.")
        cursor.close()
        conn.close()
        return
    
    years = list(range(2015, 2025))  # 2015-2024
    report_id = 1
    
    try:
        for country_id in range(1, num_countries + 1):
            for year in years:
                # Generate random but realistic happiness data
                ranking = random.randint(1, 180)
                happiness_score = round(random.uniform(2.5, 7.8), 3)
                dystopia_residual = round(random.uniform(1.0, 2.5), 3)
                
                cursor.execute(
                    """INSERT INTO happiness_report 
                       (report_id, country_id, year, ranking, happiness_score, dystopia_residual)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (report_id, country_id, year, ranking, happiness_score, dystopia_residual)
                )
                report_id += 1
        
        conn.commit()
        total_records = num_countries * len(years)
        print(f"  ✓ Generated {total_records} happiness records ({num_countries} countries × {len(years)} years)")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def generate_test_economic_data():
    """Generate test economic indicator data."""
    print("\n📌 Generating Test Economic Data...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if economic data exists
    cursor.execute("SELECT COUNT(*) FROM economic_indicator")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Economic data already exists ({count} records)")
        cursor.close()
        conn.close()
        return
    
    # Get all happiness reports
    cursor.execute("SELECT report_id FROM happiness_report ORDER BY report_id")
    reports = cursor.fetchall()
    
    if not reports:
        print("  ✗ No happiness reports found. Generate happiness data first.")
        cursor.close()
        conn.close()
        return
    
    try:
        for report in reports:
            report_id = report[0]
            # Generate realistic GDP per capita (0.0 - 1.5, normalized)
            gdp_per_capita = round(random.uniform(0.0, 1.5), 3)
            
            cursor.execute(
                """INSERT INTO economic_indicator (report_id, gdp_per_capita)
                   VALUES (%s, %s)""",
                (report_id, gdp_per_capita)
            )
        
        conn.commit()
        print(f"  ✓ Generated {len(reports)} economic indicator records")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def generate_test_social_data():
    """Generate test social indicator data."""
    print("\n📌 Generating Test Social Indicator Data...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if social data exists
    cursor.execute("SELECT COUNT(*) FROM social_indicator")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Social data already exists ({count} records)")
        cursor.close()
        conn.close()
        return
    
    # Get all happiness reports
    cursor.execute("SELECT report_id FROM happiness_report ORDER BY report_id")
    reports = cursor.fetchall()
    
    if not reports:
        print("  ✗ No happiness reports found. Generate happiness data first.")
        cursor.close()
        conn.close()
        return
    
    try:
        for report in reports:
            report_id = report[0]
            social_support = round(random.uniform(0.0, 1.0), 3)
            healthy_life_expectancy = round(random.uniform(0.0, 1.0), 3)
            freedom_to_make_life_choices = round(random.uniform(0.0, 0.6), 3)
            
            cursor.execute(
                """INSERT INTO social_indicator 
                   (report_id, social_support, healthy_life_expectancy, freedom_to_make_life_choices)
                   VALUES (%s, %s, %s, %s)""",
                (report_id, social_support, healthy_life_expectancy, freedom_to_make_life_choices)
            )
        
        conn.commit()
        print(f"  ✓ Generated {len(reports)} social indicator records")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def generate_test_perception_data():
    """Generate test perception indicator data."""
    print("\n📌 Generating Test Perception Indicator Data...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if perception data exists
    cursor.execute("SELECT COUNT(*) FROM perception_indicator")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Perception data already exists ({count} records)")
        cursor.close()
        conn.close()
        return
    
    # Get all happiness reports
    cursor.execute("SELECT report_id FROM happiness_report ORDER BY report_id")
    reports = cursor.fetchall()
    
    if not reports:
        print("  ✗ No happiness reports found. Generate happiness data first.")
        cursor.close()
        conn.close()
        return
    
    try:
        for report in reports:
            report_id = report[0]
            generosity = round(random.uniform(-0.2, 0.5), 3)
            perceptions_of_corruption = round(random.uniform(0.0, 1.0), 3)
            
            cursor.execute(
                """INSERT INTO perception_indicator 
                   (report_id, generosity, perceptions_of_corruption)
                   VALUES (%s, %s, %s)""",
                (report_id, generosity, perceptions_of_corruption)
            )
        
        conn.commit()
        print(f"  ✓ Generated {len(reports)} perception indicator records")
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to generate all test data."""
    print("\n" + "="*70)
    print("📊 GENERATE TEST DATA FOR WORLD HAPPINESS REPORT")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        generate_test_regions()
        generate_test_countries()
        generate_test_happiness_data()
        generate_test_economic_data()
        generate_test_social_data()
        generate_test_perception_data()
        
        print("\n" + "="*70)
        print("✅ DATA GENERATION COMPLETED")
        print(f"   Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print("\n💡 Tip: Run 'python check_data_missing.py' to verify generated data\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
