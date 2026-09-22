#!/usr/bin/env python3
"""
Test script for the new /verify-credentials endpoint
This simulates the endpoint behavior without requiring MySQL
"""

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Mock user database for testing
MOCK_USERS = {
    "STU001": {"pin": "1234", "face_registered": False},
    "STU002": {"pin": "5678", "face_registered": True},
}

@app.route('/verify-credentials', methods=['POST'])
def verify_credentials():
    """Mock verify credentials endpoint"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    pin = data.get('pin')

    if not student_number or not pin:
        return jsonify({'success': False, 'error': 'Student number and PIN are required'}), 400

    # Check mock database
    user = MOCK_USERS.get(student_number)
    if user and user['pin'] == pin:
        return jsonify({
            'success': True,
            'faceRegistered': user['face_registered'],
            'message': 'Credentials verified successfully'
        })
    else:
        return jsonify({'success': False, 'error': 'Invalid student number or PIN'}), 401

@app.route('/register-face', methods=['POST'])
def register_face():
    """Mock register face endpoint"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    pin = data.get('pin')

    if not student_number or not pin:
        return jsonify({'success': False, 'error': 'Student number and PIN are required'}), 400

    # Check mock database
    user = MOCK_USERS.get(student_number)
    if user and user['pin'] == pin:
        # Simulate face registration
        MOCK_USERS[student_number]['face_registered'] = True
        return jsonify({'success': True, 'message': 'Face registered successfully'})
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    """Mock register endpoint - now used for account creation in face registration"""
    data = request.get_json()
    student_number = data.get('studentNumber')
    pin = data.get('pin')

    if not student_number or not pin:
        return jsonify({'success': False, 'error': 'Student number and PIN are required'}), 400

    if student_number in MOCK_USERS:
        return jsonify({'success': False, 'error': 'Student number already exists'}), 400

    MOCK_USERS[student_number] = {"pin": pin, "face_registered": False}
    return jsonify({'success': True, 'message': 'Account created. Please register your face next.'})

if __name__ == '__main__':
    print("🚀 Starting mock server for testing...")
    print("📋 Available test users:")
    for student_id, data in MOCK_USERS.items():
        print(f"   {student_id}: PIN={data['pin']}, Face Registered={data['face_registered']}")
    print("\n🌐 Server running on http://localhost:3000")
    print("🧪 Test the /verify-credentials endpoint with:")
    print("   curl -X POST http://localhost:3000/verify-credentials \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"studentNumber\": \"STU001\", \"pin\": \"1234\"}'")
    app.run(debug=True, port=3000)