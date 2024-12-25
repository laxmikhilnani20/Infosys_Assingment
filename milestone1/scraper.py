import os
import requests
import json
from typing import List, Generator, Dict
from dataclasses import dataclass
from bs4 import BeautifulSoup
from transformers import pipeline
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

@dataclass
class ScrapedContent:
    text: str
    url: str
    timestamp: str
    status: bool
    error: str = ""
    title: str = ""
    sections: Dict[str, str] = None

class WebScraperChatbot:
    def __init__(self):
        self.API_KEY = "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"
        self.URL = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
        self.scraped_content: ScrapedContent = None
        self.web_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def get_llm_response(self, question: str, context: str) -> str:
        """Get response from Groq API."""
        try:
            prompt = f"""Using the following context, please answer the question. If the answer cannot be found in the context, say so.
            
Context: {context}

Question: {question}

Please provide a detailed, accurate answer based on the context provided. If multiple relevant pieces of information exist, synthesize them into a coherent response."""

            payload = {
                "model": "mixtral-8x7b-32768",  # Using Mixtral model for better performance
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that provides accurate, detailed answers based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,  # Lower temperature for more focused answers
                "max_tokens": 1000,
                "top_p": 0.9
            }

            response = requests.post(self.URL, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            return "Failed to get a response from the API."

        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}"
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def scrape_wikipedia(self, url: str) -> ScrapedContent:
        """Special handling for Wikipedia articles."""
        try:
            response = requests.get(url, headers=self.web_headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.select('.mw-jump-link, .mw-editsection, .reference, .error'):
                element.decompose()

            # Get title
            title = soup.find(id='firstHeading').get_text().strip()
            
            # Get main content
            content_div = soup.find(id='mw-content-text')
            
            # Process sections
            sections = {}
            current_section = "Introduction"
            current_text = []
            
            for element in content_div.find('div', class_='mw-parser-output').children:
                if element.name == 'h2':
                    # Save previous section
                    if current_text:
                        sections[current_section] = ' '.join(current_text)
                    # Start new section
                    current_section = element.get_text().strip()
                    current_text = []
                elif element.name in ['p', 'ul', 'ol']:
                    text = element.get_text().strip()
                    if text:
                        current_text.append(text)
            
            # Save last section
            if current_text:
                sections[current_section] = ' '.join(current_text)
            
            # Combine all text
            full_text = ' '.join(sections.values())
            
            return ScrapedContent(
                text=full_text,
                url=url,
                timestamp=datetime.now().isoformat(),
                status=True,
                title=title,
                sections=sections
            )
        except Exception as e:
            return ScrapedContent("", url, "", False, f"Error processing Wikipedia page: {str(e)}")


    def scrape_website(self, url: str) -> ScrapedContent:
        """Scrape content from a website using Selenium."""
        if not self.validate_url(url):
            return ScrapedContent("", url, "", False, "Invalid URL format")

        if "wikipedia.org" in url.lower():
            return self.scrape_wikipedia(url)

        try:
            options = Options()
            options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            driver.get(url)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
                
            # Extract title
            title = soup.title.string if soup.title else ""
            
            # Extract main content
            content_areas = []
            for tag in ['main', 'article', 'div[class*="content"]', 'div[class*="article"]']:
                content_areas.extend(soup.select(tag))
            
            if content_areas:
                main_content = max(content_areas, key=lambda x: len(x.get_text()))
            else:
                main_content = soup.find('body')
            
            # Extract text
            if main_content:
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol'])
                content = ' '.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            else:
                content = ""
            
            self.scraped_content = ScrapedContent(
                text=content,
                url=url,
                timestamp=datetime.now().isoformat(),
                status=True,
                title=title
            )
            print(f"Scraped website content: {self.scraped_content}")
            return self.scraped_content

        except Exception as e:
            self.scraped_content = ScrapedContent("", url, "", False, f"Error scraping website: {str(e)}")
            return self.scraped_content

    # ...existing code...
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def answer_question(self, question: str) -> str:
        """Answer questions using both scraped content and LLM."""
        if not self.scraped_content or not self.scraped_content.status:
            return "Please scrape a website first using 'scrape:<URL>'"

        try:
            # Get context from scraped content
            context = self.scraped_content.text
            if len(context) > 15000:  # Truncate if too long
                context = context[:15000] + "..."

            # Get response from LLM
            answer = self.get_llm_response(question, context)
            return answer

        except Exception as e:
            return f"Error processing question: {str(e)}"

    def run(self):
        """Main loop for the chatbot."""
        print("\nWelcome to the Web Scraper Chatbot with AI Integration!")
        print("Commands:")
        print("- 'scrape:<URL>' to scrape a website")
        print("- 'source' to show current source URL")
        print("- 'exit' to quit")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Goodbye! Have a great day!")
                    break
                    
                elif user_input.lower() == 'source':
                    if self.scraped_content and self.scraped_content.status:
                        print(f"Current source: {self.scraped_content.url}")
                        if self.scraped_content.title:
                            print(f"Title: {self.scraped_content.title}")
                    else:
                        print("No content has been scraped yet.")
                        
                elif user_input.startswith('scrape:'):
                    url = user_input.split('scrape:', 1)[1].strip()
                    print("Scraping website... Please wait.")
                    self.scraped_content = self.scrape_website(url)
                    
                    if self.scraped_content.status:
                        print(f"Successfully scraped: {self.scraped_content.title or 'Website'}")
                        print("You can now ask questions about the content.")
                    else:
                        print(f"Error: {self.scraped_content.error}")
                        
                else:
                    if not user_input:
                        print("Please enter a question or command.")
                        continue
                        
                    print("Processing your question... Please wait.")
                    answer = self.answer_question(user_input)
                    print(f"\nChatbot: {answer}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye! Have a great day!")
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    chatbot = WebScraperChatbot()
    chatbot.run()