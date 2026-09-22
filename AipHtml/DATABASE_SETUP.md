# Database Setup Guide

## Prerequisites

- MySQL Server installed and running
- Python 3.7+
- pip (Python package manager)

## Installation Steps

### 1. Install MySQL Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database Connection

Edit `db_setup.py` and `server.py` - update the `DB_CONFIG` with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # Your MySQL username
    'password': 'password',   # Your MySQL password
    'database': 'aip_db'
}
```

### 3. Initialize the Database

Run the database setup script to create tables:

```bash
python db_setup.py
```

You should see output like:

```
✓ Database 'aip_db' created/verified
✓ 'users' table created/verified
✓ 'login_logs' table created/verified
✓ 'face_data_history' table created/verified
✓ Database setup completed successfully!
```

### 4. Start Your Server

```bash
python server.py
```

## Database Schema

### users table

- `id`: Auto-increment primary key
- `student_number`: Unique student identifier
- `pin`: User's PIN (encrypted in production)
- `face_data`: JSON stored face recognition data
- `face_registered`: Boolean flag (TRUE only after face is registered via PIN)
- `created_at`: Timestamp when user was created
- `updated_at`: Timestamp of last update

### login_logs table

- Tracks all login attempts with success/failure status
- Records login method: `registration`, `pin`, `face_registration`, `face_recognition`, `face_recovery`
- Stores IP address for security audit

### face_data_history table

- Stores historical face data for all face registrations/updates
- Useful for audit trail and recovery purposes

## API Endpoints (Secure Flow)

### 1. POST /register

**Create new account (PIN only)**

- Body: `{ "studentNumber": "STU001", "pin": "1234" }`
- Response: Account created, face registration required
- Returns: `faceRegistered: false`

### 2. POST /register-face

**Register face (requires PIN verification)**

- Body: `{ "studentNumber": "STU001", "pin": "1234", "faceData": {...} }`
- Security: PIN must match registered user
- Sets: `face_registered = TRUE`
- After this, facial recognition login/recovery is enabled

### 3. POST /login

**Login with PIN**

- Body: `{ "studentNumber": "STU001", "pin": "1234" }`
- Always available for registered users

### 4. POST /login-face

**Login with facial recognition**

- Body: `{ "studentNumber": "STU001", "faceData": {...} }`
- Security: Only works if `face_registered = TRUE`
- Requires valid face match with stored data

### 5. POST /recover

**Recover account using registered face**

- Body: `{ "studentNumber": "STU001", "faceData": {...}, "newPin": "5678" }`
- Security: Face must be registered first, face must match
- Action: Resets PIN to new value
- Only works if `face_registered = TRUE`

## Security Features

✓ **Face Registration Required**: Users must register face with PIN verification
✓ **Authenticated Face Registration**: Cannot register face without PIN
✓ **Account Recovery Protected**: Recovery only works with registered face
✓ **Login Method Tracking**: All login attempts logged with method used
✓ **Face Registration Flag**: `face_registered` prevents unauthorized access
✓ **Audit Trail**: All actions tracked in login_logs table

## Important Security Notes

1. **Never allow face-based operations without face_registered = TRUE**
2. **Always verify PIN when registering face**
3. **Implement actual face comparison** in `/login-face` and `/recover` endpoints (currently placeholder)
4. **Use face recognition library** like OpenCV, face_recognition, or similar to compare faces
5. **Encrypt sensitive data** in production (PIN, face data)
6. **Use HTTPS** in production for all API calls

## Troubleshooting

**Error: Database connection failed**

- Ensure MySQL server is running
- Check credentials in `DB_CONFIG`
- Verify MySQL user has proper permissions

**Error: Table already exists**

- The setup script uses `CREATE TABLE IF NOT EXISTS`
- Safe to run multiple times
