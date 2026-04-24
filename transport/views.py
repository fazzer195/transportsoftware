from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import connection
from .models import Builty, BuiltyItem, Item, Party, Truck, User 
from django.utils import timezone

def login_view(request):
    # Agar user already logged in hai toh redirect karo
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'staff':
            return redirect('staff_dashboard')
        elif request.user.role == 'driver':
            return redirect('driver_dashboard')
        elif request.user.role == 'clerk':
            return redirect('clerk_dashboard')
        elif request.user.role == 'munshi':
            return redirect('munshi_dashboard')
        elif request.user.role == 'accountant':
            return redirect('accountant_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Super admin ke liye alag check
            if user.is_superuser:
                if role == 'super_admin':
                    auth_login(request, user)
                    return redirect('/admin/')
                else:
                    messages.error(request, 'कृपया सुपर एडमिन रोल चुनें!')
            else:
                # Normal users ke liye role check
                if user.role == role:
                    auth_login(request, user)
                    if user.role == 'admin':
                        return redirect('admin_dashboard')
                    elif user.role == 'staff':
                        return redirect('staff_dashboard')
                    elif user.role == 'munshi':
                        return redirect('munshi_dashboard')
                    elif user.role == 'driver':
                        return redirect('driver_dashboard')
                    elif user.role == 'clerk':
                        return redirect('clerk_dashboard')
                    elif user.role == 'accountant':
                        return redirect('accountant_dashboard')
                else:
                    messages.error(request, 'गलत रोल चुना गया है!')
        else:
            messages.error(request, 'गलत यूजरनेम या पासवर्ड!')
    
    return render(request, 'transport/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_dashboard(request):
    # Sirf admin role wale access kar sakte hain
    if request.user.role != 'admin':
        return redirect('login')
    return render(request, 'transport/admin_dashboard.html')

@login_required
def staff_dashboard(request):
    # Sirf staff role wale access kar sakte hain
    if request.user.role != 'staff':
        return redirect('login')
    return render(request, 'transport/staff_dashboard.html')

@login_required
def munshi_dashboard(request):
    # Sirf munshi role wale access kar sakte hain
    if request.user.role != 'munshi':
        return redirect('login')
    return render(request, 'transport/munshi_dashboard.html')

@login_required
def driver_dashboard(request):
    # Sirf driver role wale access kar sakte hain
    if request.user.role != 'driver':
        return redirect('login')
    return render(request, 'transport/driver_dashboard.html')


@login_required
def clerk_dashboard(request):
    # Sirf clerk role wale access kar sakte hain
    if request.user.role != 'clerk':
        return redirect('login')
    return render(request, 'transport/clerk_dashboard.html')


@login_required
def accountant_dashboard(request):
    # Sirf accountant role wale access kar sakte hain
    if request.user.role != 'accountant':
        return redirect('login')
    return render(request, 'transport/accountant_dashboard.html')


@login_required
def dashboard_redirect(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'staff':
        return redirect('staff_dashboard')
    elif request.user.role == 'munshi':
        return redirect('munshi_dashboard')
    elif request.user.role == 'driver':
        return redirect('driver_dashboard')
    elif request.user.role == 'clerk':
        return redirect('clerk_dashboard')
    elif request.user.role == 'accountant':
        return redirect('accountant_dashboard')
    return redirect('login')


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    # Start with all non-superuser users
    users = User.objects.filter(is_superuser=False)
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Apply role filter
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Apply status filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'inactive_users': users.filter(is_active=False).count(),
        'admin_count': users.filter(role='admin').count(),
        'staff_count': users.filter(role='staff').count(),
        'driver_count': users.filter(role='driver').count(),
    }
    return render(request, 'transport/user_list.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'पासवर्ड और कन्फर्म पासवर्ड मेल नहीं खाते!')
            return render(request, 'transport/user_form.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'यह यूजरनेम पहले से मौजूद है!')
            return render(request, 'transport/user_form.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'यह ईमेल पहले से मौजूद है!')
            return render(request, 'transport/user_form.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            address=address,
            is_active=is_active
        )

        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        if request.FILES.get('aadhar_attachment'):
            user.aadhar_attachment = request.FILES['aadhar_attachment']
        if request.FILES.get('pan_attachment'):
            user.pan_attachment = request.FILES['pan_attachment']
        if request.FILES.get('license_attachment'):
            user.license_attachment = request.FILES['license_attachment']
        
        user.aadhar_number = request.POST.get('aadhar_number', '')
        user.pan_number = request.POST.get('pan_number', '')
        user.license_number = request.POST.get('license_number', '')
        user.experience_years = request.POST.get('experience_years', 0)
        
        user.save()
        
        messages.success(request, f'यूजर "{username}" सफलतापूर्वक बन गया!')
        return redirect('user_list')
    
    return render(request, 'transport/user_form.html')

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_edit(request, user_id):
    # Admin khud ko edit nahi kar sakta
    if user_id == request.user.id:
        messages.error(request, 'आप अपने आप को एडिट नहीं कर सकते!')
        return redirect('user_list')
    
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password')
        if password:
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                user.set_password(password)
            else:
                messages.error(request, 'पासवर्ड और कन्फर्म पासवर्ड मेल नहीं खाते!')
                return render(request, 'transport/user_form.html', {'user': user})
            
        if 'profile_picture' in request.FILES:
            # Delete old file if exists
            if user.profile_picture:
                user.profile_picture.delete()
            user.profile_picture = request.FILES['profile_picture']
        
        if 'aadhar_attachment' in request.FILES:
            if user.aadhar_attachment:
                user.aadhar_attachment.delete()
            user.aadhar_attachment = request.FILES['aadhar_attachment']
        
        if 'pan_attachment' in request.FILES:
            if user.pan_attachment:
                user.pan_attachment.delete()
            user.pan_attachment = request.FILES['pan_attachment']
        
        if 'license_attachment' in request.FILES:
            if user.license_attachment:
                user.license_attachment.delete()
            user.license_attachment = request.FILES['license_attachment']
        
        user.aadhar_number = request.POST.get('aadhar_number', '')
        user.pan_number = request.POST.get('pan_number', '')
        user.license_number = request.POST.get('license_number', '')
        user.experience_years = request.POST.get('experience_years', 0) or 0
        
            
        
        user.save()
        messages.success(request, f'यूजर "{user.username}" अपडेट हो गया!')
        return redirect('user_list')
    
    return render(request, 'transport/user_form.html', {'user': user})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_delete(request, user_id):
    if user_id == request.user.id:
        messages.error(request, 'आप अपने आप को डिलीट नहीं कर सकते!')
        return redirect('user_list')
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    username = user.username
    user.delete()
    messages.success(request, f'यूजर "{username}" डिलीट हो गया!')
    return redirect('user_list')

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_toggle_status(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = not user.is_active
    user.save()
    status = "सक्रिय" if user.is_active else "निष्क्रिय"
    messages.success(request, f'यूजर "{user.username}" {status} कर दिया गया!')
    return redirect('user_list')


def get_states(request):
    """Get states where country_id = 101 (India)"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, state_name FROM states WHERE country_id = 101 ORDER BY state_name")
        states = cursor.fetchall()
    
    data = [{'id': s[0], 'name': s[1]} for s in states]
    return JsonResponse(data, safe=False)

def get_cities(request):
    """Get cities based on state_id"""
    state_id = request.GET.get('state_id')
    if state_id:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, city_name FROM cities WHERE state_id = %s ORDER BY city_name", [state_id])
            cities = cursor.fetchall()
        
        data = [{'id': c[0], 'name': c[1]} for c in cities]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def party_list(request):
    """List all parties with filters"""
    search_query = request.GET.get('search', '')
    party_type_filter = request.GET.get('party_type', '')
    city_filter = request.GET.get('city', '')
    status_filter = request.GET.get('status', '')
    
    parties = Party.objects.all()
    
    if search_query:
        parties = parties.filter(
            models.Q(name__icontains=search_query) |
            models.Q(company_name__icontains=search_query) |
            models.Q(mobile__icontains=search_query) |
            models.Q(city_name__icontains=search_query)
        )
    
    if party_type_filter:
        parties = parties.filter(party_type=party_type_filter)
    
    if city_filter:
        parties = parties.filter(city_name__icontains=city_filter)
    
    if status_filter == 'active':
        parties = parties.filter(is_active=True)
    elif status_filter == 'inactive':
        parties = parties.filter(is_active=False)
    
    paginator = Paginator(parties, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'parties': page_obj,
        'search_query': search_query,
        'party_type_filter': party_type_filter,
        'city_filter': city_filter,
        'status_filter': status_filter,
        'total_parties': parties.count(),
        'active_parties': parties.filter(is_active=True).count(),
        'inactive_parties': parties.filter(is_active=False).count(),
        'sender_count': parties.filter(party_type='sender').count(),
        'receiver_count': parties.filter(party_type='receiver').count(),
        'both_count': parties.filter(party_type='both').count(),
    }
    return render(request, 'transport/party_list.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def party_create(request):
    """Create new party"""
    if request.method == 'POST':
        try:
            party = Party.objects.create(
                party_type=request.POST.get('party_type'),
                name=request.POST.get('name'),
                company_name=request.POST.get('company_name', ''),
                mobile=request.POST.get('mobile'),
                alternate_mobile=request.POST.get('alternate_mobile', ''),
                email=request.POST.get('email', ''),
                gst_number=request.POST.get('gst_number', ''),
                address=request.POST.get('address'),
                state_id=request.POST.get('state') or None,
                city_id=request.POST.get('city') or None,
                state_name=request.POST.get('state_name', ''),
                city_name=request.POST.get('city_name', ''),
                pincode=request.POST.get('pincode'),
                opening_balance=request.POST.get('opening_balance', 0),
                credit_limit=request.POST.get('credit_limit', 0),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, f'Party "{party.name}" created successfully!')
            return redirect('party_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'transport/party_form.html')


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def party_edit(request, party_id):
    """Edit existing party"""
    party = get_object_or_404(Party, id=party_id)
    
    if request.method == 'POST':
        try:
            party.party_type = request.POST.get('party_type')
            party.name = request.POST.get('name')
            party.company_name = request.POST.get('company_name', '')
            party.mobile = request.POST.get('mobile')
            party.alternate_mobile = request.POST.get('alternate_mobile', '')
            party.email = request.POST.get('email', '')
            party.gst_number = request.POST.get('gst_number', '')
            party.address = request.POST.get('address')
            party.state_id = request.POST.get('state') or None
            party.city_id = request.POST.get('city') or None
            party.state_name = request.POST.get('state_name', '')
            party.city_name = request.POST.get('city_name', '')
            party.pincode = request.POST.get('pincode')
            party.opening_balance = request.POST.get('opening_balance', 0)
            party.credit_limit = request.POST.get('credit_limit', 0)
            party.is_active = request.POST.get('is_active') == 'on'
            party.save()
            
            messages.success(request, f'Party "{party.name}" updated successfully!')
            return redirect('party_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'transport/party_form.html', {'party': party})


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def party_delete(request, party_id):
    """Delete party"""
    party = get_object_or_404(Party, id=party_id)
    party_name = party.name
    party.delete()
    messages.success(request, f'Party "{party_name}" deleted successfully!')
    return redirect('party_list')


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def party_toggle_status(request, party_id):
    """Toggle party active/inactive status"""
    party = get_object_or_404(Party, id=party_id)
    party.is_active = not party.is_active
    party.save()
    status = "activated" if party.is_active else "deactivated"
    messages.success(request, f'Party "{party.name}" {status}!')
    return redirect('party_list')


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def truck_list(request):
    trucks = Truck.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        trucks = trucks.filter(
            models.Q(vehicle_number__icontains=search_query) |
            models.Q(owner_name__icontains=search_query)
        )
    
    paginator = Paginator(trucks, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'trucks': page_obj,
        'search_query': search_query,
        'total_trucks': trucks.count(),
        'active_trucks': trucks.filter(status='active').count(),
        'on_trip_trucks': trucks.filter(status='on_trip').count(),
        'maintenance_trucks': trucks.filter(status='maintenance').count(),
    }
    return render(request, 'transport/truck_list.html', context)

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def truck_create(request):
    drivers = User.objects.filter(role='driver', is_active=True)
    
    if request.method == 'POST':
        truck = Truck.objects.create(
            vehicle_number=request.POST.get('vehicle_number'),
            chassis_number=request.POST.get('chassis_number'),
            engine_number=request.POST.get('engine_number'),
            truck_type=request.POST.get('truck_type'),
            fuel_type=request.POST.get('fuel_type'),
            max_weight_capacity=request.POST.get('max_weight_capacity', 0),
            max_volume_capacity=request.POST.get('max_volume_capacity', 0),
            owner_name=request.POST.get('owner_name'),
            owner_phone=request.POST.get('owner_phone'),
            primary_driver_id=request.POST.get('primary_driver') or None,
            rc_number=request.POST.get('rc_number'),
            insurance_number=request.POST.get('insurance_number'),
            insurance_expiry=request.POST.get('insurance_expiry') or None,
            fitness_validity=request.POST.get('fitness_validity') or None,
            permit_number=request.POST.get('permit_number'),
            status=request.POST.get('status'),
        )
        
        # Handle file uploads
        if request.FILES.get('rc_attachment'):
            truck.rc_attachment = request.FILES['rc_attachment']
        if request.FILES.get('insurance_attachment'):
            truck.insurance_attachment = request.FILES['insurance_attachment']
        if request.FILES.get('permit_attachment'):
            truck.permit_attachment = request.FILES['permit_attachment']
        
        truck.save()
        messages.success(request, f'Truck "{truck.vehicle_number}" added successfully!')
        return redirect('truck_list')
    
    return render(request, 'transport/truck_form.html', {'drivers': drivers})

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def truck_edit(request, truck_id):
    truck = get_object_or_404(Truck, id=truck_id)
    drivers = User.objects.filter(role='driver', is_active=True)
    
    if request.method == 'POST':
        truck.vehicle_number = request.POST.get('vehicle_number')
        truck.chassis_number = request.POST.get('chassis_number')
        truck.engine_number = request.POST.get('engine_number')
        truck.truck_type = request.POST.get('truck_type')
        truck.fuel_type = request.POST.get('fuel_type')
        truck.max_weight_capacity = request.POST.get('max_weight_capacity', 0)
        truck.max_volume_capacity = request.POST.get('max_volume_capacity', 0)
        truck.owner_name = request.POST.get('owner_name')
        truck.owner_phone = request.POST.get('owner_phone')
        truck.primary_driver_id = request.POST.get('primary_driver') or None
        truck.rc_number = request.POST.get('rc_number')
        truck.insurance_number = request.POST.get('insurance_number')
        truck.insurance_expiry = request.POST.get('insurance_expiry') or None
        truck.fitness_validity = request.POST.get('fitness_validity') or None
        truck.permit_number = request.POST.get('permit_number')
        truck.status = request.POST.get('status')
        
        if request.FILES.get('rc_attachment'):
            truck.rc_attachment = request.FILES['rc_attachment']
        if request.FILES.get('insurance_attachment'):
            truck.insurance_attachment = request.FILES['insurance_attachment']
        if request.FILES.get('permit_attachment'):
            truck.permit_attachment = request.FILES['permit_attachment']
        
        truck.save()
        messages.success(request, f'Truck "{truck.vehicle_number}" updated successfully!')
        return redirect('truck_list')
    
    return render(request, 'transport/truck_form.html', {'truck': truck, 'drivers': drivers})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def truck_delete(request, truck_id):
    truck = get_object_or_404(Truck, id=truck_id)
    truck.delete()
    messages.success(request, 'Truck deleted successfully!')
    return redirect('truck_list')


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def item_list(request):
    """List all items with filters"""
    search_query = request.GET.get('search', '')
    unit_filter = request.GET.get('unit', '')
    status_filter = request.GET.get('status', '')
    
    items = Item.objects.all()
    
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if unit_filter:
        items = items.filter(unit=unit_filter)
    
    if status_filter:
        items = items.filter(status=status_filter)
    
    paginator = Paginator(items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items': page_obj,
        'search_query': search_query,
        'unit_filter': unit_filter,
        'status_filter': status_filter,
        'total_items': items.count(),
        'active_items': items.filter(status='active').count(),
        'inactive_items': items.filter(status='inactive').count(),
        'unit_choices': Item.UNIT_CHOICES,
    }
    return render(request, 'transport/item_list.html', context)


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def item_create(request):
    """Create new item"""
    if request.method == 'POST':
        try:
            # Generate code if not provided
            code = request.POST.get('code', '')
            if not code:
                import datetime
                code = f"ITEM{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            item = Item.objects.create(
                name=request.POST.get('name'),
                code=code,
                description=request.POST.get('description', ''),
                size=request.POST.get('size', ''),
                unit=request.POST.get('unit'),
                weight_per_unit=request.POST.get('weight_per_unit', 0),
                default_freight_rate=request.POST.get('default_freight_rate', 0),
                status=request.POST.get('status', 'active'),
                created_by=request.user,
            )
            messages.success(request, f'Item "{item.name}" created successfully!')
            return redirect('item_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'transport/item_form.html')


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def item_edit(request, item_id):
    """Edit existing item"""
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        try:
            item.name = request.POST.get('name')
            item.code = request.POST.get('code')
            item.description = request.POST.get('description', '')
            item.size = request.POST.get('size', '')
            item.unit = request.POST.get('unit')
            item.weight_per_unit = request.POST.get('weight_per_unit', 0)
            item.default_freight_rate = request.POST.get('default_freight_rate', 0)
            item.status = request.POST.get('status', 'active')
            item.save()
            
            messages.success(request, f'Item "{item.name}" updated successfully!')
            return redirect('item_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'transport/item_form.html', {'item': item})


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def item_delete(request, item_id):
    """Delete item"""
    item = get_object_or_404(Item, id=item_id)
    item_name = item.name
    item.delete()
    messages.success(request, f'Item "{item_name}" deleted successfully!')
    return redirect('item_list')


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'staff','munshi'])
def item_toggle_status(request, item_id):
    """Toggle item active/inactive status"""
    item = get_object_or_404(Item, id=item_id)
    item.status = 'inactive' if item.status == 'active' else 'active'
    item.save()
    status = "activated" if item.status == 'active' else "deactivated"
    messages.success(request, f'Item "{item.name}" {status}!')
    return redirect('item_list')


@login_required
def get_items_api(request):
    """API endpoint for builty form - get items for dropdown"""
    items = Item.objects.filter(status='active').values('id', 'name', 'code', 'unit', 'weight_per_unit', 'default_freight_rate')
    return JsonResponse(list(items), safe=False)

@login_required
def builty_list(request):
    """List all builty with filters"""
    # Munshi sirf apni builty dekhega, Admin sab
    if request.user.role == 'munshi':
        builty = Builty.objects.filter(created_by=request.user)
    else:
        builty = Builty.objects.all()
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    if search_query:
        builty = builty.filter(
            Q(builty_no__icontains=search_query) |
            Q(sender__name__icontains=search_query) |
            Q(receiver__name__icontains=search_query)
        )
    
    if status_filter:
        builty = builty.filter(status=status_filter)
    
    if from_date:
        builty = builty.filter(date__gte=from_date)
    
    if to_date:
        builty = builty.filter(date__lte=to_date)
    
    paginator = Paginator(builty, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'builty_list': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'from_date': from_date,
        'to_date': to_date,
        'total_builty': builty.count(),
        'pending_count': builty.filter(status='pending').count(),
        'in_transit_count': builty.filter(status='in_transit').count(),
        'delivered_count': builty.filter(status='delivered').count(),
    }
    return render(request, 'transport/builty_list.html', context)


@login_required
def builty_create(request):
    """Create new builty"""
    parties = Party.objects.filter(is_active=True)
    trucks = Truck.objects.filter(status='active')
    drivers = User.objects.filter(role='driver', is_active=True)
    items = Item.objects.filter(status='active')
    
    if request.method == 'POST':
        try:
            # Get or create sender
            sender_id = request.POST.get('sender')
            if sender_id and sender_id != '':
                sender = Party.objects.get(id=sender_id)
            else:
                # Create new sender
                sender = Party.objects.create(
                    party_type='sender',
                    name=request.POST.get('sender_name'),
                    mobile=request.POST.get('sender_mobile'),
                    address=request.POST.get('sender_address'),
                    city_name=request.POST.get('sender_city'),
                    state_name=request.POST.get('sender_state'),
                    pincode=request.POST.get('sender_pincode'),
                    is_active=True
                )
            
            # Get or create receiver
            receiver_id = request.POST.get('receiver')
            if receiver_id and receiver_id != '':
                receiver = Party.objects.get(id=receiver_id)
            else:
                receiver = Party.objects.create(
                    party_type='receiver',
                    name=request.POST.get('receiver_name'),
                    mobile=request.POST.get('receiver_mobile'),
                    address=request.POST.get('receiver_address'),
                    city_name=request.POST.get('receiver_city'),
                    state_name=request.POST.get('receiver_state'),
                    pincode=request.POST.get('receiver_pincode'),
                    is_active=True
                )
            
            # Get vehicle details
            vehicle_id = request.POST.get('vehicle')
            if vehicle_id and vehicle_id != '':
                vehicle = Truck.objects.get(id=vehicle_id)
                vehicle_number = vehicle.vehicle_number
                driver = vehicle.primary_driver
                driver_name = driver.username if driver else ''
                driver_phone = driver.phone if driver else ''
            else:
                vehicle = None
                vehicle_number = request.POST.get('vehicle_number', '')
                driver = None
                driver_name = request.POST.get('driver_name', '')
                driver_phone = request.POST.get('driver_phone', '')
            
            # Create builty
            builty = Builty.objects.create(
                sender=sender,
                receiver=receiver,
                from_location=request.POST.get('from_location'),
                to_location=request.POST.get('to_location'),
                vehicle=vehicle,
                vehicle_number=vehicle_number,
                driver=driver,
                driver_name=driver_name,
                driver_phone=driver_phone,
                total_quantity=int(request.POST.get('total_quantity', 0)),
                total_weight=request.POST.get('total_weight', 0),
                total_freight=request.POST.get('total_freight', 0),
                total_hamali=request.POST.get('total_hamali', 0),
                total_billi_charge=request.POST.get('total_billi_charge', 0),
                total_other_expense=request.POST.get('total_other_expense', 0),
                paid_amount=request.POST.get('paid_amount', 0),
                remarks=request.POST.get('remarks', ''),
                created_by=request.user,
                status='pending'
            )
            
            # Calculate grand total
            builty.grand_total = builty.calculate_grand_total()
            builty.save()
            
            # Save items
            item_names = request.POST.getlist('item_name[]')
            item_ids = request.POST.getlist('item_id[]')
            item_descs = request.POST.getlist('item_desc[]')
            item_quantities = request.POST.getlist('item_quantity[]')
            item_units = request.POST.getlist('item_unit[]')
            item_weights = request.POST.getlist('item_weight[]')
            item_freights = request.POST.getlist('item_freight[]')
            item_hamalis = request.POST.getlist('item_hamali[]')
            item_billi_charges = request.POST.getlist('item_billi_charge[]')
            
            for i in range(len(item_names)):
                if item_names[i] and item_quantities[i]:
                    item_obj = None
                    item_name = item_names[i].strip()
                    item_unit = item_units[i] if i < len(item_units) else 'pcs'
                    item_weight = float(item_weights[i]) if i < len(item_weights) else 0
                    item_freight = float(item_freights[i]) if i < len(item_freights) else 0
                    
                    # First try to get item by ID if provided
                    item_id = None
                    if i < len(item_ids) and item_ids[i]:
                        try:
                            item_obj = Item.objects.get(id=int(item_ids[i]))
                        except:
                            pass
                    
                    # If not found by ID, try to find by name
                    if not item_obj:
                        try:
                            item_obj = Item.objects.get(name__iexact=item_name, status='active')
                        except Item.DoesNotExist:
                            pass
                    
                    # If still not found, create new item
                    if not item_obj:
                        # Create new item automatically
                        item_obj = Item.objects.create(
                            name=item_name,
                            code=f"AUTO{Item.objects.count() + 1:05d}",
                            description=item_descs[i] if i < len(item_descs) else f"Auto created from builty {builty.builty_no}",
                            unit=item_unit,
                            weight_per_unit=item_weight,
                            default_freight_rate=item_freight,
                            status='active',
                            created_by=request.user
                        )
                    
                    # Create BuiltyItem with item reference
                    BuiltyItem.objects.create(
                        builty=builty,
                        item=item_obj,  # Store ForeignKey reference
                        item_name=item_obj.name,  # Store name as backup
                        description=item_descs[i] if i < len(item_descs) else '',
                        quantity=int(item_quantities[i]),
                        unit=item_unit,
                        weight=item_weight,
                        freight=item_freight,
                        hamali=float(item_hamalis[i]) if i < len(item_hamalis) else 0,
                        billi_charge=float(item_billi_charges[i]) if i < len(item_billi_charges) else 0,
                    )
            
            messages.success(request, f'Builty {builty.builty_no} created successfully!')
            
            # Redirect based on user role
            if request.user.role == 'munshi':
                return redirect('munshi_dashboard')
            else:
                return redirect('builty_list')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'transport/builty_form.html', {
                'parties': parties,
                'trucks': trucks,
                'drivers': drivers,
                'items': items,
                'form_data': request.POST,
            })
    
    context = {
        'parties': parties,
        'trucks': trucks,
        'drivers': drivers,
        'items': items,
    }
    return render(request, 'transport/builty_form.html', context)


@login_required
def builty_detail(request, builty_id):
    """View builty details"""
    builty = get_object_or_404(Builty, id=builty_id)
    
    # Munshi sirf apni builty dekh sakta hai
    if request.user.role == 'munshi' and builty.created_by != request.user:
        messages.error(request, 'You are not authorized to view this builty')
        return redirect('builty_list')
    
    return render(request, 'transport/builty_detail.html', {'builty': builty})


@login_required
def builty_print(request, builty_id):
    """Print builty challan"""
    builty = get_object_or_404(Builty, id=builty_id)
    return render(request, 'transport/builty_print.html', {'builty': builty})


@login_required
def builty_update_status(request, builty_id):
    """Update builty status (delivery)"""
    builty = get_object_or_404(Builty, id=builty_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        builty.status = new_status
        
        if new_status == 'delivered':
            builty.delivery_date = timezone.now().date()
            builty.delivery_person = request.POST.get('delivery_person', '')
            
            if request.FILES.get('pod_attachment'):
                builty.pod_attachment = request.FILES['pod_attachment']
        
        builty.save()
        messages.success(request, f'Builty {builty.builty_no} status updated to {new_status}')
        
        if request.user.role == 'munshi':
            return redirect('munshi_dashboard')
        return redirect('builty_list')
    
    return render(request, 'transport/builty_status_update.html', {'builty': builty})


@login_required
def builty_delete(request, builty_id):
    """Delete builty (admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Only admin can delete builty')
        return redirect('builty_list')
    
    builty = get_object_or_404(Builty, id=builty_id)
    builty_no = builty.builty_no
    builty.delete()
    messages.success(request, f'Builty {builty_no} deleted successfully!')
    return redirect('builty_list')


def get_party_details(request, party_id):
    """API to get party details"""
    party = get_object_or_404(Party, id=party_id)
    data = {
        'name': party.name,
        'mobile': party.mobile,
        'address': party.address,
        'city': party.city_name or party.city_id,
        'state': party.state_name or str(party.state) if party.state else '',
        'pincode': party.pincode,
    }
    return JsonResponse(data)


def get_vehicle_details(request, vehicle_id):
    """API to get vehicle details"""
    vehicle = get_object_or_404(Truck, id=vehicle_id)
    data = {
        'vehicle_number': vehicle.vehicle_number,
        'driver_id': vehicle.primary_driver.id if vehicle.primary_driver else '',
        'driver_name': vehicle.primary_driver.username if vehicle.primary_driver else '',
        'driver_phone': vehicle.primary_driver.phone if vehicle.primary_driver else '',
    }
    return JsonResponse(data)
