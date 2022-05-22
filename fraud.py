from traceback import print_tb
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import pickle
from sklearn.metrics import plot_confusion_matrix
from matplotlib import pyplot as plt
transaction_data = pd.read_csv('./transaction_dataset.csv')
print(transaction_data.keys())
labels = transaction_data['FLAG']
features = ['Sent tnx',\
    'Received Tnx',\
    'min value received',\
    'max value received ',\
    'avg val received',\
    'min val sent',\
    'max val sent',\
    'avg val sent',\
    'total Ether sent',\
    'total ether received',\
    'total ether balance'
    ]
data = ['FLAG',\
    'Sent tnx',\
    'Received Tnx',\
    'min value received',\
    'max value received ',\
    'avg val received',\
    'min val sent',\
    'max val sent',\
    'avg val sent',\
    'total Ether sent',\
    'total ether received',\
    'total ether balance'
    ]
transaction_data = transaction_data[data]


transaction_data = transaction_data.sample(frac=1).reset_index(drop=True)

train, test = train_test_split(transaction_data, test_size=0.2)

train_targets = train['FLAG'].to_numpy()
train_features = train[features].to_numpy()


from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=42)
train_features, train_targets = sm.fit_resample(train_features, train_targets)
test_targets = test['FLAG'].to_numpy()
test_features = test[features].to_numpy()


train_features = preprocessing.normalize(train_features, norm='l2')
test_features = preprocessing.normalize(test_features, norm='l2')
clf = LogisticRegression(random_state=0).fit(train_features, train_targets)
print(clf.score(test_features, test_targets))

y = clf.predict(test_features)
y_true = test_targets

plot_confusion_matrix(clf, test_features, y_true)
plt.show()
#for x, y in zip(test_features, test_targets):
#    print(x, y)
with open('model.pkl','wb') as f:
    pickle.dump(clf,f)