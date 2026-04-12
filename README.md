# MDCU Connect LINE OA Backend

## Set up project locally

### Prerequisite
- Python
- MySQL
- Cloudflare

### Set up backend service
1. On your terminal, navigate to the desired workspace and clone the project
```bash
git clone git@github.com:docchula/mdcuconnect-lineoa-backend.git
```

2. Navigate to project directory
```bash
cd mdcuconnect-lineoa-backend
```

3. Create a virtual environment for python
```bash
python3 -m venv venv
```

4. Activate the Environment
```bash
source venv/bin/activate
```

5. Install dependencies
```bash
python3 -m pip install -r requirements_dev.txt
```

6. Install pre-commit
```bash
pre-commit install
```

7. Copy environtment template file `.env-t` to `.env` file

### Set up database
1. Create a new MySQL database
```sql
CREATE DATABASE <DB_NAME> CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
```

2. Create a user with password
```sql
CREATE USER '<DB_USER>'@'localhost' IDENTIFIED BY '<DB_PASSWORD>';
```

3. Grant privileges on the database to your user
```sql
GRANT ALL PRIVILEGES ON <DB_NAME>.* TO '<DB_USER>'@'localhost';
FLUSH PRIVILEGES;
```

4. Update `.env`
```bash
DB_NAME=<DB_NAME>
DB_USERNAME=<DB_USER>
DB_PASSWORD=<DB_PASSWORD>
DB_HOST=localhost
DB_PORT=3306
```

### Set up LINE OA
1. Go to https://account.line.biz/login and login with your LINE account

2. On the left menu bar, create a new OA

3. After created account, click on `Chat` tab, it will navigate you to `Response settings` page, then click on `Messaging API settings` and click enable. It will ask you to create a new provider

4. After created provider, you will see `Channel ID` and `Channel Secret`, update your `.env` according to the values

5. Click on `LINE Developers Console` and select the provider you just created, then create a new Messaging API channel

6. In Messaging API channel, click on `Messaging API` tab and scroll down to the bottom, you will see the `Channel access token`

7. Click `Issue` and copy the token to `LINE_CHANNEL_ACCESS_TOKEN` in `.env`

### Set up cloudflare tunnel for webhook url
1. On your terminal, run the backend service
```bash
python3 manage.py runserver
```
the service should run on http://localhost:8000 or http://127.0.0.1:8000

2. On another terminal, run
```bash
cloudflared tunnel --url http://localhost:8000
```
you should see the quick tunnel url. For example: https://combination-grades-track-thesaurus.trycloudflare.com

3. Copy the quick tunnel url and paste it in LINE OA webhook url, also append `/webhook/callback/` at the end of the quick tunnel url. For example: https://combination-grades-track-thesaurus.trycloudflare.com/webhook/callback/

4. At this point, you should be able to interact with the LINE OA

### Run celery
1. Open a new terminal and active the environment

2. Run the following command:
```bash
celery -A website worker -l info
```
