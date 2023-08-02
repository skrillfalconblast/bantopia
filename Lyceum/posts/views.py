from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.views.decorators.csrf import csrf_exempt

from django.db.models import F, ExpressionWrapper, Value, FloatField, Case, When, IntegerField
from django.db.models.functions import Round, Log, Greatest, Abs


from .models import Post, Tag, Vote, Draft, Visit
from chat.models import Message
from users.models import WatchlistActivity

import random



# Create your views here.

User = get_user_model()

def sort_trending():
    posts = Post.objects.annotate(score=ExpressionWrapper(
        Round((F('post_timestamp_created') / 45000) + Log(10, Greatest(F('post_number_of_messages'), 1)), precision=7), output_field=FloatField()
        ), sort=Value("trending")).order_by('-score')[:100]
    
    return posts
        
def sort_controversial():
    posts = Post.objects.annotate(total=ExpressionWrapper(Abs(F('post_number_of_yes_votes') + F('post_number_of_no_votes')), IntegerField()), score=Case(When(total=0, then=Value(0, output_field=FloatField())), default=ExpressionWrapper(
        (F('post_timestamp_created') / 45000) + Log(10, (F('total')) / Greatest(Abs(F('post_number_of_yes_votes') - F('post_number_of_no_votes')), 1)), output_field=FloatField()
    )), sort=Value("controversial")).order_by('-score')[:100] 
    
    return posts

def search(search_term):
    posts = Post.objects.annotate(rank=SearchRank(SearchVector('post_title'), SearchQuery(search_term))).order_by('-rank')[:100]

    return posts

@csrf_exempt
def index(request):

    user = request.user # Pulls user from request for authentication checks within the template.   

    if user.is_authenticated:

        sort = request.GET.get('sort')
        search_term = request.GET.get('search')

        if request.method == 'GET':
            if search_term:
                if search_term != '':
                    posts = search(search_term)

            elif sort == 'trending':

                posts = sort_trending()

            elif sort == 'controversial':

                posts = sort_controversial()

            else:
                posts = Post.objects.order_by('-post_datetime_created')

        else:
            posts = Post.objects.order_by('-post_datetime_created')

        user = request.user # Pulls user from request for authentication checks within the template.   

        watching = user.watching.all()
        watchlist_activity = WatchlistActivity.objects.filter(watchlist_activity_user__in=watching).order_by('-watchlist_activity_datetime')

        visits = Visit.objects.filter(visit_user=user).order_by('-visit_datetime')

        context = {'posts' : posts, 'user' : user, 'watchlist_activity' : watchlist_activity, 'visits' : visits}

        return render(request, 'index.html', context)
    else:
        if request.method == 'GET':
            sort = request.GET.get('sort')

            if sort == 'trending': 
                posts = sort_trending()
            elif sort == 'controversial':
                posts = sort_controversial()
            else:
                posts = Post.objects.order_by('-post_datetime_created')

        else:
            posts = Post.objects.order_by('-post_datetime_created')

        context = {'posts' : posts}

        return render(request, 'index.html', context)


def write(request):

    user = request.user

    if user.is_authenticated:

        def stringToList(string):
            return list(string.split(', '))
        
        if request.method == 'POST': # If a submit button was clicked
            postPressed = request.POST.get('post-btn')
            draftPressed = request.POST.get('draft-btn')
            deletePressed = request.POST.get('delete-btn')

            draft_type = request.POST.get('type')
            draft_title = request.POST.get('title')
            draft_desc = request.POST.get('text')
            draft_tags = request.POST.get('tags') # They are simply stored in a string for ease of storage.

            try:
                if postPressed: # If the post button was pressed.

                    post_code = get_random_string(length=8)



                    if draft_type.strip() != '' and draft_title.strip() != '' and draft_desc.strip() != '':
                        post = Post(
                            post_code=post_code, post_type=draft_type,
                            post_title=draft_title, post_desc=draft_desc,
                            post_author=user, post_author_name=user.display_name,
                            post_number_of_messages=0)
                        post.save()

                        post = Post.objects.get(post_code=post_code)

                        tags = stringToList(draft_tags)

                        for tag in tags:

                            tag = Tag(tag_text=tag, tag_post=post)
                            tag.save()


                        existing_draft_code = request.GET.get('drafting')

                        if Draft.objects.filter(draft_code=existing_draft_code, draft_author=user): # If an existing draft is being posted

                            draft = Draft.objects.get(draft_code=existing_draft_code, draft_author=user)

                            draft.delete()

                        if draft_type == 'DE':
                            WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.DECLARE)
                        elif draft_type == 'TH':
                            WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.THEORISE)

                        return redirect('/') # If something is posted, the user will always be redirected to the homepage.
                    else:
                        return render(request, 'post/write.html')
                
                elif draftPressed: # If draft button was pressed

                    existing_draft_code = request.GET.get('drafting')

                    if Draft.objects.filter(draft_code=existing_draft_code, draft_author=user): # If an existing draft is being edited

                        draft = Draft.objects.get(draft_code=existing_draft_code, draft_author=user)

                        draft.draft_type = draft_type
                        draft.draft_title = draft_title
                        draft.draft_desc = draft_desc
                        draft.draft_tags = draft_tags
                        draft.save()

                    else: # If a new draft is being made

                        draft_code = get_random_string(length=8)

                        draft = Draft(
                            draft_code=draft_code, draft_type=draft_type,
                            draft_title=draft_title, draft_desc=draft_desc,
                            draft_author=user, draft_tags=draft_tags)
                        draft.save()

                    return redirect('/post/your-drafts')

                elif deletePressed:

                    existing_draft_code = request.GET.get('drafting')

                    if Draft.objects.filter(draft_code=existing_draft_code, draft_author=user): # If the queried draft exists

                        draft = Draft.objects.get(draft_code=existing_draft_code, draft_author=user)

                        draft.delete()
                        
                        return redirect('/post/your-drafts')
                    
                    else: # The queried draft doesn't exist or nothing is quereid

                        return render(request, '/post/write.html')

            except:
                return render(request, '/post/write.html')

        else: # If the page is simply loading, without a POST request

            if request.method == 'GET': # If there is a URL query

                draft_code = request.GET.get('drafting')

                if Draft.objects.filter(draft_code=draft_code, draft_author=request.user): # If the queried draft exists

                    draft = Draft.objects.get(draft_code=draft_code, draft_author=request.user)

                    context = {'draft' : draft}
                    
                    return render(request, 'post/write.html', context)
                else: # If the method is recognised as GET but the queried draft doesn't exist
                    return render(request, 'post/write.html')
            
            else: # If the page is simply loading without any query
                return render(request, '/post/write.html')
    return redirect('/create-profile/')
             

def drafts(request):
    user = request.user

    if user.is_authenticated:
        drafts = Draft.objects.filter(draft_author=user)

        context = {'drafts' : drafts}

        return render(request, 'post/drafts.html', context)
    else:
        return redirect('/create-profile/')

def posts(request):
    if request.user.is_authenticated:
        if Post.objects.filter(post_author=request.user):
            context = {'posts' : Post.objects.filter(post_author=request.user)}
            return render(request, 'post/posts.html', context)
        else:
            context = {'posts' : None}
            return render(request, 'post/posts.html', context)
    else:
        return redirect('/create-profile/')
    
# ------------------------------------------------

def commContent(request, post_code):
    
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)

        tags = Tag.objects.filter(tag_post=post)

        user = request.user

        if user.is_authenticated:
            try:
                if post != Visit.objects.latest('visit_datetime').visit_post:

                    Visit.objects.create(visit_post=post, visit_user=user)
    
            except Visit.DoesNotExist:
                Visit.objects.create(visit_post=post, visit_user=user)

       
        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}
        
        context = {'post' : post, 'tags' : tags, 'y' : votes["y"], 'n' : votes["n"]}
        return render(request, 'comms/content.html', context)
    else:
        return redirect('/') # Make a 404 error page 
        

def commMastercases(request, post_code):
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)
       
        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}

        context = {'post' : post, 'y' : votes["y"], 'n' : votes["n"]}
        return render(request, 'comms/cases.html', context)
    else:
        return redirect('/') # Make a 404 error page 

def commCounters(request, post_code):
    if Post.objects.filter(post_code=post_code):
        post = Post.objects.get(post_code=post_code)
       
        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}

        counters = list(Message.objects.filter(message_post=post, message_score__gt=1).order_by('-message_score')[:5])

        quip_list = ['souls, apparently, liked this.', 'gentlemen found this appealing.', 
                 'losers felt positively stimulated.', 'people were pleased.', 'old boys were chuffed.',
                 'gangstas approved.', 'cowboys were wrangled.', 'masters nodded their heads.',
                 'zombies were saaaatisfiiiiied!', 'ancients sent you a poke.', 'youngsters double tapped.',
                 'creeps shot a wink.', 'brothers agreed.', 'maidens were charmed.',
                 'fathers weren\'t disappointed!', 'astronauts went over the moon.', 'dudez were pumped.',
                 'kids were hyped.', 'goblins were smitten.', 'sa faagaeetia alii.', 
                 'girls fancied this.', 'buisnessmen profited.', 'dragons were fired up!',
                 'birds were eggcited!', 'cars went vroom vroom!', 'links were forged!', 'meows were meowed.']
        
        quips = random.sample(quip_list, len(counters))

        counters_and_quips = zip(counters, quips)
        
        context = {'post' : post, 'counters' : counters_and_quips, 'y' : votes["y"], 'n' : votes["n"]}

        return render(request, 'comms/counters.html', context)
    else:
        return redirect('/') # Make a 404 error page 

def commDogs(request, post_code):  
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)
       
        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}
                                
        if post.post_TPP:
            TPP = post.post_TPP.display_name
        else:
            TPP = '---'

        if post.post_PEN1:
            PEN1 = post.post_PEN1.display_name
        else:
            PEN1 = '???'

        context = {'post' : post, 'TPP' : TPP, 'PEN1' : PEN1, 'y' : votes["y"], 'n' : votes["n"]}

        return render(request, 'comms/dogs.html', context)
    else:
        return redirect('/') # Make a 404 error page 

################ ERROR PAGES #######################  

def csrf_failure(request, reason=""):
    quip_list = ['Call me crazy, but it looks like you have a werid looking csrf verification token. Do me a favour and <span>reload</span> the page, to fix this digusting error.',
             'Your csrf verficiation token is super yucky, <span>reload</span> and get a new one!',
             "WOAAAAAAHHHHH, I ain't never seen a csrf token looking like that! <span>Reload</span> to heal my eyes!",
             "Your csrf verficaiton token is so ugly it crashed the server! <span>Reload</span> for all our sakes.", 
             "I've seen some messed up things in my time, but that csrf verification token... *shudders* A sight like that could grow a baby a beard. <span>Reload</span>, because that's nasty!"]
    
    quip = random.choice(quip_list)

    context = {'quip' : quip}

    return render(request, 'errors/csrf_failure.html', context)