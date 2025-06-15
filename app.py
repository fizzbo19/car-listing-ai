import streamlit as st
import openai

# App title
st.set_page_config(page_title="AI Car Listing Generator", layout="centered")
st.title("🚗 AI Car Listing Generator")

# API Key input
api_key = st.text_input("Enter your OpenAI API key", type="password")

# Inputs
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

# Generate car listing using OpenAI
if submit and api_key:
    openai.api_key = api_key  # ✅ This is how to set the API key

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
    """

    with st.spinner("Generating..."):
        response = openai.ChatCompletion.create(  # ✅ Correct method for v1.x
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful car sales assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        listing = response.choices[0].message.content
        st.subheader("📋 Your Listing:")
        st.code(listing, language='markdown')
        st.download_button("⬇️ Download as Text", listing, file_name="car_listing.txt")
        st.text("Copy the text above or download it as a file.")
