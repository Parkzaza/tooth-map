from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 's3cr3t_k3y_123456'

# Define the upload folder for files
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize default data for teeth status
teeth_data = {
    '11': 'ปกติ', '12': 'ปกติ', '13': 'ปกติ', '14': 'ปกติ',
    '15': 'ปกติ', '16': 'ปกติ', '17': 'ปกติ', '18': 'ปกติ',
    '21': 'ปกติ', '22': 'ปกติ', '23': 'ปกติ', '24': 'ปกติ',
    '25': 'ปกติ', '26': 'ปกติ', '27': 'ปกติ', '28': 'ปกติ',
    '31': 'ปกติ', '32': 'ปกติ', '33': 'ปกติ', '34': 'ปกติ',
    '35': 'ปกติ', '36': 'ปกติ', '37': 'ปกติ', '38': 'ปกติ',
    '41': 'ปกติ', '42': 'ปกติ', '43': 'ปกติ', '44': 'ปกติ',
    '45': 'ปกติ', '46': 'ปกติ', '47': 'ปกติ', '48': 'ปกติ'
}

events = []  # Store calendar events
reports = []  # Store patient reports
# ข้อมูลผู้ป่วย (จำลอง)
patients = {
    'john': {'name': 'John Doe', 'points': 50, 'password': '1234'},
    'jane': {'name': 'Jane Smith', 'points': 30, 'password': '5678'}
}

# รางวัลที่สามารถแลกได้
rewards = [
    {'id': 1, 'description': 'ส่วนลดการรักษา 10%', 'points_required': 30},
    {'id': 2, 'description': 'รักษาฟันฟรี 1 ครั้ง', 'points_required': 50}
]

# Define the upload folder for files
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/index')
def index():
    return redirect(url_for('main'))

# Main page (home page)
@app.route('/main')
def main():
    status_count = {}
    for status in teeth_data.values():
        status_count[status] = status_count.get(status, 0) + 1
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    patient = patients[username]

    return render_template('main.html', patient=patient, teeth_data=teeth_data, status_count=status_count, rewards=rewards)

@app.route('/calendar')
def calendar_page():
    global events  # Use global variable events
    calendar_events = [
        {
            'title': event['title'],
            'start': event['date'],
            'color': '#800080',  # Purple color
            'description': event['notes']
        }
        for event in events
    ]
    return render_template('calendar.html', events=calendar_events)

@app.route('/patient_report', methods=['GET', 'POST'])
def patient_report():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        tooth_numbers = request.form.getlist('tooth_number[]')
        tooth_sides = request.form.getlist('tooth_side[]')
        problem_description = request.form['problem_description']
        appointment_needed = request.form.get('appointment_needed')
        image_upload = request.files.get('image_upload')
        date_reported = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        image_path = None
        if image_upload and image_upload.filename != '':
            filename = secure_filename(image_upload.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_upload.save(image_path)

        # Combine tooth numbers and sides for easier storage
        tooth_info = [{"number": tooth_numbers[i], "side": tooth_sides[i]} for i in range(len(tooth_numbers))]

        # Store the data in the reports list (for prototype purposes)
        report = {
            'patient_name': patient_name,
            'tooth_info': tooth_info,
            'problem_description': problem_description,
            'appointment_needed': appointment_needed,
            'image_path': image_path,
            'date_reported': date_reported
        }

        reports.append(report)  # Add the report to the list

        return redirect(url_for('patient_report'))  # Redirect back to the form

    return render_template('patient_report.html', reports=reports)

@app.route('/submit_dental_record', methods=['POST'])
def submit_dental_record():
    tooth_side = request.form.get('tooth_side_1')
    problem_type = request.form.get('problem_type_1')
    appointment_date = request.form.get('appointment_date', '')
    notes = request.form.get('notes', '')
    doctor_name = request.form.get('doctor_name', 'ไม่ระบุ')

    # Split the tooth numbers provided
    tooth_sides = [side.strip() for side in tooth_side.split(',')]

    # Check and create the upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    image_path = None
    if 'image_upload' in request.files:
        image = request.files['image_upload']
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            notes += f"\nดูรูปภาพที่แนบ: {url_for('static', filename='uploads/' + filename)}"

    for side in tooth_sides:
        teeth_data[side] = problem_type

        # Add the event for the tooth problem on the current date
        events.append({
            'title': f'ฟันซี่ {side} - {problem_type}',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'notes': notes
        })

        # Add the appointment event if an appointment date is provided
        if appointment_date:
            existing_event = next((event for event in events if event['date'] == appointment_date and event['title'].startswith(f'นัดหมายกับหมอ {doctor_name}')), None)
            if existing_event:
                existing_event['title'] += f", ฟันซี่ {side}"
                existing_event['notes'] += f"\n{notes}"
            else:
                events.append({
                    'title': f'นัดหมายกับหมอ {doctor_name} - ฟันซี่ {side}',
                    'date': appointment_date,
                    'notes': notes
                })

    return redirect(url_for('index'))

@app.route('/dental_record', methods=['GET', 'POST'])
def dental_record():
    if request.method == 'POST':
        tooth_number = request.form.get('tooth_number')
        tooth_side = request.form.get('tooth_side')
        problem_type = request.form.get('problem_type')
        appointment_date = request.form.get('appointment_date')
        notes = request.form.get('notes')
        doctor_name = "นศพ"  # Default doctor name

        tooth_sides = [side.strip() for side in tooth_side.split(',')]

        for side in tooth_sides:
            teeth_data[side] = problem_type

        existing_event = next((event for event in events if event['problem_type'] == problem_type and event['doctor'] == doctor_name and event['date'] == appointment_date), None)

        if existing_event:
            existing_event['tooth_sides'] += ', ' + ', '.join(tooth_sides)
        else:
            events.append({
                'title': f'นัดหมายกับหมอ {doctor_name}',
                'date': appointment_date,
                'doctor': doctor_name,
                'problem_type': problem_type,
                'tooth_sides': ', '.join(tooth_sides),
                'notes': notes
            })

        events.append({
            'title': f'ปัญหาฟัน: {problem_type}',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'doctor': doctor_name,
            'problem_type': problem_type,
            'tooth_sides': ', '.join(tooth_sides),
            'notes': notes
        })

        return redirect(url_for('index'))

    return render_template('dental_record.html')

# หน้าล็อกอิน
# แก้ไขใน route ของหน้า login เพื่อให้ redirect ไปที่หน้า main แทน profile
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in patients and patients[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('main'))  # เปลี่ยน profile เป็น main
        else:
            return 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'

    return render_template('login.html')
# หน้าแลกแต้ม
@app.route('/redeem_reward', methods=['POST'])
def redeem_reward():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    patient = patients[username]
    reward_id = int(request.form['reward_id'])
    reward = next((r for r in rewards if r['id'] == reward_id), None)

    # ตรวจสอบว่าแต้มเพียงพอหรือไม่
    if reward and patient['points'] >= reward['points_required']:
        patient['points'] -= reward['points_required']  # หักแต้ม

    return redirect(url_for('main'))

# ออกจากระบบ
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # ใช้พอร์ตใหม่ถ้าจำเป็น
