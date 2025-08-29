from celery import shared_task
from datetime import datetime
import requests
import json
from django.conf import settings

@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file_path = "/tmp/crm_report_log.txt"
        
        # GraphQL query to fetch CRM statistics
        query = """
        query {
            totalCustomers
            totalOrders
            totalRevenue
            recentOrders(limit: 5) {
                id
                totalAmount
                orderDate
                customer {
                    name
                    email
                }
            }
        }
        """
        
        # Alternative query if the above fields don't exist
        alternative_query = """
        query {
            customers {
                totalCount
            }
            orders {
                totalCount
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """
        
        url = "http://localhost:8000/graphql"
        
        # Try the main query first
        try:
            payload = {"query": query}
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'errors' in result:
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            data = result.get('data', {})
            
            total_customers = data.get('totalCustomers', 0)
            total_orders = data.get('totalOrders', 0)
            total_revenue = data.get('totalRevenue', 0)
            
            # If main query fields don't exist, try alternative approach
            if total_customers == 0 and total_orders == 0 and total_revenue == 0:
                payload = {"query": alternative_query}
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                data = result.get('data', {})
                
                total_customers = data.get('customers', {}).get('totalCount', 0)
                total_orders = data.get('orders', {}).get('totalCount', 0)
                
                # Calculate total revenue from orders
                orders = data.get('orders', {}).get('edges', [])
                total_revenue = sum(
                    float(order.get('node', {}).get('totalAmount', 0)) 
                    for order in orders
                )
            
        except Exception as e:
            # Fallback: Use Django ORM directly if GraphQL fails
            from django.db.models import Sum
            from crm.models import Customer, Order
            
            total_customers = Customer.objects.count()
            total_orders = Order.objects.count()
            total_revenue = Order.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            # Log that we used fallback method
            fallback_note = " (using ORM fallback)"
        else:
            fallback_note = ""
        
        # Format the report
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, ${total_revenue:.2f} revenue{fallback_note}\n"
        )
        
        # Add detailed information if available
        try:
            # Try to get recent orders for more details
            detail_query = """
            query {
                orders(limit: 3, orderBy: {orderDate: DESC}) {
                    id
                    totalAmount
                    orderDate
                    customer {
                        name
                    }
                }
            }
            """
            
            payload = {"query": detail_query}
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                orders = result.get('data', {}).get('orders', [])
                
                if orders:
                    report_message += "  Recent Orders:\n"
                    for order in orders:
                        report_message += (
                            f"    - {order['customer']['name']}: "
                            f"${order['totalAmount']} on {order['orderDate'][:10]}\n"
                        )
        except:
            pass  # Silently fail if detailed query doesn't work
        
        report_message += "-" * 60 + "\n"
        
        # Write to log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(report_message)
        
        return f"CRM report generated: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
        
    except Exception as e:
        error_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error generating CRM report: {str(e)}\n"
        error_log_path = "/tmp/crm_report_errors.log"
        
        with open(error_log_path, 'a') as error_file:
            error_file.write(error_message)
        
        return f"Error generating CRM report: {str(e)}"

@shared_task
def test_task():
    """Test task to verify Celery is working"""
    return "Celery is working correctly!"