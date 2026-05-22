from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination that allows client to set page_size via query param."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
