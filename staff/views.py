from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from borrower.models import BorrowerProfile


def is_staff(user):
    return user.is_authenticated and user.role == 'staff'


@user_passes_test(is_staff)
def verify_documents(request):
    borrowers = BorrowerProfile.objects.filter(
        documentverification__isnull=True)
    return render(request, 'staff/verify_documents.html', {'borrowers': borrowers})


@user_passes_test(is_staff)
def approve_borrower(request, borrower_id):
    borrower = BorrowerProfile.objects.get(id=borrower_id)
    DocumentVerification.objects.create(borrower=borrower, is_verified=True)
    return redirect('verify_documents')
