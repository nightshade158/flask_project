import datetime
import random
from prettytable import PrettyTable
import mysql.connector as mysqlcon
from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'onlineretailstore'

#  generate a autentication of new customer in  online retain store using email and password and store it in database using command line interface and then use it in the code


connection = mysqlcon.connect(
    host="localhost",
    database="onlineretailstore",
    user="root",
    password="1234"
)

# Create a database connection
db = pymysql.connect(host="localhost", user="root", password="1234", db="onlineretailstore")
cursor = db.cursor()


# Function to generate a wallet ID based on the firstname
def get_wallet_id_by_firstname(firstname):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM wallet WHERE wname = %s", (firstname))
    result = cursor.fetchone()
    cursor.close()
    print("Wallet id fetched successfully.")
    if result:
        return result[0]
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if connection.is_connected():
        print('Connected to MySQL database')
        cursor = connection.cursor()
        cursor.execute('select * from Customer')
        row = cursor.fetchone()
        while row is not None:
            # print(row)
            row = cursor.fetchone()
        cursor.close()
    else:
        print('Connection failed')

    return render_template('index.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        cursor = connection.cursor()

        cursor.execute("SELECT MAX(customer_id) FROM customer")
        customer_id = cursor.fetchone()
        customer_id = customer_id[0] + 1

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        contact = request.form['contact']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        email = request.form['email']
        password = request.form['password']

        wallet_id = get_wallet_id_by_firstname(firstname)

        cursor.execute("INSERT INTO customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (customer_id, email, password, firstname, lastname, contact, dob, wallet_id))
        connection.commit()
        cursor.close()
        return redirect(f'customer_address/{customer_id}')
    return render_template('create_account.html')


@app.route('/add_wallet', methods=['GET', 'POST'])
def add_wallet():
    if request.method == 'POST':
        fname = request.form['fname']
        amount = request.form['amount']

        cursor = connection.cursor()
        cursor.execute("SELECT id FROM wallet ORDER BY id DESC LIMIT 1")
        wallet_id = cursor.fetchone()
        if wallet_id:
            wallet_id = wallet_id[0] + 1
        else:
            wallet_id = 1

        cursor.execute("INSERT INTO wallet VALUES (%s, %s, %s)", (wallet_id, fname, amount))
        connection.commit()
        cursor.close()

        print("Your wallet has been created")
        return redirect('create_account')

    return render_template('add_wallet.html')  # Create an HTML template for the form


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT customer_id FROM Customer WHERE email_id = %s AND password = %s", (email, password))
        customer = cursor.fetchone()

        if customer:
            return render_template('home.html', customer_id = customer[0])
        else:
            return render_template('login.html', error="Login failed")
    else:
        return render_template('login.html')


@app.route('/home')
def home():
    # Implement the home page logic here
    return render_template('home.html')


@app.route('/login_employee', methods=['GET', 'POST'])
def login_employee():
    if request.method == 'POST':
        cursor = connection.cursor()
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM Employee WHERE email_id = %s AND password = %s", (email, password))
        employee = cursor.fetchone()
        cursor.close()

        if employee:
            return render_template('employee_dashboard.html',first_name = employee[3])  # Replace with your logic for a successful login
        else:
            return "Login failed"  # Replace with your logic for a failed login

    return render_template('login_employee.html')


@app.route('/customer_address/<customer_id>', methods=['GET', 'POST'])
def add_customer_address(customer_id):
    if request.method == 'POST':
        house_no = request.form['house_no']
        locality = request.form['locality']
        city = request.form['city']
        pincode = request.form['pincode']
        print(customer_id)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO customer_address (customer_id, house_no, locality, city, pincode) VALUES (%s, %s, %s, %s, %s)",
            (customer_id, house_no, locality, city, pincode))
        connection.commit()
        cursor.close()

        print("Address added")

        return redirect('/')

    return render_template('add_customer_address.html', customer_id=customer_id)


@app.route('/add_newCustomer', methods=['GET', 'POST'])
def add_new_customer():
    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute("SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1")
        customer_id = cursor.fetchone()
        if customer_id:
            customer_id = customer_id[0] + 1
        else:
            customer_id = 1

        first_name = request.form['first_name']
        last_name = request.form['last_name']

        cursor.execute("SELECT email_id FROM Customer")
        list_email = cursor.fetchall()
        email = request.form['email']
        for i in list_email:
            if email == i[0]:
                print("Email id already registered")
                return render_template('email_already_registered.html')

        password = request.form['password']
        contact = request.form['contact']
        date_of_birth = request.form['date_of_birth']

        # Perform the wallet creation and address addition here (see notes below)

        # Assuming you have a separate route for wallet creation
        # wallet_id = create_wallet(first_name)  # Implement this function
        wallet_id = request.form['wallet_id']

        cursor.execute(
            "INSERT INTO Customer (customer_id, email_id, password, first_name, last_name, contact, date_of_birth, wallet_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (customer_id, email, password, first_name, last_name, contact, date_of_birth, wallet_id))
        connection.commit()

        # Print or render customer details
        customer_details = {
            "Customer id": customer_id,
            "First name": first_name,
            "Last name": last_name,
            "Email": email,
            "Contact": contact,
            "Date of birth": date_of_birth,
            "Wallet id": wallet_id
        }

        return render_template('customer_details.html', customer_details=customer_details)

    return render_template('add_new_customer.html')


@app.route('/view_order')
def view_order():
    cursor.execute("SELECT * FROM Order")  # You may need to use backticks for table names with special characters
    orders = cursor.fetchall()
    table_vorder = PrettyTable(["Order id", "Assigned delivery agent id", "Customer id", "Transaction id", "Date"])
    for order in orders:
        table_vorder.add_row([order[0], order[1], order[2], order[3], order[-1]])

    return render_template('view_order.html', table=table_vorder.get_html_string())


@app.route('/view_soldItems')
def view_soldItems():
    cursor.execute("SELECT * FROM Sold_Items")
    soldItems = cursor.fetchall()
    table_sold = PrettyTable(["Customer id", "Order id", "Product id", "Number of Items"])
    for si in soldItems:
        table_sold.add_row(si[0], si[1], si[2], si[-1])

    return render_template('view_soldItems.html', table=table_sold.get_html_string())


@app.route('/view_transactions')
def view_transactions():
    cursor.execute("SELECT * FROM Transactions")
    transactions = cursor.fetchall()
    table_transactions = PrettyTable(["Transaction id", "Wallet id", "Amount"])
    for tra in transactions:
        table_transactions.add_row(tra[0], tra[1], tra[2])

    return render_template('view_transactions.html', table=table_transactions.get_html_string())


@app.route('/see_cart/<customer_id>')
def see_cart(customer_id):
    cursor.execute("SELECT * FROM Cart WHERE customer_id = %s", (customer_id,))
    cart = cursor.fetchall()

    table_cart = PrettyTable(["Product id", "Name", "Price", "Number of Items", "Total Price"])
    if cart:
        for item in cart:
            product_id = item[1]
            no_of_items = item[2]
            cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            table_cart.add_row([product_id, product[1], product[2], no_of_items, product[2] * no_of_items])
    else:
        return "Cart is empty"

    return render_template('see_cart.html', table=table_cart.get_html_string())


@app.route('/add_to_cart/<customer_id>', methods=['GET', 'POST'])
def add_to_cart(customer_id):
    if request.method == 'POST':
        product_id = request.form['product_id']
        no_of_items = request.form['no_of_items']

        # Check whether the customer is in the database
        cursor.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        if customer:
            cursor.execute("BEGIN")
            cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            # Check whether the product exists
            if product:
                cursor.execute("SELECT stock FROM Products WHERE id = %s", (product_id,))
                stock = cursor.fetchone()

                # Check whether the stock of the product is available
                if stock[0] >= int(no_of_items):
                    cursor.execute("INSERT INTO Cart VALUES (%s, %s, %s)", (customer_id, product_id, no_of_items))
                    cursor.execute("COMMIT")
                    return redirect(url_for('view_cart', customer_id=customer_id))
                else:
                    cursor.execute("ROLLBACK")
                    return "We have only {} items in stock.".format(stock[0])
            else:
                cursor.execute("ROLLBACK")
                return "Product not found."
        else:
            return "Customer not found."
    else:
        return render_template('add_to_cart.html', customer_id=customer_id)


@app.route('/view_cart/<customer_id>')
def view_cart(customer_id):
    cursor.execute("SELECT * FROM Cart WHERE customer_id = %s", (customer_id,))
    cart = cursor.fetchall()
    cart_items = []

    for cart_item in cart:
        product_id = cart_item[1]
        no_of_items = cart_item[2]
        cursor.execute("SELECT name, price FROM Products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cart_items.append((product[0], product[1], no_of_items, product[1] * no_of_items))

    return render_template('view_cart.html', cart_items=cart_items)


@app.route('/update_customer/<customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    if request.method == 'POST':
        choice = int(request.form['choice'])

        cursor.execute("SELECT wallet_id FROM Customer WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        if customer:
            if choice == 1:
                first_name = request.form['first_name']
                cursor.execute("UPDATE Customer SET first_name = %s WHERE customer_id = %s", (first_name, customer_id))
                cursor.execute("UPDATE Wallet SET wname = %s WHERE id = %s", (first_name, customer[0]))
                rtn = "First name updated as desired"
            elif choice == 2:
                last_name = request.form['last_name']
                cursor.execute("UPDATE Customer SET last_name = %s WHERE customer_id = %s", (last_name, customer_id))
                rtn = "Last name updated as desired"
            elif choice == 3:
                email = request.form['email']
                cursor.execute("UPDATE Customer SET email_id = %s WHERE customer_id = %s", (email, customer_id))
                rtn = "Email updated as desired"
            elif choice == 4:
                current_password = request.form['current_password']
                if current_password == customer[2]:
                    new_password = request.form['new_password']
                    cursor.execute("UPDATE Customer SET password = %s WHERE customer_id = %s",
                                   (new_password, customer_id))
                    rtn = "Password updated as desired"
                else:
                    rtn = "Invalid Password"
            elif choice == 5:
                contact = request.form['contact']
                cursor.execute("UPDATE Customer SET contact = %s WHERE customer_id = %s", (contact, customer_id))
                rtn = "Contact info updated as desired"
            elif choice == 6:
                date_of_birth = request.form['date_of_birth']
                cursor.execute("UPDATE Customer SET date_of_birth = %s WHERE customer_id = %s",
                               (date_of_birth, customer_id))
                rtn = "Date of birth updated as desired"
            elif choice == 7:
                house_no = request.form['house_no']
                locality = request.form['locality']
                city = request.form['city']
                pincode = request.form['pincode']
                cursor.execute(
                    "UPDATE CustomerAddress SET house_no = %s, locality = %s, city = %s, pincode = %s WHERE customer_id = %s",
                    (house_no, locality, city, pincode, customer_id))
                rtn = "Address updated as desired"
            elif choice == 8:
                rtn = "Update canceled"
            else:
                rtn = "Invalid choice"
        else:
            rtn = "Customer not found"
        connection.commit()
        return rtn

    return render_template('update_customer.html', customer_id=customer_id)


@app.route('/place_order/<customer_id>', methods=['GET', 'POST'])
def place_order(customer_id):
    if request.method == 'POST':
        cursor.execute("BEGIN")
        cursor.execute("SELECT wallet_id FROM customer WHERE customer_id = %s", (customer_id,))
        wallet = cursor.fetchone()
        wallet_id = wallet[0]
        cursor.execute("SELECT amount FROM Wallet WHERE id = %s", (wallet_id,))
        wallet2 = cursor.fetchone()
        amount = wallet2[0]
        cursor.execute("SELECT * FROM Cart WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchall()

        bill_amount = 0
        if cart:
            # see_cart(customer_id)  # Replace this with appropriate logic to display the cart
            print("Are you sure you want to proceed with the above order?")
            choice_order = request.form.get('choice_order')

            if choice_order == 'y':
                for i in range(len(cart)):
                    product_id = cart[i][1]
                    no_of_items = cart[i][2]
                    cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
                    product = cursor.fetchone()
                    stock = product[-1]

                    bill_amount += (product[2] * no_of_items)

                delivery_agent_id = random.randint(500, 600)
                date = datetime.now()
                cursor.execute("SELECT id FROM O_rder ORDER BY id DESC LIMIT 1")
                order_id = cursor.fetchone()
                order_id = order_id[0] + 1
                cursor.execute("SELECT id FROM Transactions ORDER BY id DESC LIMIT 1")
                transaction_id = cursor.fetchone()
                transaction_id = transaction_id[0] + 1

                cursor.execute("INSERT INTO Transactions VALUES (%s, %s, %s)", (transaction_id, wallet_id, bill_amount))
                cursor.execute("INSERT INTO O_rder VALUES (%s, %s, %s, %s, %s)",
                               (order_id, delivery_agent_id, customer_id, transaction_id, date))

                for i in range(len(cart)):
                    cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
                    product = cursor.fetchone()
                    stock = product[-1]
                    cursor.execute("INSERT INTO Sold_Items VALUES (%s, %s, %s, %s)",
                                   (customer_id, order_id, cart[i][1], cart[i][2]))

                cursor.execute("COMMIT")

                # Display the bill
                bill_table = PrettyTable(["Product id", "Product name", "Product price", "No of items", "Total price"])
                for i in range(len(cart)):
                    product_id = cart[i][1]
                    no_of_items = cart[i][2]
                    cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
                    product = cursor.fetchone()
                    bill_table.add_row([product_id, product[1], "$"+str(product[2]), no_of_items, '$'+str(product[2] * no_of_items)])

                cursor.execute("DELETE FROM Cart WHERE customer_id = %s", (customer_id,))
                connection.commit()

                return render_template('order_confirmation.html', order_id=order_id,
                                       delivery_agent_id=delivery_agent_id, customer_id=customer_id,
                                       transaction_id=transaction_id, date=date, bill_amount=bill_amount,
                                       bill_table=bill_table.get_html_string())

            else:
                cursor.execute("ROLLBACK")
                return "No order placed"

        else:
            cursor.execute("ROLLBACK")
            return "Cart is empty"

    return render_template('place_order.html', customer_id=customer_id)


@app.route('/remove_from_cart/<customer_id>', methods=['GET', 'POST'])
def remove_from_cart(customer_id):
    if request.method == 'POST':
        cursor.execute("BEGIN")
        cursor.execute("SELECT * FROM Cart WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchall()

        if cart:
            product_id_to_remove = request.form['product_id']
            for product in cart:
                if product[1] == int(product_id_to_remove):
                    cursor.execute("DELETE FROM Cart WHERE product_id = %s AND customer_id = %s",
                                   (product_id_to_remove, customer_id))
                    cursor.execute("COMMIT")
                    return redirect(url_for('remove_success', customer_id=customer_id))
            return "Product not found in the cart."
        else:
            cursor.execute("ROLLBACK")
            return "Cart is empty."

    return render_template('remove_from_cart.html', customer_id=customer_id)


@app.route('/remove_success/<customer_id>')
def remove_success(customer_id):
    cursor.execute("SELECT * FROM Cart WHERE customer_id = %s", (customer_id,))
    cart = cursor.fetchall()
    return render_template('remove_success.html', customer_id=customer_id, cart=cart)


@app.route('/add_money_to_wallet/<customer_id>', methods=['GET', 'POST'])
def add_money_to_wallet(customer_id):
    if request.method == 'POST':
        cursor.execute("BEGIN")
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM Customer WHERE customer_id = %s AND email_id = %s AND password = %s",
                       (customer_id, email, password))
        customer = cursor.fetchone()

        if customer:
            wallet_id = customer[-1]
            cursor.execute("SELECT amount FROM Wallet WHERE id = %s", (wallet_id,))
            wallet = cursor.fetchone()
            previous_amount = wallet[0]

            amount_to_add = int(request.form['amount'])
            cursor.execute("UPDATE Wallet SET amount = %s WHERE id = %s", (previous_amount + amount_to_add, wallet_id))
            cursor.execute("COMMIT")

            return render_template('money_added.html', customer_id=customer_id, previous_amount=previous_amount,
                                   amount_to_add=amount_to_add, current_amount=previous_amount + amount_to_add)

        else:
            cursor.execute("ROLLBACK")
            return "Invalid credentials"

    return render_template('add_money_to_wallet.html', customer_id=customer_id)


@app.route('/see_products')
def see_products():
    cursor.execute("SELECT id, name, price, rating, stock FROM Products")
    products = cursor.fetchall()

    # table_products = PrettyTable()
    # table_products.field_names = ["Product id", "Name", "Price", "Rating", "Current Stock"]
    # for product in products:
    #    table_products.add_row(product)

    product_list = [product for product in products]  # Exclude the product id

    return render_template('see_products.html', products=product_list)


@app.route('/see_orders/<customer_id>')
def see_orders(customer_id):
    cursor.execute("SELECT * FROM O_rder WHERE customer_id = %s", (customer_id,))
    orders = cursor.fetchall()

    order_details = []

    for order in orders:
        cursor.execute("SELECT * FROM Sold_Items WHERE order_id = %s", (order[0],))
        sold = cursor.fetchall()
        sold_items = []

        for s in sold:
            sold_product_id = s[2]
            cursor.execute("SELECT * FROM Products WHERE id = %s", (sold_product_id,))
            sold_product = cursor.fetchall()

            for sp in sold_product:
                sold_items.append([s[2], sp[1], sp[2], s[3], sp[2] * s[3]])

                order_details.append({
                    "order_id": order[0],
                    "delivery_agent_id": order[1],
                    "customer_id": order[2],
                    "transaction_id": order[3],
                    "date": order[4],
                    "sold_items": sold_items
                })

    return render_template('see_orders.html', customer_id=customer_id, orders=order_details)


@app.route('/see_wallet/<customer_id>')
def see_wallet(customer_id):
    cursor.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()

    if customer:
        wallet_id = customer[-1]
        cursor.execute("SELECT * FROM Wallet WHERE id = %s", (wallet_id,))
        wallet = cursor.fetchone()

        return render_template('see_wallet.html', wallet_id=wallet[0], wallet_name=wallet[1], amount=wallet[-1])

    return "Invalid credentials"


@app.route('/filter_products', methods=['GET', 'POST'])
def filter_products():
    if request.method == 'POST':
        choice = request.form['filter_choice']

        if choice == "1":
            min_price = request.form['min_price']
            max_price = request.form['max_price']
            cursor.execute(
                "SELECT id, name, price, rating, stock FROM Products WHERE price BETWEEN %s AND %s ORDER BY price ASC",
                (min_price, max_price))
            products = cursor.fetchall()
            filter_criteria = f'Price between {min_price} and {max_price}'

        elif choice == "2":
            min_stock = request.form['min_stock']
            max_stock = request.form['max_stock']
            cursor.execute("SELECT id, name, price, rating, stock FROM Products WHERE stock BETWEEN %s AND %s",
                           (min_stock, max_stock))
            products = cursor.fetchall()
            filter_criteria = f'Stock between {min_stock} and {max_stock}'

        elif choice == "3":
            name = request.form['product_name']
            cursor.execute("SELECT id, name, price, rating, stock FROM Products WHERE name LIKE %s",
                           ('%' + name + '%',))
            products = cursor.fetchall()
            filter_criteria = f'Product name contains "{name}"'

        elif choice == "4":
            min_rating = request.form['min_rating']
            max_rating = request.form['max_rating']
            cursor.execute("SELECT id, name, price, rating, stock FROM Products WHERE rating BETWEEN %s AND %s",
                           (min_rating, max_rating))
            products = cursor.fetchall()
            filter_criteria = f'Rating between {min_rating} and {max_rating}'

        else:
            return "Invalid choice"

        table_products = PrettyTable()
        table_products.field_names = ["Product id", "Name", "Price", "Rating", "Current Stock"]
        if products:
            for product in products:
                table_products.add_row(product)
            product_list = [product[1:] for product in products]  # Exclude the product id

            return render_template('filtered_products.html', filter_criteria=filter_criteria, products=product_list)
        else:
            return "No products found"

    return render_template('filter_products.html')


@app.route('/check_delivery_partner/<customer_id>')
def check_delivery_partner(customer_id):
    cursor.execute("SELECT * FROM O_rder WHERE customer_id = %s", (customer_id,))
    orders = cursor.fetchall()
    delivery_info = []

    for order in orders:
        delivery_agent_id = order[1]
        cursor.execute("SELECT * FROM delivery_agent WHERE id = %s", (delivery_agent_id,))
        delivery_partner = cursor.fetchone()
        if delivery_partner:
            delivery_info.append(
                [order[0], delivery_partner[0], f"{delivery_partner[1]} {delivery_partner[2]}", delivery_partner[-1]])

    if delivery_info:
        return render_template('check_delivery_partner.html', delivery_info=delivery_info)
    else:
        return "No orders placed"


@app.route('/view_customer')
def view_customer():
    cursor.execute("SELECT * FROM Customer")
    customers = cursor.fetchall()
    customer_info = []

    for customer in customers:
        customer_info.append(
            [customer[0], customer[1], customer[3], customer[4], customer[5], customer[6], customer[-1]])

    if customer_info:
        return render_template('view_customer.html', customer_info=customer_info)
    else:
        return "No customer information available"


@app.route('/view_customer_address')
def view_customer_address():
    cursor.execute("SELECT * FROM Customer_address")
    addresses = cursor.fetchall()
    address_info = []

    for address in addresses:
        address_info.append([address[0], address[1], address[2], address[3], address[4]])

    if address_info:
        return render_template('view_customer_address.html', address_info=address_info)
    else:
        return "No customer address information available"


@app.route('/view_delivery_agent')
def view_delivery_agent():
    cursor.execute("SELECT * FROM Delivery_agent")
    agents = cursor.fetchall()
    agent_info = []

    for agent in agents:
        agent_info.append([agent[0], agent[1], agent[2], agent[3]])

    if agent_info:
        return render_template('view_delivery_agent.html', agent_info=agent_info)
    else:
        return "No delivery agent information available"


@app.route('/add_new_product', methods=['GET', 'POST'])
def add_new_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = int(request.form['price'])
        stock = int(request.form['stock'])
        image = "http://dummyimage.com/149x100.png/dddddd/000011"  # You can customize the image URL
        rating = int(request.form['rating'])

        cursor.execute("SELECT id from Products ORDER BY id DESC LIMIT 1")
        product_id = cursor.fetchone()
        product_id = product_id[0] + 1

        cursor.execute("INSERT INTO Products VALUES (%s, %s, %s, %s, %s, %s)",
                       (product_id, product_name, price, image, rating, stock))
        db.commit()
        return redirect(url_for('view_products'))
    return render_template('add_product.html')


@app.route('/view_products')
def view_products():
    # Retrieve and display products
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    return render_template('view_products.html', products=products)


@app.route('/product_update', methods=['GET', 'POST'])
def product_update():
    if request.method == 'POST':
        product_id = request.form['product_id']
        cursor.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if product:
            update_choice = request.form['update_choice']
            if update_choice == 'update_stock':
                stock = int(request.form['stock'])
                cursor.execute("UPDATE Products SET stock = %s WHERE id = %s", (stock, product_id))
                db.commit()
                return redirect(url_for('view_products'))
            elif update_choice == 'update_price':
                price = int(request.form['price'])
                cursor.execute("UPDATE Products SET price = %s WHERE id = %s", (price, product_id))
                db.commit()
                return redirect(url_for('view_products'))
            elif update_choice == 'delete_product':
                return render_template('confirm_delete.html', product=product)
        else:
            return "Product not found"

    return render_template('product_update.html')


@app.route('/confirm_delete/<product_id>', methods=['POST'])
def confirm_delete(product_id):
    delete = request.form['delete']
    if delete == 'yes':
        cursor.execute("DELETE FROM Products WHERE id = %s", (product_id,))
        db.commit()
        return redirect(url_for('view_products'))
    else:
        return "Product not deleted"


@app.route('/add_delivery_agent', methods=['GET', 'POST'])
def add_delivery_agent():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact = request.form['contact']

        cursor.execute("select id from Delivery_agent ORDER BY id DESC LIMIT 1")
        delivery_agent_id = cursor.fetchone()
        delivery_agent_id = delivery_agent_id[0] + 1

        cursor.execute("INSERT INTO Delivery_agent VALUES (%s, %s, %s, %s)",
                       (delivery_agent_id, first_name, last_name, contact))
        db.commit()
        return redirect(url_for('view_delivery_agents'))

    return render_template('add_delivery_agent.html')


@app.route('/view_delivery_agents')
def view_delivery_agents():
    # Retrieve and display delivery agents
    cursor.execute("SELECT * FROM Delivery_agent")
    delivery_agents = cursor.fetchall()
    return render_template('view_delivery_agents.html', delivery_agents=delivery_agents)


@app.route('/monthly_revenue')
def monthly_revenue():
    query = "SELECT YEAR(O_rder.date), MONTH(O_rder.date), SUM(Transactions.amount) " \
            "FROM O_rder JOIN Transactions ON O_rder.transaction_id = Transactions.id " \
            "GROUP BY YEAR(O_rder.date), MONTH(O_rder.date) " \
            "ORDER BY SUM(Transactions.amount) DESC;"
    cursor.execute(query)
    results = cursor.fetchall()

    return render_template('monthly_revenue.html', results=results)


@app.route('/product_region')
def product_region():
    query = "SELECT customer_address.city, Sold_Items.items, Products.name " \
            "FROM Products JOIN Sold_Items ON Products.id = Sold_Items.product_id " \
            "JOIN customer_address ON Sold_Items.customer_id = customer_address.customer_id " \
            "GROUP BY customer_address.city, Sold_Items.items, Products.name " \
            "ORDER BY Sold_Items.items DESC;"
    cursor.execute(query)
    results = cursor.fetchall()

    return render_template('product_region.html', results=results)


@app.route('/product_sales')
def product_sales():
    query = "SELECT Products.id, Products.name, SUM(Sold_Items.items) AS Total_quantity_sold, " \
            "SUM(Sold_Items.items) * Products.price AS Revenue_by_product " \
            "FROM Products JOIN Sold_Items ON Products.id = Sold_Items.product_id " \
            "GROUP BY Products.id " \
            "ORDER BY Revenue_by_product DESC;"
    cursor.execute(query)
    results = cursor.fetchall()

    return render_template('product_sales.html', results=results)


@app.route('/deliveries_by_agent')
def deliveries_by_agent():
    query = "SELECT Delivery_Agent.id, Delivery_Agent.first_name, Delivery_Agent.last_name, " \
            "COUNT(*) AS number_of_orders " \
            "FROM O_rder JOIN Delivery_Agent ON Delivery_Agent.id = O_rder.delivery_agent_id " \
            "GROUP BY Delivery_Agent.id " \
            "ORDER BY number_of_orders DESC;"
    cursor.execute(query)
    results = cursor.fetchall()

    return render_template('deliveries_by_agent.html', results=results)


@app.route('/customer_dashboard/<customer_id>', methods=['GET'])
def customer_dashboard(customer_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM customer WHERE customer_id=%s", (customer_id,))
    data = cursor.fetchone()
    customer = [ele for ele in data]
    print(customer)
    cursor.execute("SELECT * FROM Customer_address WHERE customer_id = %s", (customer[0],))
    customer1 = cursor.fetchone()
    for i in range(5):
        if i == 0:
            continue
        customer.append(customer1[i])
    print(customer)

    cursor.close()

    return render_template('customer_dashboard.html', details = customer)


@app.route('/employee_dashboard')
def employee_dashboard():
    # Implement employee functionality here
    return render_template('employee_dashboard.html')


if __name__ == '__main__':
    if connection.is_connected():
        print('Connected to MySQL database')
        cursor = connection.cursor()
        cursor.execute('select * from Customer')
        row = cursor.fetchone()
        while row is not None:
            # print(row)
            row = cursor.fetchone()
    else:
        print('Connection failed')
    app.run(debug=True)
