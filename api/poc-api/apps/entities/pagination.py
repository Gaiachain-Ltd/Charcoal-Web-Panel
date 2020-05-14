from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination as CoreLimitOffsetPagination


class LimitOffsetPagination(CoreLimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        if self.limit is None:
            return list(queryset)

        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data):
        if not self.limit:
            return Response(OrderedDict([
                ('count', self.count),
                ('results', data)
            ]))
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
