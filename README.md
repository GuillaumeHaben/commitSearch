# Get Commit information about flaky tests

## Dependencies

Python 3.9.0

## Setup

For `parse.py`, create a `credentials.json` file with the following:
```
{
    "gh_user": "Github Username",
    "gh_token": "API_token"
}
```

## Scripts

1. `search.py`  
`search.py [csvFile] [resultsFolder] > saveFile.txt`  
- csvFile: Downloaded from https://seart-ghs.si.usi.ch/
- resultsFolder: Path to folder where everything will be saved
- saveFile: Pipe output to file

This script first take the dump `csvFile` of GitHubSearch containing most popular python projets.  
Then it sorts them by interesting features and creates a top list of project to consider.  
Then it calls SourceGraph searching for "flaky" in those projects' commit messages.  
Then, it saves queries needed to get results in "saveFile.txt"

2. `sh saveFile.txt`  

Execute all queries 1 by 1.  
Save response as `sourcegraphsearch.json` in the corresponding folder

3. `parse.py`  
`parse.py [resultsFolder]`  

Script that goes through all folders in `resultsFolder`  
A folder is a project containing a `sourcegraphsearch.json`  
In this file, there is a list of "Results", match for "flaky" in any commit messages  
This script will query the GitHub API for all commits containing "flaky" and save JSON response in the project folder

4. `commitAnalysis.py`  
`commitAnalysis.py [resultsFolder]`

This script takes the path of the `resultsFolder`  
It analyses all commits containing "flaky" keyword  
Playing aroung fix kerwords, attempts to find fixes in test and/or code