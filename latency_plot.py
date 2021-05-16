import sys
import os
import matplotlib.pyplot as plt
import statistics

from matplotlib.ticker import NullFormatter  # useful for `logit` scale
from matplotlib.ticker import ScalarFormatter  # useful for `logit` scale

def plot_data(path, utilisationPath):
    startIndex = 3
    count = 25
    actualBlockCount = 0
    startTime = -1
    stopTime = -1
    results = []
    for fName in os.listdir(path):
        fPath = os.path.join(path, fName)
        if fName == ".gitkeep":
            continue
        with open(fPath, 'r') as f:
            localBlockCount = 0
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
                    localBlockCount = localBlockCount + 1
                    if startTime < 0 or ((blockIndex == startIndex) and (blockTime < startTime)):
                        startTime = blockTime
                    if blockTime > stopTime:
                        stopTime = blockTime
                    if localBlockCount > actualBlockCount:
                        actualBlockCount = localBlockCount
                if localBlockCount == count:
                    break
            results.append((fName, l))
    # (all the data)
    for r in results:
        # in logarythmic scale based on logistic distribution
        plt.plot([(float(x[3]-startTime)/1000000000.0) for x in r[1]], [(x+1)/float(actualBlockCount) for x in range(actualBlockCount)], linewidth=0.1) #label=r[0],

    nPeers = len(results)

    # Build LPL plot
    tFastest = []
    tSlowest = []
    tMedian = []
    #  getting fastest/slowest peer for EACH block
    # for i in range(actualBlockCount):
    #     blockIFastestPeer = (min([r[1][i][3] for r in results if len(r[1]) > i])-startTime)/1000000000
    #     tFastest.append(blockIFastestPeer)
    #     blockISlowestPeer = (max(r[1][i][3] for r in results if len(r[1]) > i) - startTime) / 1000000000
    #     tSlowest.append(blockISlowestPeer)
    #     blockIMedianPeer = (statistics.mean(r[1][i][3] for r in results if len(r[1]) > i) - startTime) / 1000000000
    #     tMedian.append(blockIMedianPeer)

    #  getting fastest/slowest peer by the time of receiving ALL blocks
    results.sort(key=lambda peer: peer[1][len(peer[1])-1][3])  # sort by the last received block time
    for peer in results:
        if len(peer[1]) == actualBlockCount:
            tFastest = [(t[3] - startTime) / 1000000000.0 for t in peer[1]]
            break
    for i in range(nPeers):
        peer = results[nPeers-i-1]
        if len(peer[1]) == actualBlockCount:
            tSlowest = [(t[3] - startTime) / 1000000000.0 for t in peer[1]]
            break
    medianPeer = results[int(nPeers/2)+2]
    tMedian = [(t[3] - startTime) / 1000000000.0 for t in medianPeer[1]]

    blocks = [((x+1) / actualBlockCount) for x in range(actualBlockCount)]
    plt.plot(tFastest, blocks, '1', label="fastest peer", linewidth=0.1)
    plt.plot(tSlowest, blocks, '1', label="slowest peer", linewidth=0.1)
    plt.plot(tMedian, blocks, '1', label="median peer", linewidth=0.1)
    plt.yscale('logit')
    plt.xscale('linear')
    plt.xlabel('Time, sec')
    plt.ylabel('Received blocks, out of NBlocks (logit scale)')
    plt.title('Latency at the peer level using the original gossip module of NeoGo')

    y_formatter = ScalarFormatter(useOffset=True)
    plt.gca().yaxis.set_major_formatter(y_formatter)
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.
    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.legend()
    # plt.show()
    plt.savefig('./img/lpl' + '.png')

    # Build LBL plot
    plt.cla()
    blockTimes = []
    peers = [(j + 1) / nPeers for j in range(nPeers)]
    for i in range(len(results[0][1])):
        startIBlock = min(r[1][i][3] for r in results if len(r[1]) > i)
        x = [(r[1][i][3]-startIBlock) / 1000000000 for r in results if len(r[1]) > i]
        x.sort()
        blockTimes.append(x)
        plt.plot(x, peers[:len(x)], linewidth=0.1)

    # Build LBL plot
    bFastest = []
    bSlowest = []
    bMedian = []
    for i in range(len(results)):
        peerIFastestBlock = min(t[i] for t in blockTimes if len(t) > i)
        bFastest.append(peerIFastestBlock)
        peerISlowestBlock = max(t[i] for t in blockTimes if len(t) > i)
        bSlowest.append(peerISlowestBlock)
        peerIMedianBlock = statistics.mean(t[i] for t in blockTimes if len(t) > i)
        bMedian.append(peerIMedianBlock)
    plt.plot(bFastest, peers, '1', label="fastest block", linewidth=0.1)
    plt.plot(bSlowest, peers, '1', label="slowest block", linewidth=0.1)
    plt.plot(bMedian, peers, '1', label="median block", linewidth=0.1)

    plt.yscale('logit')
    plt.xscale('linear')
    xRightLim = bSlowest[len(bSlowest)-1]+1
    #plt.xlim(-0.5, xRightLim)
    plt.xlabel('Time, sec')
    plt.ylabel('Peer that received the block, out of NPeers (logit scale)')
    plt.title('Latency at the block level using the original gossip module of NeoGo')
    y_formatter = ScalarFormatter(useOffset=True)
    plt.gca().yaxis.set_major_formatter(y_formatter)
    # Format the minor tick labels of the y-axis into empty strings with
    # `NullFormatter`, to avoid cumbering the axis with too many labels.
    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.legend()
    # plt.show()
    plt.savefig('./img/lbl' + '.png')

    # Build Network Utilisation plot
    plt.cla()
    interval = 2_000_000_000  # 500ms = 0.5s
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
    plt.plot(intervals, consensusMeanY, c='blue', label='leader peer', linewidth=0.5)  # KByte
    plt.plot(intervals, [consensusAVG for x in intervals], c='blue', ls="-.", linewidth=0.5)
    plt.plot(intervals, standardMeanY, c='orange', label='regular peer', linewidth=0.5)  # KByte
    plt.plot(intervals, [standardAVG for x in intervals], c='orange', ls="-.", linewidth=0.5)

    plt.xlabel('Time, sec')
    plt.ylabel('Network utilization, KB/s')
    plt.title('Network utilization using the original gossip module of NeoGo')
    plt.legend()
    # plt.show()
    plt.savefig('./img/nu' + '.png')


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
