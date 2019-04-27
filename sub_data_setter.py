import numpy as np
import pandas as pd
from PIL import Image
from torch.utils.data.dataset import Dataset
from torchvision import transforms

# MAN_AT_ARMS = 
# PIKEMAN = 
# SKIRMISHER = 
SCOUT_B3 = 396565680
# KNIGHT = 

class UnitData(Dataset):
    def __init__(self, csv_path):
        '''
        Args:
            csv_path (string): path to csv file
            img_path (string): path for image directory
        Where the initial logic is defined like reading a csv, assigning transforms etc.
        '''
        self.resize_64 = transforms.Resize(size=64)
        self.to_tensor = transforms.ToTensor()
        self.normalize_rgb = transforms.Normalize(mean=([0.5]*3),std=([0.5]*3))
        self.grayscale = torchvision.transforms.Grayscale()
        self.apply_transformations = transforms.Compose([resize_64, to_tensor, normalize_rgb, grayscale])
        self.data_reference = pd.read_csv(csv_path, header=None)
        self.image_arr = np.asarray(self.data_reference.iloc[:,0])
        self.x_label_arr = np.asarray(self.data_reference.iloc[:,1])
        self.y_label_arr = np.asarray(self.data_reference.iloc[:,2])
        self.selected_arr = np.asarray(self.data_reference.iloc[:,3])
        # One-hot unit selected.
        # self.man_at_arms_arr = np.asarray(self.data_reference.iloc[:,3])
        # self.pikeman_arr = np.asarray(self.data_reference.iloc[:,4])
        # self.skirmisher_arr = np.asarray(self.data_reference.iloc[:,5])
        # self.scout_arr = np.asarray(self.data_reference.iloc[:,6])
        # self.knight_arr = np.asarray(self.data_reference.iloc[:,7])



        self.data_len = len(self.data_reference.index)
        
    def __getitem__(self, index):
        '''
        Returns the data and labels. This function is called from dataloader like this
        img, label = MyCustomDataset.__getitem__(99)  # For 99th item
        The index parameter is the nth data/image (as tensor) to return.
        '''
        image_name  = self.image_arr[index]
        image = Image.open(image_name)
        # One-hot unit selected.
        # man_at_arms = self.man_at_arms_arr[index]
        # pikeman = self.pikeman_arr[index]
        # skirmisher = self.skirmisher_arr[index]
        # scout = self.scout_arr[index]
        # knight = self.knight_arr[index]
        selected = self.selected_arr[index]
        scout_selected = if selected == SCOUT_B3 then 1 else 0

        x = self.x_label_arr[index]
        y = self.y_label_arr[index]
        image_tensor = self.apply_transformations(image)
        return (image_tensor, [x,y])

    def __len__(self):
        '''
        Returns count of samples.
        '''
        return self.data_len

if __name__ = '__main__':
    unit_trials_1 = UnitClickData('../data/units_selected_batch1.csv')
    u1_loader = torch.utils.data.DataLoader(dataset=unit_trials_1, batch_size=4, shuffle=True)

    for images, labels in u1_loader:
        pass