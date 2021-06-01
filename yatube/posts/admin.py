from django.contrib import admin
from .models import Post, Group


class Posts(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'


class Groups(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')
    # Не уверен на счет необходимости добавлять фильтр
    search_fields = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Post, Posts)
admin.site.register(Group, Groups)
