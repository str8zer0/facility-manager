from django.shortcuts import render


def home(request):
    return render(request, "common/home.html")


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
