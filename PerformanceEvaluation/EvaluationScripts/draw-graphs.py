import sys
import glob
import json
import traceback
import os
import numpy as np
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.font_manager import FontProperties

from pylab import rcParams
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
rcParams.update({'font.size': 16})


def find_settings(folder):
    configs = glob.glob(folder + "/*/")
    configs.sort(key=lambda elem: int(elem.split("_")[-1].replace("/", "")))
    return configs


def print_chart(y_ticks, pull_values_1, pull_values_2, push_values_1, push_values_2, y_label_1, y_label_2,
                range_1=None, range_2=None,
                title="", filename="test.pdf"):
    fig, ax1 = plt.subplots()
    t = y_ticks
    plots = []
    ax1.set_title(title)
    ax1.plot(t, push_values_1, 'r-o', label="Delivery Rate Push")
    ax1.plot(t, pull_values_1, 'b-^', label="Delivery Rate Pull")
    ax1.set_xlabel('Number of parallel forwarded voice streams')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel(y_label_1)
    ax1.tick_params('y')
    if range_1 is not None:
        axes = plt.gca()
        axes.set_ylim(range_1)

    ax2 = ax1.twinx()
    ax2.plot(t, push_values_2, 'r--o', label="CPU Utilization Push")
    ax2.plot(t, pull_values_2, 'b--^', label="CPU Utilization Pull")
    ax2.set_ylabel(y_label_2, rotation=90, labelpad=5)
    ax2.tick_params('y')
    if range_2 is not None:
        axes = plt.gca()
        axes.set_ylim(range_2)

    fontP = FontProperties()
    fontP.set_size("14")

    # ask matplotlib for the plotted objects and their labels
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="center right", prop=fontP, bbox_to_anchor=(0.98, 0.4))

    # fig.tight_layout()
    # plt.show()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()


if len(sys.argv) != 2:
    print("Usage: $ python voip-topo-metric-calculation path_to_run")
    exit(-1)
else:
    folder = sys.argv[1]

    num_calls = []

    push_cpu = []
    push_mem = []
    push_delivery_rate = []
    push_propagation_delay = []

    pull_cpu = []
    pull_mem = []
    pull_delivery_rate = []
    pull_propagation_delay = []

    configs = find_settings(folder)
    for conf in configs:
        num_calls.append(float(conf.split("_")[-1].replace("/", "")))

        f = open(conf + "/PULL/averages.json", "r")
        content = json.loads(f.readlines()[0])
        f.close()
        pull_cpu.append(float(content["perf_values"]["cpu"][0]) / 100)
        pull_mem.append(float(content["perf_values"]["mem"][0]))
        pull_propagation_delay.append(float(content["propagation_delay"][0]))
        pull_delivery_rate.append(float(content["delivery_rate"][0]))

        f = open(conf + "/PUSH/averages.json", "r")
        content = json.loads(f.readlines()[0])
        f.close()
        push_cpu.append(float(content["perf_values"]["cpu"][0]) / 100)
        push_mem.append(float(content["perf_values"]["mem"][0]))
        push_propagation_delay.append(float(content["propagation_delay"][0]))
        push_delivery_rate.append(float(content["delivery_rate"][0]))

    print(num_calls)
    print(push_cpu)

    print_chart(num_calls, pull_delivery_rate, pull_cpu, push_delivery_rate, push_cpu, "Expected/Delivered Data Packet Ratio",
                "CPU usage of NFD", filename="rate_cpu.pdf", title="Delivery Rate vs. CPU Usage", range_1=[0, 1.1], range_2=[0, 1.1],)
    print_chart(num_calls, pull_delivery_rate, pull_mem, push_delivery_rate, push_mem, "Delivery Rate",
                "Memory Utilization [%]", filename="rate_mem.pdf", title="Delivery Rate vs. Memory Utilization", range_1=[0, 1.1])
    print_chart(num_calls, pull_delivery_rate, pull_propagation_delay, push_delivery_rate, push_propagation_delay,
                "Delivery Rate", "Propagation Delay", filename="rate_delay.pdf",
                title="Delivery Rate vs. Propagation Delay", range_1=[0, 1.1])
    print_chart(num_calls, pull_propagation_delay, pull_cpu, push_propagation_delay, push_cpu, "Propagation Delay [ms]",
                "CPU Utilization", filename="delay_cpu.pdf", title="Propagation Delay vs. CPU Utilization", range_2=[0, 1.1],)
