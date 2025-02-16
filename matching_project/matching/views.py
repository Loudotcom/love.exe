from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .forms import CustomUserCreationForm, UserProfileForm, DealbreakerQuestionForm, DealbreakerAnswerForm
from .models import DealbreakerAnswer, DealbreakerQuestion, UserProfile, Hobby, LikeDislike
from django.contrib.auth.decorators import login_required
from cities_light.models import City, Country
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse_lazy



def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('update-profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


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
            print(f"Question added: {new_question.text}")
            return redirect('update-profile')
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
            return redirect('update-profile')
    else:
        answer_form = DealbreakerAnswerForm()

    cities = City.objects.all()
    countries = Country.objects.all()
    user_questions = DealbreakerQuestion.objects.filter(creator=request.user)
    dealbreaker_answers = DealbreakerAnswer.objects.filter(user_profile=user_profile)

    print(f"User's questions: {user_questions}")
    print(f"User's answers: {dealbreaker_answers}")

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

            return render(request, 'profile/profile_detail.html', {
                'profile': profile,
                'dealbreaker_questions': questions,
                'all_answered_correctly': True
            })
        else:
            return render(request, 'match/answer_questions.html', {
                'dealbreaker_questions': questions,
                'error_message': "Some answers are incorrect."
            })
    
    return render(request, 'match/answer_questions.html', {
        'dealbreaker_questions': questions
    })



def login(request):

    return render(request, 'registration/login.html')



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