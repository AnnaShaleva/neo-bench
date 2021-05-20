import sys
import os
import matplotlib.pyplot as plt
import statistics

from matplotlib.ticker import NullFormatter  # useful for `logit` scale
from matplotlib.ticker import ScalarFormatter  # useful for `logit` scale

# firstBlockIndex is the index of the first generates block in experiment
firstBlockIndex = 3

def plot_data(path, utilisationPath):
    startIndex = 3
    count = 600
    interval = 10_000_000_000  # 5s

    results = []
    for fName in os.listdir(path):
        fPath = os.path.join(path, fName)
        if fName == ".gitkeep":
            continue
        with open(fPath, 'r') as f:
            indexesOfBlocksReceived = {}
            l = []
            for line in f.readlines():
                parts = line.split("\t")
                messageSourceType = parts[2].split(" ")[4]
                blockInfo = parts[3].split(" ")
                blockIndex = int(blockInfo[1][:-1])
                blockTimestamp = int(blockInfo[3][:-1])
                blockTime = int(blockInfo[5][:-2])
                if indexesOfBlocksReceived.get(blockIndex) is None:
                    l.append((messageSourceType, blockIndex, blockTimestamp, blockTime))
                    indexesOfBlocksReceived[blockIndex] = True
            results.append((fName, l))
    peerCount = len(results)
    blockCount = max(max(b[1] for b in r[1]) for r in results) - firstBlockIndex + 1
    # normalize results: sort by peer (from 20333 to max) and by block index (from idx=3 to max)
    fullArr = [[None for x in range(blockCount)] for y in range(peerCount)]
    for r in results:
        peerIndex = int(r[0]) - 20333
        for block in r[1]:
            blockIndex = block[1] - firstBlockIndex
            fullArr[peerIndex][blockIndex] = block[3]

    # remove files if needed
    removeFiles = False
    listToRemove = [20402, 20350]
    if removeFiles:
        for l in listToRemove:
            del (fullArr[l - 20333])
            peerCount = peerCount-1

    # trim right all columns with Null inside (these blocks were not received, usually these are several last blocks)
    columnToRemoveIdx = blockCount + 1
    for i in range(peerCount):
        for j in range(blockCount):
            if fullArr[i][j] is None:
                print(i+20333, j+3)
                if j < columnToRemoveIdx:
                    columnToRemoveIdx = j
                break
    if columnToRemoveIdx != blockCount+1:
        for i in range(peerCount):
            fullArr[i] = fullArr[i][:columnToRemoveIdx]
        blockCount = len(fullArr[0])
        print("Trim right columns starting from block #" + str(columnToRemoveIdx+firstBlockIndex) + ": Null found. Block count = " + str(blockCount))

    # trim right and left blocks which are not required
    if startIndex-firstBlockIndex > 0:
        for i in range(peerCount):
            fullArr[i] = fullArr[i][startIndex-firstBlockIndex:]
        blockCount = len(fullArr[0])
    if count < blockCount:
        for i in range(peerCount):
            fullArr[i] = fullArr[i][:count]
        blockCount = len(fullArr[0])

    print("Peer count: " + str(peerCount))
    print("Block count: " + str(blockCount) + " (starting from block #" + str(startIndex) + ")")
    # find start and stop time for experiment
    startTime = min(min(p) for p in fullArr)
    stopTime = max(max(p) for p in fullArr)

    # find dissemination start of each block and compute latencies for each block
    arr = [[None for x in range(blockCount)] for y in range(peerCount)]
    for j in range(blockCount):
        minTime = min(fullArr[i][j] for i in range(peerCount))
        for i in range(peerCount):
            arr[i][j] = (fullArr[i][j] - minTime) / 1_000_000_000.0  # convert to seconds

    # LPL for all peers
    y = [(x + 1) / float(blockCount) for x in range(blockCount)]
    lpl = arr.copy()
    for i in range(peerCount):
        # Option A: plot block diffs only
        lpl[i].sort()
        plt.plot(lpl[i], y, linewidth=0.1)

        # Option B: plot sum of diffs
        # s = 0
        # x = []
        # for j in range(blockCount):
        #    s = lpl[i][j] + s
        #    x.append(s)
        # plt.plot(x, y, linewidth=0.1)

    # LPL for fastest/slowest peer
    lpl.sort(key=lambda x: sum(x))
    plt.plot(lpl[0], y, '1', label="fastest peer", linewidth=0.1)
    plt.plot(lpl[peerCount-1], y, '1', label="slowest peer", linewidth=0.1)
    plt.plot(lpl[int((peerCount-1)/2)], y, '1', label="median peer", linewidth=0.1)

    plt.yscale('logit')
    plt.xscale('linear')
    plt.xlabel('Time, sec')
    plt.ylabel('Received blocks, out of NBlocks=' + str(blockCount)+' (logit scale)')
    plt.title('Latency at the peer level using the original gossip module of NeoGo')

    y_formatter = ScalarFormatter(useOffset=True)
    plt.gca().yaxis.set_major_formatter(y_formatter)
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.
    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.legend()
    # plt.show()
    plt.savefig('./img/lpl_diff' + '.png')

    # LBL for all peers
    plt.cla()
    y = [(x + 1) / float(peerCount) for x in range(peerCount)]
    lbl = []
    for j in range(blockCount):
        lst = [arr[i][j] for i in range(peerCount)]
        lst.sort()
        plt.plot(lst, y, linewidth=0.1)
        lbl.append(lst)

    # LBL for fastest/slowest peer
    lbl.sort(key=lambda x: max(x))
    plt.plot(lbl[0], y, '1', label="fastest block", linewidth=0.1)
    plt.plot(lbl[blockCount-1], y, '1', label="slowest block", linewidth=0.1)
    plt.plot(lbl[int((blockCount-1)/2)], y, '1', label="median block", linewidth=0.1)

    plt.yscale('logit')
    plt.xscale('linear')
    plt.xlabel('Time, sec')
    plt.ylabel('Peer that received the block, out of NPeers=' + str(peerCount)+' (logit scale)')
    plt.title('Latency at the block level using the original gossip module of NeoGo')

    y_formatter = ScalarFormatter(useOffset=True)
    plt.gca().yaxis.set_major_formatter(y_formatter)
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.
    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.legend()
    # plt.show()
    plt.savefig('./img/lbl_diff' + '.png')

    # Build Network Utilisation plot
    plt.cla()
    messages = []
    for fName in os.listdir(utilisationPath):
        fPath = os.path.join(utilisationPath, fName)
        if fName == ".gitkeep":
            continue
        with open(fPath, 'r') as f:
            l = []
            for line in f.readlines():
                parts = line.split("\t")[3].split(" ")
                msgType = parts[1][1:-2]
                msgSize = int(parts[3][:-1])
                msgTime = int(parts[5][:-2])
                if msgTime >= startTime:
                    l.append((msgType, msgSize, msgTime))
            messages.append((fName, l))

    # (all the data)
    # for m in messages:
    #     plt.plot([(float(x[2] - startTime) / 1000000000.0) for x in m[1]], [x[1]/1024. for x in m[1]], linewidth=0.1)
    intervals = [(x - startTime) / 1000000000.0 for x in range(startTime, stopTime, interval)]
    consensusPeers = []
    standardPeers = []
    for peer in messages:
        y = []
        for t in range(startTime, stopTime, interval):
            bytesSum = 0
            for msg in peer[1]:
                msgTime = msg[2]
                if t <= msgTime < t+interval:
                    bytesSum = bytesSum + msg[1]
            y.append(bytesSum)
        # plt.plot(intervals, [b / 1024. / (interval / 1000000000.0) for b in y]) # KByte
        if peer[0] == "20333" or peer[0] =="20334" or peer[0] == "20335" or peer[0] == "20336":
            consensusPeers.append(y)
        else:
            standardPeers.append(y)
    consensusMean = [statistics.mean([peer[i] for peer in consensusPeers]) for i in range(len(intervals))]
    standardMean = [statistics.mean([peer[i] for peer in standardPeers]) for i in range(len(intervals))]
    consensusMeanY = [b / 1024. / (interval / 1000000000.0) for b in consensusMean]
    standardMeanY = [b / 1024. / (interval / 1000000000.0) for b in standardMean]
    consensusAVG = statistics.mean(consensusMeanY)
    standardAVG = statistics.mean(standardMeanY)
    plt.plot(intervals, consensusMeanY, c='blue', label='consensus peer', linewidth=0.5)  # KByte
    plt.plot(intervals, [consensusAVG for x in intervals], c='blue', ls="-.", linewidth=0.5)
    plt.plot(intervals, standardMeanY, c='orange', label='regular peer', linewidth=0.5)  # KByte
    plt.plot(intervals, [standardAVG for x in intervals], c='orange', ls="-.", linewidth=0.5)

    plt.xlabel('Time, sec')
    plt.ylabel('Network utilization, KB/s')
    plt.title('Network utilization using the original gossip module of NeoGo')
    plt.legend()
    # plt.show()
    plt.savefig('./img/nu_diff' + '.png')


if __name__ == '__main__':
    helpMessage = 'Please, provide logs path. Example:\n\t$ python3 lpl_plot.py ./logs/ ./utilisation_logs/'
    if len(sys.argv) < 3:
        print(helpMessage)
        exit(1)
    path = sys.argv[1]
    utilisationPath = sys.argv[2]
    if not os.path.isdir(path):
        print(path+' is not a directory.')
        print(helpMessage)
        exit(1)
    if not os.path.isdir(utilisationPath):
        print(utilisationPath+' is not a directory.')
        print(helpMessage)
        exit(1)

    if not os.path.exists('./img'):
        os.makedirs('./img')
    plot_data(path, utilisationPath)
    print("Images successfully saved to ./img folder.")
