import json
import os
import streamlit as st
import traceback

keys = [
  'final_quiz_score',
  'quiz_total_questions',
  'failed_questions',
  'highest_score',
  'messages',
  'flashcards',
]

class JSONStorage:
  def __init__(self, default=None):
    if not os.path.exists('storage.json'):
      with open('storage.json', 'w+') as f:
        f.write("{}")
    with open('storage.json', 'r') as f:
      try:
        self.storage = json.load(f)
      except json.JSONDecodeError:
        print(traceback.format_exc())
        self.storage = {}

  def get(self, key, default=None):
    return self.storage.get(key, default)

  def set(self, key, value):
    self.storage[key] = value

  def clear(self):
    self.storage.clear()

  def save(self):
    with open('storage.json', 'w') as f:
      json.dump(self.storage, f)

  def store_session_state(self, ss):
    for key in keys:
      if key in ss:
        if key == 'messages':
          if len(ss[key]) > 20:
            # Only store the 20 most recent messages to limit size
            self.storage[key] = ss[key][-20:]
          else:
            self.storage[key] = ss[key]
        else:
          self.storage[key] = ss[key]
    self.save()

  def populate_session_state(self, ss):
    for key, value in self.storage.items():
      if key in keys:
        ss[key] = value