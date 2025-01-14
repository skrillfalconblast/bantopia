from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.core.mail import send_mail

from django.db.models import F, ExpressionWrapper, Value, FloatField, Case, When, IntegerField, Max, Subquery, OuterRef, Prefetch, Q
from django.db.models.functions import Round, Log, Greatest, Abs

from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models.functions import JSONObject

from django.utils.html import escape

from .models import Post, Tag, Vote, Draft, Visit, Splash
from chat.models import Message
from users.models import WatchlistActivity, Ban

from .serializers import PostSerializer

import random


# Create your views here.

User = get_user_model()

def counterHack(posts):
    for post in posts:
        #counters = list(Message.objects.filter(message_post=post, message_score__gt=1).values_list('message_content', flat=True).order_by('-message_score')[:5])
        
        counters = post.counters[:5]

        counterString = ''

        for i, counter in enumerate(counters):
            rank = f'<span>#{i+1}</span> {escape(counter)}'

            if counterString == '':
                counterString = counterString + rank
            else:
                counterString = counterString + ' ' + rank

        
        if counterString:
            post.counters = counterString
        else:

            ticker_texts = ["<span>Calm,</span> endless calm. <span>Broken.</span> The water's surface draws <span>near.</span> The <span>glass heaven</span> enveloping your form feels <span>large</span> under the surface. It’s <span>all</span>, it’s everything. But you were made to <span>breathe.</span> I need <span>air.</span> Oh, <span>we’re floating</span>, steadily towards the liquid veil. The <span>bubbles</span> look crystalline, playing with <span>the heavy light</span> as they hustle towards <span>the surface.</span> I’m moving up with <span>them.</span> Huh, <span>look at that</span>, I see something <span>behind the water</span>, something <span>above</span>, almost getting farther as I <span>draw closer.</span> I <span>tear</span> through that veil. Infinity <span>basks</span> before me. Sky, sun, trees, nature in all its glory, <span>light</span> as I have never seen before. A <span>black hawk</span> soars above, my head tracks its flight. <span>Let’s go.</span> ",
                            "<span>Bantopia</span> is literally the <span>coolest place</span> to be on <span>the Internet.</span> <span>Sure</span>, it’s a <span>bit crazy</span>, but <span>it’s pretty fun.</span> You see <span>this ticker</span>, it’s pretty cool. <span>But bro,</span> why in the world are you <span>staring</span> at it? If you’re <span>afk</span> I’ll understand, <span>but otherwise,</span> it’s kind of <span>weird</span>. Okay, <span>stop staring</span> at this point. <span>It’s rude</span>. Oh gosh, I probably <span>provoked</span> you to continue <span>looking at me.</span> In fact, <span>whatever</span>, I don’t have <span>anything to hide!</span> Keep <span>looking</span>, it’s your time that’s <span>being wasted</span>. Unlike you, <span>I have things to do</span> apart from staring at <span>randomly assigned</span> ticker text. Peace <span>out.</span>",
                            "You are likely on <span>bantopia.com</span>. This is likely the <span>gazillionth time</span> you’ve read this message. You are likely on the <span>New</span> tab. Your screen is mostly composed of the colors: <span>orange</span> and white. You probably like to <span>debate</span> or argue. You probably live in the northern <span>hemisphere</span>. You’re probably a cool <span>guy</span>. You’re likely about to enter a <span>chat</span>. You’re likely street <span>smart</span>. You likely prefer YouTube to other <span>social media.</span> This is likely the first time you’ve <span>read</span> this message. You’re likely predicting this <span>ticker</span> is going to end soon. You’re likely correct<span>.</span>",
                            "Don’t think, <span>act.</span> Just <span>do</span> it! <span>Think</span> with your mind, not your <span>brain</span>! Get into the <span>zone!</span> <span>Man up</span>! Listen to <span>your instincts!</span> Click the post! JUST CLICK THE POST <span>BRO!</span> It’s not even <span>hard!</span> Just make the <span>choice</span> and stick by it! Do <span>everything you can</span> to supplement your journey. <span>You know</span> your purpose, act now! You only <span>live once</span>! This is you’re <span>only shot</span> at greatness! CLICK THE POST! It’s all <span>background noise</span>! Don’t think, <span>act!</span> Click the <span>post!</span>",
                            "It started when an <span>alien device</span> did what it did. And <span>stuck itself</span> upon his wrist with <span>secrets</span> that it hid. Now he's got <span>super powers,</span> he's no ordinary kid, he’s <span>Ben 10</span>! So if you <span>see him,</span> you might be in for a <span>big surprise.</span> He'll turn <span>into an alien</span> before your very eyes. He's <span>slimy, creepy, fast and strong</span>, he's every <span>shape and size</span>, he's <span>Ben 10!</span> Armed with power, he's on the <span>case.</span> Fighting off evil from <span>Earth</span> or <span>space.</span> He'll <span>never stop</span> till he makes them <span>pay.</span> ‘Cause he's <span>the baddest kid</span> to ever save the day! <span>Ben 10!</span>",
                            "There is no one <span>righteous</span>, not even <span>one</span>; there is no one <span>who understands;</span> there is no one who <span>seeks God</span> <span>All have turned away</span>, they have together <span>become worthless;</span> there is <span>no one who does good</span>, not even <span>one.</span> Their throats are <span>open graves;</span> their tongues <span>practice deceit</span>. The <span>poison of vipers</span> is on their lips. Their mouths <span>are full of cursing</span> and bitterness. Their feet are swift to <span>shed blood;</span> ruin and misery <span>mark their ways,</span> and the way of peace <span>they do not know</span>. There is <span>no fear of God</span> before their eyes.",
                            "<span>In the beginning</span>, God created the <span>heavens</span> and the earth. The earth was <span>without form and void</span>, and <span>darkness</span> was over the face of the <span>deep</span>. And the <span>Spirit of God</span> was hovering over the face of <span>the waters.</span> And God said, “Let there be <span>light</span>,” and there was <span>light</span>. And God saw that the <span>light was good.</span> And God separated the <span>light</span> from the <span>darkness</span>. God called the <span>light Day,</span> and the <span>darkness</span> he called <span>Night</span>. And there was <span>evening</span> and there was <span>morning</span>, the first <span>day.</span>",
                            "The <span>cat</span> (Felis catus) is a <span>domestic species</span> of small <span>carnivorous</span> mammal. It is the <span>only</span> domesticated species in the family <span> Felidae</span> and is commonly referred to as the <span>kitty cat</span> or <span>the pussy cat</span> to distinguish it from the <span>wild members</span> of the family. Cats are <span>commonly</span> kept as <span>house pets</span> but can also be farm cats or <span>feral cats</span>; the feral cat ranges freely and <span>adores human contact</span>. Domestic cats are <span>valued</span> by humans for <span>comdedic value</span> and their ability to <span>eradicate</span> vermin. About 60 cat breeds are <span>recognized</span> by various cat <span>tamers</span>, such as the <span>fluffy</span> cat, the <span>short-hair</span> cat and the <span>no</span> hair cat.",
                            "This, is <span>Berk</span>. It's <span>twelve days</span> North of <span>hopeless</span>, and a <span>few degrees</span> South of <span>freezing to death</span>. It's located <span/>solidly</span> on <span>the meridian of misery</span>. My <span>village</span>. In a word, <span>sturdy</span>. And it's been <span>here</span> for <span>seven generations</span>, but <span>every single building</span> is <span>new</span>. We have <span>fishing</span>, hunting, and a charming <span>view of the sunsets</span>. The only <span>problems</span> are the <span>pests</span>. You <span>see</span>, most <span>places</span> have mice or <span>mosquitoes</span>. We have... <span>dragons</span>. Most people would <span>leave</span>. Not us. <span>We're Vikings</span>. We have, <span>stubbornness</span> issues. <span>My</span> name's <span>Hiccup</span>. Great <span>name</span>, I <span>know</span>. But, it's not <span>the worst</span>. <span/>Parents<span> believe a <span>hideous</span> name will <span>frighten off</span> gnomes and trolls. Like our <span>charming</span> Viking demeanor wouldn't do that.",
                            "<span>Water.</span> Earth. <span>Fire.</span> Air. Long ago, <span>the four nations</span> lived together in <span>harmony</span>. Then, everything changed when <span>the Fire Nation attacked</span>. Only the <span>Avatar</span>, master of all <span>four elements</span>, could stop them, but when the <span>world</span> needed him most, <span>he vanished</span>. A hundred years passed and <span>my brother</span> and I discovered the new Avatar, an <span>airbender</span> named Aang. And although his <span>airbending skills are great</span>, he has <span>a lot to learn</span> before he's ready to save anyone. But I believe <span>Aang</span> can <span>save the world</span>.",
                            "He <span>chose</span> the path of <span>perpetual torment</span>. In his <span>ravenous</span> hatred he <span>found no peace</span>, and with <span>boiling blood</span> he <span>scoured</span> <span>the umbral plains</span> seeking <span>vengeance</span> against <span>the dark lords</span> who <span>had wronged him.</span> He <span>wore the crown</span> of the <span>knight sentinels</span>, and <span>those</span> who <span>tasted</span> the <span>bite of his sword</span> named him the <span>Doomslayer<span>. <span>Tempered<span> by the <span>fires of hell<span>, his <span>iron will</span> remained <span>steadfast</span> through the <span>passage</span> that <span>preys</span> upon the <span>weak</span>, for <span>he<span> alone was <span>the hell walker</span>, the <span>unchained predator</span> who sought <span>retribution</span> in <span>all quarters</span>, dark and <span>light</span>, <span>fire</span> and ice, in <span>the beginning</pan> and the end<span>.</span> And <span>he hunted</span> the <span>slaves of doom</span> with <span>barbarous cruelty</span>; for he <span>passed</span> through the <span>divide</span> as none but demon <span>had before.</span>"]
            
            post.ticker_text = random.choice(ticker_texts)

    return posts

def sort_new():

    posts = Post.objects.prefetch_related(Prefetch('message_set')).annotate(last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values(data=JSONObject(
            content="message_content", datetime_sent="message_datetime_sent"
        ))[:1]), counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=1), ordering='-message__message_score')).order_by('-post_datetime_created')

    posts = counterHack(posts)

    return posts

def sort_trending():
    #posts = Post.objects.annotate(score=ExpressionWrapper(
        #Round((F('post_timestamp_created') / 45000) + Log(10, Greatest(F('post_number_of_messages'), 1)), precision=7), output_field=FloatField()
        #), sort=Value("trending")).order_by('-score')[:100]
    
    posts = Post.objects.prefetch_related(Prefetch('message_set')).alias(
        latest_message=Max('message__message_datetime_sent'), 
    ).annotate(last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values(data=JSONObject(
            content="message_content", datetime_sent="message_datetime_sent"
        ))[:1]), counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=1), ordering='-message__message_score')).order_by('-latest_message')

    posts = counterHack(posts)

    return posts
        
def sort_controversial():
    posts = Post.objects.prefetch_related(Prefetch('message_set')).annotate(total=ExpressionWrapper(Abs(F('post_number_of_yes_votes') + F('post_number_of_no_votes')), IntegerField()), score=Case(When(total=0, then=Value(0, output_field=FloatField())), default=ExpressionWrapper(
        (F('post_timestamp_created') / 45000) + Log(10, (F('total')) / Greatest(Abs(F('post_number_of_yes_votes') - F('post_number_of_no_votes')), 1)), output_field=FloatField()
    )), sort=Value("controversial"), 
    last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values(data=JSONObject(
            content="message_content", datetime_sent="message_datetime_sent"
        ))[:1]), counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=1), ordering='-message__message_score')).order_by('-score')[:100] 

    posts = counterHack(posts)
    
    return posts

def search(search_term):
    posts = Post.objects.prefetch_related(Prefetch('message_set')).annotate(rank=SearchRank(SearchVector('post_title'), SearchQuery(search_term)), 
                                  last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values('message_content')[:1])
                                  , counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=1), ordering='-message__message_score')).order_by('-rank')[:100]

    counterHack(posts)

    return posts

def tag_search(search_term):
    posts = Post.objects.prefetch_related(Prefetch('message_set')).annotate(rank=SearchRank(SearchVector('tag__tag_text'), SearchQuery(search_term)), 
                                  last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values('message_content')[:1])
                                  , counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=1), ordering='-message__message_score')).order_by('-rank')[:100]

    counterHack(posts)

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
                    if search_term[0] == '#':
                        posts = tag_search(search_term)
                    else:
                        posts = search(search_term)

            elif sort == 'trending':

                posts = sort_trending()

            elif sort == 'controversial':

                posts = sort_controversial()

            else:

                posts = sort_new()

                #posts = Post.objects.annotate(counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=-1), ordering='-message__message_score')).order_by('-post_datetime_created')

        else:

            posts = sort_new()

        user = request.user # Pulls user from request for authentication checks within the template.   
        
        watching = user.watching.all()
        
        watchlist_activity = WatchlistActivity.objects.filter(watchlist_activity_user__in=watching).select_related('watchlist_activity_user', 'watchlist_activity_post').order_by('-watchlist_activity_datetime')[:50]

        visits = Visit.objects.filter(visit_user=user).select_related('visit_post').order_by('-visit_datetime')[:50]

        user_notified_set = set(user.post_set.values_list('pk',flat=True))

        try: 
            splash_text = Splash.objects.all().latest('splash_datetime').splash_text
        except:
            splash_text = "Something's wrong..."

        context = {'posts' : posts, 'user' : user, 'watchlist_activity' : watchlist_activity, 'visits' : visits, 'user_notified_set' : user_notified_set, 'splash_text' : splash_text}

        return render(request, 'index.html', context)
    else:
        if request.method == 'GET':

            sort = request.GET.get('sort')

            if sort == 'trending': 

                posts = sort_trending()

            elif sort == 'controversial':

                posts = sort_controversial()

            else:

                posts = sort_new()

        else:
            posts = sort_new()

        try: 
            splash_text = Splash.objects.all().latest('splash_datetime').splash_text
        except:
            splash_text = "Something's wrong..."

        context = {'posts' : posts, 'user_notified_set' : None, 'splash_text' : splash_text}

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

            draft_type = request.POST.get('type').strip()
            draft_title = request.POST.get('title').strip()
            draft_desc = request.POST.get('text').strip()
            draft_tags = request.POST.get('tags').strip() # They are simply stored in a string for ease of storage.

            post_user = request.POST.get('user')
            if post_user:
                post_user = post_user.strip()


            try:
                if postPressed: # If the post button was pressed.

                    if not Post.objects.filter(post_title=draft_title, post_desc=draft_desc): # A if previous identical post doesn't exist.

                        if not Ban.objects.filter(banned_user=user):

                            if draft_type != '' and draft_title != '' and draft_desc != '':

                                if user.is_superuser and post_user:

                                    try:
                                        post_user_obj = User.objects.get(display_name=post_user)
                                    except User.DoesNotExist:
                                        try:
                                            post_user_obj = User.objects.create_user(display_name=post_user, password='password')
                                            user.puppets.add(post_user_obj)
                                        except:
                                            post_user_obj = None

                                    if post_user_obj:
                                        
                                        post_code = get_random_string(length=8)

                                        post = Post(
                                            post_code=post_code, post_type=draft_type,
                                            post_title=draft_title, post_desc=draft_desc,
                                            post_author=post_user_obj, post_author_name=post_user_obj.display_name,
                                            post_number_of_messages=0)
                                        
                                        post.save()

                                        post = Post.objects.get(post_code=post_code)

                                        tags = stringToList(draft_tags)

                                        for tag in tags:
                                            
                                            tag = Tag(tag_text=tag[:50], tag_post=post)
                                            tag.save()


                                        existing_draft_code = request.GET.get('drafting')

                                        if Draft.objects.filter(draft_code=existing_draft_code, draft_author=post_user_obj): # If an existing draft is being posted

                                            draft = Draft.objects.get(draft_code=existing_draft_code, draft_author=post_user_obj)

                                            draft.delete()

                                        if draft_type == 'DE':
                                            WatchlistActivity.objects.create(watchlist_activity_user=post_user_obj, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.DECLARE)
                                        elif draft_type == 'TH':
                                            WatchlistActivity.objects.create(watchlist_activity_user=post_user_obj, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.THEORISE)
                                        elif draft_type == 'QU':
                                            WatchlistActivity.objects.create(watchlist_activity_user=post_user_obj, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.ASK)
                                        
                                    else:    
                                        return render(request, 'post/write.html')
                                    
                                else:

                                    post_code = get_random_string(length=8)

                                    post = Post(
                                        post_code=post_code, post_type=draft_type,
                                        post_title=draft_title, post_desc=draft_desc,
                                        post_author=user, post_author_name=user.display_name,
                                        post_number_of_messages=0)
                                
                                    post.save()

                                    post = Post.objects.get(post_code=post_code)

                                    tags = stringToList(draft_tags)

                                    for tag in tags:
                                        
                                        tag = Tag(tag_text=tag[:50], tag_post=post)
                                        tag.save()


                                    existing_draft_code = request.GET.get('drafting')

                                    if Draft.objects.filter(draft_code=existing_draft_code, draft_author=user): # If an existing draft is being posted

                                        draft = Draft.objects.get(draft_code=existing_draft_code, draft_author=user)

                                        draft.delete()

                                    if draft_type == 'DE':
                                        WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.DECLARE)
                                    elif draft_type == 'TH':
                                        WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.THEORISE)
                                    elif draft_type == 'QU':
                                        WatchlistActivity.objects.create(watchlist_activity_user=user, watchlist_activity_post=post, watchlist_activity_type=WatchlistActivity.ASK)

                                    subject = 'New Post!'
                                    message = f"Hey Aiden! Someone just posted something on bantopia!"
                                    email_from = settings.EMAIL_HOST_USER
                                    recipient_list = ['skrillfalconblast@icloud.com']
                                    send_mail(subject, message, email_from, recipient_list)

                                return redirect('/') # If something is posted, the user will always be redirected to the homepage.
                            else:
                                return render(request, 'post/write.html')
                        else:
                            return redirect('/')
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

                        return render(request, 'post/write.html')

            except:
                return render(request, 'post/write.html')

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
                return render(request, 'post/write.html')
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
            return render(request, 'post/posts.html')
        
        else:

            context = {'posts' : None}
            return render(request, 'post/posts.html', context)
        
    else:

        return redirect('/create-profile/')
    
# ------------------------------------------------

def commContext(request, post_code, post_slug):
    
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)

        tags = Tag.objects.filter(tag_post=post)

        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}

        user = request.user

        if user.is_authenticated:
            try:
                if post != Visit.objects.latest('visit_datetime').visit_post:

                    Visit.objects.create(visit_post=post, visit_user=user)
    
            except Visit.DoesNotExist:
                Visit.objects.create(visit_post=post, visit_user=user)
        
        context = {'post' : post, 'tags' : tags, 'y' : votes["y"], 'n' : votes["n"]}
        return render(request, 'comms/context.html', context)
    else:
        return redirect('/') # Make a 404 error page 
        

def commMastercases(request, post_code, post_slug):
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)

        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}

        user = request.user

        if user.is_authenticated:
            try:
                if post != Visit.objects.latest('visit_datetime').visit_post:

                    Visit.objects.create(visit_post=post, visit_user=user)
    
            except Visit.DoesNotExist:
                Visit.objects.create(visit_post=post, visit_user=user)

        context = {'post' : post, 'y' : votes["y"], 'n' : votes["n"]}
        return render(request, 'comms/cases.html', context)
    else:
        return redirect('/') # Make a 404 error page 

def commCounters(request, post_code, post_slug):
    if Post.objects.filter(post_code=post_code):
        
        post = Post.objects.get(post_code=post_code)

        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}
        
        user = request.user

        if user.is_authenticated:
            try:
                if post != Visit.objects.latest('visit_datetime').visit_post:

                    Visit.objects.create(visit_post=post, visit_user=user)
    
            except Visit.DoesNotExist:
                Visit.objects.create(visit_post=post, visit_user=user)

        counters = list(Message.objects.filter(message_post=post, message_score__gt=1).order_by('-message_score')[:5])

        quip_list = ['souls, apparently, liked this.', 'gentlemen found this appealing.', 
                 'losers felt good.', 'people were pleased.', 'old boys were chuffed.',
                 'gangstas approved.', 'cowboys were wrangled.', 'masters nodded their heads.',
                 'fathers weren\'t disappointed!', 'astronauts went over the moon.', 'dudez were pumped.',
                 'kids were hyped.', 'goblins were smitten.', 'sa faagaeetia alii.', 
                 'minds were stimulated.', 'buisnessmen profited.', 'dragons were fired up!',
                 'birds were eggcited!', 'cars went vroom vroom!', 'links were forged!', 'meows were meowed.',
                 'dogs barked!', 'sirens when whoop whoop!', 'dorks thought this was big brain', 'chimpanzees were fascinated.',
                 'dragons roared!!!', 'minorities felt empowered.', 'cheifs said how?', 'tiktok users doubletapped',
                 'frogs felt froggy.']
        
        quips = random.sample(quip_list, len(counters))

        counters_and_quips = zip(counters, quips)
        
        context = {'post' : post, 'counters' : counters_and_quips, 'y' : votes["y"], 'n' : votes["n"]}

        return render(request, 'comms/counters.html', context)
    else:
        return redirect('/') # Make a 404 error page 

def commDogs(request, post_code, post_slug):  
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)
       
        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}
        
        user = request.user

        if user.is_authenticated:
            try:
                if post != Visit.objects.latest('visit_datetime').visit_post:

                    Visit.objects.create(visit_post=post, visit_user=user)
    
            except Visit.DoesNotExist:
                Visit.objects.create(visit_post=post, visit_user=user)
                                
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
     
class PostAPI(APIView):

    def get(self, request):
        last_post = Post.objects.latest('post_datetime_created')
        serializer = PostSerializer(last_post)
        
        return Response(serializer.data, status=200)


################ ERROR PAGES #######################  

def csrf_failure(request, reason=""):
    quip_list = ['Call me crazy, but it looks like you have a werid looking csrf verification token. Do me a favour and <span>go back and try again</span>, to fix this digusting error.',
             'Your csrf verficiation token is super yucky, <span>go back and try again</span> to get a new one!',
             "WOAAAAAAHHHHH, I ain't never seen a csrf token looking like that! <span>Go back and try again</span> to heal my eyes!",
             "Your csrf verficaiton token is so ugly it crashed the server! <span>Go back and try again</span> for all our sakes.", 
             "I've seen some messed up things in my time, but that csrf verification token... *shudders* A sight like that could give a baby a beard. <span>Go back and try again</span>, because that's nasty!"]
    
    quip = random.choice(quip_list)

    context = {'quip' : quip}

    return render(request, 'errors/csrf_failure.html', context)