from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

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
    
class Item(models.Model):
    UNIT_CHOICES = [
        ('kg', 'KG (Kilogram)'),
        ('g', 'G (Gram)'),
        ('qtl', 'QTL (Quintal)'),
        ('ton', 'TON (Ton)'),
        ('pcs', 'Pieces'),
        ('box', 'Box'),
        ('bag', 'Bag'),
        ('bundle', 'Bundle'),
        ('roll', 'Roll'),
        ('meter', 'Meter'),
        ('feet', 'Feet'),
        ('liter', 'Liter'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=255, help_text="Item name (e.g., Cement, Rice, Medicine Box)")
    code = models.CharField(max_length=50, blank=True, unique=True, help_text="Item code/SKU")
    description = models.TextField(blank=True, help_text="Detailed description")
    
    # Specifications
    size = models.CharField(max_length=100, blank=True, help_text="Size (e.g., 50kg, 1x2ft, 10x10)")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    weight_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Weight per unit in KG")
    
    # Pricing (Optional - for freight calculation)
    default_freight_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Default freight rate per KG/QTL")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_items')
    
    class Meta:
        ordering = ['name']
        verbose_name = "Item"
        verbose_name_plural = "Items"
    
    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"    


class Builty(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    ]
    
    # Builty Identification
    builty_no = models.CharField(max_length=50, unique=True, editable=False)
    date = models.DateField(auto_now_add=True)
    
    # Party Details (Sender & Receiver)
    sender = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, related_name='sent_builty')
    receiver = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, related_name='received_builty')
    
    # Route Details
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    
    # Vehicle & Driver Details
    vehicle = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'driver'})
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=15, blank=True)
    vehicle_number = models.CharField(max_length=20, blank=True)
    
    # Consignment Details
    total_quantity = models.IntegerField(default=0)
    total_weight = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Charges
    total_freight = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_hamali = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_billi_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_other_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Grand Total
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Delivery
    delivery_date = models.DateField(null=True, blank=True)
    delivery_person = models.CharField(max_length=100, blank=True)
    pod_attachment = models.FileField(upload_to='pod_documents/', blank=True, null=True)
    
    # Remarks
    remarks = models.TextField(blank=True)
    
    # Created by
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_builty')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-id']
        verbose_name = "Builty"
        verbose_name_plural = "Builty"
    
    def calculate_grand_total(self):
        """Calculate grand total safely"""
        try:
            freight = Decimal(str(self.total_freight)) if self.total_freight else Decimal('0')
            hamali = Decimal(str(self.total_hamali)) if self.total_hamali else Decimal('0')
            billi = Decimal(str(self.total_billi_charge)) if self.total_billi_charge else Decimal('0')
            other = Decimal(str(self.total_other_expense)) if self.total_other_expense else Decimal('0')
            paid = Decimal(str(self.paid_amount)) if self.paid_amount else Decimal('0')
            
            self.grand_total = freight + hamali + billi + other - paid
        except Exception as e:
            self.grand_total = Decimal('0')
        return self.grand_total
    
    def save(self, *args, **kwargs):
        if not self.builty_no:
            import datetime
            now = datetime.datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            last_builty = Builty.objects.filter(builty_no__icontains=f"{year}/{month}").order_by('-id').first()
            if last_builty:
                try:
                    last_no = int(last_builty.builty_no.split('/')[-1])
                    new_no = last_no + 1
                except:
                    new_no = 1
            else:
                new_no = 1
            self.builty_no = f"KBRL/{year}/{month}/{str(new_no).zfill(4)}"
        
        # Calculate grand total before saving
        self.calculate_grand_total()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.builty_no} - {self.sender.name if self.sender else 'N/A'} to {self.receiver.name if self.receiver else 'N/A'}"


class BuiltyItem(models.Model):
    builty = models.ForeignKey(Builty, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Item Details
    item_name = models.CharField(max_length=255)  # Free text if no item master
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, default='pcs')  # KG, QTL, PCS, etc.
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Charges per item
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hamali = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billi_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_freight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def total(self):
        return self.freight + self.hamali + self.billi_charge + self.other_expense - self.paid_freight
    
    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    

    