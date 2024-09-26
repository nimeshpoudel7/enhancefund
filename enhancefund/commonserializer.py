from rest_framework import serializers

class CommonSerializer(serializers.ModelSerializer):
    """Base serializer to handle common functionality."""

    def get_error_message(self):
        """Return the first error message from the serializer."""
        if self.errors:
            print(self.errors.values())
            return list(self.errors.values())[0][0]  # Return the first error message
        return "Unknown error"