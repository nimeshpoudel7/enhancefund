from django.shortcuts import render


def loan_list(request):
    return render(request, 'loans/list.html')
