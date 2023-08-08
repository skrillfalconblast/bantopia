from django.contrib.sitemaps import Sitemap
from posts.models import Post


class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return Post.objects.all().order_by('-post_datetime_created')

    def lastmod(self, obj):
        return obj.post_datetime_created