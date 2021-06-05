from django.contrib import admin
from .models import Post, Group, Comment


class Posts(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'


class Groups(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')
    list_filter = ('title',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'


class Comments(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'post', 'author')
    list_filter = ('author',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'


admin.site.register(Post, Posts)
admin.site.register(Group, Groups)
admin.site.register(Comment, Comments)
