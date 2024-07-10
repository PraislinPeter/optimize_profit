

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from maximize_profit_service import ProductionOptimizer
from fastapi.responses import StreamingResponse

app = FastAPI()
machines = {
    "Machine 1": 12,  # hours per day
    "Machine 2": 9    # hours per day
}
products_profits = {
    "Product A": 7,   # profit per unit
    "Product B": 4    # profit per unit
}
products_time = {
    "Product A": {"Machine 1": 3, "Machine 2": 3},  # hours per unit
    "Product B": {"Machine 1": 2, "Machine 2": 1}   # hours per unit
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
        chart_buf= optimizer.solve()
        return  StreamingResponse(chart_buf, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


