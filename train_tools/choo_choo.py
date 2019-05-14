import numpy as np
import sys
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import time
import cv2
import os
from torch.autograd import Variable
from torch.utils.data.sampler import SubsetRandomSampler

# Internal import.
import sub_data_setter

seed = 0xDEADBEEF # Wagyu.

np.random.seed(seed)
torch.manual_seed(seed)

device = torch.device("cuda" if torch.cuda.is_available() 
                                  else "cpu")

selected = ('NONE', 'MAN-AT-ARMS', 'PIKEMAN', 'SKIRMISHER', 'SCOUT', 'KNIGHT')
x = None
y = None

class ScoutCNN(torch.nn.Module):
    
    def __init__(self):
        super(ScoutCNN, self).__init__()
        
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
        self.fc1 = torch.nn.Linear(16 * 16 * 16, 32)

        # 32 input features from fc1; 2 output features for our x and y 
        self.fc2 = torch.nn.Linear(32, 2)
        
    def forward(self, x):
        
        #Computes the activation of the first convolution
        #Size changes from (3, 32, 32) to (18, 32, 32)
        x = F.relu(self.conv1(x))
        
        #Size changes from (18, 32, 32) to (18, 16, 16)
        x = self.pool(x)
        
        #Reshape data to input to the input layer of the neural net
        #Size changes from (18, 16, 16) to (1, 4096)
        #Recall that the -1 infers this dimension from the other given dimension
        x = x.view(-1, 16 * 16 * 16)
        
        #Computes the activation of the first fully connected layer
        #Size changes from (1, 4096) to (1, 32)
        x = F.relu(self.fc1(x))
        
        #Computes the second fully connected layer (activation applied later)
        #Size changes from (1, 32) to (1, 2)
        x = self.fc2(x)

        return(x)

def get_loader(csv_path, batch_size):
    '''
    Takes in a dataset and batch size for loading. 
    '''
    unit_trials = sub_data_setter.UnitClickData(csv_path)
    loader = torch.utils.data.DataLoader(dataset=unit_trials, batch_size=batch_size, shuffle=True, num_workers=2)
    return(loader)

def createLossAndOptimizer(net, learning_rate=0.001):
    loss = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)
    return(loss, optimizer)


def train(net, batch_size, n_epochs, learning_rate, trainCSV, valCSV, testCSV):
    
    #Print all of the hyperparameters of the training iteration:
    print("===== HYPERPARAMETERS =====")
    print("batch_size=", batch_size)
    print("epochs=", n_epochs)
    print("learning_rate=", learning_rate)
    print("=" * 30)
    
    #Get training data
    train_loader = get_loader(trainCSV, batch_size)
    validation_loader = get_loader(valCSV, 32)
    test_loader = get_loader(testCSV, 4)

    n_batches = len(train_loader)
    
    #Create our loss and optimizer functions
    loss, optimizer = createLossAndOptimizer(net, learning_rate)
    
    #Time for printing
    training_start_time = time.time()
    
    #Loop for n_epochs
    print("Starting epochs...")
    for epoch in range(n_epochs):
        print("Epoch",epoch)
        running_loss = 0.0
        print_every = n_batches // 10
        epoch_start_time = time.time()
        total_train_loss = 0
        start_time = time.time()
        
        for i, data in enumerate(train_loader, 0):
            #Get inputs
            inputs, labels, natural = data
            
            #Wrap them in a Variable object
            inputs, labels = Variable(inputs), Variable(labels)
            inputs, labels = inputs.to(device), labels.to(device)

            #Set the parameter gradients to zero
            optimizer.zero_grad()
            
            #Forward pass, backward pass, optimize
            outputs = net.forward(inputs)
            loss_size = loss(outputs, labels)
            loss_size.backward()
            optimizer.step()
            
            #Print statistics
            addedLoss = torch.Tensor.item(loss_size.data)
            running_loss += addedLoss
            total_train_loss += addedLoss
            
            #Print every 10th batch of an epoch
            if (i + 1) % (print_every + 1) == 0:
                print("Epoch {}, {:d}% \t train_loss: {:.2f} took: {:.2f}s".format(
                        epoch, int(100 * (i+1) / n_batches), running_loss / print_every, time.time() - start_time))
                #Reset running loss and time
                running_loss = 0.0
                start_time = time.time()
            
        #At the end of the epoch, do a pass on the validation set
        total_val_loss = 0
        for j, (inputs, labels, natural) in enumerate(validation_loader):
            #Wrap tensors in Variables
            inputs, labels = Variable(inputs), Variable(labels)
            inputs, labels = inputs.to(device), labels.to(device)
            
            #Forward pass
            value_outputs = net.forward(inputs)
            value_loss_size = loss(value_outputs, labels)
            if j == 0:
                print(natural)
                print(value_outputs)
                print("vs")
                print(labels)
                example_img_path = natural[0]
                example_prediction = (int(torch.IntTensor.item(value_outputs[0][0])), int(torch.IntTensor.item(value_outputs[0][1])))
                example_ground = (int(torch.IntTensor.item(labels[0][0])), int(torch.IntTensor.item(labels[0][1])))
                cv2.destroyAllWindows()
                example_img_path = os.path.abspath(os.path.join(os.sep, 'aoeai',example_img_path))
                print(example_img_path,example_prediction,example_ground)
                img = cv2.imread(example_img_path)
                window_width = int(img.shape[1])
                window_height = int(img.shape[0])
                cv2.namedWindow('dst_rt', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('dst_rt', window_width, window_height)
                cv2.circle(img, example_prediction, 10, (100,0,255), thickness=4, lineType=8, shift=0)
                cv2.circle(img, example_ground, 10, (200,100,5), thickness=4, lineType=8, shift=0)
                cv2.imshow('dst_rt', img)
                cv2.imwrite( "prediction_{0}.jpg".format(epoch), img );
                cv2.waitKey(1000)
            addedLoss = torch.Tensor.item(value_loss_size.data)
            total_val_loss += addedLoss
            
        print("Validation loss = {:.2f}".format(total_val_loss / len(validation_loader)))
        with open("valLoss",'a+') as f:
            f.write("{}:{:.2f}\n".format(epoch,total_val_loss / len(validation_loader)))
        
    print("Training finished, took {:.2f}s".format(time.time() - training_start_time))

if __name__ == "__main__":
    trainingCSV = sys.argv[1]
    valCSV = sys.argv[2]
    testCSV = sys.argv[3]
    CNN = ScoutCNN()
    CNN.to(device)
    train(CNN, batch_size=128, n_epochs=100, learning_rate=0.004, trainCSV=trainingCSV, valCSV=valCSV, testCSV=testCSV)
    torch.save(CNN.state_dict(),'training_5-13.pt')