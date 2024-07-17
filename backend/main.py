

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from maximize_profit_service import ProductionOptimizer
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],  # Ensure OPTIONS method is allowed
    allow_headers=["Content-Type"],
)
machines = {
    "Machine 1": 12,  # hours per day
    "Machine 2": 9    # hours per day
}
products_profits = {
    "Product A": 7,   # profit per unit
    "Product B": 4,
    "Product C": 10   # profit per unit
}
products_time = {
    "Product A": {"Machine 1": 3, "Machine 2": 3},  # hours per unit
    "Product B": {"Machine 1": 2, "Machine 2": 1},
     "Product C": {"Machine 1": 3, "Machine 2": 1} # hours per unit
}

class ProductsMinInput(BaseModel):
    products_min: dict

@app.post("/optimize")
def optimize_production(input_data: ProductsMinInput):
    try:
        optimizer = ProductionOptimizer(
            machines,
            products_profits,
            products_time,
            input_data.products_min  # Ensure products_min is correctly passed
        )
        chart_buf,m1,m2= optimizer.solve()
        response = StreamingResponse(chart_buf, media_type="image/png")
        response.headers["machine1"] = str(m1)
        response.headers["machine2"] = str(m2)
        print(response)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


