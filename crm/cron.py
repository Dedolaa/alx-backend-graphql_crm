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

# Optional: Additional cron jobs can be added here
def another_cron_job():
    """Example of another cron job."""
    pass