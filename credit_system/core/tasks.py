import pandas as pd
from celery import shared_task
from .models import Customer, Loan

@shared_task
def ingest_data(file_path_customer, file_path_loan):
    try:
        df_customer = pd.read_excel(file_path_customer)
        for _, row in df_customer.iterrows():
            Customer.objects.create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age = row['Age'],
                phone_number=row['Phone Number'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],
            )
        
        print('Customer data ingested successfully')
        
        df_loan = pd.read_excel(file_path_loan)
        for _, row in df_loan.iterrows():
            customer = Customer.objects.get(customer_id=row['Customer ID'])

            Loan.objects.create(
                customer_id=customer,
                loan_id=row['Loan ID'],
                loan_amount=row['Loan Amount'],
                tenure=row['Tenure'],
                interest_rate=row['Interest Rate'],
                emi=row['Monthly payment'],
                emi_paid_on_time=row['EMIs paid on Time'],
                start_date=pd.to_datetime(row['Date of Approval']).date(),
                end_date=pd.to_datetime(row['End Date']).date()
            )
            
        return "Customer and Loan data ingested successfully"
    except Exception as e:
        print(e)
        return f"Error ingesting data: {str(e)}"
