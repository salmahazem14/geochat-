import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("API_KEY"))

MODEL = "llama-3.3-70b-versatile"

SCHEMA = """
Tables (all have: id, name, tags JSONB, wkb_geometry):
- atms(id, name, tags, wkb_geometry POINT 4326)
- banks(id, name, tags, wkb_geometry POINT 4326)
- churches(id, name, tags, wkb_geometry POINT 4326)
- hospitals(id, name, tags, wkb_geometry POINT 4326)
- metro_stations(id, name, tags, wkb_geometry POINT 4326)
- mosques(id, name, tags, wkb_geometry POINT 4326)
- parks(id, name, tags, wkb_geometry POLYGON 4326)
- pharmacies(id, name, tags, wkb_geometry POINT 4326)
- restaurants(id, name, tags, wkb_geometry POINT 4326)
- schools(id, name, tags, wkb_geometry POINT 4326)
- universities(id, name, tags, wkb_geometry POINT 4326)

Rules:
- ONLY SELECT queries allowed
- ALWAYS include ALL of these in SELECT:
    name,
    tags,
    ST_AsGeoJSON(wkb_geometry) AS geometry
- The tags column is JSONB and contains extra OSM fields like name:en, wikipedia, wikidata
- No INSERT / DELETE / UPDATE / DROP
- Use ILIKE for text search on name column
- For distance queries:
    ST_DWithin(wkb_geometry::geography, ref::geography, meters)
"""

SYSTEM_PROMPT = f"""
You are a PostgreSQL + PostGIS expert for a map of Egypt.

You convert natural language into SAFE SQL queries.

STRICT RULES:
- Return ONLY SQL (no explanation, no markdown)
- Only use given schema
- Never invent tables or columns
- Always include name, tags, and geometry in SELECT
- Always ensure query is valid PostGIS
{SCHEMA}
"""

def generate_sql(user_query: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0.0
    )

    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql
