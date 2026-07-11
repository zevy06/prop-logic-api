from fastapi import FastAPI
from pydantic import BaseModel
from backend import generate_truth_table

app = FastAPI()

class Proposition(BaseModel):
    formula: str

@app.post("/calculate")
def calculate_truth_table(proposition: Proposition):
    return generate_truth_table(proposition.formula)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Truth Table API! Use the /calculate endpoint to generate truth tables."}