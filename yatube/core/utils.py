from django.core.paginator import Paginator
from yatube.settings import POSTS_PER_PAGE
from posts.models import Follow

def paginator(obj_list, request):
    page_number = request.GET.get('page')
    return Paginator(obj_list, POSTS_PER_PAGE).get_page(page_number)


def check_subscribed(user, author):
    """
    Если user подписан на author функция вернут True,
    в противном случае вернет False
    """
    try:
        folows = Follow.objects.get(user=user, author=author)
    except:
        folows = None   
    if isinstance(folows, Follow):
        return True
    else: False

def check_subscription_button(user, author):
    """
    Если user==author вернет Fales
    """
    if user == author:
        return False
    else:
        return True
