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
        loss_list.append(float(curr_loss))
epochs = np.array(epochs_list)
loss = np.array(loss_list)

fig = plt.figure(1)
graphA = plt.subplot(211)
graphA.set_ylabel('L1 Loss')
plt.plot(epochs, loss, 'bo', epochs, loss, 'k')

epochs_list = []
loss_list = []
val_loss_path = sys.argv[2]
with open(val_loss_path,"r") as rdr:
    for line in rdr:
        curr_epoch, curr_loss = line.split(':')
        epochs_list.append(int(curr_epoch))
        loss_list.append(float(curr_loss))
epochs = np.array(epochs_list)
loss = np.array(loss_list)

epochs = np.array(epochs_list)
loss = np.array(loss_list)
graphB = plt.subplot(212)
graphB.set_ylabel('L2 Loss')
graphB.set_xlabel('Epochs')
plt.plot(epochs, loss, 'bo', epochs, loss, 'k')

plt.show()