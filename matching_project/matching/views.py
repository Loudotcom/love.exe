from multiprocessing import context
from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.contenttypes.models import ContentType
from .forms import CustomUserCreationForm, LoginForm, UserProfileForm, DealbreakerQuestionForm, DealbreakerAnswerForm
from .models import DealbreakerAnswer, DealbreakerQuestion, UserProfile, Hobby, LikeDislike, Message
from django.contrib.auth.decorators import login_required
from cities_light.models import City, Country
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse_lazy



def home(request):
    return render(request, 'home.html')


def register(request):

    try:
        if request.user.is_authenticated:
            return redirect('home')

        else:    
            if request.method == 'POST':
                form = CustomUserCreationForm(request.POST, request.FILES)
                if form.is_valid():
                    user = form.save()
                    auth.login(request, user)
                    return redirect('update-profile')
            else:
                form = CustomUserCreationForm()

    except Exception as e:
        print(str(e))
        return redirect('home')

    return render(request, 'registration/register.html', {'form': form})



def login(request):

    try:
        if request.user.is_authenticated:
            return redirect('home')
        
        else:

            form = LoginForm()

            if request.method == 'POST':
                form = LoginForm(request, data=request.POST)
                if form.is_valid():
                    username = request.POST.get('username')
                    password = request.POST.get('password')

                    user = authenticate(request, username=username, password=password)

                    if user is not None:
                        auth.login(request, user)
                        return redirect('profile')
                    else:
                        print("Invalid username or password.")
                else:
                    print(form.errors)

    except Exception as e:
        print(str(e))
        return redirect('home')

    return render(request, 'registration/login.html', {'form': form})


def logout(request):
    auth.logout(request)
    return redirect('home')


@login_required
def update_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST' and 'update_profile' in request.POST:
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    if request.method == 'POST' and 'add_question' in request.POST:
        question_form = DealbreakerQuestionForm(request.POST)
        if question_form.is_valid():
            new_question = question_form.save(commit=False)
            new_question.creator = request.user
            new_question.save()
            user_profile.questions.add(new_question)
            messages.success(request, f'Question "{new_question.text}" added successfully!')
            return redirect('update-profile')
        else:
            messages.error(request, 'There was an error adding your question. Please try again.')

    else:
        question_form = DealbreakerQuestionForm()

    if request.method == 'POST' and 'answer_question' in request.POST:
        answer_form = DealbreakerAnswerForm(request.POST)

        if answer_form.is_valid():
            question = DealbreakerQuestion.objects.get(id=request.POST['question'])
            answer = answer_form.save(commit=False)
            answer.user_profile = user_profile
            answer.question = question
            answer.save()
            messages.success(request, 'Your answer has been submitted successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'There was an error submitting your answer. Please try again.')

    else:
        answer_form = DealbreakerAnswerForm()

    cities = City.objects.all()
    countries = Country.objects.all()
    user_questions = DealbreakerQuestion.objects.filter(creator=request.user)
    dealbreaker_answers = DealbreakerAnswer.objects.filter(user_profile=user_profile)

    return render(request, 'profile/update-profile.html', {
        'form': form,
        'question_form': question_form,
        'answer_form': answer_form,
        'user_questions': user_questions,
        'dealbreaker_answers': dealbreaker_answers,
        'cities': cities,
        'countries': countries
    })


@login_required
def profile(request, user_id=None):
    if user_id:
        profile = get_object_or_404(UserProfile, id=user_id)
    else:
        profile = UserProfile.objects.get(user=request.user)

    hobbies = profile.hobbies.all()
    dealbreaker_questions = profile.questions.all()
    dealbreaker_answers = DealbreakerAnswer.objects.filter(user_profile=profile)

    context = {
        'profile': profile,
        'hobbies': hobbies,
        'dealbreaker_questions': dealbreaker_questions,
        'dealbreaker_answers': dealbreaker_answers,
    }

    return render(request, 'profile/profile.html', context)


@login_required
def matching_view(request):
    selected_hobbies = request.GET.getlist('hobbies')[:3]
    profiles = UserProfile.objects.exclude(user=request.user)

    if selected_hobbies:
        profiles = profiles.filter(hobbies__name__in=selected_hobbies).distinct()

    hobbies = Hobby.objects.all()
    content_type = ContentType.objects.get_for_model(UserProfile)

    return render(request, 'match/matching_list.html', {
        'profiles': profiles,
        'hobbies': hobbies,
        'selected_hobbies': selected_hobbies,
        'content_type': content_type
    })


@login_required
def get_dealbreaker_questions(request, profile_id):
    """Fetch dealbreaker questions for the selected profile."""
    profile = get_object_or_404(UserProfile, id=profile_id)
    questions = profile.questions.all().values('id', 'text', 'question_type')

    return JsonResponse({'questions': list(questions)})



@login_required
def answer_dealbreaker_questions(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id)
    questions = profile.questions.all() 
    stored_answers = DealbreakerAnswer.objects.filter(user_profile=profile)
    correct_answers = {answer.question.id: answer.answer_yn for answer in stored_answers}

    if request.method == "POST":
        user_answers = {
            int(q_id): request.POST.get(f"question_{q_id}") == "True"
            for q_id in correct_answers
        }

        all_answered_correctly = all(correct_answers[q_id] == user_answers[q_id] for q_id in correct_answers)

        if all_answered_correctly:
            profile_html = f"""
                <div class="profile-details" style="padding: 10px; border-radius: 8px; background-color: var(--soft-ivory); color: var(--elegant-wine); display: flex; flex-direction: row;">
                    <!-- Profile Image on the Left -->
                    <div class="profile-image" style="flex: 0 0 150px; margin-right: 20px; text-align: center;">
                        <img src="{profile.profile_picture.url if profile.profile_picture else '/static/default-profile.png'}" alt="Profile Picture" class="img-fluid" style="width: 150px; height: 150px; border-radius: 0;">
                    </div>
                    
                    <!-- Profile Info on the Right -->
                    <div class="profile-header" style="flex: 1; display: flex; justify-content: flex-start; flex-direction: column;">
                        <h4 style="color: var(--deep-rose); margin-bottom: 10px;">Profile Details</h4>
                        <p><strong>Bio:</strong> {profile.bio}</p>
                        <p><strong>Age:</strong> {profile.age}</p>
                        <p><strong>City:</strong> {profile.city.name}</p>
                        <p><strong>Country:</strong> {profile.country.name}</p>
                        <p><strong>Hobbies:</strong> {", ".join(hobby.name for hobby in profile.hobbies.all())}</p>
                    </div>
                </div>
            """
       
            like_count = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(UserProfile), object_id=profile.id, like=True).count()
            dislike_count = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(UserProfile), object_id=profile.id, like=False).count()

            return JsonResponse({
                'status': 'success',
                'html': profile_html,
                'like_count': like_count,
                'dislike_count': dislike_count
            })

        else:
            return JsonResponse({'status': 'error', 'message': "Sorry, this match is not for you."})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



@login_required
def message_detail(request, profile_id):
    other_user_profile = get_object_or_404(UserProfile, id=profile_id)
    other_user = other_user_profile.user
    messages = Message.objects.filter(
        sender=request.user, recipient=other_user
    ) | Message.objects.filter(
        sender=other_user, recipient=request.user
    ).order_by('sent_at')

    if request.method == 'POST':
        content = request.POST.get('content')

        if content:
            Message.objects.create(
                sender=request.user, recipient=other_user, content=content
            )
            return redirect('message_detail', profile_id=other_user_profile.id)


    return render(request, 'match/message_detail.html', {'messages': messages, 'other_user': other_user})



@login_required
def like_dislike(request):
    if request.method == 'POST':
        content_type_id = request.POST.get('content_type_id')
        object_id = request.POST.get('object_id')
        vote = request.POST.get('vote')

        content_type = get_object_or_404(ContentType, pk=content_type_id)
        user_to_like = get_object_or_404(UserProfile, pk=object_id) 

        try:
            like_dislike_obj = LikeDislike.objects.get(
                content_type=content_type, object_id=object_id, user=request.user
            )
            like_dislike_obj.like = (vote == 'like')
            like_dislike_obj.save()
        except LikeDislike.DoesNotExist:
            like_dislike_obj = LikeDislike.objects.create(
                content_type=content_type, object_id=object_id, user=request.user, like=(vote == 'like')
            )
            
        like_count = LikeDislike.objects.filter(content_type=content_type, object_id=object_id, like=True).count()
        dislike_count = LikeDislike.objects.filter(content_type=content_type, object_id=object_id, like=False).count()

        return JsonResponse({
            'status': 'success',
            'likes': like_count,
            'dislikes': dislike_count
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def liked_profiles(request):
    user = request.user
    content_type = ContentType.objects.get_for_model(UserProfile)
    liked_profiles = UserProfile.objects.filter(
        id__in=LikeDislike.objects.filter(user=user, like=True, content_type=content_type).values_list('object_id', flat=True)
    )
    matched_profiles = []
    for profile in liked_profiles:
        if LikeDislike.objects.filter(user=profile.user, object_id=user.profile.id, like=True, content_type=content_type).exists():
            matched_profiles.append(profile)

    return render(request, 'profile/liked_profiles.html', {
        'liked_profiles': liked_profiles,
        'matched_profiles': matched_profiles
    })