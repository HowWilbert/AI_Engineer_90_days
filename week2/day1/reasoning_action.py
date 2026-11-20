import os
import re
from time import sleep
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

# register as a client
client = Groq(api_key=api_key)

# model configurations
model = "openai/gpt-oss-120b"
reasoning_effort = "low"
max_steps = 5

def get_product_price(name):
    name = name.lower().strip()
    if name == "iphone 17":
        return 1000
    elif name == "iphone 15":
        return 500
    else:
        return "Product not found"

def calculator(expression):
    # only allow arithmetic, eval() on raw model output is unsafe
    if not re.fullmatch(r"[\d\s+\-*/().]+", expression):
        return "Calculation Error! Only numbers and + - * / ( ) are allowed."
    try:
        return eval(expression)
    except Exception:
        return "Calculation Error!"

tools = {
    "get_product_price": get_product_price,
    "calculator": calculator
}

system_prompt = """
# Role
You are a shopping assistant.

# Task
Tell the user what a product costs and how much money they will have left after buying it.
Use the tools for every price lookup and every calculation. Never do math in your head.
All prices are in rupees.

# Tools
1. get_product_price(name)
   - Returns the price of the product as a number.
   - Returns "Product not found" if the product does not exist.
2. calculator(expression)
   - Evaluates an arithmetic expression using only numbers and + - * / ( ).
   - Returns the result as a number.

# Rules
1. Each reply contains EITHER one Action OR the Final Answer, never both.
2. Call only one tool per reply, then stop.
3. Never write "Observation:" yourself. The tool result will be sent to you as "Observation: <result>".
4. Never guess or invent a price or a result.
5. If a product is not found, say so in the Final Answer and do not calculate anything.
6. If the user cannot afford the product, tell them how much more money they need.

# Output Format
Thought: what you need to do next
Action: tool_name("argument")

When you have all the information:
Thought: I have all the information
Final Answer: your answer to the user

Pass the argument as a single quoted value:
Action: get_product_price("iPhone 17")
Action: calculator("5000 - 1000")

Never use named arguments:
get_product_price(name="iPhone 17")
calculator(expression="5000 - 1000")

# Example
User: I have 2000 rupees and want to buy an iPhone 15. What will be left?

Thought: I need the price of the iPhone 15.
Action: get_product_price("iPhone 15")

Observation: 500

Thought: I need to subtract 500 from 2000.
Action: calculator("2000 - 500")

Observation: 1500

Thought: I have all the information.
Final Answer: The iPhone 15 costs 500 rupees. After buying it you will have 1500 rupees left.
"""

sys_message = {
    "role": "system",
    "content": system_prompt
}

def run_agent(prompt):
    message = {
        "role": "user",
        "content": prompt
    }
    messages = [sys_message, message]

    for step in range(max_steps):
        print("-"*50)
        print("STEP", step + 1)
        print("-"*50)

        # stop before the model can invent its own Observation
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            reasoning_effort=reasoning_effort,
            temperature=0,
            stop=["Observation:"]
        )

        answer = response.choices[0].message.content or ""

        print(answer)

        # add the LLM response back to messages
        messages.append({
            "role": "assistant",
            "content": answer
        })

        # Action: tool_name(argument) -> groups -> tool_name, argument
        match = re.search(
            r"Action:\s*(\w+)\((.*)\)",
            answer
        )

        # an Action takes priority over a Final Answer written in the same reply
        if match:
            tool_name = match.group(1)
            tool_input = match.group(2).strip().strip("\"'")

            if tool_name in tools:
                observation = tools[tool_name](tool_input)
            else:
                observation = "Tool not found!"

        elif "Final Answer:" in answer:
            return answer.split("Final Answer:")[-1].strip()

        else:
            observation = "No valid Action found. Use the format: Action: tool_name(\"argument\")"

        print("Observation:", observation)

        # give tool result back to LLM
        messages.append({
            "role": "user",
            "content": "Observation: " + str(observation)
        })
        sleep(5)

    print(f"Stopped: no Final Answer after {max_steps} steps.")
    return None


user_prompt = """
I want to buy Iphone 17, I have 500 rupees what will be my balance after i do the purchase ?
"""

if __name__ == "__main__":
    run_agent(user_prompt)
