import streamlit as st
from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import stripe

# Streamlit UI
st.set_page_config(page_title="🚗 AI Car Listing Generator", layout="centered")
st.title("🚗 AI Car Listing Generator")

# Optional: Show payment success or cancel messages
query_params = st.experimental_get_query_params()

if "success" in query_params:
    st.success("🎉 Payment successful! Your Premium plan is now active.")
elif "canceled" in query_params:
    st.warning("❌ Payment canceled. You can continue with your free plan.")

# Get API key input
api_key = st.text_input("Enter your OpenAI API key", type="password")

# Stripe config
stripe.api_key = st.secrets["stripe"]["secret_key"]
price_id = st.secrets["stripe"]["price_id"]

# Form to collect car details
with st.form("car_form"):
    user_id = st.text_input("Your Business Email or Dealer ID", "")
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

# Function to append data to Google Sheet
def append_to_google_sheet(data_dict):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_info = json.loads(st.secrets["google"]["credentials_json"])
    creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/12UDiRnjQXwxcHFjR3SWdz8lB45-OTGHBzm3YVcExnsQ/edit"
    ).sheet1

    row = [
        data_dict.get("User ID"),
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
        data_dict.get("Timestamp"),
    ]

    sheet.append_row(row)

# Function to check number of listings in current month for a user
def check_usage_this_month(user_id):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_info = json.loads(st.secrets["google"]["credentials_json"])
    creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/12UDiRnjQXwxcHFjR3SWdz8lB45-OTGHBzm3YVcExnsQ/edit"
    ).sheet1
    data = sheet.get_all_records()

    this_month = datetime.now().strftime("%Y-%m")
    count = 0
    for row in data:
        if row.get("User ID") == user_id and row.get("Timestamp", "").startswith(this_month):
            count += 1
    return count

# Simulated usage limit (replace this logic with real user tracking later)
monthly_usage = 3  # Example: 3 listings already used

# Stripe checkout for subscription if user hits limit
if monthly_usage >= 3:
    st.warning("🚫 You've reached your 3 free listings this month.")
    if st.button("💳 Upgrade to Premium (£9.99/month)"):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url="https://car-listing-ai-kyjvkaybulqzjtdejuatq8.streamlit.app?success=true",
                cancel_url="https://car-listing-ai-kyjvkaybulqzjtdejuatq8.streamlit.app?canceled=true",
            )
            st.markdown(
                f"[🔗 Click here to complete subscription]({checkout_session.url})",
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Stripe error: {e}")
    st.stop()

# Main submission logic
if submit:
    if not api_key or not user_id:
        st.warning("⚠️ Please enter both your OpenAI API key and business ID.")
    else:
        try:
            usage_count = check_usage_this_month(user_id)

            if usage_count >= 3:
                st.warning(f"⚠️ You’ve reached your 3 free listings for this month. Please upgrade to continue using this tool.")
            else:
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

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                car_data = {
                    "User ID": user_id,
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
                    "Timestamp": timestamp,
                }
                append_to_google_sheet(car_data)
                st.success(f"✅ Listing generated and saved. You've used {usage_count + 1} out of 3 free listings this month.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")



