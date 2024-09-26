from django.shortcuts import render, redirect
from .forms import InvestorProfileForm

def investor_dashboard(request):
    if request.method == 'POST':
        form = InvestorProfileForm(request.POST)
        if form.is_valid():
            investor_profile = form.save(commit=False)  # Don't save to the database yet
            investor_profile.user = request.user  # Set the user to the logged-in user
            investor_profile.save()  # Save to the database
            return redirect('home:index')
    else:
        form = InvestorProfileForm()

    return render(request, 'investor/dashboard.html', {'form': form})
