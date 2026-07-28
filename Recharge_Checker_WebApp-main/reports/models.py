from django.db import models


class Renewal(models.Model):
    """One matched churn->renewal recharge record. The whole table is
    replaced every time someone uploads a fresh pair of CSVs, so it always
    reflects the latest processed report — for everyone."""
    customer_id = models.CharField(max_length=100, blank=True)
    customer_name = models.CharField(max_length=255, blank=True)
    manager = models.CharField(max_length=255, blank=True)
    bu_code = models.CharField(max_length=100, blank=True)
    recharge_date = models.DateField(null=True, blank=True)
    package = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    plan_name = models.CharField(max_length=100, blank=True)
    period = models.CharField(max_length=50, blank=True)
    fiscal_year = models.CharField(max_length=20, blank=True)
    speed = models.CharField(max_length=50, blank=True)
    churn_days = models.CharField(max_length=50, blank=True)

    class Meta:
        indexes = [models.Index(fields=['recharge_date'])]


class ReportMeta(models.Model):
    """Singleton row (id=1) holding the churn counts needed for the
    Churn vs Renewal charts, plus who/when last refreshed the report."""
    churn_bu_counts = models.JSONField(default=dict, blank=True)
    churn_manager_counts = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=150, blank=True)


class Snapshot(models.Model):
    """A frozen copy of the report for a given calendar date, shared the
    same way the live report is."""
    snapshot_date = models.DateField(unique=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    total_renewals = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    data = models.JSONField(default=list)

    class Meta:
        ordering = ['-snapshot_date']
