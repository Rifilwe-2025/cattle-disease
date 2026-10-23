# Resetting the PostgreSQL superuser password

Only needed if `scripts/setup_postgres.py` rejects your `postgres` password.
PostgreSQL 18 on this machine uses `scram-sha-256`, so there is no way in
without either the password or Administrator rights.

Everything below needs an **Administrator** PowerShell: press Start, type
`PowerShell`, right-click → *Run as administrator*.

---

## Step 1 — Temporarily trust local connections

Open the host-based auth file:

```powershell
notepad "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
```

Near the bottom you will see lines like:

```
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

Change **only those two** `scram-sha-256` values to `trust`:

```
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
```

Save and close.

> `trust` means anyone on this machine can connect as any role with no
> password. That is why Step 4 puts it back. Do not leave it this way.

## Step 2 — Restart PostgreSQL

```powershell
Restart-Service postgresql-x64-18
```

## Step 3 — Set a new postgres password

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d postgres
```

You should get a `postgres=#` prompt with no password asked. Then:

```sql
ALTER USER postgres WITH PASSWORD 'your-new-superuser-password';
\q
```

Pick something you will remember — you need it in Step 5.

## Step 4 — Put the authentication back (do not skip)

Reopen `pg_hba.conf`, change those two `trust` values back to
`scram-sha-256`, save, then:

```powershell
Restart-Service postgresql-x64-18
```

Confirm it is enforced again — this **should** fail:

```powershell
$env:PGPASSWORD=""
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d postgres -w -c "SELECT 1;"
```

You want to see `no password supplied` or `password authentication failed`.
If it connects, `trust` is still active — recheck the file and restart again.

## Step 5 — Run the project setup

```powershell
cd "C:\Users\RifilweMbengo\Desktop\Early Disease Prediction For Cattle"
venv\Scripts\python.exe scripts\setup_postgres.py
```

Enter the password from Step 3 when asked for the superuser password, then
choose a new `Admin_Ree` password.

---

## If you would rather not touch PostgreSQL at all

The project already runs on SQLite with all your data — 6 users, 2 farmers,
3 vets, 6 applications, 22 cases. Just start it:

```powershell
venv\Scripts\python.exe manage.py runserver
```

SQLite is a perfectly legitimate choice for a capstone demo. PostgreSQL is
worth it if your assessors expect a client/server database, or if you want to
mention connection pooling and concurrent writes in your defence.
