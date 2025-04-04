

import streamlit as st
from trip_agents import TripCrew
from dotenv import load_dotenv
import os
import sys
import json.encoder
import json.decoder
import json
import collections
import collections.abc
import ast
import warnings

os.environ["OTEL_SDK_DISABLED"] = "true"
# Load environment variables
load_dotenv()

def main():
    st.title("🤖 AI Travel Planning Assistant")
    
    # Sidebar for user inputs
    with st.sidebar:
        st.header("Trip Preferences")
        travel_type = st.selectbox("Travel Type", ["Leisure", "Business", "Adventure", "Cultural"])
        interests = st.multiselect("Interests", ["History", "Food", "Nature", "Art", "Shopping", "Nightlife"])
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall"])
        duration = st.slider("Trip Duration (days)", 1, 30, 7)
        budget = st.selectbox("Budget Range", ["Rs5000-10000", "Rs10000-20000", "Rs20000-30000", "Rs30000-50000"])
        user_current_city = st.text_input("Current City")
    
    # Button to generate the travel plan
    if st.button("Generate Travel Plan"):
        inputs = {
            "travel_type": travel_type,
            "interests": interests,
            "season": season,
            "duration": duration,
            "budget": budget,
            "start_city": user_current_city
        }
        
        with st.spinner("🤖 AI Agents are working on your perfect trip..."):
            try:
                # Run the TripCrew and capture the result (a dictionary)
                crew_output = TripCrew(inputs).run()
                print("crew_output:",crew_output)
                #ast literal eval
                crew_output = ast.literal_eval(crew_output)
                st.write("crew_output:",crew_output)
                # Debugging: inspect the raw crew_output structure
                st.subheader("Debugging: Crew Output Data")
                st.write("Type of output:", type(crew_output))
                print("crew_output type:",type(crew_output))
                try:
                    st.json(crew_output)
                except Exception as ex:
                    st.write(crew_output)
                
                # Extract outputs using the keys from the returned dictionary
                city_selection = crew_output.get('city_selection', "❌ No city selection found.")
                city_research = crew_output.get('city_research', "❌ No city research found.")
                itinerary = crew_output.get('itinerary', "❌ No itinerary generated.")
                budget_breakdown = crew_output.get('budget', "❌ No budget breakdown available.")
                
                # Display results in expanders
                st.subheader("Your AI-Generated Travel Plan")
                with st.expander("Recommended Cities"):
                    st.markdown(city_selection)
                with st.expander("Destination Insights"):
                    st.markdown(city_research)
                with st.expander("Detailed Itinerary"):
                    st.markdown(itinerary)
                with st.expander("Budget Breakdown"):
                    st.markdown(budget_breakdown)
                
                st.success("✅ Trip planning completed! Enjoy your journey!")
            except Exception as e:
                st.error(f"An error occurred while processing the results: {e}")

if __name__ == "__main__":
    main()
