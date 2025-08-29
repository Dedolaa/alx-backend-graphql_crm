#!/usr/bin/env python3
"""
Robust GraphQL script that handles server downtime gracefully.
"""

from gql import gql, Client
import requests
import json
from datetime import datetime, timedelta
import time
import os

def send_order_reminders_sync():
    """Synchronous version using requests library with retry logic"""
    
    # GraphQL endpoint
    url = "http://localhost:8000/graphql"
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    query_variations = [
        """
        query GetRecentOrders($since: DateTime!) {
            orders(filter: {orderDate: {gte: $since}}) {
                id
                customer {
                    email
                    name
                }
                orderDate
                totalAmount
            }
        }
        """,
        """
        query GetRecentOrders($since: DateTime!) {
            allOrders(filter: {orderDate: {gte: $since}}) {
                id
                customer {
                    email
                    name
                }
                orderDate
                totalAmount
            }
        }
        """,
        """
        query {
            __schema {
                types {
                    name
                    fields {
                        name
                    }
                }
            }
        }
        """
    ]
    
    headers = {
        "Content-Type": "application/json",
    }
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Try each query variation
            for i, query in enumerate(query_variations):
                try:
                    if "since" in query:
                        payload = {
                            "query": query,
                            "variables": {"since": seven_days_ago}
                        }
                    else:
                        payload = {"query": query}
                    
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Check for GraphQL errors
                    if 'errors' in result:
                        print(f"Query variation {i+1} failed with errors: {result['errors']}")
                        continue
                    
                    # Try to extract orders data
                    orders = []
                    data = result.get('data', {})
                    
                    if 'orders' in data:
                        orders = data['orders']
                    elif 'allOrders' in data:
                        orders = data['allOrders']
                    else:
                        # If we got schema info, let's see what's available
                        if 'types' in data.get('__schema', {}):
                            print("Available types:", [t['name'] for t in data['__schema']['types'] if t['name'].lower().find('order') != -1])
                        continue
                    
                    # Process orders if found
                    if orders:
                        log_message = f"{datetime.now()}: Processing {len(orders)} recent orders\n"
                        
                        for order in orders:
                            order_id = order.get('id', 'N/A')
                            customer_email = order.get('customer', {}).get('email', 'N/A')
                            customer_name = order.get('customer', {}).get('name', 'N/A')
                            order_date = order.get('orderDate', order.get('order_date', 'N/A'))
                            total_amount = order.get('totalAmount', order.get('total_amount', 'N/A'))
                            
                            log_message += f"  - Order {order_id}: {customer_name} ({customer_email}), Amount: ${total_amount}, Date: {order_date}\n"
                        
                        log_message += f"{datetime.now()}: Order reminders processed!\n"
                        
                        # Write to log file
                        with open("C:/temp/order_reminders_log.txt", 'a') as log_file:
                            log_file.write(log_message)
                        
                        # Print to console
                        print("Order reminders processed!")
                        return
                    
                except Exception as e:
                    print(f"Query variation {i+1} failed: {e}")
                    continue
            
            # If no query worked
            error_msg = f"{datetime.now()}: Could not find valid orders query or no orders found\n"
            with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                log_file.write(error_msg)
            print("No orders found or couldn't determine query structure")
            return
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"Connection failed. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                error_message = f"{datetime.now()}: Failed to connect to GraphQL server after {max_retries} attempts\n"
                with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                    log_file.write(error_message)
                print("Failed to connect to GraphQL server")
                return
        
        except requests.exceptions.RequestException as e:
            error_message = f"{datetime.now()}: Network error: {str(e)}\n"
            with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                log_file.write(error_message)
            print(f"Network error: {str(e)}")
            return
        
        except Exception as e:
            error_message = f"{datetime.now()}: Unexpected error: {str(e)}\n"
            with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                log_file.write(error_message)
            print(f"Unexpected error: {str(e)}")
            return

def main():
    """Main function"""
    send_order_reminders_sync()

if __name__ == "__main__":
    main()