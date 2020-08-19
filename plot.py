import sys
import os
import matplotlib.pyplot as plt

# files batch is a dictionary {plot_name:[[log_file, legend_string, line colour],...]}
files_batch = {
    'single 10 wrk':[["GoSingle_wrk_10.log", "go", 'blueviolet'],
                        ["no_VT_GoSingle_wrk_10.log", "go, no VT", 'orangered'],
                        ["SharpSingle_wrk_10.log", "c#", 'green']],
    'single 30 wrk':[["GoSingle_wrk_30.log", "go",  'blueviolet'],
                        ["no_VT_GoSingle_wrk_30.log", "go, no VT",  'orangered'],
                        ["SharpSingle_wrk_30.log", "c#",  'green']],
    'single 100 wrk':[["GoSingle_wrk_100.log", "go",  'blueviolet'],
                        ["no_VT_GoSingle_wrk_100.log", "go, no VT",  'orangered']],
    'single 25 rate':[["GoSingle_rate_25.log", "go", 'blueviolet'],
                        ["no_VT_GoSingle_rate_25.log", "go, no VT", 'orangered'],
                        ["SharpSingle_rate_25.log", "c#", 'green']],
    'single 50 rate':[["GoSingle_rate_50.log", "go", 'blueviolet'],
                         ["no_VT_GoSingle_rate_50.log", "go, no VT", 'orangered']],
    'single 60 rate':[["GoSingle_rate_60.log", "go", 'blueviolet'],
                         ["no_VT_GoSingle_rate_60.log", "go, no VT", 'orangered']],
    'single 300 rate':[["GoSingle_rate_300.log", "go", 'blueviolet'],
                         ["no_VT_GoSingle_rate_300.log", "go, no VT", 'orangered']],
    'single 1000 rate':[["GoSingle_rate_1000.log", "go", 'blueviolet'],
                        ["no_VT_GoSingle_rate_1000.log", "go, no VT", 'orangered']],
    '4 nodes 10 wrk': [["Go4x1_wrk_10.log", "go", 'blueviolet'],
                          ["no_VT_Go4x1_wrk_10.log", "go, no VT", 'orangered'],
                          ["Sharp4x_SharpRPC_wrk_10.log", "c#", 'green'],
                          ["Sharp4x_GoRPC_wrk_10.log", "c# + go RPC", 'aqua']],
    '4 nodes 30 wrk': [["Go4x1_wrk_30.log", "go", 'blueviolet'],
                          ["no_VT_Go4x1_wrk_30.log", "go, no VT", 'orangered'],
                          ["Sharp4x_SharpRPC_wrk_30.log", "c#", 'green'],
                          ["Sharp4x_GoRPC_wrk_30.log", "c# + go RPC", 'aqua']],
    '4 nodes 100 wrk': [["Go4x1_wrk_100.log", "go", 'blueviolet'],
                          ["no_VT_Go4x1_wrk_100.log", "go, no VT", 'orangered'],
                          ["Sharp4x_GoRPC_wrk_100.log", "c# + go RPC", 'aqua']],
    '4 nodes 25 rate': [["Go4x1_rate_25.log", "go", 'blueviolet'],
                          ["no_VT_Go4x1_rate_25.log", "go, no VT", 'orangered'],
                          ["Sharp4x_SharpRPC_rate_25.log", "c#", 'green'],
                          ["Sharp4x_GoRPC_rate_25.log", "c# + go RPC", 'aqua']],
    '4 nodes 50 rate': [["Go4x1_rate_50.log", "go", 'blueviolet'],
                          ["no_VT_Go4x1_rate_50.log", "go, no VT", 'orangered'],
                          ["Sharp4x_GoRPC_rate_50.log", "c# + go RPC", 'aqua']],
    '4 nodes 60 rate': [["Go4x1_rate_60.log", "go", 'blueviolet'],
                          ["no_VT_Go4x1_rate_60.log", "go, no VT", 'orangered'],
                          ["Sharp4x_GoRPC_rate_60.log", "c# + go RPC", 'aqua']],
    '4 nodes 300 rate': [["Go4x1_rate_300.log", "go", 'blueviolet'],
                            ["no_VT_Go4x1_rate_300.log", "go, no VT", 'orangered'],
                            ["Sharp4x_GoRPC_rate_300.log", "c# + go RPC", 'aqua']],
    '4 nodes 1000 rate': [["Go4x1_rate_1000.log", "go", 'blueviolet'],
                            ["no_VT_Go4x1_rate_1000.log", "go, no VT", 'orangered'],
                            ["Sharp4x_GoRPC_rate_1000.log", "c# + go RPC", 'aqua']],

}


def plot_data(path):
    large = 22; med = 14;
    params = {'axes.titlesize': large,
              'legend.fontsize': med,
              'figure.figsize': (12, 8),
              'axes.labelsize': med,
              'axes.titlesize': med,
              'xtick.labelsize': med,
              'ytick.labelsize': med,
              'figure.titlesize': large}
    plt.rcParams.update(params)

    for name, files in files_batch.items():
        tps = [[]]*len(files)
        cpu = [[]]*len(files)
        mem = [[]]*len(files)
        avgTps = []*len(files)

        # extract data
        for fileCounter in range(len(files)):
            file = files[fileCounter]
            cpuFile = []
            memFile = []
            tpsFile = []
            with open(path + file[0], "r") as f:
                lines = f.readlines()
                avgTps.append(float(lines[5][6:]))
                for i in range(11, len(lines)):
                    line = lines[i]
                    cpumem = line.split('%,')
                    if len(cpumem) == 2:
                        cpuFile.append(float(cpumem[0]))
                        memFile.append(float(cpumem[1].strip(' ').strip('\n').strip('MB')))
                    else:
                        tpsStart = i + 2
                        break
                for i in range(tpsStart, len(lines) - 1):
                    tpsFile.append(float(lines[i]))
            tps[fileCounter] = tpsFile
            cpu[fileCounter] = cpuFile
            mem[fileCounter] = memFile

        # plot tps for `name`
        for i in range(len(files)):
            file = files[i]
            plt.plot(tps[i], label=file[1], color=file[2], linewidth=0.8)
            plt.axhline(y=avgTps[i], label=file[1] + ' avg TPS',linestyle='--', color=file[2], linewidth=0.8)
        plt.xlabel('Blocks')
        plt.ylabel('Transactions per second')
        plt.title('tps '+name)
        plt.legend()
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.savefig('./img/tps_' + name.replace(' ', '_') + '.png')
        plt.close()

        # plot cpu for `name`
        for i in range(len(files)):
            file = files[i]
            plt.plot(cpu[i], label=file[1], color=file[2], linewidth=0.8)
        plt.xlabel('Time')
        plt.ylabel('CPU, %')
        plt.title('cpu '+name)
        plt.legend()
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.savefig('./img/cpu_' + name.replace(' ', '_') + '.png')
        plt.close()

        # plot memory for `name`
        for i in range(len(files)):
            file = files[i]
            plt.plot(mem[i], label=file[1], color=file[2], linewidth=0.8)
        plt.xlabel('Time')
        plt.ylabel('Memory, Mb')
        plt.title('memory '+name)
        plt.legend()
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.savefig('./img/mem_' + name.replace(' ', '_') + '.png')
        plt.close()


if __name__ == '__main__':
    helpMessage = 'Please, provide logs path. Example:\n\t$ python3 plot.py ./logs/'
    if len(sys.argv) < 2:
        print(helpMessage)
        exit(1)
    path = sys.argv[1]
    if not os.path.isdir(path):
        print(path+' is not a directory.')
        print(helpMessage)
        exit(1)

    if not os.path.exists('./img'):
        os.makedirs('./img')
    plot_data(path)
    print("Images successfully saved to ./img folder.")
