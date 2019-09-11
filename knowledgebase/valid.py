#Not remember what it for, have to revisit
class not_own_mail(object):
    def __init__(self, email):
        self.email = email

    def __call__(self, value):
        if value == self.email:
            raise ValidationError('It must be a different email address.')
        else:
            return value