from django.shortcuts import render

def main(request):
    ret = {}
    return render(request, "browse/index.html", ret)
