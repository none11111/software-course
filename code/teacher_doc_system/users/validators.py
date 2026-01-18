from django.core.exceptions import ValidationError


class ContainsLetterValidator:
    """密码必须包含至少一个字母"""
    def validate(self, password, user=None):
        if not any(c.isalpha() for c in password):
            raise ValidationError('密码必须包含字母', code='password_no_letter')

    def get_help_text(self):
        return '密码必须包含至少一个字母'


class ContainsDigitValidator:
    """密码必须包含至少一个数字"""
    def validate(self, password, user=None):
        if not any(c.isdigit() for c in password):
            raise ValidationError('密码必须包含数字', code='password_no_digit')

    def get_help_text(self):
        return '密码必须包含至少一个数字'


class NotAllDotsValidator:
    """密码不能全是点号"""
    def validate(self, password, user=None):
        if password and all(c == '.' for c in password):
            raise ValidationError('密码不能只包含点号，请使用字母和数字组合', code='password_all_dots')

    def get_help_text(self):
        return '密码不能只包含点号'


