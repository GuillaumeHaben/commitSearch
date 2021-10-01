#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import json
import csv
from pprint import pprint
import subprocess
import shlex

# Get args
csvPath = sys.argv[1]
resultsPath = sys.argv[2]

def main():
    """
    Main function
    """
    checkUsage()
    
    projects = csvReader(csvPath)
    main = []

    limit = 10000

    # Sort top projects by different features
    projectsByCommits = sortBy(projects, "Commits", limit)
    projectsByContributors = sortBy(projects, "Contributors", limit)
    projectsByReleases = sortBy(projects, "Releases", limit)
    projectsByStars = sortBy(projects, "Stars", limit)
    projectsBySize = sortBy(projects, "Size", limit)
    projectsByIssues = sortBy(projects, "Issues", limit)

    # Get all together
    allList = projectsByCommits + projectsByContributors + projectsByReleases + projectsByStars + projectsBySize + projectsByIssues

    for project in allList:
        main.append(project["Name"])

    # Remove duplicates
    unique = set(main)


    for project in unique:
        searchSourceGraph(project)

    # print("Total number of projects:", len(main))
    # print("Unique projects:", len(unique))

    # for root, dirs, files in os.walk("./results/commits"):
    #     resultsAnalysis(files)
        
# def resultsAnalysis(files):
#     for name in files:
#         with open("./results/commits/" + name) as report:
#             data = json.load(report)
#             print(name, data["ResultCount"])
#     return

def searchSourceGraph(projectName):
    """
    Take a project name
    Print query 
    """
    # Avoid slashes in repo name
    repoName = projectName.replace("/","_")
    dirPath = os.path.join(resultsPath, repoName)
    # If folder doesn't exist we create it
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)
    # If file doesn't exist or folder is empty, we make the query
    if not os.path.isfile(os.path.join(dirPath, "sourcegraphsearch.json")) or not os.listdir(dirPath):
        queryCommit = "src search -json 'flaky count:all timeout:59s type:commit repo:" + projectName + "$' | tee " + dirPath + "/sourcegraphsearch.json"
        # Add sleep for API "too many requests"
        sleepCommand = "sleep 3"
        print(queryCommit)
        print(sleepCommand)
    return

def csvReader(csvPath):
    """
    Read csv file from input arg
    Return list of projects
    """
    projects = []
    with open(csvPath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        lineCount = 0
        for row in csvReader:
            if lineCount == 0:
                lineCount += 1
            else:
                lineCount += 1
                project = assembleProject(row)
                projects.append(project)
    return projects

def assembleProject(row):
    """
    Take a row form csv file
    Return project object
    """
    name = row[0]
    commits = int(row[2]) if row[2] else 0
    contributors = int(row[6]) if row[6] else 0
    releases = int(row[5]) if row[5] else 0
    stars = int(row[9]) if row[9] else 0
    size = int(row[11]) if row[11] else 0
    issues = int(row[17]) if row[17] else 0
    project = {
        "Name": name,
        "Commits": commits,
        "Contributors": contributors,
        "Releases": releases,
        "Stars": stars,
        "Size": size,
        "Issues": issues,
    }
    return project

def sortBy(projectList, feature, n):
    """
    Take projectList, sorting feature, first n to return
    Return projectList sorted accordingly
    """
    return sorted(projectList, key=lambda x: x[feature], reverse=True)[:n]

def checkUsage():
    """
    Check Usage
    """
    #Check the programs' arguments
    if len(sys.argv) != 3 or not os.path.isfile(sys.argv[1]) or not os.path.isdir(sys.argv[2]):
        print("Usage:")
        print("python search.py /path/to/pythonProjects.csv /path/to/resultsFolder")
        sys.exit(1)

if __name__ == "__main__":
    main()