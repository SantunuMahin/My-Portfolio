from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import ConnectForm
from .models import (
    AboutMe, CP_Log, Projects, Experience,
    Certifications, Hobbies, ConnectMe
)

def index(request):
    if request.method == "POST":
        form = ConnectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            # Redirect to the same page with #connect anchor
            return redirect(f"{reverse('index')}#connect")
        else:
            messages.error(request, "Sorry, we couldn't send your message.")
            # Keep the form data and scroll to #connect on reload
            scroll_to_connect = True
    else:
        form = ConnectForm()
        scroll_to_connect = False

    context = {
        'about': AboutMe.objects.first(),
        'cp_log': CP_Log.objects.all(),
        'projects': Projects.objects.all(),
        'experiences': Experience.objects.all(),
        'certifications': Certifications.objects.all(),
        'hobbies': Hobbies.objects.all(),
        'form': form,
        'scroll_to_connect': scroll_to_connect,  # Pass this to template
    }
    return render(request, 'interface/index.html', context)


