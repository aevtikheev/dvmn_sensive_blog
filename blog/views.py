from django.shortcuts import render, get_object_or_404

from blog.models import Comment, Post, Tag

MOST_POPULAR_POSTS_COUNT = 5
MOST_FRESH_POSTS_COUNT = 5
MOST_POPULAR_TAGS_COUNT = 5
RELATED_POSTS_COUNT = 20


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount":  post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags_with_posts],
        'first_tag_title': post.tags_with_posts[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    most_popular_posts = (
        Post.objects
            .popular()[:MOST_POPULAR_POSTS_COUNT]
            .prefetch_related('author')
            .fetch_with_tags_posts()
            .fetch_with_comments_count()
    )
    most_fresh_posts = (
        Post.objects
            .order_by('-published_at')[:MOST_FRESH_POSTS_COUNT]
            .prefetch_related('author')
            .fetch_with_tags_posts()
            .fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:MOST_POPULAR_TAGS_COUNT]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related('author'), slug=slug)
    comments = Comment.objects.select_related('author').filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.fetch_with_posts_count()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': likes.count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:MOST_POPULAR_TAGS_COUNT]

    most_popular_posts = (
        Post.objects
            .popular()[:MOST_POPULAR_POSTS_COUNT]
            .prefetch_related('author')
            .fetch_with_tags_posts()
            .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)
    most_popular_tags = Tag.objects.popular()[:MOST_POPULAR_TAGS_COUNT]

    most_popular_posts = (
        Post.objects
            .popular()[:MOST_POPULAR_POSTS_COUNT]
            .prefetch_related('author')
            .fetch_with_tags_posts()
            .fetch_with_comments_count()
    )

    related_posts = (
        tag.posts
        .all()[:RELATED_POSTS_COUNT]
        .prefetch_related('author')
        .fetch_with_tags_posts()
        .fetch_with_comments_count()
    )

    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
