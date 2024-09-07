from flask import Flask, render_template

app = Flask(__name__)

# หน้าแรก
@app.route('/')
def home():
    return render_template('index.html')

# หน้าแบบฟอร์มผู้ป่วย
@app.route('/patient-form')
def patient_form():
    return render_template('patient-form.html')

# หน้าแสดงรายชื่อผู้ป่วย
@app.route('/patient-list')
def patient_list():
    return render_template('patient-list.html')

# หน้าแสดงรายละเอียดผู้ป่วย
@app.route('/patient-detail')
def patient_detail():
    return render_template('patient-detail.html')

if __name__ == '__main__':
    app.run(debug=True)
