import streamlit as st
from trip_agents import TripCrew
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt
import numpy as np
# Load environment variables
load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true"

def main():
    st.title("🤖 AI Travel Planning Assistant")
    
    # Sidebar for user inputs
    with st.sidebar:
        st.header("Trip Preferences")
        travel_type = st.selectbox("Travel Type", ["Leisure", "Business", "Adventure", "Cultural"])
        interests = st.multiselect("Interests", ["History", "Food", "Nature", "Art", "Shopping", "Nightlife"])
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall"])
        duration = st.slider("Trip Duration (days)", 1, 30, 7)
        budget_currency = st.selectbox("Budget Currency", ["INR", "USD", "EUR", "GBP"])
        budget = st.number_input("Budget Amount", min_value=1000, max_value=100000, value=5000, step=1000)
        user_current_city = st.text_input("Current City")

        budget_in_currency = str(budget_currency) + " " + str(budget)
    # Button to generate the travel plan
    if st.button("Generate Travel Plan"):
        inputs = {
            "travel_type": travel_type,
            "interests": interests,
            "season": season,
            "duration": duration,
            "budget": budget_in_currency,
            "start_city": user_current_city
        }
        
        with st.spinner("🤖 AI Agents are working on your perfect trip..."):
            try:
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
                
                # Display the travel plan
                display_travel_plan(crew_output)
                
                st.success("✅ Trip planning completed! Enjoy your journey!")
            except Exception as e:
                st.error(f"An error occurred while processing the results: {e}")

def display_travel_plan(data):
    """Format and display the travel plan data in a user-friendly way"""
    st.subheader("Your AI-Generated Travel Plan")
    
    # Destination Section
    st.header("🌆 Destination")
    if 'city_selection' in data and 'selected_city' in data['city_selection']:
        st.subheader(data['city_selection']['selected_city'])
    else:
        st.write("No destination selected")
    
    # City Research Section
    if 'city_research' in data:
        research = data['city_research']
        
        with st.expander("🔍 Destination Insights", expanded=True):
            # Attractions
            if 'attractions' in research:
                st.subheader("Must-See Attractions")
                for attraction in research['attractions']:
                    st.write(f"• {attraction}")
            
            # Cuisine
            if 'cuisine' in research:
                st.subheader("Local Cuisine")
                for dish in research['cuisine']:
                    st.write(f"• {dish}")
            
            # Cultural Norms
            if 'cultural_norms' in research:
                st.subheader("Cultural Tips")
                for norm in research['cultural_norms']:
                    st.write(f"• {norm}")
            
            # Accommodation Areas
            if 'accommodation_areas' in research:
                st.subheader("Best Areas to Stay")
                for area in research['accommodation_areas']:
                    st.write(f"• {area}")
            
            # Transportation Tips
            if 'transportation_tips' in research:
                st.subheader("Getting Around")
                for tip in research['transportation_tips']:
                    st.write(f"• {tip}")
    
    # Itinerary Section
    if 'itinerary' in data and 'daily_schedules' in data['itinerary']:
        with st.expander("📅 Detailed Itinerary", expanded=True):
            schedules = data['itinerary']['daily_schedules']
            
            for day_plan in schedules:
                st.subheader(f"Day {day_plan['day']}")
                
                for activity in day_plan['activities']:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        st.write(f"**{activity['time']}**")
                    with col2:
                        st.write(f"**{activity['activity']}**")
                        st.write(f"📍 {activity['location']}")
                    with col3:
                        st.write(f"🚗 {activity['transportation']}")
                
                st.divider()
    
    # Budget Section
    if 'budget' in data:
        budget = data['budget']
        
        with st.expander("💰 Budget Breakdown", expanded=True):
            # Create a pie chart of expenses
            if all(k in budget for k in ['accommodation', 'transportation', 'activities', 'meals', 'emergency_fund']):
                
                labels = ['Accommodation', 'Transportation', 'Activities', 'Meals', 'Emergency Fund']
                values = [
                    budget['accommodation']['cost'],
                    budget['transportation']['cost'],
                    budget['activities']['cost'],
                    budget['meals']['cost'],
                    budget['emergency_fund']['cost']
                ]
                
                fig, ax = plt.subplots(figsize=(10, 5))
                wedges, texts, autotexts = ax.pie(
                    values, 
                    labels=labels, 
                    autopct='%1.1f%%',
                    textprops={'fontsize': 10}
                )
                ax.set_title('Budget Allocation')
                st.pyplot(fig)
            
            # Display detailed budget information
            col1, col2 = st.columns(2)
            
            with col1:
                if 'total_cost' in budget:
                    st.metric("Total Budget", f"Rs{budget['total_cost']}")
                
                if 'accommodation' in budget:
                    st.subheader("Accommodation")
                    st.write(f"Rs{budget['accommodation']['cost']}")
                    st.write(budget['accommodation']['details'])
                
                if 'transportation' in budget:
                    st.subheader("Transportation")
                    st.write(f"Rs{budget['transportation']['cost']}")
                    st.write(budget['transportation']['details'])
            
            with col2:
                if 'activities' in budget:
                    st.subheader("Activities")
                    st.write(f"Rs{budget['activities']['cost']}")
                    st.write(budget['activities']['details'])
                
                if 'meals' in budget:
                    st.subheader("Meals")
                    st.write(f"Rs{budget['meals']['cost']}")
                    st.write(budget['meals']['details'])
                
                if 'emergency_fund' in budget:
                    st.subheader("Emergency Fund")
                    st.write(f"Rs{budget['emergency_fund']['cost']}")
                    st.write(budget['emergency_fund']['details'])

if __name__ == "__main__":
    main()