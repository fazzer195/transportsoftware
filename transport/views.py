from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q
from .models import User
from django.core.paginator import Paginator

def login_view(request):
    # Agar user already logged in hai toh redirect karo
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'staff':
            return redirect('staff_dashboard')
    
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
def dashboard_redirect(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'staff':
        return redirect('staff_dashboard')
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
        
        messages.success(request, f'यूजर "{username}" सफलतापूर्वक बन गया!')
        return redirect('user_list')
    
    return render(request, 'transport/user_form.html')

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Check if password is being changed
        password = request.POST.get('password')
        if password:
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                user.set_password(password)
            else:
                messages.error(request, 'पासवर्ड और कन्फर्म पासवर्ड मेल नहीं खाते!')
                return render(request, 'transport/user_form.html', {'user': user})
        
        user.save()
        messages.success(request, f'यूजर "{user.username}" अपडेट हो गया!')
        return redirect('user_list')
    
    return render(request, 'transport/user_form.html', {'user': user})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def user_delete(request, user_id):
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