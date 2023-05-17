from random import choice

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .filters import AdvFilter
from .models import Advertisement, AdFiles, Profile, OneTimeCode, Reply
from .forms import ReplyForm, RegistrationForm, AdvForm, AdFilesFormset


# Create your views here.
def get_user_info_for_right_bar(user):
    user_context = {}
    user_context['username'] = user.username if user.username else user.email
    user_context['email_not_confirmed'] = user.email_confirmed
    return user_context


def add_value_photo_or_video(file):
    photos = ['jpg', 'jpeg', 'png', 'ico', 'gif', 'tiff', 'webp', 'eps', 'svg']
    videos = ['mp4', 'mov', 'wmv', 'avi', 'avchd', 'flv', 'f4v', 'swf', 'mkv']
    format = str(file.file).split('.')[-1].lower()
    if format in photos:
        file.photo = True
    elif format in videos:
        file.video = True
    return file


def get_title_href(ad):
    images = AdFiles.objects.filter(ad=ad)
    if images:
        title = choice(images)
        return str(title.file)


class AdvList(ListView):
    model = Advertisement
    template_name = 'AdvList.html'
    context_object_name = 'AdvList'
    queryset = Advertisement.objects.order_by('-id')

    def get_queryset(self):
        queryset = super().get_queryset()
        return AdvFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = AdvFilter(self.request.GET, queryset=self.get_queryset())
        for ad in self.object_list:
            ad.title_img = get_title_href(ad)

        if self.request.user.is_authenticated:
            context['user_context'] = get_user_info_for_right_bar(self.request.user)
        return context


class AdvDetail(LoginRequiredMixin, DetailView):
    model = Advertisement
    template_name = 'AdvDetails.html'
    context_object_name = 'adv'

    def get_reply_form(self):
        reply_form = ReplyForm()
        user = self.request.user
        ad = self.object
        reply_form.initial = {'ad': ad, 'user': user}
        return reply_form

    def get_context_data(self, **kwargs):
        context = super(AdvDetail, self).get_context_data(**kwargs)
        files = AdFiles.objects.filter(ad=kwargs['object'])
        for file in files:
            file = add_value_photo_or_video(file)
        context['files'] = files
        context['form'] = self.get_reply_form()

        if self.request.user.is_authenticated:
            context['user_context'] = get_user_info_for_right_bar(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        redirect_from = request.META['HTTP_REFERER']
        form = ReplyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(redirect_from)


class AdvCreate(LoginRequiredMixin, CreateView):
    template_name = 'AdvCreate.html'
    form_class = AdvForm
    model = Advertisement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'].initial = {'user': self.request.user}
        if self.request.POST:
            context['form'] = AdvForm(self.request.POST)
            context['formset'] = AdFilesFormset(self.request.POST, self.request.FILES, instance=context['form'].instance)
        else:
            context['formset'] = AdFilesFormset()

        if self.request.user.is_authenticated:
            context['user_context'] = get_user_info_for_right_bar(self.request.user)
        return context

    def post(self, request):
        super(AdvCreate, self).post(request)
        return redirect('/')

    def form_valid(self, form):
        formset = AdFilesFormset(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            ad = form.save()
            files = self.request.FILES.getlist("adfiles_set-0-file")
            for file in files:
                AdFiles.objects.create(ad=ad, file=file)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AdvUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'AdvEdit.html'
    form_class = AdvForm

    def get_object(self, **kwargs):
        user = self.request.user
        id = self.kwargs.get('pk')
        return get_object_or_404(Advertisement, id=id, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files = AdFiles.objects.filter(ad=self.kwargs.get('pk'))
        for file in files:
            file = add_value_photo_or_video(file)
        context['files'] = files

        if self.request.POST:
            context['form'] = AdvForm(self.request.POST)
            context['formset'] = AdFilesFormset(self.request.POST, self.request.FILES, instance=context['form'].instance)
        else:
            context['formset'] = AdFilesFormset()

        if self.request.user.is_authenticated:
            context['user_context'] = get_user_info_for_right_bar(self.request.user)
        return context

    def post(self, request, pk):
        super(AdvUpdate, self).post(request)
        return redirect(request.environ['HTTP_REFERER'])

    def form_valid(self, form):
        formset = AdFilesFormset(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            ad = form.save()
            files = self.request.FILES.getlist("adfiles_set-0-file")
            for file in files:
                AdFiles.objects.create(ad=ad, file=file)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AdvDelete(DeleteView):
    template_name = 'AdvDelete.html'
    queryset = Advertisement.objects.all()
    success_url = '/'
    context_object_name = 'adv'

    def get_object(self, **kwargs):
        user = self.request.user
        id = self.kwargs.get('pk')
        return get_object_or_404(Advertisement, id=id, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files = AdFiles.objects.filter(ad=kwargs['object'])
        for file in files:
            file = add_value_photo_or_video(file)
        context['files'] = files
        if self.request.user.is_authenticated:
            context['user_context'] = get_user_info_for_right_bar(self.request.user)
        return context


class UserAdvReplys(LoginRequiredMixin, ListView):
    model = Advertisement
    template_name = 'userAdvReplys.html'
    context_object_name = 'advSearch'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(user=user).order_by('-id')
        return AdvFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_context'] = get_user_info_for_right_bar(self.request.user)
        context['filter'] = AdvFilter(self.request.GET, queryset=self.get_queryset())

        objects = context['object_list']
        for ad in objects:
            ad.title_img = get_title_href(ad)
            ad.replies = Reply.objects.filter(ad=ad)
        context['object_list'] = objects
        return context


class RegistrationView(CreateView):
    model = Profile
    form_class = RegistrationForm
    success_url = '/'
    template_name = 'account/signup.html'

    def post(self, request):
        super(RegistrationView, self).post(request)
        login_username = request.POST['username']
        login_password = request.POST['password1']
        created_user = authenticate(username=login_username, password=login_password)
        if created_user:
            login(request, created_user)
            return redirect('/')
        else:
            messages.error(request, 'регистрация не удалась. Пользователь с таким именем или электронной почтой существует')
            return redirect('/signup')


def confirm_emal(request):
    if request.method != 'POST':
        return render(request, 'account/ConfirmEmail.html')
    username = str(request.user)
    code = int(request.POST['code'])
    if OneTimeCode.objects.filter(code=code, user__username=username).exists():
        user = Profile.objects.get(username=username)
        user.email_confirmed = True
        user.save()
        return redirect('/')
    else:
        return render(request, 'account/ConfirmEmail.html', {'confirmError': 'не удалось подтвердить адрес электронной почты. Войдите на сайт под логином и паролем, указанным при регистрации, затем снова перейдите по ссылке и ведите указанный в письме код'})


def delete_file(request, pk):
    file = get_object_or_404(AdFiles, pk=pk)
    if file.ad.user == request.user:
        file.delete()
    return redirect(request.environ['HTTP_REFERER'])


def reply_accept(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if reply.ad.user == request.user:
        reply.accepted = 1
        reply.save()
    return redirect(request.environ['HTTP_REFERER'])


def reply_deny(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if reply.ad.user == request.user:
        reply.accepted = -1
        reply.save()
    return redirect(request.environ['HTTP_REFERER'])