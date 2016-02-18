import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import re
import numpy as np
import sys

# Load data
data = open(sys.argv[1]).read()
RGX = r'#.*?Learning epochs=(\d+), inference epochs=(\d+).*?\n(\d\.?\d*)\n(\d\.?\d*)'
les, ies, md, wd = zip(*re.findall(RGX, data, flags=re.S))

# Plot marginals stability
plt.plot(map(lambda x : np.log10(int(x)), ies), map(float, md), '--o')
plt.xlabel('Log_10(# of inference epochs)')
plt.ylabel('Avg. abs. difference in marginal value')
plt.title('Avg. change in marginals between runs')
plt.savefig('marginals-stability.png')

# Plot weights stability
plt.plot(map(lambda x : np.log10(int(x)), les), map(lambda f : 100*float(f), wd), '--o')
plt.xlabel('Log_10(# of learning epochs)')
plt.ylabel('Avg. abs. relative (%) difference in weight value')
plt.title('Avg. change in weights between runs')
plt.savefig('weights-stability.png')
