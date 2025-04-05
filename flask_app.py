from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, make_response
from trip_agents import TripCrew
from dotenv import load_dotenv
import os
import json
import io
from weasyprint import HTML, CSS
from datetime import datetime

import supabase
from supabase.client import Client, ClientOptions
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase_client = supabase.create_client(supabase_url, supabase_key)
os.environ["OTEL_SDK_DISABLED"] = "true"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-secret-key-for-sessions")

# Store generated plans temporarily in memory
# In a production app, use a proper database
generated_plans = {}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def landing():
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response and response.user:
                session['authenticated'] = True
                session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'full_name': response.user.user_metadata.get('full_name', '')
                }
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
        except Exception as e:
            flash(f'Error signing in: {str(e)}', 'error')
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        try:
            response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })
            
            if response and response.user:
                session['authenticated'] = True
                session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'full_name': full_name
                }
                flash('Account created successfully!')
                return redirect(url_for('dashboard'))
            else:
                flash('Error creating account', 'error')
        except Exception as e:
            flash(f'Error signing up: {str(e)}', 'error')
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    try:
        supabase_client.auth.sign_out()
        session.pop('authenticated', None)
        session.pop('user', None)
        flash('You have been logged out')
    except Exception as e:
        flash(f'Error signing out: {str(e)}', 'error')
    
    return redirect(url_for('login'))

@app.route('/generate_plan', methods=['POST'])
@login_required
def generate_plan():
    try:
        # Get data from the frontend
        data = request.json
        OPENAI_API_KEY = data.get('OPENAI_API_KEY')
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        
        # Prepare the inputs for the TripCrew
        inputs = {
            "interests": data.get('interests', []),
            "season": data.get('season'),
            "duration": data.get('duration'),
            "start_city": data.get('start_city'),
            "people": data.get('people')
        }
        
        # Handle the budget - could be a number or a string (Low/Medium/High)
        budget = data.get('budget')
        budget_currency = data.get('budget_currency')
        
        if budget is not None:
            if isinstance(budget, int) or (isinstance(budget, str) and budget.isdigit()):
                # Numeric budget
                inputs["budget"] = f"{budget_currency} {budget}"
            else:
                # Text budget (Low/Medium/High)
                inputs["budget"] = f"{budget} ({budget_currency})"
        
        # Add selected_city only if it exists
        if 'selected_city' in data:
            inputs["selected_city"] = data.get('selected_city')
        
        print(inputs)
        # Run the TripCrew and capture the result
        crew_output = TripCrew(inputs).run()
        
        # Handle different potential return types
        if isinstance(crew_output, str):
            try:
                # Try to parse the string as JSON first
                crew_output = json.loads(crew_output)
            except json.JSONDecodeError:
                try:
                    # If that fails, try ast.literal_eval
                    import ast
                    crew_output = ast.literal_eval(crew_output)
                except:
                    # If all parsing fails, use as is
                    pass
        
        # Generate a unique ID for this plan and store it
        plan_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(hash(str(crew_output)))[0:6]
        generated_plans[plan_id] = {
            "plan": crew_output,
            "inputs": inputs
        }
        
        return jsonify({"success": True, "plan": crew_output, "plan_id": plan_id})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download_pdf', methods=['POST'])
@login_required
def download_pdf():
    try:
        plan_id = request.form.get('plan_id')
        trip_name = request.form.get('trip_name', 'My Trip Plan')
        trip_description = request.form.get('trip_description', '')
        
        # Retrieve the stored plan
        if plan_id not in generated_plans:
            return jsonify({"success": False, "error": "Plan not found"}), 404
        
        plan_data = generated_plans[plan_id]
        plan = plan_data["plan"]
        inputs = plan_data["inputs"]
        
        # Generate HTML content for PDF
        html_content = render_template(
            'plan_pdf.html',
            plan=plan,
            inputs=inputs,
            trip_name=trip_name,
            trip_description=trip_description,
            generated_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Generate PDF from HTML
        html = HTML(string=html_content, base_url=request.url_root)
        pdf_file = io.BytesIO()
        html.write_pdf(pdf_file)
        pdf_file.seek(0)
        
        # Create response with PDF
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{trip_name.replace(" ", "_")}_TravelPlan.pdf"'
        
        return response
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5005)