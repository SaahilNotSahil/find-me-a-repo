import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class Model:
  def __init__(self, jsonData):
    self.user_text = jsonData['desc']
    self.user_language_input = jsonData['pl']
    self.user_input = self.user_text + " " + self.user_language_input

  def combined_features(self, row):
      return row['Repository Name']+" "+row['Language']+" "+row['Tags']+row['Description']

  def createData(self):
    data = pd.read_csv("https://query.data.world/s/zxtxz5ro2skvafkuaycnh74g5ppp2g")

    data = data.drop(["Last Update Date", "Number of Stars"], axis=1)

    data["Tags"] = data["Tags"].replace(',', ' ', regex=True)
    data["Description"] = data["Description"].replace(',', ' ', regex=True)

    data = data.fillna(" ")

    data["combined_features"] = data.apply(self.combined_features, axis=1)

    self.data = data

    self.user_series = pd.Series([self.user_input])
    self.data_with_User = data["combined_features"].append(
        self.user_series, ignore_index=True)

  def createModel(self):
    cv = TfidfVectorizer()
    count_matrix = cv.fit_transform(self.data_with_User.values.astype('U'))
    self.cosine_sim = cosine_similarity(count_matrix)
    self.data["index"] = pd.DataFrame([i for i in range(980)])
    self.user_repo_index = 980

  def flatten(self, t):
      return [item for sublist in t for item in sublist]

  def get_title_from_index(self, index):
      if len(self.data[self.data["index"] == index]["index"]) != 0:
          return self.data[self.data["index"] == index]["index"].values.tolist()

  def find_similar_repos(self, user_repo_index):
      similar = list(enumerate(self.cosine_sim[user_repo_index]))
      sorted_similar = sorted(similar, key=lambda x: x[1], reverse=True)

      test_list = []
      for i in range(len(sorted_similar)):
          test_list.append(self.get_title_from_index(sorted_similar[i][0]))

      res = []
      for val in test_list:
          if val is not None:
              res.append(val)

      res = self.flatten(res)
      
      return res[:15]

  def recommend(self):
    self.find_similar_repos(self.user_repo_index)

    df = pd.DataFrame(columns=["Username", "Repository Name",
                      "Description", "Language", "Tags", "Url"])

    for i in self.find_similar_repos(self.user_repo_index):
        df = pd.DataFrame(df)
        df.loc[len(df.index)] = self.data.iloc[i, :6]

        result = df.to_json(orient="records")
        parsed = json.loads(result)

    return json.dumps(parsed, indent=4)
