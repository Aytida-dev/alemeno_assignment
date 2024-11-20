from django.db import DatabaseError
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta

from .controllers import calculate_credit_score, get_loan

from .models import Customer, Loan


from .serializers import CustomerSerializer, LoanBody, LoanSerializer, RegisterBody

# Create your views here.

@api_view(['GET'])
def home(request):
    return Response({'message': 'Welcome to Credit System!'})

@api_view(['POST'])
def create_customer(request):
    try:
        serializer = RegisterBody(data=request.data)
        
        if not serializer.is_valid():
            return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=400)
        
        try:
            new_customer = serializer.create(serializer.validated_data)
        except DatabaseError as db_error:
            print(f"Database error: {db_error}")
            return Response({'message': 'error while creating customer'}, status=500)

        return Response({
            'customer_id': new_customer.customer_id,
            'name': f"{new_customer.first_name} {new_customer.last_name}",
            'phone_number': new_customer.phone_number,
            'monthly_income': new_customer.monthly_salary,
            'age': request.data.get('age'),  
            'approved_limit': new_customer.approved_limit
        }, status=201)
        
    except ValidationError as validation_error:
        print(f"Validation error: {validation_error}")
        return Response({'message': 'Invalid input', 'errors': str(validation_error)}, status=400)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({'message': 'An unexpected error occurred'}, status=500)
    
@api_view(['POST'])
def check_eligiblity(request):
    try:
        serializer = LoanBody(data=request.data)
        
        if not serializer.is_valid():
            return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=400)
        
        try:
            customer_id = serializer.validated_data['customer_id']
            customer = Customer.objects.get(customer_id=customer_id)
            loans = Loan.objects.filter(customer_id=customer_id)            
        except Exception as e:
            return Response({'message': 'Customer not found'}, status=404)
        
        credit_score, status = calculate_credit_score(customer, loans, serializer.validated_data['loan_amount'])
        if status == "REJECT":
            return Response({'customer_id':customer.customer_id , 'approval':False}, status=200)
        
        result = get_loan(credit_score)
        if result['status'] == "REJECT":
            return Response({'customer_id':customer.customer_id , 'approval':False}, status=200)
        
        emi = (serializer.validated_data['loan_amount'] * (1 + serializer.validated_data['interest_rate']/100))/serializer.validated_data['tenure']
        
        return Response({
            'customer_id':customer.customer_id , 
            'approval':True, 'monthly_installment':emi , 
            'tenure':serializer.validated_data['tenure'],
            'interest_rate':serializer.validated_data['interest_rate'],
            'corrected_interest_rate':result.get('interest',serializer.validated_data['interest_rate'])
        }, status=200)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({'message': 'An unexpected error occurred'}, status=500)


@api_view(['POST'])
def create_loan(request):
    try:
        serializer = LoanBody(data=request.data)
        
        if not serializer.is_valid():
            return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=400)
        
        try:
            customer_id = serializer.validated_data['customer_id']
            customer = Customer.objects.get(customer_id=customer_id)
            loans = Loan.objects.filter(customer_id=customer_id)            
        except Exception as e:
            return Response({'message': 'Customer not found'}, status=404)
        
        credit_score, status = calculate_credit_score(customer, loans, serializer.validated_data['loan_amount'])
        if status == "REJECT":
            return Response({'customer_id':customer.customer_id , 'approval':False}, status=200)
        
        result = get_loan(credit_score)
        if result['status'] == "REJECT":
            return Response({'customer_id':customer.customer_id , 'approval':False}, status=200)
        
        emi = (serializer.validated_data['loan_amount'] * (1 + serializer.validated_data['interest_rate']/100))/serializer.validated_data['tenure']
        
        try:
            Loan.objects.create(
                customer_id=customer,
                loan_amount=serializer.validated_data['loan_amount'],
                tenure=serializer.validated_data['tenure'],
                interest_rate=result.get('interest',serializer.validated_data['interest_rate']),
                emi=emi,
                emi_paid_on_time=0,
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=serializer.validated_data['tenure']*30)
            )
        except DatabaseError as db_error:
            print(f"Database error: {db_error}")
            return Response({'message': 'error while creating loan'}, status=500)
        
        return Response({
            'customer_id':customer.customer_id , 
            'approval':True, 'monthly_installment':emi , 
            'tenure':serializer.validated_data['tenure'],
            'interest_rate':serializer.validated_data['interest_rate'],
            'corrected_interest_rate':result.get('interest',serializer.validated_data['interest_rate'])
        }, status=200)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({'message': 'An unexpected error occurred'}, status=500)
    
@api_view(['GET'])
def get_loan(request , loan_id):
    try:
        result = Loan.objects.select_related('customer_id').get(loan_id=loan_id)
        loan = LoanSerializer(result).data
        customer = CustomerSerializer(result.customer_id).data
        
        return Response({
            'loan_id':loan['loan_id'],
            'customer':customer,
            'loan_amount':loan['loan_amount'],
            'interest_rate':loan['interest_rate'],
            'tenure':loan['tenure'],
            'monthly_installment':loan['emi'],
            }, status=200)
        
    except Loan.DoesNotExist:
        return Response({'message': 'Loan not found'}, status=404)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({'message': 'An unexpected error occurred'}, status=500)
    
@api_view(['GET'])
def view_loan_by_customer(request,customer_id):
    try:
        result = Customer.objects.prefetch_related('loan_set').get(customer_id=customer_id)
    
        loans = LoanSerializer(result.loan_set.all(),many=True).data
                
        response = []
        for loan in loans:
            emi_left = loan['tenure'] - loan['emi_paid_on_time']
            response.append({
                'loan_id':loan['loan_id'],
                'loan_amount':loan['loan_amount'],
                'interest_rate':loan['interest_rate'],
                'monthly_installment':loan['emi'],
                'repayments_left':emi_left
            })
        
        return Response(response, status=200)
    except Customer.DoesNotExist:
        return Response({'message': 'Customer not found'}, status=404)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response({'message': 'An unexpected error occurred'}, status=500)
        
        

