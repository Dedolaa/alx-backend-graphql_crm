#!/bin/bash

# Change to your project directory - UPDATE THIS PATH!
cd /c/Users/USER/alx_backend_graphql_crm

# Log start time
echo "$(date): Starting customer cleanup job" >> /tmp/customer_cleanup_log.txt

# Simple Python command to test the environment first
python -c "
print('Python is working')
print('Testing basic imports...')
try:
    import django
    from django.conf import settings
    print('Django imported successfully')
    print('Settings:', settings.SECRET_KEY[:10] + '...' if hasattr(settings, 'SECRET_KEY') else 'No SECRET_KEY')
except Exception as e:
    print('Django import error:', e)
" >> /tmp/customer_cleanup_log.txt 2>&1

# Now run the actual cleanup
python manage.py shell << 'EOF' >> /tmp/customer_cleanup_log.txt 2>&1
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

print("=== Starting cleanup process ===")

try:
    # Calculate date one year ago
    one_year_ago = timezone.now() - timedelta(days=365)
    print(f"One year ago: {one_year_ago}")
    
    # Method 1: Using subquery (most efficient)
    from django.db.models import Exists, OuterRef
    
    recent_orders = Order.objects.filter(
        customer=OuterRef('pk'),
        order_date__gte=one_year_ago
    )
    
    inactive_customers = Customer.objects.annotate(
        has_recent_order=Exists(recent_orders)
    ).filter(has_recent_order=False)
    
    deleted_count = inactive_customers.count()
    print(f"Found {deleted_count} inactive customers to delete")
    
    if deleted_count > 0:
        inactive_customers.delete()
        print(f"SUCCESS: Deleted {deleted_count} inactive customers")
    else:
        print("SUCCESS: No inactive customers found")
    
    print(f"DELETED:{deleted_count}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("DELETED:0")
EOF

echo "$(date): Cleanup job completed" >> /tmp/customer_cleanup_log.txt