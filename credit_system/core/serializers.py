from django.db import DatabaseError
from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        
class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'
        
        
class RegisterBody(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    monthly_income = serializers.FloatField(min_value=0.01)
    age = serializers.IntegerField(min_value=1)

    monthly_salary = serializers.FloatField(required=False)  
    approved_limit = serializers.FloatField(required=False)  

    def get_approved_limit(self, validated_data):
        return round(validated_data['monthly_income'] * 36, -5)  

    def create(self, validated_data):
        try:
            validated_data['monthly_salary'] = validated_data['monthly_income']
            validated_data['approved_limit'] = self.get_approved_limit(validated_data)

            validated_data.pop('monthly_income', None)

            return Customer.objects.create(**validated_data)
        except DatabaseError as db_error:
            print(f"Database error while creating customer: {db_error}")
            raise
        except Exception as e:
            print(f"Unexpected error during customer creation: {e}")
            raise
        
class LoanBody(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0.01)
    tenure = serializers.IntegerField(min_value=1)
    interest_rate = serializers.FloatField(min_value=0.01)
    tenure = serializers.IntegerField(min_value=1)

        