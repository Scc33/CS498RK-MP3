#!/usr/bin/env python

"""
 * @file test.py
 *
 * @author Sean Coughlin
 * @date Created: Fall 2021
"""

import sys
import getopt
import http.client
import urllib
import json
from datetime import date
from time import mktime

def usage():
    print('dbFill.py -u <baseurl> -p <port> -n <numUsers> -t <numTasks>')

def getUsers(conn):
    # Retrieve the list of users
    conn.request("GET","""/api/users?filter={"_id":1}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)

    # Array of user IDs
    users = [str(d['data'][x]['_id']) for x in range(len(d['data']))]

    return users

def main(argv):
    # Server Base URL and port
    baseurl = "localhost"
    port = 4000

    # Number of POSTs that will be made to the server
    userCount = 5
    taskCount = 5

    # Python array containing common first names and last names
    firstNames = ["james","john","robert","michael","william"]
    lastNames = ["smith","johnson","williams","jones","brown"]

    # Server to connect to (1: url, 2: port number)
    conn = http.client.HTTPConnection(baseurl, port)

    # HTTP Headers
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}

    # Array of user IDs
    userIDs = []
    userNames = []

    # Loop 'userCount' number of times
    for i in range(userCount):
        params = urllib.parse.urlencode({'name': firstNames[i] + " " + lastNames[i], 'email': firstNames[i] + "@" + lastNames[i] + ".com"})

        # POST the user
        conn.request("POST", "/api/users", params, headers)
        response = conn.getresponse()
        data = response.read()
        d = json.loads(data)
        print(d)
        assert(response.status == 201)

        # Store the users id
        userIDs.append(str(d['data']['_id']))
        userNames.append(str(d['data']['name']))

    taskName = ["1","2","3","4","5"]
    taskDescription = ["1","2","3","4","5"]
    taskDeadline = [(mktime(date.today().timetuple())) * 1000 for i in range(taskCount)]
    taskCompleted = [False, False, False, False, False]
    taskIDs = []

    # Loop 'taskCount' number of times
    for i in range(taskCount):
        params = urllib.parse.urlencode({'name': taskName[i], 'deadline': taskDeadline[i], 'assignedUserName': userNames[i], 'assignedUser': userIDs[i], 'completed': str(taskCompleted[i]).lower(), 'description': taskDescription[i]})

        # POST the task
        conn.request("POST", "/api/tasks", params, headers)
        response = conn.getresponse()
        assert(response.status == 201)
        data = response.read()
        d = json.loads(data)
        taskIDs.append(str(d['data']['_id']))

        taskID = str(d['data']['_id'])

        # Make sure the task is added to the pending list of the user
        # GET the correct user
        conn.request("GET","""/api/users?where={"_id":\""""+userIDs[i]+"""\"}""")
        response = conn.getresponse()
        assert(response.status == 200)
        assert(response.reason == "OK")
        data = response.read()
        d = json.loads(data)

        # Store all the user properties
        assignedUserName = str(d['data'][0]['name'])
        assignedUserEmail = str(d['data'][0]['email'])
        assignedUserDate = str(d['data'][0]['dateCreated'])

        # Append the new taskID to pending tasks
        assignedUserTasks = d['data'][0]['pendingTasks']
        print(assignedUserTasks)
        assignedUserTasks = [str(x).replace('[','').replace(']','').replace("'",'').replace('"','') for x in assignedUserTasks]
        #assignedUserTasks.append(taskID)

        # PUT in the user
        params = urllib.parse.urlencode({'_id': userIDs[i], 'name': assignedUserName, 'email': assignedUserEmail, 'dateCreated': assignedUserDate, 'pendingTasks': assignedUserTasks}, True)
        conn.request("PUT", "/api/users/"+userIDs[i], params, headers)
        response = conn.getresponse()
        print(response.status)
        assert(response.status == 200)
        assert(response.reason == "OK")
        data = response.read()
        d = json.loads(data)

        conn.request("GET","""/api/users?where={"_id":\""""+userIDs[i]+"""\"}""")
        response = conn.getresponse()
        assert(response.status == 200)
        assert(response.reason == "OK")
        data = response.read()
        d = json.loads(data)
        print(d['data'][0]['pendingTasks'])

    # Retrieve the list of users
    conn.request("GET","/api/users")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['pendingTasks'][0] == taskIDs[0])
    assert(d['data'][1]['pendingTasks'][0] == taskIDs[1])
    assert(d['data'][2]['pendingTasks'][0] == taskIDs[2])
    assert(d['data'][3]['pendingTasks'][0] == taskIDs[3])
    assert(d['data'][4]['pendingTasks'][0] == taskIDs[4])
    assert(d['data'][0]['name']==userNames[0])
    assert(d['data'][1]['name']==userNames[1])
    assert(d['data'][2]['name']==userNames[2])
    assert(d['data'][3]['name']==userNames[3])
    assert(d['data'][4]['name']==userNames[4])
    assert(d['data'][0]['email']==firstNames[0]+"@"+lastNames[0]+".com")
    assert(d['data'][1]['email']==firstNames[1]+"@"+lastNames[1]+".com")

    # Test query
    conn.request("GET","""/api/users?filter={"_id":1}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['pendingTasks'][0] == taskIDs[0])
    assert(d['data'][1]['pendingTasks'][0] == taskIDs[1])
    assert(d['data'][2]['pendingTasks'][0] == taskIDs[2])
    assert(d['data'][3]['pendingTasks'][0] == taskIDs[3])
    assert(d['data'][4]['pendingTasks'][0] == taskIDs[4])
    assert(d['data'][0]['name']==userNames[0])
    assert(d['data'][1]['name']==userNames[1])
    assert(d['data'][2]['name']==userNames[2])
    assert(d['data'][3]['name']==userNames[3])
    assert(d['data'][4]['name']==userNames[4])
    assert(d['data'][0]['email']==firstNames[0]+"@"+lastNames[0]+".com")
    assert(d['data'][1]['email']==firstNames[1]+"@"+lastNames[1]+".com")

    # Test query
    conn.request("GET", """http://localhost:4000/api/users?sort={"name":1}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['name'] == userNames[0])
    assert(d['data'][1]['name'] == userNames[1])
    assert(d['data'][2]['name'] == userNames[3])
    assert(d['data'][3]['name'] == userNames[2])

    conn.request("GET", """http://localhost:4000/api/users?sort={"name":-1}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['name'] == userNames[4])
    assert(d['data'][1]['name'] == userNames[2])
    assert(d['data'][2]['name'] == userNames[3])
    assert(d['data'][3]['name'] == userNames[1])
    assert(d['data'][4]['name'] == userNames[0])

    # Test query with limit
    conn.request("GET", """http://localhost:4000/api/users?sort={"name":1}&limit=2""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['name'] == userNames[0])
    assert(d['data'][1]['name'] == userNames[1])
    assert(len(d['data']) == 2)

    # Test query with skip
    conn.request("GET", """http://localhost:4000/api/users?sort={"name":1}&skip=2""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    print(d['data'])
    assert(d['data'][0]['name'] == userNames[3])
    assert(d['data'][1]['name'] == userNames[2])
    assert(len(d['data']) == 3)

    # Test count
    conn.request("GET", """http://localhost:4000/api/users?count=true""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'] == 5)

    # Test count
    conn.request("GET", """http://localhost:4000/api/users?count=true&limit=3""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'] == 3)

    # Test count
    conn.request("GET", """/api/users?count=true&skip=3""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'] == 2)

    # Test query
    conn.request("GET", """http://localhost:4000/api/tasks?sort={"name":1}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['name'] == taskName[0])
    assert(d['data'][1]['name'] == taskName[1])
    assert(d['data'][2]['name'] == taskName[2])
    assert(d['data'][3]['name'] == taskName[3])

    conn.request("GET", """http://localhost:4000/api/tasks?sort={"name":-1}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['name'] == taskName[4])
    assert(d['data'][1]['name'] == taskName[3])
    assert(d['data'][2]['name'] == taskName[2])
    assert(d['data'][3]['name'] == taskName[1])
    assert(d['data'][4]['name'] == taskName[0])

    # Test query with limit
    conn.request("GET", """http://localhost:4000/api/tasks?sort={"name":1}&limit=2""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['name'] == taskName[0])
    assert(d['data'][1]['name'] == taskName[1])
    assert(len(d['data']) == 2)

    # Test query with skip
    conn.request("GET", """http://localhost:4000/api/tasks?sort={"name":1}&skip=2""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    print(d['data'])
    assert(d['data'][0]['name'] == taskName[2])
    assert(d['data'][1]['name'] == taskName[3])
    assert(len(d['data']) == 3)

    # Test count
    conn.request("GET", """http://localhost:4000/api/tasks?count=true""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'] == 5)

    # Test count
    conn.request("GET", """http://localhost:4000/api/tasks?count=true&limit=3""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'] == 3)

    # Test count
    conn.request("GET", """/api/tasks?count=true&skip=3""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'] == 2)

    # Test update (valid)
    params = urllib.parse.urlencode({'name': "myname", 'email': "myname@test.com"})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(response.status, d)
    assert(response.status == 201)
    conn.request("GET", """/api/users?where={"name":"myname"}""") 
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(response.status == 200)
    assert(len(d['data']) == 1)
    print(d)
    assert(d['data'][0]['name'] == "myname")
    assert(d['data'][0]['email'] == "myname@test.com")
    userID = d['data'][0]['_id']
    params = urllib.parse.urlencode({'name': "mynameupdated", 'email': "mynameupdated@test.com"})
    conn.request("PUT", "/api/users/" + userID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data']['name'] == "mynameupdated")
    conn.request("GET", """/api/users?where={"name":"mynameupdated"}""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d['data'][0]['email'] == "mynameupdated@test.com")
    
    # Test update (invalid)
    params = urllib.parse.urlencode({'name': "mynamebad", 'email': ''})
    conn.request("PUT", "/api/users/" + userID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 400)

    # Get invalid user
    conn.request("GET", """/api/users/41224d776a326fb40f000001""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(response.status, d)
    assert(response.status == 404)

    # Get invalid task
    conn.request("GET", """/api/tasks/41224d776a326fb40f000001""")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 404)

    # Insert an incomplete user
    params = urllib.parse.urlencode({'name': "", 'email': "test@test.com"})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and email")
    params = urllib.parse.urlencode({'name': "", 'email': ""})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and email")
    params = urllib.parse.urlencode({'name': "asdf", 'email': ""})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and email")

    # Insert an incomplete task
    params = urllib.parse.urlencode({'name': "", 'deadline': taskDeadline[i]})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Missing fields, need name and deadline to post a task")
    params = urllib.parse.urlencode({'name': "", 'deadline': ""})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Missing fields, need name and deadline to post a task")
    params = urllib.parse.urlencode({'name': "asdf", 'deadline': ""})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Missing fields, need name and deadline to post a task")

    # Update an incomplete user
    params = urllib.parse.urlencode({'name': "", 'email': "test@test.com"})
    conn.request("PUT", "/api/users/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and email")
    params = urllib.parse.urlencode({'name': "", 'email': ""})
    conn.request("PUT", "/api/users/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and email")
    params = urllib.parse.urlencode({'name': "asdf", 'email': ""})
    conn.request("PUT", "/api/users/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and email")

    # Update an incomplete task
    params = urllib.parse.urlencode({'name': "", 'deadline': taskDeadline[i]})
    conn.request("PUT", "/api/tasks/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Missing fields, need name and deadline to put a task")
    params = urllib.parse.urlencode({'name': "", 'deadline': ""})
    conn.request("PUT", "/api/tasks/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Missing fields, need name and deadline to put a task")
    params = urllib.parse.urlencode({'name': "asdf", 'deadline': ""})
    conn.request("PUT", "/api/tasks/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Missing fields, need name and deadline to put a task")

    # Multiple users with the same email
    params = urllib.parse.urlencode({'name': "duplicate", 'email': "test@test.com"}) 
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    duplicateUserID = d["data"]["_id"]
    assert(response.status == 201)
    params = urllib.parse.urlencode({'name': "duplicate", 'email': "test@test.com"}) 
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, that email is already in use")
    params = urllib.parse.urlencode({'name': "duplicate", 'email': "test@test.com"})
    conn.request("PUT", "/api/users/" + userIDs[0], params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, that email is already in use")
    conn.request("DELETE", "/api/users/" + duplicateUserID, params, headers)
    response = conn.getresponse()
    assert(response.status == 200)
    data = response.read()

    # Delete an invalid task
    bad = str("41224d776a326fb40f000001")
    conn.request("DELETE", "/api/tasks/" + bad)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(response.status)
    print(d)
    assert(response.status == 404)

    # Delete an invalid user
    bad = str("41224d776a326fb40f000001")
    conn.request("DELETE", "/api/users/" + bad)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(response.status)
    print(d)
    assert(response.status == 404)

    # Delete a task that doesn't belong to the user
    params = urllib.parse.urlencode({'name': "unrelated", 'deadline': taskDeadline[i]})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    taskID = d["data"]["_id"]
    assert(response.status == 201)
    conn.request("DELETE", "/api/tasks/" + taskID)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)

    # Delete a user and check accompying tasks
    # breakpoint()
    conn.request("DELETE", "/api/users/" + userIDs[0])
    response = conn.getresponse()
    data = response.read()
    assert(response.status == 200)
    conn.request("GET", "/api/tasks/" + taskIDs[0])
    response = conn.getresponse()
    assert(response.status == 200)
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(d["data"]["assignedUser"] == "")
    assert(d["data"]["assignedUserName"] == "unassigned")

    # Delete a task and check accompying users
    conn.request("DELETE", "/api/tasks/" + taskIDs[1])
    response = conn.getresponse()
    data = response.read()
    assert(response.status == 200)
    conn.request("GET", "/api/users/" + userIDs[1])
    response = conn.getresponse()
    assert(response.status == 200)
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(len(d["data"]["pendingTasks"]) == 0)

    # Create a user a populate the task (post)
    params = urllib.parse.urlencode({'name': "user1", 'email': "user1@gmail"}) 
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    userID = d["data"]["_id"]
    assert(response.status == 201)
    params = urllib.parse.urlencode({'name': "task1", 'deadline': taskDeadline[i], 'assignedUser': userID, 'assignedUserName': "user1"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 201)
    conn.request("GET", "/api/users/" + userID)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(len(d["data"]["pendingTasks"]) == 1)

    # Create a task and populate the user (post)
    params = urllib.parse.urlencode({'name': "task2", 'deadline': taskDeadline[i], 'assignedUser': userID})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    taskID = d["data"]["_id"]
    assert(response.status == 201)
    pendingTasks = taskID
    params = urllib.parse.urlencode({'name': "user2", 'email': "user2t@gmail", "pendingTasks": pendingTasks})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(response.status == 201)
    conn.request("GET", "/api/tasks/" + taskID)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    print(d["data"]["assignedUser"], userID)
    assert(d["data"]["assignedUser"] == userID)

    # Create a user a populate the task, Create a task and populate the user (put)
    params = urllib.parse.urlencode({'name': "user3", 'email': "user3t@gmail"})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    userID = d["data"]["_id"]
    assert(response.status == 201)
    params = urllib.parse.urlencode({'name': "task3", 'deadline': taskDeadline[i], 'assignedUser': userID, 'assignedUserName': "user3"})
    conn.request("PUT", "/api/tasks/" + taskID, params, headers)
    response = conn.getresponse()
    print(response.status, taskID, userID)
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    conn.request("GET", "/api/users/" + userID)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(len(d["data"]["pendingTasks"]) == 1)
    params = urllib.parse.urlencode({'name': "user3updated", 'email': "user3@gmail"})
    conn.request("PUT", "/api/users/" + userID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(d["data"]["name"] == "user3updated")
    assert(d["data"]["_id"] == userID)
    assert(response.status == 200)
    conn.request("GET", "/api/tasks/" + taskID)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(response.status == 200)
    assert(d["data"]["assignedUserName"] == "user3updated")
    assert(d["data"]["assignedUser"] == userID)

    # Create a task with an unknown user
    params = urllib.parse.urlencode({'name': "task4", 'deadline': taskDeadline[i], 'assignedUser': "41224d776a326fb40f000001"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 201)
    assert(d["data"]["assignedUser"] == "")
    assert(d["data"]["assignedUserName"] == "unassigned")
    params = urllib.parse.urlencode({'name': "task4", 'deadline': taskDeadline[i], 'assignedUser': userID, 'assignedUserName': "user3updated"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 201)
    params = urllib.parse.urlencode({'name': "task4", 'deadline': taskDeadline[i], 'assignedUser': "41224d776a326fb40f000001"})
    conn.request("PUT", "/api/tasks/" + taskID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d["data"]["assignedUser"] == "")
    assert(d["data"]["assignedUserName"] == "unassigned")

    # Create a user with an uknown task
    params = urllib.parse.urlencode({'name': "user4", 'email': "user4@gmail", "pendingTasks": "41224d776a326fb40f000001"})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 201)
    assert(len(d["data"]["pendingTasks"]) == 0)

    # Remove task if completed
    params = urllib.parse.urlencode({'name': "task5", 'deadline': taskDeadline[i], 'assignedUser': userID, 'assignedUserName': "user3updated"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    taskID = d["data"]["_id"]
    assert(response.status == 201)
    conn.request("GET", "/api/users?where={"'"name"'":"'"user3updated"'"}")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(response.status, d)
    assert(response.status == 200)
    assert(len(d["data"]) == 1)
    pendingTaskLen = len(d["data"][0]["pendingTasks"])
    params = urllib.parse.urlencode({'name': "task5", 'deadline': taskDeadline[i], 'assignedUser': userID, 'assignedUserName': "user3updated", 'completed': "true"})
    conn.request("PUT", "/api/tasks/" + taskID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    conn.request("GET", "/api/users?where={"'"name"'":"'"user3updated"'"}")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(len(d["data"][0]["pendingTasks"]) == pendingTaskLen - 1)

    # Create user with completed tasks
    params = urllib.parse.urlencode({'name': "task6", 'deadline': taskDeadline[i], 'assignedUser': "", 'assignedUserName': "", 'completed': "true"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    taskID = d["data"]["_id"]
    assert(response.status == 201)
    params = urllib.parse.urlencode({'name': "user5", 'email': "user5@gmail", "pendingTasks": taskID})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(response.status == 201)
    assert(len(d["data"]["pendingTasks"]) == 0)

    # More tests (create task with unknown user)
    params = urllib.parse.urlencode({'name': "task7", 'deadline': taskDeadline[i], 'assignedUser': "41224d776a326fb40d000001" , 'assignedUserName': "user7"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(response.status, d)
    assert(response.status == 201)
    assert(d["message"] == "Task created but with no assigned user")
    assert(d["data"]["assignedUser"] == "")
    assert(d["data"]["assignedUserName"] == "unassigned")
    conn.request("GET", "/api/tasks?where={"'"name"'":"'"task6"'"}")
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    taskID = d["data"][0]["_id"]
    taskAssignedUser = d["data"][0]["assignedUser"]
    params = urllib.parse.urlencode({'name': "task8", 'deadline': taskDeadline[i], 'assignedUser': "41224d776a326fb40d000001" , 'assignedUserName': "user7"})
    conn.request("PUT", "/api/tasks/" + taskID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 200)
    assert(d["message"] == "Task updated but with no assigned user")

    # More tests (create task with missing fields)
    params = urllib.parse.urlencode({'name': "", 'deadline': taskDeadline[i]})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 400)
    assert(d["message"] == "Missing fields, need name and deadline to post a task")
    params = urllib.parse.urlencode({'name': "task8", 'deadline': "", 'assignedUser': "41224d776a326fb40a000001" , 'assignedUserName': "user7"})
    conn.request("PUT", "/api/tasks/" + taskID, params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 400)
    assert(d["message"] == "Missing fields, need name and deadline to put a task")

    # Exit gracefully
    conn.close()
    print("It worked :)")


if __name__ == "__main__":
     main(sys.argv[1:])