# database.py - Handles all database operations for PostgreSQL
import psycopg2
import psycopg2.extras # to fetch data as dictionaries
import os
import json
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        # Try to get the database URL from Streamlit secrets first (for deployment)
        db_url = st.secrets["DATABASE_URL"]
    except (AttributeError, KeyError):
        # Fallback to .env file for local development
        db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        # This message will appear in the Streamlit logs if the secret is missing
        st.error("Database connection string is not configured. Please set it in Streamlit secrets.")
        print("FATAL: DATABASE_URL not found in Streamlit secrets or .env file.")
        return None

    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        print(f"FATAL: Error connecting to the database: {e}")
        return None

def init_database():
    """Initialize the database and create the evaluations table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                job_description_filename VARCHAR(255) NOT NULL,
                resume_filename VARCHAR(255) NOT NULL,
                hard_score FLOAT NOT NULL,
                semantic_score FLOAT NOT NULL,
                final_score FLOAT NOT NULL,
                verdict VARCHAR(50) NOT NULL,
                must_have_skills JSONB,
                found_must_have_skills JSONB,
                good_to_have_skills JSONB, 
                found_good_to_have_skills JSONB,
                ai_feedback TEXT
            )
            ''')
        conn.commit()
    except Exception as e:
        print(f"DATABASE ERROR in init_database: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def save_evaluation(result_data):
    """Save an evaluation result to the database. Returns True on success, False on failure."""
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        with conn.cursor() as cur:
            must_have_skills = json.dumps(list(result_data.get('must_have_skills', [])))
            found_must_have = json.dumps(list(result_data.get('found_must_have_skills', [])))
            good_to_have_skills = json.dumps(list(result_data.get('good_to_have_skills', [])))
            found_good_to_have = json.dumps(list(result_data.get('found_good_to_have_skills', [])))
            
            cur.execute('''
            INSERT INTO evaluations (
                timestamp, job_description_filename, resume_filename,
                hard_score, semantic_score, final_score, verdict,
                must_have_skills, found_must_have_skills,
                good_to_have_skills, found_good_to_have_skills,
                ai_feedback
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                datetime.now(),
                result_data['jd_filename'], result_data['resume_filename'],
                result_data['hard_score'], result_data['semantic_score'], result_data['final_score'],
                result_data['verdict'],
                must_have_skills, found_must_have,
                good_to_have_skills, found_good_to_have,
                result_data.get('ai_feedback', "")
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"DATABASE ERROR in save_evaluation: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def _fetch_all_as_dicts(query, params=()):
    """Helper function to fetch evaluations and return them as a list of dictionaries."""
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
        # No commit/rollback needed for SELECT queries
        return [dict(row) for row in results]
    except Exception as e:
        print(f"DATABASE ERROR during fetch: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_evaluations():
    """Retrieve all evaluations, ordered by most recent."""
    return _fetch_all_as_dicts('SELECT * FROM evaluations ORDER BY timestamp DESC')

def search_evaluations(search_term):
    """Search evaluations by filename or verdict."""
    query = '''
    SELECT * FROM evaluations 
    WHERE job_description_filename ILIKE %s OR resume_filename ILIKE %s OR verdict ILIKE %s
    ORDER BY timestamp DESC
    '''
    like_term = f'%{search_term}%'
    return _fetch_all_as_dicts(query, (like_term, like_term, like_term))

def delete_evaluation(evaluation_id):
    """Delete a specific evaluation by its ID."""
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM evaluations WHERE id = %s', (evaluation_id,))
        conn.commit()
    except Exception as e:
        print(f"DATABASE ERROR in delete_evaluation: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def delete_all_evaluations():
    """Delete all evaluations and reset the table's counter."""
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute('TRUNCATE TABLE evaluations RESTART IDENTITY')
        conn.commit()
    except Exception as e:
        print(f"DATABASE ERROR in delete_all_evaluations: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def cleanup_old_records(days_to_keep):
    """Delete records from the database older than a specified number of days."""
    conn = get_db_connection()
    if not conn:
        return 0
        
    deleted_count = 0
    try:
        with conn.cursor() as cur:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cur.execute('DELETE FROM evaluations WHERE timestamp < %s', (cutoff_date,))
            deleted_count = cur.rowcount
        conn.commit()
    except Exception as e:
        print(f"DATABASE ERROR in cleanup_old_records: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()
    return deleted_count

