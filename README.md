# 🏠 EuroHome

**EuroHome** is a data-driven web platform that makes the EU housing market more transparent and accessible. Whether you are a student hunting for an affordable place near your university, a real estate agent listing properties, or a government worker planning housing-support funding, EuroHome brings listings, budgets, market analytics, and machine-learning predictions together in one place.

**Read about how we built EuroHome on [our blog here!](https://isabel-larenas.github.io/Belgium-Dialogue-Blog/)**


## Major Features

EuroHome serves three user personas each with its own purpose:

### 🧑‍🎓 Students
- **Browse listings** across EU housing markets and filter by price, location, and distance to university
- **Save listings** to revisit later and compare options
- **Read & view reviews** from other students about properties and areas
- **Housing Satisfaction Predictor**: a machine-learning model that estimates how satisfied you would be with a country based on your comfortability levels

### 🏡 Real Estate Agents
- **Market Dashboard**: interactive analytics on prices and housing trends across EU countries
- **Add and manage listings** with a full property-entry form
- **Browse** the active listings

### 🇪🇺 Government Agencies
- **View funding** programs across EU countries
- **Funding drafts**: create, view, and manage draft funding proposals backed by data
- **Housing Deprivation Predictor**: a machine-learning model trained on Eurostat social-indicator data to forecast housing deprivation
- **Risk Heatmap**: visualize housing-risk indicators geographically across the EU

## Getting Started

1. Clone the repository

2. Create an `api/.env` file. It needs the following keys:

      ```bash
      SECRET_KEY=                  # create a random string
      DB_USER=root
      DB_HOST=db
      DB_PORT=3306
      DB_NAME=housing_db
      MYSQL_ROOT_PASSWORD=         # create a password
      ```

3. Run `docker compose up -d` to start all services
   - To stop everything, run `docker compose down`

4. Open your browser and navigate to `http://localhost:8501`

## Using the Application

1. Open **http://localhost:8501** in your browser.
2. On the **Home** page, pick a persona and select a mock user from the dropdown:
   - **Login as a Student**: browse/save listings, read reviews, run the Housing Satisfaction Predictor
   - **Login as a Real Estate Agent**: add listings, browse inventory, explore the Market Dashboard
   - **Login as a Government Agency worker**: run the Housing Deprivation Predictor, view the Risk Heatmap, and create funding drafts
3. Use the **left sidebar** to navigate between pages
4. Visit the **About** page to learn more about the project and team

## The Team

EuroHome was built by **Geo Thatch**, **Isabel Larenas**, **Maira Padani**, and **Laasya Gattu**.

See **[docs/TEAM.md](docs/TEAM.md)** for a recap of each member's major contributions.