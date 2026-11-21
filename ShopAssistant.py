from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('shop_database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    low_stock = conn.execute('SELECT * FROM products WHERE quantity <= min_stock').fetchall()
    transactions = conn.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    chat_history = conn.execute('SELECT * FROM chat_history ORDER BY timestamp DESC').fetchall()
    
    total_profit_row = conn.execute('SELECT SUM(profit) FROM transactions').fetchone()
    total_profit = total_profit_row[0] if total_profit_row and total_profit_row[0] else 0.0
    
    conn.close()
    return render_template('index.html', products=products, low_stock=low_stock, transactions=transactions, chat_history=chat_history, total_profit=total_profit)

@app.route('/add_product', methods=('POST',))
def add_product():
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    quantity = int(request.form.get('quantity', 0))
    min_stock = int(request.form.get('min_stock', 2))
    
    image = request.files.get('image')
    image_path = ''
    if image and image.filename != '':
        image_filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
        image_path = f"uploads/{image_filename}"

    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, category, price, quantity, min_stock, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                 (name, category, price, quantity, min_stock, image_path))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_product/<int:id>', methods=('POST', 'GET'))
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_transaction', methods=('POST',))
def add_transaction():
    client_name = request.form.get('client_name')
    service_description = request.form.get('service_description')
    cost = float(request.form.get('cost', 0))
    profit = float(request.form.get('profit', 0))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO transactions (client_name, service_description, cost, profit) VALUES (?, ?, ?, ?)',
                 (client_name, service_description, cost, profit))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/chat', methods=('POST',))
def chat():
    user_query = request.form.get('query', '').strip().lower()
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    
    matched_products = []
    for p in products:
        if p['name'].lower() in user_query or user_query in p['name'].lower() or (p['category'] and p['category'].lower() in user_query):
            matched_products.append(p)
            
    if matched_products:
        if len(matched_products) == 1:
            p = matched_products[0]
            stock_status = "⚠️ تنبيه: الكمية اقتربت على النفاذ!" if p['quantity'] <= p['min_stock'] else "متوفرة بحالة ممتازة ✅"
            answer = f"أهلاً بك! لقد وجدت السلعة المطلوبة في مخزونك:\n\n• **اسم السلعة:** {p['name']}\n• **التصنيف:** {p['category']}\n• **السعر:** {p['price']} د.ل\n• **الكمية المتبقية:** {p['quantity']} قطع\n• **حالة المخزون:** {stock_status}"
            product_data = dict(p)
            products_list = None
        else:
            answer = f"وجدت {len(matched_products)} سلع تطابق استفسارك '{user_query}':\n"
            for i, p in enumerate(matched_products, 1):
                stock_status = "⚠️ (قارب على النفاذ)" if p['quantity'] <= p['min_stock'] else "✅"
                answer += f"\n{i}. **{p['name']}** | السعر: {p['price']} د.ل | المتبقي: {p['quantity']} قطع {stock_status}"
            answer += "\n\nأي نوع تقصد بالتحديد؟"
            product_data = None
            products_list = [dict(p) for p in matched_products]
    else:
        if any(word in user_query for word in ["مرحبا", "سلام", "اهلا", "صباح", "مساء"]):
            answer = "أهلاً بك! أنا مساعدك الذكي الخاص بإدارة الورش والمتاجر. يمكنك سؤالي عن أي سلعة وسأجيبك فوراً."
            product_data = None
            products_list = None
        else:
            answer = f"عذراً، لم أتمكن من العثور على سلعة تطابق استفسارك '{user_query}' في قاعدة البيانات. يمكنك إضافتها بسهولة عبر القائمة الجانبية."
            product_data = None
            products_list = None

    conn.execute('INSERT INTO chat_history (question, answer) VALUES (?, ?)', (user_query, answer))
    conn.commit()
    conn.close()

    return jsonify({
        'answer': answer,
        'product': product_data,
        'products_list': products_list
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)