from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DeskOrderSerializer, OrderResponseSerializer
from .services import create_order


class OrderCreateView(APIView):
    def post(self, request):
        serializer = DeskOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(serializer.validated_data)
        return Response(
            OrderResponseSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
