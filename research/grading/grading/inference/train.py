
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    pear_data = pd.read_csv('./result.csv')
    features = [
        'alternaria_area', 'alternaria_count', 
        'injury_area', 'injury_count', 
        'speckle_area', 'speckle_count',
        'chemical_area', 'chemical_count', 
        'plane_area', 'plane_count'
    ]
    df = pd.DataFrame(pear_data, columns=features)
    X_train, X_test, y_train, y_test = train_test_split(df[features], pear_data['grading_id'], test_size=0.25, stratify= pear_data['grading_id'], random_state=123456)
    rf = RandomForestClassifier(n_estimators=100, oob_score=True, random_state=123456)
    rf.fit(X_train, y_train)
    predicted = rf.predict(X_test)
    accuracy = accuracy_score(y_test, predicted)
    print(f'Mean accuracy score: {accuracy:.3}')
    print(confusion_matrix(y_test, predicted))
    # cm = pd.DataFrame(confusion_matrix(y_test, predicted), columns=[1, 2, 3, 4, 5], index=[1, 2, 3, 4, 5])
    # sns.heatmap(cm, annot=True)
    # plt.savefig('filename.png', orientation = 'horizontal')

if __name__ == '__main__':
    main()