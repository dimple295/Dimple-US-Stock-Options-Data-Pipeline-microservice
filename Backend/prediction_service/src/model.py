import torch
import torch.nn as nn

class TransformerLSTM(nn.Module):
    def __init__(self, num_features, lstm_hidden_size=128, num_heads=4, num_transformer_layers=2, forecast_horizon=240, num_stocks=120):
        super(TransformerLSTM, self).__init__()
        self.lstm = nn.LSTM(num_features, lstm_hidden_size, num_layers=2, batch_first=True, dropout=0.2)
        self.pos_encoder = nn.Parameter(torch.randn(1, 120, lstm_hidden_size))
        encoder_layer = nn.TransformerEncoderLayer(d_model=lstm_hidden_size, nhead=num_heads, batch_first=True, dropout=0.2)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_transformer_layers)
        self.fc = nn.Linear(lstm_hidden_size, num_stocks * forecast_horizon)
        self.forecast_horizon = forecast_horizon
        self.num_stocks = num_stocks

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        lstm_out = lstm_out + self.pos_encoder
        transformer_out = self.transformer_encoder(lstm_out)
        out = self.fc(transformer_out[:, -1, :])
        out = out.view(-1, self.forecast_horizon, self.num_stocks)
        return out