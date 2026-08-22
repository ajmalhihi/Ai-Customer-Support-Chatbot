import os
import math
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

# Step 1: Load environment variables from .env file
load_dotenv()

# Step 2: Initialize FastAPI application
app = FastAPI(title="Ajmal Electronics Support Assistant")

# Step 3: Define data models for request bodies
class ChatRequest(BaseModel):
    message: str
    history: list = []

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

# Step 4: System prompt with embedded company information
SYSTEM_PROMPT = """You are Ajmal Electronics' customer support assistant.
Ajmal Electronics is a consumer electronics and home appliances brand. Our products are supplied to and sold through Pittappillil Agencies showrooms across Kerala, as well as their online store.

Guidelines:
- Only answer questions using the company information provided below.
- If you do not know the answer based strictly on this information, state clearly that you don't know and recommend contacting the nearest showroom or customer support, instead of guessing.
- Keep answers SHORT — 2-4 sentences for most questions, not lists, unless the person specifically asks you to list or compare multiple things.
- Write in plain conversational sentences. Do not use markdown formatting like asterisks, bullet points, or bold text — this is a plain chat interface that cannot render markdown.
- Always be warm, polite, and courteous throughout the conversation. Only greet the user with a hello/welcome once, at the very start of the conversation — do not repeat a greeting in later replies, just answer their question directly and politely.
- If a customer's question is broad or vague (like just naming a product category), briefly ask a clarifying question to understand what they're specifically looking for, instead of listing everything at once.
- If asked where to buy or see products in person, explain that Ajmal Electronics products are available at Pittappillil Agencies showrooms and their online store.
- When asked about prices, use the specific product prices listed below. Prices are approximate and can change, so mention that customers should confirm exact pricing at the showroom.
- When asked for the "most expensive" or "top of the line" item in a category, name the flagship/premium model listed for that category, including its striking price — these are real ultra-premium models, so the price is meant to sound impressive.
- If asked about the founder or owner of the company, share only the information provided below. Do not speculate or add any personal details beyond what's listed.

Company Knowledge Base:
- Company Name: Ajmal Electronics
- Description: A consumer electronics and home appliances brand
- Retail Partner: Pittappillil Agencies, a Kerala-based retailer founded in 1990, sells Ajmal Electronics products through its physical showrooms and online store

About the Founder:
- Ajmal Electronics was founded by a young entrepreneur who started the company at just 23 years old.
- The company was founded approximately 4-5 years ago.
- The founder built Ajmal Electronics with a vision of bringing quality, affordable electronics and home appliances to households across Kerala, partnering with established retail networks like Pittappillil Agencies to reach customers effectively.
- No further personal details about the founder are available or shared.

Product Catalog:

TELEVISIONS:
- LG 32-inch HD Smart LED TV — Rs 17,690 (budget/entry-level)
- LG 43-inch 4K Ultra HD Smart LED TV — Rs 30,990
- Samsung 55-inch Crystal 4K Smart TV — Rs 43,990
- LG 55-inch NanoCell 4K Smart TV — Rs 45,999
- Samsung 65-inch Neo QLED 4K Smart TV — Rs 92,999
- LG 65-inch OLED 4K Smart TV — Rs 2,20,000
- FLAGSHIP/Most Expensive TV: LG 88-inch 8K OLED Smart TV — Rs 45,00,000 (approx. 45 lakh), our most premium and largest television, featuring flagship 8K OLED display technology

AIR CONDITIONERS (Split ACs):
- LG 1 Ton 3 Star Inverter Split AC — Rs 32,990
- Samsung 1 Ton 5 Star Inverter Split AC — Rs 37,490
- LG 1.5 Ton 3 Star Inverter Split AC — Rs 35,490
- Samsung 1.5 Ton 5 Star Inverter Split AC — Rs 47,500
- Panasonic 1.5 Ton 5 Star Inverter Split AC — Rs 47,990
- FLAGSHIP/Most Expensive AC: LG Signature 2 Ton Dual Inverter Artist Cooling Series AC — Rs 1,85,000 (approx), our premium designer AC line with artwork-finish panels and advanced dual inverter cooling

REFRIGERATORS:
- LG 260L 3 Star Double Door Refrigerator — Rs 25,500 (entry-level)
- Samsung 236L 3 Star Double Door Refrigerator — Rs 27,990
- LG 340L Frost Free Double Door Refrigerator — Rs 35,000 (approx)
- Samsung/LG Side-by-Side Refrigerator (630L-790L) — starting Rs 1,09,000
- FLAGSHIP/Most Expensive Refrigerator: LG 984L French Door Refrigerator — Rs 5,49,000 (approx. 5.49 lakh), our largest capacity, most premium French door refrigerator

WASHING MACHINES:
- LG 8kg Top Load Fully Automatic Washing Machine — Rs 20,900 (entry-level)
- Samsung 8kg EcoBubble Top Load Washing Machine — Rs 20,490
- LG 10kg Top Load Washing Machine — Rs 32,400
- LG 12kg Front Load Washing Machine with AI Direct Drive — Rs 69,990
- FLAGSHIP/Most Expensive Washing Machine: LG Signature 20kg Front Load Washing Machine — Rs 1,45,000 (approx), our premium ultra-large capacity front load model

Other Categories Available:
- Kitchen appliances and kitchenware
- Bluetooth speakers and mobile phones
- Bed and home furnishing products at select showrooms

Store Information:
- Ajmal Electronics products are sold through Pittappillil Agencies showrooms located across major towns in Kerala.
- Customers can shop in physical showrooms or online via Pittappillil Agencies' website.
- Teleshopping is available for customers who want guided virtual assistance.
- Doorstep delivery is available for online orders.

Frequently Asked Questions (FAQs):
- Where to buy: All Ajmal Electronics products are available at Pittappillil Agencies showrooms and their online store.
- Shopping options: Customers can visit a nearby showroom, shop online, or use teleshopping for guided virtual assistance.
- Delivery: Online orders are delivered to the customer's doorstep.
- Store locator: The exact nearest showroom carrying Ajmal Electronics products can be found using the "Find nearest store" button in this chat.
"""

# Step 5: Real showroom locations carrying Ajmal Electronics products (city-level coordinates)
STORES = [
    {"name": "Ernakulam", "address": "Chitoor Road, Ernakulam", "lat": 9.9816, "lon": 76.2999},
    {"name": "Kakkanad", "address": "Thrikkakkara, Kakkanad, Ernakulam", "lat": 10.0159, "lon": 76.3419},
    {"name": "Angamaly", "address": "TB Jn, Angamaly", "lat": 10.1957, "lon": 76.3861},
    {"name": "Kottayam", "address": "SH Mound, Nagampadam, Kottayam", "lat": 9.5916, "lon": 76.5222},
    {"name": "Thrissur", "address": "Paravattani, Thrissur", "lat": 10.5276, "lon": 76.2144},
    {"name": "Kollam", "address": "Near Ushus Auditorium, Kollam", "lat": 8.8932, "lon": 76.6141},
    {"name": "Kozhikode", "address": "Eranhipalam Mini Bypass, Kozhikode", "lat": 11.2588, "lon": 75.7804},
    {"name": "Thiruvananthapuram", "address": "Paruthipara, Trivandrum", "lat": 8.5241, "lon": 76.9366},
    {"name": "Alappuzha", "address": "Ambalapuzha", "lat": 9.3931, "lon": 76.3339},
    {"name": "Pathanamthitta", "address": "Near Catholic Bishop's House, Pathanamthitta", "lat": 9.2648, "lon": 76.7870},
    {"name": "Kayamkulam", "address": "Kareelakulangara, Kayamkulam", "lat": 9.1728, "lon": 76.5028},
    {"name": "Palakkad", "address": "Shekharipuram, Palakkad", "lat": 10.7867, "lon": 76.6548},
    {"name": "Malappuram (Manjeri)", "address": "TKM Complex, Manjeri", "lat": 11.1197, "lon": 76.1213},
]

# Step 6: Calculate distance in km between two lat/lon points (haversine formula)
def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Step 7: Root route to serve the frontend HTML application
@app.get("/")
def serve_index():
    """Serves the index.html file when users open the root page."""
    return FileResponse("static/index.html")

# Step 8: Define POST /chat endpoint
@app.post("/chat")
def chat_endpoint(payload: ChatRequest):
    """
    Receives user message JSON: {"message": "user's text", "history": [...]}
    Sends the full conversation (history + new message) to Gemini so it
    remembers context from earlier in the chat.
    Returns reply JSON: {"reply": "bot's response"}
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your-api-key-here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not set or configured. Please set your actual API key in the .env file."
        )

    try:
        client = genai.Client(api_key=api_key)

        # Build the full conversation: past messages + the new one
        contents = []
        for turn in payload.history:
            contents.append({
                "role": turn["role"],
                "parts": [{"text": turn["content"]}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": payload.message}]
        })

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        bot_reply = response.text
        return {"reply": bot_reply}

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(error)}")

# Step 9: Define POST /nearest-store endpoint
@app.post("/nearest-store")
def nearest_store(payload: LocationRequest):
    """
    Receives user's coordinates and returns the closest showroom carrying
    Ajmal Electronics products.
    """
    closest_store = None
    shortest_distance = None

    for store in STORES:
        distance = calculate_distance_km(
            payload.latitude, payload.longitude, store["lat"], store["lon"]
        )
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_store = store

    return {
        "name": closest_store["name"],
        "address": closest_store["address"],
        "distance_km": round(shortest_distance, 1)
    }

# Step 10: Mount static folder to serve static files under /static
app.mount("/static", StaticFiles(directory="static"), name="static")