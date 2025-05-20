# To sync the packages run 
```
pip freeze > requirements.txt
```

# Requirements
- Python 3.9+
- Flask 2.x
- Other dependencies (listed in requirements.txt)

# Installation
```bash
git clone https://github.com/UMOC/UMOC-Backend.git
cd UMOC-Backend
pip install -r requirements.txt
```

# Usage

Run the main.py file. Maybe sync the packages first.
```bash
python src/main.py
```
or
```bash
docker build -t umoc-backend .
docker run -d -p 5000:5000 umoc-backend
```
The server will be running on http://127.0.0.1:5000

# API response Time
```bash
pip install locust
locust -f src/metrics/locustfile.py --headless -u 10 -r 2 --run-time 20s --host http://localhost:5000
```

# Example Data

USERS:
```json
[
    {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "username": "user1",
        "password": "password1",
        "session_id": "00000000-0000-0000-1111-000000000001"
    },
    {
        "user_id": "00000000-0000-0000-0000-000000000002",
        "username": "user2",
        "password": "password2",
        "session_id": "00000000-0000-0000-1111-000000000002"
    },
    {
        "user_id": "00000000-0000-0000-0000-000000000003",
        "username": "user3",
        "password": "password3",
        "session_id": "00000000-0000-0000-1111-000000000003"
    }
]
```
Bei Login wird die Session ID zurückgegeben und die alte überschrieben.


