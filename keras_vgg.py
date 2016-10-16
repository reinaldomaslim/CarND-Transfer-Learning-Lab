from keras.applications.vgg19 import VGG19
from keras.layers import Dense, GlobalAveragePooling2D, Input, Dropout
from sklearn.model_selection import train_test_split
from keras.models import Model
import tensorflow as tf
import pickle

nb_classes = 43
batch_size = 128
nb_epoch = 20

with open('./data/train.p', mode='rb') as f:
    train = pickle.load(f)
with open('./data/test.p', mode='rb') as f:
    test = pickle.load(f)

X_train, X_val, y_train, y_val = train_test_split(
    train['features'],
    train['labels'],
    test_size=0.33,
    random_state=0)
X_test, y_test = test['features'], test['labels']

X_train = X_train.astype('float32')
X_val = X_val.astype('float32')
X_test = X_test.astype('float32')

# 0-255 -> 0-1
X_train /= 255
X_val /= 255
X_test /= 255

# https://www.tensorflow.org/versions/r0.11/api_docs/python/image.html#images
# For ways to preprocess images
images = Input(shape=(32, 32, 3))
resized_images = tf.image.resize_images(images, (224, 224))

base_model = VGG19(input_tensor=images, include_top=False, weights='imagenet')

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.8)(x)
predictions = Dense(nb_classes, activation='softmax')(x)

model = Model(input=base_model.input, output=predictions)

# freeze base model layers
for layer in base_model.layers:
    layer.trainable = False


model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'])

model.fit(
    X_train,
    y_train,
    verbose=1,
    batch_size=batch_size,
    nb_epoch=nb_epoch,
    validation_data=(X_val, y_val))

_, acc = model.evaluate(X_test, y_test, verbose=0)
print("Testing accuracy =", acc)
