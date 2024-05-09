1. Download & setup Ngrok

2. Open CMD, run:
- cd command to navigate to Ngrok's destination folder
- $ngrok http 8000

3. Go to https://tmd-2001040053.atlassian.net/plugins/servlet/webhooks
   
5. Fill the Ngrok URL you've got in JIRA webhook (with '/webhook/' at the end of URL)

6. In settings.py, set up ALLOWED_HOSTS = ['Ngrok URL', 'localhost', '127.0.0.1']

7. Open terminal, run:
- pip install dependencies
- cd command to navigate to folder containing manage.py
- $python manage.py runserver

6. Open a JIRA project, create an issue
Now, you can go to http://localhost:4040/inspect/http to view the transmitted JSON.

7. The calculated result shows up in terminal, a CSV file is saved into your local PC

