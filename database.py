import sqlite3
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="language_courses.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        # Terms table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
        ''')
        
        # Teachers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            term_id INTEGER,
            bio TEXT,
            FOREIGN KEY (term_id) REFERENCES terms(id)
        )
        ''')
        
        # Courses table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            term_id INTEGER,
            teacher_id INTEGER,
            day TEXT,
            time TEXT,
            location TEXT,
            topics TEXT,
            price INTEGER,
            FOREIGN KEY (term_id) REFERENCES terms(id),
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
        ''')
        
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            student_id TEXT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Registrations table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER,
            student_id TEXT,
            course_id INTEGER,
            term_id INTEGER,
            teacher_id INTEGER,
            payment_type TEXT,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            first_payment_confirmed BOOLEAN DEFAULT 0,
            second_payment_confirmed BOOLEAN DEFAULT 0,
            receipt_photo_link TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (telegram_id) REFERENCES users(telegram_id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (term_id) REFERENCES terms(id),
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
        ''')
        
        # FAQ table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
        ''')
        
        # About info table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS about (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
        ''')
        
        self.conn.commit()
    
    def add_sample_data(self):
        """Add sample data to the database for testing purposes."""
        # Sample terms
        terms = [
            (1, "ترم 1 زبان", "دوره مقدماتی زبان انگلیسی"),
            (2, "ترم 2 زبان", "دوره پیش‌متوسطه زبان انگلیسی"),
            (3, "ترم 3 زبان", "دوره متوسطه زبان انگلیسی"),
            (4, "ترم 4 زبان", "دوره پیشرفته زبان انگلیسی")
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO terms (id, name, description) VALUES (?, ?, ?)", terms)
        
        # Sample teachers
        teachers = [
            (1, "دکتر محمدی", 1, "دکترای آموزش زبان انگلیسی از دانشگاه تهران"),
            (2, "دکتر علوی", 1, "دکترای زبان شناسی از دانشگاه شیراز"),
            (3, "استاد رضایی", 2, "کارشناسی ارشد مترجمی زبان انگلیسی"),
            (4, "دکتر صادقی", 3, "دکترای زبان و ادبیات انگلیسی"),
            (5, "استاد کریمی", 4, "مدرک DELTA از دانشگاه کمبریج")
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO teachers (id, name, term_id, bio) VALUES (?, ?, ?, ?)", teachers)
        
        # Sample courses
        courses = [
            (1, 1, 1, "شنبه", "14:00-16:00", "کلاس 101", "گرامر پایه، مکالمه مقدماتی", 2500000),
            (2, 1, 2, "یکشنبه", "10:00-12:00", "کلاس 102", "گرامر پایه، مکالمه مقدماتی", 2500000),
            (3, 2, 3, "دوشنبه", "16:00-18:00", "کلاس 201", "مکالمه پیش‌متوسطه، درک مطلب", 3000000),
            (4, 3, 4, "سه‌شنبه", "14:00-16:00", "کلاس 301", "مکالمه متوسطه، نوشتار", 3500000),
            (5, 4, 5, "چهارشنبه", "18:00-20:00", "کلاس 401", "مکالمه پیشرفته، آمادگی آزمون", 4000000)
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO courses (id, term_id, teacher_id, day, time, location, topics, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", courses)
        
        # Sample FAQ
        faqs = [
            (1, "شرایط ثبت‌نام چیست؟", "برای ثبت‌نام باید دانشجو باشید و شماره دانشجویی معتبر داشته باشید."),
            (2, "آیا امکان انصراف وجود دارد؟", "تا قبل از شروع کلاس‌ها، 80% مبلغ پرداختی عودت داده می‌شود."),
            (3, "کلاس‌ها آنلاین است یا حضوری؟", "کلاس‌ها به صورت حضوری در دانشگاه برگزار می‌شود."),
            (4, "تعداد جلسات هر ترم چند جلسه است؟", "هر ترم شامل 16 جلسه آموزشی است."),
            (5, "مدرک پایان دوره دارای اعتبار است؟", "بله، مدرک پایان دوره دارای مهر رسمی انجمن زبان دانشگاه است.")
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO faq (id, question, answer) VALUES (?, ?, ?)", faqs)
        
        # About info
        about_info = [
            (1, "انجمن زبان دانشگاه", """انجمن زبان دانشگاه از سال 1390 با هدف ارتقای سطح زبان انگلیسی دانشجویان تأسیس شده است. 
            مدرسین این انجمن از اساتید برجسته دانشگاه و دارای مدارک معتبر بین‌المللی هستند.
            تاکنون بیش از 5000 دانشجو در دوره‌های مختلف انجمن شرکت کرده‌اند.""")
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO about (id, title, content) VALUES (?, ?, ?)", about_info)
        
        self.conn.commit()
    
    def get_terms(self):
        """Get all available terms."""
        self.cursor.execute("SELECT id, name, description FROM terms")
        return self.cursor.fetchall()
    
    def get_teachers_by_term(self, term_id):
        """Get all teachers for a specific term."""
        self.cursor.execute("SELECT id, name, bio FROM teachers WHERE term_id = ?", (term_id,))
        return self.cursor.fetchall()
    
    def get_course_details(self, term_id, teacher_id):
        """Get course details for a specific term and teacher."""
        self.cursor.execute("""
        SELECT c.id, t.name, c.day, c.time, c.location, c.topics, c.price 
        FROM courses c
        JOIN terms t ON c.term_id = t.id
        WHERE c.term_id = ? AND c.teacher_id = ?
        """, (term_id, teacher_id))
        return self.cursor.fetchone()
    
    def register_user(self, telegram_id, student_id, first_name, last_name):
        """Register a new user or update existing user."""
        try:
            self.cursor.execute("""
            INSERT OR REPLACE INTO users (telegram_id, student_id, first_name, last_name)
            VALUES (?, ?, ?, ?)
            """, (telegram_id, student_id, first_name, last_name))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False
    
    def add_registration(self, telegram_id, student_id, course_id, term_id, teacher_id, payment_type, payment_method):
        """Add a new course registration."""
        try:
            self.cursor.execute("""
            INSERT INTO registrations 
            (telegram_id, student_id, course_id, term_id, teacher_id, payment_type, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (telegram_id, student_id, course_id, term_id, teacher_id, payment_type, payment_method))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding registration: {e}")
            return None
    
    def update_registration_receipt(self, registration_id, receipt_photo_link):
        """Update a registration with receipt photo link."""
        try:
            self.cursor.execute("""
            UPDATE registrations 
            SET receipt_photo_link = ?
            WHERE id = ?
            """, (receipt_photo_link, registration_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating registration receipt: {e}")
            return False
    
    def update_payment_status(self, registration_id, payment_status, is_first_payment=True):
        """Update the payment status for a registration."""
        try:
            if is_first_payment:
                self.cursor.execute("""
                UPDATE registrations 
                SET payment_status = ?, first_payment_confirmed = 1
                WHERE id = ?
                """, (payment_status, registration_id))
            else:
                self.cursor.execute("""
                UPDATE registrations 
                SET payment_status = ?, second_payment_confirmed = 1
                WHERE id = ?
                """, (payment_status, registration_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    def get_registration_by_id(self, registration_id):
        """Get registration details by ID."""
        self.cursor.execute("""
        SELECT r.*, u.first_name, u.last_name, c.price, t.name as teacher_name, tm.name as term_name
        FROM registrations r
        JOIN users u ON r.telegram_id = u.telegram_id
        JOIN courses c ON r.course_id = c.id
        JOIN teachers t ON r.teacher_id = t.id
        JOIN terms tm ON r.term_id = tm.id
        WHERE r.id = ?
        """, (registration_id,))
        return self.cursor.fetchone()
    
    def get_user_registrations(self, telegram_id):
        """Get all registrations for a user."""
        self.cursor.execute("""
        SELECT r.id, tm.name as term_name, t.name as teacher_name, c.price, 
               r.payment_status, r.first_payment_confirmed, r.second_payment_confirmed,
               r.payment_type, r.payment_method, r.registration_date
        FROM registrations r
        JOIN courses c ON r.course_id = c.id
        JOIN teachers t ON r.teacher_id = t.id
        JOIN terms tm ON r.term_id = tm.id
        WHERE r.telegram_id = ?
        ORDER BY r.registration_date DESC
        """, (telegram_id,))
        return self.cursor.fetchall()
    
    def get_pending_registrations(self):
        """Get all pending registrations for admin review."""
        self.cursor.execute("""
        SELECT r.id, u.first_name, u.last_name, u.student_id, 
               tm.name as term_name, t.name as teacher_name, c.price, 
               r.payment_type, r.payment_method, r.receipt_photo_link,
               r.first_payment_confirmed, r.second_payment_confirmed
        FROM registrations r
        JOIN users u ON r.telegram_id = u.telegram_id
        JOIN courses c ON r.course_id = c.id
        JOIN teachers t ON r.teacher_id = t.id
        JOIN terms tm ON r.term_id = tm.id
        WHERE r.payment_status = 'pending'
        ORDER BY r.registration_date ASC
        """)
        return self.cursor.fetchall()
    
    def get_faq(self):
        """Get all FAQ items."""
        self.cursor.execute("SELECT question, answer FROM faq")
        return self.cursor.fetchall()
    
    def get_about(self):
        """Get about information."""
        self.cursor.execute("SELECT title, content FROM about")
        return self.cursor.fetchone()
    
    def check_student_id(self, student_id):
        """Check if a student ID exists in the database."""
        # In a real application, this would check the Excel file
        # For now, we'll simulate it with sample data
        return True, "محمد", "احمدی"
    
    def close(self):
        """Close the database connection."""
        self.conn.close() 