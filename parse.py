#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import json
import csv
from pprint import pprint
import subprocess
import shlex
import csv  
import requests
import time

resultsPath = sys.argv[1]

def main():
    """
    Main function
    """
    checkUsage()
    csvData = []

    countAlert = 0
    countTimeout = 0
    countLimit = 0
    countQuerytime = 0
    countResults = 0
    countProjects = 0

    for root, dirs, files in os.walk(resultsPath):
        for directory in dirs:
            # if len(os.listdir(os.path.join(resultsPath, directory))) > 1:
            #     continue
            sourceGraphFilePath = os.path.join(resultsPath, directory, "sourcegraphsearch.json")
            if not os.path.isfile(sourceGraphFilePath):
                continue
            with open(sourceGraphFilePath) as report:
                data = json.load(report)
                countProjects += 1

            # print("ElapsedMilliseconds", data["ElapsedMilliseconds"])
            # print("LimitHit", data["LimitHit"])
            countQuerytime += data["ElapsedMilliseconds"]
            if data["ElapsedMilliseconds"] >= 59000:
                countTimeout += 1
            if data["LimitHit"] == True:
                countLimit += 1
            if data["Alert"]["Title"] != "":
                # print("Alert", data["Alert"]["Title"])
                countAlert += 1

            if data["Results"] != []:
                countResults += len(data["Results"])
                for result in data["Results"]:
                    messagePreview = result["messagePreview"]
                    if messagePreview != None:
                        messageValue = messagePreview["value"]
                        if "flaky" in messageValue.lower():
                            projectName = data["Query"].split("repo:")[-1][:-1]
                            commit = result["commit"]["oid"]
                            url = "https://github.com/" + projectName + "/commit/" + commit
                            comment = getInterestingLinesFromMessage("flaky", messageValue)
                            
                            if not os.path.isfile(os.path.join(resultsPath, directory, commit) + ".json"):
                                queryGitHub(projectName, commit, directory)

                            # if "fix" in comment.lower():
                            #     row = [projectName, url, commit, comment]
                            #     csvData.append(row)
        
    # csvData = sorted(csvData, key=lambda x:x[0])
    # writeToCsv(csvData)
    print("Number of projects", countProjects)
    print("Number of commits containing flaky", countResults)
    print("countAlert", countAlert)
    print("countTimeout", countTimeout)
    print("countLimit", countLimit)
    print("countQuerytime", countQuerytime)

def getInterestingLinesFromMessage(keyword, message):
    # Split by lines
    message = message.replace("\r", "\n")
    message = message.split("\n")

    comment = ""
    for line in message:
        if keyword in line.lower():
            comment += line + ","
    comment = comment.rstrip(',')
    return comment

def queryGitHub(projectName, commit, directory):
    # Get API credentials
    gh_user, gh_token = getCredentials()
    # Query GitHub
    print(projectName, commit)
    r = requests.get('https://api.github.com/repos/' + projectName + '/commits/' + commit, auth=(gh_user, gh_token))
    print("status:", r.status_code)
    remainingQueries = int(r.headers["X-RateLimit-Remaining"])
    rateReset = int(r.headers["X-RateLimit-Reset"])
    now = int(time.time())
    wait = rateReset - now
    print("remainingQueries:", remainingQueries)
    print("Need to wait:", wait)
    if remainingQueries <= 1:
        time.sleep(wait)
    jsonR = r.json()
    # Save to directory
    saveToFile(jsonR, commit, directory)

def saveToFile(result, commit, folder):
    with open(os.path.join(resultsPath, folder, commit) + '.json', 'w') as outfile:
        json.dump(result, outfile, sort_keys=True, indent=4)
    return

def writeToCsv(data):
    with open('file.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return

def getCredentials():
    if not os.path.exists("./credentials.json"):
        print("No credential found for API authentification.")
        return
    with open('./credentials.json') as data_file:
        data = json.load(data_file)
    gh_user = data['gh_user']
    gh_token =  data['gh_token']
    return gh_user, gh_token

def checkUsage():
    """
    Check Usage
    """
    #Check the programs' arguments
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print("Usage:")
        print("python parse.py /path/to/results")
        sys.exit(1)

if __name__ == "__main__":
    main()