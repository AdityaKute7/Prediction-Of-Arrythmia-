import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples to generate
num_samples = 1000

# Function to simulate a normal ECG signal
def generate_normal_ecg():
    rr_interval = np.random.normal(0.8, 0.05)  # Normal RR interval (0.6 to 1.0 seconds)
    p_wave = np.random.normal(0.1, 0.02)  # Normal P wave duration
    qrs_complex = np.random.normal(0.12, 0.02)  # Normal QRS complex duration
    t_wave = np.random.normal(0.16, 0.03)  # Normal T wave duration
    qt_interval = rr_interval / 2  # QT interval (approx. half of the RR interval)
    return [rr_interval, p_wave, qrs_complex, t_wave, qt_interval]

# Function to simulate an arrhythmic ECG signal
def generate_arrhythmic_ecg():
    rr_interval = np.random.normal(0.5, 0.15)  # Irregular RR interval
    p_wave = np.random.normal(0.1, 0.03)  # Abnormal P wave
    qrs_complex = np.random.normal(0.14, 0.03)  # Prolonged QRS complex
    t_wave = np.random.normal(0.18, 0.04)  # Abnormal T wave
    qt_interval = rr_interval / 1.5  # Prolonged QT interval
    return [rr_interval, p_wave, qrs_complex, t_wave, qt_interval]

# Generate dataset
data = []
labels = []

for _ in range(num_samples):
    if np.random.rand() > 0.5:
        # Generate a normal ECG signal
        data.append(generate_normal_ecg())
        labels.append('Normal')
    else:
        # Generate an arrhythmic ECG signal
        data.append(generate_arrhythmic_ecg())
        labels.append('Arrhythmia')

# Convert to pandas DataFrame
columns = ['RR_interval', 'P_wave', 'QRS_complex', 'T_wave', 'QT_interval']
df = pd.DataFrame(data, columns=columns)
df['Label'] = labels

# Save the dataset to a CSV file
df.to_csv('synthetic_ecg_dataset.csv', index=False)

# Display the first few rows of the dataset
df.head()
