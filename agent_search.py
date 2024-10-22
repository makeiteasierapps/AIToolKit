import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, initialize_agent, load_tools
from langchain import OpenAI, SerpAPIWrapper
from langchain.utilities import ApifyWrapper

from langchain.utilities import ApifyWrapper
from langchain.document_loaders.base import Document
from langchain.indexes import VectorstoreIndexCreator

load_dotenv()
os.environ.get("OPENAI_API_KEY")
os.environ.get('SERPAPI_API_KEY')
os.environ.get('APIFY_API_TOKEN')
llm = OpenAI(temperature = 0)

# # Initialize the ApifyWrapper with your API token
# apify = ApifyWrapper()

# # Run the Website Content Crawler actor and fetch its results into a LangChain document loader
# loader = apify.call_actor(
#     actor_id="apify/website-content-crawler",
#     run_input={"startUrls": [{"url": "https://python.langchain.com/en/latest/"}]},
#     dataset_mapping_function=lambda item: Document(
#         page_content=item["text"] or "", metadata={"source": item["url"]}
#     ),
# )

# # Initialize the vector index from the crawled documents
# index = VectorstoreIndexCreator().from_loaders([loader])

# # Query the vector index
# query = "What is LangChain?"
# result = index.query_with_sources(query)

# print(result["answer"])
# print(result["sources"])


# Set up Apify
apify = ApifyWrapper()
# Define custom tools

apify_tool = Tool(
    name="Apify",
    func=apify.call_actor,
    description="useful for extracting content from web pages"
)


tools = load_tools(['serpapi', apify_tool])

# Initializes the agent
agent = initialize_agent(tools, llm, agent='zero-shot-react-description', verbose=True)

response = agent.run('Find a website that has an article about the brand Bad Birdie, Return a description and a link to the article')
print(response)


'''
# create custom prompt templates
prompt = PromptTemplate(
    input_variables = ['food'],
    template = "What are 5 vacation destinations for someone who likes to eat {food}",
)

print(llm(prompt.format(food = 'bar-b-q')))


text = "What are 5 vacation destinations for someone that likes to eat pasta? and give me a recipe"
print(llm(text))
'''







