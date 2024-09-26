class BaseValidator:
    def validate_data(self, data,REQUIRED_USER_FIELDS):
        errors = {}

        for field in REQUIRED_USER_FIELDS:
            if field not in data:
                errors[field] = f"{field} is required."

        return errors