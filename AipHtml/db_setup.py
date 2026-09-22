import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',  # Change this to your MySQL password
    'database': 'aip_db'
}

def create_database():
    """Create the database and tables"""
    try:
        # Connect to MySQL server (without specifying database)
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"✓ Database '{DB_CONFIG['database']}' created/verified")
        
        # Select the database
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_number VARCHAR(50) UNIQUE NOT NULL,
                pin VARCHAR(255) NOT NULL,
                face_data LONGTEXT,
                face_registered BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        print("✓ 'users' table created/verified")
        
        # Create login logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_number VARCHAR(50) NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                login_method VARCHAR(50),
                success BOOLEAN DEFAULT TRUE,
                ip_address VARCHAR(45),
                FOREIGN KEY (student_number) REFERENCES users(student_number)
            )
        ''')
        print("✓ 'login_logs' table created/verified")
        
        # Create face data history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS face_data_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_number VARCHAR(50) NOT NULL,
                face_data LONGTEXT,
                stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_number) REFERENCES users(student_number)
            )
        ''')
        print("✓ 'face_data_history' table created/verified")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database setup completed successfully!")
        
    except Error as e:
        print(f"✗ Error: {e}")
        print("\nMake sure MySQL is running and update the password in DB_CONFIG")

if __name__ == '__main__':
    create_database()
