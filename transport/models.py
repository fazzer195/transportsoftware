from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('munshi', 'Munshi'),
        ('driver', 'Driver'),
        ('clerk', 'Clerk'),
        ('accountant', 'Accountant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    aadhar_attachment = models.FileField(upload_to='aadhar_cards/', blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    pan_attachment = models.FileField(upload_to='pan_cards/', blank=True, null=True)
    
    # Driver specific fields (will be used only if role is driver)
    license_number = models.CharField(max_length=20, blank=True, null=True)
    license_attachment = models.FileField(upload_to='licenses/', blank=True, null=True)
    experience_years = models.IntegerField(default=0, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    

class State(models.Model):
    state_name = models.CharField(max_length=100)
    country_id = models.IntegerField()
    

    class Meta:
        db_table = 'states'  # Exact table name
        managed = False      # Django table manage nahi karega
        app_label = 'transport'

class City(models.Model):
    city_name = models.CharField(max_length=100)
    state_id = models.IntegerField()  # Foreign key to states.id
    
    class Meta:
        db_table = 'cities'
        managed = False


class Party(models.Model):
    PARTY_TYPE_CHOICES = [
        ('sender', 'Sender (Consignor)'),
        ('receiver', 'Receiver (Consignee)'),
        ('both', 'Both (Sender & Receiver)'),
    ]
    
    # Basic Information
    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES, default='both')
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    
    # Contact Information
    mobile = models.CharField(max_length=15)
    alternate_mobile = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    gst_number = models.CharField(max_length=15, blank=True)
    
    # Address (State/City se linked)
    address = models.TextField()
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Also keep text fields for backward compatibility
    state_name = models.CharField(max_length=100, blank=True)
    city_name = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10)
    
    # Business Details
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_party_type_display()})"


class Truck(models.Model):
    TRUCK_TYPE_CHOICES = [
        ('open', 'Open Body'),
        ('closed', 'Closed Body'),
        ('container', 'Container'),
        ('freezer', 'Freezer/Reefer'),
        ('tipper', 'Tipper/Dumper'),
        ('tanker', 'Tanker'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
        ('on_trip', 'On Trip'),
    ]
    
    # Vehicle Identification
    vehicle_number = models.CharField(max_length=20, unique=True)  # UP 78 GN 2245
    chassis_number = models.CharField(max_length=50, blank=True, null=True)
    engine_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Vehicle Details
    truck_type = models.CharField(max_length=20, choices=TRUCK_TYPE_CHOICES, default='open')
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='diesel')
    
    # Capacity
    max_weight_capacity = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum weight in KG")
    max_volume_capacity = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum volume in cubic feet")
    
    # Owner Details
    owner_name = models.CharField(max_length=255, blank=True, null=True)
    owner_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Driver (FK to User with role='driver')
    primary_driver = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_trucks', limit_choices_to={'role': 'driver'})
    
    # RC and Insurance
    rc_number = models.CharField(max_length=50, blank=True, null=True)
    rc_attachment = models.FileField(upload_to='rc_documents/', blank=True, null=True)
    insurance_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_expiry = models.DateField(blank=True, null=True)
    insurance_attachment = models.FileField(upload_to='insurance_docs/', blank=True, null=True)
    
    # Fitness and Permit
    fitness_validity = models.DateField(blank=True, null=True)
    permit_number = models.CharField(max_length=50, blank=True, null=True)
    permit_attachment = models.FileField(upload_to='permits/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['vehicle_number']
    
    def __str__(self):
        return f"{self.vehicle_number} ({self.get_truck_type_display()})"

    

    