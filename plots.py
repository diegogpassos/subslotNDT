import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib
import numpy as np
import pandas as pd
import sys
import scipy.stats as st
import os
import time

def loadSamples(filename):
    df = pd.read_csv(filename, sep=" ", header=None)
    return df[2].to_numpy()

# Onesided confidence intervals
def intConf(data, conf):
    return st.sem(data) * st.t.ppf((1 + conf) / 2., len(data))

def filenameToParams(filename):
    components = filename.split("_")
    p = float(components[1].split("p")[1])
    s = int(components[2].split("s")[1])
    dc = float(components[3].split("dc")[1].split(".dat")[0])

    return p, s, dc

def loadAllDataFiles():

    df = pd.DataFrame(columns=["bidirectional", "dc", "p", "s", "ndt", "e"])
    i = 0

    directory = os.fsencode(".")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".dat"): 
            samples = loadSamples(filename)

            p, s, dc = filenameToParams(filename)
            ndt = np.mean(samples / s)
            e = intConf(samples / s, 0.95)
            bidirectional = filename.startswith("b")

            df.loc[i] = [bidirectional, dc, p, s, ndt, e]
            i = i + 1

    return df.sort_values(["bidirectional", "dc", "s", "p"])  

def plotNDTxS(df, label=''):
    x = df["s"].values
    y = df["ndt"].values
    yerr = df["e"].values
   
    plt.xlabel('Subslots per Slot (s)')
    plt.ylabel('NDT (Slots)')

    plt.grid(True, color='0.8', linestyle='--', )
    plt.tight_layout()

    plt.errorbar(x, y, yerr=yerr, capsize=5, lw=1, markersize=4, fmt='o-', label=label)

df = loadAllDataFiles()

rc('font', **{'family': 'serif', 'serif': ['cmr10']})
plt.rcParams["figure.figsize"] = (5,4)

plt.style.use('grayscale')

# Show that NDT almost does not change in the unidirectional case between methodologies
plotNDTxS(df.loc[(df['bidirectional'] == False) & (df['dc'] == 1.03) & (df['p'] == 0.4)], 'p = 0.4')
plotNDTxS(df.loc[(df['bidirectional'] == False) & (df['dc'] == 1.03) & (df['p'] == 0.7)], 'p = 0.7')
plotNDTxS(df.loc[(df['bidirectional'] == False) & (df['dc'] == 1.03) & (df['p'] == 1)], 'p = 1.0')
plt.legend(loc=(0.7, 0.5))

plt.savefig('unidirecionalVaryingP.png', dpi=300)
plt.close()
#plt.show()

# Show that, for p = 1, in the unidirectional discovery mode, NDT increases by 0.5 slot 
# in the proposed methodology with large s.
plotNDTxS(df.loc[(df['bidirectional'] == False) & (df['dc'] == 42.5) & (df['p'] == 1)])
plt.savefig('unidirecionalP=1DC42_5.png', dpi=300)
plt.close()
#plt.show()
plotNDTxS(df.loc[(df['bidirectional'] == False) & (df['dc'] == 9.02) & (df['p'] == 1)])
plt.savefig('unidirecionalP=1DC9_02.png', dpi=300)
plt.close()
#plt.show()

# Show that, for p = 1, in the bidirectional discovery mode, NDT decreases 
# in the proposed methodology with large s.
plotNDTxS(df.loc[(df['bidirectional'] == True) & (df['dc'] == 42.5) & (df['p'] == 1)])
plt.savefig('bidirecionalP=1DC42_5.png', dpi=300)
plt.close()
#plt.show()
plotNDTxS(df.loc[(df['bidirectional'] == True) & (df['dc'] == 9.02) & (df['p'] == 1)])
plt.savefig('bidirecionalP=1DC9_02.png', dpi=300)
plt.close()
#plt.show()

# Show that, for low p, in the bidirectional discovery mode, NDT decreases by half 
# in the proposed methodology with large s.
plotNDTxS(df.loc[(df['bidirectional'] == True) & (df['dc'] == 9.02) & (df['p'] == 0.1)])
plt.savefig('bidirecionalP=0_1DC9_02.png', dpi=300)
plt.close()
#plt.show()
