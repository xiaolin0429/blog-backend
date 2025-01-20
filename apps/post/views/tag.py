from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Tag
from ..serializers import TagSerializer

class TagListView(generics.ListCreateAPIView):
    """标签列表视图"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    ordering = ['id']

class TagCreateView(generics.CreateAPIView):
    """标签创建视图"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class TagUpdateView(generics.UpdateAPIView):
    """标签更新视图"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class TagDeleteView(generics.DestroyAPIView):
    """标签删除视图"""
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticated]

class TagBatchCreateView(generics.CreateAPIView):
    """标签批量创建视图"""
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        tags = request.data if isinstance(request.data, list) else [request.data]
        serializer = self.get_serializer(data=tags, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        ) 