import google.generativeai as genai
import json
import logging

class InteractiveMealPlanner:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat = self.model.start_chat(history=[])
        self.current_meal_plan = None
        self.survey_data = None
        self.user_preferences = {}

    def generate_initial_meal_plan(self, survey_data):
        self.survey_data = survey_data
        prompt = f"""
        You are a specialized meal plan generator. Create a personalized 7-day meal plan based on the following information:
        - Weight: {survey_data['weight']} kg
        - Height: {survey_data['height']} cm
        - Gender: {survey_data['gender']}
        - Activity level: {survey_data['activity']}
        - Fitness goal: {survey_data['goal']}

        Adhere to these rules strictly:
        1. Provide exactly 7 days of meal planning, labeled Day 1 through Day 7.
        2.The output must be a valid JSON array containing exactly 7 objects, one for each day
        3. Do not include any introductions, explanations, or dietary advice.
        4. Contains exactly 7 day objects.
        5. Double-check to ensure it complies with the formatting rules

        Format the meal plan as a JSON array with 7 objects, one for each day.
        Each day should have breakfast, lunch, dinner, and two snacks.
        
        Example of correct formatting:
        [
            {{
                "day": "Day 1",
                "meals": {{
                    "breakfast": "Oatmeal with berries and nuts",
                    "morning_snack": "Apple with almond butter",
                    "lunch": "Grilled tofu salad with mixed greens",
                    "afternoon_snack": "Carrot sticks with hummus",
                    "dinner": "Lentil curry with brown rice and roasted vegetables"
                }}
            }},
            // ... (Days 2-7)
        ]
         Format the provided meal plan strictly according to these instructions and example. Do not include any explanations or additional text outside the JSON structure.
        """

        try:
            response = self.chat.send_message(prompt)
            meal_plan = json.loads(response.text)
            if self.validate_meal_plan(meal_plan):
                self.current_meal_plan = meal_plan
                return self.current_meal_plan
            else:
                return self.regenerate_meal_plan()
        except json.JSONDecodeError:
            logging.error("Invalid JSON response from AI model")
            return self.regenerate_meal_plan()
        except Exception as e:
            logging.error(f"Error in generate_initial_meal_plan: {str(e)}")
            return self.generate_default_meal_plan()
        
    def validate_meal_plan(self, meal_plan):
        if not isinstance(meal_plan, list) or len(meal_plan) != 7:
            return False
        for day in meal_plan:
            if 'day' not in day or 'meals' not in day:
                return False
            if len(day['meals']) != 5:
                return False
        return True
    
    def regenerate_meal_plan(self):
        logging.info("Regenerating meal plan")
        return self.generate_initial_meal_plan(self.survey_data)
    
    def update_meal_plan(self, user_request):
        if not self.current_meal_plan or not self.survey_data:
            return "No meal plan or survey data exists. Please generate an initial meal plan first."

        prompt = f"""
        You are a specialized meal planner. Modify the existing 7-day meal plan based on the following information:

        User Information:
        - Weight: {self.survey_data['weight']} kg
        - Height: {self.survey_data['height']} cm
        - Gender: {self.survey_data['gender']}
        - Activity level: {self.survey_data['activity']}
        - Fitness goal: {self.survey_data['goal']}

        Current Meal Plan:
        {json.dumps(self.current_meal_plan, indent=2)}

        This is the specific dietary request from user: {user_request}(Remember to put this into account when creating their meal plan)

        Adhere to these rules strictly:
        1. Maintain the structure of 7 days, labeled Day 1 through Day 7.
        2. Each day must have breakfast, morning_snack, lunch, afternoon_snack, and dinner.
        3. Apply the user's request to the relevant days or the entire week as appropriate.
        4. If the user specifies changes for particular days, only modify those days.
        5. If the user's request is general, apply appropriate changes across all days.
        6. Do not include any explanations or comments in the output.

        Format the updated meal plan as a JSON array with 7 objects, one for each day.
        
        Example of correct formatting:
        [
            {{
                "day": "Day 1",
                "meals": {{
                    "breakfast": "Updated breakfast item",
                    "morning_snack": "Updated morning snack item",
                    "lunch": "Updated lunch item",
                    "afternoon_snack": "Updated afternoon snack item",
                    "dinner": "Updated dinner item"
                }}
            }},
            // ... (Days 2-7)
        ]

        Provide only the updated JSON meal plan, strictly following these instructions and example.
        """
        try:
            response = self.chat.send_message(prompt)
            updated_plan = json.loads(response.text)
            self.current_meal_plan = updated_plan
            return self.current_meal_plan
        except Exception as e:
            logging.error(f"Error in update_meal_plan: {str(e)}")
            return "Failed to update meal plan. Please try again with a different request."

    def get_preferences(self):
        return self.user_preferences
    
    def generate_default_meal_plan(self):
        # Create a simple default meal plan if generation fails
        default_plan = []
        for i in range(1, 8):
            default_plan.append({
                "day": f"Day {i}",
                "meals": {
                    "breakfast": "Oatmeal with fruit",
                    "morning_snack": "Apple",
                    "lunch": "Chicken salad",
                    "afternoon_snack": "Yogurt",
                    "dinner": "Grilled fish with vegetables"
                }
            })
        return default_plan

    def get_meal_plan(self):
        return self.current_meal_plan

    def get_meal_suggestions(self, meal_type, preferences=None):
        prompt = f"""
        Suggest 3 {meal_type} options based on the following preferences:
        {json.dumps(preferences if preferences else self.user_preferences, indent=2)}
        
        Format the response as a JSON array of meal objects, each containing 'name' and 'description'.
        Example:
        [
            {{
                "name": "Vegetarian Stir-Fry",
                "description": "A colorful mix of tofu and fresh vegetables in a light soy sauce."
            }},
            // ... (2 more suggestions)
        ]
        """

        try:
            response = self.chat.send_message(prompt)
            suggestions = json.loads(response.text)
            return suggestions
        except Exception as e:
            logging.error(f"Error in get_meal_suggestions: {str(e)}")
            return [{"name": "Failed to generate suggestions", "description": "Please try again."}]