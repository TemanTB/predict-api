from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import uuid
from prediction import predict

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db-temantb'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

def authorize_request():
    authorization_header = request.headers.get('Authorization')

    if not authorization_header:
        print("No authorization header found.")
        return None

    _, refresh_token = authorization_header.split(' ', 1) 


    with mysql.connection.cursor() as cur:
        cur.execute("SELECT userId FROM users WHERE refresh_token = %s", (refresh_token,))
        user = cur.fetchone()

    if user is None:
        print("User not found for the given refresh token.")
        return None

    user_id = user.get('userId') if isinstance(user, dict) else user
    return user_id


@app.route('/', methods=['GET'])
def index():
    return 'hello'



@app.route('/health', methods=['POST'])
def health():
    # def calculate_hasil():
    #     hasil = 1
    #     return hasil

    if request.method == 'POST':
        try:
            data = request.json
            input_text = data.get('description')

            get_predit = 0 if predict(input_text) == 'positif' else 1

            date_str = data.get('date')
            created_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
            next_date = created_date + timedelta(days=14)

            userId = authorize_request()

            if not userId:
                return jsonify({"status": "error", "message": "Invalid refresh token"}), 401

            with mysql.connection.cursor() as conn:
                
                conn.execute("SELECT MAX(weeks) FROM health WHERE userId = %s", (userId,))
                max_weeks = conn.fetchone()[0]
                current_weeks = max_weeks + 1 if max_weeks is not None else 1

               
                conn.execute("SELECT point FROM health WHERE userId = %s ORDER BY time DESC LIMIT 1", (userId,))
                last_point_result = conn.fetchone()

                if last_point_result is not None:
                    last_point = last_point_result[0]
                    if get_predit == 0:
                        current_point = max(last_point - 1, 1)               
                        images = 'https://storage.googleapis.com/temantb-api.appspot.com/up.png'
                    else: 
                        current_point = last_point + 1  
                        images = 'https://storage.googleapis.com/temantb-api.appspot.com/down.png'

                    if current_point > 5:
                        average = "Memburuk"
                    else:
                        average = "Membaik"
                else:
                    current_point = 5
                    average = "Membaik"
                    images = 'https://storage.googleapis.com/temantb-api.appspot.com/up.png'


                health_id = str(uuid.uuid4())
                alert = f"Please put your health back on {next_date}"

                conn.execute(
                    "INSERT INTO health (healthId, weeks, date, nextDate, point, alert, description, average, images, userId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (health_id, current_weeks, created_date, next_date, current_point, alert, input_text, average, images, userId),
                )

                mysql.connection.commit()

            return jsonify({
                "status": {
                    "code": 201,
                    "message": "success post data"
                },
                "message": "Data inserted successfully",
                "data": {
                "ml_predict": get_predit,
                "current_point": current_point,
                "description": input_text,
                }      
            }), 201

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    else:
        return jsonify({"status": "error", "message": "Invalid request method"})

if __name__ == '__main__':
    app.run(debug=True)