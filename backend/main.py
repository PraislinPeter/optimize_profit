

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jobshop import JobShopScheduler
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
    "Machine 2": 9,
    "Machine 3": 9    # hours per day
}
products_profits = {
    "Product A": 7,   # profit per unit
    "Product B": 4,
    "Product C": 10   # profit per unit
}
products_time = {
    "Product A": {"Machine 1": 3, "Machine 2": 3, "Machine 3": 2},  # hours per unit
    "Product B": {"Machine 1": 2, "Machine 2": 1, "Machine 3": 2},
    "Product C": {"Machine 1": 3, "Machine 2": 1, "Machine 3": 1}   # hours per unit
}

jobs_data = [
        [(0, 3), (1, 2), (2, 2)],  # Job 0
        [(0, 2), (2, 1), (1, 4)],  # Job 1
        [(1, 4), (2, 3)],          # Job 2
    ]


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
        chart_buf, idle_times = optimizer.solve()
        
        # Set headers for idle times of each machine
        response = StreamingResponse(chart_buf, media_type="image/png")
        for i, idle_time in enumerate(idle_times):
            response.headers[f"machine{i + 1}"] = str(idle_time)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/jobshop')
def jobshop():
    scheduler = JobShopScheduler(jobs_data)
    scheduler.solve()
    gantt_chart_buffer = scheduler.gantt_chart()
    return StreamingResponse(gantt_chart_buffer, media_type="image/png")




