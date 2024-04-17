import uuid
import datetime

from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class ProtableFilterBackend(BaseFilterBackend):
    """
    自定义过滤器，可适配前端ProTable组件

    支持：
        - sort
        - filter
        - search
        - globalSearch
    """

    def filter_queryset(self, request, queryset, view):

        # params = request.query_params  # GET
        params = request.data            # POST

        # 处理sort参数
        sort_param = params.get('sort')
        if sort_param:
            queryset = self.apply_sorting(queryset, sort_param)

        filter_param = params.get('filter')
        if filter_param:
            queryset = self.apply_filtering(queryset, filter_param)

        # 处理search参数
        search_param = params.get('search')
        if search_param:
            fuzzy_search = params.get('fuzzy_search')
            queryset = self.apply_search(queryset, search_param, fuzzy_search)

        # 处理globalSearch参数
        global_search_param = params.get('globalSearch')
        global_search_fields = getattr(view, 'global_search_fields', [])
        if global_search_param and global_search_fields:
            queryset = self.apply_global_search(queryset, global_search_param, global_search_fields)

        return queryset

    def apply_sorting(self, queryset, sort_param):
        order_list = []
        for field, order in sort_param.items():
            order = '-' if order == 'descend' else ''
            order_list.append(f'{order}{field}')
        return queryset.order_by(*order_list)

    def apply_filtering(self, queryset, filter_param):
        for field, values in filter_param.items():
            queryset = queryset.filter(**{f'{field}__in': values})
        return queryset
    
    def apply_global_search(self, queryset, global_search_param, global_search_fields):
        query = Q()
        for field in global_search_fields:
            query |= Q(**{f'{field}__icontains': global_search_param})
        return queryset.filter(query)

    def apply_search(self, queryset, search_param, fuzzy_search):
        for field, values in search_param.items():
            # 列表过滤
            if isinstance(values, list):
                lookup = f'{field}__in'
                queryset = queryset.filter(**{lookup: values})
            # 数值过滤
            elif isinstance(values, int) or isinstance(values, float):
                lookup = field
                queryset = queryset.filter(**{lookup: values})
            # 文本过滤，支持模糊检索和完全匹配检索(exact忽略大小写)
            elif isinstance(values, str):
                try:
                    uuid.UUID(values)
                    lookup = field
                except:
                    lookup = f'{field}__icontains' if fuzzy_search else f'{field}__exact'
                queryset = queryset.filter(**{lookup: values})
            # 复杂过滤，如区间，比较，时间等
            elif isinstance(values, dict):
                queryset = self.apply_complex_filter(queryset, field, values)
        return queryset

    def apply_complex_filter(self, queryset, field, values):
        # 区间检索
        # print(11111, 'complex filter:', field, values)
        if 'start' in values or 'end' in values:
            if values.get('start') is not None:
                queryset = queryset.filter(**{f'{field}__gte': values['start']})
            if values.get('end') is not None:
                queryset = queryset.filter(**{f'{field}__lte': values['end']})

        # 比较检索
        if 'operator' in values and 'value' in values:
            operator = values['operator']
            value = values['value']
            if operator is not None and value is not None:
                queryset = queryset.filter(**{f'{field}{operator}': value})

        # 时间范围检索
        if 'start_time' in values or 'end_time' in values:
            start_time = self.check_time(values.get('start_time'))
            end_time = self.check_time(values.get('end_time'))
            if start_time is not None:
                queryset = queryset.filter(**{f'{field}__gte': start_time})
            if end_time is not None:
                queryset = queryset.filter(**{f'{field}__lte': end_time})

        return queryset

    @staticmethod
    def check_time(time_value):
        if isinstance(time_value, int):
            if len(str(time_value)) == 13:
                time_value = time_value / 1000
            return datetime.datetime.fromtimestamp(time_value)
        return None
