from datetime import datetime

from .models import Customer, Loan

def calculate_credit_score(customer : Customer , loan_data : Loan , required_loan:float)->list[int,str]:
    approved_limit = customer.approved_limit
    
    if approved_limit < required_loan:
        return [0,"REJECT"]
    
    if len(loan_data) == 0:
        return [80,"CHECK"]
    
    loans_paid_on_time = 0
    loans_taken_in_past = 0
    loan_taken_in_current_year = 0
    total_loan_amount = 0
    current_emis = 0
        
    for loan in loan_data:
        loans_paid_on_time = loans_paid_on_time + loan.emi_paid_on_time
        loans_taken_in_past = loans_taken_in_past + 1 
        total_loan_amount = total_loan_amount + loan.loan_amount
        current_emis = current_emis + loan.emi
        
        if loan.start_date.year == datetime.now().year:
            loan_taken_in_current_year = loan_taken_in_current_year + 1
    
    credit_score = (loans_paid_on_time/loans_taken_in_past) * 100
    credit_score = min(credit_score,100)
    
    if current_emis > (customer.monthly_salary * 0.5):
        return [credit_score,"REJECT"]
    
    return [credit_score,"CHECK"]
       
       
def get_loan(credit_score)->dict:
    if credit_score > 50:
        return {"status":"APPROVE"}
    elif 50 > credit_score > 30:
        return {"status":"APPROVE","interest":12}
    elif 30 > credit_score > 10:
        return {"status":"APPROVE","interest":16}
    else:
        return {"status":"REJECT"}