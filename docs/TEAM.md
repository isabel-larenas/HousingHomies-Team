# Team Contributions

Below is a recap of each member's **major contributions** to the project.

## Geo Thatch
- Created the SQL tables and the mock data for university, user, listing, reviews, favorites, and funding tables. Inserted into 01housing_db.sql and 02housing_db.sql.
- Created API routes for listings, reviews, housing (includes country, cities, and university), and funding. 
- Built out the real estate agent persona pages (view_listings_rea, market_dashboard, add_listing)
- Built the initial design for student listings and reviews
- Add-review page with all CRUD features
- Add-listing page with all CRUD features
- Wrote and designed nav.py, home.py, and about.py 


## Isabel Larenas
- Created and deployed the **second machine-learning model** (linear regression) for the government agency user persona
    - This model **predicts housing deprivation** based on multiple socioeconomic indicators such as immigration, housing-cost overburden, GDP per capita, population density, and unemployment
    - **Added routes** to the Flask API for train, test, prediction, params, and deprivation-map for the Europe heatmap
    - Created the **Streamlit page** for the model including an interactive heatmap and table ranked for countries that need the most funding
- **Cleaned and merged the EU datasets** (immigration, housing overburden, GDP, population, and unemployment) into the training data and developed a Jupyter Notebook to explore the data
- Contributed to the **student life satisfaction prediction model**
- Created the **README**


## Maira Padani
- **Government agency funding workflow**: built the government agency persona pages end-to-end, including the `funding_draft` table in `01housing_db.sql`, all draft CRUD routes in `funding.py`, and three Streamlit pages to view, manage, and create funding plans. Added success banners for save and delete actions.
- **Route reorganization**: split `housing_routes01.py` into separate blueprint files by entity and updated `rest_entry.py` to register each one.
- **Risk heatmap**: built the full risk heatmap page including filters, Folium map, and bar chart rankings. Handled country name mismatches between the GeoJSON source and the database. Added download buttons for the map and rankings CSV.
- **Social indicator routes**: added the `social_indicator_stats` table and Eurostat sync routes for all six indicators. Fixed the HPI sync.
- **Student prediction integration**: added the prediction route and connected the model on `04_student_pred.py`.
- **Persona pages and theming**: updated all three persona home pages with consistent button card layout and EuroHome animation, applied the app theme and logo, and removed leftover test pages.

## Laasya Gattu
- Created and deployed the **first machine learning model** (linear regression) for the student user persona
    - **Predicts overall life satisfaction level** based on environment and location factors such as crime, noise, pollution, housing price index, and degree of urbanisation
    - Conducted all initial cleaning, EDA, data vis, and merging of the Eurostat datasets
    - Added **CRUD routes** to the Flask API for student train, test, prediction, and params
- Created the **Streamlit page for the ML model** including sliders for user inputs, an interactive heatmap to view best accommodating countries for the user, and a table for countries ranked by satisfaction score.
- Created the **Streamlit page for the student persona Favorites page** for saving and viewing favorite listings; added the corresponding favorites table to the SQL script and CRUD routes
- Contributed to design of the Streamlit with **Home page layouts** for each of the user personas
- Contributed to development of **housing deprivation ML model**

