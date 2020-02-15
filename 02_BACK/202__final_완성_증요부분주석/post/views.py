import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import PostForm, CommentForm

from .models import Post, Like, Comment,Tag
from django.db.models import Count

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()
    
    return render(request, 'post/post_detail.html', {
        'comment_form': comment_form,
        'post': post,
    })
    
@login_required
def my_post_list(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    user_profile = user.profile
    
    target_user = get_user_model().objects.filter(id=user.id).select_related('profile') \
        .prefetch_related('profile__follower_user__from_user', 'profile__follow_user__to_user')
    # select_related : foreign-key, 일대일의 관계, prefetch_related : foreign-key, 다대다, 일대다
    post_list = user.post_set.all()
    
    all_post_list = Post.objects.all()
    
    return render(request, 'post/my_post_list.html', {
        'user_profile': user_profile,
        'target_user': target_user,
        'post_list': post_list,
        'all_post_list': all_post_list,
        'username': username,
    })

def post_list(request, tag=None):
    tag_all = Tag.objects.annotate(num_post=Count('post')).order_by('-num_post')
    
    if tag:
        post_list = Post.objects.filter(tag_set__name__iexact=tag) \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')
    else:
        post_list = Post.objects.all() \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')

    comment_form = CommentForm()
    
    paginator = Paginator(post_list, 3)
    page_num = request.POST.get('page')
    
    # 첫번째 페이지라면 page를 1로 한다
    # page가 가능한 범위를 넘어서면 가장 마지막 페이지를 보여준다
    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # ajax로 요청이 들어왔다면 post_list_ajax.hml파일로 posts, comment_form을 보내서 처리한다
    if request.is_ajax():
        return render(request, 'post/post_list_ajax.html', {
            'posts': posts,
            'comment_form': comment_form,
        })
    # isalnum 알파벳으로만과 숫자로만 되어있는지 확인 ( 문자열인지 체크 )
    # join을 이용해서 태그를 합치고
    # 검색을 처리할 post_search로 보낸다
    if request.method == 'POST':
        tag = request.POST.get('tag')
        tag_clean = ''.join(e for e in tag if e.isalnum())
        return redirect('post:post_search', tag_clean)
    
    # 현재 접속한 유저가 로그인한 상태라면 처리할 내용
    if request.user.is_authenticated:
        # 현재 접속한 유저를 확인
        username = request.user
        user = get_object_or_404(get_user_model(), username=username)
        user_profile = user.profile
        follow_set = request.user.profile.get_following
        follow_post_list = Post.objects.filter(author__profile__in=follow_set)
        
        return render(request, 'post/post_list.html', {
            'user_profile': user_profile,
            'tag': tag,
            'posts': posts,
            'follow_post_list': follow_post_list,
            'comment_form': comment_form,
            'tag_all': tag_all,
        })
    else:
        return render(request, 'post/post_list.html', {
            'tag': tag,
            'posts': posts,
            'comment_form': comment_form,
            'tag_all': tag_all,
        })
    
# 새글작성
@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # commit=False 함수 호출을 지연시켜서 중복 저장을 막는다
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # tag_save models단에서 처리되는 태그저장
            post.tag_save() 
            messages.info(request, '새 글이 등록되었습니다')
            return redirect('post:post_list')
    else:
        form = PostForm()
    return render(request, 'post/post_new.html', {
        'form': form,
    })

# 글 수정
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.warning(request, '잘못된 접근입니다')
        return redirect('post:post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            post.tag_set.clear()
            post.tag_save()
            messages.success(request, '수정완료')
            return redirect('post:post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'post/post_edit.html', {
        'post': post,
        'form': form,
    })

# 좋아요
@login_required
@require_POST
def post_like(request):
    pk = request.POST.get('pk', None)
    # get_object_or_404 함수는 Django 모델을 첫번째 인자로 받고, 몇개의 키워드 인수를 모델 관리자의 get() 함수에 넘깁니다. 만약 객체가 존재하지 않을 경우, Http404 예외가 발생합니다.
    post = get_object_or_404(Post, pk=pk)
    # get_or_create 튜플형식으로 반환을 한다 True, false에 따라서 스위치처럼 작동
    post_like, post_like_created = post.like_set.get_or_create(user=request.user)

    if not post_like_created:
        post_like.delete()
        message = "좋아요 취소"
    else:
        message = "좋아요"

    context = {'like_count': post.like_count,
               'message': message}

    return HttpResponse(json.dumps(context), content_type="application/json")



@login_required
@require_POST
def post_bookmark(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_bookmark, post_bookmark_created = post.bookmark_set.get_or_create(user=request.user)

    if not post_bookmark_created:
        post_bookmark.delete()
        message = "북마크 취소"
    else:
        message = "북마크"

    context = {'bookmark_count': post.bookmark_count,
               'message': message}

    return HttpResponse(json.dumps(context), content_type="application/json")    
    
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user or request.method == 'GET':
        messages.warning(request, '잘못된 접근입니다.')
        return redirect('post:post_list')

    if request.method == 'POST':
        post.delete()
        # messages.success(request, '삭제완료')
        return redirect('post:post_list')

@login_required
def comment_new(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return render(request, 'post/comment_new_ajax.html', {
                'comment': comment,   
            })
    return redirect("post:post_list")


@login_required
def comment_new_detail(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return render(request, 'post/comment_new_detail_ajax.html', {
                'comment': comment,
            })


@login_required
def comment_delete(request):
    pk = request.POST.get('pk')
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST' and request.user == comment.author:
        comment.delete()
        message = '삭제완료'
        status = 1
    
    else:
        message = '잘못된 접근입니다'
        status = 0
        
    return HttpResponse(json.dumps({'message': message, 'status': status, }), content_type="application/json")