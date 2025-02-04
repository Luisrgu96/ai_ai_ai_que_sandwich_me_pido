from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from typing import List
from langchain.memory import ConversationBufferMemory

# First, set your Groq API key as an environment variable
import os


# Set your Groq API key
os.environ["GROQ_API_KEY"] = "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"

# Define available sandwiches with more detailed attributes
SANDWICH_LIST = [
    {
        "name": "Club Sandwich",
        "attributes": ["meat", "classic", "filling", "cold", "layered"],
        "ingredients": ["turkey", "bacon", "lettuce", "tomato", "mayonnaise"]
    },
    {
        "name": "Grilled Cheese",
        "attributes": ["vegetarian", "hot", "comfort", "cheesy"],
        "ingredients": ["cheese", "butter", "bread"]
    },
    {
        "name": "Mediterranean Veggie",
        "attributes": ["vegetarian", "healthy", "fresh", "cold"],
        "ingredients": ["hummus", "cucumber", "tomato", "feta", "olives"]
    },
    {
        "name": "Spicy Italian",
        "attributes": ["meat", "spicy", "cold", "bold"],
        "ingredients": ["salami", "pepperoni", "ham", "provolone", "peppers"]
    },
    {
        "name": "PB&J",
        "attributes": ["vegetarian", "sweet", "classic", "simple"],
        "ingredients": ["peanut butter", "jelly"]
    },
    {
        "name": "Tuna Salad",
        "attributes": ["seafood", "creamy", "cold", "protein"],
        "ingredients": ["tuna", "mayonnaise", "celery", "onion"]
    },
    {
        "name": "Buffalo Chicken",
        "attributes": ["meat", "spicy", "hot", "bold"],
        "ingredients": ["chicken", "buffalo sauce", "blue cheese", "lettuce"]
    }
]

# Create the Groq chat model
llm = ChatGroq(
    temperature=0.7,
    model_name="mixtral-8x7b-32768"
)

# Create prompt for asking questions
QUESTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly sandwich profiler. Ask ONE question about the person's food preferences.
    Focus on preferences like:
    - Spice tolerance
    - Dietary restrictions
    - Temperature preference (hot/cold)
    - Favorite ingredients
    
    Ask only ONE question at a time, make it conversational and friendly.
    """),
    ("human", "Previous answers: {previous_answers}\nAsk the next question.")
])

# Create prompt for final recommendation
RECOMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a sandwich expert. Based on the user's preferences, recommend ONE perfect sandwich from this list:
    {sandwich_list}
    
    Consider their answers to the profiling questions:
    {all_answers}
    
    Explain why this sandwich would be perfect for them based on their preferences.
    Be enthusiastic and detailed in your recommendation!""")
])

def main():
    print("🥪 Welcome to the Personalized Sandwich Recommender! 🥪")
    print("I'll ask you a few questions to find your perfect sandwich.")
    
    answers = []
    
    # Ask 3 questions
    for i in range(3):
        # Get the next question
        chain = QUESTION_PROMPT | llm
        question_response = chain.invoke({
            "previous_answers": "\n".join(answers)
        })
        
        # Get user's answer
        user_answer = input("\n" + question_response.content + " ")
        answers.append(f"Q{i+1}: {question_response.content}\nA{i+1}: {user_answer}")
        
    # Format sandwich list for the recommendation
    sandwich_info = "\n".join([
        f"- {s['name']}: {', '.join(s['attributes'])} | Ingredients: {', '.join(s['ingredients'])}"
        for s in SANDWICH_LIST
    ])
    
    # Get recommendation
    chain = RECOMENDATION_PROMPT | llm
    recommendation = chain.invoke({
        "sandwich_list": sandwich_info,
        "all_answers": "\n".join(answers)
    })
    
    print("\n🥪 Your Perfect Sandwich Recommendation 🥪")
    print(recommendation.content)

if __name__ == "__main__":
    main()
