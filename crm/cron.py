import datetime
import requests

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_line = f"{now} CRM is alive\n"
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(log_line)
    # Optionally check GraphQL hello field
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': '{ hello }'}
        )
        if response.status_code == 200:
            pass  # Could log success/failure if desired
    except Exception:
        pass

def update_low_stock():
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = '/tmp/low_stock_updates_log.txt'
        mutation = '''
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    name
                    stock
                }
                message
            }
        }
        '''
        try:
                response = requests.post(
                        'http://localhost:8000/graphql',
                        json={'query': mutation}
                )
                if response.status_code == 200:
                        data = response.json()
                        updates = data.get('data', {}).get('updateLowStockProducts', {})
                        products = updates.get('updatedProducts', [])
                        with open(log_file, 'a') as f:
                                for product in products:
                                        f.write(f"{now} Updated: {product['name']} New stock: {product['stock']}\n")
                else:
                        with open(log_file, 'a') as f:
                                f.write(f"{now} Error: Could not reach GraphQL endpoint\n")
        except Exception as e:
                with open(log_file, 'a') as f:
                        f.write(f"{now} Exception: {e}\n")
