from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import JsonResponse
from .models import LikeDislike
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .forms import CustomUserCreationForm, UserProfileForm, DealbreakerQuestionForm, DealbreakerAnswerForm
from .models import DealbreakerAnswer, DealbreakerQuestion, UserProfile
from django.contrib.auth.decorators import login_required


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
            return redirect('update-profile')
    else:
        form = UserProfileForm(instance=user_profile)

    if request.method == 'POST' and 'add_question' in request.POST:
        question_form = DealbreakerQuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.creator = request.user
            question.save()
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
    user_questions = DealbreakerQuestion.objects.filter(creator=request.user)
    dealbreaker_answers = DealbreakerAnswer.objects.filter(user_profile=user_profile)

    return render(request, 'profile/update-profile.html', {
        'form': form,
        'question_form': question_form,
        'answer_form': answer_form,
        'user_questions': user_questions,
        'dealbreaker_answers': dealbreaker_answers
    })


@login_required
def profile(request):
     
    profile = UserProfile.objects.get(user=request.user)


    context = {

        'profile': profile,
    }

    return render(request, 'profile/profile.html', context)



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
        except LikeDislike.DoesNotExist:
            like_dislike_obj = LikeDislike.objects.create(
                content_type=content_type, object_id=object_id, user=request.user, like=(vote == 'like') if vote in ('like', 'dislike') else None
            )

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})