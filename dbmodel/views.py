from django.shortcuts import render

from .models import warning


def my_view(request):
    data = warning.get_data()
    return render(request, 'test.html', {'data': data})


def warnedit(request):
    processing_id = request.GET.get("num")
    data2 = warning.get_data().filter(id=processing_id)
    for temp in data2:
        warning.objects.filter(id=processing_id).update(info="已处理")
    data = warning.get_data()
    return render(request, 'test2.html', {'data': data})
