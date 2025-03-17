import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or set it directly: openai.api_key = "YOUR_API_KEY"

def get_openai_response(prompt):
    """
    Sends a prompt to the OpenAI API and returns the generated response.

    Args:
        prompt (str): The input prompt for the chatbot.

    Returns:
        str: The generated response from the OpenAI API, or None if an error occurs.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or another suitable model
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message["content"].strip()
    except openai.error.OpenAIError as e:
        print(f"Error from OpenAI API: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None

def chatbot():
    """
    Runs the chatbot loop, interacting with the user and generating responses.
    """
    print("Welcome to the chatbot! Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        response = get_openai_response(user_input)
        if response:
            print("Chatbot:", response)
        else:
            print("Chatbot: Sorry, I couldn't generate a response.")

if __name__ == "__main__":
    chatbot()
