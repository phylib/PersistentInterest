import sys
import glob
import json
import traceback
import os
import numpy as np
import scipy as sp
import scipy.stats


#####################################################################
#
# This script calculates averages of one emulation run for the performance
# comparison of the forwarding capabilities when using PIs and classical
# Interests.
# The averages are written to the file "averages.json" in json format
#
# To execute the script on a many folders in parallel use:
# find . | grep nfd.log | xargs -I {} -P 10 python ~/PythonScripts/pitestbedeval/average-calculation.py {}
#
#####################################################################


class LogLine:
    def __init__(self, line):
        parts = line.split("\t")
        self.time = int(parts[0])
        self.node = parts[1]
        self.packet_type = parts[2]
        self.send_receive = parts[3]
        self.name = parts[4]
        if len(self.name.split("/")) == 3:
            self.seq_no = -1
        else:
            self.seq_no = int(self.name.split("/")[3])


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
    if np.isnan(h):
        h = 0
    return m, h


def calc_perf_values(folder):
    perf_values = {}
    with open(folder + "/nfd.log") as f:
        file_content = f.readlines()[1:]
        f.close()
        cpu_vals = []
        mem_vals = []
        for line in file_content:
            parts = line.split(", ")
            cpu_vals.append(float(parts[1]))
            mem_vals.append(float(parts[2]))
        perf_values["cpu"] = mean_confidence_interval(cpu_vals)
        perf_values["mem"] = mean_confidence_interval(mem_vals)
    return perf_values


def findApplications(folder):
    files = glob.glob(folder + "/S*.log")
    apps = [f.split("/")[-1].replace(".log", "").replace("S", "") for f in files]
    return apps


def calc_values_for_app(app_no):
    server_log_file = folder + "/S" + str(app_no) + ".log"
    client_log_file = folder + "/C" + str(app_no) + ".log"
    server_log = []
    client_log = []
    with open(server_log_file) as f:
        tmp = f.readlines()[1:]
        for l in tmp:
            server_log.append(LogLine(l))
        f.close()
    with open(client_log_file) as f:
        tmp = f.readlines()[1:]
        for l in tmp:
            client_log.append(LogLine(l))
        f.close()

    # Calc number of received/expected packet ratio
    max_server_seq_no = max([l.seq_no for l in server_log if l.packet_type == "D" and l.send_receive == "S"])
    max_client_seq_no = max([l.seq_no for l in client_log if l.packet_type == "I" and l.send_receive == "S"])
    required_packets = max(max_server_seq_no, max_client_seq_no) + 1

    num_received_data_packets = len(
        set([l.seq_no for l in client_log if l.send_receive == "R" and l.packet_type == "D"]))
    delivery_rate = num_received_data_packets / float(required_packets)

    # calculate propagation delay
    propagation_delays = []
    received_data_packets = [l for l in client_log if l.packet_type == "D" and l.send_receive == "R"]
    send_data_packets = [l for l in server_log if l.packet_type == "D" and l.send_receive == "S"]
    for packet in received_data_packets:
        seq_no = packet.seq_no
        for send_packet in send_data_packets:
            if send_packet.seq_no == seq_no:
                propagation_delays.append(packet.time - send_packet.time)
                break

    propagation_delay = (sum(propagation_delays) / float(len(propagation_delays)))

    return {"delivery_rate": delivery_rate, "propagation_delay": propagation_delay}


if len(sys.argv) != 2:
    print("Usage: $ python voip-topo-metric-calculation path_to_run")
    exit(-1)
else:
    folder = sys.argv[1]
    if os.path.isfile(folder):  # Remove last part of folder-string in the case that a file was selected
        folder = "/".join(folder.split("/")[:-1])

    perf_values = calc_perf_values(folder)

    applications = findApplications(folder)
    rates = []
    delays = []
    for app in applications:
        tmp = calc_values_for_app(app)
        rates.append(tmp["delivery_rate"])
        delays.append(tmp["propagation_delay"])

    delivery_rate = mean_confidence_interval(rates)
    propagation_delay = mean_confidence_interval(delays)

    results = {
        "perf_values": perf_values,
        "delivery_rate": delivery_rate,
        "propagation_delay": propagation_delay
    }

    f = open(folder + "/averages.json", "w+")
    f.write(json.dumps(results))
    f.close()
    # print(perf_values)
    # print(delivery_rate)
    # try:
    #    f = open(folder + "/packet_hist.txt", "w+")
    #    f.write(json.dumps(packet_hists))
    #    f.close()

    # except Exception:
    #    print("Error in calc_metrics(..) " + repr(Exception))
    #    traceback.print_exc()
    #    exit(-1)
