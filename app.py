# Importing necessary Libraries
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user
import pickle
import numpy as np
import warnings
from sklearn.exceptions import DataConversionWarning
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash

arthritis_med  = {"18" : "https://www.apollopharmacy.in/otc/apollo-life-joint-health-new-formula-tablets-30-s","30":"https://www.apollopharmacy.in/otc/apollo-pharmacy-pain-relief-oil-60-ml","50":"https://bioayurveda.com/products/bio-jointartho-tablet?variant=44365974733080&campaignid=19744115199&adgroupid=&creative=&matchtype=&network=x&device=c&keyword=&gclid=Cj0KCQjwj_ajBhCqARIsAA37s0ydEr63N8xdmPA608SAAjhvlIS7MEqS1Wml_uSgwkiVi3u0bqQe0dIaAsOnEALw_wcB","80":"https://pharmeasy.in/health-care/products/pharmeasy-joint-support---maintains-joints-mobility---bone-joint-health---bottle-of-60-3864230"};
diarrhea_med = {"15":"https://www.schwabeindia.com/product/kindigest/?attribute_pa_packagename=30sizeglobules&attribute_pa_size=10g&utm_source=Google%20Shopping&utm_campaign=Google%20Shoppping%20Feed&utm_medium=cpc&utm_term=734&gclid=Cj0KCQjwj_ajBhCqARIsAA37s0zzeLDh5x03RHnfHV0DfqtjMOI6pWzczxJI655ijsXDxnF7ItEPxtAaAnMfEALw_wcB","18":"https://www.excelpharma.co.in/product/e-diarrhorea-dropse-vet-no-4/?gclid=Cj0KCQjwj_ajBhCqARIsAA37s0wlDN59W3bkHSECIRku3IfQnHyBv0GZiqa-8DHlWO8aWXZI9p-EubcaAkHBEALw_wcB"};
gastritis_med = {"15" : "https://www.pulseplus.in/product/gastica-drops-pc-14282?gclid=Cj0KCQjwj_ajBhCqARIsAA37s0wcbW_hLuf-75s35WDzRMV8rgGBSMG9Yfm2PAWr-7bV_xhUxaZGRvMaAkCjEALw_wcB" ,"30":"https://www.herbkart.com/acidity-capsule-30-capsules/?srsltid=AR57-fA0g9_x9nDqzeohfUuphSLlqdJDpjRuj6UFr6Qzcv4TNi-deiXEX6Q"}
migraine_med = {"20":"https://vissconext.com/products/therapeutic-headband-for-headache?variant=41700698259637&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&utm_campaign=17669352220&adgroupid=&utm_content=&utm_term=&gclid=Cj0KCQjwj_ajBhCqARIsAA37s0xBUytcUTbAg8Amh5m4sgJoUcZjDwU26KZ1Yygd2CJfpVLyChRKMBIaAqi5EALw_wcB","30":"https://www.netmeds.com/non-prescriptions/bi-quinol-tablet-20s?srsltid=AR57-fBQ0v44O0tadpiALXd1WqEh98qHEhiKop3Iou8kXAxjq_XVCg08kMg"}



# Ignoring User warnings and Data Conversion Warning
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DataConversionWarning)

# Establishing Flask Connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = {'admin':'sqlite:///database2.db'}
app.config['SECRET_KEY'] = 'secretkey'

#
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# Defining the table columns
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    address = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    pastcondition = db.Column(db.String(80), nullable=False)

class adminUser(db.Model,UserMixin):
    __bind_key__="admin"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


#Defining a class called RegisterForm, which inherits from FlaskForm
class RegisterForm(FlaskForm):
    firstname = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "First Name", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})
    lastname = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Last Name", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})
    age = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "Age", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})
    gender = SelectField('Gender', choices=[('Male','Male'),('Female','Female')], render_kw={"class": "text-sm mx-1"})
    email = StringField(validators=[InputRequired(), Length(min=10, max=40)], render_kw={"placeholder": "Email", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})
    address = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Enter your City", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent  shadow-sm"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent  shadow-sm"})
    pastcondition = StringField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Past Conditions", "class": "h-20 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})
    submit = SubmitField('Register', render_kw={"class": "bg-black w-full h-10 cursor-pointer text-white rounded-md text-sm"})

    # This is a validation method to check if a given email address already exists in the database.
    from flask import flash

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            flash('That email already exists. Please choose a different one.', 'error')
            raise ValidationError('That email already exists. Please choose a different one.')


# Creating a login form for users to enter their email and password information, and submit it to the server for authentication..
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=40)], render_kw={"placeholder": "Email", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent  shadow-sm"})

    submit = SubmitField('Login', render_kw={"class": "bg-black w-full h-10 cursor-pointer text-white rounded-md text-sm"})

 #Create an admin user
class adminForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=40)], render_kw={"placeholder": "Email", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent shadow-sm"})

    password = PasswordField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password", "class": "h-8 w-full rounded-md border border-slate-300 text-sm pl-2 bg-transparent  shadow-sm"})

    submit = SubmitField('Login', render_kw={"class": "bg-black w-full h-10 cursor-pointer text-white rounded-md text-sm"})


#Loading Diease Dectection Pickle File
f = open("DecisionTree-Model.sav", "rb")
model_N = pickle.load(f)

#loading Medicine Recommendation Pickle file
f2 = open("drugTree.pkl", "rb")
model_med = pickle.load(f2)


#Mapping Symptoms as indexes in dataset using dictionary
symptom_mapping = {
    'acidity': 0,
    'indigestion': 1,
    'headache': 2,
    'blurred_and_distorted_vision': 3,
    'excessive_hunger': 4,
    'muscle_weakness': 5,
    'stiff_neck': 6,
    'swelling_joints': 7,
    'movement_stiffness': 8,
    'depression': 9,
    'irritability': 10,
    'visual_disturbances': 11,
    'painful_walking': 12,
    'abdominal_pain': 13,
    'nausea': 14,
    'vomiting': 15,
    'blood_in_mucus': 16,
    'Fatigue': 17,
    'Fever': 18,
    'Dehydration': 19,
    'loss_of_appetite': 20,
    'cramping': 21,
    'blood_in_stool': 22,
    'gnawing': 23,
    'upper_abdomain_pain': 24,
    'fullness_feeling': 25,
    'hiccups': 26,
    'abdominal_bloating': 27,
    'heartburn': 28,
    'belching': 29,
    'burning_ache': 30
}
# Creating a Medical form to intergrate Medicine Recommendation Model
class medForm(FlaskForm):
    gender = SelectField('Gender :', render_kw={"style": "width: 170px;"},choices=[('', ' Select your gender'),(1,' Male'),(0,' Female')],default= None,validators=[DataRequired()])
    age = StringField(validators=[InputRequired()],render_kw={"style": "width: 60px;","placeholder": "Age"})
    severity = SelectField('Severity :',  render_kw={"style": "width: 220px;"},choices=[('', 'Select the level of severity'),(0,'Few days'),(1,'A week'),(2,'Few weeks or more')],default= None,validators=[DataRequired()])
    disease = SelectField('Disease :',  render_kw={"style": "width: 150px;"}, choices=[('', ' Select the diease'),(0, 'Diarrhea'), (1, 'Gastritis'),(2, 'Arthritis'),(3, 'Migraine')],default= None,validators=[DataRequired()])

# Creating Symptoms dropdown Menu for selecting Symptoms
class serviceForm(FlaskForm):
    choices = [('', ' Select a Symptom'), ('acidity', 'Acidity'), ('indigestion', 'Indigestion'),
               ('headache', 'Headache'), ('blurred_and_distorted_vision', 'Blurred and distorted vision'),
               ('excessive_hunger', 'Excessive hunger'), ('muscle_weakness', 'Muscle weakness'),
               ('stiff_neck', 'Stiff neck'), ('swelling_joints', 'Swelling joints'),
               ('movement_stiffness', 'Movement stiffness'), ('depression', 'Depression'),
               ('irritability', 'Irritability'), ('visual_disturbances', 'Visual disturbances'),
               ('painful_walking', 'Painful walking'), ('abdominal_pain', 'Abdominal pain'),
               ('nausea', 'Nausea'), ('vomiting', 'Vomiting'), ('blood_in_mucus', 'Blood in mucus'),
               ('Fatigue', 'Fatigue'), ('Fever', 'Fever'), ('Dehydration', 'Dehydration'),
               ('loss_of_appetite', 'Loss of appetite'), ('cramping', 'Cramping'),
               ('blood_in_stool', 'Blood in stool'), ('gnawing', 'Gnawing'),
               ('upper_abdomain_pain', 'Upper abdomain pain'), ('fullness_feeling', 'Fullness feeling'),
               ('hiccups', 'Hiccups'), ('abdominal_bloating', 'Abdominal bloating'),
               ('heartburn', 'Heartburn'), ('belching', 'Belching'), ('burning_ache', 'Burning ache')]
    symptom1 = SelectField('1st Symptom', choices=choices, default= None,validators=[DataRequired()])
    symptom2 = SelectField('2nd Symptom', choices=choices, default= None,validators=[DataRequired()])
    symptom3 = SelectField('3rd Symptom', choices=choices, default= None,validators=[DataRequired()])
    symptom4 = SelectField('4th Symptom', choices=choices, default= None,validators=[DataRequired()])
    

#Defining a fucntion to convert user inputs and predict
def serviceValidation(selected_symptoms):

    # Convert the selected symptoms to a 30-element list of 1s and 0s
    inputs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    if selected_symptoms[0] in selected_symptoms[1:]:
        flash('2 or more symtop are Same , please select different one.', 'error')
        return "2 or more symtop are Same , please select different one."
    if selected_symptoms[1] in selected_symptoms[2:]:
        flash('2 or more symtop are Same , please select different one.', 'error')
        return "2 or more symtop are Same , please select different one."
    if selected_symptoms[2] in selected_symptoms[3:]:
        flash('2 or more symtop are Same , please select different one.', 'error')
        return "2 or more symtop are Same , please select different one."        
    if selected_symptoms[1] in selected_symptoms[3]:
        flash('2 or more symtop are Same , please select different one.', 'error')
        return "2 or more symtop are Same , please select different one."
    if selected_symptoms[0] in selected_symptoms[3:]:
        flash('2 or more symtop are Same , please select different one.', 'error')
        return "2 or more symtop are Same , please select different one."
    
    for symptom in selected_symptoms:
        if symptom:
            inputs[symptom_mapping[symptom]] = 1

    # convert list to NumPy array
    inputs = np.array(inputs)
    inputs = inputs.reshape(1, -1)


    # Pass the inputs to your machine learning model and retrieve the predicted result
    predicted_result = model_N.predict(inputs)
    print(predicted_result[0])

    # Return the predicted result to the user
    return predicted_result[0]


def medicineValidation(selectedOptions):
    """Defining a function to recommend medicine"""
    inputs = np.array(selectedOptions)  # convert list to NumPy array
    inputs = inputs.reshape(1, -1)
    # Pass the inputs to your machine learning model and retrieve the predicted result
    recommend_Med = model_med.predict(inputs)
    # Return the predicted result to the user
    return recommend_Med[0]


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('service'))
        else:
            # login failed, display error message
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('signin.html', form=form)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.password.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User( firstname=form.firstname.data, lastname=form.lastname.data, age=form.age.data, gender=form.gender.data,email=form.email.data, address=form.address.data, password=hashed_password, pastcondition=form.pastcondition.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))

    return render_template('register.html', form=form)

@app.route('/service', methods=['GET','POST'])
@login_required
def service():
    global predicted_result
    user = User.query.filter_by(id=current_user.id).first()


    form = serviceForm()
    if form.validate_on_submit():
        selectedSymptoms = [form.symptom1.data, form.symptom2.data, form.symptom3.data, form.symptom4.data]
        predicted_result = serviceValidation(selectedSymptoms)

        return render_template('service.html', form=form, predicted_result=predicted_result, id=user.id, name=user.firstname.upper(), age=user.age, gender=user.gender)
    return render_template('service.html', form=form, id=user.id, name=user.firstname.upper(), age=user.age, gender=user.gender)

@app.route('/admin',methods=['POST','GET'])
@login_required
def admin():

    users=User.query.all()
    return render_template('userlist.html',users=users) 




@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    form = adminForm()
    if form.validate_on_submit():
        adminuser = adminUser.query.filter_by(email=form.email.data).first()
        
        if ( adminuser.email == form.email.data and adminuser.password==form.password.data):
            login_user(adminuser)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')
            return render_template('adminsignin.html', form=form)
           
    return render_template('signin.html', form=form)

@app.route('/med_service', methods=['GET','POST'])
@login_required
def med_service():

    form = medForm()
    user = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        selectedOptions = [form.disease.data, form.age.data, form.gender.data, form.severity.data]
        recommend_Med = medicineValidation(selectedOptions)
        print ("recommend_Med" ,recommend_Med)
        '''if "2" in selectedOptions[0]:
            recommend_medd  = arthritis_med["18"]
        if "0" in selectedOptions[0]:
            recommend_medd  = diarrhea_med["15"]
        if "1" in selectedOptions[0]: 
            recommend_medd  = gastritis_med["15"]
        if "3" in selectedOptions[0]: 
            recommend_medd  = migraine_med["20"]'''
            
        #return render_template("med_service.html", form=form, predicted_result=recommend_Med.upper(), id=user.id, name=user.firstname.upper(), age=user.age, gender=user.gender)
        return render_template("med_service.html", form=form, predicted_result= recommend_Med, id=user.id, name=user.firstname.upper(), age=user.age, gender=user.gender)
    return render_template("med_service.html", form=form, id=user.id, name=user.firstname.upper(), age=user.age, gender=user.gender)


@app.route('/doc_service')
def doc_service():  # put application's code here
    user = User.query.filter_by(id=current_user.id).first()

    return render_template("doc_service.html",id=user.id, name=user.firstname.upper(), age=user.age, gender=user.gender)

@app.route('/faq')
def faq():  # put application's code here
    return render_template("faq.html")

if __name__ == '__main__':
    app.run(debug=True)

# ...


   