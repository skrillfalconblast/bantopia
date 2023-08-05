from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import WatchlistActivity

from .forms import EditPasswordForm

User = get_user_model()

# Create your views here.

def login(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':

            display_name = request.POST.get('login-name')
            password = request.POST.get('login-password')

            user = authenticate(request, display_name=display_name, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('/')
            else:
                message = "That profile doesn't seem to exist, if you forgot your password contact skrillfalconblast@icloud.com"
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
                if not User.objects.filter(display_name=display_name):
                    try:
                        other_users = User.objects.all()
                        user = User.objects.create_user(display_name=display_name, password=password)
                        for other_user in other_users: # This would add every previous user as part of the user's watch list to stimulate the community.
                            user.watching.add(other_user)

                        user = authenticate(request, display_name=display_name, password=password)
                        auth_login(request, user)
                        return redirect('/')
                    except ValidationError as email_fail_info:
                        message = 'That email was clearly invalid.'
                    except ValueError:
                        message = 'Fill. In. All. The. Fields.'
                else:
                    message = 'That display name is already in use, contact support@lyceum.com to find the account using it.'
            else:
                message = "Those passwords don't match. Repeat. Those passwords don't match."

            context = {'message' : message}
            
            return render(request, 'profile/create.html', context)

        else:
            return render(request, 'profile/create.html')
    else:
        return redirect('/')

def dashboard(request, display_name):

    if request.user.is_authenticated and request.user.display_name == display_name:


        user = request.user


        if request.method == 'POST':
            orange_choice = request.POST.get('orange-choice')
            blue_choice = request.POST.get('blue-choice')
            green_choice = request.POST.get('green-choice')
            red_choice = request.POST.get('red-choice')
            purple_choice = request.POST.get('purple-choice')
            pink_choice = request.POST.get('pink-choice')
            maroon_choice = request.POST.get('maroon-choice')
            aqua_choice = request.POST.get('aqua-choice')

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
            elif pink_choice:
                user.color = User.PINK
                user.save()
            elif maroon_choice:
                user.color = User.MAROON
                user.save()
            elif aqua_choice:
                user.color = User.AQUA
                user.save()
            
        watching = user.watching.all()
        watchlist_activity = WatchlistActivity.objects.filter(watchlist_activity_user__in=watching).order_by('-watchlist_activity_datetime')[:30]

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

        context = {'watchlist_activity' : timeframed_watchlist_activity}

        return render(request, 'profile/dashboard.html', context)
    
    else:
        return redirect('/')

def edit_profile(request, display_name):

    if request.user.is_authenticated and request.user.display_name == display_name:

        if request.method == 'POST':

            user = request.user

            old_pass = request.POST.get('old_password')
            new_pass1 = request.POST.get('new_password')
            new_pass2 = request.POST.get('confirm_new_password')

            if new_pass1 and new_pass2:
                if new_pass1 == new_pass2:
                    if user.check_password(old_pass):
                        user.set_password(new_pass1)
                        user.save()

                        user = authenticate(request, display_name=user.display_name, password=new_pass1)
                        login(request, user)

                        return redirect('../dashboard')
                    else:
                        print("That isn't your old password!")
                else:
                    print("Your new passwords don't match!")
            else:
                print("Please enter and confirm a new password!")

        context = {}

        context['password_form'] = EditPasswordForm()

        return render(request, 'profile/edit-profile.html', context)
    
    else:
        return redirect('/')

def logout(request):
    auth_logout(request)
    return redirect('/')
