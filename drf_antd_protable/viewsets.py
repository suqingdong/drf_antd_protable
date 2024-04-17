from rest_framework.viewsets import ModelViewSet

from .mixins import ProTableMixin
from .pagination import ProtablePagination
from .filters import ProtableFilterBackend


class ProTableViewSet(ProTableMixin, ModelViewSet):
    pagination_class = ProtablePagination
    filter_backends = [ProtableFilterBackend]
