"""
Script to help set up PostgreSQL database for the project.
Run this to test PostgreSQL connection and create database if needed.
"""
import psycopg2
from psycopg2 import sql
import sys

def setup_database():
    """Set up PostgreSQL database."""
    print("=" * 60)
    print("PostgreSQL Database Setup")
    print("=" * 60)
    print()
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': input("Enter PostgreSQL password for user 'postgres': "),
        'database': 'postgres'  # Connect to default database first
    }
    
    db_name = 'cattle_disease_db'
    
    try:
        # Connect to PostgreSQL
        print("\n[1/3] Connecting to PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        
        # Check if database exists
        print(f"\n[2/3] Checking if database '{db_name}' exists...")
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s
        """, (db_name,))
        
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{db_name}' already exists!")
        else:
            # Create database
            print(f"\n[3/3] Creating database '{db_name}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"✓ Database '{db_name}' created successfully!")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("SUCCESS! Database is ready.")
        print("=" * 60)
        print(f"\nDatabase Name: {db_name}")
        print(f"User: {db_config['user']}")
        print(f"Host: {db_config['host']}")
        print(f"Port: {db_config['port']}")
        print("\nYou can now run: python manage.py migrate")
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ ERROR: Could not connect to PostgreSQL")
        print(f"Error: {e}")
        print("\nPossible issues:")
        print("1. PostgreSQL is not installed")
        print("2. PostgreSQL service is not running")
        print("3. Wrong password")
        print("4. Wrong host/port")
        print("\nThe system will use SQLite as fallback.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_database()
