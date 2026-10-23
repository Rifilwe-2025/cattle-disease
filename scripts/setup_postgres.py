"""
One-shot PostgreSQL setup: create the role and database, move the SQLite data
across, and verify the result.

Run from the project root:

    venv\\Scripts\\python.exe scripts\\setup_postgres.py

It prompts for two passwords and echoes neither:

  1. The PostgreSQL superuser ('postgres') password - used only for this
     session to create the role, never written anywhere.
  2. A NEW password for the Admin_Ree role - written only to .env, which is
     gitignored. Pick something other than the old @ADMIN2026, which is
     public in this repo's git history.

What it does, in order:
  - creates or updates the Admin_Ree role with the new password
  - creates cattle_disease_db owned by that role, if absent
  - points .env at PostgreSQL (preserving your other .env values)
  - runs migrate on the new database
  - loads backups/data-from-sqlite.json
  - RESETS SEQUENCES. This step matters: 220 of the 226 fixture objects carry
    explicit primary keys, and PostgreSQL does not advance a sequence when a
    row is inserted with an explicit id. Without this, the next case a farmer
    submits would fail with a duplicate key error.
  - prints row counts so you can confirm nothing was lost

Safe to re-run. Your SQLite file is left untouched, so you can switch back by
removing DB_ENGINE from .env.
"""
from __future__ import annotations

import getpass
import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
FIXTURE = BASE_DIR / 'backups' / 'data-from-sqlite.json'
PY = BASE_DIR / 'venv' / 'Scripts' / 'python.exe'
MANAGE = BASE_DIR / 'manage.py'

DB_NAME = 'cattle_disease_db'
DB_USER = 'Admin_Ree'
APPS_WITH_DATA = ['accounts', 'farmers', 'vets', 'cases']


def die(msg: str, code: int = 1):
    print('\nERROR: ' + msg)
    sys.exit(code)


def step(n, total, msg):
    print(f'\n[{n}/{total}] {msg}')


def run_manage(args: list[str], env: dict) -> subprocess.CompletedProcess:
    """Run a management command in a subprocess so it reads the new .env."""
    return subprocess.run(
        [str(PY), str(MANAGE), *args],
        cwd=str(BASE_DIR), env=env, capture_output=True, text=True,
    )


def update_env(new_password: str) -> None:
    """Point .env at PostgreSQL, preserving every other value already there."""
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding='utf-8').splitlines()

    managed = {
        'DB_ENGINE': 'postgresql',
        'POSTGRES_DB': DB_NAME,
        'POSTGRES_USER': DB_USER,
        'POSTGRES_PASSWORD': new_password,
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
    }

    STALE_HINT = 'uncomment to use postgresql'

    out, seen = [], set()
    for line in lines:
        # This placeholder comment sits above the commented-out block and
        # reads as a contradiction once the block is live, so drop it.
        if STALE_HINT in line.lower():
            continue
        m = re.match(r'^\s*#?\s*([A-Z_]+)\s*=', line)
        key = m.group(1) if m else None
        if key in managed:
            if key not in seen:
                out.append(f'{key}={managed[key]}')
                seen.add(key)
            continue          # drop duplicates and commented-out variants
        out.append(line)

    missing = [k for k in managed if k not in seen]
    if missing:
        if out and out[-1].strip():
            out.append('')
        out.append('# PostgreSQL (written by scripts/setup_postgres.py)')
        out.extend(f'{k}={managed[k]}' for k in missing)

    ENV_PATH.write_text('\n'.join(out) + '\n', encoding='utf-8')


def main() -> int:
    print('=' * 68)
    print('PostgreSQL setup for CattleCare AI')
    print('=' * 68)

    if not PY.exists():
        die(f'virtualenv python not found at {PY}')
    if not FIXTURE.exists():
        die(f'fixture not found at {FIXTURE}\n'
            'Generate it first with:\n'
            '  venv\\Scripts\\python.exe manage.py dumpdata --natural-foreign '
            '--natural-primary -e contenttypes -e auth.Permission '
            '-e admin.logentry -e sessions.session --indent 2 '
            '-o backups/data-from-sqlite.json')

    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        die('psycopg2 is not installed. Run:\n'
            '  venv\\Scripts\\python.exe -m pip install psycopg2-binary')

    TOTAL = 7

    # ---- credentials ----------------------------------------------------
    super_pw = getpass.getpass("\nPostgreSQL superuser ('postgres') password: ")
    if not super_pw:
        die('no password entered')

    print('\nNow choose a NEW password for the Admin_Ree role.')
    print('Do not reuse @ADMIN2026 - it is public in this repo\'s git history.')
    new_pw = getpass.getpass('New Admin_Ree password: ')
    if len(new_pw) < 8:
        die('please choose at least 8 characters')
    if new_pw != getpass.getpass('Confirm new password: '):
        die('passwords did not match')
    if new_pw == '@ADMIN2026':
        die('that is the exposed password - please pick a different one')

    # ---- 1. connect as superuser ----------------------------------------
    step(1, TOTAL, 'Connecting to PostgreSQL as superuser...')
    try:
        conn = psycopg2.connect(host='localhost', port=5432, user='postgres',
                                password=super_pw, dbname='postgres',
                                connect_timeout=10)
    except psycopg2.OperationalError as e:
        msg = str(e).strip()
        hint = ''
        if 'password authentication failed' in msg:
            hint = ('\n\nThat password was rejected. If you do not remember the '
                    'postgres password, see RESET_POSTGRES_PASSWORD.md for how '
                    'to reset it (needs Administrator).')
        die(f'could not connect: {msg}{hint}')
    conn.autocommit = True
    cur = conn.cursor()
    print('      connected')

    # ---- 2. role --------------------------------------------------------
    step(2, TOTAL, f'Creating/updating role "{DB_USER}"...')
    cur.execute('SELECT 1 FROM pg_roles WHERE rolname = %s', (DB_USER,))
    exists = cur.fetchone() is not None
    if exists:
        cur.execute(sql.SQL('ALTER ROLE {} WITH LOGIN CREATEDB PASSWORD %s')
                    .format(sql.Identifier(DB_USER)), (new_pw,))
        print('      role existed - password updated')
    else:
        cur.execute(sql.SQL('CREATE ROLE {} WITH LOGIN CREATEDB PASSWORD %s')
                    .format(sql.Identifier(DB_USER)), (new_pw,))
        print('      role created')

    for setting, value in [('client_encoding', 'utf8'),
                           ('default_transaction_isolation', 'read committed'),
                           ('timezone', 'Africa/Harare')]:
        cur.execute(sql.SQL('ALTER ROLE {} SET {} TO %s').format(
            sql.Identifier(DB_USER), sql.Identifier(setting)), (value,))

    # ---- 3. database ----------------------------------------------------
    step(3, TOTAL, f'Creating database "{DB_NAME}"...')
    cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (DB_NAME,))
    if cur.fetchone():
        print('      database already exists - leaving it in place')
    else:
        cur.execute(sql.SQL('CREATE DATABASE {} OWNER {} ENCODING {}').format(
            sql.Identifier(DB_NAME), sql.Identifier(DB_USER),
            sql.Literal('UTF8')))
        print('      database created')
    cur.close()
    conn.close()

    # ---- 4. .env --------------------------------------------------------
    step(4, TOTAL, 'Pointing .env at PostgreSQL...')
    update_env(new_pw)
    print(f'      {ENV_PATH.name} updated (gitignored; other values preserved)')

    env = os.environ.copy()
    env.update({
        'DB_ENGINE': 'postgresql', 'POSTGRES_DB': DB_NAME,
        'POSTGRES_USER': DB_USER, 'POSTGRES_PASSWORD': new_pw,
        'POSTGRES_HOST': 'localhost', 'POSTGRES_PORT': '5432',
        'PYTHONIOENCODING': 'utf-8',
    })

    # ---- 5. migrate -----------------------------------------------------
    step(5, TOTAL, 'Running migrations on the new database...')
    r = run_manage(['migrate', '--noinput'], env)
    if r.returncode != 0:
        die('migrate failed:\n' + (r.stderr or r.stdout)[-2500:])
    applied = [l.strip() for l in r.stdout.splitlines()
               if 'Applying' in l or 'No migrations' in l]
    if applied:
        for line in applied[:40]:
            print('      ' + line)
    else:
        print('      done')

    # ---- 6. load data + reset sequences ---------------------------------
    step(6, TOTAL, 'Loading your data...')
    r = run_manage(['loaddata', str(FIXTURE)], env)
    if r.returncode != 0:
        die('loaddata failed:\n' + (r.stderr or r.stdout)[-2500:])
    print('      ' + (r.stdout.strip().splitlines() or ['done'])[-1])

    print('      resetting sequences (required after loading explicit ids)...')
    r = run_manage(['sqlsequencereset', *APPS_WITH_DATA], env)
    if r.returncode != 0:
        die('sqlsequencereset failed:\n' + (r.stderr or r.stdout)[-1500:])
    reset_sql = '\n'.join(
        l for l in r.stdout.splitlines()
        if l.strip() and not l.lstrip().startswith('--')
    )
    if reset_sql.strip():
        import psycopg2 as pg
        c2 = pg.connect(host='localhost', port=5432, user=DB_USER,
                        password=new_pw, dbname=DB_NAME, connect_timeout=10)
        c2.autocommit = True
        cc = c2.cursor()
        cc.execute(reset_sql)
        cc.close()
        c2.close()
        print('      sequences reset')
    else:
        print('      nothing to reset')

    # ---- 7. verify ------------------------------------------------------
    step(7, TOTAL, 'Verifying...')
    probe = (
        "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE',"
        "'cattle_disease_system.settings'); django.setup();"
        "from django.db import connection;"
        "from accounts.models import User;"
        "from farmers.models import Farmer;"
        "from vets.models import Vet, VetApplication;"
        "from cases.models import Case, Disease, Symptom;"
        "print('      engine :', connection.vendor);"
        "print('      database:', connection.settings_dict['NAME']);"
        "print('      users=%d farmers=%d vets=%d applications=%d cases=%d '"
        "'diseases=%d symptoms=%d' % (User.objects.count(), Farmer.objects.count(),"
        "Vet.objects.count(), VetApplication.objects.count(), Case.objects.count(),"
        "Disease.objects.count(), Symptom.objects.count()))"
    )
    r = subprocess.run([str(PY), '-c', probe], cwd=str(BASE_DIR), env=env,
                       capture_output=True, text=True)
    print(r.stdout.rstrip() or r.stderr[-1200:])

    print('\n' + '=' * 68)
    print('Done. The project is now on PostgreSQL.')
    print('=' * 68)
    print('\nStart it with:  venv\\Scripts\\python.exe manage.py runserver')
    print('To go back to SQLite: delete the DB_ENGINE line from .env')
    print('\nYour SQLite file and backups/data-from-sqlite.json are untouched.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
