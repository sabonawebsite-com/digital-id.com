from flask import Flask, render_template, request, jsonify  
from flask_sqlalchemy import SQLAlchemy  
import qrcode  
import io  
import base64  
import random  

app = Flask(__name__)  

# Configure the SQLite database  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event_attendees3.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)  

# Define the Attendee model  
class Attendee(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    maqaa = db.Column(db.String(100), nullable=False)  
    dhugati = db.Column(db.String(100), nullable=False)  
    bayina = db.Column(db.String(100), nullable=False)  
    kafalti = db.Column(db.String(100), nullable=False)  
    haftee = db.Column(db.String(100), nullable=False)  
    generated_id = db.Column(db.String(50), nullable=False)  

    def __repr__(self):  
        return f'<Attendee {self.dhugati}>'  

# Create the database tables  
with app.app_context():  
    db.create_all()  

@app.route('/')  
def index():  
    return render_template('index.html')  

@app.route('/generate', methods=['POST'])  
def generate_id():  
    data = request.form  

    # Ensure all required fields are present  
    required_fields = ['Maqaa', 'Mal ajaja', 'Hagam', 'Kafaltii', 'Haftee']  
    for field in required_fields:  
        if field not in data:  
            return jsonify({'error': f'Missing field: {field}'}), 400  

    maqaa = data['Maqaa']  
    dhugati = data['Mal ajaja']  
    bayina = data['Hagam']  
    kafalti = "@" + data['Kafaltii']  
    haftee = data['Haftee']  
    id = f'{str(random.randint(0, 9999)).zfill(4)}'  

    qr_text = f'ID : {id}\nMaqaa: {maqaa}\nDhugati: {dhugati}\nBayina: {bayina}\nKafalti: {kafalti}\nHaftee: {haftee}'  
    
    try:  
        qr = qrcode.make(qr_text)  
        buffer = io.BytesIO()  
        qr.save(buffer, format='PNG')  
        qr_img = base64.b64encode(buffer.getvalue()).decode('utf-8')  

        # Save the attendee data to the database  
        new_attendee = Attendee(maqaa=maqaa, dhugati=dhugati, bayina=bayina, kafalti=kafalti, haftee=haftee, generated_id=id)  
        db.session.add(new_attendee)  
        db.session.commit()  
    except Exception as e:  
        return jsonify({'error': str(e)}), 500  # Return error if database operation fails  

    # Return data to front end  
    return jsonify({  
        'Maqaa': maqaa,  
        'Mal ajaja': dhugati,  
        'Hagam': bayina,  
        'Kafaltii': kafalti,  
        'Haftee': haftee,  
        'qr_img': f'data:image/png;base64,{qr_img}',  
        'id': id  
    })  

if __name__ == '__main__':  
    app.run(debug=True)