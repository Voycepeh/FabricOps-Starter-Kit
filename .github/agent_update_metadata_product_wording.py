from pathlib import Path

path = Path("scripts/reference_docs_metadata.py")
text = path.read_text()

replacements = {
    '"purpose": "Keep the active Data Stewards used by the Data Agreement workflow."': '"purpose": "Know who is responsible for the data."',
    '"purpose": "Define why data can be shared, who is accountable, the approved purpose and usage, and the review period."': '"purpose": "Define why the data is shared, with whom, and under what conditions."',
    '"purpose": "Record a lightweight view of source partitions so FabricOps can spot additions, removals and changes before ETL."': '"purpose": "See whether the source arrived and changed as expected."',
    '"purpose": "See the tables and columns FabricOps has registered, including where they live and how they are structured."': '"purpose": "See what data is available and how it is structured."',
    '"purpose": "See the shape and quality of each column from a profiled dataset snapshot."': '"purpose": "Understand the shape, completeness, and characteristics of the data."',
    '"purpose": "See the most common values and their frequencies for profiled columns."': '"purpose": "See how values are distributed across the data."',
    '"purpose": "See where the data came from and where it ends up."': '"purpose": "See where the data came from and where it ends up."',
    '"purpose": "Add business and governance context to the data."': '"purpose": "Add business and governance context to the data."',
    '"purpose": "Define the expectations the data used in the ETL pipeline should meet."': '"purpose": "Define the expectations the data used in the ETL pipeline should meet."',
    '"purpose": "See whether the expectations of the data in the ETL pipeline run are met."': '"purpose": "See whether the expectations of the data in the ETL pipeline run are met."',
    '"purpose": "See the specific source rows and DQ rule details behind failed runtime guardrail results."': '"purpose": "See which records did not meet the expectations."',
    '"purpose": "Define what the data is, how it looks, its approved usage and schema fingerprint, and link it to the Data Agreement."': '"purpose": "Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement."',
    '"purpose": "Record access review information for a user and governed data scope."': '"purpose": "See who can use the data and how it can be used."',
}

for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"Expected wording not found: {old}")
    text = text.replace(old, new, 1)

path.write_text(text)
