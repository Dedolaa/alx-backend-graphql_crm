from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Exists, OuterRef
from crm.models import Customer, Order

class Command(BaseCommand):
    help = 'Delete customers with no orders in the past year'

    def handle(self, *args, **options):
        one_year_ago = timezone.now() - timedelta(days=365)
        
        try:
            # Subquery to find customers with recent orders
            recent_orders = Order.objects.filter(
                customer=OuterRef('pk'),
                order_date__gte=one_year_ago
            )
            
            # Find inactive customers (no recent orders)
            inactive_customers = Customer.objects.annotate(
                has_recent_order=Exists(recent_orders)
            ).filter(has_recent_order=False)
            
            deleted_count = inactive_customers.count()
            inactive_customers.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} inactive customers')
            )
            return deleted_count
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
            return 0