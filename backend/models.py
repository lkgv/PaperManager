from django.db import models
from django.contrib.auth.models import User


# user models
class Users(User):
    head_img = models.ImageField()
    # the root the classification tree
    classification_tree_root = models.ForeignKey('ClassificationTree')
    log = models.ForeignKey('Log')

    def __str__(self):
        return self.username


# user's classification tree model
class ClassificationTree(models.Model):
    name = models.CharField(max_length=256)
    father = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return self.name


# paper models
class Paper(models.Model):
    title = models.CharField(max_length=256)
    author = models.ManyToManyField('Author')
    publish_time = models.DateTimeField(auto_now_add=False)
    add_time = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    hash_code = models.CharField(max_length=64)
    classification_tree_node = models.ForeignKey(ClassificationTree)
    log = models.ManyToManyField('Log')
    notes = models.ForeignKey('Note', blank=True, null=True)

    def __str__(self):
        return self.title


# the author of the paper
class Author(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()

    def __str__(self):
        return self.first_name+' '+self.last_name


# the log of the paper
class Log(models.Model):
    log = models.CharField(max_length=1024)

    def __str__(self):
        return self.log


# the notes of a paper
class Note(models.Model):
    paper_title = models.CharField(max_length=256)
    paper_page = models.IntegerField()
    content = models.CharField(max_length=2048)

    def __str__(self):
        return self.paper_title+':'+self.paper_page
