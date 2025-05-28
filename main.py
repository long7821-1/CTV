from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
import pandas as pd
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'thay-bang-chuoi-bi-mat'

EXCEL_FILE = "ctv.xlsx"

# Tài khoản admin (tùy bạn sửa thêm)
ADMIN_USERS = {
    "thanhthuy171nhe@gmail.com": "123456",
    "admin2": "123456"
}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def load_data():
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
        else:
            df = pd.DataFrame(columns=["Mã CTV", "Họ tên", "Ngân hàng", "Số tài khoản", "Tên tài khoản", "Lương"])
    except Exception as e:
        print(f"Lỗi đọc file Excel: {e}")
        df = pd.DataFrame(columns=["Mã CTV", "Họ tên", "Ngân hàng", "Số tài khoản", "Tên tài khoản", "Lương"])

    data = {}
    for _, row in df.iterrows():
        ma = str(row["Mã CTV"]).strip().upper()
        data[ma] = {
            "ten": row["Họ tên"],
            "bank": str(row["Ngân hàng"]).strip().upper(),
            "account_no": str(row["Số tài khoản"]).strip(),
            "account_name": str(row["Tên tài khoản"]).strip().upper(),
            "luong": str(row["Lương"]).strip()
        }
    return df, data


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        if username in ADMIN_USERS and ADMIN_USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Sai tài khoản hoặc mật khẩu.")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/export-ctv')
@login_required
def export_ctv():
    try:
        return send_file(EXCEL_FILE,
                         as_attachment=True,
                         download_name='ctv.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return f"Lỗi khi xuất file: {e}"


@app.route('/tra-cuu', methods=['POST'])
def tra_cuu():
    _, data = load_data()
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


@app.route('/admin/add-ctv', methods=['GET', 'POST'])
@login_required
def add_ctv():
    if request.method == 'POST':
        df, data = load_data()
        ma_ctv = request.form.get('ma_ctv', '').strip().upper()
        ho_ten = request.form.get('ho_ten', '').strip()
        ngan_hang = request.form.get('ngan_hang', '').strip().upper()
        so_tai_khoan = request.form.get('so_tai_khoan', '').strip()
        ten_tai_khoan = request.form.get('ten_tai_khoan', '').strip().upper()
        luong = request.form.get('luong', '').strip()

        if not all([ma_ctv, ho_ten, ngan_hang, so_tai_khoan, ten_tai_khoan]):
            return render_template('add_ctv.html', error="Vui lòng điền đầy đủ các trường.")

        if not ma_ctv.isalnum():
            return render_template('add_ctv.html', error="Mã CTV chỉ được chứa chữ và số.")

        if not so_tai_khoan.isdigit():
            return render_template('add_ctv.html', error="Số tài khoản chỉ được chứa số.")

        if luong:
            try:
                if float(luong) <= 0:
                    return render_template('add_ctv.html', error="Lương phải là số dương.")
            except ValueError:
                return render_template('add_ctv.html', error="Lương phải là số hợp lệ.")

        if ma_ctv in data:
            return render_template('add_ctv.html', error="Mã CTV đã tồn tại.")

        try:
            new_row = pd.DataFrame([{
                "Mã CTV": ma_ctv,
                "Họ tên": ho_ten,
                "Ngân hàng": ngan_hang,
                "Số tài khoản": so_tai_khoan,
                "Tên tài khoản": ten_tai_khoan,
                "Lương": luong
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df["Lương"] = ""
            df.loc[df["Mã CTV"] == ma_ctv, "Lương"] = luong
            df.to_excel(EXCEL_FILE, index=False)
            return render_template('add_ctv.html', success="Thêm CTV thành công!")
        except Exception as e:
            return render_template('add_ctv.html', error=f"Lỗi khi lưu dữ liệu: {e}")
    return render_template('add_ctv.html')


@app.route('/admin/add-salary', methods=['GET', 'POST'])
@login_required
def add_salary():
    if request.method == 'POST':
        df, data = load_data()
        ma_ctv = request.form.get('ma_ctv', '').strip().upper()
        luong = request.form.get('luong', '').strip()

        if not all([ma_ctv, luong]):
            return render_template('add_salary.html', error="Vui lòng điền đầy đủ các trường.")

        if not ma_ctv.isalnum():
            return render_template('add_salary.html', error="Mã CTV chỉ được chứa chữ và số.")

        try:
            if float(luong) <= 0:
                return render_template('add_salary.html', error="Lương phải là số dương.")
        except ValueError:
            return render_template('add_salary.html', error="Lương phải là số hợp lệ.")

        if ma_ctv not in data:
            return render_template('add_salary.html', error="Mã CTV không tồn tại.")

        try:
            df["Lương"] = ""
            df.loc[df["Mã CTV"] == ma_ctv, "Lương"] = luong
            df.to_excel(EXCEL_FILE, index=False)
            return render_template('add_salary.html', success="Thêm lương thành công!")
        except Exception as e:
            return render_template('add_salary.html', error=f"Lỗi khi lưu dữ liệu: {e}")
    return render_template('add_salary.html')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Sử dụng cổng từ biến môi trường, mặc định là 5000
    app.run(host='0.0.0.0', port=port, debug=False)  # Lắng nghe trên 0.0.0.0 và tắt debug khi triển khai
