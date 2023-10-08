from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from .models import WatchlistActivity

import random
import re

User = get_user_model()

# Create your views here.

def login(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':

            display_name = request.POST.get('login-name')
            password = request.POST.get('login-password')

            if User.objects.filter(display_name=display_name):
                user = authenticate(request, display_name=display_name, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('/')
                else:
                    message = "incorrect-password"
                    context = {'message' : message}
                    return render(request, 'profile/logIn.html', context)
            else:
                message = "nonexistent-display-name"
                context = {'message' : message}
                return render(request, 'profile/logIn.html', context)
        else:
            return render(request, 'profile/logIn.html')
    else:
        return redirect('/')


def createProfile(request):

    if not request.user.is_authenticated:

        if request.method == 'POST':
            message = None

            display_name = request.POST.get('create-name')

            password1 = request.POST.get('create-password')
            password2 = request.POST.get('create-confirm-password')

            if password1 == password2:
                password = password1
                if len(display_name) <= 20:
                    if re.fullmatch('^[a-zA-Z0-9_]+( [a-zA-Z0-9_]+)*$', display_name):
                        if not User.objects.filter(display_name=display_name).exists():
                            try:
                                other_users = User.objects.all()
                                user = User.objects.create_user(display_name=display_name, password=password)

                                if user:
                                    # This would add every previous user as part of the user's watch list to stimulate the community.
                                    user.watching.set(other_users)

                                    user = authenticate(request, display_name=display_name, password=password)
                                    auth_login(request, user) # Log them in
                                    return redirect('/')
                                else:
                                    message = 'display-name-taken'
                            
                            except ValueError as value_error_info:
                                if str(value_error_info) == 'empty-display-name':
                                    message = 'empty-display-name'
                                elif str(value_error_info) == 'empty-password':
                                    message = 'empty-password'
                        else:
                            message = 'display-name-taken'
                    else:
                        message = 'invalid-characters'
                else:
                    message = 'display-name-overflow'
            else:
                message = "mismatched-passwords"

            context = {'message' : message}
            
            return render(request, 'profile/create.html', context)

        else:
            return render(request, 'profile/create.html')
    else:
        return redirect('/')

def dashboard(request, display_name):

    if request.user.is_authenticated and request.user.display_name == display_name:

        tab_texts = [
            "Your Dashboard",
            "Your Dashboard",
            "Your Dashboard",
            "Your Dashboard",
            "Central Headquarters",
            "HQ",
            "The ManCave",
            f"{request.user.display_name}'s Den",
            "The Chrome Dome",
            "Base Control",
            "Customisation Habitation",
            "Command Land",
            "Rule School"
        ]

        tab_text = random.choice(tab_texts)

        user = request.user


        if request.method == 'POST':
            orange_choice = request.POST.get('orange-choice')
            blue_choice = request.POST.get('blue-choice')
            green_choice = request.POST.get('green-choice')
            red_choice = request.POST.get('red-choice')
            purple_choice = request.POST.get('purple-choice')
            brown_choice = request.POST.get('brown-choice')
            maroon_choice = request.POST.get('maroon-choice')
            dreadnought_choice = request.POST.get('dreadnought-choice')

            if orange_choice:
                user.color = User.ORANGE
                user.save()
            elif blue_choice:
                user.color = User.BLUE
                user.save()
            elif green_choice:
                user.color = User.GREEN
                user.save()
            elif red_choice:
                user.color = User.RED
                user.save()
            elif purple_choice:
                user.color = User.PURPLE
                user.save()
            elif brown_choice:
                user.color = User.BROWN
                user.save()
            elif maroon_choice:
                user.color = User.MAROON
                user.save()
            elif dreadnought_choice:
                user.color = User.DREADNOUGHT
                user.save()
            
        watching = user.watching.all()
        watchlist_activity = WatchlistActivity.objects.filter(watchlist_activity_user__in=watching).select_related('watchlist_activity_user', 'watchlist_activity_post').order_by('-watchlist_activity_datetime')[:30]

        timeframes = []

        if watchlist_activity:
            for activity in watchlist_activity:
                if 'second' in activity.longAgo():
                    timeframes.append('seconds')
                elif 'minute' in activity.longAgo():
                    timeframes.append('minutes')
                elif 'hour' in activity.longAgo():
                    timeframes.append('hours')
                else:
                    timeframes.append(None)
            
            timeframed_watchlist_activity = zip(watchlist_activity, timeframes) 
        else:
            timeframed_watchlist_activity = []

        context = {'watchlist_activity' : timeframed_watchlist_activity, 'tab_text' : tab_text}

        return render(request, 'profile/dashboard.html', context)
    
    else:
        return redirect('/')

def edit_profile(request, display_name):

    if request.user.is_authenticated and request.user.display_name == display_name:

        tab_texts = [
            "The Ol' Switch-a-roo",
            "Edit Profile",
            "Edit Profile",
            "Edit Profile",
            "Metamorphosis",
            "Changing something?",
            "No peeping!",
            "Shhhh! It's a secret.",
        ]

        tab_text = random.choice(tab_texts)

        message = ''

        if request.method == 'POST':

            user = request.user

            old_pass = request.POST.get('old_password')
            new_pass1 = request.POST.get('new_password')
            new_pass2 = request.POST.get('confirm_new_password')

            new_name = request.POST.get('new_display_name')

            if new_pass1 and new_pass2 and not new_name:
                if new_pass1 == new_pass2:
                    if user.check_password(old_pass):
                        user.set_password(new_pass1)
                        user.save()

                        user = authenticate(request, display_name=user.display_name, password=new_pass1)
                        auth_login(request, user)

                        return redirect('./dashboard')
                    else:
                        message = 'incorrect-old-password'
                else:
                    message = 'mismatched-new-passwords'
            elif new_name and not new_pass1 and not new_pass2 and not old_pass:

                if len(new_name) <= 20:
                    if re.fullmatch('^[a-zA-Z0-9_]+( [a-zA-Z0-9_]+)*$', new_name):

                        if not User.objects.filter(display_name=new_name):

                            user.display_name = new_name

                            user.save()
                            return redirect(f'/{user.display_name}/dashboard')
                        else:
                            message = 'display-name-taken'

                    else:
                        message = 'invalid-characters'

                else:
                    message = 'display-name-overflow'

            elif new_pass1 and new_pass2 and new_name:
                if new_pass1 == new_pass2:
                    if len(new_name) <= 20:
                        if re.fullmatch('^[a-zA-Z0-9_]+( [a-zA-Z0-9_]+)*$', new_name):
                            if not User.objects.filter(display_name=new_name):
                                if user.check_password(old_pass):
                                    user.display_name = new_name
                                    user.set_password(new_pass1)
                                    user.save()

                                    user = authenticate(request, display_name=new_name, password=new_pass1)
                                    auth_login(request, user)

                                    return redirect(f'/{user.display_name}/dashboard')
                                else:
                                    message = 'incorrect-old-password'
                            else:
                                message = 'display-name-taken'
                        else:
                            message = 'invalid-characters'
                    else:
                        message = 'display-name-overflow'
                else:
                    message = 'mismatched-new-passwords'
            else:
                message = 'empty-fields'

        context = {'tab_text' : tab_text, 'message' : message}

        return render(request, 'profile/edit-profile.html', context)
    
    else:
        return redirect('/')

def logout(request):
    auth_logout(request)
    return redirect('/')
