
import tensorflow as tf
from tensorflow.keras import layers
import mlflow.tensorflow

def build_model():
    model = tf.keras.Sequential([
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy')
    return model

if __name__ == "__main__":
    mlflow.tensorflow.autolog() # 🔥 Auto-track TF experiments
    model = build_model()
    print("🧠 TensorFlow Model built and MLflow autologging enabled.")
