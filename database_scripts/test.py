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

        # Store the users id
        userIDs.append(str(d['data']['_id']))
        userNames.append(str(d['data']['name']))

    taskName = ["1","2","3","4","5"]
    taskDescription = ["1","2","3","4","5"]
    taskDeadline = [(mktime(date.today().timetuple())) * 1000 for i in range(taskCount)]
    taskCompleted = [True, False, False, False, False]

    # Loop 'taskCount' number of times
    for i in range(taskCount):
        params = urllib.parse.urlencode({'name': taskName[i], 'deadline': taskDeadline[i], 'assignedUserName': userNames[i], 'assignedUser': userIDs[i], 'completed': str(taskCompleted[i]).lower(), 'description': taskDescription[i]})

        # POST the task
        conn.request("POST", "/api/tasks", params, headers)
        response = conn.getresponse()
        assert(response.status == 201)
        data = response.read()
        d = json.loads(data)

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
        assignedUserTasks = [str(x).replace('[','').replace(']','').replace("'",'').replace('"','') for x in assignedUserTasks]
        assignedUserTasks.append(taskID)

        # PUT in the user
        params = urllib.parse.urlencode({'_id': userIDs[i], 'name': assignedUserName, 'email': assignedUserEmail, 'dateCreated': assignedUserDate, 'pendingTasks': assignedUserTasks}, True)
        conn.request("PUT", "/api/users/"+userIDs[i], params, headers)
        response = conn.getresponse()
        assert(response.status == 200)
        assert(response.reason == "OK")
        data = response.read()
        d = json.loads(data)

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


    # Exit gracefully
    conn.close()
    print(str(userCount)+" users and "+str(taskCount)+" tasks added at "+baseurl+":"+str(port))


if __name__ == "__main__":
     main(sys.argv[1:])
