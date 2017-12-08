import collections
from collections import Counter
import pandas as pd
import numpy as np
import json
import csv
import ast
import textwrap

# The CSV file as source (actually just the four columns from the original
# source file)
# Had to clean up this data a bit, mostly the book titles were shortened.
csvfile = 'annotator-subject-tag-book.csv'

# Create an empty JSON object with the first element as an empty
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


####
#  Create CSV with all subjects and tags separated out
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

####
# Format data as JSON
####
#{
# "name": "books",
# "children": [
#  {

#   "name": "Book Title",
#   "children": [
#    {
#     "name": "Subject",
#     "children": [
#      {"name": "Subject 1", "size": 8},
#      {"name": "Subject 2", "size": 2},
#      {"name": "Subject 3", "size": 4}
#     ]
#    },
#    {
#     "name": "Tags",
#     "children": [
#      {"name": "Tags 1", "size": 8},
#      {"name": "Tags 2", "size": 2},
#      {"name": "Tags 3", "size": 4}
#     ]
#    },
#    {
#     "name": "Annotators",
#     "children": [
#      {"name": "Annotators 1", "size": 8},
#      {"name": "Annotators 2", "size": 2},
#      {"name": "Annotators 3", "size": 4}
#     ]
#    }
#   ]

#  }
# ]
#}
# 
# So, iterate over all the books (from the books list created above)
# For each book, get
#  a list of subjects assigned to that book
#   and the number of subjects assigned to that book
#  Then do the same for tags and annotators
#  and put that info in the format above.
with open('separatedrows.csv', 'r') as f:
    reader = csv.reader(f)
    allseprows = list(reader)

def getcolumn(columnName, columngroup):
    column = {}
    column['name'] = columnName
    column['children'] = []
    for name, group in columngroup.iterrows():
        size = np.asscalar(np.int16(group[0]))
        column['children'].append(dict(name=name,size=size))
    return column

allnotes = pd.read_csv('separatedrows.csv')
allbooksobj = {}
allbooksobj['name'] = 'Books'
allbooksobj['children'] = []

for book in books:
    # Gets all the rows per book
    match = allnotes[allnotes.books == book]
    bookobj = {}
    bookobj['name'] = book
    bookobj['children'] = []

    # Get subjects and number of subjects
    subjectgroup = match.groupby('subjects').count()
    subjectdict = getcolumn('Subject', subjectgroup)

    tagsgroup = match.groupby('tags').count()
    tagsdict = getcolumn('Tags', tagsgroup)

    annotatorsgroup = match.groupby('annotator').count()
    annotatorsdict = getcolumn('Annotator', annotatorsgroup)

    bookobj['children'].append(subjectdict)
    bookobj['children'].append(tagsdict)
    bookobj['children'].append(annotatorsdict)

    allbooksobj['children'].append(bookobj)


print(allbooksobj)
with open('d3tree.json', 'w') as bfile:
    json.dump(allbooksobj, bfile)

bookorder = allnotes.groupby('books').count()
allgroups = allnotes.groupby([ 'annotator', 'subjects', 'tags', 'books' ])
#subjects = allnotes.groupby('books').get_group('subjects')


bookvalues = bookorder.values.tolist()
booklist = {}
booklist['items'] = []
popular = []
for index, row in bookorder.iterrows():
    # Convert the numpy int to one that JSON will like. Without this, can't
    # write to json file below
    # see https://stackoverflow.com/questions/9452775/converting-numpy-dtypes-to-native-python-types/11389998#11389998
    num = np.asscalar(np.int16(row[0]))
    booklist['items'].append(dict(text=index, count=num))
    strnum = str(num)
    title = textwrap.shorten(index, width=30, placeholder='')
    # Should use sub instead so I can use a regex, but this is faster for given
    # time...
    title = title.replace('[', '')
    title = title.replace(']', '')
    title = title.replace('.', '')
    popular.append(list([ title,strnum ]))
