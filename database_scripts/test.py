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
    taskCompleted = [True, False, False, False, False]
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
    assert(d["message"] == "Error, you need to provide a name and deadline")
    params = urllib.parse.urlencode({'name': "", 'deadline': ""})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and deadline")
    params = urllib.parse.urlencode({'name': "asdf", 'deadline': ""})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and deadline")

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
    assert(d["message"] == "Error, you need to provide a name and deadline")
    params = urllib.parse.urlencode({'name': "", 'deadline': ""})
    conn.request("PUT", "/api/tasks/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and deadline")
    params = urllib.parse.urlencode({'name': "asdf", 'deadline': ""})
    conn.request("PUT", "/api/tasks/1", params, headers)
    response = conn.getresponse()
    assert(response.status == 400)
    data = response.read()
    d = json.loads(data)
    assert(d["message"] == "Error, you need to provide a name and deadline")

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
    # bad = str("41224d776a326fb40f000001")
    # conn.request("DELETE", "/api/tasks/" + bad)
    # response = conn.getresponse()
    # data = response.read()
    # d = json.loads(data)
    # print(response.status)
    # print(d)
    # assert(response.status == 404)

    # Delete a user and check accompying tasks
    conn.request("DELETE", "/api/users/" + userIDs[0])
    response = conn.getresponse()
    data = response.read()
    assert(response.status == 200)
    conn.request("GET", "/api/tasks/" + taskIDs[0])
    response = conn.getresponse()
    assert(response.status == 200)
    data = response.read()
    d = json.loads(data)
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
    assert(response.status == 200)
    conn.request("GET", "/api/tasks/" + taskID)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    print(d)
    assert(d["data"]["assignedUserName"] == "user3updated")

    # Create a task with an unknown user
    params = urllib.parse.urlencode({'name': "task4", 'deadline': taskDeadline[i], 'assignedUser': "41224d776a326fb40f000001"})
    conn.request("POST", "/api/tasks", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 400)
    params = urllib.parse.urlencode({'name': "task4", 'deadline': taskDeadline[i], 'assignedUser': userID, 'assignedUserName': "user3"})
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
    assert(response.status == 400)

    # Create a user with an uknown task
    params = urllib.parse.urlencode({'name': "user4", 'email': "user4@gmail", "pendingTasks": "41224d776a326fb40f000001"})
    conn.request("POST", "/api/users", params, headers)
    response = conn.getresponse()
    data = response.read()
    d = json.loads(data)
    assert(response.status == 201)
    assert(len(d["data"]["pendingTasks"]) == 0)

    # Remove task if completed

    # Create user with completed tasks

    # Exit gracefully
    conn.close()
    print("It worked :)")


if __name__ == "__main__":
     main(sys.argv[1:])