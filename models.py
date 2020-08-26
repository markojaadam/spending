# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Currency(models.Model):
    pkey_id = models.SmallIntegerField(primary_key=True)
    currency = models.CharField(max_length=256)
    code = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'currency'
        app_label = 'spending'


class Spending(models.Model):
    pkey_id = models.BigAutoField(primary_key=True)
    amount = models.BigIntegerField()
    fkey_currency = models.ForeignKey(Currency, models.DO_NOTHING, db_column='fkey_currency')
    reason = models.CharField(max_length=2048, blank=True, null=True)
    date = models.BigIntegerField()  # map oid (uint32) as bigint
    timestamp = models.BigIntegerField()  # map oid (uint32) as bigint

    class Meta:
        managed = False
        db_table = 'spending'
        app_label = 'spending'
