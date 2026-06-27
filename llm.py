import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("API_KEY"))

MODEL = "llama-3.3-70b-versatile"

SCHEMA = """
Tables:
- atms(id, name, wkb_geometry POINT 4326)
- banks(id, name, wkb_geometry POINT 4326)
- churches(id, name, wkb_geometry POINT 4326)
- hospitals(id, name, wkb_geometry POINT 4326)
- metro_stations(id, name, wkb_geometry POINT 4326)
- mosques(id, name, wkb_geometry POINT 4326)
- parks(id, name, wkb_geometry POLYGON 4326)
- pharmacies(id, name, wkb_geometry POINT 4326)
- restaurants(id, name, wkb_geometry POINT 4326)
- schools(id, name, wkb_geometry POINT 4326)
- universities(id, name, wkb_geometry POINT 4326)

Rules:
- ONLY SELECT queries allowed
- ALWAYS include:
  ST_AsGeoJSON(wkb_geometry) AS geometry
- No INSERT / DELETE / UPDATE / DROP
- Use ILIKE for text search
- For distance:
  ST_DWithin(wkb_geometry::geography, ref::geography, meters)
"""

SYSTEM_PROMPT = f"""
You are a PostgreSQL + PostGIS expert.

You convert natural language into SAFE SQL queries.

STRICT RULES:
- Return ONLY SQL (no explanation)
- Only use given schema
- Never invent tables or columns
- Always include geometry output
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