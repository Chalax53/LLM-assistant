import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
from PIL import Image
import re
import os
from flask import Flask, json, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from json.decoder import JSONDecodeError

load_dotenv()

#PARSES ALL TEXT
class OCRService:
    
    # CHAT GPT - extract relevant data from parsed text - DEPRECATED
    @staticmethod
    def analyze_text_with_gpt(text):
        """Sends extracted text to GPT API for structured extraction."""
        client = OpenAI (
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        prompt = f"""
        Extract the following details from the given text:
        - Full Name
        - Address

        Text:
        {text}

        Respond with a JSON object like this:
        {{
            "full_name": "Alejandro Lopez Castro",
            "address": "123 Fake Street, City, Country"
        }}
        """

        try:
            completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )

            gptResponse = completion.choices[0].message.content

            #remove the `` json...
            if gptResponse.startswith("```json"):
                gptResponse = gptResponse[len("```json"):].strip()
            if gptResponse.endswith("```"):
                gptResponse = gptResponse[:-3].strip()

            print("==GPT RESPONSE===")
            print(gptResponse)
            return gptResponse 

        except Exception as e:
            print(f"Error calling GPT API: {e}")
            return None
