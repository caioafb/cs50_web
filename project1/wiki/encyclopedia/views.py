from django.shortcuts import render, redirect

from . import util
from markdown2 import Markdown
import random

def index(request):
    entries = util.list_entries()

    if request.method == "POST":
        md_to_html = Markdown()
        search = request.POST["q"]

        if util.get_entry(search.capitalize()):
            entry = util.get_entry(search.capitalize())
        elif util.get_entry(search.upper()):
            entry = util.get_entry(search.upper())
        else:
            entry = util.get_entry(search)

        if entry:
            return render(request, "encyclopedia/entry.html", {
                "title": search,
                "entry": md_to_html.convert(entry)
            })
        else:
            substring_entries = []
            for entry in entries:
                if search.lower() in entry.lower():
                    substring_entries.append(entry)
            
            return render(request, "encyclopedia/search.html", {
                "search": search,
                "entries": substring_entries
            })

    return render(request, "encyclopedia/index.html", {
        "entries": entries
    })

def entry(request, title):
    md_to_html = Markdown()
    if util.get_entry(title.capitalize()):
        entry = util.get_entry(title.capitalize())
    elif util.get_entry(title.upper()):
        entry = util.get_entry(title.upper())
    else:
        entry = util.get_entry(title)

    if entry:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": md_to_html.convert(entry)
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title
        })
    
def new_page(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        
        if util.get_entry(title.capitalize()):
            entry = util.get_entry(title.capitalize())
        elif util.get_entry(title.upper()):
            entry = util.get_entry(title.upper())
        else:
            entry = util.get_entry(title)

        if not entry:
            util.save_entry(title, content)
            return redirect('index')
        else:
            return render(request, "encyclopedia/new_page.html", {"error":True})
        
    return render(request, "encyclopedia/new_page.html")

def edit_page(request):
    if request.method == "POST":
        if request.POST["option"] == "edit":
            title = request.POST["entry"]
            entry = util.get_entry(title)
            return render(request, "encyclopedia/edit_page.html", {
                "title": title,
                "entry": entry
            })
        elif request.POST["option"] == "save":
            md_to_html = Markdown()
            title = request.POST["title"]
            content = request.POST["content"]
            util.save_entry(title, content)
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "entry": md_to_html.convert(content)
            })
        
def random_page(request)    :
    title = random.choice(util.list_entries())
    return redirect('entry', title)
