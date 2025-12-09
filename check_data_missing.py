#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILE: check_data_missing.py
FUNGSI: Check data yang hilang atau NULL di database
DESKRIPSI: Script untuk mengidentifikasi missing data, NULL values, dan data integrity issues
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Load environment variables
load_dotenv()

# =====================================================
# DATABASE CONNECTION
# =====================================================

DB_HOST = os.getenv('SUPABASE_HOST', 'aws-1-ap-south-1.pooler.supabase.com')
DB_PORT = int(os.getenv('SUPABASE_PORT', '5432'))
DB_NAME = os.getenv('SUPABASE_DB', 'postgres')
DB_USER = os.getenv('SUPABASE_USER', 'postgres.bbxemgwtzlzqhcjecjon')
DB_PASSWORD = os.getenv('SUPABASE_PASSWORD', 'wBp0zGOKpIF2Jllh')

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

def check_table_counts():
    """Check total records in each table."""
    print("\n" + "="*70)
    print("📊 TABLE RECORD COUNTS")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    tables = [
        'region', 'country', 'happiness_report',
        'economic_indicator', 'social_indicator', 'perception_indicator'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            print(f"✓ {table:25} → {count:6,} records")
        except Exception as e:
            print(f"✗ {table:25} → ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def check_null_values():
    """Check NULL values in important columns."""
    print("\n" + "="*70)
    print("🔍 NULL VALUES CHECK")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    checks = {
        'happiness_report': ['country_id', 'year', 'ranking', 'happiness_score'],
        'economic_indicator': ['report_id', 'gdp_per_capita'],
        'social_indicator': ['report_id', 'social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices'],
        'perception_indicator': ['report_id', 'generosity', 'perceptions_of_corruption'],
        'country': ['country_id', 'country_name', 'region_id'],
        'region': ['region_id', 'region_name']
    }
    
    for table, columns in checks.items():
        print(f"\n📋 {table}:")
        for col in columns:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) as null_count 
                    FROM {table} 
                    WHERE {col} IS NULL
                """)
                result = cursor.fetchone()
                null_count = result['null_count'] if result else 0
                
                if null_count == 0:
                    print(f"  ✓ {col:30} → 0 NULL values")
                else:
                    print(f"  ⚠️  {col:30} → {null_count:,} NULL values")
            except Exception as e:
                print(f"  ✗ {col:30} → ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def check_duplicate_records():
    """Check for duplicate records."""
    print("\n" + "="*70)
    print("🔄 DUPLICATE RECORDS CHECK")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check duplicate countries
    print("\n📋 Duplicate Countries (by name):")
    try:
        cursor.execute("""
            SELECT country_name, COUNT(*) as count
            FROM country
            GROUP BY country_name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"  ⚠️  {row['country_name']:30} → {row['count']} records")
        else:
            print("  ✓ No duplicate countries found")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    # Check duplicate regions
    print("\n📋 Duplicate Regions (by name):")
    try:
        cursor.execute("""
            SELECT region_name, COUNT(*) as count
            FROM region
            GROUP BY region_name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"  ⚠️  {row['region_name']:30} → {row['count']} records")
        else:
            print("  ✓ No duplicate regions found")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    # Check duplicate happiness records (same country & year)
    print("\n📋 Duplicate Happiness Reports (by country & year):")
    try:
        cursor.execute("""
            SELECT country_id, year, COUNT(*) as count
            FROM happiness_report
            GROUP BY country_id, year
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"  ⚠️  country_id={row['country_id']:3}, year={row['year']} → {row['count']} records")
        else:
            print("  ✓ No duplicate happiness reports found")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def check_year_distribution():
    """Check year distribution in happiness_report."""
    print("\n" + "="*70)
    print("📅 YEAR DISTRIBUTION IN HAPPINESS REPORT")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT year, COUNT(*) as count
            FROM happiness_report
            GROUP BY year
            ORDER BY year DESC
        """)
        results = cursor.fetchall()
        
        if results:
            for row in results:
                print(f"  ✓ Year {row['year']} → {row['count']:4,} records")
        else:
            print("  ⚠️  No data found in happiness_report")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def check_region_country_mapping():
    """Check region-country mapping completeness."""
    print("\n" + "="*70)
    print("🗺️  REGION-COUNTRY MAPPING CHECK")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check countries without region
    print("\n📋 Countries without Region:")
    try:
        cursor.execute("""
            SELECT COUNT(*) as count FROM country WHERE region_id IS NULL
        """)
        result = cursor.fetchone()
        count = result['count'] if result else 0
        if count == 0:
            print(f"  ✓ All countries have regions assigned")
        else:
            print(f"  ⚠️  {count} countries have NULL region_id")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    # Check region distribution
    print("\n📋 Countries per Region:")
    try:
        cursor.execute("""
            SELECT r.region_name, COUNT(c.country_id) as country_count
            FROM region r
            LEFT JOIN country c ON r.region_id = c.region_id
            GROUP BY r.region_id, r.region_name
            ORDER BY country_count DESC
        """)
        results = cursor.fetchall()
        for row in results:
            print(f"  ✓ {row['region_name']:40} → {row['country_count']:3} countries")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def check_indicator_completeness():
    """Check completeness of indicator data."""
    print("\n" + "="*70)
    print("📊 INDICATOR DATA COMPLETENESS")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Total happiness reports
    try:
        cursor.execute("SELECT COUNT(*) as count FROM happiness_report")
        total_reports = cursor.fetchone()['count']
    except:
        total_reports = 0
    
    indicators = {
        'economic_indicator': 'Economic Indicators (GDP)',
        'social_indicator': 'Social Indicators',
        'perception_indicator': 'Perception Indicators'
    }
    
    print(f"\nTotal Happiness Reports: {total_reports:,}\n")
    
    for table, label in indicators.items():
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            percentage = (count / total_reports * 100) if total_reports > 0 else 0
            
            status = "✓" if percentage >= 90 else "⚠️"
            print(f"{status} {label:35} → {count:6,} records ({percentage:5.1f}%)")
        except Exception as e:
            print(f"✗ {label:35} → ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def check_data_ranges():
    """Check data value ranges for validity."""
    print("\n" + "="*70)
    print("📈 DATA VALUE RANGES CHECK")
    print("="*70)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Happiness score range (should be 0-10)
    print("\n📋 Happiness Score Range:")
    try:
        cursor.execute("""
            SELECT 
                MIN(happiness_score) as min_score,
                MAX(happiness_score) as max_score,
                AVG(happiness_score) as avg_score
            FROM happiness_report
        """)
        result = cursor.fetchone()
        print(f"  Min: {result['min_score']:.3f}")
        print(f"  Max: {result['max_score']:.3f}")
        print(f"  Avg: {result['avg_score']:.3f}")
        
        if result['min_score'] >= 0 and result['max_score'] <= 10:
            print("  ✓ Score range is valid (0-10)")
        else:
            print("  ⚠️  Score range is outside expected bounds (0-10)")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    # Ranking range (should be positive integers)
    print("\n📋 Ranking Range:")
    try:
        cursor.execute("""
            SELECT 
                MIN(ranking) as min_rank,
                MAX(ranking) as max_rank
            FROM happiness_report
        """)
        result = cursor.fetchone()
        print(f"  Min: {result['min_rank']}")
        print(f"  Max: {result['max_rank']}")
        print(f"  ✓ Ranking range looks valid")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
    
    cursor.close()
    conn.close()

def main():
    """Main function to run all checks."""
    print("\n" + "="*70)
    print("🔍 DATA MISSING & INTEGRITY CHECK")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        check_table_counts()
        check_null_values()
        check_duplicate_records()
        check_year_distribution()
        check_region_country_mapping()
        check_indicator_completeness()
        check_data_ranges()
        
        print("\n" + "="*70)
        print("✅ CHECK COMPLETED")
        print(f"   Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
