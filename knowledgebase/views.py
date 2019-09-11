import base64
from datetime import *
from django.shortcuts import render, redirect, get_object_or_404
from knowledgebase.models import *
from django.http import HttpResponse
from django.template import loader
from knowledgebase.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
#from django.conf import settings
from django.urls import *
from .pylib import Sidebar

from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash

def signup(request):
    from django import forms
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('space_view')
    else:
        form = SignupForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required(redirect_field_name = 'redirect_to', login_url=reverse_lazy('login'))
def user_profile(request):
    user = User.objects.get(username=request.user)
    user_ext = UserExtended.objects.get(user=request.user.id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user) #initial=post.__dict__,
        form_ext = ProfileExtendedForm(request.POST, instance=user_ext)
        if form.is_valid() and form_ext.is_valid():
            if form.has_changed():
                if form.cleaned_data['password2']:
                    user.set_password(form.cleaned_data['password2'])
                    update_session_auth_hash(request, user)
                form.save()
            if form_ext.has_changed() or request.FILES:
                if request.FILES:
                    avatar = request.FILES.get('user_avatar').file.read()
                    user_ext.user_avatar = base64.b64encode(avatar).decode('UTF-8')
                form_ext.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
        form_ext = ProfileExtendedForm(instance=user_ext)
        
    activity = Activity.objects.filter(activity_creator=request.user).order_by('-activity_created')
    template = loader.get_template('knowledgebase/user_profile.html')
    context = {
        'form':form,
        'form_ext':form_ext,
        'avatar': user_ext.user_avatar,
        'activity':activity,
    }
    return HttpResponse(template.render(context, request))

#PAGES FUNCTIONS
#TODO: restrict view deleted pages
@login_required(redirect_field_name = 'redirect_to', login_url=reverse_lazy('login'))
def page_view(request, space_id, page_id=None):
    sidebar = Page.objects.filter(
        page_parent_id__isnull=False).filter(
        space_id__isnull=False).filter(
        page_type = 'PAGE').order_by(
        'page_title'
    )
    spaces_list = Space.objects.all()
    space = Space.objects.get(pk=space_id)
    if not page_id:
        page = space.space_home_id
    else:
        page = get_object_or_404(Page, pk=page_id, space_id_id = space_id)

    existed_activity = Activity.objects.filter(
        activity_page=page, activity_creator=request.user
    ).order_by('activity_created')

    time_diff = timedelta(days=2)
    if existed_activity:
        existed_activity = existed_activity[0]
        time_diff = datetime.now() - existed_activity.activity_created
    if time_diff > timedelta(days=1):
#        existed_activity.activity_type='VIEWED'
#        existed_activity.activity_created = datetime.now()
#        existed_activity.save()
#    else:
        Activity(
            activity_relation='PAGE',
            activity_type='VIEWED',
            activity_page=page,
            activity_creator=request.user,
            activity_created = datetime.now()
        ).save()
    
    template = loader.get_template('knowledgebase/page_view.html')
    sb = Sidebar(sidebar, 'page_view')
    context = {
        'sidebar':sb.mksidebar(page.id, 0),
        'spaces_list':spaces_list,
        'space':space,
        'page': page,
    }
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name = 'redirect_to', login_url=reverse_lazy('login'))
def page_edit(request, space_id, page_id, action=None):
    #Actions: 1:new page, 2:delete page, 3:draft
    import copy
    if action: action = int(action)
        
    activity = Activity(
        activity_relation='PAGE',
        activity_creator=request.user,
        activity_created = datetime.now()
    )

    if not action or action == 3:
        page = get_object_or_404(Page, pk=page_id, space_id_id = space_id)
        prev_page = copy.deepcopy(page)
        prev_page.pk = prev_page.page_parent_id_id = None
    else:
        if action == 2:
            page = get_object_or_404(Page, pk=page_id, space_id_id = space_id)
            page.page_type = 'DELETED'
            page.save()
            
            activity.activity_page=page
            activity.activity_type ='DELETED'
            activity.save()
            
            return redirect('page_view', space_id=space_id)
        else:
            page = None

    draft = Page.objects.filter(
        page_type='DRAFT').filter(
        space_id=space_id).filter(
        draft_parent_id_id=page_id
    )
    if draft:
        draft = draft[0]
        if action == 3:
            page.page_content = draft.page_content
            draft.restore = True
        else:
            draft.restore = False

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            post_action = request.POST.get('draft')
            page = form.save(commit=False)
            
            if not action and not post_action:
                page.page_version += 1
                page.page_modifier = request.user
                prev_page.save()
                
                activity.activity_type ='EDITED'
            elif action == 1:
                page.page_type = 'PAGE'
                page.page_parent_id_id = page_id
                page.space_id_id = space_id
                page.page_creator = page.page_modifier = request.user
                page.page_created = page.page_updated = datetime.now()
                
                activity.activity_type ='CREATED'
            if post_action:
                if action == 1:
                    page.save()
                    page.draft_parent_id_id = page_id = page.pk
                    page.pk = None
                else:
                    page.draft_parent_id_id = page_id
                    if draft:
                        page.pk = draft.pk
                    else:
                        page.pk = None
                page.page_type = 'DRAFT'
                page.page_modifier = request.user
                
            page.save()
            
            activity.activity_page = page
            activity.save()

            if not post_action and draft: draft.delete()
            
            if post_action:
                return redirect('page_edit', space_id=space_id, page_id=page_id, action=3)
            return redirect('page_view', space_id=space_id, page_id=page.pk)
    else:
        form = PageForm(instance=page)
    
    if not page:
        page = {'id':page_id,'space_id_id':space_id}

    template = loader.get_template('knowledgebase/page_edit.html')
    context = {
        'form': form,
        'page': page,
        'draft': draft,
    }
    return HttpResponse(template.render(context, request))

#SPACES FUNCTIONS
@login_required(redirect_field_name = 'redirect_to', login_url=reverse_lazy('login'))
def space_view(request):
    space_ls = Space.objects.all()
    template = loader.get_template('knowledgebase/space_view.html')
    context = {
        'spaces':space_ls,
    }
    return HttpResponse(template.render(context, request))
    
def space_edit(request, space_id, action=None):
    if not action:
        post = get_object_or_404(Space, pk=space_id)
    else:
        if action == '2':
            space = Space.objects.get(pk=space_id)
            space_home_id = space.space_home_id_id
            space.delete()
            Page.objects.get(pk=space_home_id).delete()
            return redirect('space_view')
        else:
            post = None
    if request.method == 'POST':
        form = SpaceForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if action == '1':
                home_page = Page()
                home_page.page_version = 1
                home_page.page_title = post.space_title
                home_page.page_content = post.space_description
                home_page.save()

                post.space_home_id_id = home_page.id
                post.save()

                home_page.space_id_id = post.space_id
                home_page.save()

            post.save()
            return redirect('space_view')
    else:
        form = SpaceForm(instance=post)
    template = loader.get_template('knowledgebase/space_edit.html')
    context = {
        'form': form,
        'space': post,
    }
    return HttpResponse(template.render(context, request))
