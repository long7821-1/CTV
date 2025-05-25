from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Đọc dữ liệu từ file Excel
try:
    df = pd.read_excel("ctv.xlsx")
except Exception as e:
    print(f"Không thể đọc file Excel: {e}")
    df = pd.DataFrame(columns=["Mã CTV", "Họ tên", "Ngân hàng", "Số tài khoản", "Tên tài khoản", "Lương"])

# Tiền xử lý dữ liệu
data = {}
for _, row in df.iterrows():
    ma = str(row["Mã CTV"]).strip().upper()
    data[ma] = {
        "ten": row["Họ tên"],
        "bank": str(row["Ngân hàng"]).strip().upper(),
        "account_no": str(row["Số tài khoản"]).strip(),
        "account_name": str(row["Tên tài khoản"]).strip().upper(),
        "luong": str(row["Lương"]).strip()  # Cột "Lương"
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tra-cuu', methods=['POST'])
def tra_cuu():
    ma = request.json.get('ma', '').upper()
    if ma in data:
        return jsonify({
            "ten": data[ma]["ten"],
            "ma": ma,
            "bank": data[ma]["bank"],
            "account_no": data[ma]["account_no"],
            "account_name": data[ma]["account_name"],
            "luong": data[ma]["luong"]
        })
    return jsonify({"ten": "Không tìm thấy mã này", "ma": ""})

if __name__ == '__main__':
    app.run(debug=True)