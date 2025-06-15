import streamlit as st
from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials
import json

# Function to append data to Google Sheet
def append_to_google_sheet(data_dict):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Load Google credentials from Streamlit secrets
    credentials_info = json.loads(st.secrets["google"]["credentials_json"])

    creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(creds)

    # Replace with your Google Sheet URL
    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/12UDiRnjQXwxcHFjR3SWdz8lB45-OTGHBzm3YVcExnsQ/edit"
    ).sheet1

    row = [
        data_dict.get("Make"),
        data_dict.get("Model"),
        data_dict.get("Year"),
        data_dict.get("Mileage"),
        data_dict.get("Color"),
        data_dict.get("Fuel Type"),
        data_dict.get("Transmission"),
        data_dict.get("Price"),
        data_dict.get("Features"),
        data_dict.get("Dealer Notes"),
    ]

    sheet.append_row(row)


# Streamlit UI config
st.set_page_config(page_title="🚗 AI Car Listing Generator", layout="centered")
st.title("🚗 AI Car Listing Generator")

# Get OpenAI API key securely from user input
api_key = st.text_input("Enter your OpenAI API key", type="password")

with st.form("car_form"):
    make = st.text_input("Car Make", "BMW")
    model = st.text_input("Model", "X5 M Sport")
    year = st.text_input("Year", "2021")
    mileage = st.text_input("Mileage", "28,000 miles")
    color = st.text_input("Color", "Black")
    fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Hybrid", "Electric"])
    transmission = st.selectbox("Transmission", ["Automatic", "Manual"])
    price = st.text_input("Price", "£45,995")
    features = st.text_area("Key Features", "Panoramic roof, heated seats, M Sport package")
    notes = st.text_area("Dealer Notes (optional)", "Full service history, finance available")
    submit = st.form_submit_button("Generate Listing")

if submit:
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to generate the listing.")
    else:
        try:
            client = OpenAI(api_key=api_key)

            prompt = f"""
You are an expert car sales assistant. Create a compelling, detailed, and professional listing for a car with the following details:

Make: {make}
Model: {model}
Year: {year}
Mileage: {mileage}
Color: {color}
Fuel Type: {fuel}
Transmission: {transmission}
Price: {price}
Features: {features}
Dealer Notes: {notes}

The description should be 100–150 words, highlight the car’s main selling points, and include a friendly yet persuasive tone that builds urgency and trust.
Use separate paragraphs and include relevant emojis to make it more engaging.
"""

            with st.spinner("Generating..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful car sales assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )
                listing = response.choices[0].message.content

            st.subheader("📋 Your Listing:")
            st.markdown(listing)

            st.download_button("⬇️ Download as Text", listing, file_name="car_listing.txt")

            st.text("Copy the text above or download it as a file.")

            car_data = {
                "Make": make,
                "Model": model,
                "Year": year,
                "Mileage": mileage,
                "Color": color,
                "Fuel Type": fuel,
                "Transmission": transmission,
                "Price": price,
                "Features": features,
                "Dealer Notes": notes,
            }
            append_to_google_sheet(car_data)
            st.success("✅ Car details saved to Google Sheets!")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

