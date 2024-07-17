import numpy as np

def johnson_rule(job_set):
    """
    Apply Johnson's rule to a 2-machine flowshop problem.
    job_set: list of tuples, where each tuple is (job_index, (A, B)) for a job
    Returns the job sequence as a list of job indices.
    """
    set1 = [job for job in job_set if job[1][0] <= job[1][1]]
    set2 = [job for job in job_set if job[1][0] > job[1][1]]

    set1.sort(key=lambda x: x[1][0])
    set2.sort(key=lambda x: x[1][1], reverse=True)

    ordered_jobs = set1 + set2
    return [job[0] for job in ordered_jobs]

def calculate_makespan(sequence, processing_times):
    """
    Calculate the makespan for a given job sequence.
    sequence: list of job indices
    processing_times: 2D numpy array of processing times
    """
    num_jobs = processing_times.shape[0]
    num_machines = processing_times.shape[1]

    completion_time = np.zeros((num_jobs, num_machines))

    # First job
    completion_time[0, 0] = processing_times[sequence[0], 0]
    for j in range(1, num_machines):
        completion_time[0, j] = completion_time[0, j-1] + processing_times[sequence[0], j]

    # Remaining jobs
    for i in range(1, num_jobs):
        completion_time[i, 0] = completion_time[i-1, 0] + processing_times[sequence[i], 0]
        for j in range(1, num_machines):
            completion_time[i, j] = max(completion_time[i, j-1], completion_time[i-1, j]) + processing_times[sequence[i], j]

    return completion_time[-1, -1]

def cds_algorithm(processing_times):
    """
    Apply the CDS algorithm to the flowshop scheduling problem.
    processing_times: 2D numpy array of processing times
    """
    num_jobs, num_machines = processing_times.shape
    best_sequence = None
    best_makespan = float('inf')

    for k in range(1, num_machines):
        A = np.sum(processing_times[:, :k], axis=1)
        B = np.sum(processing_times[:, k:], axis=1)
        job_set = [(i, (A[i], B[i])) for i in range(num_jobs)]
        
        sequence = johnson_rule(job_set)
        makespan = calculate_makespan(sequence, processing_times)
        
        if makespan < best_makespan:
            best_makespan = makespan
            best_sequence = sequence

    return best_sequence, best_makespan

# Example usage
processing_times = np.array([
    [2, 3, 2],
    [4, 1, 3],
    [3, 2, 4]
])

best_sequence, best_makespan = cds_algorithm(processing_times)
print(f"Best sequence: {best_sequence}")
print(f"Best makespan: {best_makespan}")



