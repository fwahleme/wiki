
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from markdown2 import markdown
from . import util
from random import randint

subFolder = "wiki/"

class EnterSearchForm(forms.Form):
    searchString = forms.CharField(label="Search String")

class EnterTitleForm(forms.Form):
    titleString = forms.CharField(label="Title", initial='')

def randomPage(request):
    """ Load a random page
    """
    allEntries = util.list_entries()
    index = randint(0, len(allEntries)-1)
    return loadTitlePage(request, allEntries[index])

def editEntry(request, titleParm):
    """ Load the page for creating or editing an entry.
        Process the Post to save the page
        titleParm will be '__new__' or the title.  So we know if we can overwrite and existing file.
    """
    # GET loads the edit page
    if request.method == "GET":
        # create a new entry
        if titleParm == '___new___':
            return render(request, "encyclopedia/edit_entry.html", {"titleForm":EnterTitleForm, "titleParm":titleParm, "body":''} )
        # edit existing entry
        else:
            # ??for some reason saving to file adds extra carriage returns; take the out
            entry = stripCR(util.get_entry(titleParm))
            # printc("Loading edit page", entry)
            if entry is not None:
                myForm = EnterTitleForm({"titleString":titleParm})
                return render(request, "encyclopedia/edit_entry.html", {"titleForm":myForm, "titleParm":titleParm, "body":entry} )
            else:
                return HttpResponse(f"Could not find entry {titleParm}")

    # POST
    elif request.method == "POST":
        form = EnterTitleForm(request.POST)
        if form.is_valid():
            overWrite = (titleParm != '___new___')
            return saveEntry(request, form.cleaned_data["titleString"], request.POST['bodyText'], overWrite)
        else:
            return HttpResponse("Invalid form entry")

    # Else unexpected method
    else:
        return HttpResponse("unexpected method")

def saveEntry(request, title, body, overWrite):
    # printc(f"calling util.save_entry()", body)
    # if title already exists, send message
    if (not overWrite) and (util.get_entry(title) is not None):
        return render(request, "encyclopedia/encyclopedia_error.html", {"message": "\"" + title + "\" is already an encyclopedia entry."} )

    # save data and open the entry page by calling loadTitlePage()
    else:
        util.save_entry(title, body)
        return loadTitlePage(request, title)

def index(request):
    """ Load the main page or process a search request
    """
    # GET loads the main page
    if request.method == "GET":
        return render(request, "encyclopedia/index.html", 
                    {"entries": util.list_entries(), "subpathParm": subFolder, "searchForm":EnterSearchForm} 
                )
            
    # POST comes from the search form
    elif request.method == "POST":
        form = EnterSearchForm(request.POST)
        if form.is_valid():
            # findSearchEntry() will open the entry page, or a filtered list
            return findSearchEntry(request, form.cleaned_data["searchString"])
        else:
            return HttpResponse("Invalid form entry")

    # Else unexpected method
    else:
        return HttpResponse("unexpected method")

def loadTitlePage(request, titleParm):
    """ Given the name of an entry, load it's page if it exists.
        Else show an error page.
    """
    mdEntryContent = util.get_entry(titleParm)
    # printc(f"read file with util.get_entry()", mdEntryContent)
    if mdEntryContent is None:
        return render(request, "encyclopedia/encyclopedia_error.html", {"message": titleParm + " is not a valid encyclopedia entry."} )
    else:
        return render(request, "encyclopedia/encyclopedia_show_entry.html", 
            {"contentParm": markdown(mdEntryContent), "titleParm": titleParm.upper()} 
        )

def findSearchEntry(request, entry):
    """ Check user's search string.
        If entry is found open it's page.
        Else show a filtered list based on the user's input.
    """
    # if found entry, open it's page by calling loadTitlePage()
    if util.get_entry(entry) is not None:
        return loadTitlePage(request, entry)

    # else entry not found, show filtered list based on entry
    else: 
        allEntries = util.list_entries()
        filteredList = []
        for e in allEntries:
            if entry.lower() in e.lower():
                filteredList.append(e)
        return render(request, "encyclopedia/search.html", 
            {"searchStr":entry, "subpathParm": subFolder, "filteredEntries":filteredList} 
        )  

def printc(header, str):
    print(f"{header}")
    for c in range(0,len(str)):
        print({str[c]})

def stripCR(str):
    newStr = ""
    for i in range(0, len(str)):
        if str[i] != '\r':
            newStr += str[i]
    return newStr