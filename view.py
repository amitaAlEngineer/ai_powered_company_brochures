import os
import requests
import json
from typing import List
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, Response
import time
from IPython.display import Markdown, display, update_display
from config import (
    openAI_api_key,
    MODEL,
    openai,
    headers
)


class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """
    
    def __init__(self ,url):
        self.url =url
        response = requests.get(self.url,headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body , "html.parser")
        self.title = soup.title.string if soup.title else "No Title Found!"
        
        if soup.body:
            for irrelavant in soup.body["script" ,"style","css","image","input"]:
                irrelavant.decompose()
            self.text = soup.body.get_text(separator ="\n" , strip=True)
        else:
            self.text=""
            
        links  = [link.get("href") for link in soup.find_all('a')]
        self.links =[link for link in links if link]
        
        def get_content(self):
            return f"Web page Title : \n {self.title} \n web page content : \n {self.text}\n\n"
        


# we will use GPT 40 mini to see which link is relevant

def get_relevant_links(url):
    website = Website(url)
    
    link_system_prompt = "You are provided with a list of links found on a webpage. \
    You are able to decide which of the links would be most relevant to include in a brochure about the company, \
    such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
    link_system_prompt += "You should respond in JSON as in this example:"
    link_system_prompt += """
    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page": "url": "https://another.full.url/careers"}
        ]
    }
    """
    
    print("\n\n link_system_prompt   :  ",link_system_prompt)
    
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
    Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    
    print("\n\n user_prompt   :  ",user_prompt)
    
    
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": user_prompt}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)


# Make the brochure
def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_relevant_links(url)
    
    print("\n\n Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
    print("\n\n final user prompt  : ",user_prompt)
    return user_prompt
    
    
def stream_brochure(company_name, url):
    
    system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
    Include details of company culture, customers and careers/jobs if you have the information."
    
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
        stream=True
    )
    
    def generate():
        for chunk in stream:
            content = chunk.choices[0].delta.content or ''
            formatted_content = content.replace("```", "")  # Ensure markdown is clean
            yield f"data: {formatted_content}\n\n"
            time.sleep(0.1)

    return Response(generate(), content_type="text/event-stream")



