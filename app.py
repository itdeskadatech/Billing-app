from flask import Flask, render_template, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

menu = [
    {'id': 1, 'name': 'Classic Burger', 'price': 5},
    {'id': 2, 'name': 'Cheese Burger', 'price': 6},
    {'id': 3, 'name': 'Veggie Burger', 'price': 4},
    {'id': 4, 'name': 'Chicken Burger', 'price': 7},
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        orders = []
        subtotal = 0

        for item in menu:
            qty = int(request.form.get(f'qty_{item["id"]}', 0))
            if qty > 0:
                total = item['price'] * qty
                subtotal += total
                orders.append({
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': qty,
                    'total': total
                })

        student_discount = 0
        if request.form.get('student') == 'yes':
            student_discount = subtotal * 0.2

        delivery_charge = 0
        if request.form.get('delivery') == 'yes':
            delivery_charge = (subtotal - student_discount) * 0.05

        tip = float(request.form.get('tip', 0))

        total = subtotal - student_discount + delivery_charge + tip

        email = request.form.get('email')
        if email:
            send_email(email, orders, subtotal, student_discount, delivery_charge, tip, total)

        return render_template('index.html', menu=menu, submitted=True, orders=orders,
                               subtotal=subtotal, student_discount=round(student_discount, 2),
                               delivery_charge=round(delivery_charge, 2), tip=round(tip, 2), total=round(total, 2))

    return render_template('index.html', menu=menu, submitted=False)

def send_email(to_email, orders, subtotal, discount, delivery, tip, total):
    from_email = 'rambbagal@gmail.com'   # replace with your email
    from_password = 'Raj@7888'   # replace with your app password

    subject = "Your Burger Bill"
    body = f"""
    <h2>Your Burger Bill Summary</h2>
    <ul>
    {''.join([f'<li>{item["quantity"]}x {item["name"]} = ${item["total"]}</li>' for item in orders])}
    </ul>
    <p><strong>Subtotal:</strong> ${subtotal}</p>
    <p><strong>Student Discount:</strong> -${discount}</p>
    <p><strong>Delivery Charge:</strong> +${delivery}</p>
    <p><strong>Tip:</strong> +${tip}</p>
    <h3><strong>Total:</strong> ${total}</h3>
    <p>Thank you for ordering!</p>
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        print("Email sending failed:", e)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
