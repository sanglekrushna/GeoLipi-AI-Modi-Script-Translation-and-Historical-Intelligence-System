import os
import json
import torch
import numpy as np
import cv2
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

class OCRVocabulary:
    def __init__(self, chars_list):
        self.char_to_id = {char: i + 1 for i, char in enumerate(chars_list)}
        self.id_to_char = {i + 1: char for i, char in enumerate(chars_list)}
        self.char_to_id['<blank>'] = 0
        self.id_to_char[0] = ''

    def encode(self, text):
        return [self.char_to_id[c] for c in text if c in self.char_to_id]

    def decode(self, ids):
        return "".join([self.id_to_char[i] for i in ids if i in self.id_to_char])

    def __len__(self):
        return len(self.id_to_char)

class CRNNOCRDataset(Dataset):
    def __init__(self, data_dir, labels_dict, vocab, target_height=64, target_width=512):
        self.data_dir = data_dir
        self.filenames = list(labels_dict.keys())
        self.labels = list(labels_dict.values())
        self.vocab = vocab
        self.target_height = target_height
        self.target_width = target_width

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        img_path = os.path.join(self.data_dir, self.filenames[idx])
        img = Image.open(img_path).convert('L')
        
        # Aspect-ratio preserving resize and pad
        w, h = img.size
        ratio = w / h
        new_w = int(self.target_height * ratio)
        new_w = min(new_w, self.target_width)
        
        img = img.resize((new_w, self.target_height), Image.Resampling.LANCZOS)
        
        # Pad to target_width
        padded_img = Image.new('L', (self.target_width, self.target_height), 255)
        padded_img.paste(img, (0, 0))
        
        img_tensor = np.array(padded_img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_tensor).unsqueeze(0)  # [1, H, W]
        
        label_text = self.labels[idx]
        label_ids = self.vocab.encode(label_text)
        
        return img_tensor, torch.LongTensor(label_ids)

def crnn_collate_fn(batch):
    images, labels = zip(*batch)
    images = torch.stack(images, 0)
    
    label_lengths = torch.LongTensor([len(l) for l in labels])
    labels_padded = pad_sequence(labels, batch_first=True, padding_value=0)
    
    return images, labels_padded, label_lengths

def create_crnn_dataloaders(data_dir, labels_json, vocab, batch_size=32):
    with open(labels_json, encoding='utf-8') as f:
        labels_dict = json.load(f)
    
    dataset = CRNNOCRDataset(data_dir, labels_dict, vocab)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=crnn_collate_fn)
