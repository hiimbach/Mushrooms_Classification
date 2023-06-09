import os 
import torch

from torch.utils.data import Dataset
from PIL import Image, ImageFile
from sklearn.model_selection import train_test_split

# Avoid image truncates
ImageFile.LOAD_TRUNCATED_IMAGES = True

def data_split(dir, split_ratio=0.8):
    '''
    Used to split data to train_data, split_data and a list of class_names
    
    Parameters:
        dir: data directory, format as:
            0/a.jpg
            1/b.jpg
            ...
        batch_size (int)
        split_ratio: the ratio of train_data/all_data
    
    Return:
        train_data (dict): {'img_path': [], 'label': []}
        val_data (dict): {'img_path': [], 'label': []}
        class_names (list)
    '''
    
    # This variable is used to store all data read
    data = {}
    class_names = []
    class_idx = -1
    
    # First read all data from the dir
    # Each folder represents for a class
    for folder in os.listdir(dir):
        folder_path = os.path.join(dir, folder)
        class_names.append(folder)
        class_idx += 1
        
        data[folder] = {'img_path': [], 'label': []}
        data_folder = data[folder]
        
        for item in os.listdir(folder_path):
            img_path = os.path.join(folder_path, item)

            # In each folder in the data dictionary, we append img and corresponding label in 2 list
            data_folder['img_path'].append(img_path)
            data_folder['label'].append(class_idx)
            
    # Create train dict and val dict to split data
    train_data = {'img_path': [], 'label': []}
    val_data = {'img_path': [], 'label': []}

    # Split data to train and val
    for folder in data:
        data_folder = data[folder]
        
        # Choose img and corresponding label randomly
        idx = range(len(data_folder['label']))
        train_idx, test_idx = train_test_split(idx, test_size=(1-split_ratio))
        for i in train_idx:
            train_data['img_path'].append(data_folder['img_path'][i])
            train_data['label'].append(data_folder['label'][i])
            
        for i in test_idx:
            val_data['img_path'].append(data_folder['img_path'][i])
            val_data['label'].append(data_folder['label'][i])
    
    return train_data, val_data, class_names

class CustomDataset(Dataset):
    def __init__(self, data, transform=None):
        '''
        Custom torch.utils.data.Dataset from data generated by fn data_split above
        
        Arguments:
            data (dict): {'img_path': [], 'label': []}
            transform: torchvision.transforms
        '''
        self.data = data
        self.transform = transform
        
    def __getitem__(self, idx):
        label = self.data['label'][idx]
        image = Image.open(self.data['img_path'][idx]).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, label
        
    def __len__(self):
        return len(self.data['label'])
    


def filenames_to_tensor(files, transform):
    '''
    Parameters:
        files (list): list of file name (str)
        transform (torchvision.transforms.transforms.Compose): requires to transform to Tensor after augment
        
    Return:
        img_batch (torch.Tensor)    
    '''
    
    # This list is used to store all tensor and concat at the end
    tensor_list = []
    
    # Read all files and transform it to tensor
    for img_path in files:
        img = Image.open(img_path)
        # Unsqueeze is used to expand dim to concat later
        tensor_list.append(torch.unsqueeze(transform(img), dim=0))
        
    return torch.cat(tensor_list)


def custom_loader(data, batch_size):
    # Use to split data to batches when inferencing
    '''
    Argument: 
        data (list): list of images' paths
        
    Return:
        data_loader: list(list)
    '''
    
    data_loader = []
    data_len = len(data)
    
    i = 0
    while (i+batch_size) < data_len:
        img_batch = data[i:i+batch_size]
        
        data_loader.append(img_batch)
        
        i += batch_size
        
    # Because there is some little data left which is not enough to create a full batch,
    # we group it to the final batch 
    img_batch = data[i:]
    
    data_loader.append(img_batch)
    
    return data_loader


def read_file_classnames(path):
    '''
    Arguments:
        path (str): Path to file contains class names
        
    Return: 
        class_names (list): List of class names
    '''
    
    with open(path) as f:
        all_names = f.readline()
        
    class_names = [name.strip() for name in all_names.split(',')]
    
    return class_names
    
    
def write_file_classnames(class_names, save_name, save_path=''):
    '''
    Write a file contains names of classes, split by a ,
    
    Arguments:
        class_names (list(str)): List of class names
        save_path (str or os.path): Path of folder to save at
        save_name (str): Name of saved file
    '''
    
    save_info = ','.join(class_names)
    save_addr = os.path.join(save_path, f"{save_name}.txt")
    with open(save_addr, "w") as f:
        f.write(save_info)
        
    return 