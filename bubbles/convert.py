import collections
from collections import Counter
import pandas as pd
import json
import csv
import ast

# The CSV file as source (actually just the four columns from the original
# source file)
# Had to clean up this data a bit, mostly the book titles were shortened.
csvfile = 'annotator-subject-tag-book.csv'

# Create an empty JSON object with the first element as an empty
jsonobj = {}
jsonobj['nodes'] = []
jsonobj['links'] = []
nodes = []


# Function to get a list of items from a column
def getlist(column):
    # Some rows have multiple subjects, separated by semi-colons. This splits those
    # out into lists. So we have lists of lists.
    ulist = column.str.split(";", expand=True)
    # This flattens all those lists of lists into just one big list.
    ulist = ulist.values.flatten()
    # Strip out the white spaces
    ulist = striplist(ulist)
    # This gets just the unique subjects and makes them a list
    ulist = list(set(ulist))
    return ulist

# Function to strip white space from each cell.
# Could not get more elegent solutions to work. Tried:
# lambda: [x.trim() for x in tags]
def striplist(l):
    z = []
    for x in l:
        if x:
            x = x.strip()
            z.append(x)
    return z

# Function to create a list of all the unique items (annotator, subject, tag or
# book title) 
def addnode(ulist):
    for n in ulist:
        nodes.append(n)

# Function to put the list of unique column items (annotator, subject, tag or
# book title) into JSON format
# This creates the first part of the JSON object in the format:
# "nodes": [
#   { "name": "Annotator" },
#   { "name": "Subject" },
#   { "name": "Tag" },
#   { "name": "Book" }
#   ]
def nodify(thelist, what):
    for n in thelist:
        jsonobj['nodes'].append(dict(what=n))

####
#  Create the nodes section
###

# Use pandas to read in each column.
rows = pd.read_csv(csvfile)

# get unique list of annotators, subjects, tags, and books
annots = getlist(rows.annotator)
subjs = getlist(rows.subjects)
tags = getlist(rows.tags)
books = getlist(rows.books)

# Make a list of all the things
addnode(annots)
addnode(subjs)
addnode(tags)
addnode(books)

# Make the list of all the things into the JSON Object
nodify(nodes, "name")


####
#  Create the links section
####

# Rebuild the CSV by iterating through each row, if there is a row that has
# multiple subjects or tags, then create as many duplicate rows as there are
# subjects or tags in that row
# Pandas can probably do this much better, but alas, I don't know that well.
with open(csvfile, 'r') as f:
    reader = csv.reader(f)
    allrows = list(reader)

# Do the tags first
newrows = list()
for r in allrows:
    if (';' in r[2]):
        tags = r[2].split(";")
        for t in tags:
            newrow = list()
            newrow.append(r[0])
            newrow.append(r[1])
            newrow.append(t.strip())
            newrow.append(r[3])
            newrows.append(newrow)
    else:
        newrows.append(r)

# now do it to subjects
finalrows = list()
for r in newrows:
    if (';' in r[1]):
        subjects = r[1].split(";")
        for s in subjects:
            newrow = list()
            newrow.append(r[0])
            newrow.append(s.strip())
            newrow.append(r[2])
            newrow.append(r[3])
            finalrows.append(newrow)
    else:
        finalrows.append(r)

# now write all of the separated rows to a csv file for later use
with open('separatedrows.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    for r in finalrows:
        wr.writerow(r)



# Counts how many times each row is duplicated, and that number is the value in
# the links array
with open('separatedrows.csv') as f:
    c = Counter(f)
    dups = [t for t in c.most_common() if t[1] > 0]
    dups_dict = {row: count for row, count in c.most_common() if count > 0}



# for each row in csv, find array id for each author, subject, tag, and book
# listed, then make a links object for author -> subject, subject -> tag, tag ->
# book.
# Create second part of JSON object in the format:
# "links": [
#       {
#           "source": S,
#           "target": T,
#           "value": V
#       }
#   ]
# Where V is the number of how many times the row was duplicated

# This count doesn't need to be in there..
del dups_dict['"annotator","subjects","tags","books"\n']
#newdups = [i for i in dups if i[0] != '"annotator","subjects","tags","books"\n']

# For use in the Google Chart version
gcode = []
for key, value in dups_dict.items():
    # key is a string that looks like a list, but isn't, so can't split on ,
    # because there are commas within the list 'element'. So use literal_eval
    # to turn it into a real list
    things = ast.literal_eval(key)

    source1 = nodes.index(things[0].strip('"'))
    target1 = nodes.index(things[1].strip('"'))
    jsonobj['links'].append(dict(source=source1,target=target1,value=value))
    gcode.append([things[0], things[1], value])

    source2 = nodes.index(things[1])
    target2 = nodes.index(things[2])
    jsonobj['links'].append(dict(source=source2,target=target2,value=value))
    gcode.append([things[1], things[2], value])

    source3 = nodes.index(things[2])
    target3 = nodes.index(things[3])
    jsonobj['links'].append(dict(source=source3,target=target3,value=value))
    gcode.append([things[2], things[3], value])


# Write the JSON object to a file
with open('astb.json', 'w') as outfile:
    json.dump(jsonobj, outfile)


# print out the gcode to copy/paste into the gchart.html.
# Need to figure out how to get GChart to use a file, then write the gcode list
# to a CSV or JSON file instead.
#print(gcode)
