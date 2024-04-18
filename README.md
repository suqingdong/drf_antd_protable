# Automates DRF APIs for Ant Design ProTable

> `drf_antd_protable` automates DRF APIs for Ant Design ProTable, enabling seamless data handling with pagination, sorting, filtering, and searching support, while automatically generating frontend table configurations.

## Installation
```bash
python3 -m pip install -U drf-antd-protable
```

## Usage

#### 1. use as `viewsets`

```python
# views.py
from drf_antd_protable.viewsets import ProTableViewSet
from . import models, serializers

class MyTableViewSet(ProTableViewSet):
    queryset = models.QA.objects.all()
    serializer_class = serializers.QA_Serializer
```

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import MyTableViewSet

router = DefaultRouter()
router.register('demo_table', MyTableViewSet, basename='demo_table')

urlpatterns = [
    # ...
    path('', include(router.urls)),
    # ...
]
```

#### 2. supporting columns configuration
- `hidden_fields`
- `select_fields`
- `sorter_fields`
- `copyable_fields`
- `not_search_fields`
- `render_region_fields`
- `render_compare_fields`
- `verbose_name_map`

example

```python
class MyTableViewSet(ProTableViewSet):
    queryset = models.QA.objects.all()
    serializer_class = serializers.QA_Serializer

    hidden_fields = ['id']
    select_fields = ['department']
    sorter_fields = ['user', 'question']
    copyable_fields = ['anwser']
    not_search_fields = ['department']
    render_region_fields = ['size']
    render_compare_fields = ['count']
    verbose_name_map = {
        'size': '大小',
        'count': '数量',
    }
```

## Endpoints

- `demo_table/columns/`
![](https://suqingdong.github.io/drf_antd_protable/src/columns.png)

- `demo_table/data/`
![](https://suqingdong.github.io/drf_antd_protable/src/data.png)

- `demo_table/export/`
![](https://suqingdong.github.io/drf_antd_protable/src/export.png)


## Use in Frontend
```jsx
import { ProTable } from '@ant-design/pro-components'
import { useRequest } from 'ahooks'
import { request } from '@umijs/max'

const DemoTable = () => {
    const columnsRequest = useRequest(async () => request('/api/demo_table/columns/'))

    return (
        <ProTable
            columns={columnsRequest.data}
            request={async (params, sorter, filter) => {
                const { current, pageSize, keyword, ...search } = params;
                const payload = {
                    sort: sorter,
                    filter: filter,
                    search: search,
                    globalSearch: keyword,
                };
                const data = await request('/api/demo_table/data/', {
                    method: 'POST',
                    data: payload,
                    params: { current, pageSize },
                })
                return data
            }}
        />
    )
}
```