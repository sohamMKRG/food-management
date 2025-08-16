Local Food Wastage Management System: Final Project Report
This project delivers a full-stack data management and analysis system designed to combat local food wastage. By connecting food providers with receivers, the platform facilitates efficient food redistribution and provides data-driven insights to improve operations.
Project Objectives
 Platform Development: Create a user-friendly Streamlit application to serve as the front-end for the system.
 Database Management: Utilize a SQL database (SQLite) to store, manage, and query food donation data.
 Data Analysis: Provide valuable insights into food donation trends, provider contributions, and claim statuses.
 CRUD Operations: Implement functionalities for adding, updating, and deleting food listings.
Skills Demonstrated
 Python: Used for data processing, application logic, and interacting with the database.
 Streamlit: Built the interactive, web-based user interface for the application.
 SQL (SQLite): Managed data storage and performed complex queries for trend analysis.
 Data Analysis: Analyzed key metrics such as food quantities, provider types, and claim statuses.
Application Features
The Streamlit app is organized into four main sections, each serving a specific purpose:
1. Dashboard & Analysis: This section presents the core data analysis from the project. It displays the results of the 15+ SQL queries in tables and charts, providing a clear overview of food wastage trends.
2. Find Food: An interactive search and filter tool that allows users to find available food listings based on location, food type, and meal type. The results include direct contact information for providers.
3. Manage Listings: This is the core management area for food providers. It features a user-friendly interface to perform Create, Update, and Delete (CRUD) operations on food listings.
4. SQL Query Runner: A dedicated tab for users to execute their own SELECT queries directly on the database and view the results. This feature demonstrates the power of the underlying data structure.
Key Insights from Data Analysis
The SQL queries and EDA revealed several key findings:
 The total quantity of food available from all providers is 45,395 units, highlighting the significant amount of surplus food in the system.
 The top food provider type by total quantity donated is Restaurant, followed by Grocery Store and Supermarket.
 The most commonly available food types are Bread, Fruits, and Vegetables.
 The majority of food claims are Pending, indicating a potential need for faster coordination between providers and receivers.
 The city with the highest number of listings is New Christopherberg, while the city with the most receivers is North Jacobhaven, suggesting areas of high activity.
How to Run the Application
To run the Streamlit application locally, ensure you have Python installed and follow these steps:
1. Clone this repository to your local machine.
2. Navigate to the project directory in your terminal.
3. Install the required libraries: pip install -r requirements.txt
4. Run the application: streamlit run app.py
Live Application
A live version of the application has been deployed to Streamlit Cloud for easy access and demonstration.
Project Files
 app.py: The main Streamlit application file.
 requirements.txt: Lists the Python dependencies required to run the app.
 providers_cleaned.csv: Cleaned data for food providers.
 receivers_cleaned.csv: Cleaned data for food receivers.
 food_listings_cleaned.csv: Cleaned data for food listings.
 claims_cleaned.csv: Cleaned data for food claims.
 EDA.ipynb: Jupyter Notebook containing the Exploratory Data Analysis.
 SQL.ipynb: Jupyter Notebook with the 15+ SQL queries and their outputs.
