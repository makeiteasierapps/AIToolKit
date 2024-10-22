from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_parsed_data(data):
    data_without_whitespace = ''.join(data.split())
    prompt = f"I would like you to parse json data to an easy to read format. Next to each line provide the python code to access that data. I need this also formatted to be displayed on my website so wrap the data in html elements. Here is the data: {data_without_whitespace}"
    
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "\n\n<ul>\n  <li><strong>Name:</strong> John Smith <code>(data['name'])</code></li>\n<li>\n<strong>Address:</strong>\n<ul style=\"color:gray;\">\n      <li>Street: 123 Main St <code>(data['address']['street'])</code></li>\n      <li>City: Anytown <code>(data['address']['city'])</code></li>\n      <li>State: CA <code>(data['address']['state'])</code></li>\n      <li>Zip: 12345 <code>(data['address']['zip'])</code></li>\n    </ul>\n  </li>\n  <li>\n    <strong>Phone Numbers:</strong>\n    <ul style=\"color: gray;\">\n      <li>Home: 555-1234 <code>(data['phone_numbers'][0]['number'])</code></li>\n      <li>Work: 555-5678 <code>(data['phone_numbers'][1]['number'])</code></li>\n    </ul>\n  </li>\n  <li><strong>Is Active:</strong> True <code>(data['is_active'])</code></li>\n</ul>"}
        ],
        temperature = 0,
        max_tokens = 2000,
        top_p = 0,
        frequency_penalty = 0,
        presence_penalty = 0 
    )
    print(data)
    print(response)
    
    return response['choices'][0]['message']['content']




