from ortools.linear_solver import pywraplp
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
matplotlib.use('Agg')


class ProductionOptimizer:
    def __init__(self, machines, products_profits, products_time, products_min):
        self.machines = machines
        self.products_profits = products_profits
        self.products_time = products_time
        self.products_min = products_min
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.decision_variables = {}

    def define_variables(self):
        for product in self.products_profits:
            self.decision_variables[product] = self.solver.IntVar(0, self.solver.infinity(), f'x_{product}')

    def add_constraints(self):
        # Machine time constraints
        for machine in self.machines:
            constraint = sum(self.products_time[product][machine] * self.decision_variables[product] for product in self.products_profits)
            self.solver.Add(constraint <= self.machines[machine])

        # Minimum production constraints
        for product in self.products_min:
            self.solver.Add(self.decision_variables[product] >= self.products_min[product])

    def set_objective(self):
        objective = sum(self.products_profits[product] * self.decision_variables[product] for product in self.products_profits)
        self.solver.Maximize(objective)
    
    def format_product_data(self, product_data):
        """
        Formats the product data into a specified format.

        Returns:
        list: A list of tuples formatted as (product, machine1_hours, machine2_hours).
        """
        formatted_data = []

        for product, count in product_data.items():
            machine_hours = self.products_time[product]
            for _ in range(count):
                formatted_data.append((product, machine_hours["Machine 1"], machine_hours["Machine 2"]))

        return formatted_data

    def solve(self):
        self.define_variables()
        self.add_constraints()
        self.set_objective()

        status = self.solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            production_levels = {product: int(self.decision_variables[product].solution_value()) for product in self.products_profits}
            max_profit = int(self.solver.Objective().Value())
            print(f"Max Profit: {max_profit}")
            return self.create_chart(self.johnsons_method(self.format_product_data(production_levels)))
        else:
            raise Exception("The problem does not have an optimal solution.")
    def johnsons_method(self,jobs):
        # Split jobs into two sets A and B
        A = [(i, job) for i, job in enumerate(jobs) if job[1] < job[2]]
        B = [(i, job) for i, job in enumerate(jobs) if job[1] >= job[2]]

        # Sort A by increasing order of ti1
        A.sort(key=lambda x: x[1][1])
        
        # Sort B by decreasing order of ti2
        B.sort(key=lambda x: x[1][2], reverse=True)
        
        # Concatenate A and B to get the optimal order
        ordered_jobs = A + B
        
        # Extract jobs in the optimal order
        optimal_order = [job[1] for job in ordered_jobs]
        
        return optimal_order
    def calculate_job_schedule(self,input_data):
        jobs = []
        current_time_m1 = 0
        current_time_m2 = 0

        for product, time_m1, time_m2 in input_data:
            start_m1 = current_time_m1
            end_m1 = start_m1 + time_m1
            start_m2 = max(end_m1, current_time_m2)
            end_m2 = start_m2 + time_m2

            jobs.append([product, start_m1, end_m1, start_m2, end_m2])

            current_time_m1 = end_m1
            current_time_m2 = end_m2

        return jobs
    def create_chart(self,input_data):
        jobs = self.calculate_job_schedule(input_data)

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

    # Define the colors for different jobs
        colors = {'Product A': 'skyblue', 'Product B': 'lightgreen'}

    # Create the Gantt chart
        for job in jobs:
            product, start_m1, end_m1, start_m2, end_m2 = job
            ax.broken_barh([(start_m1, end_m1 - start_m1)], (10, 9), facecolors=(colors[product]),edgecolor='black')
            ax.text(start_m1 + (end_m1 - start_m1) / 2, 15, product, ha='center', va='center', color='black', fontsize=10, fontweight='bold')

            ax.broken_barh([(start_m2, end_m2 - start_m2)], (20, 9), facecolors=(colors[product]),edgecolor='black')
            ax.text(start_m2 + (end_m2 - start_m2) / 2, 25, product, ha='center', va='center', color='black', fontsize=10, fontweight='bold')


        # Set labels and grid
        ax.set_yticks([15, 25])
        ax.set_yticklabels(['Machine 1', 'Machine 2'])
        ax.set_xlabel('Time')
        ax.set_ylabel('Machines')
        ax.set_title('Gantt Chart for Jobs on Two Machines')
        ax.grid(True)

    # Add legend
        patches_list = [patches.Patch(color=color, label=product) for product, color in colors.items()]
        ax.legend(handles=patches_list)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Return the plot as a response
        return buf

                    









            

