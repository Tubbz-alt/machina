from .dataset import Tabular, download
from ..types import RegressionMixin, ClassificationMixin

import os, json
import requests
import pandas as pd
import ipdb
import csv

from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer

import machina


class Airbnb(Tabular):
    '''
    Any instance attribute you add will be serialized.
    '''
    source = 'http://insideairbnb.com/index.html'
    _base_url = 'http://data.insideairbnb.com/{geography}/{date}/{filename}'
    _base_folder = '.datasets/inside_airbnb'
    
    _region_lookup = {
        'chicago': 'united-states/il/chicago',
        'columbus': 'united-states/oh/columbus',
        'denver': 'united-states/co/denver',
        'oakland': 'united-states/ca/oakland',
        'portland': 'united-states/or/portland',
        'seattle': 'united-states/wa/seattle',
        'new-york-city': 'united-states/ny/new-york-city',
        'asheville': 'united-states/nc/asheville',
        'boston': 'united-states/ma/boston',
        'los-angeles': 'united-states/ca/los-angeles'
    }

    def __init__(self, city, date, target, summary, force, features, names, seed, min_freq):
        city = city.lower()
        self._city = city
        self._date = date
        self._summary = summary
        self._seed = seed
        self._target_name = target
        self._min_freq = min_freq
    
        filename = 'visualisations/listings.csv' if summary else 'data/listings.csv.gz'
        self.url = self._base_url.format(geography=self._region_lookup[city], date=date, filename=filename)
        directory = machina.__path__[0]
        self.path = "{directory}/{base}/{city}/{date}".format(directory=directory, 
                                                              base=self._base_folder,
                                                              city=city,
                                                              date=date)

        self._filename = filename.split('/')[-1]

        if os.path.exists(f"{self.path}/processed_listings.csv") and (not force):
            self._frame = pd.read_csv(f"{self.path}/processed_listings.csv", index_col='id', low_memory=False, quoting=csv.QUOTE_ALL)
        else:
            print(f"Downloading data from {self.url}")
            self._frame = pd.read_csv(self.url, index_col='id', low_memory=False)

            if not summary:
                binary = ['host_is_superhost', 'host_has_profile_pic', 'host_identity_verified', 'requires_license', 'instant_bookable',
                          'is_business_travel_ready', 'require_guest_profile_picture', 'require_guest_phone_verification']

                money = ['price', 'security_deposit', 'cleaning_fee', 'extra_people']
                # data manipulation and attribute setting 
                for bcol in binary:
                    self._frame[bcol] = self._frame[bcol].replace('t', 1).replace('f', 0).astype(bool)
        
                for mcol in money:
                    self._frame[mcol] = self._frame[mcol].str.strip('$').str.replace(',', '').astype(float)

                tokenizer = CountVectorizer(stop_words='english').build_tokenizer()

                # feature transform
                self._frame.fillna(value={'description': ''}, inplace=True)
                self._frame['description_length'] = self._frame['description'].apply(lambda x: len(tokenizer(x)) if x else 0).astype(int)
                self._frame['host_response_rate'] = self._frame['host_response_rate'].str.replace('%', '').astype(float)
                self._frame['host_age_days'] = (datetime.strptime(date, '%Y-%m-%d') - pd.to_datetime(self._frame['host_since'])) \
                                                    .apply(lambda x: x.days)

                verifications = []
                amenities = []

                print("Converting Categorical Columns")
                for row in self._frame.copy().itertuples():
                    verifications += [ x.strip() for x in row.host_verifications.strip("[").strip("]").replace('"', '').replace("'", '').split(',') ]
                    amenities += [ x.strip() for x in row.amenities.strip("{").strip("}").replace('"', '').replace("'", '').split(',') ]
      
                verification_cols = frozenset([ v for v in verifications if (v != '') and (v != 'None')]) 
                amenity_cols = frozenset([ a for a in amenities if a != ''])

                def binarize_verify(col):
                    return lambda x: 1 if col in [ v.strip() for v in x.strip("[").strip("]").replace('"', '').replace("'", '').split(',') ] else 0

                def binarize_amenity(col):
                    return lambda x: 1 if col in [ v.strip() for v in x.strip("{").strip("}").replace('"', '').replace("'", '').split(',') ] else 0
                    
                for col in verification_cols:
                    self._frame[f"verification_{col}"] = self._frame['host_verifications'].apply(binarize_verify(col)).astype(bool)

                for col in amenity_cols:
                    self._frame[f"amenity_{col}"] = self._frame['amenities'].apply(binarize_amenity(col)).astype(bool)

                self._frame = self._frame.dropna(subset=[self._target_name])

                print("Dropping missing values")
                self._frame = self._frame.dropna(subset=['bedrooms', 'host_since', 'host_location', 'host_response_time', \
                                                         'host_response_rate', 'host_is_superhost', 'host_has_profile_pic', \
                                                          'host_identity_verified', 'bathrooms', 'beds', 'reviews_per_month', \
                                                          'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness', \
                                                          'review_scores_checkin', 'review_scores_communication', \
                                                          'review_scores_location', 'review_scores_value']) \
                                         .drop(['host_verifications', 'amenities', 'host_since'], axis=1) \
                                         .fillna(value={'description': '', 'cleaning_fee': 0.0, 'security_deposit': 0.0 })            
            
    
            if not os.path.exists(self.path):
                os.makedirs(self.path) 

            print(f"File written to {self.path}/processed_listings.csv")
            self._frame.to_csv(f"{self.path}/processed_listings.csv", quoting=csv.QUOTE_ALL, index=True)

        self._features = features.copy() if features else self._frame.columns.tolist().copy() 

        if features:
            # do for both new and cached dataets
            if 'host_verifications' in self._features:
                for col in self._frame.columns[self._frame.columns.str.startswith('verification_')]:
                    if (self._frame[col].sum() / len(self._frame[col])) >= self._min_freq:
                        self._features.append(col)

                self._features.remove('host_verifications')

            if 'amenities' in self._features:
                for col in self._frame.columns[self._frame.columns.str.startswith('amenity_')]:
                    if (self._frame[col].sum() / len(self._frame[col])) >= self._min_freq:
                        self._features.append(col)

                self._features.remove('amenities')

        self._target = self._frame.loc[:, self._target_name]
        self._data = self._frame.loc[:, self._features]

        old_cols = self._data.columns.copy()
        new_cols = []   

        for col in old_cols:
            if col.startswith('amenity_'):
                amenity = col[len('amenity_'):].replace('_', ' ').title()
                new_cols.append(f"Amenity: {amenity}")
            elif col.startswith('verification_'):
                verification = col[len('verification_'):].replace('_', ' ').title()
                new_cols.append(f"Host Verification: {verification}")
            elif names:
                new_cols.append(names[col] if col in names else col)
            else:
                new_cols.append(col)

        self._data.columns = new_cols
    
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, df):
        self._data = df

    @property
    def feature_names(self):
        return self._data.columns

    @property
    def target(self):
        return self._target

    @property
    def target_names(self):
        return self._target_name

    @property
    def _built(self):
        return os.path.exists(f"{self.path}/{self._filename}")
                        
    def build(self):
        dirs = os.path.dirname(self.path)

        print(f"downloading data to {dirs}")
        if not os.path.exists(dirs):
            os.makedirs(dirs) 

        download([self.url], dirs)

    def serialize(self, filename):
        output = {
            'source': self.source,
            'url': self.url,
            'city': self._city,
            'date': self._date,
            'summary': self._summary,
            'seed': self._seed,
        }

        output['_data'] = self._frame.to_dict()
        output['_target'] = {
            str(self._target_name): self._target.to_dict()
        }

        with open(filename, 'w') as fh:
            json.dump(output, fh, ensure_ascii=False)

class AirbnbRegressor(Airbnb, RegressionMixin):
    def __init__(self, city, date, summary=False, force=False, features=None, names=None, seed=18, min_freq=0.0):
        super(AirbnbRegressor, self).__init__(target='price', city=city, date=date, summary=summary, force=force, features=features, names=names, seed=seed, min_freq=min_freq)

class AirbnbClassifier(Airbnb, ClassificationMixin):
    def __init__(self, city, date, summary=False, force=False, features=None, names=None, seed=18):
        super(AirbnbClassifier, self).__init__(target='host_is_superhost', city=city, date=date, summary=summary, force=force, features=features, names=names, seed=seed)