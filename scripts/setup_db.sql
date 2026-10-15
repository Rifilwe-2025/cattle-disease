-- Optional: create the role and database for running this project on
-- PostgreSQL instead of the default SQLite.
--
-- The project runs on SQLite out of the box, so you only need this if you set
-- DB_ENGINE=postgresql in .env.
--
-- Run as a superuser from the project root:
--   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -f scripts\setup_db.sql
--
-- NOTE: this script deliberately contains no password. psql prompts you for
-- one and substitutes it, so the credential never lands in git. Put the same
-- password in .env as POSTGRES_PASSWORD (.env is gitignored).

\prompt 'Choose a password for the Admin_Ree role: ' admin_pw

-- Create the role only if it does not already exist. \gexec runs the string
-- the SELECT produces, which lets us do this without a DO block (a DO body is
-- a string literal, so :'admin_pw' would not be substituted inside one).
SELECT 'CREATE ROLE "Admin_Ree" WITH LOGIN CREATEDB'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'Admin_Ree')\gexec

-- Set (or reset) the password from the value you were prompted for.
ALTER ROLE "Admin_Ree" WITH LOGIN PASSWORD :'admin_pw' CREATEDB;

-- Settings Django expects.
ALTER ROLE "Admin_Ree" SET client_encoding TO 'utf8';
ALTER ROLE "Admin_Ree" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "Admin_Ree" SET timezone TO 'Africa/Harare';

-- Create the database if it is not there yet.
SELECT 'CREATE DATABASE cattle_disease_db OWNER "Admin_Ree" ENCODING ''UTF8'''
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'cattle_disease_db')\gexec

\echo 'Done. Set DB_ENGINE=postgresql and POSTGRES_PASSWORD in .env, then run: python manage.py migrate'
