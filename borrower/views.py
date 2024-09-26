from django.shortcuts import render, redirect
from .forms import BorrowerProfileForm
# Import AnonymousUser for check
from django.contrib.auth.models import AnonymousUser


def apply_for_loan(request):

    if request.method == 'POST':
        form = BorrowerProfileForm(request.POST)
        if form.is_valid():
            borrower_profile = form.save(commit=False)
            borrower_profile.user = request.user  # Assign the logged-in user
            borrower_profile.save()
            # Redirect after successful form submission
            return redirect('home:index')
    else:
        form = BorrowerProfileForm()

    return render(request, 'borrower/apply.html', {'form': form})
