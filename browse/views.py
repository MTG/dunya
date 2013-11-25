from django.shortcuts import render, redirect

def main(request):
    return redirect("carnatic-main")
    ret = {}
    return render(request, "browse/index.html", ret)
