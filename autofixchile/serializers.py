from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Vehiculo, Atencion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class VehiculoSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    class Meta:
        model = Vehiculo
        fields = '__all__'

    def create(self, validated_data):
        
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

class AtencionSerializer(serializers.ModelSerializer):
    vehiculo = VehiculoSerializer(read_only=True)

    class Meta:
        model = Atencion
        fields = '__all__'

    def create(self, validated_data):
        
        validated_data['vehiculo'] = validated_data.get('vehiculo', self.context['request'].user.vehiculos.first())
        return super().create(validated_data)
