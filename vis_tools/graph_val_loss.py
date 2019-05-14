import matplotlib.pyplot as plt 
import numpy as np
import sys
epochs_list = []
loss_list = []
val_loss_path = sys.argv[1]
with open(val_loss_path,"r") as rdr:
    for line in rdr:
        curr_epoch, curr_loss = line.split(':')
        epochs_list.append(int(curr_epoch))
        loss_list.append(int(curr_loss))

epochs = np.array(epochs_list)
loss = np.array(loss_list)

plt.figure(1)
plt.subplot(211)
plt.plot(epochs, loss, 'bo', epochs, loss, 'k')

plt.subplot(212)
plt.plot(epochs, np.cos(2*np.pi*epochs), 'r--')
plt.show()