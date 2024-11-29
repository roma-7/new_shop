from django.shortcuts import render


def about_us(request):
    return render(request, "main/about_us.html")


def faq(request):
    return render(request, "main/faq.html")
