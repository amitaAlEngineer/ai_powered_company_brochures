from app import app
from dotenv import load_dotenv
import os
from openai import OpenAI


load_dotenv()

openAI_api_key = os.getenv('OPEN_AI_API_KEY')
MODEL = 'gpt-4o-mini'
openai = OpenAI()


HOST = "http://127.0.0.1/"
PORT = "6302"



# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}