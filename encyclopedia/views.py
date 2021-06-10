from django.shortcuts import render
from . import util
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django import forms


#Las dos lineas de abajo son importantes para convertir de markdown a HTML como módulo

import markdown2  
from markdown2 import Markdown
import secrets

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    markdowner = Markdown() # objeto markdowner de la clase Markdown
    entryPage = util.get_entry(entry)
    if entryPage is None:
        notFound = True
        search = False
        return render(request, "encyclopedia/index.html",{
                    "search": search,
                    "notFound": notFound,
                    "value": entry
                })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(entryPage), # aquí utilizo al objeto
            "entryTitle": entry
        })

class NewEntryForm(forms.Form):
        newEntryTitle = forms.CharField(widget=forms.TextInput(attrs={"class" : 'form-control col-md-8 col-lg-8'}),label="Title")
        newEntryData = forms.CharField(widget=forms.Textarea(attrs={"class" : 'form-control col-md-8 col-lg-8', 'rows': '6'}),label="Content") 
        edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def newEntry(request):
    if request.method == 'POST':
        form = NewEntryForm(request.POST)
        if form.is_valid():
            
            title = form.cleaned_data["newEntryTitle"]
            content = form.cleaned_data["newEntryData"]
            edit = form.cleaned_data["edit"]

            if util.get_entry(title) is not None and edit is False:
               alreadyExist = True
               return render(request, "encyclopedia/newEntry.html",{
                   "alreadyExist":alreadyExist,
                   "form":form,
                   "title":title,
                })     
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry':title}))
        
        else:
            return render(request, "encyclopedia/newEntry.html",{
                "form":form,
            })
    else:
        return render(request, "encyclopedia/newEntry.html", {
            "form":NewEntryForm(),
        })

def random(request):
    entriesList = util.list_entries()
    randomEntry = secrets.choice(entriesList)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': randomEntry}))


def edit(request, entry):
    entryToEdit = util.get_entry(entry)
    if entryToEdit is None:
        return HttpResponse("Error")
    else:
        form = NewEntryForm()
        form.fields["newEntryTitle"].initial = entry     
        form.fields["newEntryTitle"].widget = forms.HiddenInput()
        aux = "#" + entry #Esto crea una variable #titulo
        form.fields["newEntryData"].initial = entryToEdit.lstrip(aux) #lstrip me quita la adición de titulo que hace save_entry y tenemos en el archivo .md
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newEntry.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "title": form.fields["newEntryTitle"].initial
        })     

def search(request):
    value = request.GET.get('q','')
    if util.get_entry(value) is None:
      
        validEntries = []
        allEntries = util.list_entries()
        search = True
        notFound = False # habia un error con esta variable no declarada
        for validEntry in allEntries:
            if value.lower() in validEntry.lower():
                validEntries.append(validEntry)
        if len(validEntries) == 0:
            search = False
            notFound = True
        return render(request, "encyclopedia/index.html",{
                    "value":value,
                    "entries":validEntries,
                    "search": search,
                    "notFound": notFound,
                })

    else:
        return HttpResponseRedirect(reverse("entry", kwargs={'entry':value}))