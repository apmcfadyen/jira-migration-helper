from jira import JIRA
import json

f = open('info.json')
info = json.load(f)
f.close()

user = info['user']
password = info['password']
link = info['link']

# Declare and init jira
jira = JIRA(link, basic_auth=(user, password))

# Set project here:
proj = "PP"

# Shuts up the console if false
verbose = True

# Run this in the console to check the field names and get keys. Make a note below.
# print(jira.fields())

# migrated text = "customfield_10422"
new = "customfield_10414"

# Pulling in everything from the project
issues = jira.search_issues('project = ' + proj)
i = 0
k = 0
size = issues.total
keep_going = True
if verbose: print("Found " + str(issues.total) + " issues")

while keep_going:
    issues = jira.search_issues('project = ' + proj + ' and \'cf[10414]\' is empty and \'cf[10422]\' is not empty')
    size = issues.total
    start = i * size
    issues = jira.search_issues('project = ' + proj + ' and \'cf[10414]\' is empty and \'cf[10422]\' is not empty', start, size)

    if k >= size:
        keep_going = False

    for issue in issues:
        if k >= size:
            keep_going = False
        print(k)
        print(issue.key)
        if issue.fields.customfield_10422 != issue.fields.customfield_10414 or issue.fields.customfield_10422 != "None":
            if verbose: print("Checklist Text: " + str(issue.fields.customfield_10414))
            issue.update(fields={new: issue.fields.customfield_10422})
        if verbose: print("Checklist text is now: " + str(issue.fields.customfield_10414))
        k = k + 1

keep_going = True
if verbose: print(str(k) + " checklists migrated.")

# The next part replaces the subdomain for places where the link doesn't update
# Best to do the whole url to avoid any unnecessary replaces

old_domain = info['old domain']
new_domain = info['new domain']

i = 0
k = 0
j = 0

issues = jira.search_issues('project = ' + proj)
while keep_going:
    start = i * size
    issues = jira.search_issues('project = ' + proj, start, size)
    for issue in issues:
        # Only operate on strings where the description contains the old domain
        if old_domain in str(issue.fields.description):
            if verbose: print("Old issue description: " + issue.fields.description)
            description_string = str(issue.fields.description)
            updated_description = description_string.replace(old_domain, new_domain)
            issue.update(fields={'description': updated_description})
            if verbose: print("New issue description: " + issue.fields.description)
            k = k+1
            j = j+1
        else:
            k = k+1
        if k>=size:
            keep_going = False
if verbose: print("Updated " + str(j) + " descriptions")

keep_going = True
i = 0
k = 0
j = 0

issues = jira.search_issues('project = ' + proj)
while keep_going:
    start = i * size
    issues = jira.search_issues('project = ' + proj, start, size)
    for issue in issues:
        comments = issue.fields.comment.comments
        for comment in comments:
            # Only operate on strings where the comment body contains the old domain
            if old_domain in str(comment.body):
                comment_string = comment.body
                if verbose: print(comment_string)
                updated_comment = comment_string.replace(old_domain, new_domain)
                if verbose: print(updated_comment)
                comment.update(body=updated_comment)
                i = i+1
    k=k+1
    if(k>=size):
        keep_going = False
if verbose: print("Updated " + str(i) + " comments")

keep_going = True
i = 0
k = 0
j = 0
bad_text = " (migrated)"

issues = jira.search_issues('project = ' + proj)
while keep_going:
    start = i * size
    issues = jira.search_issues('project = ' + proj, start, size)
    for issue in issues:
        prio = str(issue.fields.priority.name)
        if bad_text in prio:
            new_prio = prio.replace(bad_text,'')
            issue.update(priority={"name": new_prio})
            k += 1
            j += 1
        else:
            k += 1
    if(k>=size):
        keep_going = False
print("Updated " + str(j) + " priorities")

print("Done")