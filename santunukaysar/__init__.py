# Fix for Python 3.14 copy(super()) compatibility with Django BaseContext
try:
    from django.template import context as django_template_context

    def _patch_base_context_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    django_template_context.BaseContext.__copy__ = _patch_base_context_copy
except Exception:
    pass
