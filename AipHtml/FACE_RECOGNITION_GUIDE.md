# Face Recognition Implementation Guide

## Current Status

The `/login-face` and `/recover` endpoints have placeholders for actual face verification. You need to implement face comparison logic.

## Recommended Libraries

### Option 1: face_recognition (Easiest - Recommended)

```bash
pip install face-recognition
pip install dlib
```

**Implementation:**

```python
import face_recognition
import base64
import numpy as np
from io import BytesIO
from PIL import Image

def extract_face_encoding(face_data_json):
    """Convert stored face data to encoding"""
    face_dict = json.loads(face_data_json)
    # If stored as base64 image
    if 'image' in face_dict:
        img_data = base64.b64decode(face_dict['image'])
        image = Image.open(BytesIO(img_data))
        image_np = np.array(image)
        encodings = face_recognition.face_encodings(image_np)
        if encodings:
            return encodings[0]
    return None

def compare_faces(new_face_data, stored_face_encoding):
    """Compare two face encodings"""
    new_encoding = extract_face_encoding(new_face_data)
    if new_encoding is None:
        return False

    # Compare with tolerance (lower = stricter)
    distance = face_recognition.face_distance([stored_face_encoding], new_encoding)
    return distance[0] < 0.6  # Tolerance threshold
```

### Option 2: OpenCV with Deep Learning

```bash
pip install opencv-python
```

### Option 3: Microsoft Azure Face API / Google Cloud Vision

- Cloud-based solutions with pre-built models
- More accurate but requires API keys and internet connection

## Integration Steps

### Step 1: Update requirements.txt

```
Flask==2.3.3
flask-cors==4.0.0
mysql-connector-python==8.2.0
face-recognition==1.3.5
dlib==19.24.2
Pillow==10.0.0
numpy==1.24.3
```

### Step 2: Update server.py

Find these three locations and replace the placeholders:

**In `/login-face` endpoint (around line 120):**

```python
# REPLACE THIS:
# In a real app, you would use a face recognition library to compare faces
# For now, this is a placeholder - replace with actual face comparison logic
# Example: compare_faces(face_data, user['face_data'])

# WITH THIS:
stored_encoding = extract_face_encoding(user['face_data'])
if not stored_encoding or not compare_faces(face_data, stored_encoding):
    cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                   (student_number, 'face_recognition', False))
    conn.commit()
    cursor.close()
    return jsonify({'success': False, 'error': 'Face does not match'}), 401
```

**In `/recover` endpoint (around line 180):**

```python
# REPLACE THIS:
# In a real app, verify the face_data matches the stored face
# For now, this is a placeholder - replace with actual face comparison
# Example: if not compare_faces(face_data, user['face_data']):
#     return jsonify({'success': False, 'error': 'Face does not match'}), 401

# WITH THIS:
stored_encoding = extract_face_encoding(user['face_data'])
if not stored_encoding or not compare_faces(face_data, stored_encoding):
    cursor.execute('INSERT INTO login_logs (student_number, login_method, success) VALUES (%s, %s, %s)',
                   (student_number, 'face_recovery', False))
    conn.commit()
    cursor.close()
    return jsonify({'success': False, 'error': 'Face does not match'}), 401
```

### Step 3: Add helper functions to server.py

Add these functions near the top of server.py after the imports and DB config:

```python
import face_recognition
import base64
import numpy as np
from io import BytesIO
from PIL import Image

def extract_face_encoding(face_data_json):
    """Convert stored face data to face encoding for comparison"""
    try:
        face_dict = json.loads(face_data_json)

        # If stored as base64 image
        if 'image' in face_dict:
            img_data = base64.b64decode(face_dict['image'])
            image = Image.open(BytesIO(img_data))
            image_np = np.array(image)
            encodings = face_recognition.face_encodings(image_np)
            if encodings:
                return encodings[0]

        # If stored as encoding array
        elif 'encoding' in face_dict:
            return np.array(face_dict['encoding'])
    except Exception as e:
        print(f"Error extracting face encoding: {e}")

    return None

def compare_faces(new_face_data, stored_face_encoding):
    """Compare two face encodings with tolerance"""
    try:
        new_encoding = extract_face_encoding(new_face_data)
        if new_encoding is None:
            return False

        # Compare faces with tolerance (lower = stricter)
        # 0.6 is default, lower values are stricter (0.5 very strict, 0.65 more lenient)
        distance = face_recognition.face_distance([stored_face_encoding], new_encoding)
        return distance[0] < 0.6
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return False
```

## Testing Face Recognition

### Test with cURL

```bash
# Register face
curl -X POST http://localhost:3000/register-face \
  -H "Content-Type: application/json" \
  -d '{
    "studentNumber": "STU001",
    "pin": "1234",
    "faceData": {"image": "base64_encoded_image_here"}
  }'

# Login with face
curl -X POST http://localhost:3000/login-face \
  -H "Content-Type: application/json" \
  -d '{
    "studentNumber": "STU001",
    "faceData": {"image": "base64_encoded_image_here"}
  }'
```

## Production Checklist

- [ ] Implement actual face comparison (not placeholder)
- [ ] Choose face recognition library (recommended: face_recognition)
- [ ] Add tolerance threshold tuning (0.6 is default)
- [ ] Encrypt PIN in database
- [ ] Use HTTPS for all endpoints
- [ ] Add rate limiting to prevent brute force
- [ ] Add CORS restrictions
- [ ] Log all security events
- [ ] Regular security audits
- [ ] Multi-factor authentication consideration

## Troubleshooting

**No faces detected in image:**

- Ensure image has clear, frontal face
- Check image quality and size
- Verify face_recognition.face_encodings() returns results

**False positives (wrong face matches):**

- Decrease tolerance (from 0.6 to 0.5)
- Require better quality images

**Slow performance:**

- Use GPU acceleration if available
- Consider async processing for batch operations
- Cache face encodings in database instead of recalculating
