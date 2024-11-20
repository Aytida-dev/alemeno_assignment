import random
from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=20, unique=True)
    monthly_salary = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField(null=True, blank=True, default=0.0)

    def save(self, *args, **kwargs):
        if not self.customer_id: 
            self.customer_id = random.randint(10000, 99999)
            while Customer.objects.filter(customer_id=self.customer_id).exists():
                self.customer_id = random.randint(10000, 99999)
        super().save(*args, **kwargs)
    
class Loan(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.IntegerField(db_index=True)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    emi = models.FloatField()
    emi_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    def save(self, *args, **kwargs):
        if not self.loan_id: 
            self.loan_id = random.randint(10000, 99999)
            while Loan.objects.filter(loan_id=self.loan_id).exists():
                self.loan_id = random.randint(10000, 99999)
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('customer_id', 'loan_id')
    
    