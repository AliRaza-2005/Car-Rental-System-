import csv
import os
import random
import datetime

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_PATH, 'users.csv')
VEHICLES_FILE = os.path.join(BASE_PATH, 'vehicles.csv')
RESERVATIONS_FILE = os.path.join(BASE_PATH, 'reservations.csv')
RENTALS_FILE = os.path.join(BASE_PATH, 'rentals.csv')
INVOICES_FILE = os.path.join(BASE_PATH, 'invoices.csv')
MAINTENANCE_FILE = os.path.join(BASE_PATH, 'maintenance.csv')

CATEGORIES = ['Economy', 'Sedan', 'SUV', 'Luxury']
COUPONS = {'SAVE10': 0.10, 'STUDENT5': 0.05, 'WEEKEND15': 0.15}

current_user = None


def ensure_files():
    files = [
        (USERS_FILE, ['id', 'role', 'username', 'password', 'name', 'email', 'phone', 'license', 'blacklisted']),
        (VEHICLES_FILE, ['id', 'category', 'brand', 'model', 'year', 'rate', 'status', 'mileage', 'license_plate', 'insurance']),
        (RESERVATIONS_FILE, ['id', 'customer_id', 'vehicle_id', 'start_date', 'end_date', 'status', 'total_amount']),
        (RENTALS_FILE, ['id', 'reservation_id', 'customer_id', 'vehicle_id', 'start_date', 'due_date', 'return_date', 'status', 'total_amount', 'late_fee', 'damage_fee', 'fuel_fee']),
        (INVOICES_FILE, ['id', 'rental_id', 'customer_id', 'amount', 'discount', 'deposit', 'paid', 'status', 'date']),
        (MAINTENANCE_FILE, ['id', 'vehicle_id', 'date', 'type', 'details', 'status', 'cost', 'insurance_info']),
    ]
    for path, headers in files:
        if not os.path.exists(path):
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
    create_default_accounts()


def create_default_accounts():
    users = read_csv(USERS_FILE)
    roles = {u['role'] for u in users}
    if 'admin' not in roles:
        add_csv_row(USERS_FILE, {
            'id': '1',
            'role': 'admin',
            'username': 'admin',
            'password': 'admin123',
            'name': 'Admin',
            'email': 'admin@rentals.com',
            'phone': '0000000000',
            'license': '',
            'blacklisted': 'False'
        })
    if 'employee' not in roles:
        add_csv_row(USERS_FILE, {
            'id': '2',
            'role': 'employee',
            'username': 'employee',
            'password': 'emp123',
            'name': 'Employee',
            'email': 'employee@rentals.com',
            'phone': '1111111111',
            'license': '',
            'blacklisted': 'False'
        })


def read_csv(path):
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def write_csv(path, rows, fieldnames):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_csv_row(path, row):
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)


def generate_id(path):
    rows = read_csv(path)
    return str(len(rows) + 1)


def print_line():
    print('-' * 50)


def pause():
    input('Press Enter to continue...')


def find_user(username, password=None):
    users = read_csv(USERS_FILE)
    for user in users:
        if user['username'] == username and (password is None or user['password'] == password):
            return user
    return None


def register_customer():
    print_line()
    print('Register New Customer')
    username = input('Username: ').strip()
    if find_user(username):
        print('Username already exists.')
        return
    password = input('Password: ').strip()
    name = input('Full name: ').strip()
    email = input('Email: ').strip()
    phone = input('Phone: ').strip()
    license_number = input('Driving license number: ').strip()
    customer_id = generate_id(USERS_FILE)
    add_csv_row(USERS_FILE, {
        'id': customer_id,
        'role': 'customer',
        'username': username,
        'password': password,
        'name': name,
        'email': email,
        'phone': phone,
        'license': license_number,
        'blacklisted': 'False'
    })
    print('Customer registered successfully. Your customer ID is', customer_id)


def customer_login():
    print_line()
    print('Customer Login')
    username = input('Username: ').strip()
    password = input('Password: ').strip()
    user = find_user(username, password)
    if user and user['role'] == 'customer':
        if user['blacklisted'] == 'True':
            print('Your account is blacklisted. Contact admin.')
            return None
        print('Login successful. Welcome', user['name'])
        return user
    print('Invalid customer credentials.')
    return None


def forgot_password():
    print_line()
    print('Forgot Password')
    username = input('Enter your username: ').strip()
    user = find_user(username)
    if not user:
        print('No such user found.')
        return
    email = input('Enter your registered email: ').strip()
    if email != user['email']:
        print('Email does not match.')
        return
    new_password = input('Enter new password: ').strip()
    rows = read_csv(USERS_FILE)
    for row in rows:
        if row['username'] == username:
            row['password'] = new_password
    write_csv(USERS_FILE, rows, rows[0].keys())
    print('Password updated successfully.')


def login_role(role_name):
    print_line()
    print(role_name.capitalize(), 'Login')
    username = input('Username: ').strip()
    password = input('Password: ').strip()
    user = find_user(username, password)
    if user and user['role'] == role_name:
        print(f'{role_name.capitalize()} login successful. Welcome', user['name'])
        return user
    print('Invalid credentials for', role_name)
    return None


def get_vehicles():
    return read_csv(VEHICLES_FILE)


def save_vehicles(vehicles):
    if vehicles:
        write_csv(VEHICLES_FILE, vehicles, vehicles[0].keys())
    else:
        write_csv(VEHICLES_FILE, [], ['id', 'category', 'brand', 'model', 'year', 'rate', 'status', 'mileage', 'license_plate', 'insurance'])


def add_vehicle():
    print_line()
    print('Add Vehicle')
    category = input('Category (Economy, Sedan, SUV, Luxury): ').strip().title()
    if category not in CATEGORIES:
        print('Invalid category.')
        return
    brand = input('Brand: ').strip()
    model = input('Model: ').strip()
    year = input('Year: ').strip()
    rate = input('Daily rate: ').strip()
    mileage = input('Mileage: ').strip()
    license_plate = input('License plate: ').strip()
    insurance = input('Insurance details: ').strip()
    vehicle_id = generate_id(VEHICLES_FILE)
    add_csv_row(VEHICLES_FILE, {
        'id': vehicle_id,
        'category': category,
        'brand': brand,
        'model': model,
        'year': year,
        'rate': rate,
        'status': 'Available',
        'mileage': mileage,
        'license_plate': license_plate,
        'insurance': insurance
    })
    print('Vehicle added with ID', vehicle_id)


def update_vehicle():
    print_line()
    print('Update Vehicle')
    vid = input('Vehicle ID: ').strip()
    vehicles = get_vehicles()
    for v in vehicles:
        if v['id'] == vid:
            print('Current info:', v)
            v['brand'] = input('Brand [{}]: '.format(v['brand'])).strip() or v['brand']
            v['model'] = input('Model [{}]: '.format(v['model'])).strip() or v['model']
            v['year'] = input('Year [{}]: '.format(v['year'])).strip() or v['year']
            v['rate'] = input('Daily rate [{}]: '.format(v['rate'])).strip() or v['rate']
            v['status'] = input('Status [{}]: '.format(v['status'])).strip().title() or v['status']
            v['mileage'] = input('Mileage [{}]: '.format(v['mileage'])).strip() or v['mileage']
            v['insurance'] = input('Insurance [{}]: '.format(v['insurance'])).strip() or v['insurance']
            save_vehicles(vehicles)
            print('Vehicle updated.')
            return
    print('Vehicle not found.')


def delete_vehicle():
    print_line()
    print('Delete Vehicle')
    vid = input('Vehicle ID: ').strip()
    vehicles = get_vehicles()
    new_list = [v for v in vehicles if v['id'] != vid]
    if len(new_list) == len(vehicles):
        print('Vehicle not found.')
        return
    save_vehicles(new_list)
    print('Vehicle deleted.')


def search_vehicle():
    print_line()
    print('Search Vehicle')
    keyword = input('Search by brand, model or category: ').strip().lower()
    vehicles = get_vehicles()
    matches = [v for v in vehicles if keyword in v['brand'].lower() or keyword in v['model'].lower() or keyword in v['category'].lower()]
    if not matches:
        print('No vehicles found.')
        return
    for v in matches:
        print(v)


def list_vehicles_by_status(status):
    vehicles = get_vehicles()
    found = [v for v in vehicles if v['status'] == status]
    for v in found:
        print(v)
    if not found:
        print('No vehicles with status', status)


def verify_license():
    print_line()
    print('Verify Driving License')
    cid = input('Customer ID: ').strip()
    users = read_csv(USERS_FILE)
    for u in users:
        if u['id'] == cid and u['role'] == 'customer':
            if not u['license']:
                print('No license on file.')
                return
            print('License number:', u['license'])
            print('License status: Verified')
            return
    print('Customer not found.')


def customer_profile(user):
    print_line()
    print('Customer Profile')
    print('Name:', user['name'])
    print('Email:', user['email'])
    print('Phone:', user['phone'])
    print('License:', user['license'])
    print('Blacklisted:', user['blacklisted'])


def update_customer():
    print_line()
    print('Update Customer Record')
    cid = input('Customer ID: ').strip()
    users = read_csv(USERS_FILE)
    for u in users:
        if u['id'] == cid and u['role'] == 'customer':
            u['name'] = input('Name [{}]: '.format(u['name'])).strip() or u['name']
            u['email'] = input('Email [{}]: '.format(u['email'])).strip() or u['email']
            u['phone'] = input('Phone [{}]: '.format(u['phone'])).strip() or u['phone']
            u['license'] = input('License [{}]: '.format(u['license'])).strip() or u['license']
            write_csv(USERS_FILE, users, users[0].keys())
            print('Customer updated.')
            return
    print('Customer not found.')


def blacklist_customer():
    print_line()
    print('Blacklist Customer')
    cid = input('Customer ID: ').strip()
    users = read_csv(USERS_FILE)
    for u in users:
        if u['id'] == cid and u['role'] == 'customer':
            u['blacklisted'] = 'True'
            write_csv(USERS_FILE, users, users[0].keys())
            print('Customer blacklisted.')
            return
    print('Customer not found.')


def get_reservations():
    return read_csv(RESERVATIONS_FILE)


def save_reservations(rows):
    if rows:
        write_csv(RESERVATIONS_FILE, rows, rows[0].keys())
    else:
        write_csv(RESERVATIONS_FILE, [], ['id', 'customer_id', 'vehicle_id', 'start_date', 'end_date', 'status', 'total_amount'])


def book_vehicle(user):
    print_line()
    print('Book Vehicle')
    available = [v for v in get_vehicles() if v['status'] == 'Available']
    if not available:
        print('No available vehicles.')
        return
    for v in available:
        print(v)
    vid = input('Vehicle ID to reserve: ').strip()
    vehicle = next((v for v in available if v['id'] == vid), None)
    if not vehicle:
        print('Vehicle not available.')
        return
    start = input('Start date (YYYY-MM-DD): ').strip()
    end = input('End date (YYYY-MM-DD): ').strip()
    try:
        d1 = datetime.datetime.strptime(start, '%Y-%m-%d')
        d2 = datetime.datetime.strptime(end, '%Y-%m-%d')
        days = max((d2 - d1).days, 1)
    except ValueError:
        print('Invalid date format.')
        return
    total = float(vehicle['rate']) * days
    reserve_id = generate_id(RESERVATIONS_FILE)
    add_csv_row(RESERVATIONS_FILE, {
        'id': reserve_id,
        'customer_id': user['id'],
        'vehicle_id': vehicle['id'],
        'start_date': start,
        'end_date': end,
        'status': 'Reserved',
        'total_amount': str(total)
    })
    vehicles = get_vehicles()
    for v in vehicles:
        if v['id'] == vehicle['id']:
            v['status'] = 'Reserved'
    save_vehicles(vehicles)
    print('Reservation created with ID', reserve_id, 'Total:', total)


def cancel_reservation(user):
    print_line()
    print('Cancel Reservation')
    rid = input('Reservation ID: ').strip()
    reservations = get_reservations()
    for r in reservations:
        if r['id'] == rid and r['customer_id'] == user['id']:
            if r['status'] != 'Reserved':
                print('Cannot cancel reservation in status', r['status'])
                return
            r['status'] = 'Cancelled'
            save_reservations(reservations)
            vehicles = get_vehicles()
            for v in vehicles:
                if v['id'] == r['vehicle_id']:
                    v['status'] = 'Available'
            save_vehicles(vehicles)
            print('Reservation cancelled.')
            return
    print('Reservation not found.')


def modify_reservation(user):
    print_line()
    print('Modify Reservation')
    rid = input('Reservation ID: ').strip()
    reservations = get_reservations()
    for r in reservations:
        if r['id'] == rid and r['customer_id'] == user['id'] and r['status'] == 'Reserved':
            new_end = input('New end date (YYYY-MM-DD) [{}]: '.format(r['end_date'])).strip() or r['end_date']
            try:
                d1 = datetime.datetime.strptime(r['start_date'], '%Y-%m-%d')
                d2 = datetime.datetime.strptime(new_end, '%Y-%m-%d')
                days = max((d2 - d1).days, 1)
            except ValueError:
                print('Invalid date format.')
                return
            vehicle = next((v for v in get_vehicles() if v['id'] == r['vehicle_id']), None)
            if not vehicle:
                print('Vehicle missing.')
                return
            r['end_date'] = new_end
            r['total_amount'] = str(float(vehicle['rate']) * days)
            save_reservations(reservations)
            print('Reservation updated.')
            return
    print('Reservation not found or cannot modify.')


def reservation_history(user):
    print_line()
    print('Reservation History')
    reservations = [r for r in get_reservations() if r['customer_id'] == user['id']]
    if not reservations:
        print('No reservation history.')
        return
    for r in reservations:
        print(r)


def upcoming_reservations():
    print_line()
    print('Upcoming Reservations')
    today = datetime.date.today()
    reservations = get_reservations()
    for r in reservations:
        if r['status'] == 'Reserved':
            start = datetime.datetime.strptime(r['start_date'], '%Y-%m-%d').date()
            if start >= today:
                print(r)


def get_rentals():
    return read_csv(RENTALS_FILE)


def save_rentals(rows):
    if rows:
        write_csv(RENTALS_FILE, rows, rows[0].keys())
    else:
        write_csv(RENTALS_FILE, [], ['id', 'reservation_id', 'customer_id', 'vehicle_id', 'start_date', 'due_date', 'return_date', 'status', 'total_amount', 'late_fee', 'damage_fee', 'fuel_fee'])


def start_rental():
    print_line()
    print('Start Rental')
    reservations = [r for r in get_reservations() if r['status'] == 'Reserved']
    if not reservations:
        print('No reserved vehicles ready for rental.')
        return
    for r in reservations:
        print(r)
    rid = input('Reservation ID to start rental: ').strip()
    reservation = next((r for r in reservations if r['id'] == rid), None)
    if not reservation:
        print('Reservation not found.')
        return
    vehicle = next((v for v in get_vehicles() if v['id'] == reservation['vehicle_id']), None)
    if not vehicle:
        print('Vehicle record missing.')
        return
    due_date = reservation['end_date']
    rental_id = generate_id(RENTALS_FILE)
    add_csv_row(RENTALS_FILE, {
        'id': rental_id,
        'reservation_id': reservation['id'],
        'customer_id': reservation['customer_id'],
        'vehicle_id': reservation['vehicle_id'],
        'start_date': reservation['start_date'],
        'due_date': due_date,
        'return_date': '',
        'status': 'Active',
        'total_amount': reservation['total_amount'],
        'late_fee': '0',
        'damage_fee': '0',
        'fuel_fee': '0'
    })
    reservation['status'] = 'Completed'
    save_reservations(get_reservations())
    vehicles = get_vehicles()
    for v in vehicles:
        if v['id'] == vehicle['id']:
            v['status'] = 'Rented'
    save_vehicles(vehicles)
    print('Rental started with ID', rental_id)


def return_vehicle():
    print_line()
    print('Return Vehicle')
    rentals = [r for r in get_rentals() if r['status'] == 'Active']
    if not rentals:
        print('No active rentals.')
        return
    for r in rentals:
        print(r)
    rid = input('Rental ID: ').strip()
    rental = next((r for r in rentals if r['id'] == rid), None)
    if not rental:
        print('Rental not found.')
        return
    return_date = input('Return date (YYYY-MM-DD): ').strip()
    try:
        due = datetime.datetime.strptime(rental['due_date'], '%Y-%m-%d')
        ret = datetime.datetime.strptime(return_date, '%Y-%m-%d')
        late_days = max((ret - due).days, 0)
    except ValueError:
        print('Invalid date format.')
        return
    damage_fee = float(input('Damage fee if any: ').strip() or '0')
    fuel_fee = float(input('Fuel fee if any: ').strip() or '0')
    late_fee = late_days * 20
    rental['return_date'] = return_date
    rental['status'] = 'Returned'
    rental['late_fee'] = str(late_fee)
    rental['damage_fee'] = str(damage_fee)
    rental['fuel_fee'] = str(fuel_fee)
    save_rentals(get_rentals())
    vehicles = get_vehicles()
    for v in vehicles:
        if v['id'] == rental['vehicle_id']:
            v['status'] = 'Available'
    save_vehicles(vehicles)
    amount = float(rental['total_amount']) + late_fee + damage_fee + fuel_fee
    invoice_id = generate_id(INVOICES_FILE)
    add_csv_row(INVOICES_FILE, {
        'id': invoice_id,
        'rental_id': rental['id'],
        'customer_id': rental['customer_id'],
        'amount': str(amount),
        'discount': '0',
        'deposit': '0',
        'paid': 'False',
        'status': 'Pending',
        'date': return_date
    })
    print('Vehicle returned. Invoice created with amount:', amount)


def extend_rental():
    print_line()
    print('Extend Rental')
    rentals = [r for r in get_rentals() if r['status'] == 'Active']
    if not rentals:
        print('No active rentals.')
        return
    for r in rentals:
        print(r)
    rid = input('Rental ID: ').strip()
    rental = next((r for r in rentals if r['id'] == rid), None)
    if not rental:
        print('Rental not found.')
        return
    new_due = input('New due date (YYYY-MM-DD): ').strip()
    try:
        datetime.datetime.strptime(new_due, '%Y-%m-%d')
    except ValueError:
        print('Invalid date format.')
        return
    rental['due_date'] = new_due
    save_rentals(get_rentals())
    print('Rental extended to', new_due)


def active_rentals():
    print_line()
    print('Active Rentals')
    rentals = [r for r in get_rentals() if r['status'] == 'Active']
    for r in rentals:
        print(r)
    if not rentals:
        print('No active rentals.')


def rental_history():
    print_line()
    print('Rental History')
    rentals = read_csv(RENTALS_FILE)
    for r in rentals:
        if r['status'] in ('Returned', 'Completed'):
            print(r)
    if not rentals:
        print('No rental records.')


def calculate_bill():
    print_line()
    print('Calculate Bill')
    invoice_id = input('Invoice ID: ').strip()
    invoices = read_csv(INVOICES_FILE)
    for i in invoices:
        if i['id'] == invoice_id:
            amount = float(i['amount'])
            coupon = input('Coupon code (optional): ').strip().upper()
            discount = COUPONS.get(coupon, 0)
            discounted_amount = amount * (1 - discount)
            deposit = float(input('Security deposit: ').strip() or '0')
            total = discounted_amount + deposit
            i['discount'] = str(discount)
            i['deposit'] = str(deposit)
            i['amount'] = str(total)
            i['status'] = 'Ready'
            write_csv(INVOICES_FILE, invoices, invoices[0].keys())
            print('Bill calculated. Total amount:', total)
            return
    print('Invoice not found.')


def generate_invoice():
    print_line()
    print('Generate Invoice')
    invoices = read_csv(INVOICES_FILE)
    for i in invoices:
        if i['status'] == 'Ready':
            i['paid'] = 'True'
            i['status'] = 'Paid'
            print('Invoice', i['id'], 'for amount', i['amount'], 'generated.')
    write_csv(INVOICES_FILE, invoices, invoices[0].keys())


def service_schedule():
    print_line()
    print('Service Schedule')
    vid = input('Vehicle ID: ').strip()
    date = input('Service date (YYYY-MM-DD): ').strip()
    details = input('Service details: ').strip()
    cost = input('Estimated cost: ').strip()
    mid = generate_id(MAINTENANCE_FILE)
    add_csv_row(MAINTENANCE_FILE, {
        'id': mid,
        'vehicle_id': vid,
        'date': date,
        'type': 'Service',
        'details': details,
        'status': 'Scheduled',
        'cost': cost,
        'insurance_info': ''
    })
    print('Service record added with ID', mid)


def maintenance_records():
    print_line()
    print('Maintenance Records')
    records = read_csv(MAINTENANCE_FILE)
    for r in records:
        print(r)
    if not records:
        print('No maintenance records.')


def accident_report():
    print_line()
    print('Accident Report')
    vid = input('Vehicle ID: ').strip()
    date = input('Date (YYYY-MM-DD): ').strip()
    details = input('Accident details: ').strip()
    cost = input('Repair cost: ').strip()
    mid = generate_id(MAINTENANCE_FILE)
    add_csv_row(MAINTENANCE_FILE, {
        'id': mid,
        'vehicle_id': vid,
        'date': date,
        'type': 'Accident',
        'details': details,
        'status': 'Reported',
        'cost': cost,
        'insurance_info': ''
    })
    print('Accident record created with ID', mid)


def insurance_details():
    print_line()
    print('Insurance Details')
    vid = input('Vehicle ID: ').strip()
    vehicles = get_vehicles()
    vehicle = next((v for v in vehicles if v['id'] == vid), None)
    if vehicle:
        print('Insurance:', vehicle['insurance'])
    else:
        print('Vehicle not found.')


def revenue_report():
    print_line()
    print('Revenue Report')
    invoices = [i for i in read_csv(INVOICES_FILE) if i['status'] == 'Paid']
    total = sum(float(i['amount']) for i in invoices)
    print('Total revenue from paid invoices:', total)


def monthly_report():
    print_line()
    print('Monthly Report')
    month = input('Month number (1-12): ').strip()
    invoices = read_csv(INVOICES_FILE)
    selected = [i for i in invoices if i['date'].startswith(f'2024-{int(month):02d}') or i['date'].startswith(f'2025-{int(month):02d}')]
    total = sum(float(i['amount']) for i in selected)
    print('Revenue for month', month, ':', total)


def most_rented_cars():
    print_line()
    print('Most Rented Cars')
    rentals = read_csv(RENTALS_FILE)
    counts = {}
    for r in rentals:
        vid = r['vehicle_id']
        counts[vid] = counts.get(vid, 0) + 1
    for vid, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        vehicle = next((v for v in get_vehicles() if v['id'] == vid), None)
        print(vid, count, vehicle['brand'] if vehicle else '')


def active_customers():
    print_line()
    print('Active Customers')
    rentals = [r for r in read_csv(RENTALS_FILE) if r['status'] == 'Active']
    ids = {r['customer_id'] for r in rentals}
    for cid in ids:
        user = next((u for u in read_csv(USERS_FILE) if u['id'] == cid), None)
        if user:
            print(user['id'], user['name'])


def fleet_utilization():
    print_line()
    print('Fleet Utilization')
    vehicles = get_vehicles()
    total = len(vehicles)
    if total == 0:
        print('No vehicles in fleet.')
        return
    counts = {status: len([v for v in vehicles if v['status'] == status]) for status in ['Available', 'Reserved', 'Rented', 'Maintenance']}
    print('Total vehicles:', total)
    for status, count in counts.items():
        print(status + ':', count)


def available_inventory():
    print_line()
    print('Available Inventory')
    list_vehicles_by_status('Available')


def admin_menu():
    while True:
        print_line()
        print('Admin Menu')
        print('1. Vehicle Management')
        print('2. Customer Management')
        print('3. Reservation System')
        print('4. Rental System')
        print('5. Billing & Payments')
        print('6. Maintenance')
        print('7. Reports & Analytics')
        print('8. Logout')
        choice = input('Choose option: ').strip()
        if choice == '1':
            vehicle_management_menu()
        elif choice == '2':
            customer_management_menu()
        elif choice == '3':
            reservation_menu_admin()
        elif choice == '4':
            rental_menu()
        elif choice == '5':
            billing_menu()
        elif choice == '6':
            maintenance_menu()
        elif choice == '7':
            reports_menu()
        elif choice == '8':
            break
        else:
            print('Invalid option.')


def employee_menu():
    while True:
        print_line()
        print('Employee Menu')
        print('1. Vehicle Management')
        print('2. Reservation System')
        print('3. Rental System')
        print('4. Billing & Payments')
        print('5. Maintenance')
        print('6. Logout')
        choice = input('Choose option: ').strip()
        if choice == '1':
            vehicle_management_menu()
        elif choice == '2':
            reservation_menu_admin()
        elif choice == '3':
            rental_menu()
        elif choice == '4':
            billing_menu()
        elif choice == '5':
            maintenance_menu()
        elif choice == '6':
            break
        else:
            print('Invalid option.')


def customer_menu(user):
    while True:
        print_line()
        print('Customer Menu')
        print('1. Book Vehicle')
        print('2. Cancel Reservation')
        print('3. Modify Reservation')
        print('4. Upcoming Reservations')
        print('5. Reservation History')
        print('6. Start Rental')
        print('7. Return Vehicle')
        print('8. Extend Rental')
        print('9. Active Rentals')
        print('10. Rental History')
        print('11. Customer Profile')
        print('12. Logout')
        choice = input('Choose option: ').strip()
        if choice == '1':
            book_vehicle(user)
        elif choice == '2':
            cancel_reservation(user)
        elif choice == '3':
            modify_reservation(user)
        elif choice == '4':
            upcoming_reservations()
        elif choice == '5':
            reservation_history(user)
        elif choice == '6':
            start_rental()
        elif choice == '7':
            return_vehicle()
        elif choice == '8':
            extend_rental()
        elif choice == '9':
            active_rentals()
        elif choice == '10':
            rental_history()
        elif choice == '11':
            customer_profile(user)
        elif choice == '12':
            break
        else:
            print('Invalid option.')


def vehicle_management_menu():
    while True:
        print_line()
        print('Vehicle Management')
        print('1. Add Vehicle')
        print('2. Update Vehicle')
        print('3. Delete Vehicle')
        print('4. Search Vehicle')
        print('5. Available Vehicles')
        print('6. Reserved Vehicles')
        print('7. Rented Vehicles')
        print('8. Maintenance Vehicles')
        print('9. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            add_vehicle()
        elif choice == '2':
            update_vehicle()
        elif choice == '3':
            delete_vehicle()
        elif choice == '4':
            search_vehicle()
        elif choice == '5':
            list_vehicles_by_status('Available')
        elif choice == '6':
            list_vehicles_by_status('Reserved')
        elif choice == '7':
            list_vehicles_by_status('Rented')
        elif choice == '8':
            list_vehicles_by_status('Maintenance')
        elif choice == '9':
            break
        else:
            print('Invalid option.')


def customer_management_menu():
    while True:
        print_line()
        print('Customer Management')
        print('1. Register Customer')
        print('2. Verify Driving License')
        print('3. Update Customer')
        print('4. Blacklist Customer')
        print('5. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            register_customer()
        elif choice == '2':
            verify_license()
        elif choice == '3':
            update_customer()
        elif choice == '4':
            blacklist_customer()
        elif choice == '5':
            break
        else:
            print('Invalid option.')


def reservation_menu_admin():
    while True:
        print_line()
        print('Reservation System')
        print('1. Book Vehicle')
        print('2. Cancel Reservation')
        print('3. Modify Reservation')
        print('4. Upcoming Reservations')
        print('5. Reservation History')
        print('6. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            customer = login_customer_for_action()
            if customer:
                book_vehicle(customer)
        elif choice == '2':
            customer = login_customer_for_action()
            if customer:
                cancel_reservation(customer)
        elif choice == '3':
            customer = login_customer_for_action()
            if customer:
                modify_reservation(customer)
        elif choice == '4':
            upcoming_reservations()
        elif choice == '5':
            reservation_history_menu()
        elif choice == '6':
            break
        else:
            print('Invalid option.')


def login_customer_for_action():
    username = input('Customer username: ').strip()
    user = find_user(username)
    if user and user['role'] == 'customer':
        return user
    print('Customer not found.')
    return None


def reservation_history_menu():
    customers = [u for u in read_csv(USERS_FILE) if u['role'] == 'customer']
    for c in customers:
        print(c['id'], c['name'], c['username'])
    cid = input('Customer ID for history: ').strip()
    user = next((u for u in customers if u['id'] == cid), None)
    if user:
        reservation_history(user)
    else:
        print('Customer not found.')


def rental_menu():
    while True:
        print_line()
        print('Rental System')
        print('1. Start Rental')
        print('2. Return Vehicle')
        print('3. Extend Rental')
        print('4. Active Rentals')
        print('5. Rental History')
        print('6. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            start_rental()
        elif choice == '2':
            return_vehicle()
        elif choice == '3':
            extend_rental()
        elif choice == '4':
            active_rentals()
        elif choice == '5':
            rental_history()
        elif choice == '6':
            break
        else:
            print('Invalid option.')


def billing_menu():
    while True:
        print_line()
        print('Billing & Payments')
        print('1. Calculate Bill')
        print('2. Generate Invoice')
        print('3. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            calculate_bill()
        elif choice == '2':
            generate_invoice()
        elif choice == '3':
            break
        else:
            print('Invalid option.')


def maintenance_menu():
    while True:
        print_line()
        print('Vehicle Maintenance')
        print('1. Service Schedule')
        print('2. Maintenance Records')
        print('3. Accident Reports')
        print('4. Insurance Details')
        print('5. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            service_schedule()
        elif choice == '2':
            maintenance_records()
        elif choice == '3':
            accident_report()
        elif choice == '4':
            insurance_details()
        elif choice == '5':
            break
        else:
            print('Invalid option.')


def reports_menu():
    while True:
        print_line()
        print('Reports & Analytics')
        print('1. Revenue Report')
        print('2. Monthly Report')
        print('3. Most Rented Cars')
        print('4. Active Customers')
        print('5. Fleet Utilization')
        print('6. Available Inventory')
        print('7. Back')
        choice = input('Choose option: ').strip()
        if choice == '1':
            revenue_report()
        elif choice == '2':
            monthly_report()
        elif choice == '3':
            most_rented_cars()
        elif choice == '4':
            active_customers()
        elif choice == '5':
            fleet_utilization()
        elif choice == '6':
            available_inventory()
        elif choice == '7':
            break
        else:
            print('Invalid option.')


def main_menu():
    ensure_files()
    while True:
        print_line()
        print('Car Rental Management System')
        print('1. Admin Login')
        print('2. Employee Login')
        print('3. Customer Registration')
        print('4. Customer Login')
        print('5. Forgot Password')
        print('6. Exit')
        choice = input('Select option: ').strip()
        if choice == '1':
            user = login_role('admin')
            if user:
                admin_menu()
        elif choice == '2':
            user = login_role('employee')
            if user:
                employee_menu()
        elif choice == '3':
            register_customer()
        elif choice == '4':
            user = customer_login()
            if user:
                customer_menu(user)
        elif choice == '5':
            forgot_password()
        elif choice == '6':
            print('Goodbye!')
            break
        else:
            print('Invalid choice.')


if __name__ == '__main__':
    main_menu()
