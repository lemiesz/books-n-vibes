from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.http import JsonResponse
from django.db.models import F
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from .forms import SignupForm, ProfileForm, MixForm, FeaturedForm
from .models import Profile, Mix, FeaturedDJ


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_profile')
    return render(request, 'home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard_profile')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, display_name=user.username)
            login(request, user)
            return redirect('dashboard_profile')
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})


class LoginView(DjangoLoginView):
    template_name = 'auth/login.html'


class LogoutView(DjangoLogoutView):
    next_page = '/'


@login_required
def dashboard_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'display_name': request.user.username})
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'dashboard/profile.html', {'form': form})


@login_required
def dashboard_mixes(request):
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            Mix.objects.filter(id=request.POST['delete_id'], dj=request.user).delete()
        else:
            form = MixForm(request.POST, request.FILES)
            if form.is_valid():
                mix = form.save(commit=False)
                mix.dj = request.user
                mix.save()
    form = MixForm()
    mixes = Mix.objects.filter(dj=request.user)
    return render(request, 'dashboard/mixes.html', {'form': form, 'mixes': mixes})


@login_required
def dashboard_featured(request):
    message = None
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            FeaturedDJ.objects.filter(id=request.POST['delete_id'], owner=request.user).delete()
        else:
            form = FeaturedForm(request.POST)
            if form.is_valid():
                try:
                    linked = User.objects.get(username=form.cleaned_data['username'])
                    FeaturedDJ.objects.get_or_create(owner=request.user, linked=linked)
                except User.DoesNotExist:
                    form.add_error('username', 'User not found')
        
    form = FeaturedForm()
    featured = FeaturedDJ.objects.filter(owner=request.user).select_related('linked')
    return render(request, 'dashboard/featured.html', {'form': form, 'featured': featured})


def dj_page(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.filter(user=user).first()
    mixes = Mix.objects.filter(dj=user, visibility=Mix.PUBLIC).order_by('-created_at')
    featured = FeaturedDJ.objects.filter(owner=user).select_related('linked')
    return render(request, 'public/dj_page.html', {
        'dj': user,
        'profile': profile,
        'mixes': mixes,
        'featured': featured,
    })


def mix_page(request, slug):
    mix = get_object_or_404(Mix, slug=slug)
    return render(request, 'public/mix_page.html', {'mix': mix})


@require_POST
def api_mix_played(request, mix_id):
    mix = get_object_or_404(Mix, id=mix_id)
    Mix.objects.filter(id=mix_id).update(play_count=F('play_count') + 1)
    mix.refresh_from_db()
    return JsonResponse({'ok': True, 'play_count': mix.play_count})
