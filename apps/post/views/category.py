from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..models import Category
from ..serializers import CategorySerializer

class CategoryListView(generics.ListCreateAPIView):
    """分类列表视图"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'created_at']
    ordering = ['order', 'id']

class CategoryCreateView(generics.CreateAPIView):
    """分类创建视图"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class CategoryUpdateView(generics.UpdateAPIView):
    """分类更新视图"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class CategoryDeleteView(generics.DestroyAPIView):
    """分类删除视图"""
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]

class CategoryQuickCreateView(APIView):
    """快速创建分类视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        parent_id = request.data.get('parent')
        
        if not name:
            return Response(
                {'error': '分类名称不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查名称长度
        if len(name) < 2 or len(name) > 50:
            return Response(
                {'error': '分类名称长度必须在2-50个字符之间'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已存在
        if Category.objects.filter(name=name).exists():
            return Response(
                {'error': '分类名称已存在'},
                status=status.HTTP_409_CONFLICT
            )
        
        # 检查父分类是否存在
        parent = None
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                return Response(
                    {'error': '父分类不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # 创建分类
        category = Category.objects.create(
            name=name,
            parent=parent
        )
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'id': category.id,
                'name': category.name,
                'parent': parent.id if parent else None,
                'parent_name': parent.name if parent else None,
                'created_at': category.created_at.isoformat()
            },
            'timestamp': timezone.now().isoformat(),
            'requestId': request.META.get('HTTP_X_REQUEST_ID', '')
        }) 