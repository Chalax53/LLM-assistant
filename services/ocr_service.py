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
    @staticmethod
    def extract_info_from_image(image_file):
        try:
            image = Image.open(image_file).convert("L")  # Convert to grayscale for better OCR
            text = pytesseract.image_to_string(image)
            
            # Normalize text (remove extra spaces & empty lines)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)  # Join back into a clean string

            print("==== CLEAN TEXT ====")
            print(clean_text)
            # SEND THIS TEXT TO CHATGPT AND EXTRACT relevant data.
            gpt_response = OCRService.analyze_text_with_gpt(clean_text)
            
            if not gpt_response:
                return {"error": "No response from GPT."}
            
            # Parse the JSON response from GPT
            try:
                data = json.loads(gpt_response)
                full_name = data.get("full_name")
                address = data.get("address")
                print("Extracted Full Name:", full_name)
                print("Extracted Address:", address)
                return {
                    "full_name": full_name,
                    "address": address
                }
            except JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return {"error": "Invalid JSON format"}, 400

        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}
    
    # CHAT GPT 
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


    @staticmethod
    def extract_info_from_estado_cuenta(image_file):
        try:
            image = Image.open(image_file).convert("L")  # L = grayscale, RGB = colour
            text = pytesseract.image_to_string(image)
            
            # Normalize text (remove extra spaces and empty lines)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)  # Join back into a clean string

            print("==== CLEAN TEXT ====")
            print(clean_text)
            # SEND THIS TEXT TO CHATGPT AND EXTRACT relevant data.
            gpt_response = OCRService.parseCuentaConGPT(clean_text)
            
            if not gpt_response:
                return {"error": "No response from GPT."}
            
            # Parse the JSON response from GPT
            try:
                data = json.loads(gpt_response)
                full_name = data.get("full_name")
                address = data.get("address")
                fecha_corte = data.get("fecha_corte")
                print("Extracted Full Name:", full_name)
                print("Extracted Address:", address)
                print("Extracted Address:", fecha_corte)
                return {
                    "full_name": full_name,
                    "address": address,
                    "fecha_corte": fecha_corte
                }
            except JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return {"error": "Invalid JSON format"}, 400

        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}
        

    @staticmethod
    def parseCuentaConGPT(text):
        """Sends extracted text to GPT API for structured extraction."""
        client = OpenAI (
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        prompt = f"""
        You are an assistant that extracts relevant information from text.
        Task:
        1. Identify date ranges formatted as 'dd al dd de MONTH yyyy' and return only the MONTH.
        2. Extract the following details from the given text:
        - Full Name
        - Address
        - MONTH (from the date range)

        Text:
        {text}

        Respond with a JSON object like this:
        {{
            "full_name": "Alejandro Lopez Castro",
            "address": "123 Fake Street, City, Country"
            "fecha_corte": "Diciembre"
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
        

    @staticmethod
    def extractInfoLocally(image_file):
        """ Locally extracts all words from photo, stores relevant info in local DB """
        try:
            image = Image.open(image_file).convert("L")  # Convert to grayscale for better OCR
            text = pytesseract.image_to_string(image)
            
            # Normalize text (remove extra spaces & empty lines)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)  # Join back into a clean string

            print("==== PARSED TEXT ====")
            print(clean_text)
            
            
            # Parse the JSON response from GPT
            # try:
            #     data = json.loads(gpt_response)
            #     full_name = data.get("full_name")
            #     address = data.get("address")
            #     print("Extracted Full Name:", full_name)
            #     print("Extracted Address:", address)
            #     return {
            #         "full_name": full_name,
            #         "address": address
            #     }
            # except JSONDecodeError as e:
            #     print(f"Error decoding JSON: {e}")
            #     return {"error": "Invalid JSON format"}, 400

        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}