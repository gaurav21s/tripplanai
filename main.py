import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, make_response
from trip_agents import TripCrew
from dotenv import load_dotenv
import io
import re

# Replace xhtml2pdf with ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, ListFlowable, ListItem
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import supabase
from supabase import create_client
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase_client = create_client(supabase_url, supabase_key)
os.environ["OTEL_SDK_DISABLED"] = "true"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "flask_key")
CORS(app, resources={r"/*": {"origins": "*"}})
# Configure app-specific logging
app.logger.setLevel(logging.INFO)
app.logger.info('Application starting up')

# Store generated plans temporarily in memory
# In a production app, use a proper database
generated_plans = {}

# File to store plans for persistence
PLANS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_plans.json')

# Load existing plans from file if it exists
def load_plans():
    global generated_plans
    try:
        if os.path.exists(PLANS_FILE):
            with open(PLANS_FILE, 'r') as f:
                generated_plans = json.load(f)
            print(f"Loaded {len(generated_plans)} plans from {PLANS_FILE}")
    except Exception as e:
        print(f"Error loading plans: {str(e)}")
        generated_plans = {}

# Save plans to file
def save_plans():
    # Commenting out to prevent saving new plans to generated_plans.json
    """
    try:
        with open(PLANS_FILE, 'w') as f:
            json.dump(generated_plans, f)
        print(f"Saved {len(generated_plans)} plans to {PLANS_FILE}")
    except Exception as e:
        print(f"Error saving plans: {str(e)}")
    """
    pass  # No-op function - we don't want to save new plans

# Load plans at startup
load_plans()

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
    app.logger.info("Loading dashboard page")
    
    # No longer needed since we removed test buttons
    # test_plan_ids = []
    # test_plan_names = {}
    
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/examples')
def examples():
    # In a real implementation, you'd fetch these from a database
    example_itineraries = [
        {
            "id": "bali-adventure",
            "title": "Adventure in Bali",
            "image": "https://images.unsplash.com/photo-1571893544028-06b07af6dade",
            "duration": 7,
            "rating": 4.5,
            "description": "Discover the perfect balance of adventure, culture and relaxation in this tropical paradise."
        },
        {
            "id": "paris-romance",
            "title": "Romantic Paris",
            "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f",
            "duration": 5,
            "rating": 4.8,
            "description": "Explore the city of love with this carefully crafted itinerary for couples."
        },
        {
            "id": "tokyo-explorer",
            "title": "Tokyo Explorer",
            "image": "https://images.unsplash.com/photo-1550597230-fe87251b54fd",
            "duration": 6,
            "rating": 4.7,
            "description": "Dive into the vibrant city of Tokyo, from ancient temples to futuristic skyscrapers."
        }
    ]
    return render_template('examples.html', examples=example_itineraries)

@app.route('/examples/<itinerary_id>')
def view_example(itinerary_id):
    # In a real implementation, you'd fetch this from a database
    example_itineraries = {
        "bali-adventure": {
            "id": "bali-adventure",
            "title": "Adventure in Bali",
            "image": "https://images.unsplash.com/photo-1571893544028-06b07af6dade",
            "duration": 7,
            "rating": 4.5,
            "description": "Discover the perfect balance of adventure, culture and relaxation in this tropical paradise.",
            "days": [
                {
                    "day": 1,
                    "activities": [
                        {"time": "2:00 PM", "activity": "Arrive at Ngurah Rai International Airport", "location": "Denpasar"},
                        {"time": "4:00 PM", "activity": "Check-in at beach resort", "location": "Kuta Beach"}
                    ]
                },
                {
                    "day": 2,
                    "activities": [
                        {"time": "9:00 AM", "activity": "Surfing lessons", "location": "Kuta Beach"},
                        {"time": "3:00 PM", "activity": "Explore trendy shops and restaurants", "location": "Seminyak"}
                    ]
                }
            ],
            "highlights": ["Ubud Monkey Forest", "Tegalalang Rice Terraces", "Mount Batur Sunrise Trek"]
        },
        "paris-romance": {
            "id": "paris-romance",
            "title": "Romantic Paris",
            "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f",
            "duration": 5,
            "rating": 4.8,
            "description": "Explore the city of love with this carefully crafted itinerary for couples."
        },
        "tokyo-explorer": {
            "id": "tokyo-explorer",
            "title": "Tokyo Explorer",
            "image": "https://images.unsplash.com/photo-1550597230-fe87251b54fd",
            "duration": 6,
            "rating": 4.7,
            "description": "Dive into the vibrant city of Tokyo, from ancient temples to futuristic skyscrapers."
        }
    }
    
    itinerary = example_itineraries.get(itinerary_id)
    if not itinerary:
        return render_template('404.html'), 404
    
    return render_template('example_view.html', itinerary=itinerary)

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
        session.pop('openai_api_key', None)  # Remove API key when logging out
        flash('You have been logged out')
    except Exception as e:
        flash(f'Error signing out: {str(e)}', 'error')
    
    return redirect(url_for('login'))

@app.route('/save_api_key', methods=['POST'])
@login_required
def save_api_key():
    try:
        print(f"Save API key request from user: {session.get('user', {}).get('email', 'unknown')}")
        data = request.json
        api_key = data.get('api_key')
        
        if api_key:
            # Check if the API key format is valid (simple check)
            if not api_key.startswith('sk-'):
                print("Invalid API key format detected")
                return jsonify({"success": False, "error": "Invalid API key format. OpenAI API keys typically start with 'sk-'"}), 400
                
            # Save to session
            session['openai_api_key'] = api_key
            print("API key saved successfully to session")
            return jsonify({"success": True, "message": "API key saved successfully"})
        else:
            print("No API key provided in request")
            return jsonify({"success": False, "error": "No API key provided"}), 400
    except Exception as e:
        print(f"Error in save_api_key route: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_api_key', methods=['GET'])
@login_required
def get_api_key():
    try:
        print(f"Get API key request from user: {session.get('user', {}).get('email', 'unknown')}")
        api_key = session.get('openai_api_key', '')
        print(f"API key found in session: {bool(api_key)}")
        return jsonify({"api_key": api_key})
    except Exception as e:
        print(f"Error in get_api_key route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_api_key', methods=['POST'])
@login_required
def clear_api_key():
    session.pop('openai_api_key', None)
    return jsonify({"success": True, "message": "API key cleared successfully"})

@app.route('/generate_plan', methods=['POST'])
@login_required
def generate_plan():
    try:
        # Get data from the frontend
        data = request.json
        print(f"Generate plan request from user: {session.get('user', {}).get('email', 'unknown')}")
        
        # Prioritize API key from request over the one in the session
        OPENAI_API_KEY = data.get('OPENAI_API_KEY') or session.get('openai_api_key')
        
        # Check if we have an API key
        if not OPENAI_API_KEY:
            print("No OpenAI API key available")
            return jsonify({
                "success": False, 
                "error": "No OpenAI API key available. Please provide an API key."
            }), 400
            
        # Log API key presence (don't log the actual key)
        print(f"API key available: {bool(OPENAI_API_KEY)}")
        
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
        
        print(f"Trip inputs: {inputs}")
        
        # Run the TripCrew and capture the result
        try:
            crew_output = TripCrew(inputs, api_key=OPENAI_API_KEY).run()
        except Exception as trip_error:
            print(f"Error in TripCrew.run(): {str(trip_error)}")
            return jsonify({
                "success": False,
                "error": f"Error generating trip plan: {str(trip_error)}"
            }), 500
        
        # Handle different potential return types
        if isinstance(crew_output, str):
            try:
                # Try to parse the string as JSON first
                # Fix JSON with single quotes and other common issues
                fixed_json = crew_output.replace("'", '"')  # Replace single quotes with double quotes
                fixed_json = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', fixed_json)  # Add quotes around property names
                
                # Fix any trailing commas in arrays or objects
                fixed_json = re.sub(r',\s*}', '}', fixed_json)
                fixed_json = re.sub(r',\s*]', ']', fixed_json)
                
                crew_output = json.loads(fixed_json)
            except json.JSONDecodeError as e:
                try:
                    # If that fails, try ast.literal_eval for Python-like dictionaries
                    import ast
                    crew_output = ast.literal_eval(crew_output)
                    
                    # Convert Python dict to valid JSON
                    crew_output = json.loads(json.dumps(crew_output))
                except Exception as ast_error:
                    print(f"JSON parsing error: {e}")
                    print(f"AST parsing error: {ast_error}")
                    # If all parsing fails, return the string as-is in a standard format
                    crew_output = {
                        "error": "Could not parse response",
                        "city_selection": {"selected_city": inputs.get("selected_city", "Your Destination")},
                        "city_research": {
                            "attractions": ["Error parsing trip plan"],
                            "cuisine": ["Please try again with different parameters"],
                            "cultural_norms": ["The AI response format was invalid"],
                            "accommodation_areas": [],
                            "transportation_tips": []
                        },
                        "itinerary": {"daily_schedules": [{"day": 1, "activities": [{"time": "", "activity": "Error generating itinerary", "location": ""}]}]},
                        "budget": {"total_cost": "0"}
                    }
        
        # Generate a unique ID for this plan and store it
        plan_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(hash(str(crew_output)))[0:6]
        generated_plans[plan_id] = {
            "plan": crew_output,
            "inputs": inputs
        }
        
        # Instead of saving to file, keep in memory only
        # save_plans()
        
        # Instead of returning JSON, redirect to the display_trip route
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If it's an AJAX request, return the plan_id so the frontend can redirect
            return jsonify({"success": True, "plan": crew_output, "plan_id": plan_id, "redirect_url": url_for('display_trip', plan_id=plan_id)})
        else:
            # Otherwise redirect directly
            return redirect(url_for('display_trip', plan_id=plan_id))
    
    except Exception as e:
        import traceback
        print(f"Error in generate_plan: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download_pdf', methods=['POST'])
@login_required
def download_pdf():
    try:
        plan_id = request.form.get('plan_id')
        trip_name = request.form.get('trip_name', 'My Trip Plan')
        trip_description = request.form.get('trip_description', '')
        
        # Debug logging
        print(f"Requested download for plan_id: {plan_id}")
        print(f"Available plan IDs: {list(generated_plans.keys())}")
        
        # Retrieve the stored plan
        if plan_id not in generated_plans:
            # Fallback: If the plan isn't found (maybe due to server restart),
            # create a basic plan for the PDF
            print(f"Plan not found with ID: {plan_id}, using fallback plan")
            
            # Create a basic fallback plan
            plan = {
                "city_selection": {"selected_city": trip_name.split(" - ")[0] if " - " in trip_name else trip_name},
                "city_research": {
                    "attractions": ["Visit your planned attractions"],
                    "cuisine": ["Try local cuisine"],
                    "cultural_norms": ["Research local customs before you go"]
                },
                "itinerary": {
                    "daily_schedules": [
                        {
                            "day": 1,
                            "activities": [
                                {"time": "9:00 AM", "activity": "Start your adventure", "location": "Your destination"}
                            ]
                        }
                    ]
                },
                "budget": {
                    "total_cost": "Please refer to your original plan",
                    "accommodation": {"cost": "N/A", "details": "Hotel costs will vary by season and location."},
                    "transportation": {"cost": "N/A", "details": "Transportation costs depend on your travel style."},
                    "meals": {"cost": "N/A", "details": "Budget for meals based on local prices."}
                }
            }
            
            inputs = {
                "people": "Travelers",
                "season": "Your travel season",
                "budget": "Budget range",
                "budget_currency": "USD"
            }
        else:
            plan_data = generated_plans[plan_id]
            plan = plan_data["plan"]
            inputs = plan_data["inputs"]
        
        # Generate PDF using ReportLab
        buffer = io.BytesIO()
        
        # Create the PDF with ReportLab
        create_trip_pdf(
            buffer,
            plan=plan, 
            inputs=inputs,
            trip_name=trip_name,
            trip_description=trip_description,
            generated_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        buffer.seek(0)
        
        # Create response with PDF
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{trip_name.replace(" ", "_")}_TravelPlan.pdf"'
        
        return response
        
    except Exception as e:
        import traceback
        print(f"Error in download_pdf: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

# New function to create PDF using ReportLab
def create_trip_pdf(buffer, plan, inputs, trip_name, trip_description, generated_date):
    # Create PDF with proper margins and title
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=f"{trip_name} - Travel Itinerary"
    )
    
    # Register fonts for more visual appeal
    # We'll use the standard fonts available in ReportLab
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Create custom styles with vibrant colors
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=30,  # Increased font size
        leading=36,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e73be'),  # Rich blue
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Helvetica',
        fontSize=18,  # Increased font size
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#444444')
    ))
    
    styles.add(ParagraphStyle(
        name='Header',
        fontName='Helvetica-Bold',
        fontSize=20,  # Increased font size
        leading=24,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#1e73be'),  # Rich blue
        spaceAfter=12,
    ))
    
    styles.add(ParagraphStyle(
        name='Subheader',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#296baa'),  # Slightly lighter blue
        spaceBefore=12,
        spaceAfter=8
    ))
    
    # Modify existing Normal style
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 11
    styles['Normal'].leading = 15  # Increased leading for better readability
    styles['Normal'].alignment = TA_LEFT
    styles['Normal'].textColor = colors.HexColor('#333333')
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
        textColor=colors.white,
        backColor=colors.HexColor('#1e73be'),  # Rich blue
        borderPadding=(8, 8, 8, 8),  # Increased padding
        borderRadius=6,  # Rounded corners effect
        spaceBefore=15,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='Activity',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#333333')
    ))
    
    styles.add(ParagraphStyle(
        name='ActivityLocation',
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#666666')
    ))
    
    styles.add(ParagraphStyle(
        name='ActivityTransport',
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#1e73be')  # Match primary color
    ))
    
    styles.add(ParagraphStyle(
        name='BudgetTotal',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_RIGHT,
        textColor=colors.white
    ))
    
    styles.add(ParagraphStyle(
        name='BudgetDetails',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333'),
        spaceBefore=5,
        leftIndent=5
    ))
    
    styles.add(ParagraphStyle(
        name='HighlightBox',
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        backColor=colors.HexColor('#f8f9fa'),
        borderColor=colors.HexColor('#e9ecef'),
        borderWidth=1,
        borderPadding=(10, 10, 10, 10),
        borderRadius=5,
        spaceAfter=12
    ))
    
    # Elements for the document
    elements = []
    
    # Cover Page with background color and enhanced design
    elements.append(Spacer(1, 6*cm))  # More space at top
    
    # Trip name in large, bold text
    elements.append(Paragraph(trip_name, styles['CoverTitle']))
    elements.append(Spacer(1, 0.7*cm))
    
    # Subtitle
    elements.append(Paragraph("Travel Itinerary", styles['CoverSubtitle']))
    elements.append(Spacer(1, 2*cm))
    
    # Short description if provided
    if trip_description:
        elements.append(Paragraph(trip_description, ParagraphStyle(
            name='CoverDescription',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        )))
        elements.append(Spacer(1, 1*cm))
    
    # Generation date
    elements.append(Paragraph(f"Generated on: {generated_date}", ParagraphStyle(
        name='DateStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER
    )))
    elements.append(Spacer(1, 8*cm))
    
    # Footer of cover
    elements.append(Paragraph("Created by TravelPlanAI", ParagraphStyle(
        name='CoverFooter',
        parent=styles['CoverSubtitle'],
        fontSize=14,
        textColor=colors.HexColor('#666666')
    )))
    elements.append(PageBreak())
    
    # Trip Information
    elements.append(Paragraph(trip_name, styles['Header']))
    if trip_description:
        elements.append(Paragraph(trip_description, styles['Normal']))
    elements.append(Spacer(1, 0.8*cm))
    
    # Trip metadata with improved styling
    city_name = plan.get('city_selection', {}).get('selected_city', 'Your Destination')
    days_count = len(plan.get('itinerary', {}).get('daily_schedules', [])) or 'N/A'
    
    # Enhanced metadata presentation
    trip_meta_data = [
        ["📅 Duration", "👥 Travelers", "🌦️ Season", "💰 Budget"],
        [
            f"{days_count} days",
            f"{inputs.get('people', 'N/A')}",
            f"{inputs.get('season', 'N/A')}",
            f"{inputs.get('budget', 'N/A')}"
        ]
    ]
    
    meta_table = Table(trip_meta_data, colWidths=[doc.width/4.0]*4)
    meta_table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e73be')),  # Matching blue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Data row styling
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0f7ff')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#333333')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 11),
        
        # Overall table styling
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c0d6f9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWHEIGHT', (0, 0), (-1, 0), 25),
        ('ROWHEIGHT', (0, 1), (-1, 1), 35),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e73be')),  # Border around the table
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),  # Rounded corners
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 1.2*cm))
    
    # Destination Overview if available
    if plan.get('city_research'):
        section_title = f"Destination Overview: {city_name}"
        elements.append(Paragraph(section_title, styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        city_research = plan.get('city_research', {})
        
        # Trip summary in a highlight box
        summary_text = f"{city_name} offers a perfect blend of natural beauty, rich cultural traditions, and adventurous activities. This itinerary takes you through the best experiences, capturing the essence of this amazing place."
        
        elements.append(Paragraph(summary_text, styles['HighlightBox']))
        
        # Create two-column layout for attractions and cuisine
        if city_research.get('attractions') or city_research.get('cuisine'):
            # Container for the two columns
            column_data = []
            
            # First column: Top attractions if available
            left_column = []
            if city_research.get('attractions'):
                left_column.append(Paragraph("Top Attractions", styles['Subheader']))
                attractions_list = []
                for attraction in city_research.get('attractions', []):
                    attractions_list.append(ListItem(Paragraph(attraction, styles['Normal'])))
                
                left_column.append(ListFlowable(attractions_list, bulletType='bullet', leftIndent=20))
            
            # Second column: Local cuisine if available
            right_column = []
            if city_research.get('cuisine'):
                right_column.append(Paragraph("Local Cuisine", styles['Subheader']))
                cuisine_list = []
                for dish in city_research.get('cuisine', []):
                    cuisine_list.append(ListItem(Paragraph(dish, styles['Normal'])))
                
                right_column.append(ListFlowable(cuisine_list, bulletType='bullet', leftIndent=20))
            
            # Create table for two columns
            column_data = [[left_column, right_column]]
            col_table = Table(column_data, colWidths=[doc.width/2.0-10, doc.width/2.0-10])
            col_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            elements.append(col_table)
            elements.append(Spacer(1, 0.8*cm))
            
        # Cultural tips in highlight box if available
        if city_research.get('cultural_norms'):
            elements.append(Paragraph("Cultural Tips", styles['Subheader']))
            cultural_list = []
            for tip in city_research.get('cultural_norms', []):
                cultural_list.append(ListItem(Paragraph(tip, styles['Normal'])))
            
            elements.append(ListFlowable(cultural_list, bulletType='bullet', leftIndent=20))
            elements.append(Spacer(1, 0.8*cm))
            
        # Add page break before itinerary
        elements.append(PageBreak())
    
    # Daily Itinerary with enhanced styling
    if plan.get('itinerary') and plan.get('itinerary', {}).get('daily_schedules'):
        elements.append(Paragraph("Daily Itinerary", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Process each day's schedule
        for day in plan.get('itinerary', {}).get('daily_schedules', []):
            # Day header with day number
            day_num = day.get('day', 'N/A')
            day_header = Paragraph(f"Day {day_num}", styles['Subheader'])
            elements.append(day_header)
            
            # Activities table with improved styling
            activities_data = []
            
            # Add table header with transportation column
            activities_data.append(["Time", "Activity", "Location", "Transportation"])
            
            # Add activities with proper formatting
            for activity in day.get('activities', []):
                transport = activity.get('transportation', activity.get('transport', ''))
                
                # Create formatted transport text with icon
                transport_text = transport if transport and transport != 'N/A' else 'Walking'
                transport_para = Paragraph(f"🚍 {transport_text}", styles['ActivityTransport'])
                
                row = [
                    activity.get('time', 'N/A'),
                    Paragraph(activity.get('activity', 'Activity details not available'), styles['Activity']),
                    Paragraph(activity.get('location', 'Location not specified'), styles['ActivityLocation']),
                    transport_para
                ]
                activities_data.append(row)
            
            # If no activities, add a placeholder row
            if len(activities_data) == 1:  # Only header row exists
                activities_data.append(["", Paragraph("Activities not specified for this day", styles['Activity']), "", ""])
            
            # Create activities table with better styling - adjust column widths to include transportation
            activities_table = Table(activities_data, colWidths=[doc.width*0.10, doc.width*0.35, doc.width*0.25, doc.width*0.30])
            activities_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e73be')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f9ff'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c0d6f9')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#1e73be')),
                ('ROWHEIGHT', (0, 0), (-1, 0), 25),
                ('ROWHEIGHT', (0, 1), (-1, -1), 40),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e73be')),  # Border around the table
            ]))
            
            elements.append(activities_table)
            elements.append(Spacer(1, 1*cm))
        
        # Add page break before budget
        elements.append(PageBreak())
    
    # Budget Section with visual enhancements
    if plan.get('budget'):
        elements.append(Paragraph("Budget Breakdown", styles['SectionTitle']))
        
        budget = plan.get('budget', {})
        
        # Use the user's currency or default to USD
        currency = inputs.get('budget_currency', '').upper()
        if not currency:
            # Check if the budget string contains INR or if start_city contains India/Surat
            budget_str = inputs.get('budget', '').upper()
            start_city = inputs.get('start_city', '').lower()
            if 'INR' in budget_str or 'india' in start_city or 'surat' in start_city:
                currency = 'INR'
            else:
                currency = budget.get('currency', 'USD').upper()
        
        # Show total budget in a prominent box
        if budget.get('total_cost'):
            # Create a striking total cost display
            total_cost = budget.get('total_cost', '0')
            
            # Create visually attractive total budget display
            total_table_data = [
                [Paragraph("Total Estimated Cost", ParagraphStyle(
                    name='TotalLabel',
                    parent=styles['Normal'],
                    fontSize=14,
                    textColor=colors.white,
                    alignment=TA_LEFT
                )), 
                Paragraph(f"{currency} {total_cost}", styles['BudgetTotal'])]
            ]
            
            total_table = Table(total_table_data, colWidths=[doc.width*0.6, doc.width*0.4])
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e73be')), # Main blue color
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e73be')),
            ]))
            
            elements.append(total_table)
            elements.append(Spacer(1, 1*cm))
        
        # Process budget categories with consistent color
        budget_categories = [
            {'key': 'accommodation', 'icon': '🏨', 'label': 'Accommodation'},
            {'key': 'transportation', 'icon': '🚗', 'label': 'Transportation'},
            {'key': 'activities', 'icon': '🎭', 'label': 'Activities & Attractions'},
            {'key': 'meals', 'icon': '🍽️', 'label': 'Food & Dining'},
            {'key': 'emergency_fund', 'icon': '🔐', 'label': 'Emergency Fund'},
            {'key': 'other', 'icon': '📋', 'label': 'Other Expenses'}
        ]
        
        # Use consistent color for all budget categories
        budget_color = '#1e73be'  # Main blue color
        
        for category in budget_categories:
            if category['key'] in budget:
                cat_data = budget.get(category['key'], {})
                
                if not isinstance(cat_data, dict):
                    continue
                
                # Category header row
                cat_header = Paragraph(f"{category['icon']} {category['label']}", styles['Subheader'])
                elements.append(cat_header)
                
                # Category details in a visually appealing box
                cost = cat_data.get('cost', 'N/A')
                details = cat_data.get('details', 'Details not available')
                
                # Category row with consistent color
                cat_table_data = [
                    ["Cost:", f"{currency} {cost}"]
                ]
                
                cat_table = Table(cat_table_data, colWidths=[doc.width*0.2, doc.width*0.8])
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(budget_color)),
                    ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(budget_color + '40')),  # Light version of the color
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                    ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#333333')),
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(budget_color)),
                ]))
                
                elements.append(cat_table)
                
                # Details paragraph
                if details:
                    elements.append(Paragraph(details, styles['BudgetDetails']))
                
                elements.append(Spacer(1, 0.7*cm))
        
        # Add travel costs if they are in a different section
        if plan.get('travel_cost') and plan.get('travel_cost').get('travel'):
            travel_data = plan.get('travel_cost').get('travel')
            
            elements.append(Paragraph("✈️ Travel Costs", styles['Subheader']))
            
            travel_cost = travel_data.get('cost', 'N/A')
            travel_details = travel_data.get('details', 'Details not available')
            
            travel_table_data = [
                ["Cost:", f"{currency} {travel_cost}"]
            ]
            
            travel_table = Table(travel_table_data, colWidths=[doc.width*0.2, doc.width*0.8])
            travel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(budget_color)),  # Use consistent color
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor(budget_color + '40')),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#333333')),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(budget_color)),
            ]))
            
            elements.append(travel_table)
            
            if travel_details:
                elements.append(Paragraph(travel_details, styles['BudgetDetails']))
    
    # Travel Tips
    elements.append(PageBreak())
    elements.append(Paragraph("Travel Tips", styles['SectionTitle']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Two column layout for tips
    tips_data = []
    
    # Column 1: Packing essentials
    col1 = []
    col1.append(Paragraph("Packing Essentials", styles['Subheader']))
    packing_list = [
        ListItem(Paragraph("Passport and travel documents", styles['Normal'])),
        ListItem(Paragraph("Local currency and credit cards", styles['Normal'])),
        ListItem(Paragraph("Weather-appropriate clothing", styles['Normal'])),
        ListItem(Paragraph("Medications and first aid kit", styles['Normal'])),
        ListItem(Paragraph("Power adapters and chargers", styles['Normal']))
    ]
    col1.append(ListFlowable(packing_list, bulletType='bullet', leftIndent=20))
    
    # Column 2: Health & Safety
    col2 = []
    col2.append(Paragraph("Health & Safety", styles['Subheader']))
    health_list = [
        ListItem(Paragraph("Travel insurance information", styles['Normal'])),
        ListItem(Paragraph("Local emergency numbers", styles['Normal'])),
        ListItem(Paragraph("Location of nearest embassy", styles['Normal'])),
        ListItem(Paragraph("Drinking water safety tips", styles['Normal'])),
        ListItem(Paragraph("Sun protection and insect repellent", styles['Normal']))
    ]
    col2.append(ListFlowable(health_list, bulletType='bullet', leftIndent=20))
    
    # Create table for two columns
    tips_data = [[col1, col2]]
    tips_table = Table(tips_data, colWidths=[doc.width/2.0-10, doc.width/2.0-10])
    tips_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(tips_table)
    elements.append(Spacer(1, 1.5*cm))
    
    # Destination-specific tips in highlight box
    elements.append(Paragraph("Local Etiquette", styles['Subheader']))
    elements.append(Paragraph(
        "Remember to respect local customs and traditions. Dress modestly when visiting temples and religious sites. " +
        "Always ask permission before taking photos of locals. Learn a few basic phrases in the local language - it goes a long way!",
        styles['HighlightBox']
    ))
    
    # Footer
    elements.append(Spacer(1, 2*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dddddd'), spaceBefore=0.5*cm, spaceAfter=0.5*cm))
    
    elements.append(Paragraph("This itinerary was created with TravelPlanAI", ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor('#999999')
    )))
    elements.append(Paragraph("Prices and availability may vary. We recommend confirming all details before traveling.", ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor('#999999')
    )))
    elements.append(Paragraph(f"© {datetime.now().year} TravelPlanAI - All rights reserved", ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor('#999999')
    )))
    
    # Build the PDF with custom canvas for better page layout
    doc.build(elements)

@app.route('/display_trip/<plan_id>')
@login_required
def display_trip(plan_id):
    """Display a trip plan using the new simplified template."""
    app.logger.info(f"Displaying trip with ID: {plan_id}")
    
    # First check if the plan is in the in-memory dictionary
    if plan_id in generated_plans:
        plan_data: dict[str, dict[str, dict[str, dict[str, str] | str] | dict[str, str | Unknown] | dict[str, dict[str, str]] | dict[str, list[dict[str, int | list[dict[str, str]]]]] | dict[str, list[str]]] | dict[str, dict[str, Unknown | Unknown] | dict[str, list[dict[str, int | list[dict[str, str]]]]] | dict[str, list[str]] | dict[str, str] | str] | dict[str, dict[str, list[dict[str, int | list[dict[str, str]]]]] | dict[str, list[str]] | dict[str, str] | dict[str, Unknown]] | dict[str, Unknown | Unknown] | dict[str, dict[str, str | Unknown]] | Any] = generated_plans[plan_id]
        return render_template('trip_result.html', plan_data=plan_data, plan_id=plan_id)
    
    # If not in memory, check if it's in the file (for legacy plans only)
    plans = load_plans_from_file()
    
    if plan_id not in plans:
        app.logger.error(f"Plan not found with ID: {plan_id}")
        flash(f"Plan with ID {plan_id} not found.", "error")
        return redirect(url_for('dashboard'))
    
    plan_data = plans[plan_id]
    
    # Render the new template with the plan data
    return render_template('trip_result.html', plan_data=plan_data, plan_id=plan_id)

# Helper functions
def load_plans_from_file():
    """Load all plans from the generated_plans.json file."""
    if not os.path.exists(PLANS_FILE):
        return {}
    
    try:
        with open(PLANS_FILE, 'r') as f:
            plans = json.load(f)
        return plans
    except Exception as e:
        print(f"Error loading plans: {str(e)}")
        return {}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    app.run(host="0.0.0.0", port=port, debug=False)
