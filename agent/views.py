from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
import re


from agent.llm import ask_llm
from agent.memory import store_user_name


@login_required
def home(request):
    return render(request, "index.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "register.html",
                {"error": "Username already exists."}
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name
        )

        store_user_name(str(user.id), name)
        return redirect("/login/")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            request.session["just_logged_in"] = True
            if user.first_name:
                    store_user_name(str(user.id), user.first_name)


            return redirect("/")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/login/")


@login_required
@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    if request.session.get("just_logged_in"):
        request.session.pop("just_logged_in")

        name = request.user.first_name or "there"
        return JsonResponse({
            "reply": f"Welcome {name}! 👋 How can I help you with coding today?"
        })
    data = json.loads(request.body)
    user_msg = data.get("message", "")
    history = data.get("history", "")
    

    reply = ask_llm(user_msg, str(request.user.id))
    return JsonResponse({"reply": reply})
