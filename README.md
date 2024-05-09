JIRA account (for testing only):
- Mail: myduieen0410@gmail.com
- Pass: tmd2001040053
- Site address: tmd-2001040053.atlassian.net
(Use this URL to log in to Jira Service Management)


Execution steps:
1. Download & setup Ngrok

2. Open CMD, run:
- cd command to navigate to Ngrok's destination folder
- $ngrok http 8000

3. Go to https://tmd-2001040053.atlassian.net/plugins/servlet/webhooks
Fill the Ngrok URL you've got in JIRA webhook (with '/webhook/' at the end of URL)

4. In settings.py, set up ALLOWED_HOSTS = ['Ngrok URL', 'localhost', '127.0.0.1']

5. Open terminal, run:
- pip install dependencies
- cd command to navigate to folder containing manage.py
- $python manage.py runserver

6. Open a JIRA project, create an issue
Now, you can go to http://localhost:4040/inspect/http to view the transmitted JSON.

7. The calculated result shows up in terminal, a CSV file is saved into your local PC

