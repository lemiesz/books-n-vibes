from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from mutagen import File as MutagenFile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    socials_json = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.display_name or self.user.username


class Mix(models.Model):
    PUBLIC = 'PUBLIC'
    UNLISTED = 'UNLISTED'
    VIS_CHOICES = [(PUBLIC, 'Public'), (UNLISTED, 'Unlisted')]

    dj = models.ForeignKey(User, related_name='mixes', on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    audio = models.FileField(upload_to='mixes/audio/')
    cover = models.ImageField(upload_to='mixes/covers/', blank=True, null=True)
    duration_sec = models.PositiveIntegerField(blank=True, null=True)
    bpm = models.PositiveIntegerField(blank=True, null=True)
    genres_csv = models.CharField(max_length=200, blank=True)
    visibility = models.CharField(max_length=9, choices=VIS_CHOICES, default=PUBLIC)
    play_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:170]
            slug = base
            counter = 2
            while Mix.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        if self.audio and not self.duration_sec:
            try:
                audio = MutagenFile(self.audio.path)
                if audio and audio.info:
                    self.duration_sec = int(audio.info.length)
                    super().save(update_fields=['duration_sec'])
            except Exception:
                pass

    @property
    def genres(self):
        return [g.strip() for g in self.genres_csv.split(',') if g.strip()]

    def __str__(self):
        return self.title


class FeaturedDJ(models.Model):
    owner = models.ForeignKey(User, related_name='featured_links', on_delete=models.CASCADE)
    linked = models.ForeignKey(User, related_name='featured_by', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('owner', 'linked')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.owner} -> {self.linked}"
