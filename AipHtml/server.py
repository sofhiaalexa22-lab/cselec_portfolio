from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Aip_2216',  # Change this to your MySQL password
    'database': 'aip_db'
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/verify-credentials', methods=['POST'])
def verify_credentials():
    """Verify student number and PIN for face registration (doesn't require face to be registered)"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    pin = data.get('pin')
    
    if not student_number or not pin:
        return jsonify({'success': False, 'error': 'Student number and PIN are required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT student_number, face_registered FROM users WHERE student_number = %s AND pin = %s',
                       (student_number, pin))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return jsonify({
                'success': True, 
                'faceRegistered': user['face_registered'],
                'message': 'Credentials verified successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid student number or PIN'}), 401
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/register', methods=['POST'])
def register():
    """Register a new user or verify an existing account with PIN"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    pin = data.get('pin')
    
    if not student_number or not pin:
        return jsonify({'success': False, 'error': 'Student number and PIN are required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE student_number = %s', (student_number,))
        existing_user = cursor.fetchone()

        if existing_user:
            if existing_user['pin'] == pin:
                cursor.close()
                return jsonify({'success': True, 'message': 'Account verified successfully. Please register your face next.'})
            else:
                cursor.close()
                return jsonify({'success': False, 'error': 'Student number already exists with a different PIN'}), 400

        cursor.execute('INSERT INTO users (student_number, pin, face_registered) VALUES (%s, %s, FALSE)',
                       (student_number, pin))
        conn.commit()
        
        # Log the registration
        cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                       (student_number, 'registration', True))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Account created. Please register your face next.'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_number = data['studentNumber']
    pin = data['pin']
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE student_number = %s AND pin = %s',
                       (student_number, pin))
        user = cursor.fetchone()
        
        if user:
            # Log successful login
            cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                           (student_number, 'pin', True))
            conn.commit()
            cursor.close()
            return jsonify({'success': True, 'user': user, 'faceRegistered': user['face_registered']})
        else:
            # Log failed login
            cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                           (student_number, 'pin', False))
            conn.commit()
            cursor.close()
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/register-face', methods=['POST'])
def register_face():
    """Register face for a user (requires PIN authentication first)"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    pin = data.get('pin')
    face_data = json.dumps(data.get('faceData', {}))
    
    if not student_number or not pin or not face_data or face_data == '{}':
        return jsonify({'success': False, 'error': 'Student number, PIN, and face data are required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First verify the user with PIN
        cursor.execute('SELECT * FROM users WHERE student_number = %s AND pin = %s',
                       (student_number, pin))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid student number or PIN'}), 401
        
        # Update face data and set face_registered to TRUE
        cursor.execute('UPDATE users SET face_data = %s, face_registered = TRUE, updated_at = CURRENT_TIMESTAMP WHERE student_number = %s',
                       (face_data, student_number))
        conn.commit()
        
        # Store in history
        cursor.execute('INSERT INTO face_data_history (student_number, face_data) VALUES (%s, %s)',
                       (student_number, face_data))
        conn.commit()
        
        # Log the face registration
        cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                       (student_number, 'face_registration', True))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Face registered successfully'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/login-face', methods=['POST'])
def login_face():
    """Login using facial recognition (requires registered face)"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    face_data = json.dumps(data.get('faceData', {}))
    
    if not student_number or not face_data or face_data == '{}':
        return jsonify({'success': False, 'error': 'Student number and face data are required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check if face is registered for this student
        cursor.execute('SELECT * FROM users WHERE student_number = %s AND face_registered = TRUE',
                       (student_number,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            return jsonify({'success': False, 'error': 'No registered face found for this student'}), 401
        
        # In a real app, you would use a face recognition library to compare faces
        # For now, this is a placeholder - replace with actual face comparison logic
        # Example: compare_faces(face_data, user['face_data'])
        
        # Log successful facial recognition login
        cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                       (student_number, 'face_recognition', True))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'user': user})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/recover', methods=['POST'])
def recover():
    """Recover account using registered face (requires face to be registered first)"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    face_data = json.dumps(data.get('faceData', {}))
    new_pin = data.get('newPin')
    
    if not student_number or not face_data or face_data == '{}' or not new_pin:
        return jsonify({'success': False, 'error': 'Student number, face data, and new PIN are required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists and has registered face
        cursor.execute('SELECT * FROM users WHERE student_number = %s AND face_registered = TRUE',
                       (student_number,))
        user = cursor.fetchone()
        
        if not user:
            # Log failed recovery attempt
            cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                           (student_number, 'face_recovery', False))
            conn.commit()
            cursor.close()
            return jsonify({'success': False, 'error': 'User not found or face not registered'}), 401
        
        # In a real app, verify the face_data matches the stored face
        # For now, this is a placeholder - replace with actual face comparison
        # Example: if not compare_faces(face_data, user['face_data']):
        #     return jsonify({'success': False, 'error': 'Face does not match'}), 401
        
        # Update PIN with new PIN
        cursor.execute('UPDATE users SET pin = %s, updated_at = CURRENT_TIMESTAMP WHERE student_number = %s',
                       (new_pin, student_number))
        conn.commit()
        
        # Store face data in history
        cursor.execute('INSERT INTO face_data_history (student_number, face_data) VALUES (%s, %s)',
                       (student_number, face_data))
        conn.commit()
        
        # Log successful recovery
        cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                       (student_number, 'face_recovery', True))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Account recovered successfully. PIN has been reset.'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # Note: Run db_setup.py first to initialize the database
    # python db_setup.py
    app.run(debug=True, port=3000)