import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from IPython import get_ipython
import collections
from datetime import datetime
import numpy as np
from model import RFModel


with open('../Data/TrainingData/TrollsBots/cleaned/TrollBot_ReadyForTraining.csv') as f:
    my_data_training = pd.read_csv(f, sep=',')
print("Clean Dataset Shape for Trolls and Bots: ", my_data_training.shape)

with open('../Data/TrainingData/NormieData/cleaned/NormieData_ReadyForTraining_small.csv') as f:
    my_data_normies = pd.read_csv(f, sep=',')
print("Clean Dataset Shape for Normies: ", my_data_normies.shape)
#my_data_normies['target'] = 'normal'

my_data = my_data_training.append(my_data_normies)
print("Clean Dataset Shape Combined: ", my_data.shape)


# drop duplicates
print(f"Start: {len(my_data)}")
my_data = my_data.drop_duplicates(subset=['author','link_id','created_utc'])
print(f"After drop_dups: {len(my_data)}")

# correct labeling
my_data.loc[my_data.author == 'PoliticsModeratorBot','target'] = 'bot'

# Label known bot in normies
bot_authors = my_data[my_data.target == 'bot'].author.unique()

print(f"Length of bot_authors = {len(bot_authors)}")
count_normal = len(my_data[(my_data.target == 'normal')])
count_bot = len(my_data[(my_data.target == 'bot')])
print(f'Pre, normal count = {count_normal} and bot = {count_bot}')

#Should adjust known bots but seems to be adjusting most normal?
my_data.loc[((my_data.target == 'normal') & (my_data.author.isin(bot_authors))),'target'] = 'bot'

count_normal = len(my_data.loc[(my_data.target == 'normal')])
count_bot = len(my_data.loc[(my_data.target == 'bot')])
print(f'After, normal count = {count_normal} and bot = {count_bot}')

# Delete irrelevant columns
columns = ['link_id', 'author', 'created_utc', 'body', 'no_follow', 'over_18', 'is_submitter', 'recent_avg_no_follow']
my_data.drop(columns, inplace=True, axis=1)
print("After removing columns not considered: ", my_data.shape)

my_data[my_data['target']=='normal'].describe()
my_data[my_data['target']=='bot'].describe()
my_data[my_data['target']=='troll'].describe()

# Set fractions between the user classes
#print("\nFixing ratios between classes")
#dataset = my_data[my_data.target==2]
#dataset = dataset.append(my_data[my_data.target==1].sample(n=len(dataset)*2))
#dataset = dataset.append(my_data[my_data.target==0])
#my_data = dataset

# Number of targets
targets = collections.Counter(my_data['target'])
print(targets)

# Extract feature and target np arrays (inputs for placeholders)
input_y = my_data['target'].values
input_x = my_data.drop(['target'], axis=1)

print(f"Len of input x = {len(input_x)}")
print(f"Len of input y = {len(input_y)}")
input_x.fillna(0, inplace=True)
# Splitting the dataset into the Training set and Test set
X_train, X_test, y_train, y_test = train_test_split(
            input_x, input_y,
            test_size=0.3, random_state=16)

#print(f"type: {type(X_train)}")
#print(f"print: {X_train}")
#X_train.to_csv("lib/data/X_train.csv")
#print(f"print: {y_train}")
#f= open("lib/data/y_train.csv", "w+")
#content = str(y_train)    
#for row in y_train:
    #print(f"Row = {row}")
#    f.write(f"{row}\n")

#print(f"content = {content}")
f.close()

#y_train.to_csv("lib/data/Y_train.csv")
# Create a Decision Tree Classifier
clf = DecisionTreeClassifier(max_depth=3,
                             class_weight={'normal':1, 'bot':2.5, 'troll':5},
                             min_samples_leaf=100)

# Added by todd

#print(f"type: {type(X_train)}")

#print(f"type: {type(y_train)}")
#y_train = y_train.fillna(0)
#print(y_train.isnan(np.NaN))
# Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(X_train, y_train)

# prediction on test set
print(f"Data:\n{X_test}")

y_pred = clf.predict(X_test)

# Model Accuracy, how often is the classifier correct?
y_true = y_test

matrix = pd.crosstab(y_true, y_pred, rownames=['True'],
                     colnames=['Predicted'], margins=True)
print(matrix)
print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
print("Mcc:", metrics.matthews_corrcoef(y_test, y_pred))
print("F1 :", metrics.f1_score(y_test, y_pred, average=None))
print("Recall :", metrics.recall_score(y_test, y_pred, average=None))
print("Precision:", metrics.precision_score(y_test, y_pred, average=None))

feature_imp = pd.Series(
        clf.feature_importances_,
        index=my_data.columns.drop('target')).sort_values(ascending=False)
print(feature_imp)

# prediction on training set
y_pred = clf.predict(X_train)

# Model Accuracy, how often is the classifier correct?
y_true = y_train

matrix = pd.crosstab(y_true, y_pred, rownames=['True'],
                     colnames=['Predicted'], margins=True)
print(matrix)

estimator = clf

from sklearn.tree import export_graphviz
# Export as dot file
export_graphviz(estimator, out_file='tree.dot',
                feature_names = my_data.drop(['target'], axis=1).columns.values,
                class_names = np.array(['bot','normal','troll']),
                rounded = False, proportion = False,
                precision = 5, filled = True)

# Convert to png using system command (requires Graphviz)
from subprocess import call
call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])

# Display in jupyter notebook
from IPython.display import Image
Image(filename = 'tree.png')

# Build the model and pickle it for use by the API
model = RFModel()

# Create a Gaussian Classifier
model.create(3)

# Train the model using the training sets y_pred=clf.predict(X_test)
model.train(X_train, y_train)
y_pred = model.predict(X_test)
y_true = y_test
matrix = pd.crosstab(y_true, y_pred, rownames=['True'],
                     colnames=['Predicted'], margins=True)
print(matrix)
print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
print("Mcc:", metrics.matthews_corrcoef(y_test, y_pred))
print("F1 :", metrics.f1_score(y_test, y_pred, average=None))
print("Recall :", metrics.recall_score(y_test, y_pred, average=None))
print("Precision:", metrics.precision_score(y_test, y_pred, average=None))

feature_imp = pd.Series(
        model.feature_importances(),
        index=my_data.columns.drop('target')).sort_values(ascending=False)
feature_imp

model.pickle_clf()
model.pickle_clean_data()

# Plot number of targets
from IPython import get_ipython
import matplotlib.pyplot as plt

ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')

    # Creating a bar plot
    sns.set(style="darkgrid")
    sns.countplot(x="target", data=my_data)

    # Add labels to your graph
    plt.xlabel('Target Score')
    plt.ylabel('Targets')
    plt.title("Targets Distribution")
    plt.show()

# Visualize the feature importance
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')

    # Creating a bar plot
    sns.barplot(x=feature_imp, y=feature_imp.index)

    # Add labels to your graph
    plt.xlabel('Feature Importance Score')
    plt.ylabel('Features')
    plt.title("Visualizing Important Features")
    plt.show()

