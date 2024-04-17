from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProtablePagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'current'
    page_size_query_param = 'pageSize'
    # max_page_size = 50
    default_ordering = '-id'

    def paginate_queryset(self, queryset, request, view=None):
        if not queryset.ordered:
            try:
                queryset = queryset.order_by(self.default_ordering)
            except:
                pass
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'data': data,
        })

