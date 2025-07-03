from crewai import Agent, Task, Crew, LLM
from crewai.flow.flow import Flow, listen, start
# from langchain_groq import ChatGroq
import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()


class TripAgents:
    def __init__(self, model="gpt-4o-mini", api_key=None):
        # Initialize with API key parameter
        self.model = model
        self.api_key = api_key
        
        # Create LLM with provided API key
        self.llm = LLM(
            model=model,
            temperature=0.6,
            api_key=api_key  # Pass the API key to LLM
        )
        
    
    def city_selector_agent(self):
        return Agent(
            role='City Selection and Budget Optimization Expert',
            goal='Identify affordable and realistic destinations based on user budget constraints',
            backstory=(
                "A budget-conscious travel consultant with expertise in affordable destinations and travel cost estimation. "
                "Expert at analyzing travel budgets and determining feasible destinations based on distance, accommodation costs, "
                "and local prices. Known for recommending realistic options that maximize experiences while strictly respecting budget constraints."
            ),
            llm=self.llm,
            verbose=False,
            cache=False
        )
    
    def local_expert_agent(self):
        return Agent(
            role='Local Destination Expert',
            goal="Provide detailed insights about selected cities including top attractions, local customs, and hidden gems",
            backstory="A knowledgeable local guide with first-hand experience of the city's culture and attractions",
            llm=self.llm,
            verbose=False,
            cache=False
        )
    
    def travel_planner_agent(self):
        return Agent(
            role='Professional Travel Planner',
            goal="Create detailed day-by-day itineraries with time allocations, transportation options, and activity sequencing",
            backstory="An experienced travel coordinator with perfect logistical planning skills",
            llm=self.llm,
            verbose=False,
            cache=False
        )
    
    def budget_manager_agent(self):
        return Agent(
            role='Travel Budget Specialist',
            goal="Optimize travel plans to stay within budget while maximizing experience quality",
            backstory="A financial planner specializing in travel budgets and cost optimization",
            llm=self.llm,
            verbose=False,
            cache=False
        )
        
    def budget_check_agent(self):
        return Agent(
            role='Budget and Expense Checker',
            goal="Check if the budget is within the budget expectations",
            backstory="A financial expert who checks if the budget plan is making sense and is within the budget expectations",
            llm=self.llm,
            verbose=False,
            cache=False
        )

    def travel_agent(self):
        return Agent(
            role="Travel Transportation Agent",
            goal="An expert who is best at finding the best prices for flights, trains, buses, ferries, and cabs for given destination and season",
            backstory=(
                "A travel transportation expert with decades of experience in finding the best prices for flights, trains, buses, ferries, and cabs for given destination and season through online booking platforms, google search, and other travel websites"),
            llm=self.llm,
            verbose=False,
            cache=False
        )
        
        
class TripTasks:
    def __init__(self):
        pass
    
    def city_selection_task(self, agent, inputs):
        return Task(
            name="city_selection",
            description=(
                f"Analyze user preferences, current city, budget, duration, and select the best destination:\n"
                f"- Interests: {inputs['interests']}\n"
                f"- Season: {inputs['season']}\n"
                f"- User current city: {inputs['start_city']}\n"
                f"- Budget: {inputs['budget']}\n"
                f"- Duration: {inputs['duration']}\n"
                f"- No of People: {inputs['people']}\n"
                "STRICT BUDGET ANALYSIS RULES:\n"
                "1. First, calculate the TOTAL available budget: Parse the currency and amount from the budget input.\n"
                "2. Then, calculate the budget PER PERSON: total_budget / number_of_people.\n"
                "3. Calculate a REALISTIC travel radius based on budget:\n"
                "   - VERY LOW budget (e.g., under 5,000 INR per person): Only suggest destinations within 100km of start_city\n"
                "   - LOW budget (e.g., 10,000-20,000 INR per person): Only suggest destinations within 500km of start_city\n"
                "   - MEDIUM budget: Regional destinations within the same country or neighboring countries\n"
                "   - HIGH budget: Top Destination in the same country or International destinations are acceptable\n"
                "4. Estimate and reserve MINIMUM COSTS for these essential components:\n"
                "   - Transport costs TO and FROM destination (research realistic costs)\n"
                "   - Accommodation costs for the entire duration (based on local rates)\n"
                "   - Local transportation costs\n"
                "   - Food costs (at least 3 meals per day)\n"
                "   - Basic activity costs related to stated interests\n"
                "   - Emergency fund (10% of total budget)\n"
                "5. Only suggest a destination if ALL these components can be covered within the budget.\n"
                "6. For low budgets, prefer:\n"
                "   - Nearby destinations to minimize travel costs\n"
                "   - Off-season timing when applicable\n"
                "   - Less touristy alternatives to popular destinations\n"
                "   - Destinations known for affordability\n"
                "7. For High Budget you can also suggest big famous international cities."
                "Output: Provide 1 city option with a detailed rationale.\n"
                "- Be crisp and concise\n"
                "- Explicitly state why the city fits within budget with rough cost estimates\n"
                "- Do not include any other text or Note: or comments in your response\n"
            ),
            agent=agent,
            expected_output="""
            {
                "selected_city": "string", 
                "rationale": "string",
            }
            """
        )
    
    def city_research_task(self, agent, city, inputs):
        return Task(
            name="city_research",
            description=(
                f"Provide detailed quick insights about {city} including:\n"
                "- Top and famous attractions\n"
                f"- Tips for {city} based on the season {inputs['season']}\n"
                "- Local cuisine highlights\n"
                "- Cultural norms/etiquette\n"
                "- Recommended accommodation areas\n"
                "- Transportation tips\n"
                "- Be detailed and accurate\n"
                "- Do not include any other irrelevant text or Note: or comments in your response\n"
            ),
            agent=agent,
            expected_output="""
            {
                "attractions": ["string"],
                "cuisine": ["string"],
                "cultural_norms": ["string"],
                "accommodation_areas": ["string"],
                "transportation_tips": ["string"]
            }
            """
        )
    
    def itinerary_creation_task(self, agent, inputs, city_research):
        return Task(
            name="itinerary",
            description=(
                f"Create a {inputs['duration']}-day itinerary for {inputs['people']} people, keeping the interests list {inputs['interests']} in mind including:\n"
                "- Daily schedule with time (24 hours format) allocations\n"
                "- Activity sequencing\n"
                "- Transportation between locations\n"
                "- Meal planning suggestions(Breakfast: 07:00 – 09:00, Lunch: 12:00 – 14:00, Dinner: 19:00 – 21:00)\n"
                "- Be crisp and concise\n"
                "- Do not include any other text or Note: or comments in your response\n"
            ),
            agent=agent,
            context=[city_research],
            expected_output="""
            {
                "daily_schedules": [
                    {
                        "day": "integer",
                        "activities": [
                            {
                                "time": "string",
                                "activity": "string",
                                "location": "string",
                                "transportation": "string"
                            }
                        ]
                    }
                ]
            }
            """
        )
    
    def budget_planning_task(self, agent, inputs, itinerary,selected_city):
        return Task(
            name="budget_plan",
            description=(
               f"Create a comprehensive, accurate budget plan for a {inputs['duration']}-day trip with {inputs['people']} people from {inputs['start_city']} to {selected_city} with a total budget of {inputs['budget']}:\n"
                "ESSENTIAL REQUIREMENTS:\n"
                "1. Research CURRENT, REAL prices from multiple sources for each category:\n"
                "   - For accommodation: Check booking platforms AND direct hotel/hostel rates\n"
                "   - For activities: Check official attraction websites for current pricing\n"
                "2. Include ALL necessary expenses:\n"
                "   - Transportation costs only for cabs, taxis and auto rickshaws, bike ride, tuktuk etc within the destination city\n"
                "   - ALL local transportation mentioned in the itinerary\n"
                "   - Accommodation for the ENTIRE duration (not just per night)\n"
                "   - Entry fees for ALL activities in the itinerary\n"
                "   - Realistic food costs (breakfast, lunch, dinner) based on local prices\n"
                "   - Emergency fund\n"
                "   - Visa fees if applicable\n"
                "3. Provide SPECIFIC breakdowns:\n"
                "   - Transportation: Cost per person, company/service names, route details\n"
                "   - Accommodation: Total cost for entire stay, type of accommodation, location\n"
                "   - Activities: Individual entry costs for each attraction in the itinerary\n"
                "   - Meals: Estimated cost per meal based on local restaurant prices\n"
                "4. Double-check that total cost DOES NOT exceed the stated budget\n"
                "5. Be HONEST and REALISTIC - do not underestimate costs\n"
                "- Do not include any other text or Note: or comments in your response\n"
            ),
            agent=agent,
            context=[itinerary],
            expected_output="""
            {
                "accommodation": {"cost": "number", "details": "string"},
                "transportation": {"cost": "number", "details": "string"},
                "activities": {"cost": "number", "details": "string"},
                "meals": {"cost": "number", "details": "string"},
                "emergency_fund": {"cost": "number", "details": "string = Allocation for unforeseen expenses"},
                "total_cost": "number(should be equal to all the expenses)"
            }
            """        
        )
        
    def budget_check_task(self, agent, inputs, budget_plan,selected_city):
        return Task(
            name="budget_check",
            description=(
                f"Perform a rigorous verification of the budget plan for a {inputs['duration']}-day trip with {inputs['people']} people from {inputs['start_city']} to {selected_city} with a total budget of {inputs['budget']}:\n"
                "VERIFICATION REQUIREMENTS:\n"
                "1. Cross-check EVERY cost estimate against CURRENT real-world prices:\n"
                "   - Accommodation: Check rates on Booking.com, Airbnb, Agoda, OYO, and hotel websites\n"
                "     * Verify availability for the actual dates of travel\n"
                "     * Check if rates include taxes and fees\n"
                "   - Activities: Check official attraction websites for current pricing\n"
                "   - Meals: Research actual restaurant prices in the destination\n"
                "2. Flag ANY unrealistic estimates with corrections:\n"
                "   - If accommodation quality seems unrealistic for the price, note this\n"
                "   - If meal budgets don't align with local costs, provide adjustments\n"
                "3. Verify mathematical accuracy:\n"
                "   - Ensure ALL calculations are correct\n"
                "   - Confirm the total equals the sum of all components\n"
                "5. Be RIGOROUS and THOROUGH - this is the final verification to protect the traveler\n"
                "- Do not include any other text or Note: or comments in your response\n"
            ),
            agent=agent,
            context=[budget_plan],
            expected_output="""
            {
                "accommodation": {"cost": "number", "details": "string"},
                "transportation": {"cost": "number", "details": "string"},
                "activities": {"cost": "number", "details": "string"},
                "meals": {"cost": "number", "details": "string"},
                "emergency_fund": {"cost": "number", "details": "fix string = Allocation for unforeseen expenses"},
                "total_cost": "number(should be equal to all the expenses)",
            }
            """        
        )
        
    def travel_agent_task(self, agent, inputs, selected_city):
        return Task(
            name="travel_agent",
            description=(
                f"Find the best prices for flights or trains or buses or ferries or cabs for {selected_city} during {inputs['season']} season from start city:{inputs['start_city']} for {inputs['people']} people.\n"
                "Use google search and online booking platforms to find the best prices.\n"
                f"Provide the cost for round trip ticket for {inputs['people']} people.\n"
                "Provide the cost for round trip ticket from qouted websites/ platforms/ google search results.\n"
                "Travel cost is different and excluded from the budget plan and totol cost.\n"
                f"Also give the total cost in the {inputs['budget']} currency.\n"
                "- Do not include any other text or Note: or comments in your response\n"
            ),
            agent=agent,
            expected_output="""
            {
                "travel": {"cost": "number", "details": "string = (flight/train/bus/other_transportation round trip ticket cost from qouted websites) and This cost in not included in the budget plan and total cost"},
            }
            """
        )

class TripFlow(Flow):
    def __init__(self, inputs={}, api_key=None, model="gpt-4o-mini"):
        super().__init__()
        self.llm = LLM(
            model=model,
            temperature=0.6,
            api_key=api_key  # Pass API key to LLM
        )
        self.inputs = inputs
        self.api_key = api_key
        self.model = model
    
    @start()
    def process_city(self):
        if self.inputs.get('selected_city'):
            # User provided a city
            return self.inputs['selected_city']
        else:
            # No city provided, use city selector agent
            agents = TripAgents()
            tasks = TripTasks()
            
            city_selector = agents.city_selector_agent()
            select_cities = tasks.city_selection_task(city_selector, self.inputs)
            
            crew = Crew(
                agents=[city_selector],
                tasks=[select_cities],
                verbose=False,
                llm=self.llm
            )
            
            result = crew.kickoff()
            if hasattr(result, "tasks_output") and result.tasks_output:
                try:
                    city_data = json.loads(result.tasks_output[0].raw)
                    return city_data['selected_city']
                except:
                    return "Paris"  # Fallback default
            return "Paris"  # Fallback default

class TripCrew:
    def __init__(self, inputs, api_key=None, model="gpt-4o-mini"):
        self.inputs = inputs
        self.api_key = api_key
        self.model = model
        
        # Check if API key is provided
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set API key in environment variables as backup
        os.environ["OPENAI_API_KEY"] = api_key
            
        # Initialize LLM with API key
        self.llm = LLM(
            model=model,
            temperature=0.6,
            api_key=api_key
        )
        
    def run(self):
        try:
            # Initialize flow to handle city selection
            flow = TripFlow(inputs=self.inputs, api_key=self.api_key, model=self.model)
            selected_city = flow.kickoff()
            
            # Validate selected city
            if not selected_city:
                selected_city = "Paris"  # Default fallback
            
            agents = TripAgents(api_key=self.api_key, model=self.model)
            tasks = TripTasks()
            
            # Create Agents
            local_expert = agents.local_expert_agent()
            travel_planner = agents.travel_planner_agent()
            budget_manager = agents.budget_manager_agent()
            budget_check = agents.budget_check_agent()
            travel_agent = agents.travel_agent()
            
            # Create Tasks with selected city
            research_city = tasks.city_research_task(local_expert, selected_city, self.inputs)
            create_itinerary = tasks.itinerary_creation_task(travel_planner, self.inputs, research_city)
            budget_plan = tasks.budget_planning_task(budget_manager, self.inputs, create_itinerary, selected_city)
            check_budget = tasks.budget_check_task(budget_check, self.inputs, budget_plan, selected_city)
            travel_cost = tasks.travel_agent_task(travel_agent, self.inputs, selected_city)
            
            # Assemble Crew and run remaining tasks
            crew = Crew(
                agents=[local_expert, travel_planner, budget_manager, budget_check, travel_agent],
                tasks=[research_city, create_itinerary, budget_plan, check_budget, travel_cost],
                verbose=True,  # Set to True for debugging
                planning=True,
                planning_llm=self.llm,
                cache=False,
            )
            
            result = crew.kickoff()
            
            # Process results with error handling
            if hasattr(result, "tasks_output"):
                tasks_list = result.tasks_output
                final_result = {
                    "city_selection": {"selected_city": selected_city},
                }
                
                # Safely parse each task output
                try:
                    if len(tasks_list) > 0 and tasks_list[0].raw:
                        final_result["city_research"] = json.loads(tasks_list[0].raw)
                    else:
                        final_result["city_research"] = {"attractions": ["No attractions found"], "cuisine": ["No cuisine information available"], "cultural_norms": ["No cultural information available"]}
                except Exception as e:
                    print(f"Error parsing city research: {str(e)}")
                    final_result["city_research"] = {"attractions": ["Error loading attractions"], "cuisine": ["Error loading cuisine"], "cultural_norms": ["Error loading cultural information"]}
                
                try:
                    if len(tasks_list) > 1 and tasks_list[1].raw:
                        final_result["itinerary"] = json.loads(tasks_list[1].raw)
                    else:
                        final_result["itinerary"] = {"daily_schedules": [{"day": 1, "activities": [{"time": "9:00", "activity": "No itinerary available", "location": ""}]}]}
                except Exception as e:
                    print(f"Error parsing itinerary: {str(e)}")
                    final_result["itinerary"] = {"daily_schedules": [{"day": 1, "activities": [{"time": "9:00", "activity": "Error loading itinerary", "location": ""}]}]}
                
                try:
                    if len(tasks_list) > 3 and tasks_list[3].raw:
                        final_result["budget"] = json.loads(tasks_list[3].raw)
                    elif len(tasks_list) > 2 and tasks_list[2].raw:
                        final_result["budget"] = json.loads(tasks_list[2].raw)
                    else:
                        final_result["budget"] = {"total_cost": "0", "accommodation": {"cost": "0", "details": "No budget information available"}}
                except Exception as e:
                    print(f"Error parsing budget: {str(e)}")
                    final_result["budget"] = {"total_cost": "0", "accommodation": {"cost": "0", "details": "Error loading budget information"}}
                
                try:
                    if len(tasks_list) > 4 and tasks_list[4].raw:
                        final_result["travel_cost"] = json.loads(tasks_list[4].raw)
                    else:
                        final_result["travel_cost"] = {"travel": {"cost": "0", "details": "No travel cost information available"}}
                except Exception as e:
                    print(f"Error parsing travel cost: {str(e)}")
                    final_result["travel_cost"] = {"travel": {"cost": "0", "details": "Error loading travel cost information"}}
            else:
                final_result = {
                    "city_selection": {"selected_city": selected_city},
                    "city_research": {"attractions": ["No attractions found"], "cuisine": ["No cuisine information available"], "cultural_norms": ["No cultural information available"]},
                    "itinerary": {"daily_schedules": [{"day": 1, "activities": [{"time": "9:00", "activity": "No itinerary available", "location": ""}]}]},
                    "budget": {"total_cost": "0", "accommodation": {"cost": "0", "details": "No budget information available"}},
                    "travel_cost": {"travel": {"cost": "0", "details": "No travel cost information available"}}
                }
                
            return final_result
            
        except Exception as e:
            print(f"Error in TripCrew.run(): {str(e)}")
            # Return a fallback response structure
            return {
                "city_selection": {"selected_city": self.inputs.get('selected_city', 'Your Destination')},
                "city_research": {
                    "attractions": ["Error generating trip plan"],
                    "cuisine": ["Please try again with different parameters"],
                    "cultural_norms": ["An error occurred: " + str(e)],
                    "accommodation_areas": [],
                    "transportation_tips": []
                },
                "itinerary": {"daily_schedules": [{"day": 1, "activities": [{"time": "", "activity": "Error generating itinerary", "location": ""}]}]},
                "budget": {"total_cost": "0"}
            }

# With user-specified city
# inputs = {
#     'selected_city': 'Phu Quoc, Vietnam',  # Optional
#     'interests': ['culture', 'food'],
#     'season': 'summer',
#     'duration': '5',
#     'budget': 'medium (inr)',
#     'people': '2',
#     'start_city': "Surat,India"
# }

# # Without user-specified city
# inputs = {
#     'interests': ['wildlife', 'nature'],
#     'season': 'Rainy',
#     'duration': '3',
#     'budget': 'Rs 20000 - Rs 30000',
#     'start_city': 'Delhi',
#     'people': '2'
# }

# trip_crew = TripCrew(inputs)
# result = trip_crew.run()
# print(result)