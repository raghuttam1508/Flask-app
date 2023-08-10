from datetime import datetime
from flask import Flask, redirect, render_template, request, jsonify
import flask
from flask_mysqldb import MySQL
import json

application = Flask(__name__)
application.app_context().push()

application.config["MYSQL_HOST"] = "localhost"
application.config["MYSQL_USER"] = "root"
application.config["MYSQL_PASSWORD"] = "root"
application.config["MYSQL_DB"] = "Ecommerce_Flask"
mysql = MySQL(application)


def is_alphabet(name):
    st = name.replace(" ", "")
    return st.isalpha()


@application.route("/")
def home():
    return render_template("index.html")


@application.route("/create_customer", methods=["POST", "GET"])
def create_customer():
    try:
        cur = mysql.connection.cursor()
    except Exception as e:
        return jsonify({"message": f"Database connection not Established, {e}"})

    if request.method == "POST":
        # details = {
        #     'phone_number': '9876543214',
        #     'Name':'Raghu',
        #     'Address':'Mumbai',
        #     }
        try:
            details = request.form
            phone_number = int(details["phone_number"])
            name = details["name"]
            address = details["address"]
        except Exception as e:
            return jsonify({"message": f"Error in input data type Error - {e}"})

        if phone_number is None or not name or not address:
            return jsonify({"message": "Missing Phone Number, Name, or Address"}), 400

        if not is_alphabet(name):
            return jsonify({"message": "Invalid name format"}), 400

        if not address.strip():
            return jsonify({"message": "Empty Address"})

        if phone_number < 1000000000 or phone_number > 9999999999:
            return (
                jsonify(
                    {
                        "message": "Phone number should have only numbers and should be of 10 digit"
                    }
                ),
                422,
            )

        check_query = "SELECT cust_id, name FROM Customers WHERE phone_number = %s"
        cur.execute(check_query, (phone_number,))
        existing_customer = cur.fetchone()

        if existing_customer:
            return (
                jsonify(
                    {
                        "message": f"Customer with the same name and phone number already exists, with ID {existing_customer[0]} and name {existing_customer[1]}"
                    }
                ),
                422,
            )

        query = (
            "INSERT INTO Customers (phone_number, name, address) VALUES (%s, %s, %s)"
        )
        val = (phone_number, name, address)
        cur.execute(query, val)
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": f"sucessfully created user {name}"})
    else:
        return render_template("CreateCustomerForm.html")


@application.route("/order", methods=["POST", "GET"])
def create_order():
    try:
        cur = mysql.connection.cursor()
    except Exception as e:
        return jsonify({"message": f"Database connection not Established, {e}"})

    if request.method == "POST":
        # details = {
        #     'item_name' : "Tooth Brush",
        #     'phone_number': '7894561237',
        # }

        try:
            details = request.form
            item_name = details["item_name"]
            phone_number = int(details["phone_number"])
        except Exception as e:
            return jsonify({"message": f"Error in input data type {e}"})

        if item_name is None or phone_number is None:
            return jsonify({"message": "Missing item name or phone number"}), 400
        if phone_number < 1000000000 or phone_number > 9999999999:
            return (
                jsonify(
                    {
                        "message": "Phone number should have only numbers and should be of 10 digit"
                    }
                ),
                422,
            )
        if not item_name.strip():
            return jsonify({"message": "Empty Item Name"})

        select_cust_id = "select cust_id from Customers where phone_number = %s"
        cur.execute(select_cust_id, (phone_number,))
        cust_id = cur.fetchone()

        if not cust_id:
            return jsonify({"message": "Customer not found"}), 404

        insert_to_orders = "INSERT INTO Orders (item_name, created_at, updated_at) values (%s, NOW(), NOW())"
        item = item_name.strip()
        cur.execute(insert_to_orders, (item,))
        mysql.connection.commit()

        order_id = cur.lastrowid
        vals = (cust_id, order_id)

        insert_ref_query = (
            "INSERT INTO customer_order_ref (cust_id, order_id) VALUES (%s, %s)"
        )
        cur.execute(insert_ref_query, vals)
        mysql.connection.commit()

        ref_id = cur.lastrowid
        cur.close()
        return jsonify(
            {
                "message": f"Order created successfully with Order ID {order_id} and refernce ID {ref_id}"
            }
        )

    if request.method == "GET":
        return render_template("OrderForm.html")


@application.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "GET":
        return render_template("productsPage.html")


@application.route("/updateStatus", methods=["GET", "POST"])
def update_order_status():
    try:
        cur = mysql.connection.cursor()
    except Exception as e:
        return jsonify({"message": f"Database connection not Established, {e}"})

    if request.method == "POST":
        # details = {
        #     "order_id" : 5,
        #     "Status" : "Dispatched"
        # }

        try:
            details = request.form

            order_id = details["order_id"]
            status = details["status"]
        except Exception as e:
            return jsonify({"message": f"Error in input data type, Error -  {e}"})

        if order_id is None or status is None:
            return jsonify({"message": "Missing data"})

        if not order_id.isdigit():
            return jsonify({"message": "Order ID must be a number"})

        if not is_alphabet(status):
            return jsonify({"message": "Invalid Status"}), 400

        check_order_id = "select order_id from Orders where order_id = %s"
        cur.execute(check_order_id, (order_id,))
        id_1 = cur.fetchone()

        if id_1 is None:
            return jsonify({"message": "Order not found"}), 404

        update_status = (
            "update Orders set status = %s, updated_at = NOW() where order_id = %s"
        )
        cur.execute(update_status, (status, order_id))
        mysql.connection.commit()

        return jsonify({"message": f"Updated order status of {order_id} to {status}"})
    else:
        return render_template("/updateStatusForm.html")


@application.route("/get_orders", methods=["GET", "POST"])
def get_orders():
    try:
        cur = mysql.connection.cursor()
    except Exception as e:
        return jsonify({"message": f"Database connection not Established, {e}"})

    if request.method == "POST":
        # details = {
        #     "phone_number" : 9876541232
        # }
        try:
            details = request.form 
            phone_number = int(details["phone_number"])
        except Exception as e:
            return jsonify({"message": f"Error in input data type, Error - {e}"})

        if phone_number is None:
            return jsonify({"message": "Missing Phone Number"}), 400

        if phone_number < 1000000000 or phone_number > 9999999999:
            return (
                jsonify(
                    {
                        "message": "Phone number should have only numbers and should be of 10 digit"
                    }
                ),
                422,
            )
        check_query = "select cust_id from Customers where phone_number = %s"
        cur.execute(check_query, (phone_number,))
        existing_cust_id = cur.fetchone()

        if not existing_cust_id:
            return jsonify(
                {"message": f"Customer with phone number {phone_number} does not exist"}
            )

        get_order_details = "select item_name, order_id, status from Orders where order_id in ( select order_id from customer_order_ref where cust_id = %s) order by updated_at desc;"
        cur.execute(get_order_details, (existing_cust_id,))
        results = cur.fetchall()

        order_data = {}
        count = 0
        for i in results:
            order_data[count] = {
                "order_id": str(i[1]),
                "item name": str(i[0]),
                "status": str(i[2]),
            }
            count += 1
        return jsonify(order_data)

    else:
        return render_template("GetOrders.html")


# @app.route('/show')
# def show():
#     Cust = Customers.query.all()
#     m = jsonify(Cust)
#     print(m)
#     return render_template("show.html",Cust=Cust)

if __name__ == "__main__":
    application.run(debug=True)
