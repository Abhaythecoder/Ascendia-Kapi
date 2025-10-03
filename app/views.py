# --- file: payapp/app/views.py ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import UserSignupForm, UserLoginForm, CreatorProfileForm
from .models import CreatorProfile, Analytics, DonationAttempt

def home(request):
    """Renders the homepage."""
    context = {'page_title': 'Home'}
    return render(request, 'app/home.html', context)

def signup_view(request):
    """Handles user registration using forms.py."""
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)
            user.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('app:login')
        else:
            context = {'page_title': 'Sign Up', 'form': form}
            return render(request, 'app/signup.html', context)
    else:
        form = UserSignupForm()
        context = {'page_title': 'Sign Up', 'form': form}
        return render(request, 'app/signup.html', context)

def login_view(request):
    """Handles user login authentication."""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('app:landing')
            else:
                messages.error(request, 'Invalid username or password.')
                context = {'page_title': 'Login', 'form': form}
                return render(request, 'app/login.html', context)
        else:
            context = {'page_title': 'Login', 'form': form}
            return render(request, 'app/login.html', context)
    else:
        form = UserLoginForm()
        context = {'page_title': 'Login', 'form': form}
        return render(request, 'app/login.html', context)

def logout_view(request):
    """Logs out the current user."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('app:home')

@login_required(login_url='app:login')
def landing(request):
    """Renders the landing page for a logged-in user with analytics data."""
    analytics, created = Analytics.objects.get_or_create(creator=request.user)
    
    total_amount_generated = DonationAttempt.objects.filter(
        creator=request.user
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    highest_amount = DonationAttempt.objects.filter(
        creator=request.user
    ).aggregate(Max('amount'))['amount__max'] or 0
    
    context = {
        'page_title': 'Dashboard',
        'page_views': analytics.page_views,
        'qr_generations': analytics.qr_generations,
        'total_amount_generated': total_amount_generated,
        'highest_amount': highest_amount,
    }
    return render(request, 'app/landing.html', context)

@login_required(login_url='app:login')
def my_profile(request):
    """Displays the profile for the currently logged-in user."""
    profile = request.user.creatorprofile
    context = {'page_title': 'My Profile', 'profile': profile}
    return render(request, 'app/my_profile.html', context)

def creator_profile(request, username):
    """Displays the public profile for a specific creator and tracks page views."""
    user = get_object_or_404(User, username=username)
    profile = user.creatorprofile
    
    # Increment page view count for this creator
    analytics, created = Analytics.objects.get_or_create(creator=user)
    analytics.page_views += 1
    analytics.save()
    
    context = {'page_title': f'{username}\'s Profile', 'creator': user, 'profile': profile}
    return render(request, 'app/creator_profile.html', context)

def find_creator(request):
    """
    Renders the page for finding creators with search functionality.
    """
    query = request.GET.get('q')
    if query:
        creators = User.objects.filter(
            Q(username__icontains=query) | Q(creatorprofile__bio__icontains=query)
        ).order_by('date_joined')
    else:
        creators = User.objects.all().order_by('date_joined')

    context = {
        'page_title': 'Find a Creator',
        'creators': creators,
        'query': query,
    }
    return render(request, 'app/find_creator.html', context)
    
@login_required(login_url='app:login')
def payments(request):
    """Renders the payments page."""
    context = {'page_title': 'Payments'}
    return render(request, 'app/payments.html', context)

@login_required(login_url='app:login')
def settings_view(request):
    """
    Manages the user's settings and profile information.
    """
    if request.method == 'POST':
        form = CreatorProfileForm(request.POST, request.FILES, instance=request.user.creatorprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('app:my_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CreatorProfileForm(instance=request.user.creatorprofile)
    
    context = {
        'page_title': 'Account Settings',
        'form': form,
    }
    return render(request, 'app/settings.html', context)

@require_POST
def qr_generate_api(request, username):
    """
    API endpoint to generate a QR code and record the donation attempt.
    """
    try:
        creator = get_object_or_404(User, username=username)
        amount = request.POST.get('amount')
        
        if not creator.creatorprofile.upi_id:
            return JsonResponse({'success': False, 'error': 'Creator has no UPI ID.'})

        if not amount or not amount.isdigit() or int(amount) <= 0:
            return JsonResponse({'success': False, 'error': 'Invalid amount.'})

        # Save the donation attempt to the database
        DonationAttempt.objects.create(creator=creator, amount=amount)

        # Increment QR generation count (optional, but requested)
        analytics, created = Analytics.objects.get_or_create(creator=creator)
        analytics.qr_generations += 1
        analytics.save()
        
        upi_id = creator.creatorprofile.upi_id
        upi_url = f'upi://pay?pa={upi_id}&am={amount}&pn={creator.username}'
        
        return JsonResponse({'success': True, 'upi_url': upi_url})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='app:login')
def reset_analytics(request):
    """
    Resets all analytics data for the logged-in user.
    """
    if request.method == 'POST':
        Analytics.objects.filter(creator=request.user).update(page_views=0, qr_generations=0)
        DonationAttempt.objects.filter(creator=request.user).delete()
    return redirect('app:landing')


@login_required(login_url='app:login')
def content_management(request):
    """Renders the content management page."""
    context = {'page_title': 'Content'}
    return render(request, 'app/content_management.html', context)

@login_required(login_url='app:login')
def subscriptions(request):
    """Renders the subscriptions page."""
    context = {'page_title': 'Subscriptions'}
    return render(request, 'app/subscriptions.html', context)

@login_required(login_url='app:login')
def analytics(request):
    """Renders the analytics page."""
    context = {'page_title': 'Analytics'}
    return render(request, 'app/analytics.html', context)
