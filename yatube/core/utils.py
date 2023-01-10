from django.core.paginator import Paginator
from yatube.settings import POSTS_PER_PAGE


def paginator(obj_list,request):
    page_number = request.GET.get('page')
    return Paginator(obj_list, POSTS_PER_PAGE).get_page(page_number)
