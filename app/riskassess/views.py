from django.shortcuts import render
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from jira import JIRA
from datetime import datetime
from django.conf import settings
import logging
import json
import random
from sympy import limit

import os
import pandas as pd

logger = logging.getLogger(__name__)    # exception

# Create your views here.
@csrf_exempt  # Ignore checking CSRF
@api_view(['POST'])
def getData(request):
    
    try:
        getDataJira(request)
        return Response()
    except Exception as e:
        logger.error(f'Error processing request: {e}', exc_info=True)
        return Response(data = 'Internal error in server!', status=500 )

def getDataJira(request):
             
    jiraOptions = {
        'server': settings.JIRA['url']}

    jira = JIRA(options = jiraOptions,
                basic_auth=(settings.JIRA['username'], 
                            settings.JIRA['password'])
            )

    # JSON
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    # New issue
    issue = body['issue']
    # Get new issue key
    issue_key = body["issue"]["key"]
    # Get sprint id of new issue
    sprint_id = get_sprint_id(jira, issue_key)
    # Get that sprint duration
    sprint_duration = get_sprint_duration(jira, sprint_id)

    ## -------------------------------------------------------------
    # Calculation
    ## -------------------------------------------------------------
    r = 0.75
    p = 0.7
    l = 0.2
    a = 0.35
    c  = 0.75
    i1 = 0.5
    i = 0.58
    i2 = 0.46

    # c_max = integer   # based on each unique project's constraint
    # c1 = issue_key - 1st issue's key in the sprint

    # q = float         # custom field manually created on JIRA

    ## Calculate ej
    project_name = issue_key.split('-')[0].capitalize()  # Extract project name from issue_key

    if "MESOS" in project_name:
        b = 1.35
        b_id = 4
    elif "USERGRID" in project_name:
        b = 1.21
        b_id = 5
    else:       # AURORA
        b = 1.28
        b_id = 3

    x = random.randint(1, 10)
    ej = b / (x**(b+1))


    ### For each sprint
    sprints = jira.sprints(board_id = b_id)
    lc = len(sprints)

    sigma = 0
    for t, sprint in enumerate(sprints):
        # Fetch issues in the sprint
        issues = jira.search_issues(f'sprint = {sprint.id}')

        # Collect unique user count
        di = len(set(issue.fields.assignee.accountId for issue in issues if issue.fields.assignee))

        ts = r * p * (i + i1)
        ms = (c * i2 * (a + l)) ** di
        sigma += (ts/ms) ** (t+1)

    m_limit = limit(c1*ej/(q**di), c1, c_max)

    pr = sigma * m_limit    #pji value

    # Extra time state
    if ej > 0.1 * sprint_duration:
        ej_state = 'High'
    elif ej < 0.05 * sprint_duration:
        ej_state = 'Low'
    else:
        ej_state = 'Moderate'


    ## -------------------------------------------------------------
    # Export CSV
    ## -------------------------------------------------------------
    # Create DataFrame
    data = {'projectName': [project_name],
            'sprintID': [sprint_id],
            'issueKey': [issue_key],
            'extraTimeNeeded': [ej_state],
            'impactWeight': [pr]}
    df = pd.DataFrame(data)

    # Determine folder path based on issue_key
    folder_path = f"F:/{project_name}"

    # Check if folder exists, create if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create CSV file name
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{issue_key}_{current_date}.csv"
    file_path = os.path.join(folder_path, file_name)

    # Export DataFrame to CSV
    df.to_csv(file_path, index=False)

    # Display message to user
    print (ej)
    print(f"The extra time needed for Issue {issue_key} is: {ej_state}")
    print(f"The negative impact weight of Issue {issue_key} is: {pr}")

    message = f"Details of issue {issue_key} have been saved in {folder_path}"
    print(message)



def get_sprint_id(jira_client, issue_key):
    # Get info of issue
    issue = jira_client.issue(issue_key)

    # Access field "Sprint" of issue
    sprints = issue.fields.customfield_10020        # Custom field related to sprints
    
    # Extract sprintID from sprints
    sprint_ids = [sprint.id for sprint in sprints]
    sprint_id = sprint_ids[0]                       # 1st sprint that the issue joins

    return sprint_id

def get_sprint_duration(jira_client, sprint_id):
    # Fetch sprint details
    sprint = jira_client.sprint(sprint_id)

    # Get start and end dates
    start_date_str = sprint.raw['startDate']
    end_date_str = sprint.raw['endDate']

    # Convert date strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')

    # Calculate sprint duration
    sprint_duration = end_date - start_date

    return sprint_duration.days
