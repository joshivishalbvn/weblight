# -*- coding: utf-8 -*-
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    http://api.example.org/accounts/?page=4
    http://api.example.org/accounts/?page=4&page_size=100
    """

    page_size = 20
    page_size_query_param = "page_size"

    def _positive_int(self, integer_string, strict=False, cutoff=None):
        """
        Cast a string to a strictly positive integer.
        """
        ret = int(integer_string)
        if ret < 0 or (ret == 0 and strict):
            raise ValueError()
        if cutoff:
            return min(ret, cutoff)
        return ret

    def get_page_size(self, request):
        """
        return custom page size
        """
        if self.page_size_query_param:
            try:
                return self._positive_int(
                    request.query_params[self.page_size_query_param], strict=True, cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link() or ""),
                    ("previous", self.get_previous_link() or ""),
                    ("num_pages", self.page.paginator.num_pages),
                    ("results", data),
                ]
            )
        )
