
from django.db import models


# Create your models here.
class Board(models.Model):
    b_no = models.AutoField(db_column='b_no', primary_key=True)
    b_title = models.CharField(db_column='b_title',max_length=255, blank=True, null=True)
    b_note = models.CharField(db_column='b_note',max_length=4096, blank=True, null=True)
    b_writer = models.CharField(db_column='b_writer',max_length=50, blank=True, null=True)
    # b_writer = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    parent_no = models.IntegerField(db_column='parent_no',blank=True, null=True)
    b_count = models.IntegerField(db_column='b_count',blank=True, null=True)
    b_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = True
        db_table = 'board'

    def __str__(self):
        return "제목 :" + self.b_title + ", 작성자 : " + self.b_writer