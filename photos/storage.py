from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        :param **kwargs:
        Found at http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists, remove it as if it was a true file system
        self.delete(name)
        return name
