#Spending tracking Django backend
<br>
# Database deployment

**Note**: All *.sql* files are located in [db](https://github.com/markojaadam/spending/tree/master/db) folder.

1. Install and [PostgreSQL](https://www.postgresql.org/download/).

2. Configure PostreSQL for password authentication: 
	a. Locate *pg_hba.conf* (on Linux: /etc/postgresql/XX/main/pg_hba.conf) wheere XX is the PostgreSQL version
	b. Change this line:
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            peer
```
	
to this

```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
```
in order to provide password authentication for the database.

  3. Login as *postgres* with `sudo -u postgres -i`
  4. Run `create_database.sh` script. This will create the role which will own
  the database itself. If this owner role is already exists the
  script will report error. Ignore it. After that, you can log off from postgres user with `exit`.
  5. Run
 
```bash
deploy_database.sh --target=all
```
   
This will create all the stuff in the newly created database.

## Notes on development

Every time you want to redeploy the entire database objects, run:

```bash
cd db
deploy_database.sh --target=all --rebuild
```
And than repeat the deploy procedure.

If you only want to recreate the API schema (containing only the database function) run

```bash
cd db
deploy_database.sh --target=api --rebuild
```

# Server deployment
- clone repository
- (optional): Create and activate virtual environment
```bash
python3 -m venv $HOME/venv
source $HOME/venv/bin/activate
```
- install requirements
```bash
python3 -m pip install -r requirements.txt
```
- add secrets
create `.secret` folder and place a `config.json` file in it with the following content:

```json
{
  "server": {
    "secret_key": "django_top_secret"
  },
  "db": {
    "dbname": "spending",
    "username": "test",
    "password": "test",
    "host": "localhost",
    "port": 5432
  }
}


```	

## Debug mode
run `python3 manage.py runserver`

## Production mode
- copy init.d script into /etc/init.d/
```bash
sudo cp initd_script.sh /etc/init.d/gunicorn-spending
sudo chmod +x /etc/init.d/gunicorn-spending
```
**note**: set the parameters above in the script according to the local setup:
```
USER=ubuntu
APP_HOME=/usr/local/src/spending/
APP_PATH=80
ACTIVATE=/home/ubuntu/venv/bin/activate
```

- start init.d script
```bash
sudo /etc/init.d/gunicorn-spending start
```

# API

The API is fully JSON-based.

## Validation

The backend has 3 layers of validation:
- JSON schema: all POST methods go through JSON schema validation. The validation schemas are defined in [json_schema.py](https://github.com/markojaadam/spending/blob/master/spending/json_schema.py)
- Server-side code validation: a few additional step for errors
- Database validation: database raises custom SQLstates for each kind of common

## Getting our own spending

Performed by simple GET method.
Optional query parameters:
- order_by: order the output based in the selected property
- currency: filter the output by the selected currency
```bash
curl -l {API_URL}/getspending?currency=HUF&order_by=amount
```
-> outputs:

list of spendings
```json
{"ok": 1, "data": [{"id": 21, "amount": 1, "reason": null, "date": 1598236973}]}
```
## Submit a new spending

Add a new spending to the database with POST:

```bash
curl -l -X POST {API_URL}/addspending --data '{"amount": 1, "currency": "USD", "reason": "shopping lollipop", "date": 1598538717}'
```
**note**: all object properties are required

-> outputs:

the ID of the new entry on successful creation:
```json
{"ok": 1, "params": {"id": 432}}
```

## Delete a spending
Deletes the sending from the database referenced by its ID:
```bash
curl -l -X POST {API_URL}/deletespending --data '{"id":432}'
```
-> outputs ack.

```json
{"ok": 1}
```

## Update a spending
Updates a spending referenced by its ID:
```bash
curl -l -X POST {API_URL}/updatespending --data '{"amount": 1, "currency": "USD", "id": 432, "reason": "shopping candy", "date": 1598538717}'
```
**note**: all object properties are required

-> outputs ack.

```json
{"ok": 1}
```

# Testing

the following test tools can be found in [tool](https://github.com/markojaadam/spending/tree/master/tool) folder:

## debug_core.py

Holds the main functions for the debugger modules.

**note:** Don't forget to replace the API_URL paramter according to the server setup:

```py
API_URL = 'http://localhost:8000/
```
 
## debug_pentest.py
 
 Usage: 
```bash
python3 pentest.py
```
It runs basic unittests on server-side validation of POST requests and penetration test:
- sends malformed JSON
- sends json with invalid values (e.g. negative amount, future times)
- sends json data containing database errors (update entries with non-existing ID)
- sends multiple concurrent requests
 
## debug_cli.py

A click-based command line client to test api with full functionality:
<br>
**./debug_cli.py add-spending**
add a spending to the database with the following arguments:
```bash
--amount (amount of spending, must be greater than zero)
--currency (3-letter ISO currency code)
--reason (description of spending, nullable)
--date (date of spending in UNIX epoch, must be less than the current time)
--debug (output verbosity: silent: no output, payload: only the server resposne, error: only server responses containing errors, all: both cient request and server response)
```
  example:
```bash
./debug_cli.py add-spending --amount=1 --currency=USD --reason=shopping --date=1598538717 --debug=all
```
  **./debug_cli.py delete-spending`**
  delete a spending using its ID:
  
```bash
--id (id of the to-be-deleted spending)
--debug
```
  example:
```bash
./debug_cli.py delete-spending --id=1 --debug=all
```
  
 **./debug_cli.py update-spending**

update a spending based on its id with the following arguments:
```bash
--id (id of the to-be-updated spending)
--amount (amount of spending, must be greater than zero)
--currency (3-letter ISO currency code)
--reason (description of spending, nullable)
--date (date of spending in UNIX epoch, must be less than the current time)
--debug (output verbosity: silent: no output, payload: only the server resposne, error: only server responses containing errors, all: both cient request and server response)
```
  example:
```bash
./debug_cli.py update-spending --id=1 --amount=1 --currency=USD --reason=shopping --date=1598538717 --debug=all
```

 **./debug_cli.py get-spending**
 get all or some of the spendings according to the following:
```bash
--order-by (order the output based on the selected aspect: amount/currency/date; default: date)
--currency (get selective output for a picked currency)
```
the output will be formatted innto command-line table.