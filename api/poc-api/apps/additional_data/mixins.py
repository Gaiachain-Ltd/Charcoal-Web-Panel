from rest_framework import viewsets


class MultiSerializerMixin(viewsets.GenericViewSet):
    """
    Allows to use many serializers in one viewset.
    """
    custom_serializer_classes = {}
    querysets = {}

    def get_serializer_class(self):
        """ Return the class to use for serializer w.r.t to the request method."""

        try:
            return self.custom_serializer_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_custom_queryset(self):
        """ Return the queryset."""

        try:
            return self.querysets[self.action]
        except (KeyError, AttributeError):
            return None
