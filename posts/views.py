from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.views.decorators.csrf import csrf_exempt

from django.db.models import F, ExpressionWrapper, Value, FloatField, Case, When, IntegerField, Max, Subquery, OuterRef
from django.db.models.functions import Round, Log, Greatest, Abs

from django.utils.html import escape

from .models import Post, Tag, Vote, Draft, Visit
from chat.models import Message
from users.models import WatchlistActivity

import random


# Create your views here.

User = get_user_model()

def counterHack(posts):
    for post in posts:
        counters = list(Message.objects.filter(message_post=post, message_score__gt=1).values_list('message_content', flat=True).order_by('-message_score')[:5])

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

            ticker_texts = ["<span>Calm,</span> endless calm. <span>Broken</span>. The water's surface draws <span>near</span>. The <span>glass heaven</span> enveloping your form feels <span>large</span> under the surface. It’s <span>all</span>, it’s everything. But you were made to <span>breathe</span>. I need <span>air</span>. Oh, <span>we’re floating</span>, steadily towards the liquid veil. The <span>bubbles</span> look crystalline, playing with <span>the heavy light</span> as they hustle towards <span>the surface</span>. I’m moving up with <span>them</span>. Huh, <span>look at that</span>, I see something <span>behind the water</span>, something <span>above</span>, almost getting farther as I <span>draw closer</span>. I <span>tear</span> through that veil. Infinity <span>basks</span> before me. Sky, sun, trees, nature in all its glory, <span>light</span> as I have never seen before. A <span>black hawk</span> soars above, my head tracks its flight. <span>Let’s go.</span> ",
                            "<span>Bantopia</span> is literally the <span>coolest place</span> to be on <span>the Internet</span>. <span>Sure</span>, it’s a <span>bit crazy</span>, but <span>it’s pretty fun.</span> You see <span>this ticker</span>, it’s pretty cool. <span>But bro,</span> why in the world are you <span>staring</span> at it? If you’re <span>afk</span> I’ll understand, <span>but otherwise,</span> it’s kind of <span>weird</span>. Okay, <span>stop staring</span> at this point. <span>It’s rude</span>. Oh gosh, I probably <span>provoked</span> you to continue <span>looking at me.</span> In fact, <span>whatever</span>, I don’t have <span>anything to hide!</span> Keep <span>looking</span>, it’s your time that’s <span>being wasted</span>. Unlike you, <span>I have things to do</span> apart from staring at <span>randomly assigned</span> ticker text. Peace <span>out.</span>",
                            "You are likely on <span>bantopia.com</span>. This is likely the <span>gazillionth time</span> you’ve read this message. You are likely on the <span>New</span> tab. Your screen is mostly composed of the colors: <span>orange</span> and white. You probably like to <span>debate</span> or argue. You probably live in the northern <span>hemisphere</span>. You’re probably a cool <span>guy</span>. You’re likely about to enter a <span>chat</span>. You’re likely street <span>smart</span>. You likely prefer YouTube to other <span>social media.</span> This is likely the first time you’ve <span>read</span> this message. You’re likely predicting this <span>ticker</span> is going to end soon. You’re likely correct<span>.</span>",
                            "Don’t think, <span>act.</span> Just <span>do</span> it! <span>Think</span> with your mind, not your <span>brain</span>! Get into the <span>zone!</span> <span>Man up</span>! Listen to <span>your instincts!</span> Click the post! JUST CLICK THE POST <span>BRO!</span> It’s not even <span>hard!</span> Just make the <span>choice</span> and stick by it! Do <span>everything you can</span> to supplement your journey. <span>You know</span> your purpose, act now! You only <span>live once</span>! This is you’re <span>only shot</span> at greatness! CLICK THE POST! It’s all <span>background noise</span>! Don’t think, <span>act!</span> Click the <span>post!</span>",
                            "It started when an <span>alien device</span> did what it did. And <span>stuck itself</span> upon his wrist with <span>secrets</span> that it hid. Now he's got <span>super powers,</span> he's no ordinary kid, he’s <span>Ben 10</span>! So if you <span>see him,</span> you might be in for a <span>big surprise</span>. He'll turn <span>into an alien</span> before your very eyes. He's <span>slimy, creepy, fast and strong</span>, he's every <span>shape and size</span>, he's <span>Ben 10!</span> Armed with power, he's on the <span>case</span>. Fighting off evil from <span>Earth</span> or <span>space</span>. He'll <span>never stop</span> till he makes them <span>pay</span>. ‘Cause he's <span>the baddest kid</span> to ever save the day! <span>Ben 10!</span>",
                            "There is no one <span>righteous</span>, not even <span>one</span>; there is no one <span>who understands;</span> there is no one who <span>seeks God</span> <span>All have turned away</span>, they have together <span>become worthless;</span> there is <span>no one who does good</span>, not even <span>one</span>. Their throats are <span>open graves;</span> their tongues <span>practice deceit</span>. The <span>poison of vipers</span> is on their lips. Their mouths <span>are full of cursing</span> and bitterness. Their feet are swift to <span>shed blood;</span> ruin and misery <span>mark their ways,</span> and the way of peace <span>they do not know</span>. There is <span>no fear of God</span> before their eyes.",
                            "<span>In the beginning</span>, God created the <span>heavens</span> and the earth. The earth was <span>without form and void</span>, and <span>darkness</span> was over the face of the <span>deep</span>. And the <span>Spirit of God</span> was hovering over the face of <span>the waters.</span> And God said, “Let there be <span>light</span>,” and there was <span>light</span>. And God saw that the <span>light was good.</span> And God separated the <span>light</span> from the <span>darkness</span>. God called the <span>light Day,</span> and the <span>darkness</span> he called <span>Night</span>. And there was <span>evening</span> and there was <span>morning</span>, the first <span>day.</span>",
                            "<span>Stop</span> what you’re doing. I must tell you a <span>secret</span>. <span>Keep watching me.</span> I won’t be <span>here</span> for long. Keep <span>watching me</span>. Keep your eyes trained on <span>this ticker text.</span> THIS IS IMPORTANT. <span>Don't be scared.</span> AND NO MATTER WHAT YOU DO, <span>don’t look behind you.</span> Don’t look behind you. <span>Don’t look behind you.</span> Until this ticker text <span>passes by</span>, don’t look <span>directly</span> behind you. <span>Pay no attention</span> to your periphery. Just a <span>few more seconds,</span> and you will most likely <span>survive</span>. Hang in there.",
                            "Guess the <span>tune</span>: Da da da <span>da-da</span> da da da <span>da-da</span>, da da da <span>da-da</span> da da da <span>da-da</span>, da da da <span>da-da</span> da da da da <span>daaaaa</span> da da da <span>da-da</span> da da da <span>da-da</span> da da <span>daaaaaaaaaa</span> da da da <span>da-da</span> daaa daaa daaaa, daaa daaaa daaaa <span>da-da</span> da daaa daaaa. <span>One more time!</span>  Da da da <span>da-da</span> da da da <span>da-da</span>, da da da <span>da-da</span> da da da <span>da-da</span>, da da da <span>da-da</span> da da da da <span>daaaaa</span> da da da <span>da-da</span> da da da <span>da-da</span> da da <span>daaaaaaaaaa</span> da da da <span>da-da</span> daaa daaa daaaa, daaa daaaa daaaa <span>da-da</span> da daaa daaaa. Answer: <span>Super Smash Bros. Ultimate Main Theme</span>",
                            "Sorry to <span>break the news</span> but this post has <span>no counters</span>. Yeah, <span>most of the other</span> ticker texts aren’t as honest as <span>me</span>. You know what, <span>I don’t like those guys.</span> Most of them are <span>creepy</span>, especially <span>stop what you’re doing,</span> he’s a <span>loser.</span> I mean the Bible verse ticker texts are <span>chill</span> but most of the others are <span>mega dorks.</span> Such as the <span>probability text</span>, he’s a <span>nerd,</span> probably the exact opposite of the <span>Ben 10 Intro text</span>, who has the maturity of a <span>slingshot.</span> Tbh I like the <span>D&D</span> ticker text, he’s pretty <span>interesting</span>. Okay, I got to go <span>now! Get back to scrolling <span>bantopia.com!</span>"]
            
            post.ticker_text = random.choice(ticker_texts)
        

    return posts

def sort_trending():
    #posts = Post.objects.annotate(score=ExpressionWrapper(
        #Round((F('post_timestamp_created') / 45000) + Log(10, Greatest(F('post_number_of_messages'), 1)), precision=7), output_field=FloatField()
        #), sort=Value("trending")).order_by('-score')[:100]
    
    posts = Post.objects.alias(
        latest_message=Max('message__message_datetime_sent'), 
    ).annotate(last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values('message_content')[:1])).order_by('-latest_message')

    counterHack(posts)

    return posts
        
def sort_controversial():
    posts = Post.objects.annotate(total=ExpressionWrapper(Abs(F('post_number_of_yes_votes') + F('post_number_of_no_votes')), IntegerField()), score=Case(When(total=0, then=Value(0, output_field=FloatField())), default=ExpressionWrapper(
        (F('post_timestamp_created') / 45000) + Log(10, (F('total')) / Greatest(Abs(F('post_number_of_yes_votes') - F('post_number_of_no_votes')), 1)), output_field=FloatField()
    )), sort=Value("controversial"), 
    last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values('message_content')[:1])).order_by('-score')[:100] 

    counterHack(posts)
    
    return posts

def search(search_term):
    posts = Post.objects.annotate(rank=SearchRank(SearchVector('post_title'), SearchQuery(search_term)), 
                                  last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values('message_content')[:1])
                                  ).order_by('-rank')[:100]

    counterHack(posts)

    return posts

@csrf_exempt
def index(request):

    tab_texts = ["There's no place...",
                "HomePage",
                "Scrolling?",
                "HomeBase",
                "Welcome to",
                "HomePage",
                "Central Nexus",
                "Scrolling?",
                "How are you?", 
                "Looking for trouble?",
                "On the hunt?",
                ]
    
    tab_text = random.choice(tab_texts)

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

                posts = Post.objects.annotate(last_message=Subquery(Message.objects.filter(message_post=OuterRef('pk')).order_by("-message_datetime_sent").values('message_content')[:1])).order_by('-post_datetime_created')
                    
                counterHack(posts)

                #posts = Post.objects.annotate(counters=ArrayAgg('message__message_content', filter=Q(message__message_score__gt=-1), ordering='-message__message_score')).order_by('-post_datetime_created')

        else:
            posts = Post.objects.order_by('-post_datetime_created')

            counterHack(posts)

        user = request.user # Pulls user from request for authentication checks within the template.   
        
        watching = user.watching.all()
        
        watchlist_activity = WatchlistActivity.objects.filter(watchlist_activity_user__in=watching).select_related('watchlist_activity_user', 'watchlist_activity_post').order_by('-watchlist_activity_datetime')

        #watchlist_activity = WatchlistActivity.objects.filter(watchlist_activity_user__in=watching).order_by('-watchlist_activity_datetime')

        visits = Visit.objects.filter(visit_user=user).select_related('visit_post').order_by('-visit_datetime')

        context = {'posts' : posts, 'user' : user, 'watchlist_activity' : watchlist_activity, 'visits' : visits, 'tab_text' : tab_text}

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

        context = {'posts' : posts, 'tab_text' : tab_text}

        return render(request, 'index.html', context)


def write(request):

    tab_texts = ["Feeling Dangerous?",
            "Post Something",
            "Masterpiece Maker",
            "Feeling Opinionated?",
            "Start trouble?",
            "What's on your mind?",
            "Post something?",
            "Post something?",
            ]
    
    tab_text = random.choice(tab_texts)

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
                        return render(request, 'post/write.html', {'tab_text' : tab_text})
                
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

                        return render(request, '/post/write.html', {'tab_text' : tab_text})

            except:
                return render(request, '/post/write.html', {'tab_text' : tab_text})

        else: # If the page is simply loading, without a POST request

            if request.method == 'GET': # If there is a URL query

                draft_code = request.GET.get('drafting')

                if Draft.objects.filter(draft_code=draft_code, draft_author=request.user): # If the queried draft exists

                    draft = Draft.objects.get(draft_code=draft_code, draft_author=request.user)

                    context = {'draft' : draft, 'tab_text' : tab_text}
                    
                    return render(request, 'post/write.html', context)
                else: # If the method is recognised as GET but the queried draft doesn't exist
                    return render(request, 'post/write.html', {'tab_text' : tab_text})
            
            else: # If the page is simply loading without any query
                return render(request, '/post/write.html', {'tab_text' : tab_text})
    return redirect('/create-profile/')
             

def drafts(request):
    user = request.user

    if user.is_authenticated:
        tab_texts = [
            "Your Drafts",
            "Draftin'",
            "DraftCraft",
            "Just Drafts",
            "Looking for Drafts?",
        ]
    
        tab_text = random.choice(tab_texts)

        drafts = Draft.objects.filter(draft_author=user)

        context = {'drafts' : drafts, 'tab_text' : tab_text}

        return render(request, 'post/drafts.html', context)
    else:
        return redirect('/create-profile/')

def posts(request):
    if request.user.is_authenticated:
        tab_texts = [
            "Your Posts",
            "Beautiful, huh?",
            "All yours...",
            "Your Posts",
            "Previous Posts",
            "Previous Posts?",
            "Sheeeeeesh",
            "0_0"
        ]
    
        tab_text = random.choice(tab_texts)

        if Post.objects.filter(post_author=request.user):
            context = {'posts' : Post.objects.filter(post_author=request.user), 'tab_text' : tab_text}
            return render(request, 'post/posts.html', context)
        else:
            context = {'posts' : None, 'tab_text' : tab_text}
            return render(request, 'post/posts.html', context)
    else:
        return redirect('/create-profile/')
    
# ------------------------------------------------

def commContent(request, post_code, post_slug):
    
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
        

def commMastercases(request, post_code, post_slug):
    if Post.objects.filter(post_code=post_code):

        post = Post.objects.get(post_code=post_code)
       
        votes = {'y' : Vote.objects.filter(vote_post=post, vote_type=True).count(),
                 'n' : Vote.objects.filter(vote_post=post, vote_type=False).count()}

        context = {'post' : post, 'y' : votes["y"], 'n' : votes["n"]}
        return render(request, 'comms/cases.html', context)
    else:
        return redirect('/') # Make a 404 error page 

def commCounters(request, post_code, post_slug):
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

def commDogs(request, post_code, post_slug):  
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
    quip_list = ['Call me crazy, but it looks like you have a werid looking csrf verification token. Do me a favour and <span>go back and try again</span>, to fix this digusting error.',
             'Your csrf verficiation token is super yucky, <span>go back and try again</span> to get a new one!',
             "WOAAAAAAHHHHH, I ain't never seen a csrf token looking like that! <span>Go back and try again</span> to heal my eyes!",
             "Your csrf verficaiton token is so ugly it crashed the server! <span>Go back and try again</span> for all our sakes.", 
             "I've seen some messed up things in my time, but that csrf verification token... *shudders* A sight like that could give a baby a beard. <span>Go back and try again</span>, because that's nasty!"]
    
    quip = random.choice(quip_list)

    context = {'quip' : quip}

    return render(request, 'errors/csrf_failure.html', context)