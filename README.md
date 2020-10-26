# Browsing History Recommender module alternative training

A Python program that can improve the execution of the similarity calculation of the Browsing History Recommender module 
of Drupal (https://www.drupal.org/project/history_rec), using NumPy and pandas, for the item-to-item collaborative filter.
Only for anonymous users of the site, using the data in the accesslog table. It aims to replace the step:
drush recommender-run, to be able to work with a large amount of data. Instead of running this drush command, 
run this python program with the populated accesslog table. When the calculations are over the similarities will 
already be recorded in the database and the Views provided by the Browsing History Recommender module can now be used.

## Usage
Clone/download the repository.

```bash
pip install -r requirements.txt
```

Create a config.ini file in the format below: 

```python
[DBConnection]
host: localhost
user: user
passwd: password
db: database
```

Run:

```bash
python recommender_drupal.py
```