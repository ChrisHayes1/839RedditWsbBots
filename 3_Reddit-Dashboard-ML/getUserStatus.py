"""Create a end point for boot identification solution."""
import os
from flask import Flask, request
from flask_restful import reqparse, Api, Resource
import pickle
from model import RFModel

application = Flask(__name__)
api = Api(application)

model = RFModel()

clf_path = 'lib/models/DecisionTreeClassifier.pkl'
with open(clf_path, 'rb') as f:
    model.clf = pickle.load(f)

clean_data_path = 'lib/models/CleanData.pkl'
with open(clean_data_path, 'rb') as f:
    model.vectorizer = pickle.load(f)

class Botidentification():
    """Class for add end points."""


    def get_user_status(self, user_json):
        """HTTP POST /.

        Boot identification solution end point.

        Returns
        -------
        Return if the JSON Data is about a Normal user, Bot or a Troll.

        """
        #application.logger.info("Received request")
        #print(f"user jason = {user_json}")
        #clean_data = model.clean_data(user_json)
        #application.logger.info("Cleaned data: " + str(clean_data))
        
        #print(f"data: {(user_json)}")
        prediction = model.predict(user_json)
        
        #print(f"pred: {prediction} \n {user_json['author', 'recent_avg_diff_ratio', 'author_verified', 'recent_max_diff_ratio']}")

        #print(prediction)
        # Return the prediction
        if prediction == 'normal':
            pred_text = 'normal user'
        elif prediction == 'bot':
            pred_text = 'possible bot'
        elif prediction == 'troll':
            pred_text = 'possible troll'
        else:
            pred_text = 'Classification error'

        output = {'prediction': pred_text}
        #print(f"pred: {pred_text}")
        #application.logger.info(output)
        return pred_text

# Setup the Api resource routing here
# Route the URL to the resource

# api.add_resource(Botidentification, '/')

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 8000))
#     application.run(debug=True, host='0.0.0.0', port=port)
