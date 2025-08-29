"""
Cron jobs for the CRM application.
"""

from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client
import os
from datetime import datetime
import requests
import json
from django.conf import settings

def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM application health.
    """
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        message = f"{timestamp} CRM is alive"
        
        # Log to file
        log_file_path = "/tmp/crm_heartbeat_log.txt"
        
        # Append to log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(message + "\n")
        
        # Optional: Verify GraphQL endpoint is responsive
        try:
            # Try to query the GraphQL endpoint
            url = "http://localhost:8000/graphql"
            
            # Try different query variations
            queries_to_try = [
                {'query': '{ hello }'},
                {'query': '{ __schema { queryType { name } } }'},
                {'query': '{ __typename }'}
            ]
            
            for query in queries_to_try:
                try:
                    response = requests.post(url, json=query, timeout=5)
                    if response.status_code == 200:
                        # GraphQL endpoint is responsive
                        with open(log_file_path, 'a') as log_file:
                            log_file.write(f"{timestamp} GraphQL endpoint is responsive\n")
                        break
                except:
                    continue
            else:
                # If all queries failed
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"{timestamp} GraphQL endpoint check failed\n")
                    
        except Exception as e:
            # Log GraphQL check error but don't fail the heartbeat
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"{timestamp} GraphQL check error: {str(e)}\n")
        
        return f"Heartbeat logged: {message}"
        
    except Exception as e:
        # Fallback: log to a different location if main log fails
        error_log_path = "/tmp/crm_heartbeat_error.log"
        with open(error_log_path, 'a') as error_file:
            error_file.write(f"{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')} Heartbeat failed: {str(e)}\n")
        
        return f"Heartbeat failed: {str(e)}"


def update_low_stock():
    """
    Update low-stock products every 12 hours using GraphQL mutation.
    """
    try:
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        log_file_path = "/tmp/low_stock_updates_log.txt"
        
        # GraphQL mutation
        mutation = """
        mutation {
            updateLowStockProducts {
                success
                message
                updatedProducts {
                    id
                    name
                    stock
                    price
                }
            }
        }
        """
        
        # Execute the mutation
        url = "http://localhost:8000/graphql"
        payload = {"query": mutation}
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for GraphQL errors
        if 'errors' in result:
            error_message = f"{timestamp} GraphQL errors: {result['errors']}\n"
            with open(log_file_path, 'a') as log_file:
                log_file.write(error_message)
            return f"GraphQL errors: {result['errors']}"
        
        # Process the mutation result
        mutation_result = result.get('data', {}).get('updateLowStockProducts', {})
        
        success = mutation_result.get('success', False)
        message = mutation_result.get('message', 'No message')
        updated_products = mutation_result.get('updatedProducts', [])
        
        # Log the results
        log_message = f"{timestamp} Low Stock Update Results:\n"
        log_message += f"Success: {success}\n"
        log_message += f"Message: {message}\n"
        
        if updated_products:
            log_message += "Updated Products:\n"
            for product in updated_products:
                log_message += f"  - {product['name']}: Stock updated to {product['stock']} (Price: ${product['price']})\n"
        else:
            log_message += "No products were updated.\n"
        
        log_message += "-" * 50 + "\n"
        
        # Write to log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_message)
        
        return f"Low stock update completed: {message}"
        
    except requests.exceptions.ConnectionError:
        error_message = f"{timestamp} Failed to connect to GraphQL server\n"
        with open(log_file_path, 'a') as log_file:
            log_file.write(error_message)
        return "Failed to connect to GraphQL server"
        
    except requests.exceptions.RequestException as e:
        error_message = f"{timestamp} Network error: {str(e)}\n"
        with open(log_file_path, 'a') as log_file:
            log_file.write(error_message)
        return f"Network error: {str(e)}"
        
    except Exception as e:
        error_message = f"{timestamp} Unexpected error: {str(e)}\n"
        with open(log_file_path, 'a') as log_file:
            log_file.write(error_message)
        return f"Unexpected error: {str(e)}"
    