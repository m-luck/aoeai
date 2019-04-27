import numpy as np
import torch
import torchvision
import torch.nn.functional as F
import torchvision.transforms as transforms
import time
from torch.autograd import Variable
from torch.utils.data.sampler import SubsetRandomSampler

seed = 0xDEADBEEF # Wagyu.

np.random.seed(seed)
torch.manual_seed(seed)

select = ('NONE', 'MAN-AT-ARMS', 'PIKEMAN', 'SKIRMISHER', 'SCOUT', 'KNIGHT')
x = None
y = None

#Training
n_training_samples = 20000
train_sampler = SubsetRandomSampler(np.arange(n_training_samples, dtype=np.int64))

#Validation
n_val_samples = 4000
val_sampler = SubsetRandomSampler(np.arange(n_training_samples, n_training_samples + n_val_samples, dtype=np.int64))

#Test
n_test_samples = 4000
test_sampler = SubsetRandomSampler(np.arange(n_test_samples, dtype=np.int64))

class ScoutCNN(torch.nn.Module):
    
    def __init__(self):
        super(SimpleCNN, self).__init__()
        
        # Remember that image size is 256, 256. Grayscale, so 1 channel.
        # Our batch shape for input is (1, 256, 256)
        '''
        The filter (of size kernel,kernel) scans over the image, and skips a pixel column each step.  
        [ ][ ][*][*][*][ ]... 
        [ ][ ][*][*][*][ ]...
        [ ][ ][*][*][*][ ]...
        [ ][ ][ ][ ][ ][ ]...
        [ ][ ][ ][ ][ ][ ]
        [ ][ ][ ][ ][ ][ ]
         .  .  .  .  .  .
         .  .  .  .  .  .
         .  .  .  .  .  .
        '''
        # Image is grayscale (1 channel) and 64px x 64px. We choose 16 filter types. 
        self.conv1 = torch.nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)

        #Pooling leads to 64x64 -> 32x32
        self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2, padding=0)

        # (16 conv filters * 32px * 32px) input features; choose 32 output features.
        self.fc1 = torch.nn.Linear(16 * 32 * 32, 32)

        # 32 input features from fc1; 2 output features for our x and y 
        self.fc2 = torch.nn.Linear(32, 2)
        
    def forward(self, x):
        
        #Computes the activation of the first convolution
        #Size changes from (3, 32, 32) to (18, 32, 32)
        x = F.relu(self.conv1(x))
        
        #Size changes from (18, 32, 32) to (18, 16, 16)
        x = self.pool(x)
        
        #Reshape data to input to the input layer of the neural net
        #Size changes from (18, 16, 16) to (1, 4608)
        #Recall that the -1 infers this dimension from the other given dimension
        x = x.view(-1, 16 * 32 *32)
        
        #Computes the activation of the first fully connected layer
        #Size changes from (1, 4608) to (1, 64)
        x = F.relu(self.fc1(x))
        
        #Computes the second fully connected layer (activation applied later)
        #Size changes from (1, 64) to (1, 10)
        x = self.fc2(x)

        return(x)

def get_loader(csv_path, batch_size):
    '''
    Takes in a dataset and batch size for loading. 
    '''
    unit_trials = UnitClickData(csv_path)
    loader = torch.utils.data.DataLoader(dataset=unit_trials, batch_size=batch_size, shuffle=True, num_workers=2)
    return(loader)

test_loader = get_loader(testset_csv, 4)
validation_loader = get_loader(valset_csv, 128)

def createLossAndOptimizer(net, learning_rate=0.001):
    loss = torch.nn.CrossEntropyLoss()
    optimizer = optim.Adam(net.parameters(), lr=learning_rate)
    return(loss, optimizer)


def train(net, batch_size, n_epochs, learning_rate):
    
    #Print all of the hyperparameters of the training iteration:
    print("===== HYPERPARAMETERS =====")
    print("batch_size=", batch_size)
    print("epochs=", n_epochs)
    print("learning_rate=", learning_rate)
    print("=" * 30)
    
    #Get training data
    train_loader = get_train_loader(batch_size)
    n_batches = len(train_loader)
    
    #Create our loss and optimizer functions
    loss, optimizer = createLossAndOptimizer(net, learning_rate)
    
    #Time for printing
    training_start_time = time.time()
    
    #Loop for n_epochs
    for epoch in range(n_epochs):
        
        running_loss = 0.0
        print_every = n_batches // 10
        epoch_start_time = time.time()
        total_train_loss = 0
        
        for i, data in enumerate(train_loader, 0):
            
            #Get inputs
            inputs, labels = data
            
            #Wrap them in a Variable object
            inputs, labels = Variable(inputs), Variable(labels)
            
            #Set the parameter gradients to zero
            optimizer.zero_grad()
            
            #Forward pass, backward pass, optimize
            outputs = net(inputs)
            loss_size = loss(outputs, labels)
            loss_size.backward()
            optimizer.step()
            
            #Print statistics
            running_loss += loss_size.data[0]
            total_train_loss += loss_size.data[0]
            
            #Print every 10th batch of an epoch
            if (i + 1) % (print_every + 1) == 0:
                print("Epoch {}, {:d}% \t train_loss: {:.2f} took: {:.2f}s".format(
                        epoch+1, int(100 * (i+1) / n_batches), running_loss / print_every, time.time() - start_time))
                #Reset running loss and time
                running_loss = 0.0
                start_time = time.time()
            
        #At the end of the epoch, do a pass on the validation set
        total_val_loss = 0
        for inputs, labels in val_loader:
            
            #Wrap tensors in Variables
            inputs, labels = Variable(inputs), Variable(labels)
            
            #Forward pass
            value_outputs = net(inputs)
            value_loss_size = loss(value_outputs, labels)
            total_val_loss += value_loss_size.data[0]
            
        print("Validation loss = {:.2f}".format(total_val_loss / len(validation_loader)))
        
    print("Training finished, took {:.2f}s".format(time.time() - training_start_time))
