from ortools.linear_solver import pywraplp
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import random
from charting_service import ChartingService

matplotlib.use('Agg')


class ProductionOptimizer:
    def __init__(self, machines, products_profits, products_time, products_min):
        self.machines = machines
        self.products_profits = products_profits
        self.products_time = products_time
        self.products_min = products_min
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.decision_variables = {}
        self.charting_service = ChartingService()  # Instantiate the charting service


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
        list: A list of tuples formatted as (product, machine1_hours, machine2_hours, ..., machineN_hours).
        """
        formatted_data = []

        for product, count in product_data.items():
            if product not in self.products_time:
                raise ValueError(f"Product '{product}' not found in products_time data")

            machine_hours = self.products_time[product]
            # Dynamically create a tuple for all machines
            machine_hours_tuple = tuple(machine_hours[machine] for machine in sorted(machine_hours.keys()))

            for _ in range(count):
                formatted_data.append((product,) + machine_hours_tuple)

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
            formatted_data = self.format_product_data(production_levels)
            optimal_jobs_order = self.cds_heuristic(formatted_data)
            jobs, idle_times= self.calculate_job_schedule(optimal_jobs_order)
            buf, idle_times = self.charting_service.create_chart(formatted_data, jobs, idle_times)
            print(jobs)
            return buf, idle_times

        else:
            raise Exception("The problem does not have an optimal solution.")
    def johnsons_method(self, jobs):
        # Split jobs into two sets A and B
        A = [(i, job) for i, job in enumerate(jobs) if job[1] < job[2]]
        B = [(i, job) for i, job in enumerate(jobs) if job[1] >= job[2]]

        # Sort A by increasing order of ti1
        A.sort(key=lambda x: x[1][1])
        
        # Sort B by decreasing order of ti2
        B.sort(key=lambda x: x[1][2], reverse=True)
        
        # Concatenate A and B to get the optimal order
        ordered_jobs = A + B
        
        # Extract job indices in the optimal order
        optimal_order_indices = [job[0] for job in ordered_jobs]
        
        return optimal_order_indices

    def calculate_makespan(self, jobs, sequence):
        num_jobs = len(sequence)
        num_machines = len(jobs[0]) - 1
        
        completion_times = [[0] * num_machines for _ in range(num_jobs)]
        
        # Initialize first job's completion times
        completion_times[0][0] = jobs[sequence[0]][1]
        for j in range(1, num_machines):
            completion_times[0][j] = completion_times[0][j-1] + jobs[sequence[0]][j+1]
        
        # Fill out the rest of the table
        for i in range(1, num_jobs):
            completion_times[i][0] = completion_times[i-1][0] + jobs[sequence[i]][1]
            for j in range(1, num_machines):
                completion_times[i][j] = max(completion_times[i-1][j], completion_times[i][j-1]) + jobs[sequence[i]][j+1]
        
        return completion_times[-1][-1]

    def cds_heuristic(self, jobs):
        num_jobs = len(jobs)
        num_machines = len(jobs[0]) - 1
        best_sequence = None
        best_makespan = float('inf')
        
        for k in range(1, num_machines):
            # Create a new list of jobs for the two-machine problem
            two_machine_jobs = [
                (i, sum(job[1:k+1]), sum(job[k+1:]))
                for i, job in enumerate(jobs)
            ]
            
            # Apply Johnson's method to the two-machine job list
            optimal_order_indices = self.johnsons_method(two_machine_jobs)
            
            # Calculate makespan for the sequence
            makespan = self.calculate_makespan(jobs, optimal_order_indices)
            
            if makespan < best_makespan:
                best_makespan = makespan
                best_sequence = optimal_order_indices
        
        # Convert the best sequence to a list of jobs
        optimal_jobs_order = [jobs[i] for i in best_sequence]
        
        return optimal_jobs_order
    def calculate_job_schedule(self, input_data):
        jobs = []
        num_machines = len(input_data[0]) - 1
        current_times = [0] * num_machines
        idle_times = [0] * num_machines

        for job in input_data:
            product = job[0]
            start_times = [0] * num_machines
            end_times = [0] * num_machines

            # Calculate start and end times for each machine
            for i in range(num_machines):
                if i == 0:
                    start_times[i] = current_times[i]
                else:
                    start_times[i] = max(end_times[i-1], current_times[i])

                end_times[i] = start_times[i] + job[i+1]

                # Calculate idle time for the machine
                if start_times[i] > current_times[i]:
                    idle_times[i] += start_times[i] - current_times[i]

                # Update the current time for the machine
                current_times[i] = end_times[i]

            # Append the job schedule
            jobs.append([product] + start_times + end_times)

        # Final idle time until the end of the schedule for all machines
        for i in range(num_machines):
            if current_times[i] < self.machines[f'Machine {i + 1}']:
                idle_times[i] += self.machines[f'Machine {i + 1}'] - current_times[i]

        return jobs, idle_times

    
                    









            


                    









            

