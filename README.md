# Reports Generator

This is a utility accounting program meant to generate some management reports
for a small countryside marketplace according to Romania's financial legislation.
It features a simple wx-based UI to let the user select the reporting interval.

It connects to a Firebase database (local for now) to extract the data, then it
generates some Excel reports. The database is generated through [Saga](https://www.sagasoft.ro/), which is a popular accounting program that uses
a Firebird database.

## Steps on Windows

1. Set up a Python venv using Poetry:
    ```
    pip install pipx
    pipx install poetry
    pipx ensurepath
    poetry install
    Invoke-Expression (poetry env activate)
    ```

2. Install [Firebird Server 3.0](https://firebirdsql.org/en/server-packages/).

3. Set up environment variables (ensure you replace `sysdba` and `password` with your info)

    With cmd:
    ```
    set ISC_USER = "sysdba"
    set ISC_USER = "masterkey"
    ```

    With PowerShell:
    ```
    $env:ISC_USER = 'sysdba'
    $env:ISC_PASSWORD = 'masterkey'
    ```

4. Run the script
    ```
    python generate.py
    ```


## Saga firebase database

Saga exports the database as a Firebird backup database file. It can be converted
to an `.fdb` file with `gbak`:
```
gbak -recreate overwrite "FBK file" CONT_BAZA.FDB
```

If you have issues with database connection, please check if it's online or reset it:
```
gfix -user "sysdba" -password "masterkey" -shut full -force 0 CONT_BAZA.FDB
gfix -user "sysdba" -password "masterkey" -online CONT_BAZA.FDB
```

Note: The database should be placed under `C:` drive (not sure why this is a requirement).
Otherwise, the connection might fail.

## Config files

There are two configuration files that must exist:
- `config.cfg` - legacy config file used for input data + DBF configuration
- `database.cfg` - config file for Firebase configuration

Overview of `config.cfg` expected schema:
```
[Common]
Intrari: ./data/input/INTRARI.DBF
Produse: ./data/input/INTR_DET.DBF
Iesiri: ./data/input/iesiri.dbf
StartDate: 20250801

[Management]
SoldPrecedent: 0

[Journal]
PlatiNumerar: 0
PlatiAlte: 0
Incasari: 0
```

Overview of `firebird.cfg` expected schema:
```
[firebird.driver]
servers = local
databases = saga

[local]
host = localhost
user = SYSDBA
password = masterkey

[saga]
server = local
database = <path to FDB file>
protocol = inet
charset = utf8
```
