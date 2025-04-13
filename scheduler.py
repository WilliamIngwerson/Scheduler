import sys
import heapq

class Process:
    def __init__(self, job_id, priority, arrival_time, total_time, block_interval):
        self.job_id = job_id
        self.priority = priority
        self.arrival_time = arrival_time
        self.total_time = total_time
        self.block_interval = block_interval
        self.remaining_time = total_time
        self.next_block_time = block_interval
        self.block_time_remaining = 0
        self.last_run_time = 0

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.last_run_time < other.last_run_time
        return self.priority > other.priority  # Higher priority first

def read_jobs(file_name):
    jobs = []
    with open(file_name, 'r') as file:
        for line in file:
            if line.startswith("#"):
                continue
            parts = line.split()
            job_id = parts[0]
            priority = int(parts[1])
            arrival_time = int(parts[2])
            total_time = int(parts[3])
            block_interval = int(parts[4])
            jobs.append((job_id, priority, arrival_time, total_time, block_interval))
    return jobs

def round_robin_scheduler(jobs, time_slice, block_duration):
    time = 0
    arrival_queue = []
    blocked_queue = []
    ready_queue = []
    completed_jobs = []
    turnaround_times = []

    for job in jobs:
        heapq.heappush(arrival_queue, (job[2], Process(*job)))

    print(f"{time_slice}\t{block_duration}")

    while arrival_queue or blocked_queue or ready_queue:
        while arrival_queue and arrival_queue[0][0] <= time:
            _, process = heapq.heappop(arrival_queue)
            heapq.heappush(ready_queue, process)

        new_blocked_queue = []
        for process in blocked_queue:
            process.block_time_remaining -= 1
            if process.block_time_remaining <= 0:
                heapq.heappush(ready_queue, process)
            else:
                new_blocked_queue.append(process)
        blocked_queue = new_blocked_queue

        if ready_queue:
            process = heapq.heappop(ready_queue)
            run_time = min(time_slice, process.remaining_time, process.next_block_time)
            time += run_time
            process.remaining_time -= run_time
            process.next_block_time -= run_time
            process.last_run_time = time

            if process.remaining_time == 0:
                print(f"{time - run_time}\t{process.job_id}\t{run_time}\tT")
                completed_jobs.append(process)
                turnaround_times.append(time - process.arrival_time)
            elif process.next_block_time == 0:
                process.next_block_time = process.block_interval
                process.block_time_remaining = block_duration
                print(f"{time - run_time}\t{process.job_id}\t{run_time}\tB")
                blocked_queue.append(process)
            else:
                print(f"{time - run_time}\t{process.job_id}\t{run_time}\tP")
                heapq.heappush(ready_queue, process)
        else:
            next_event_time = min(
                [arrival_queue[0][0] if arrival_queue else float('inf')] +
                [time + p.block_time_remaining for p in blocked_queue]
            )
            idle_time = next_event_time - time
            print(f"{time}\t(IDLE)\t{idle_time}\tI")
            time = next_event_time

    average_turnaround_time = sum(turnaround_times) / len(turnaround_times)
    print(f"Average turnaround time: {average_turnaround_time:.2f}")

    return [(process.job_id, process.last_run_time) for process in completed_jobs]

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 scheduler.py <input_file> <time_slice> <block_duration>")
        sys.exit(1)

    input_file = sys.argv[1]
    time_slice = int(sys.argv[2])
    block_duration = int(sys.argv[3])

    jobs = read_jobs(input_file)
    completed_jobs = round_robin_scheduler(jobs, time_slice, block_duration)

    for job_id, completion_time in completed_jobs:
        print(f"Job {job_id} completed at time {completion_time}")
