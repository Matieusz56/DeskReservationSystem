from django.views.generic import detail, DetailView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DeskOrderSerializer, OrderResponseSerializer
from .services import create_order
from .models import Order

class OrderCreateView(APIView):
    def post(self, request):
        serializer = DeskOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(serializer.validated_data)
        return Response(
            OrderResponseSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderResponseSerializer(orders, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class OrderDetailView(APIView):
    def get(self,request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"detail":"Order not found."},
                      status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderResponseSerializer(order)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )