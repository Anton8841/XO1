# -*- coding: utf-8 -*-
from Pyro4 import expose
import hashlib
import time


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited Solver")

    def solve(self):
        print("Job started")
        if not self.workers:
            raise Exception("No workers connected to Master node!")

        num_workers = len(self.workers)
        print("Workers count: %d" % num_workers)

        prefix, algo, total_iterations, target_zeros = self.read_input()

        start_time = time.time()

        step = total_iterations // num_workers
        mapped = []

        for i in range(num_workers):
            start_idx = i * step
            end_idx = total_iterations if i == num_workers - 1 else (i + 1) * step
            mapped.append(
                self.workers[i].mymap(
                    prefix, algo, start_idx, end_idx, target_zeros
                )
            )

        print("Map phase dispatched, waiting for workers...")

        reduced = self.myreduce(mapped)

        elapsed_time = time.time() - start_time
        print("Job finished in %.4f seconds" % elapsed_time)

        self.write_output(
            algo, total_iterations, num_workers, elapsed_time, target_zeros, reduced
        )

    @staticmethod
    @expose
    def mymap(prefix, algo, start_idx, end_idx, target_zeros):
        try:
            iterator = xrange(start_idx, end_idx)
        except NameError:
            iterator = range(start_idx, end_idx)

        matched_count = 0
        sample_matches = []
        min_hash = "f" * 64
        min_nonce = -1

        use_md5 = (str(algo).lower() == "md5")
        prefix_str = str(prefix)
        target_str = str(target_zeros)

        for nonce in iterator:
            block = "{0}:{1}".format(prefix_str, nonce).encode("utf-8")
            if use_md5:
                h = hashlib.md5(block).hexdigest()
            else:
                h = hashlib.sha256(block).hexdigest()

            if h.startswith(target_str):
                matched_count += 1
                if len(sample_matches) < 5:
                    sample_matches.append("{0} (nonce={1})".format(h, nonce))

            if h < min_hash:
                min_hash = h
                min_nonce = nonce

        return {
            "matched_count": int(matched_count),
            "sample_matches": sample_matches,
            "min_hash": str(min_hash),
            "min_nonce": int(min_nonce)
        }

    @staticmethod
    @expose
    def myreduce(mapped):
        total_matched = 0
        all_samples = []
        global_min_hash = "f" * 64
        global_min_nonce = -1

        for res in mapped:
            data = res.value
            total_matched += data["matched_count"]
            for s in data["sample_matches"]:
                if len(all_samples) < 10:
                    all_samples.append(s)
            if data["min_hash"] < global_min_hash:
                global_min_hash = data["min_hash"]
                global_min_nonce = data["min_nonce"]

        return {
            "total_matched": total_matched,
            "samples": all_samples,
            "min_hash": global_min_hash,
            "min_nonce": global_min_nonce
        }

    def read_input(self):
        prefix = "KNU_Cloud_Computing_Lab1_Block"
        algo = "sha256"
        total_iterations = 8000000
        target_zeros = "00000"
        try:
            with open(self.input_file_name, "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            if len(lines) == 1 and lines[0].isdigit():
                total_iterations = int(lines[0])
            else:
                if len(lines) >= 1:
                    prefix = str(lines[0])
                if len(lines) >= 2:
                    algo = str(lines[1])
                if len(lines) >= 3:
                    total_iterations = int(lines[2])
                if len(lines) >= 4:
                    target_zeros = str(lines[3])
        except Exception:
            pass
        return prefix, algo, total_iterations, target_zeros

    def write_output(self, algo, total_iterations, num_workers, elapsed_time, target_zeros, reduced):
        with open(self.output_file_name, "w") as f:
            f.write("=== PARCS Parallel Hashing Report (SHA-256 / MD5) ===\n")
            f.write("Algorithm:          %s\n" % algo.upper())
            f.write("Total hashes:       %d\n" % total_iterations)
            f.write("Workers (N):        %d\n" % num_workers)
            f.write("Execution time:     %.4f seconds\n" % elapsed_time)
            f.write("Throughput:         %.2f hashes/sec\n" % (total_iterations / elapsed_time))
            f.write("Target prefix:      '%s'\n" % target_zeros)
            f.write("Matches found:      %d\n" % reduced["total_matched"])
            f.write("Minimum hash:       %s (nonce=%d)\n" % (reduced["min_hash"], reduced["min_nonce"]))
            f.write("Sample matches:\n")
            for s in reduced["samples"]:
                f.write("  - %s\n" % s)