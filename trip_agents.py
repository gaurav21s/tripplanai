from crewai import Agent, Task, Crew, LLM
from crewai.flow.flow import Flow, listen, start
from langchain_groq import ChatGroq
import json
import os
import sys
# import litellm
# litellm._turn_on_debug()
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

model = "gpt-4o-mini"

class TripAgents:
    def __init__(self):
        self.llm = LLM(
            model=model,
            temperature=0.6
        )
        
    def city_selector_agent(self):
        return Agent(
            role='City Selection and Geography Expert',
            goal='Identify best cities to visit based on user preferences and specially budget',
            backstory=(
                "An expert travel geographer with extensive knowledge about world cities and local cities and experience."
                "and their cultural, historical, and entertainment offerings"
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
                "Logic to strictly follow:\n"
                "- Prioritize cities that fit **within the given budget**. No city should be recommended if it exceeds the budget when considering travel, stay, and basic expenses.\n"
                "- If budget is low, strictly prefer affordable cities, hidden gems, or lesser-known local destinations that still align with the user's interests.\n"
                "- If the user has many interests, a higher number of people, or a longer trip duration with limited budget, lean more toward cost-effective local or regional experiences.\n"
                "- Only suggest well-known/popular cities if the budget comfortably allows.\n"
                "- Also consider distance from the user's current city to reduce travel cost and recommend cities that optimize value for money.\n"
                "Output: Provide 1 city option with a brief rationale.\n"
                "- Be crisp and concise\n"
                "- Do not include any other text or comments in your response\n"
            ),
            agent=agent,
            expected_output="""
            {
                "selected_city": "string", 
                "rationale": "string"
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
                "- Do not include any other irrelevant text or comments in your response\n"
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
                "- Do not include any other text or comments in your response\n"
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
                f"Create a budget plan for {inputs['budget']} budget from the current city {inputs['start_city']} to the selected city {selected_city} for {inputs['people']} people covering:\n"
                "- Round Trip Flight/Train/Bus costs (make sure to include the cost of the return trip via checking online from multiple sources)\n"
                "- Accommodation costs\n"
                "- Transportation expenses\n"
                "- Activity fees\n"
                "- Meal budget\n"
                "- Emergency funds allocation\n"
                "- Total cost should be equal to all this expenses\n"
                "- Be crisp and concise\n"
                "- Do not include any other text or comments in your response\n"
            ),
            agent=agent,
            context=[itinerary],
            expected_output="""
            {
                "travel": {"cost": "number", "details": "string (flight/train/bus ticket cost)"},
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
                f"Check if the budget is within the budget expectations for {inputs['budget']} budget from the current city {inputs['start_city']} to the selected city {selected_city} for {inputs['people']} people.\n"
                "- Check the travel(flight/train/bus) costs again from multiple sources like (google, makemytrip, expedia, redbus, indigo, and other tourism and flight booking websites etc.)\n"
                "- Check the accommodation costs again from multiple sources like (airbnb, booking.com, agoda, oyo, hotel websites etc.)\n"
                "- Check total costs is actually the total of all the expenses\n"
                "- Correct the budget plan if found any mistakes and then return the correct budget plan\n"
                "- Do not include any other text or comments in your response\n"
            ),
            agent=agent,
            context=[budget_plan],
            expected_output="""
            {
                "travel": {"cost": "number", "details": "string (flight/train/bus ticket cost)"},
                "accommodation": {"cost": "number", "details": "string"},
                "transportation": {"cost": "number", "details": "string"},
                "activities": {"cost": "number", "details": "string"},
                "meals": {"cost": "number", "details": "string"},
                "emergency_fund": {"cost": "number", "details": "string = Allocation for unforeseen expenses"},
                "total_cost": "number(should be equal to all the expenses)",
            }
            """        
        )

class TripFlow(Flow):
    def __init__(self, inputs={}):
        super().__init__()
        self.llm = LLM(
            model=model,
            temperature=0.6
        )
        self.inputs = inputs
    
    @start()
    def process_city(self):
        if self.inputs.get('selected_city'):
            # User provided a city
            return self.inputs['selected_city']
        else:
            print("start flow inputs",self.inputs)
            # No city provided, use city selector agent
            agents = TripAgents()
            tasks = TripTasks()
            
            city_selector = agents.city_selector_agent()
            select_cities = tasks.city_selection_task(city_selector, self.inputs)
            
            crew = Crew(
                agents=[city_selector],
                tasks=[select_cities],
                verbose=True,
                llm=self.llm
            )
            
            result = crew.kickoff()
            if hasattr(result, "tasks_output") and result.tasks_output:
                try:
                    print("result",result)
                    city_data = json.loads(result.tasks_output[0].raw)
                    print("city_data",city_data)
                    return city_data['selected_city']
                except:
                    return "Paris"  # Fallback default
            return "Paris"  # Fallback default

class TripCrew:
    def __init__(self, inputs):
        self.inputs = inputs
        self.llm = LLM(
            model=model,
            temperature=0.6
        )
        
        
    def run(self):
        # Initialize flow to handle city selection
        flow = TripFlow(inputs=self.inputs)
        selected_city = flow.kickoff()
        
        agents = TripAgents()
        tasks = TripTasks()
        
        # Create Agents
        local_expert = agents.local_expert_agent()
        travel_planner = agents.travel_planner_agent()
        budget_manager = agents.budget_manager_agent()
        budget_check = agents.budget_check_agent()
        
        # Create Tasks with selected city
        research_city = tasks.city_research_task(local_expert, selected_city, self.inputs)
        create_itinerary = tasks.itinerary_creation_task(travel_planner, self.inputs, research_city)
        budget_plan = tasks.budget_planning_task(budget_manager, self.inputs, create_itinerary,selected_city)
        check_budget = tasks.budget_check_task(budget_check, self.inputs, budget_plan,selected_city)
        # Assemble Crew and run remaining tasks
        crew = Crew(
            agents=[local_expert, travel_planner, budget_manager, budget_check],
            tasks=[research_city, create_itinerary, budget_plan, check_budget],
            verbose=True,
            planning=True,
            planning_llm=self.llm,
            cache=False,
            output_log_file="log_output"
        )
        
        result = crew.kickoff()
        # print("result:",result)
        # Process results
        if hasattr(result, "tasks_output"):
            tasks_list = result.tasks_output
            final_result = {
                "city_selection": {"selected_city": selected_city},
                "city_research": json.loads(tasks_list[0].raw) if len(tasks_list) > 0 else "❌ No city research found.",
                "itinerary": json.loads(tasks_list[1].raw) if len(tasks_list) > 1 else "❌ No itinerary generated.",
                "budget": json.loads(tasks_list[2].raw) if len(tasks_list) > 2 else "❌ No budget breakdown available."
            }
        else:
            final_result = {}
        # print("final_result:",final_result)
        return final_result

# With user-specified city
# inputs = {
#     'selected_city': 'Phu Quoc, Vietnam',  # Optional
#     'travel_type': 'leisure',
#     'interests': ['culture', 'food'],
#     'season': 'summer',
#     'duration': '5',
#     'budget': 'medium'
# }

# # Without user-specified city
# inputs = {
#     'travel_type': 'adventure',
#     'interests': ['wildlife', 'nature'],
#     'season': 'Rainy',
#     'duration': '3',
#     'budget': 'Rs 20000 - Rs 30000',
#     'start_city': 'Delhi'
# }

# trip_crew = TripCrew(inputs)
# result = trip_crew.run()
# print(result)