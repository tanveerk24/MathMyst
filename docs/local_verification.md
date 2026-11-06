# Local database setup on this machine

An optional private MariaDB 10.4.32 instance was initialized specifically for verifying this project. It uses the existing XAMPP executable at `C:\xampp\mysql\bin\mysqld.exe`, but its data lives inside the project at `.local/mysql`. It listens only on **127.0.0.1:3307**. It does not use or replace `C:\xampp\mysql\data` and is separate from XAMPP's ordinary database instance.

This setup is local to this workspace and is excluded from Git. A fresh GitHub clone does not contain an initialized private database. For a different machine, follow the regular [README installation instructions](../README.md) using an installed MySQL/MariaDB service.

## Credentials and configuration

The local application and test connection values are stored in `.env`. A private administrator option file is stored in `.local/admin.cnf`. Both are ignored by Git. Do not print these files in screenshots or copy their passwords into commands, issue reports, or documentation.

The main application uses `MathMyst`; integration tests use the separate `mathmyst_test` database. The two connections use separate dedicated accounts. Neither ordinary application requests nor integration tests use the private administrator account.

## Start the existing private instance and application

Open PowerShell in the project directory:

```powershell
Set-Location 'C:\Users\Tanveer\OneDrive\Desktop\dbms project\MathMyst'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-LocalDatabase.ps1
python app.py
```

If you installed dependencies into the README's virtual environment, replace the last command with:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:5000**. The existing `.env` points the application at the private database on port 3307. The start helper launches the server in a hidden window and writes logs under `.local`. It validates the project datadir and will not initialize or repair a database.

The `-ExecutionPolicy Bypass` option applies only to this helper process; it does not change your saved PowerShell execution policy. If scripts are already permitted, invoking `.\scripts\Start-LocalDatabase.ps1` directly is sufficient.

If XAMPP was installed elsewhere, supply the equivalent executable from the MariaDB installation used to initialize this instance:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-LocalDatabase.ps1 -ServerExecutable 'D:\xampp\mysql\bin\mysqld.exe'
```

Do not point a different server version at this existing datadir without planning a database migration.

## Run verification

```powershell
python -m pytest -q
python -m pytest --integration -q
```

The integration suite loads the separate `TEST_DB_*` settings and enforces the test database name. With a virtual environment, use its Python executable in both commands. Inspect the actual pytest output for pass, failure, and skip counts on subsequent runs.

## Stop cleanly

Press **Ctrl+C** in the Flask terminal, then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Stop-LocalDatabase.ps1
```

The stop helper connects to port 3307, verifies that the server's actual datadir is this project's `.local/mysql`, and then asks `mysqladmin` to shut it down. Its administrator password is read from `.local/admin.cnf`; no password is passed as a command-line argument. It refuses to shut down an instance using a different datadir.

If the client lives elsewhere, pass `-AdminExecutable 'D:\xampp\mysql\bin\mysqladmin.exe'`. The matching `mysql.exe` must be in the same directory so the datadir check can run.

Do not delete `.local/mysql` to stop the server. If startup fails, inspect `.local/mysql-error.log`, `.local/mysql-stderr.log`, and `.local/mysql-stdout.log`. Preserve the data and resolve the reported error before restarting.

## Verification status

Verified on **6 November 2026** against this private **MariaDB 10.4.32** instance:

| Run | Result |
| --- | --- |
| `python -m pytest -q` | Integration tests are intentionally skipped by default |
| `python -m pytest --integration -q` | 140 passed in 7.78 seconds; no skipped tests |
| Optional SQL scripts | All five executed successfully; see [SQL verification](sql_verification.md) |
| Browser verification | Chrome rendered all three charts; no JavaScript exceptions; mobile navigation and SQL-query filtering passed |
| Responsive layouts | Overview, dashboard, three entity lists, problem/contribution forms, and SQL lab fit a 390px viewport |
| Offline charts | With the Chart.js CDN blocked, all three data tables remained visible and usable |
| Local database helpers | Clean shutdown, restart, and recognition of the already-running private instance succeeded |
| Dependency verification | `python -m pip check` reported no broken requirements |

Screenshots from the actual running application are available in [screenshots](screenshots/). MySQL 8 was not separately run, and its compatibility must not be presented as an independently completed verification. The normal unit command's skipped integration checks were subsequently exercised by the opt-in run above.
