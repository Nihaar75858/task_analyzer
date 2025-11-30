from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hrs = models.FloatField(
        validators=[MinValueValidator(0.5)]
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    dependencies = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date.isoformat(),
            "estimated_hrs": self.estimated_hrs,
            "importance": self.importance,
            "dependencies": self.dependencies,
        }