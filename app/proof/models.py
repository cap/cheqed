from django.db import models

class Plan(models.Model):
    text = models.TextField()

class Proof(models.Model):
    plan = models.ForeignKey(Plan)
    goal = models.TextField()

class Definition(models.Model):
    text = models.TextField()
