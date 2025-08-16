import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import datetime

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Local Food Wastage Management System")
st.title("Local Food Wastage Management System")
st.markdown("A platform to connect food providers with those in need.")

# --- Database Setup (runs once per session) ---
@st.cache_resource
def setup_database():
    """
    Loads CSV data into a SQLite database and returns the engine.
    This function is cached to run only once.
    """
    engine = create_engine('sqlite:///food_wastage.db')

    # Load the cleaned data from your CSV files
    try:
        providers_df = pd.read_csv('providers_cleaned.csv')
        receivers_df = pd.read_csv('receivers_cleaned.csv')
        food_listings_df = pd.read_csv('food_listings_cleaned.csv')
        claims_df = pd.read_csv('claims_cleaned.csv')
    except FileNotFoundError:
        st.error("Missing one or more CSV files. Please make sure all four data files are in the same directory as this script.")
        return None

    # Write the dataframes to SQL tables
    providers_df.to_sql('providers', engine, index=False, if_exists='replace')
    receivers_df.to_sql('receivers', engine, index=False, if_exists='replace')
    food_listings_df.to_sql('food_listings', engine, index=False, if_exists='replace')
    claims_df.to_sql('claims', engine, index=False, if_exists='replace')
    
    return engine

# Connect to the database
engine = setup_database()

# --- Functions for fetching data ---
@st.cache_data
def run_query(query):
    """Fetches data from the database using a given SQL query."""
    return pd.read_sql(query, engine)

# --- Tabs for the application ---
tab_dashboard, tab_find, tab_crud, tab_query_runner = st.tabs(["Dashboard & Analysis", "Find Food", "Manage Listings", "SQL Query Runner"])

with tab_dashboard:
    st.header("Project Analysis & Insights")

    # 1. How many food providers and receivers are there in each city?
    st.subheader("1. Providers and Receivers by City")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Providers")
        providers_by_city_query = "SELECT City, COUNT(*) AS TotalProviders FROM providers GROUP BY City ORDER BY TotalProviders DESC;"
        providers_by_city_df = run_query(providers_by_city_query)
        st.dataframe(providers_by_city_df, use_container_width=True)
    with col2:
        st.markdown("#### Receivers")
        receivers_by_city_query = "SELECT City, COUNT(*) AS TotalReceivers FROM receivers GROUP BY City ORDER BY TotalReceivers DESC;"
        receivers_by_city_df = run_query(receivers_by_city_query)
        st.dataframe(receivers_by_city_df, use_container_width=True)

    # 2. Which type of food provider contributes the most food?
    st.subheader("2. Most Contributing Provider Type")
    most_contributing_provider_query = """
        SELECT p.Type, SUM(fl.Quantity) AS TotalQuantity
        FROM providers AS p
        JOIN food_listings AS fl
        ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.Type
        ORDER BY TotalQuantity DESC;
    """
    most_contributing_df = run_query(most_contributing_provider_query)
    st.dataframe(most_contributing_df, use_container_width=True)
    st.bar_chart(most_contributing_df.set_index('Type'))

    # 3. What is the contact information of food providers in a specific city?
    st.subheader("3. Contact Information of Providers by City")
    cities = run_query("SELECT DISTINCT City FROM providers ORDER BY City")['City'].tolist()
    selected_city = st.selectbox("Select a city to find provider contact info:", cities)
    provider_contact_query = f"SELECT Name, Contact FROM providers WHERE City = '{selected_city}';"
    provider_contact_df = run_query(provider_contact_query)
    st.dataframe(provider_contact_df, use_container_width=True)

    # 4. Which receivers have claimed the most food?
    st.subheader("4. Top Receivers by Food Claimed")
    top_receivers_query = """
        SELECT r.Name, SUM(fl.Quantity) AS TotalQuantityClaimed
        FROM receivers AS r
        JOIN claims AS c ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings AS fl ON c.Food_ID = fl.Food_ID
        GROUP BY r.Name
        ORDER BY TotalQuantityClaimed DESC
        LIMIT 10;
    """
    top_receivers_df = run_query(top_receivers_query)
    st.dataframe(top_receivers_df, use_container_width=True)
    st.bar_chart(top_receivers_df.set_index('Name'))

    # 5. What is the total quantity of food available from all providers?
    st.subheader("5. Total Quantity of Food Available")
    total_quantity_query = "SELECT SUM(Quantity) AS TotalAvailableFood FROM food_listings;"
    total_quantity_df = run_query(total_quantity_query)
    st.metric("Total Food Quantity", f"{int(total_quantity_df.iloc[0]['TotalAvailableFood']):,}")

    # 6. Which city has the highest number of food listings?
    st.subheader("6. City with Highest Number of Food Listings")
    highest_listings_query = "SELECT Location, COUNT(*) AS NumberOfListings FROM food_listings GROUP BY Location ORDER BY NumberOfListings DESC LIMIT 1;"
    highest_listings_df = run_query(highest_listings_query)
    st.dataframe(highest_listings_df, use_container_width=True)

    # 7. What are the most commonly available food types?
    st.subheader("7. Most Commonly Available Food Types")
    most_common_food_type_query = "SELECT Food_Type, COUNT(*) AS NumberOfListings FROM food_listings GROUP BY Food_Type ORDER BY NumberOfListings DESC;"
    most_common_food_type_df = run_query(most_common_food_type_query)
    st.dataframe(most_common_food_type_df, use_container_width=True)
    st.bar_chart(most_common_food_type_df.set_index('Food_Type'))

    # 8. How many food claims have been made for each food item?
    st.subheader("8. Claims Per Food Item")
    claims_per_item_query = """
        SELECT fl.Food_Name, COUNT(c.Claim_ID) AS TotalClaims
        FROM food_listings AS fl
        JOIN claims AS c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Food_Name
        ORDER BY TotalClaims DESC
        LIMIT 10;
    """
    claims_per_item_df = run_query(claims_per_item_query)
    st.dataframe(claims_per_item_df, use_container_width=True)

    # 9. Which provider has had the highest number of successful food claims?
    st.subheader("9. Provider with Most Successful Claims")
    top_provider_successful_claims_query = """
        SELECT p.Name, COUNT(c.Claim_ID) AS SuccessfulClaims
        FROM providers AS p
        JOIN food_listings AS fl ON p.Provider_ID = fl.Provider_ID
        JOIN claims AS c ON fl.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Name
        ORDER BY SuccessfulClaims DESC
        LIMIT 1;
    """
    top_provider_successful_claims_df = run_query(top_provider_successful_claims_query)
    st.dataframe(top_provider_successful_claims_df, use_container_width=True)

    # 10. What percentage of food claims are completed vs. pending vs. canceled?
    st.subheader("10. Percentage of Claims by Status")
    claims_percentage_query = """
        SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage
        FROM claims
        GROUP BY Status;
    """
    claims_percentage_df = run_query(claims_percentage_query)
    st.dataframe(claims_percentage_df, use_container_width=True)
    st.bar_chart(claims_percentage_df.set_index('Status'))

    # 11. What is the average quantity of food claimed per receiver?
    st.subheader("11. Average Quantity of Food Claimed Per Receiver")
    avg_claimed_per_receiver_query = """
        SELECT AVG(T.TotalQuantity) AS AverageQuantityPerReceiver
        FROM (
            SELECT SUM(fl.Quantity) AS TotalQuantity
            FROM claims AS c
            JOIN food_listings AS fl ON c.Food_ID = fl.Food_ID
            GROUP BY c.Receiver_ID
        ) AS T;
    """
    avg_claimed_per_receiver_df = run_query(avg_claimed_per_receiver_query)
    st.metric("Average Food Claimed per Receiver", f"{avg_claimed_per_receiver_df.iloc[0]['AverageQuantityPerReceiver']:.2f}")

    # 12. Which meal type is claimed the most?
    st.subheader("12. Most Claimed Meal Type")
    most_claimed_meal_type_query = """
        SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS NumberOfClaims
        FROM food_listings AS fl
        JOIN claims AS c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Meal_Type
        ORDER BY NumberOfClaims DESC
        LIMIT 1;
    """
    most_claimed_meal_type_df = run_query(most_claimed_meal_type_query)
    st.dataframe(most_claimed_meal_type_df, use_container_width=True)

    # 13. What is the total quantity of food donated by each provider?
    st.subheader("13. Total Food Donated by Each Provider")
    total_donated_by_provider_query = """
        SELECT p.Name, SUM(fl.Quantity) AS TotalDonatedQuantity
        FROM providers AS p
        JOIN food_listings AS fl ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.Name
        ORDER BY TotalDonatedQuantity DESC;
    """
    total_donated_by_provider_df = run_query(total_donated_by_provider_query)
    st.dataframe(total_donated_by_provider_df, use_container_width=True)

    # 14. Top 5 cities with the highest number of food claims
    st.subheader("14. Top 5 Cities with Highest Number of Claims")
    top_cities_claims_query = """
        SELECT r.City, COUNT(c.Claim_ID) AS TotalClaims
        FROM claims AS c
        JOIN receivers AS r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.City
        ORDER BY TotalClaims DESC
        LIMIT 5;
    """
    top_cities_claims_df = run_query(top_cities_claims_query)
    st.dataframe(top_cities_claims_df, use_container_width=True)

    # 15. Average quantity of food per listing, grouped by food type
    st.subheader("15. Average Quantity Per Food Type")
    avg_quantity_food_type_query = """
        SELECT Food_Type, AVG(Quantity) AS AverageQuantity
        FROM food_listings
        GROUP BY Food_Type;
    """
    avg_quantity_food_type_df = run_query(avg_quantity_food_type_query)
    st.dataframe(avg_quantity_food_type_df, use_container_width=True)

with tab_find:
    st.header("Find Available Food")
    
    # Get filter options
    locations = run_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")['Location'].tolist()
    food_types = run_query("SELECT DISTINCT Food_Type FROM food_listings ORDER BY Food_Type")['Food_Type'].tolist()
    meal_types = run_query("SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type")['Meal_Type'].tolist()

    all_option = "All"
    locations.insert(0, all_option)
    food_types.insert(0, all_option)
    meal_types.insert(0, all_option)

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_location = st.selectbox("Filter by Location", locations)
    with col2:
        selected_food_type = st.selectbox("Filter by Food Type", food_types)
    with col3:
        selected_meal_type = st.selectbox("Filter by Meal Type", meal_types)

    # Build a dynamic SQL query based on user selections
    query = "SELECT fl.*, p.Name AS ProviderName, p.Contact AS ProviderContact FROM food_listings AS fl JOIN providers AS p ON fl.Provider_ID = p.Provider_ID WHERE 1=1"
    
    if selected_location != all_option:
        query += f" AND fl.Location = '{selected_location}'"
    if selected_food_type != all_option:
        query += f" AND fl.Food_Type = '{selected_food_type}'"
    if selected_meal_type != all_option:
        query += f" AND fl.Meal_Type = '{selected_meal_type}'"
    
    query += " ORDER BY fl.Expiry_Date ASC"

    filtered_df = run_query(query)

    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No food listings match your criteria.")

with tab_crud:
    st.header("Manage Your Food Listings")

    # A simple way to get provider info for new listings
    providers_list = run_query("SELECT Provider_ID, Name FROM providers ORDER BY Name")
    provider_dict = dict(zip(providers_list['Name'], providers_list['Provider_ID']))
    
    crud_action = st.radio("Select an action:", ["Add New Listing", "Update Existing Listing", "Delete Existing Listing"])

    if crud_action == "Add New Listing":
        st.subheader("Add a New Food Listing")
        with st.form("add_listing_form", clear_on_submit=True):
            selected_provider_name = st.selectbox("Select Provider:", providers_list['Name'].tolist())
            provider_id = provider_dict.get(selected_provider_name)

            food_name = st.text_input("Food Name:")
            quantity = st.number_input("Quantity:", min_value=1)
            expiry_date = st.date_input("Expiry Date:", min_value=datetime.date.today())
            location = st.text_input("Location (City):")
            food_type = st.selectbox("Food Type:", ['Vegetarian', 'Non-Vegetarian', 'Vegan'])
            meal_type = st.selectbox("Meal Type:", ['Breakfast', 'Lunch', 'Dinner', 'Snacks'])

            submitted = st.form_submit_button("Add Listing")
            if submitted:
                with engine.connect() as conn:
                    trans = conn.begin()
                    try:
                        # Find the next available Food_ID
                        next_food_id_query = "SELECT MAX(Food_ID) + 1 FROM food_listings"
                        next_food_id = conn.execute(next_food_id_query).scalar()
                        if not next_food_id:
                            next_food_id = 1
                        
                        provider_type_query = f"SELECT Type FROM providers WHERE Provider_ID = {provider_id}"
                        provider_type = conn.execute(provider_type_query).scalar()

                        insert_query = f"""
                            INSERT INTO food_listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                            VALUES ({next_food_id}, '{food_name}', {quantity}, '{expiry_date}', {provider_id}, '{provider_type}', '{location}', '{food_type}', '{meal_type}')
                        """
                        conn.execute(insert_query)
                        trans.commit()
                        st.success("Food listing added successfully!")
                        st.cache_data.clear()
                        st.experimental_rerun()
                    except Exception as e:
                        trans.rollback()
                        st.error(f"An error occurred: {e}")

    elif crud_action == "Update Existing Listing":
        st.subheader("Update an Existing Food Listing")
        listings_df = run_query("SELECT Food_ID, Food_Name FROM food_listings")
        if not listings_df.empty:
            listing_options = listings_df.apply(lambda row: f"{row['Food_ID']} - {row['Food_Name']}", axis=1).tolist()
            selected_listing = st.selectbox("Select Listing to Update:", listing_options)
            food_id_to_update = int(selected_listing.split(' - ')[0])
            
            # Fetch current details
            current_listing = run_query(f"SELECT * FROM food_listings WHERE Food_ID = {food_id_to_update}").iloc[0]
            
            with st.form("update_listing_form"):
                new_food_name = st.text_input("New Food Name:", value=current_listing['Food_Name'])
                new_quantity = st.number_input("New Quantity:", min_value=1, value=int(current_listing['Quantity']))
                
                submitted = st.form_submit_button("Update Listing")
                if submitted:
                    with engine.connect() as conn:
                        trans = conn.begin()
                        try:
                            update_query = f"""
                                UPDATE food_listings
                                SET Food_Name = '{new_food_name}', Quantity = {new_quantity}
                                WHERE Food_ID = {food_id_to_update}
                            """
                            conn.execute(update_query)
                            trans.commit()
                            st.success(f"Listing {food_id_to_update} updated successfully!")
                            st.cache_data.clear()
                            st.experimental_rerun()
                        except Exception as e:
                            trans.rollback()
                            st.error(f"An error occurred: {e}")
        else:
            st.info("No listings available to update.")
    
    elif crud_action == "Delete Existing Listing":
        st.subheader("Delete a Food Listing")
        listings_df = run_query("SELECT Food_ID, Food_Name FROM food_listings")
        if not listings_df.empty:
            listing_options = listings_df.apply(lambda row: f"{row['Food_ID']} - {row['Food_Name']}", axis=1).tolist()
            selected_listing = st.selectbox("Select Listing to Delete:", listing_options)
            food_id_to_delete = int(selected_listing.split(' - ')[0])

            submitted = st.button("Delete Listing")
            if submitted:
                with engine.connect() as conn:
                    trans = conn.begin()
                    try:
                        delete_query = f"DELETE FROM food_listings WHERE Food_ID = {food_id_to_delete}"
                        conn.execute(delete_query)
                        trans.commit()
                        st.success(f"Listing {food_id_to_delete} deleted successfully!")
                        st.cache_data.clear()
                        st.experimental_rerun()
                    except Exception as e:
                        trans.rollback()
                        st.error(f"An error occurred: {e}")
        else:
            st.info("No listings available to delete.")

with tab_query_runner:
    st.header("SQL Query Runner")
    st.markdown("Enter your SQL query below and click 'Run Query' to see the results. **Note:** This tool is for `SELECT` queries only.")

    query = st.text_area("SQL Query", height=150)
    
    if st.button("Run Query"):
        if query:
            try:
                # Use a simple check to prevent non-SELECT statements
                if query.strip().upper().startswith("SELECT"):
                    query_df = run_query(query)
                    st.success("Query executed successfully!")
                    st.dataframe(query_df, use_container_width=True)
                else:
                    st.warning("Only `SELECT` queries are supported in this runner.")
            except Exception as e:
                st.error(f"An error occurred while running the query: {e}")
        else:
            st.warning("Please enter a query to run.")

