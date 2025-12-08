"""
Supabase Configuration Module - World Happiness Report Dashboard
Updated for Cloud PostgreSQL Connection with Environment Variables
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple

# Load environment variables from .env file
load_dotenv()

# =====================================================
# DATABASE CONFIGURATION
# =====================================================
# For Supabase (Cloud PostgreSQL)

DB_HOST = os.getenv('SUPABASE_HOST', 'aws-1-ap-south-1.pooler.supabase.com')
DB_PORT = int(os.getenv('SUPABASE_PORT', '5432'))
DB_NAME = os.getenv('SUPABASE_DB', 'postgres')
DB_USER = os.getenv('SUPABASE_USER', 'postgres.bbxemgwtzlzqhcjecjon')
DB_PASSWORD = os.getenv('SUPABASE_PASSWORD', 'wBp0zGOKpIF2Jllh')

# Connection string for reference
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

# =====================================================
# STREAMLIT PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="World Happiness Report Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# DATABASE CONNECTION FUNCTION
# =====================================================

@st.cache_resource
def get_database_connection():
    """
    Create and cache a database connection to Supabase PostgreSQL.
    Uses st.cache_resource to maintain a single connection across reruns.
    
    Environment Variables Required:
    - SUPABASE_HOST: Database host
    - SUPABASE_PORT: Database port (usually 5432)
    - SUPABASE_USER: Database user (format: postgres.PROJECT_ID)
    - SUPABASE_PASSWORD: Database password
    - SUPABASE_DB: Database name (usually 'postgres')
    
    For Supabase, sslmode='require' is mandatory.
    """
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
        st.success("✅ Database connected successfully!")
        return conn
    except psycopg2.Error as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.stop()

# =====================================================
# QUERY EXECUTION FUNCTIONS
# =====================================================

def execute_query(query, params=None):
    """
    Execute a SELECT query and return results as a list of dictionaries.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters for prepared statements
    
    Returns:
        list: List of dictionaries with column names as keys
    """
    try:
        conn = get_database_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall()
    except psycopg2.Error as e:
        st.error(f"❌ Query execution error: {str(e)}")
        return []

def execute_query_single(query, params=None):
    """
    Execute a SELECT query and return a single result.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters for prepared statements
    
    Returns:
        dict: Single result dictionary or None
    """
    try:
        conn = get_database_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchone()
    except psycopg2.Error as e:
        st.error(f"❌ Query execution error: {str(e)}")
        return None

# =====================================================
# DATA RETRIEVAL FUNCTIONS
# =====================================================

def get_all_countries():
    """Retrieve all countries from database."""
    query = """
    SELECT country_id, country_name, region_id
    FROM country
    ORDER BY country_name
    """
    return execute_query(query)

def get_all_regions():
    """Retrieve all regions from database."""
    query = """
    SELECT region_id, region_name
    FROM region
    ORDER BY region_name
    """
    return execute_query(query)

def get_country_by_name(country_name):
    """Retrieve a specific country by name."""
    query = """
    SELECT country_id, country_name, region_id
    FROM country
    WHERE country_name = %s
    """
    return execute_query_single(query, (country_name,))

def get_happiness_report_by_country(country_id):
    """Retrieve happiness reports for a specific country across all years."""
    query = """
    SELECT 
        report_id, country_id, year, ranking, happiness_score, dystopia_residual
    FROM happiness_report
    WHERE country_id = %s
    ORDER BY year DESC
    """
    return execute_query(query, (country_id,))

def get_happiness_report_by_year(year):
    """Retrieve all happiness reports for a specific year."""
    query = """
    SELECT 
        hr.report_id, c.country_name, hr.country_id, hr.year, 
        hr.ranking, hr.happiness_score, hr.dystopia_residual
    FROM happiness_report hr
    JOIN country c ON hr.country_id = c.country_id
    WHERE hr.year = %s
    ORDER BY hr.ranking ASC
    """
    return execute_query(query, (year,))

def get_indicators_by_report_id(report_id):
    """Retrieve all indicators for a specific happiness report."""
    query = """
    SELECT 
        hr.report_id, hr.year, c.country_name, hr.happiness_score,
        ei.gdp_per_capita,
        si.social_support, si.healthy_life_expectancy, si.freedom_to_make_life_choices,
        pi.generosity, pi.perceptions_of_corruption
    FROM happiness_report hr
    JOIN country c ON hr.country_id = c.country_id
    LEFT JOIN economic_indicator ei ON hr.report_id = ei.report_id
    LEFT JOIN social_indicator si ON hr.report_id = si.report_id
    LEFT JOIN perception_indicator pi ON hr.report_id = pi.report_id
    WHERE hr.report_id = %s
    """
    return execute_query_single(query, (report_id,))

def get_country_happiness_trend(country_id):
    """Retrieve happiness score trend for a country across years."""
    query = """
    SELECT 
        year, happiness_score, ranking, dystopia_residual
    FROM happiness_report
    WHERE country_id = %s
    ORDER BY year ASC
    """
    return execute_query(query, (country_id,))

def get_region_statistics(region_id, year):
    """Retrieve happiness statistics for a region in a specific year."""
    query = """
    SELECT 
        c.country_name, hr.happiness_score, hr.ranking,
        ei.gdp_per_capita,
        si.social_support, si.healthy_life_expectancy, si.freedom_to_make_life_choices,
        pi.generosity, pi.perceptions_of_corruption
    FROM happiness_report hr
    JOIN country c ON hr.country_id = c.country_id
    LEFT JOIN economic_indicator ei ON hr.report_id = ei.report_id
    LEFT JOIN social_indicator si ON hr.report_id = si.report_id
    LEFT JOIN perception_indicator pi ON hr.report_id = pi.report_id
    WHERE c.region_id = %s AND hr.year = %s
    ORDER BY hr.happiness_score DESC
    """
    return execute_query(query, (region_id, year))

def get_global_statistics(year):
    """Retrieve global happiness statistics for a specific year."""
    query = """
    SELECT 
        COUNT(*) as total_countries,
        ROUND(AVG(happiness_score)::numeric, 3) as avg_happiness,
        ROUND(MAX(happiness_score)::numeric, 3) as max_happiness,
        ROUND(MIN(happiness_score)::numeric, 3) as min_happiness,
        ROUND(STDDEV(happiness_score)::numeric, 3) as stddev_happiness,
        ROUND(AVG(ei.gdp_per_capita)::numeric, 3) as avg_gdp,
        ROUND(AVG(si.social_support)::numeric, 3) as avg_social_support,
        ROUND(AVG(si.healthy_life_expectancy)::numeric, 3) as avg_life_expectancy,
        ROUND(AVG(si.freedom_to_make_life_choices)::numeric, 3) as avg_freedom,
        ROUND(AVG(pi.generosity)::numeric, 3) as avg_generosity,
        ROUND(AVG(pi.perceptions_of_corruption)::numeric, 3) as avg_corruption
    FROM happiness_report hr
    LEFT JOIN economic_indicator ei ON hr.report_id = ei.report_id
    LEFT JOIN social_indicator si ON hr.report_id = si.report_id
    LEFT JOIN perception_indicator pi ON hr.report_id = pi.report_id
    WHERE hr.year = %s
    """
    return execute_query_single(query, (year,))

def get_available_years():
    """Retrieve all available years in the dataset."""
    query = """
    SELECT DISTINCT year
    FROM happiness_report
    ORDER BY year DESC
    """
    result = execute_query(query)
    return [row['year'] for row in result]

def get_top_countries_by_happiness(year, limit=10):
    """Retrieve top countries by happiness score for a specific year."""
    query = """
    SELECT 
        c.country_name, c.region_id, r.region_name,
        hr.happiness_score, hr.ranking,
        ei.gdp_per_capita,
        si.social_support, si.healthy_life_expectancy, si.freedom_to_make_life_choices,
        pi.generosity, pi.perceptions_of_corruption
    FROM happiness_report hr
    JOIN country c ON hr.country_id = c.country_id
    JOIN region r ON c.region_id = r.region_id
    LEFT JOIN economic_indicator ei ON hr.report_id = ei.report_id
    LEFT JOIN social_indicator si ON hr.report_id = si.report_id
    LEFT JOIN perception_indicator pi ON hr.report_id = pi.report_id
    WHERE hr.year = %s
    ORDER BY hr.happiness_score DESC
    LIMIT %s
    """
    return execute_query(query, (year, limit))

def get_bottom_countries_by_happiness(year, limit=10):
    """Retrieve bottom countries by happiness score for a specific year."""
    query = """
    SELECT 
        c.country_name, c.region_id, r.region_name,
        hr.happiness_score, hr.ranking,
        ei.gdp_per_capita,
        si.social_support, si.healthy_life_expectancy, si.freedom_to_make_life_choices,
        pi.generosity, pi.perceptions_of_corruption
    FROM happiness_report hr
    JOIN country c ON hr.country_id = c.country_id
    JOIN region r ON c.region_id = r.region_id
    LEFT JOIN economic_indicator ei ON hr.report_id = ei.report_id
    LEFT JOIN social_indicator si ON hr.report_id = si.report_id
    LEFT JOIN perception_indicator pi ON hr.report_id = pi.report_id
    WHERE hr.year = %s
    ORDER BY hr.happiness_score ASC
    LIMIT %s
    """
    return execute_query(query, (year, limit))

def get_correlation_data(year):
    """Retrieve data for correlation analysis."""
    query = """
    SELECT 
        c.country_name,
        hr.happiness_score,
        ei.gdp_per_capita,
        si.social_support,
        si.healthy_life_expectancy,
        si.freedom_to_make_life_choices,
        pi.generosity,
        pi.perceptions_of_corruption
    FROM happiness_report hr
    JOIN country c ON hr.country_id = c.country_id
    LEFT JOIN economic_indicator ei ON hr.report_id = ei.report_id
    LEFT JOIN social_indicator si ON hr.report_id = si.report_id
    LEFT JOIN perception_indicator pi ON hr.report_id = pi.report_id
    WHERE hr.year = %s AND ei.gdp_per_capita IS NOT NULL
    ORDER BY c.country_name
    """
    return execute_query(query, (year,))

def get_regions():
    """Retrieve all regions as list of tuples (region_id, region_name)."""
    regions = get_all_regions()
    return [(r['region_id'], r['region_name']) for r in regions]

def get_happiness_count():
    """Get total count of happiness records in database."""
    query = """
    SELECT COUNT(*) as count
    FROM happiness_report
    """
    result = execute_query_single(query)
    return result['count'] if result else 0

def get_countries_count():
    """Get total count of countries in database."""
    query = """
    SELECT COUNT(*) as count
    FROM country
    """
    result = execute_query_single(query)
    return result['count'] if result else 0

def get_regions_count():
    """Get total count of regions in database."""
    query = """
    SELECT COUNT(*) as count
    FROM region
    """
    result = execute_query_single(query)
    return result['count'] if result else 0

# =====================================================
# STYLING & THEME
# =====================================================

THEME_CONFIG = {
    'primaryColor': '#1f77b4',
    'backgroundColor': '#f8f9fa',
    'secondaryBackgroundColor': '#e8eef2',
    'textColor': '#262730',
    'font': 'sans serif'
}

# =====================================================
# DASHBOARD INFO
# =====================================================

DASHBOARD_INFO = {
    'title': '🌍 World Happiness Report Dashboard (2015-2024)',
    'subtitle': 'Exploring Global Happiness Trends and Contributing Factors',
    'description': """
    This interactive dashboard visualizes the World Happiness Report data from 2015 to 2024,
    examining happiness levels across 171 countries and analyzing key factors that contribute
    to national well-being including:
    - Economic indicators (GDP per capita)
    - Social factors (social support, life expectancy)
    - Personal freedoms and generosity
    - Perceptions of corruption
    """
}

# =====================================================
# VALIDATION FUNCTIONS
# =====================================================

def validate_database_connection():
    """Test database connection and return status."""
    try:
        result = execute_query_single("SELECT COUNT(*) as count FROM country")
        if result:
            return True, result['count']
        return False, 0
    except Exception as e:
        return False, str(e)

# =====================================================
# SIDEBAR STYLING
# =====================================================

def apply_sidebar_styling():
    """Apply custom CSS styling to sidebar."""
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# DATA EXPORT FUNCTIONS
# =====================================================

import pandas as pd

def get_dataframe_from_query(query, params=None):
    """Execute query and return results as pandas DataFrame."""
    try:
        conn = get_database_connection()
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Error retrieving data: {str(e)}")
        return pd.DataFrame()

def export_to_csv(data, filename):
    """Convert data to CSV for download."""
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data
    return df.to_csv(index=False).encode('utf-8')

# =====================================================
# DEBUG UTILITIES
# =====================================================

def debug_info():
    """Display debug information (only in development)."""
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
        st.sidebar.write("### 🐛 Debug Info")
        st.sidebar.write(f"Database: {DB_NAME}")
        st.sidebar.write(f"Host: {DB_HOST}")
        st.sidebar.write(f"User: {DB_USER}")
        
        # Test connection
        is_connected, count = validate_database_connection()
        if is_connected:
            st.sidebar.success(f"✅ Connected! Countries: {count}")
        else:
            st.sidebar.error(f"❌ Connection failed: {count}")
