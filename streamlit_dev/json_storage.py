import json
import os
import streamlit as st

keys = [
  'final_quiz_score',
  'quiz_total_questions',
  'failed_questions',
  'highest_score',
  'messages',
]

class JSONStorage:
  def __init__(self, default=None):
    with open('storage.json', 'a+') as f:
      try:
        self.storage = json.load(f)
      except json.JSONDecodeError:
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
        self.storage[key] = ss[key]
    self.save()

  def populate_session_state(self, ss):
    for key, value in self.storage.items():
      if key in keys:
        ss[key] = value