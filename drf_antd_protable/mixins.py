from rest_framework.decorators import action
from rest_framework.response import Response

from .utils.exporter import Exporter
from .utils.columns import get_columns_data


class ProTableMixin(object):
    """适配前端ProTable的request
    > https://procomponents.ant.design/components/table#request
    """

    @action(detail=False, methods=['GET'])
    def columns(self, request):
        """列配置接口
        """
        data = get_columns_data(self)

        return Response(data)


    @action(detail=False, methods=['POST'])
    def data(self, request):
        """数据接口

        - 分页参数(Query String Parameters)：
            - `current`
            - `pageSize`

        - 过滤参数(Request Payload)：
            - `sort`
            - `filter`
            - `search`
            - `globalSearch`
        """
        # 使用自定义分页器和过滤器：先过滤，后分页
        queryset = self.filter_queryset(self.queryset)
        queryset = self.paginate_queryset(queryset)
        return self.get_paginated_response(self.serializer_class(queryset, many=True).data)

    @action(detail=False, methods=['POST'])
    def export(self, request):
        """数据导出接口

        *导出数据时，前端需要传递 `exportType` 参数，用于指定导出的格式, 支持：csv, xlsx*
        """
        exportType = request.data.get('exportType')

        queryset = self.filter_queryset(self.queryset)
        queryset = self.paginate_queryset(queryset)
        data = self.serializer_class(queryset, many=True).data

        name_map = {
            **{f.name: f.verbose_name  for f in self.queryset.model._meta.fields},
            **{'password': '密码'}
        }

        # return Response(data)
        return Exporter(data, title_map=name_map).export(exportType)
