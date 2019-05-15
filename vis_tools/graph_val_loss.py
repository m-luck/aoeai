import matplotlib.pyplot as plt 
import numpy as np
import sys

hfont = {'fontname':'Monospace', 'size' : 9}
plt.xticks(fontsize=7, rotation=90)
# TOP LEFT
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
graphA = plt.subplot(221)
graphA.set_ylabel('L2 8', **hfont)
graphA.tick_params(axis = 'both', which = 'major', labelsize = 8)
plt.plot(epochs, loss, 'r.', epochs, loss, 'k')

# TOP RIGHT
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

fig = plt.figure(1)
graphB = plt.subplot(222)
graphB.set_ylabel('L1 8', **hfont)
graphB.tick_params(axis = 'both', which = 'major', labelsize = 8)
plt.plot(epochs, loss, 'y.', epochs, loss, 'k')

# BOTTOM LEFT
epochs_list = []
loss_list = []
val_loss_path = sys.argv[3]
with open(val_loss_path,"r") as rdr:
    for line in rdr:
        curr_epoch, curr_loss = line.split(':')
        epochs_list.append(int(curr_epoch))
        loss_list.append(float(curr_loss))
epochs = np.array(epochs_list)
loss = np.array(loss_list)

fig = plt.figure(1)
graphC = plt.subplot(223)
graphC.set_ylabel('L2 128', **hfont)
graphC.tick_params(axis = 'both', which = 'major', labelsize = 8)
plt.plot(epochs, loss, 'r.', epochs, loss, 'k')

# BOTTOM RIGHT
epochs_list = []
loss_list = []
val_loss_path = sys.argv[4]
with open(val_loss_path,"r") as rdr:
    for line in rdr:
        curr_epoch, curr_loss = line.split(':')
        epochs_list.append(int(curr_epoch))
        loss_list.append(float(curr_loss))
epochs = np.array(epochs_list)
loss = np.array(loss_list)

epochs = np.array(epochs_list)
loss = np.array(loss_list)
graphD = plt.subplot(224)
graphD.set_ylabel('L1 128', **hfont)
graphD.set_xlabel('Epochs', **hfont)
graphD.tick_params(axis = 'both', which = 'major', labelsize = 8)
plt.plot(epochs, loss, 'y.', epochs, loss, 'k')

plt.show()