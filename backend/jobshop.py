import collections
import io
from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class JobShopScheduler:
    def __init__(self, jobs_data):
        """
        Initialize the JobShopScheduler with the provided jobs data.
        
        :param jobs_data: List of jobs, where each job is a list of tasks,
                          and each task is a tuple (machine_id, processing_time).
        """
        self.jobs_data = jobs_data
        self.machines_count = 1 + max(task[0] for job in jobs_data for task in job)
        self.all_machines = range(self.machines_count)
        self.horizon = sum(task[1] for job in jobs_data for task in job)
        self.model = cp_model.CpModel()
        self.task_type = collections.namedtuple("task_type", "start end interval")
        self.assigned_task_type = collections.namedtuple(
            "assigned_task_type", "start job index duration"
        )
        self.all_tasks = {}
        self.machine_to_intervals = collections.defaultdict(list)
        self.solver = cp_model.CpSolver()
        self.assigned_jobs = collections.defaultdict(list)
        self.status = None

    def create_variables(self):
        """Create variables for the scheduling problem."""
        for job_id, job in enumerate(self.jobs_data):
            for task_id, task in enumerate(job):
                machine, duration = task
                suffix = f"_{job_id}_{task_id}"
                start_var = self.model.NewIntVar(0, self.horizon, "start" + suffix)
                end_var = self.model.NewIntVar(0, self.horizon, "end" + suffix)
                interval_var = self.model.NewIntervalVar(
                    start_var, duration, end_var, "interval" + suffix
                )
                self.all_tasks[job_id, task_id] = self.task_type(
                    start=start_var, end=end_var, interval=interval_var
                )
                self.machine_to_intervals[machine].append(interval_var)

    def add_constraints(self):
        """Add constraints to the model."""
        # Disjunctive constraints for machines.
        for machine in self.all_machines:
            self.model.AddNoOverlap(self.machine_to_intervals[machine])

        # Precedence constraints within jobs.
        for job_id, job in enumerate(self.jobs_data):
            for task_id in range(len(job) - 1):
                self.model.Add(
                    self.all_tasks[job_id, task_id + 1].start >= self.all_tasks[job_id, task_id].end
                )

    def set_objective(self):
        """Set the objective function to minimize the makespan."""
        obj_var = self.model.NewIntVar(0, self.horizon, "makespan")
        self.model.AddMaxEquality(
            obj_var,
            [self.all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(self.jobs_data)],
        )
        self.model.Minimize(obj_var)

    def solve(self):
        """Solve the scheduling problem."""
        self.create_variables()
        self.add_constraints()
        self.set_objective()
        self.status = self.solver.Solve(self.model)

    def print_solution(self):
        """Print the solution if found."""
        if self.status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print("Solution:")
            for job_id, job in enumerate(self.jobs_data):
                for task_id, task in enumerate(job):
                    machine = task[0]
                    self.assigned_jobs[machine].append(
                        self.assigned_task_type(
                            start=self.solver.Value(self.all_tasks[job_id, task_id].start),
                            job=job_id,
                            index=task_id,
                            duration=task[1],
                        )
                    )

            output = ""
            for machine in self.all_machines:
                self.assigned_jobs[machine].sort()
                sol_line_tasks = f"Machine {machine}: "
                sol_line = "           "

                for assigned_task in self.assigned_jobs[machine]:
                    name = f"job_{assigned_task.job}_task_{assigned_task.index}"
                    sol_line_tasks += f"{name:15}"
                    start = assigned_task.start
                    duration = assigned_task.duration
                    sol_tmp = f"[{start},{start + duration}]"
                    sol_line += f"{sol_tmp:15}"

                sol_line += "\n"
                sol_line_tasks += "\n"
                output += sol_line_tasks
                output += sol_line

            print(f"Optimal Schedule Length: {self.solver.ObjectiveValue()}")
            print(output)
        else:
            print("No solution found.")

        print("\nStatistics")
        print(f"  - conflicts: {self.solver.NumConflicts()}")
        print(f"  - branches : {self.solver.NumBranches()}")
        print(f"  - wall time: {self.solver.WallTime()}s")

    def gantt_chart(self):
        """Generate and display a Gantt chart of the solution."""
        if self.status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            fig, ax = plt.subplots()
            for machine in self.all_machines:
                for assigned_task in self.assigned_jobs[machine]:
                    start = assigned_task.start
                    duration = assigned_task.duration
                    ax.broken_barh(
                        [(start, duration)],
                        (machine - 0.4, 0.8),
                        facecolors=f"C{assigned_task.job}",
                    )

            ax.set_ylim(-0.5, self.machines_count - 0.5)
            ax.set_xlim(0, self.horizon + 1)
            ax.set_xlabel("Time")
            ax.set_ylabel("Machine")
            ax.set_yticks(range(self.machines_count))
            ax.set_yticklabels([f"Machine {i}" for i in self.all_machines])
            ax.grid(True)

            handles = [
                mpatches.Patch(color=f"C{i}", label=f"Job {i}")
                for i in range(len(self.jobs_data))
            ]
            ax.legend(handles=handles)

            plt.title("Gantt Chart for Job Shop Scheduling")

            # Save the plot to a buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            return buf
        else:
            raise ValueError("No solution to plot.")


