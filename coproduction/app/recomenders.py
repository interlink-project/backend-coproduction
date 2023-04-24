import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer


def recomender_type_governance(TrainingData, SampleData):
    #print("Entra en el recomendador de tipo de gobierno")
  
    X_train_data=[]
    y_train_data=[]
    for x, y in TrainingData[0].items():
        X_train_data.append(x)
        y_train_data.append(y.split(','))

     

    #print('The x train data is:', X_train_data)
    #print('The y train data is:', y_train_data)
    


    # Define the input data
    X_train = np.array(X_train_data)
    # X_train = np.array(["new york is a hell of a town",
    #                     "new york was originally dutch",
    #                     "the big apple is great",
    #                     "new york is also called the big apple",
    #                     "nyc is nice",
    #                     "people abbreviate new york city as nyc",
    #                     "the capital of great britain is london",
    #                     "london is in the uk",
    #                     "london is in england",
    #                     "london is in great britain",
    #                     "it rains a lot in london",
    #                     "london hosts the british museum",
    #                     "new york is great and so is london",
    #                     "i like london better than new york"])
    y_train_text = y_train_data
    # y_train_text = [["new york"],["new york"],["new york"],["new york"],["new york"],
    #                 ["new york"],["london"],["london"],["london"],["london"],
    #                 ["london"],["london"],["new york","london"],["new york","london"]]
    #print('the sample data is:')
    #print(' '.join(SampleData))

    X_test = np.array([' '.join(SampleData)])

    # X_test = np.array(['nice day in nyc',
    #                 'welcome to london',
    #                 'london is rainy',
    #                 'it is raining in britian',
    #                 'it is raining in britian and the big apple',
    #                 'it is raining in britian and nyc',
    #                 'hello welcome to new york. enjoy it here and london too'])
    
    #Obtain the unique values:

    flat_list = [item for sublist in y_train_data for item in sublist]
    set_res = set(flat_list) 
    target_names=(list(set_res))

    #print('The target names are:', target_names)
    
    #target_names = ['New York', 'London']

    # Preprocess the input data
    Y, target_labels, mlb = preprocess_text(X_train, y_train_text, X_test,target_names)

    # Train the classifier
    classifier = train_classifier(X_train, Y)

    # Predict the labels for the test data
    all_labels = predict_labels(classifier, X_test, mlb)

    # #print the predicted labels
    # for item, labels in zip(X_test, all_labels):
    #     print('{0} => {1}'.format(item, ', '.join(labels)))
    
    return all_labels[0]


    
   



def preprocess_text(X_train, y_train_text, X_test,target_names):
    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(y_train_text)
    return Y, mlb.transform(target_names), mlb

def train_classifier(X_train, Y):
    classifier = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', OneVsRestClassifier(LinearSVC()))])
    classifier.fit(X_train, Y)
    return classifier

def predict_labels(classifier, X_test, mlb):
    predicted = classifier.predict(X_test)
    all_labels = mlb.inverse_transform(predicted)
    return all_labels


