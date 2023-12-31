class Customers(db.Model):
    cust_id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.Integer, nullable=False)
    Fname = db.Column(db.String(15), nullable=False)
    Lname = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(50),nullable=False)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.cust_id} - {self.Fname}"
    
class orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Enum("Dispactched","Not Dispatched"))
    created_at = db.Column(db.String(10), nullable=False)
    updated_at = db.Column(db.String(10), nullable=False)


    def __repr__(self) -> str:
        return f"{self.order_id} - {self.item_name}"
    
class customer_order_ref(db.Model):
    ref_id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer,ForeignKey(Customers.cust_id))
    order_id = db.Column(db.Integer,ForeignKey(orders.order_id))

    def __repr__(self) -> str:
        return f"{self.order_id} - {self.ref_id}"
    
