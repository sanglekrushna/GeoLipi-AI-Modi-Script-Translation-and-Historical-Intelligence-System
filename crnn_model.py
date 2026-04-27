import torch
import torch.nn as nn
import torch.nn.functional as F

class CRNN(nn.Module):
    """
    CRNN for OCR:
    CNN backbone -> sequence reshape -> 2-layer BiLSTM -> linear
    """
    def __init__(self, vocab_size, hidden_size=256):
        super(CRNN, self).__init__()
        
        # 1) CNN Backbone optimized for 64xW input
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1)),  # 64xW -> 32xW
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)),  # 32xW -> 16xW/2
            
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)),  # 16xW/2 -> 8xW/4
            
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1)),  # 8xW/4 -> 4xW/4
            
            nn.Conv2d(512, 512, kernel_size=2, stride=1, padding=0),  # 4xW/4 -> 3xW/4-1
            nn.ReLU(inplace=True)
        )
        
        # 2) Sequence Modeling (BiLSTM)
        self.rnn = nn.LSTM(512, hidden_size, bidirectional=True, num_layers=2, batch_first=False)
        
        # 3) Output Layer
        self.fc = nn.Linear(hidden_size * 2, vocab_size)

    def forward(self, x):
        # x: [B, 1, 64, W]
        conv = self.cnn(x)
        # conv: [B, 512, 1, T] -> because of vertical pooling and kernel size
        b, c, h, w = conv.size()
        assert h == 1, "Height must be reduced to 1 by CNN"
        
        conv = conv.squeeze(2)  # [B, 512, T]
        conv = conv.permute(2, 0, 1)  # [T, B, 512] (Standard for RNNs)
        
        output, _ = self.rnn(conv)
        T, B, H = output.size()
        
        logits = self.fc(output.view(T * B, H))
        logits = logits.view(T, B, -1)
        
        return F.log_softmax(logits, dim=2)

    def compute_ctc_loss(self, logits, targets, input_lengths, target_lengths):
        """
        Standard CTC loss for OCR.
        """
        loss_fn = nn.CTCLoss(blank=0, reduction='mean', zero_infinity=True)
        return loss_fn(logits, targets, input_lengths, target_lengths)
